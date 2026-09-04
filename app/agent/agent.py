import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from app.agent.tools import get_create_reminder_tool

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)

response = llm.invoke("Say hello in one sentence.")

print(response.content)

