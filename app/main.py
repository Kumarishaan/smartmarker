from fastapi import FastAPI

from .routes import reminders
from .routes import users
from .routes import agent_route
from .database import engine
from .database import Base
from .scheduler import scheduler

from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.database import DATABASE_URL


@asynccontextmanager
async def lifespan(app):
    async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        app.state.checkpointer = checkpointer
        yield

Base.metadata.create_all(bind=engine)

app = FastAPI(lifespan=lifespan)

scheduler.start()

@app.get("/")
def home():
    return {
        "message": "AI Reminder Agent Backend Running"
    }

app.include_router(reminders.router)
app.include_router(users.router)
app.include_router(agent_route.router)