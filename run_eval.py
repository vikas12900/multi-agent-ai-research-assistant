import os
import time
import pandas as pd
from pipeline import run_pipeline

RUN_NAME = "before"   # change to "after" once you've made the fixes

QUERIES = [
    "How does retrieval-augmented generation reduce hallucinations in LLMs?",
    "State of small language models for on-device use",
]

os.makedirs("eval_results", exist_ok=True)
rows = []

for i, query in enumerate(QUERIES, start=1):
    print(f"Running {i}/{len(QUERIES)}: {query}")

    start = time.time()
    result = run_pipeline(query)
    seconds = round(time.time() - start)

    scores = [item["score"] for item in result["history"]]

    rows.append({
        "id": i,
        "query": query,
        "seconds": seconds,
        "first_score": scores[0],
        "final_score": scores[-1],
        "rounds": len(scores),
    })

    with open(f"eval_results/{RUN_NAME}_{i}.md", "w", encoding="utf-8") as f:
        f.write(result["report"])

    pd.DataFrame(rows).to_csv(f"eval_results/{RUN_NAME}.csv", index=False)

    time.sleep(30)