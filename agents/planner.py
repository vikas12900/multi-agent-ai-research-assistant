from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import json

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)


def planner_agent(query: str):

    prompt = f"""
    You are a senior research planner.

    Your job is to break a user query into focused research tasks.

    Rules:
    - Return exactly 3 tasks
    - Each task should be specific and searchable.
    - Avoid overlap between tasks.
    - Return ONLY valid JSON.
    
    Format:
    {{
        "tasks": [
            "task 1",
            "task 2",
            "task 3"
        ]
    }}

    User Query:
    {query}
    """

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    try:
        result = json.loads(response.content)
        return result["tasks"]

    except Exception:
        return [query]