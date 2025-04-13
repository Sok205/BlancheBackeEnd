from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..auth.db import get_db
from ..auth.models import Event, User
from ..llm import generate_text


import httpx

router = APIRouter()

class EventCreate(BaseModel):
    name: str
    description: str
    max_users: int
    password: str
    location: str
    time: str

class EventJoin(BaseModel):
    """
    Event join model
    """
    event_id: int

class EventResponse(BaseModel):
    """
    Event response model
    """
    id: str
    name: str
    description: str
    creator_id: int
    password: str
    registered_users: int
    max_users: int
    location: str
    time: str
    class Config:
        from_attributes = True

class EventAiDetail(BaseModel):
    """
    Event AI detail model
    """
    event: EventResponse
    ai_insights: Optional[str]

@router.post("/create")
def create_event(user_id: int, event: EventCreate, db: Session = Depends(get_db)):
    """
    Endpoint for event creation
    :param user_id:
    :param event:
    :param db:
    :return:
    """
    db_event = Event(
        name=event.name,
        creator_id=user_id,
        description=event.description,
        max_users=event.max_users,
        password=event.password,
        time=event.time,
        location=event.location,
        registered_users=1
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)

    creator = db.query(User).filter(User.id == user_id).first()
    db_event.attendees.append(creator)
    db.commit()

    return {"message": "Event created successfully", "event_id": db_event.id}
@router.post("/join")
def join_event(user_id: int, event_data: EventJoin, db: Session = Depends(get_db)):
    """
    Endpoint for joining an event
    :param user_id:
    :param event_data:
    :param db:
    :return:
    """
    try:
        event = db.query(Event).filter(Event.id == event_data.event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.registered_users >= event.max_users:
            raise HTTPException(status_code=400, detail="Event is full")

        user = db.query(User).filter(User.id == user_id).first()
        if user in event.attendees:
            raise HTTPException(status_code=400, detail="Already joined this event")

        event.attendees.append(user)
        event.registered_users += 1
        db.commit()

        return {"message": "1"}

    except Exception as e:
        return {"message": "0"}


@router.get("/all", response_model=list[EventResponse])
def get_all_events(db: Session = Depends(get_db)):
    """
    Endpoint for getting all events
    :param db:
    :return:
    """
    events = db.query(Event).all()
    events = [{**event.__dict__, 'id': str(event.id)} for event in events]

    return events

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Endpoint for getting a specific event by ID
    :param event_id:
    :param db:
    :return:
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    event = {**event.__dict__, 'id': str(event.id)}

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.get("/name/{event_name}", response_model=EventResponse)
def get_event_by_name(event_name: str, db: Session = Depends(get_db)):
    """
    Endpoint for getting a specific event by name
    :param event_name:
    :param db:
    :return:
    """
    event = db.query(Event).filter(Event.name == event_name).first()
    event = {**event.__dict__, 'id': str(event.id)}

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/user/{user_id}", response_model=list[EventResponse])
def get_user_events(user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint for getting all events of a specific user
    :param user_id:
    :param db:
    :return:
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert to dict after accessing the relationship
    events = [{**event.__dict__, 'id': str(event.id)} for event in user.events]
    return events


@router.delete("/{event_id}")
def delete_event(event_id: int, user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint for deleting a specific event
    :param event_id: ID of the event to delete
    :param user_id: ID of the user requesting deletion
    :param db: Database session
    :return: Success message
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.creator_id != user_id:
        raise HTTPException(status_code=403, detail="Only the event creator can delete this event")

    db.delete(event)
    db.commit()

    return {"message": "Event deleted successfully"}

@router.delete("/user/{user_id}")
def delete_event(user_id: int, db: Session = Depends(get_db)):
    """
    Endpoint for deleting a specific event
    :param event_id: ID of the event to delete
    :param user_id: ID of the user requesting deletion
    :param db: Database session
    :return: Success message
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Event not found")


    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

#LLM PART

@router.get("/ai/{event_id}")
async def get_event_ai_insight(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    prompt = f"You are a viking, and you have organized an event called {event.name}. " \
            f"The event is about {event.description}. " \
            f"The event will take place at {event.location} on {event.time}. " \
            f"The event will have a password: {event.password}. " \
            "Provide a short insight about this event, including its potential impact, " \
            "the number of attendees, and any other relevant information."

    response = await generate_text(prompt)
    return {"generated_text": response}

