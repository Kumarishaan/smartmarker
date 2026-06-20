from sqlalchemy.orm import Session
from app.models import Reminder
from fastapi import HTTPException
from .enums import ReminderStatus

def create_reminder(db, reminder):

    db_reminder = Reminder(
        title=reminder.title,
        description=reminder.description,
        category=reminder.category,
        priority=reminder.priority,
        date=reminder.date,
        time=reminder.time,
        status=ReminderStatus.pending.value
    )

    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)

    return db_reminder

def get_reminders(db):
    return db.query(Reminder).all()


def get_reminder_by_id(db, reminder_id):
    reminder_db= db.query(Reminder).filter(
        Reminder.id == reminder_id
    ).first()

    if reminder_db:
        return reminder_db
    
    raise HTTPException(
        status_code=404,
        detail=f"Reminder {reminder_id} does not exist"
    )    


def delete_reminder(db, reminder_id):
    reminder_db = db.query(Reminder).filter(
        Reminder.id == reminder_id
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
    reminder_update):
    
    reminder_db = db.query(Reminder).filter(
        Reminder.id == reminder_id
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
        setattr(reminder_db, key, value)

    db.commit()
    db.refresh(reminder_db)

    return reminder_db    




def get_reminders_by_status(db,status: ReminderStatus):
    return db.query(Reminder).filter(
        Reminder.status == status.value
    ).all()



def get_active_reminders(db):

    return db.query(Reminder).filter(
        Reminder.status.notin_([
        ReminderStatus.completed.value,
        ReminderStatus.cancelled.value
        ])
    ).all()