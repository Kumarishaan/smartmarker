from datetime import datetime , timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from .notifications import build_reminder_email
from .database import SessionLocal
from .models import Reminder
from .enums import ReminderStatus
from .notifications import send_email

scheduler = BackgroundScheduler()

def check_reminders():

    db = SessionLocal()

    try:

        reminders = db.query(Reminder).filter(
            Reminder.status.in_([
                ReminderStatus.pending.value,
                ReminderStatus.notified.value
            ])
        ).all()

        current_time = datetime.now()

        for reminder in reminders:

            reminder_datetime = datetime.strptime(
                f"{reminder.date} {reminder.time}",
                "%Y-%m-%d %H:%M:%S"
            )


            # pending -> notified
            if (
                reminder.status == ReminderStatus.pending.value
                and current_time >= reminder_datetime
            ):
                email_sent=send_email(
                    reminder.email,
                    f"Reminder: {reminder.title}",
                    build_reminder_email(reminder)
                )
                if email_sent:
                    reminder.status = ReminderStatus.notified.value
                    reminder.notified_at = (
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    )
                    print(
                        f"Reminder Due: {reminder.title}"
                    )

            # notified -> overdue
            elif (
                reminder.status == ReminderStatus.notified.value
                and current_time >= reminder_datetime + timedelta(hours=1)
            ):

                reminder.status = ReminderStatus.overdue.value

                print(
                    f"Reminder Overdue: {reminder.title}"
                )

        db.commit()

    finally:

        db.close()


scheduler.add_job(
    check_reminders,
    trigger="interval",
    minutes=1
)        
