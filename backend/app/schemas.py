from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
from datetime import date

class ClubCreate(BaseModel):
    name: str

class EventCreate(BaseModel):
    title: str
    date: date
    club_id: int
class TaskCreate(BaseModel):
    title: str
    deadline: date
    event_id: int
    assigned_to: int
class EventOut(BaseModel):
    id: int
    title: str
    date: date
    status: str
    club_id: int

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import Optional

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    assigned_to: Optional[int] = None
