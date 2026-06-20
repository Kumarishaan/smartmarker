from pydantic import BaseModel
from typing import Optional
from .enums import ReminderStatus

class ReminderCreate(BaseModel):

    title: str
    description: str
    category: str
    priority: str
    date: str
    time: str



class ReminderUpdate(BaseModel):

    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None    
    status: ReminderStatus | None = None