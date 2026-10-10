import glob
import json
import os
import re
from datetime import datetime

import pandas as pd
import streamlit as st

import pipeline
from pipeline import run_pipeline

st.set_page_config(
    page_title="AI Research Analyst",
    page_icon="⚡",
    layout="wide",
)


def extract_sources(raw_data):
    return list(dict.fromkeys(re.findall(r"Source: (\S+)", raw_data)))


def score_label(score):
    if score >= 9:
        return "Excellent"
    if score >= 7:
        return "Good"
    if score >= 5:
        return "Fair"
    return "Weak"


# ---------------- Sidebar ----------------

with st.sidebar:
    st.header("⚙️ Settings")

    pipeline.TARGET_SCORE = st.slider(
        "Target critic score", 1, 10, pipeline.TARGET_SCORE,
        help="Stop revising once the critic gives at least this score.",
    )
    pipeline.MAX_REVISIONS = st.slider(
        "Max revisions", 0, 5, pipeline.MAX_REVISIONS,
        help="How many times the editor may revise the report.",
    )

    st.divider()
    st.subheader("🔑 API keys")
    for key in ["GROQ_API_KEY", "TAVILY_API_KEY"]:
        if os.getenv(key):
            st.success(f"{key} loaded")
        else:
            st.error(f"{key} missing — add it to .env")

    st.divider()
    st.caption(
        "Pipeline: **Planner** → **Researcher** (Tavily) → **Editor** → "
        "**Critic** ↺ Editor until the target score is reached."
    )

    if st.session_state.get("runs"):
        st.divider()
        st.subheader("🕘 This session")
        for run in reversed(st.session_state.runs):
            st.write(f"• {run['query']} — **{run['result']['final_score']}**")


st.title("⚡ AI Research Analyst")
st.caption("Multi-agent research: plan, search the web, write, and self-critique.")

analyze_tab, bench_tab = st.tabs(["🔎 Analyze", "📊 Benchmarks"])

# ---------------- Analyze ----------------

with analyze_tab:
    with st.form("query_form"):
        query = st.text_input("Enter a topic", value="Latest AI news")
        submitted = st.form_submit_button("Run Analysis", type="primary")

    if submitted:
        if not query.strip():
            st.warning("Please enter a topic.")
        else:
            with st.status("Running pipeline...", expanded=True) as status:
                try:
                    st.write("Planning → researching → writing → critiquing. This can take a minute...")
                    started = datetime.now()
                    result = run_pipeline(query.strip())
                    seconds = (datetime.now() - started).seconds
                    status.update(
                        label=f"Done in {seconds}s — {result['status'].replace('_', ' ')}",
                        state="complete",
                        expanded=False,
                    )
                    st.session_state.setdefault("runs", []).append(
                        {"query": query.strip(), "result": result, "seconds": seconds}
                    )
                    st.session_state.current = st.session_state.runs[-1]
                except Exception as e:
                    status.update(label="Pipeline failed", state="error")
                    st.error(f"Pipeline failed: {e}")

    current = st.session_state.get("current")

    if current:
        result = current["result"]
        history = result["history"]
        first = history[0]["score"]
        final = result["final_score"]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Final score", f"{final}/10", score_label(final))
        c2.metric("First draft", f"{first}/10")
        c3.metric("Improvement", f"{final - first:+.1f}")
        c4.metric("Critic rounds", len(history), f"{current['seconds']}s", delta_color="off")

        report_tab, critic_tab, research_tab = st.tabs(
            ["📄 Report", "🧐 Critic history", "📋 Research"]
        )

        with report_tab:
            st.markdown(result["report"])
            st.download_button(
                "⬇️ Download report (.md)",
                data=result["report"],
                file_name=f"{re.sub(r'[^a-zA-Z0-9]+', '_', current['query'])[:50]}.md",
                mime="text/markdown",
            )

        with critic_tab:
            if len(history) > 1:
                st.line_chart(
                    pd.DataFrame(
                        {"Score": [h["score"] for h in history]},
                        index=pd.Index([h["iteration"] for h in history], name="Draft"),
                    )
                )

            for item in history:
                best = " 🏆" if item["report"] == result["report"] else ""
                with st.expander(
                    f"Draft {item['iteration']} — score {item['score']}{best}",
                    expanded=item is history[-1],
                ):
                    st.write(f"**Reasoning:** {item['reasoning']}")

                    if item["unsupported_claims"]:
                        st.write("**Unsupported claims:**")
                        for claim in item["unsupported_claims"]:
                            st.write(f"- ⚠️ {claim}")
                    else:
                        st.write("✅ No unsupported claims.")

                    if item["improvements"]:
                        st.write("**Suggested improvements:**")
                        for improvement in item["improvements"]:
                            st.write(f"- {improvement}")

                    if st.toggle("Show this draft", key=f"draft_{item['iteration']}"):
                        st.markdown(item["report"])

        with research_tab:
            st.subheader("Research tasks")
            for n, task in enumerate(result["tasks"], start=1):
                st.write(f"{n}. {task}")

            sources = extract_sources(result["raw_data"])
            if sources:
                st.subheader("Sources")
                for url in sources:
                    st.write(f"- [{url}]({url})")

            with st.expander("Raw research"):
                st.text(result["raw_data"])
    elif not submitted:
        st.info("Enter a topic and click **Run Analysis** to start.")

# ---------------- Benchmarks ----------------

with bench_tab:
    files = sorted(glob.glob("evals/result_*.json"))

    if not files:
        st.info("No benchmark results yet. Run `python evals/run_benchmark.py <label>`.")
    else:
        names = [os.path.basename(f)[len("result_"):-len(".json")] for f in files]
        label = st.selectbox("Benchmark run", names, index=len(names) - 1)

        with open(f"evals/result_{label}.json", encoding="utf-8") as f:
            rows = json.load(f)

        df = pd.DataFrame(rows)
        df["unsupported_final"] = df["unsupported"].apply(lambda u: len(u[-1]) if u else 0)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Queries", len(df))
        c2.metric("Avg first score", f"{df['first_score'].mean():.2f}")
        c3.metric(
            "Avg final score",
            f"{df['final_score'].mean():.2f}",
            f"{df['final_score'].mean() - df['first_score'].mean():+.2f}",
        )
        c4.metric("Avg rounds", f"{df['rounds'].mean():.1f}")

        st.bar_chart(
            df.set_index(df.index + 1)[["first_score", "final_score"]],
            stack=False,
        )

        st.dataframe(
            df[["query", "first_score", "final_score", "rounds", "unsupported_final"]],
            hide_index=True,
            column_config={
                "query": "Query",
                "first_score": st.column_config.NumberColumn("First", format="%.1f"),
                "final_score": st.column_config.ProgressColumn(
                    "Final", min_value=0, max_value=10, format="%.1f"
                ),
                "rounds": "Rounds",
                "unsupported_final": "Unsupported claims (last draft)",
            },
        )

        st.subheader("Inspect a report")
        pick = st.selectbox("Query", df["query"])
        row = df[df["query"] == pick].iloc[0]
        st.write(f"Scores by round: {', '.join(str(s) for s in row['scores'])}")
        with st.container(border=True):
            st.markdown(row["report"])
