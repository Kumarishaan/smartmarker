from .database import Base
from .enums import ReminderStatus
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

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

    conversations = relationship(
    "Conversation",
    back_populates="user"
    )


class Conversation(Base):
    __tablename__ = "conversations"

    thread_id = Column(String, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User", back_populates="conversations")