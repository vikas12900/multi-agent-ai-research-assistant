import json
import os
import sys

from pipeline import run_pipeline

label = sys.argv[1]
out_path = f"evals/result_{label}.json"

queries = [q.strip() for q in open("evals/queries.txt", encoding="utf-8") if q.strip()]
if label == "test":
    queries = queries[:1]

rows = []
if os.path.exists(out_path):
    with open(out_path, encoding="utf-8") as f:
        rows = json.load(f)
done = {r["query"] for r in rows}

for q in queries:
    if q in done:
        continue

    print(f"\n######## {q} ########")
    r = run_pipeline(q)
    history = r["history"]

    rows.append({
        "query": q,
        "tasks": r["tasks"],
        "scores": [h["score"] for h in history],
        "unsupported": [h["unsupported_claims"] for h in history],
        "first_score": history[0]["score"],
        "final_score": r["final_score"],
        "final_unsupported": len(r["unsupported_claims"]),
        "rounds": len(history),
        "words": len(r["report"].split()),
        "report": r["report"],
        "research": r["raw_data"],
    })

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

n = len(rows)


def avg(key):
    return sum(r[key] for r in rows) / n


print(f"\nQueries: {n}")
print(f"Avg first-draft score:               {avg('first_score'):.2f}")
print(f"Avg final score:                     {avg('final_score'):.2f}")
print(f"Avg unsupported claims, first draft: {sum(len(r['unsupported'][0]) for r in rows) / n:.2f}")
print(f"Avg unsupported claims, final draft: {avg('final_unsupported'):.2f}")
print(f"Avg drafts per query:                {avg('rounds'):.2f}")
print(f"Avg words per report:                {avg('words'):.0f}")