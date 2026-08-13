from sqlalchemy import Column, Integer, String
from .database import Base
from .enums import ReminderStatus
from sqlalchemy import ForeignKey

class Reminder(Base):

    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    category = Column(String)
    priority = Column(String)
    date = Column(String)
    time = Column(String)
    email = Column(String)
    status = Column(String, default=ReminderStatus.pending.value)
    notified_at = Column(String, nullable=True)
    user_id = Column(Integer,ForeignKey("users.id"),nullable=False)


class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(String)

    email = Column(
        String,
        unique=True,
        nullable=False
    )

    hashed_password = Column(
        String,
        nullable=False
    )