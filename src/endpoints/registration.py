from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..auth.db import get_db
from ..auth.models import User

router = APIRouter()


class UserCreate(BaseModel):
    name: str
    description: str
    password: str


#User registry
@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """

    :param user:
    :param db:
    :return:
    """
    existing_user = db.query(User).filter(User.name == user.name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_user = User(
        name=user.name,
        description=user.description,
        password=user.password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {"message": "User created successfully", "user_id": db_user.id}

#User login
class UserLogin(BaseModel):
    name: str
    password: str


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.name == user.name).first()
    if not db_user or db_user.password != user.password:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    return {"message": "Login successful", "user_id": db_user.id}