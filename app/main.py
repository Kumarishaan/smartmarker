from fastapi import FastAPI

from .routes import reminders
from .routes import users
from .routes import agent_route
from .database import engine
from .database import Base
from .scheduler import scheduler

Base.metadata.create_all(bind=engine)

app = FastAPI()

scheduler.start()

@app.get("/")
def home():
    return {
        "message": "AI Reminder Agent Backend Running"
    }

app.include_router(reminders.router)
app.include_router(users.router)
app.include_router(agent_route.router)