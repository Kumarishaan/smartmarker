from app.notifications import send_email

send_email(
    "btech10101.23@bitmesra.ac.in",
    "Reminder Test",
    "<h1>Hello!</h1><p>Your email service is working.</p>"
)

print("Email Sent")