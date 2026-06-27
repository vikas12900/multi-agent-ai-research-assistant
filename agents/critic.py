from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY")
)

class CriticResponse(BaseModel):
    score: float = Field(
        description="Quality score from 1 to 10"
    )

    improvements: list[str] = Field(
        description="Specific improvements needed"
    )

def critic_agent(report: str):

    prompt = f"""
You are a senior research reviewer with extremely high standards.

Evaluate the report on:

- Accuracy
- Completeness
- Structure
- Clarity
- Depth of analysis
- Use of supporting evidence
- Coverage of different perspectives
- Recent information
- Actionable insights

Scoring rules:

10 = Publication quality, comparable to a professional research paper.
9 = Excellent with only very minor issues.
8 = Very good but still missing important details.
7 = Good but has several weaknesses.
6 or below = Needs major improvements.

Be conservative.

Never give a score above 8 unless the report is exceptionally comprehensive,
well-structured, evidence-backed, and covers all major aspects of the topic.

If you deduct even 0.5 points,
you MUST explain why.

Provide at least 5 concrete improvements whenever the score is below 9.

Report:

{report}
"""

    structured_llm = llm.with_structured_output(
        CriticResponse
    )

    result = structured_llm.invoke(prompt)

    return {
        "score": result.score,
        "improvements": result.improvements
    }