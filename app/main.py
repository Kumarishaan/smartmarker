from fastapi import FastAPI

from .routes import reminders

from .database import engine
from .database import Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {
        "message": "AI Reminder Agent Backend Running"
    }

app.include_router(reminders.router)