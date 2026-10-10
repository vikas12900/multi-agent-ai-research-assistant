import json
import sys
import time

from pipeline import run_pipeline

MIN_AVG_SCORE = 7.0
label = sys.argv[1]

queries = [q.strip() for q in open("evals/queries.txt") if q.strip()]
rows = []

for q in queries:
    r = run_pipeline(q)
    scores = [h["score"] for h in r["history"]]
    rows.append({
        "query": q,
        "scores": scores,
        "unsupported": [h["unsupported_claims"] for h in r["history"]],
        "first_score": scores[0],
        "final_score": r["final_score"],
        "rounds": len(scores),
        "report": r["report"]
    })
    time.sleep(20)

json.dump(rows, open(f"evals/result_{label}.json", "w"), indent = 2)

n = len(rows)
avg_first = sum(r["first_score"] for r in rows) / n
avg_final = sum(r["final_score"] for r in rows) / n
print(f"avg first score: {avg_first: .2f}")
print(f"avg final score {avg_final: .2f}")
print(f"avg gain: {avg_final - avg_first:.2f}")

if avg_final < MIN_AVG_SCORE:
    sys.exit(1)