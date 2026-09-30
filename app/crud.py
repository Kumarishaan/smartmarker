from sqlalchemy.orm import Session
from app.models import Reminder
from fastapi import HTTPException
from .enums import ReminderStatus
from datetime import datetime, date
from . import schemas
from . import models
from .security import hash_password
from uuid import uuid4
from app.models import Conversation

def create_reminder(db, reminder, user_id: int):

    db_reminder = Reminder(
        title=reminder.title,
        description=reminder.description,
        category=reminder.category,
        priority=reminder.priority,
        date=str(reminder.date),
        time=str(reminder.time),
        email=reminder.email,
        status=ReminderStatus.pending.value,
        user_id=user_id
    )

    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)

    return db_reminder

def get_reminders(db, user_id: int):
    return db.query(Reminder).filter(Reminder.user_id == user_id).all()


def get_reminder_by_id(db, reminder_id, user_id: int):
    reminder_db= db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == user_id
    ).first()

    if reminder_db:
        return reminder_db
    
    raise HTTPException(
        status_code=404,
        detail=f"Reminder {reminder_id} does not exist"
    )    


def delete_reminder(db, reminder_id, user_id: int):
    reminder_db = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == user_id
    ).first()

    if reminder_db:
        db.delete(reminder_db)
        db.commit()
        return f"Reminder {reminder_id} deleted"

    else:
        raise HTTPException(
            status_code=404,
            detail=f"Can't delete as Reminder {reminder_id} does not exist"
        )
    


def update_reminder(
    db,
    reminder_id,
    reminder_update,
    user_id: int
):
    reminder_db = db.query(Reminder).filter(
        Reminder.id == reminder_id,
        Reminder.user_id == user_id
    ).first()

    if reminder_db is None:
        raise HTTPException(
            status_code=404,
            detail=f"Reminder {reminder_id} does not exist"
        )

    update_data = reminder_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        if key in ["date", "time"] and value is not None:
            setattr(reminder_db, key, str(value))
        else:
            setattr(reminder_db, key, value)

    # -----------------------------
    # Reset status if reminder is
    # rescheduled into the future
    # -----------------------------
    if reminder_db.date is not None and reminder_db.time is not None:

        reminder_datetime = datetime.strptime(
            f"{reminder_db.date} {reminder_db.time}",
            "%Y-%m-%d %H:%M:%S"
        )

        if (
            reminder_datetime > datetime.now()
            and reminder_db.status not in [
                ReminderStatus.completed.value,
                ReminderStatus.cancelled.value
            ]
        ):
            reminder_db.status = ReminderStatus.pending.value

    db.commit()
    db.refresh(reminder_db)

    return reminder_db   




def get_reminders_by_status(db,status: ReminderStatus, user_id: int):
    return db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.status == status.value
    ).all()



def get_active_reminders(db, user_id: int):

    return db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.status.notin_([
        ReminderStatus.completed.value,
        ReminderStatus.cancelled.value
        ])
    ).all()


def create_user(
        db: Session,
        user: schemas.UserCreate
):

    new_user = models.User(

        name=user.name,

        email=user.email,

        hashed_password=hash_password(user.password)

    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user



def get_user_by_email(
        db: Session,
        email:str
):

    return (

        db.query(models.User)

        .filter(
            models.User.email == email
        )

        .first()

    )


def get_all_users(
        db: Session
):

    return db.query(
        models.User
    ).all()


def get_user_by_id(
        db: Session,
        user_id:int
):

    return (

        db.query(models.User)

        .filter(
            models.User.id == user_id
        )

        .first()

    )


def get_my_reminders(
    db: Session,
    user_id: int,
    reminder_date: date | None = None,
    status: ReminderStatus | None = None
):
    query = db.query(Reminder).filter(
        Reminder.user_id == user_id
    )

    if reminder_date is not None:
        query = query.filter(
            Reminder.date == str(reminder_date)
        )

    if status is not None:
        query = query.filter(
            Reminder.status == status.value
        )

    return query.all()



def create_conversation(db: Session, user_id: int):
    thread_id = str(uuid4())

    conversation = Conversation(
        thread_id=thread_id,
        user_id=user_id
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation



def get_conversation(
    db: Session,
    thread_id: str,
    user_id: int
):
    conversation = db.query(Conversation).filter(
        Conversation.thread_id == thread_id,
        Conversation.user_id == user_id
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return conversation

