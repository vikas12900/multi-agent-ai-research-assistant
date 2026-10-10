import os
import time

from agents.planner import planner_agent
from agents.researcher import researcher_agent
from agents.editor import editor_agent
from agents.critic import critic_agent

TARGET_SCORE = 8
MAX_REVISIONS = 2
PAUSE = int(os.getenv("LLM_PAUSE_SECONDS", "0"))


def wait():
    if PAUSE:
        print(f"Waiting {PAUSE}s for the rate limit...")
        time.sleep(PAUSE)


def run_pipeline(query):

    tasks = planner_agent(query)

    all_research = []
    for task in tasks:
        all_research.append(researcher_agent(task))

    combined_research = "\n\n".join(all_research)[:8000]
    print("Research characters:", len(combined_research))

    wait()
    report = editor_agent(combined_research)

    history = []
    status = "max_revisions"

    for i in range(MAX_REVISIONS + 1):

        print(f"\n========== DRAFT {i + 1} ==========")

        wait()
        result = critic_agent(report, combined_research)
        score = result["score"]
        improvements = result["improvements"]

        print("score:", score, "|", result["reasoning"])

        history.append({
            "iteration": i + 1,
            "score": score,
            "reasoning": result["reasoning"],
            "unsupported_claims": result["unsupported_claims"],
            "improvements": improvements,
            "report": report,
        })

        if score >= TARGET_SCORE:
            status = "converged"
            print("Target score reached. Stopping.")
            break

        if i == MAX_REVISIONS:
            print("No revisions left. Stopping.")
            break

        print("Revising report...")
        wait()
        report = editor_agent(
            raw_data=combined_research,
            current_report=report,
            improvements=improvements,
        )

    best = max(history, key=lambda h: h["score"])
    print(f"Best draft: {best['iteration']} with score {best['score']}")

    return {
        "tasks": tasks,
        "raw_data": combined_research,
        "report": best["report"],
        "history": history,
        "final_score": best["score"],
        "status": status,
    }