from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.graph import run_interview_coach_workflow
from src.tools import QUESTION_BANK, generate_questions

LOG_PATH = Path("interview_log.json")


def main() -> None:
    st.set_page_config(page_title="Multi-Agent Interview Coach", layout="wide")
    st.title("Multi-Agent Interview Coach")

    role = st.text_input("Target role", "Junior Data Analyst")
    level = st.selectbox("Experience level", ["Junior", "Entry Level", "Graduate", "1-2 Years"])
    topic = st.selectbox("Topic", sorted(QUESTION_BANK))

    questions = generate_questions(role, level, topic)
    answers = []

    st.subheader("Question Generator")
    for index, question in enumerate(questions, start=1):
        st.markdown(f"**Question {index}.** {question}")
        answers.append(st.text_area(f"Candidate answer {index}", key=f"answer_{index}", height=90))

    if st.button("Evaluate answers", type="primary"):
        state = run_interview_coach_workflow(role, level, topic, answers)
        session_log = state["session_log"]
        LOG_PATH.write_text(json.dumps(session_log, indent=2), encoding="utf-8")

        st.caption(f"Execution mode: {state['execution_mode']}")
        st.write("Completed graph nodes:", " -> ".join(state["completed_nodes"]))

        if state.get("warnings"):
            for warning in state["warnings"]:
                st.warning(warning)

        st.subheader("Answer Evaluator")
        for index, turn in enumerate(state["turns"], start=1):
            with st.expander(f"Feedback {index}", expanded=True):
                st.metric("Score", f"{turn.score}/5")
                st.write(turn.feedback)
                st.write(turn.next_step)

        st.subheader("Feedback Coach")
        st.markdown(state["feedback_plan"].report)
        for item in state["feedback_plan"].roadmap:
            st.markdown(f"- {item}")

        payload = json.dumps(session_log, indent=2)
        st.download_button("Download interview_log.json", payload, "interview_log.json")


if __name__ == "__main__":
    main()
