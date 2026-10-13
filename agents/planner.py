from langchain_groq import ChatGroq
from datetime import date
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import os

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
    max_retries=5
)

class Plan(BaseModel):
    tasks: list[str] = Field(description="Exactly 3 short web search queries")

def planner_agent(query: str):

    prompt = f"""
You are a senior research planner.
Break the user query into exactly 3 web search queries.
Today's date is {date.today(): %d %B %Y}.
If the user asks for latest, recent or current information, include the current month and year in the queries.
Each query must be short (under 12 words), specific, and cover a different angle.

User query:
{query}
"""

    try:
        plan = llm.with_structured_output(Plan, method="json_schema").invoke(prompt)
        return plan.tasks[:3]
    except Exception as e:
        print("PLANNER FALLBACK:", type(e).__name__, e)
        return [query]