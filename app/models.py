from sqlalchemy import Column, Integer, String
from .database import Base
from .enums import ReminderStatus

class Reminder(Base):

    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    category = Column(String)
    priority = Column(String)
    date = Column(String)
    time = Column(String)
    status = Column(String, default=ReminderStatus.pending.value)