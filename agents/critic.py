from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY")
)

class CriticResponse(BaseModel):
    reasoning: str = Field(
        description="one sentence, under 25 words, naming the main reason for the score"
    )

    unsupported_claims: list[str] = Field(
        description="Every claim or number in the report that is not in the research"
    )

    score: float = Field(
        description="Quality score from 1 to 10"
    )

    improvements: list[str] = Field(
        description = "Specific improvements needed"
    )

def critic_agent(report: str, research: str):

    prompt = f"""
    You are a senior research reviewer. You are given the research notes and a report written from them.

    Judge the report on:
    - Accuracy: every claim and number must appear in the research.
    - Coverage: it uses the most important findings in the research.
    - Clarity: it is well organised and easy to follow.
    - Usefulness: it gives the reader clear takeaways.
    
    Keep the reasoning to one sentence.
    For unsupported claims, paraphrase each one in under 15 words. Do not use quotation marks anywhere in your answer.

    The report is limited to 600 words. Do not ask for more length.

    Scoring rules:

    9-10 = Every claim is supported by the research. Clear, complete, nothing to cut.
    7-8 = Mostly supported and clear, with one or two weak or unsupported claims.
    5-6 = Accurate but generic, or misses important findings from the research.
    3-4 = Several unsupported claims, or poorly organised.
    1-2 = Inaccurate or off-topic.

    Give at most 3 improvements, most important first.
    Each improvement must be something the writer can fix using only the research below.
    Never ask for sources, data or detail that is not in the research.
    If a claim is not in the research, say to remove it.

    Research:

    {research}

    Report:

    {report}
    """

    structured_llm = llm.with_structured_output(
        CriticResponse,
        method="json_schema",
        strict = True
    )

    result = structured_llm.invoke(prompt)

    return {
        "reasoning": result.reasoning,
        "unsupported_claims": result.unsupported_claims,
        "score": result.score,
        "improvements": result.improvements
    }