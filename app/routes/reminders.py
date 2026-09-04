from fastapi import APIRouter
from sqlalchemy.orm import Session
from fastapi import Depends

from ..database import SessionLocal
from .. import schemas
from .. import crud
from ..enums import ReminderStatus
from .users import get_current_logged_in_user

router = APIRouter(tags=["Reminders"])

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


@router.post("/reminders")

def create_reminder_endpoint(
    reminder: schemas.ReminderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_logged_in_user)
):

    return crud.create_reminder(db, reminder,current_user.id)


@router.get("/reminders")

def get_reminders_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_logged_in_user)
):
    return crud.get_reminders(db, current_user.id)


@router.get("/reminders/{reminder_id}")

def get_reminder_by_id_endpoint(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_logged_in_user)
):
    return crud.get_reminder_by_id(db, reminder_id, current_user.id)


@router.delete("/reminders/{reminder_id}")

def delete_reminder_endpoint(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_logged_in_user)
):
    return crud.delete_reminder(db, reminder_id, current_user.id)


@router.patch("/reminders/{reminder_id}")

def update_reminder_endpoint(
    reminder_id: int,
    reminder_update: schemas.ReminderUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_logged_in_user)
):
    return crud.update_reminder(
        db,
        reminder_id,
        reminder_update,
        current_user.id
    )





@router.get("/reminders/status/{status}")
def get_reminders_by_status_endpoint(
    status: ReminderStatus,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_logged_in_user)
):

    reminders_db = crud.get_reminders_by_status(
        db,
        status,
        current_user.id
    )

    if not reminders_db:
        return {
            "message": f"There are no {status.value} reminders yet"
        }

    return reminders_db

@router.get("/active-reminders")
def get_active_reminders_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_logged_in_user)
):

    reminders_db = crud.get_active_reminders(db, current_user.id)

    if not reminders_db:
        return {
            "message": "There are no active reminders yet"
        }

    return reminders_db