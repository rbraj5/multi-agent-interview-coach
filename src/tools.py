from __future__ import annotations

from datetime import datetime

from src.schemas import Feedback, FeedbackPlan, InterviewTurn

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
        "How would you explain a model result to a non-technical stakeholder?",
    ],
    "General Software": [
        "How do you approach a bug you have not seen before?",
        "What makes code readable?",
        "How do you use Git in a small project?",
        "How would you test a simple data processing function?",
        "Tell me about a project you improved after feedback.",
    ],
}


def generate_questions(role: str, level: str, topic: str) -> list[str]:
    base_questions = QUESTION_BANK.get(topic, QUESTION_BANK["General Software"])
    return [f"For a {level} {role}: {question}" for question in base_questions]


def evaluate_answer(answer: str) -> Feedback:
    cleaned = answer.strip()
    if not cleaned:
        return Feedback(score=0, message="No answer provided.", next_step="Write a short answer with one concrete example.")

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
    message = f"Good signs: {', '.join(positives)}." if positives else "The answer is understandable but needs more evidence."
    next_step = "Add a specific project example, explain the tradeoff, and mention how the result was checked."
    return Feedback(score=score, message=message, next_step=next_step)


def evaluate_answers(questions: list[str], answers: list[str]) -> tuple[list[Feedback], list[InterviewTurn]]:
    feedback_items: list[Feedback] = []
    turns: list[InterviewTurn] = []
    for question, answer in zip(questions, answers):
        feedback = evaluate_answer(answer)
        feedback_items.append(feedback)
        turns.append(
            InterviewTurn(
                question=question,
                answer=answer,
                score=feedback.score,
                feedback=feedback.message,
                next_step=feedback.next_step,
            )
        )
    return feedback_items, turns


def build_feedback_plan(feedback_items: list[Feedback]) -> FeedbackPlan:
    if not feedback_items:
        roadmap = ["Answer at least one question to receive a roadmap."]
    else:
        average = sum(item.score for item in feedback_items) / len(feedback_items)
        roadmap = []
        if average < 3:
            roadmap.append("Practice giving answers in three parts: situation, action, result.")
            roadmap.append("Prepare two project examples before the interview.")
        else:
            roadmap.append("Keep using concrete examples and add measurable outcomes where possible.")
            roadmap.append("Practice follow-up questions that challenge the stated assumptions.")
        roadmap.append("Review weak answers and rewrite them with one technical detail and one business outcome.")

    report = "\n".join(["# Interview Feedback Plan", "", "## Roadmap", *[f"- {item}" for item in roadmap]])
    return FeedbackPlan(roadmap=roadmap, report=report)


def export_session_log(role: str, level: str, topic: str, turns: list[InterviewTurn], roadmap: list[str]) -> dict:
    return {
        "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "role": role,
        "level": level,
        "topic": topic,
        "turns": [turn.model_dump() for turn in turns],
        "roadmap": roadmap,
    }
