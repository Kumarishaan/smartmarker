from langgraph.checkpoint.postgres import PostgresSaver
from app.database import DATABASE_URL


with PostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
    checkpointer.setup()

print("LangGraph checkpoint tables created successfully.")