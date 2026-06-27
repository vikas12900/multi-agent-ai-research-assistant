from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os

load_dotenv()
groqapikey = os.getenv("GROQ_API_KEY")


llm = ChatGroq(model = "llama-3.3-70b-versatile",
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
    {feedback}

    Revise the current report.
    Address every weakness and missing information point.
    Keep the strengths.
    Return only the improved report.
    """
    else:
        prompt = f"""
        You are a senior editor. Write a clear, well-structured report based on this research:
        {raw_data}
        """
    # rest of your existing editor logic

    response = llm.invoke(
        [HumanMessage(content=prompt)]
    )

    return response.content