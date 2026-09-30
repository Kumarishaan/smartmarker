from pydantic import BaseModel
import datetime
from datetime import date
from langchain_core.tools import StructuredTool
from app.crud import get_my_reminders
from app.enums import ReminderStatus
from app.crud import update_reminder
from sqlalchemy.orm import Session
from app.models import User
from langgraph.types import interrupt
from ..crud import get_reminder_by_id, delete_reminder
from app import schemas
from app.crud import create_reminder

class CreateReminderInput(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    date: datetime.date
    time: datetime.time


def create_reminder_tool(
    db: Session,
    current_user: User,
    reminder_data: CreateReminderInput
):
    reminder = schemas.ReminderCreate(
        title=reminder_data.title,
        description=reminder_data.description,
        category=reminder_data.category,
        priority=reminder_data.priority,
        date=reminder_data.date,
        time=reminder_data.time,
        email=current_user.email
    )

    reminder_db = create_reminder(
        db,
        reminder,
        current_user.id
    )

    return reminder_db


def get_create_reminder_tool(
    db: Session,
    current_user: User
):
    def create_reminder_for_user(
        title: str,
        description: str,
        category: str,
        priority: str,
        date: datetime.date,
        time: datetime.time
    ):
        reminder_data = CreateReminderInput(
            title=title,
            description=description,
            category=category,
            priority=priority,
            date=date,
            time=time
        )

        return create_reminder_tool(
            db=db,
            current_user=current_user,
            reminder_data=reminder_data
        )

    return StructuredTool.from_function(
        func=create_reminder_for_user,
        name="create_reminder",
        description=(
            "Create a new reminder for the currently authenticated user. "
            "Use this tool when the user asks to create or set a reminder."
        )
    )

def get_my_reminders_tool(
    db: Session,
    current_user: User,
    reminder_date: date | None = None,
    status: ReminderStatus | None = None
):
    reminders = get_my_reminders(
        db=db,
        user_id=current_user.id,
        reminder_date=reminder_date,
        status=status
    )

    return [
        {
            "id": reminder.id,
            "title": reminder.title,
            "description": reminder.description,
            "category": reminder.category,
            "priority": reminder.priority,
            "date": str(reminder.date),
            "time": str(reminder.time),
            "status": reminder.status
        }
        for reminder in reminders
    ]

def get_get_my_reminders_tool(
    db: Session,
    current_user: User
):
    def get_my_reminders_for_user(
        reminder_date: date | None = None,
        status: ReminderStatus | None = None
    ):
        return get_my_reminders_tool(
            db=db,
            current_user=current_user,
            reminder_date=reminder_date,
            status=status
        )

    return StructuredTool.from_function(
        func=get_my_reminders_for_user,
        name="get_my_reminders",
        description=(
            "Get reminders belonging to the currently authenticated user. "
            "Optionally filter reminders by date and status. "
            "Use this tool when the user asks to view, find, or list their reminders. "
            "Always use the returned reminder details when answering the user."
        )
    )


class UpdateReminderInput(BaseModel):
    reminder_id: int
    title: str | None = None
    description: str | None = None
    category: str | None = None
    priority: str | None = None
    date: datetime.date | None = None
    time: datetime.time | None = None
    status: ReminderStatus | None = None


def update_reminder_tool(
    db: Session,
    current_user: User,
    reminder_data: UpdateReminderInput
):
    reminder_update = schemas.ReminderUpdate(
        **{
            key: value
            for key, value in {
                "title": reminder_data.title,
                "description": reminder_data.description,
                "category": reminder_data.category,
                "priority": reminder_data.priority,
                "date": reminder_data.date,
                "time": reminder_data.time,
                "status": reminder_data.status
            }.items()
            if value is not None
        }
    )

    reminder_db = update_reminder(
        db=db,
        reminder_id=reminder_data.reminder_id,
        reminder_update=reminder_update,
        user_id=current_user.id
    )

    return {
        "id": reminder_db.id,
        "title": reminder_db.title,
        "description": reminder_db.description,
        "date": str(reminder_db.date),
        "time": str(reminder_db.time),
        "priority": reminder_db.priority,
        "status": reminder_db.status
    }


def get_update_reminder_tool(db: Session, current_user: User):

    def update_reminder_for_user(
        reminder_id: int,
        title: str | None = None,
        description: str | None = None,
        category: str | None = None,
        priority: str | None = None,
        date: datetime.date | None = None,
        time: datetime.time | None = None,
        status: ReminderStatus | None = None
    ):
        update_data = {
            key: value
            for key, value in {
                "reminder_id": reminder_id,
                "title": title,
                "description": description,
                "category": category,
                "priority": priority,
                "date": date,
                "time": time,
                "status": status
            }.items()
            if value is not None
        }

        reminder_data = UpdateReminderInput(**update_data)

        return update_reminder_tool(
            db=db,
            current_user=current_user,
            reminder_data=reminder_data
        )

    return StructuredTool.from_function(
        func=update_reminder_for_user,
        name="update_reminder",
        description=(
            "Update an existing reminder belonging to the currently "
            "authenticated user. Use this tool when the user asks to "
            "change, reschedule, rename, or modify a reminder. "
            "Only update the fields explicitly requested by the user. "
            "The reminder_id must belong to the authenticated user."
        )
    )


class DeleteReminderInput(BaseModel):
    reminder_id: int


def delete_reminder_tool(
    db: Session,
    current_user: User,
    reminder_data: DeleteReminderInput
):
    reminder_db = get_reminder_by_id(
        db=db,
        reminder_id=reminder_data.reminder_id,
        user_id=current_user.id
    )

    reminder = {
        "id": reminder_db.id,
        "title": reminder_db.title,
        "description": reminder_db.description,
        "date": str(reminder_db.date),
        "time": str(reminder_db.time),
        "priority": reminder_db.priority,
        "status": reminder_db.status
    }

    approval = interrupt({
        "action": "delete_reminder",
        "reminder": reminder
    })

    if not approval:
        return {
            "title": reminder_db.title,
            "status": "cancelled"
        }

    delete_reminder(
        db=db,
        reminder_id=reminder_data.reminder_id,
        user_id=current_user.id
    )

    return {
        "title": reminder_db.title,
        "status": "deleted"
    }

def get_delete_reminder_tool(
    db: Session,
    current_user: User
):
    def delete_reminder_for_user(
        reminder_id: int
    ):
        reminder_data = DeleteReminderInput(
            reminder_id=reminder_id
        )

        return delete_reminder_tool(
            db=db,
            current_user=current_user,
            reminder_data=reminder_data
        )

    return StructuredTool.from_function(
        func=delete_reminder_for_user,
        name="delete_reminder",
        description=(
            "Delete one of the currently authenticated user's reminders. "
            "Before deletion, the user must explicitly approve the deletion. "
            "Use this tool only after the target reminder has been clearly identified."
        )
    )

