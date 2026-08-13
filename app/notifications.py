import os
import resend

from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv(
    "RESEND_API_KEY"
)


def send_email(
    to_email: str,
    subject: str,
    body: str
):
    try:

        resend.Emails.send(
            {
                "from": "onboarding@resend.dev",
                "to": to_email,
                "subject": subject,
                "html": body,
            }
        )

        return True

    except Exception as e:

        print(f"Email Error: {e}")

        return False
    

def build_reminder_email(reminder):
    return f"""
    <h2>Reminder Alert</h2>

    <p><b>Title:</b> {reminder.title}</p>

    <p><b>Description:</b> {reminder.description}</p>

    <p><b>Priority:</b> {reminder.priority}</p>
    <p>Your reminder is due now.</p>
    """