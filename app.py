from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import streamlit as st


LOG_PATH = Path("interview_log.json")

QUESTION_BANK = {
    "Python": [
        "How do lists and dictionaries differ in Python?",
        "How would you handle missing values in a pandas DataFrame?",
        "What is the difference between a function and a method?",
        "How would you debug a script that fails only for one input file?",
        "How do you make a small Python project easier to maintain?",
    ],
    "SQL": [
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "How would you find duplicate records in a table?",
        "When would you use GROUP BY?",
        "How would you check whether a query result is correct?",
        "What can make a SQL query slow?",
    ],
    "Machine Learning": [
        "How do you split data for model evaluation?",
        "What is overfitting?",
        "Why is feature scaling useful for some models?",
        "How would you evaluate a classification model?",
        "How would you explain a model result to a non-technical user?",
    ],
    "General Software": [
        "How do you approach a bug you have not seen before?",
        "What makes code readable?",
        "How do you use Git in a small project?",
        "How would you test a simple data processing function?",
        "Tell me about a project you improved after feedback.",
    ],
}


@dataclass
class Feedback:
    score: int
    message: str
    next_step: str


def question_generator(role: str, level: str, topic: str) -> list[str]:
    base_questions = QUESTION_BANK.get(topic, QUESTION_BANK["General Software"])
    return [f"For a {level} {role}: {question}" for question in base_questions]


def answer_evaluator(answer: str) -> Feedback:
    cleaned = answer.strip()
    if not cleaned:
        return Feedback(0, "No answer provided.", "Write a short answer with one concrete example.")

    score = 2
    positives = []
    if len(cleaned.split()) >= 25:
        score += 1
        positives.append("enough detail")
    if any(word in cleaned.lower() for word in ["because", "for example", "when", "so that"]):
        score += 1
        positives.append("some reasoning")
    if any(word in cleaned.lower() for word in ["project", "data", "user", "test", "metric", "result"]):
        score += 1
        positives.append("practical context")

    score = min(score, 5)
    if positives:
        message = f"Good signs: {', '.join(positives)}."
    else:
        message = "The answer is understandable but needs more evidence."

    next_step = "Add a specific project example, explain the tradeoff, and mention how you checked the result."
    return Feedback(score, message, next_step)


def feedback_coach(feedback_items: list[Feedback]) -> list[str]:
    if not feedback_items:
        return ["Answer at least one question to receive a roadmap."]

    average = sum(item.score for item in feedback_items) / len(feedback_items)
    roadmap = []
    if average < 3:
        roadmap.append("Practice giving answers in three parts: situation, action, result.")
        roadmap.append("Prepare two project examples before the interview.")
    else:
        roadmap.append("Keep using concrete examples and add measurable outcomes where possible.")
        roadmap.append("Practice follow-up questions that challenge your assumptions.")
    roadmap.append("Review weak answers and rewrite them with one technical detail and one business outcome.")
    return roadmap


def build_session_log(role: str, level: str, topic: str, questions: list[str], answers: list[str]) -> dict:
    turns = []
    feedback_items = []
    for question, answer in zip(questions, answers):
        feedback = answer_evaluator(answer)
        feedback_items.append(feedback)
        turns.append(
            {
                "question": question,
                "answer": answer,
                "score": feedback.score,
                "feedback": feedback.message,
                "next_step": feedback.next_step,
            }
        )

    return {
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "role": role,
        "level": level,
        "topic": topic,
        "turns": turns,
        "roadmap": feedback_coach(feedback_items),
    }


def main() -> None:
    st.set_page_config(page_title="Multi-Agent Interview Coach", page_icon="🎙️", layout="wide")
    st.title("Multi-Agent Interview Coach")

    role = st.text_input("Target role", "Junior Data Analyst")
    level = st.selectbox("Experience level", ["Junior", "Entry Level", "Graduate", "1-2 Years"])
    topic = st.selectbox("Topic", sorted(QUESTION_BANK))

    questions = question_generator(role, level, topic)
    answers = []

    st.subheader("Question Generator")
    for index, question in enumerate(questions, start=1):
        st.markdown(f"**Question {index}.** {question}")
        answers.append(st.text_area(f"Your answer {index}", key=f"answer_{index}", height=90))

    if st.button("Evaluate answers", type="primary"):
        session_log = build_session_log(role, level, topic, questions, answers)
        LOG_PATH.write_text(json.dumps(session_log, indent=2), encoding="utf-8")

        st.subheader("Answer Evaluator")
        for index, turn in enumerate(session_log["turns"], start=1):
            with st.expander(f"Feedback {index}", expanded=True):
                st.metric("Score", f"{turn['score']}/5")
                st.write(turn["feedback"])
                st.write(turn["next_step"])

        st.subheader("Feedback Coach")
        for item in session_log["roadmap"]:
            st.markdown(f"- {item}")

        payload = json.dumps(session_log, indent=2)
        st.download_button("Download interview_log.json", payload, "interview_log.json")


if __name__ == "__main__":
    main()
