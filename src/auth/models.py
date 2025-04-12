from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

user_events = Table(
    'user_events',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('event_id', Integer, ForeignKey('events.id'))
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    events = relationship('Event', secondary=user_events, back_populates='attendees')


class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    registered_users = Column(Integer, default=0)
    max_users = Column(Integer, nullable=False)
    password = Column(String, nullable=False)
    attendees = relationship('User', secondary=user_events, back_populates='events')
    creator = relationship('User', foreign_keys=[creator_id])
    time = Column(String, nullable=False)
    location = Column(String, nullable=False)