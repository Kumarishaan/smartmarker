import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite"
)

from typing import Literal
from pydantic import BaseModel


class ApprovalDecision(BaseModel):
    decision: Literal["approve", "reject", "unclear"]


approval_llm = llm.with_structured_output(ApprovalDecision)

