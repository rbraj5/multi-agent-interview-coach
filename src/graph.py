from __future__ import annotations

import os

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from src.schemas import FeedbackPlan, InterviewCoachState
from src.tools import build_feedback_plan, evaluate_answers, export_session_log, generate_questions


def _completed(state: InterviewCoachState, node: str) -> list[str]:
    return [*state.get("completed_nodes", []), node]


def _question_node(state: InterviewCoachState) -> InterviewCoachState:
    return {
        "questions": generate_questions(state["role"], state["level"], state["topic"]),
        "completed_nodes": _completed(state, "generate_questions"),
    }


def _evaluation_node(state: InterviewCoachState) -> InterviewCoachState:
    feedback_items, turns = evaluate_answers(state["questions"], state["answers"])
    return {
        "feedback_items": feedback_items,
        "turns": turns,
        "completed_nodes": _completed(state, "evaluate_answers"),
    }


def _deterministic_plan(state: InterviewCoachState) -> FeedbackPlan:
    return build_feedback_plan(state["feedback_items"])


def _llm_plan(state: InterviewCoachState) -> tuple[FeedbackPlan, list[str]]:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        return _deterministic_plan(state), []

    try:
        from langchain_openai import ChatOpenAI

        base_plan = _deterministic_plan(state)
        model = ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)
        response = model.invoke(
            "Create a concise interview coaching report. "
            "Use only the structured feedback below. Do not make hiring decisions.\n\n"
            f"Role: {state['role']}\n"
            f"Level: {state['level']}\n"
            f"Topic: {state['topic']}\n"
            f"Turns: {[turn.model_dump() for turn in state['turns']]}\n"
            f"Roadmap: {base_plan.roadmap}\n"
        )
        return FeedbackPlan(roadmap=base_plan.roadmap, report=str(response.content)), []
    except Exception as exc:  # pragma: no cover
        return _deterministic_plan(state), [f"LLM synthesis failed; deterministic feedback used. Reason: {exc}"]


def _plan_node(state: InterviewCoachState) -> InterviewCoachState:
    feedback_plan, warnings = _llm_plan(state)
    execution_mode = "LLM-assisted synthesis" if os.getenv("OPENAI_API_KEY") and not warnings else "Deterministic fallback"
    return {
        "feedback_plan": feedback_plan,
        "warnings": [*state.get("warnings", []), *warnings],
        "execution_mode": execution_mode,
        "completed_nodes": _completed(state, "build_feedback_plan"),
    }


def _export_node(state: InterviewCoachState) -> InterviewCoachState:
    return {
        "session_log": export_session_log(
            state["role"],
            state["level"],
            state["topic"],
            state["turns"],
            state["feedback_plan"].roadmap,
        ),
        "completed_nodes": _completed(state, "export_session_log"),
    }


def build_graph():
    graph = StateGraph(InterviewCoachState)
    graph.add_node("generate_questions", _question_node)
    graph.add_node("evaluate_answers", _evaluation_node)
    graph.add_node("build_feedback_plan", _plan_node)
    graph.add_node("export_session_log", _export_node)
    graph.add_edge(START, "generate_questions")
    graph.add_edge("generate_questions", "evaluate_answers")
    graph.add_edge("evaluate_answers", "build_feedback_plan")
    graph.add_edge("build_feedback_plan", "export_session_log")
    graph.add_edge("export_session_log", END)
    return graph.compile()


def run_interview_coach_workflow(role: str, level: str, topic: str, answers: list[str]) -> InterviewCoachState:
    return build_graph().invoke(
        {
            "role": role,
            "level": level,
            "topic": topic,
            "answers": answers,
            "completed_nodes": [],
            "warnings": [],
            "execution_mode": "Deterministic fallback",
        }
    )
