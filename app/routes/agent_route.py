from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from ..crud import create_conversation
from ..crud import get_conversation
from .reminders import get_db
from .users import get_current_logged_in_user
from app.agent.tools import get_delete_reminder_tool
from app.models import User
from app.agent.graph import build_agent_graph
from app.agent.tools import (
    get_create_reminder_tool,
    get_get_my_reminders_tool,
    get_update_reminder_tool
)
from app.agent.agent import llm, approval_llm
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import Command
from datetime import date


router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/conversations")
def create_new_conversation(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_logged_in_user)
):
    conversation = create_conversation(
        db=db,
        user_id=current_user.id
    )

    return {
        "thread_id": conversation.thread_id
    }


@router.post("/chat")
async def chat_with_agent(
    request: Request,
    message: str,
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_logged_in_user)
):
    get_conversation(
    db=db,
    thread_id=thread_id,
    user_id=current_user.id
   )

    create_reminder_tool = get_create_reminder_tool(
        db=db,
        current_user=current_user
    )

    get_my_reminders_tool = get_get_my_reminders_tool(
        db=db,
        current_user=current_user
    )

    update_reminder_tool = get_update_reminder_tool(
        db=db,
        current_user=current_user
    )

    delete_reminder_tool = get_delete_reminder_tool(
    db=db,
    current_user=current_user
    )

    tools = [
        create_reminder_tool,
        get_my_reminders_tool,
        update_reminder_tool,
        delete_reminder_tool
    ]

    checkpointer = request.app.state.checkpointer

    graph = build_agent_graph(
        tools=tools,
        checkpointer=checkpointer
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    snapshot = await graph.aget_state(config)

    pending_interrupt = None

    for task in snapshot.tasks:
        if task.interrupts:
            pending_interrupt = task.interrupts[0].value
            break

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

    When using tools:
    - Treat all tool results as internal backend data.
    - Never expose raw tool output, JSON, database objects, or
    implementation details.
    - Use tool results only as information needed to answer the user's request.
    - Only mention fields that are directly relevant to the user's request.
    - When the user asks to list or view reminders, by default show only:
    title, date, and time.
    -mention description, priority, and category only if the user asks for details.
    - Do not mention category, reminder ID, user ID,
    email, or other internal fields unless:
    1. the user explicitly asks for that information, or
    2. it is necessary to answer the user's request.
    - Do not label or enumerate internal metadata unnecessarily.
    - Convert dates and times into natural, human-readable formats.
    - Never expose raw tool results or internal metadata.

    When answering about reminders:
    - Keep the response concise and natural.
    - Prefer sentences or simple bullet points.
    - Do not repeat information unnecessarily.
    - If there are no matching reminders, clearly say that no matching
    reminders were found.

    When updating a reminder:
    - Only provide fields that the user explicitly asks to change.
    - Never pass a field with a value of null/None when the user did not
    request that field to be changed.
    - If the user asks only to change the time, provide only the reminder_id
    and the new time. Do not provide the date.
    - If the user asks only to change the date, provide only the reminder_id
    and the new date. Do not provide the time.
    - The backend will preserve all fields that are not provided.
    
    - If the user identifies a reminder by title, description, or a natural
    reference such as "my assignment reminder", first use the
    get_my_reminders tool to retrieve the user's reminders.
    - Use the returned reminder details to identify the most appropriate
    matching reminder.
    - Do not assume that the user's wording exactly matches the reminder title.
    - For example, if the user says "my assignment reminder" and the actual
    reminder is titled "Submit assignment", recognize that they may refer
    to the same reminder.
    - After identifying the reminder, use its reminder_id when calling
    update_reminder.
    - If exactly one reminder is a reasonable match, update it directly.
    - If multiple reminders could reasonably match, ask the user which one
    they mean.
    - Do not require the user to provide a reminder_id unless the reminder
    cannot otherwise be identified.

    When deleting a reminder:

    - If the user identifies a reminder by title, description, or a natural
    reference such as "my assignment reminder", first use the
    get_my_reminders tool.
    - Use the returned reminder details to identify the target.
    - If exactly one reminder is a reasonable match, use its reminder_id
    with the delete_reminder tool.
    - If multiple reminders could reasonably match, ask the user which
    reminder they mean.
    - Do not call delete_reminder while the target is ambiguous.
    - The delete_reminder tool will ask the user for confirmation before
    performing the deletion.
    - Never assume that deletion is approved.
    When handling the result of delete_reminder:
    - status "deleted" means the reminder was successfully deleted.
    - status "cancelled" means the reminder was NOT deleted because the user rejected the deletion.
    - Never claim that a reminder was deleted when the status is "cancelled".
"""
    if pending_interrupt is not None:

        approval_prompt = f"""
    You are interpreting a user's response to a pending reminder deletion confirmation.

    The reminder waiting for deletion approval is:

    {pending_interrupt["reminder"]}

    User's response:

    {message}

    Classify the user's response as exactly one of:

    - approve: the user clearly wants the reminder deleted
    - reject: the user clearly does not want the reminder deleted
    - unclear: the response is ambiguous, unrelated, or does not clearly authorize or reject deletion

    Never assume approval from an ambiguous response.
    """

        decision = await approval_llm.ainvoke(
            approval_prompt
        )

        if decision.decision == "unclear":
            return {
                "response": (
                    f"Please confirm whether you want me to delete "
                    f"the reminder '{pending_interrupt['reminder']['title']}'."
                )
            }

        result = await graph.ainvoke(
            Command(
                resume=decision.decision == "approve"
            ),
            config=config
        )

    else:

        result = await graph.ainvoke(
            {
                "messages": [
                    SystemMessage(content=system_message),
                    HumanMessage(content=message)
                ],
                "reminder_data": None,
                "reminders": []
            },
            config=config
        )

    if "__interrupt__" in result:
        interrupt_data = result["__interrupt__"][0].value

        reminder = interrupt_data["reminder"]

        return {
            "response": (
                f"Are you sure you want to delete "
                f"the '{reminder['title']}' reminder?"
            )
        }

    final_response = result["messages"][-1].content

    if isinstance(final_response, list):
        final_response = "".join(
            item["text"]
            for item in final_response
            if item.get("type") == "text"
        )

    return {
        "response": final_response
    } 