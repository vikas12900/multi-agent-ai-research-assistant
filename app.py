import streamlit as st
from pipeline import run_pipeline

st.set_page_config(
    page_title="AI Research Analyst",
    page_icon="⚡"
)

st.title("⚡ AI Research Analyst")

query = st.text_input(
    "Enter a topic",
    value="Latest AI news"
)

if st.button("Run Analysis"):

    try:

        result = run_pipeline(query)

        st.subheader("📋 Research Tasks")

        for task in result["tasks"]:
            st.write("•", task)

        st.subheader("🧐 Critic History")

        for item in result["history"]:

            st.write(
                f"Iteration {item['iteration']} | Score: {item['score']}"
            )

            for improvement in item["improvements"]:
                st.write(f"   - {improvement}")

        st.subheader("🏆 Final Score")
        st.write(result["final_score"])

        st.subheader("📄 Final Report")
        st.write(result["report"])

        with st.expander("Raw Research"):
            st.write(result["raw_data"])

    except Exception as e:
        st.error(f"Pipeline failed: {e}")