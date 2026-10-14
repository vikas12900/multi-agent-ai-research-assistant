from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    max_retries=5,
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

def critic_agent(report: str, research: str, query:str):

    prompt = f"""You are a strict fact-checker reviewing a research report.

User query:
{query}

Research (the ONLY allowed source of facts):
{research}

Report to review:
{report}

Check the WHOLE report every time. Do not assume earlier versions were checked.

Go through these checks in order:

1. NUMBERS: Find every number, percentage, date, and amount in the report. Each one must appear in the research. If a number is not in the research, it is unsupported, even if it seems plausible.

2. ATTRIBUTION: Each fact must be credited to the right country, company, study, or source. A real fact credited to the wrong one (e.g. China's figure given as India's, a global result given as a UK result) is unsupported.

3. CLAIMS: Any statement, recommendation, or conclusion not stated in the research is unsupported. This includes advice like "governments should..." unless the research says it.

4. COVERAGE: Check that the report answers every part of the user query. If the query asks for "pros and cons", "how it works and how much", etc., each part must be covered. Add each missing part to unsupported_claims as "MISSING: <part>".

5. COMPLETENESS: If the report ends mid-sentence or mid-section, add "TRUNCATED" to unsupported_claims.

Scoring rules (follow exactly):
- Any MISSING or TRUNCATED item: score at most 5.
- Any wrong number or wrong attribution: score at most 6.
- 3 or more unsupported claims: score at most 6.
- 1 or 2 unsupported claims: score at most 8.
- 9 or 10 only if there are zero unsupported claims and the query is fully answered.

In unsupported_claims, quote the exact claim from the report, briefly.
In improvements, say exactly what to remove or fix for each item.
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