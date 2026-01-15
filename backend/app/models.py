from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
from sqlalchemy import ForeignKey


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # CLUB_ADMIN, MEMBER, PRINCIPAL
    club_id = Column(Integer, nullable=True)


class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    events = relationship("Event", back_populates="club")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    start_time = Column(DateTime, nullable=False)
    notify_at = Column(DateTime, nullable=False)
    created_by = Column(Integer)
    date = Column(Date, nullable=False)
    status = Column(String, default="PLANNED")  # PLANNED / COMPLETED


lub_id = Column(Integer, ForeignKey("clubs.id"))
club = relationship("Club", back_populates="events")

tasks = relationship("Task", back_populates="event")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    deadline = Column(Date, nullable=False)
    completed = Column(Boolean, default=False)
    notify = Column(Boolean, default=False)

    event_id = Column(Integer, ForeignKey("events.id"))
    assigned_to = Column(Integer, ForeignKey("users.id"))

    event = relationship("Event", back_populates="tasks")
