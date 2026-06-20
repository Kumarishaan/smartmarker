from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from ..database import SessionLocal
from .. import schemas
from .. import crud
from ..enums import ReminderStatus

router = APIRouter()

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/reminders")

def create_reminder_endpoint(
    reminder: schemas.ReminderCreate,
    db: Session = Depends(get_db)
):

    return crud.create_reminder(db, reminder)


@router.get("/reminders")

def get_reminders_endpoint(
    db: Session = Depends(get_db)
):
    return crud.get_reminders(db)


@router.get("/reminders/{reminder_id}")

def get_reminder_by_id_endpoint(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    return crud.get_reminder_by_id(db, reminder_id)


@router.delete("/reminders/{reminder_id}")

def delete_reminder_endpoint(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    return crud.delete_reminder(db, reminder_id)


@router.patch("/reminders/{reminder_id}")

def update_reminder_endpoint(
    reminder_id: int,
    reminder_update: schemas.ReminderUpdate,
    db: Session = Depends(get_db)
):
    return crud.update_reminder(
        db,
        reminder_id,
        reminder_update
    )





@router.get("/reminders/status/{status}")
def get_reminders_by_status_endpoint(
    status: ReminderStatus,
    db: Session = Depends(get_db)
):

    reminders_db = crud.get_reminders_by_status(
        db,
        status
    )

    if not reminders_db:
        return {
            "message": f"There are no {status.value} reminders yet"
        }

    return reminders_db

@router.get("/active-reminders")
def get_active_reminders_endpoint(
    db: Session = Depends(get_db)
):

    reminders_db = crud.get_active_reminders(db)

    if not reminders_db:
        return {
            "message": "There are no active reminders yet"
        }

    return reminders_db