from agents.planner import planner_agent
from agents.researcher import researcher_agent
from agents.editor import editor_agent
from agents.critic import critic_agent

TARGET_SCORE = 8
MAX_ITERATIONS = 3


def run_pipeline(query):

    tasks = planner_agent(query)

    all_research = []

    for task in tasks:
        research = researcher_agent(task)
        all_research.append(research)

    combined_research = "\n\n".join(all_research)

    report = editor_agent(combined_research)

    history = []

    for i in range(MAX_ITERATIONS):

        print(f"\n========== ITERATION {i+1} ==========")

        result = critic_agent(report)

        score = result["score"]
        improvements = result["improvements"]

        print("Score:", score)
        print("Improvements:", improvements)

        history.append({
            "iteration": i + 1,
            "score": score,
            "improvements": improvements
        })

        if score >= TARGET_SCORE:
            print("Target score reached. Stopping.")
            break

        print("Revising report...")

        report = editor_agent(
            raw_data=combined_research,
            current_report=report,
            improvements=improvements,
        )

        print(f"Revision complete. Report length: {len(report)}")

    return {
        "tasks": tasks,
        "raw_data": combined_research,
        "report": report,
        "history": history,
        "final_score": score
    }