from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.getenv("GROQ_API_KEY"),
    max_retries=5,
)


def looks_cut_off(text):
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return True
    last = lines[-1]
    return len(last.split()) < 3 or last[-1] not in '.!?)*"”’'


def editor_agent(raw_data, current_report=None, improvements=None, unsupported=None):

    if current_report:
        fixes = "\n".join(f"- {p}" for p in (improvements or []))
        remove = "\n".join(f"- {c}" for c in (unsupported or [])) or "- None"
        prompt = f"""
    You are a senior editor.

    Original Research:
    {raw_data}

    Current Report:
    {current_report}

    Claims not found in the research. Remove or correct each one:
    {remove}

    Other fixes:
    {fixes}

    Revise the report. Keep what is already good.
    Use only facts found in the research.
    Return only the improved report, under 600 words.
    """
    else:
        prompt = f"""
    You are a senior editor. Write a clear, well-structured report based on this research:
    {raw_data}
    Use only facts found in the research. Do not add numbers, names or projections that are not in it.
    Maximum 600 words. Do not use tables.
    """

    for attempt in range(2):
        response = llm.invoke([HumanMessage(content=prompt)])
        if not looks_cut_off(response.content):
            break
        print("Draft looks cut off. Regenerating...")

    return response.content
