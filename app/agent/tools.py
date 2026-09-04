from pydantic import BaseModel
import datetime
from datetime import date
from langchain_core.tools import StructuredTool
from app.crud import get_my_reminders
from app.enums import ReminderStatus

class CreateReminderInput(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    date: datetime.date
    time: datetime.time


from app import schemas
from app.crud import create_reminder
from app.models import User
from sqlalchemy.orm import Session


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
    return get_my_reminders(
        db=db,
        user_id=current_user.id,
        reminder_date=reminder_date,
        status=status
    )

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
            "Use this tool when the user asks to view, find, or list their reminders."
        )
    )