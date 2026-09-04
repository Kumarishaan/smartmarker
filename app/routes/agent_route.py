from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .reminders import get_db
from app.models import User
from .users import get_current_logged_in_user
from sqlalchemy.orm import Session

from app.agent.agent import llm
from app.agent.tools import get_create_reminder_tool
from datetime import date
from langchain_core.messages import SystemMessage, HumanMessage
from datetime import date

from app.enums import ReminderStatus
from app.agent.tools import get_get_my_reminders_tool
from langchain_core.messages import ToolMessage

router = APIRouter(
    prefix="/agent",
    tags=["Agent"]
)


@router.post("/chat")
async def chat_with_agent(
    message: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_logged_in_user)
):
    create_reminder_tool_instance = get_create_reminder_tool(
        db=db,
        current_user=current_user
    )

    get_my_reminders_tool_instance = get_get_my_reminders_tool(
        db=db,
        current_user=current_user
    )

    llm_with_tools = llm.bind_tools([
        create_reminder_tool_instance,
        get_my_reminders_tool_instance
    ])

    today = date.today().isoformat()

    system_message = f"""
    You are an AI reminder assistant.

    Today's date is {today}.

    When creating a reminder:
    - Convert relative dates such as "today", "tomorrow",
      "next Monday", etc. into the exact calendar date.
    - The date must be in YYYY-MM-DD format.
    - The time must be in HH:MM:SS format.
    - Do not generate user_id, email, or status.
    - The backend automatically handles the authenticated
      user, email, and reminder status.
    """

    response = await llm_with_tools.ainvoke([
        SystemMessage(content=system_message),
        HumanMessage(content=message)
    ])

    if response.tool_calls:

        tool_call = response.tool_calls[0]

        if tool_call["name"] == "create_reminder":

            await create_reminder_tool_instance.ainvoke(
                tool_call["args"]
            )

            return {
                "response": "Reminder created successfully."
            }

        elif tool_call["name"] == "get_my_reminders":

            tool_result = await get_my_reminders_tool_instance.ainvoke(
                tool_call["args"]
            )

            final_response = await llm.ainvoke([
                SystemMessage(content=system_message),
                HumanMessage(content=message),
                response,
                ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_call["id"]
                )
            ])

            return {
                "response": final_response.content
            }

    return {
        "response": response.content
    }


