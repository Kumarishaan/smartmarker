from pydantic import BaseModel,EmailStr
from typing import Optional
from .enums import ReminderStatus
import datetime


class ReminderCreate(BaseModel):

    title: str
    description: str
    category: str
    priority: str
    date: datetime.date
    time: datetime.time
    email: EmailStr


class ReminderUpdate(BaseModel):

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    date: Optional[datetime.date] = None
    time: Optional[datetime.time] = None
    status: ReminderStatus | None = None
    email: EmailStr | None = None

class UserCreate(BaseModel):

    name: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):

    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserLogin(BaseModel):

    email: EmailStr
    password: str