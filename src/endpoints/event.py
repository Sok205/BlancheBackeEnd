from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel


from ..auth.db import get_db
from ..auth.models import Event, User

import httpx

router = APIRouter()

class EventCreate(BaseModel):
    """
    Event creation model
    """
    name: str
    max_users: int
    password: str

class EventJoin(BaseModel):
    """
    Event join model
    """
    event_id: int
    password: str

class EventResponse(BaseModel):
    """
    Event response model
    """
    id: str
    name: str
    creator_id: int
    registered_users: int
    max_users: int
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
        max_users=event.max_users,
        password=event.password,
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
    event = db.query(Event).filter(Event.id == event_data.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.password != event_data.password:
        raise HTTPException(status_code=401, detail="Incorrect event password")

    if event.registered_users >= event.max_users:
        raise HTTPException(status_code=400, detail="Event is full")

    user = db.query(User).filter(User.id == user_id).first()
    if user in event.attendees:
        raise HTTPException(status_code=400, detail="Already joined this event")

    event.attendees.append(user)
    event.registered_users += 1
    db.commit()

    return {"message": "Successfully joined event"}

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
    user.events = [{**event.__dict__, 'id': str(event.id)} for event in user.events]
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.events

#LLM PART

@router.get("/ai/{event_id}", response_model=EventAiDetail)
async def get_event_ai_insight(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event = {**event.__dict__, 'id': str(event.id)}
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "http://localhost:8080/v1/completions",
                json={
                    "prompt": f"Event: {event.name}\nParticipants: {event.registered_users}/{event.max_users}\nPlease provide a brief insight about this event.",
                    "max_tokens": 100,
                    "temperature": 0.7
                }
            )
            result = response.json()
            ai_insight = result['choices'][0]['text'].strip()
    except Exception as e:
        ai_insight = f"AI insight unavailable: {str(e)}"

    return {
        "event": event,
        "ai_insight": ai_insight
    }