from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()
groqapikey = os.getenv("GROQ_API_KEY")


llm = ChatGroq(model = "openai/gpt-oss-20b",
               api_key=groqapikey)

def editor_agent(raw_data: str, current_report = None,feedback: str = None, improvements: list = None):
    if improvements:
        feedback_text = "\n".join(f"- {point}" for point in improvements)
        prompt = f"""
    You are a senior editor.

    Original Research:
    {raw_data}

    Current Report:
    {current_report}

    Critic Feedback:
    {feedback_text}

    Revise the current report.
    Address every weakness and missing information point.
    Keep the strengths.
    Return only the improved report.
    Keep the report under 600 words.
    """
    else:
        prompt = f"""
        You are a senior editor. Write a clear, well-structured report based on this research:
        {raw_data}
        Use only facts found in the research. Do not add numbers, names or projections that are not in it.
        Maximum 600 words. Do not use tables.
        """
    # rest of your existing editor logic

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return response.content