from __future__ import annotations

import os

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from src.schemas import FeedbackPlan, InterviewCoachState, TraceEvent
from src.tools import build_feedback_plan, evaluate_answers, export_session_log, generate_questions, review_readiness


def _completed(state: InterviewCoachState, node: str) -> list[str]:
    return [*state.get("completed_nodes", []), node]


def _trace(state: InterviewCoachState, node: str, summary: str) -> list[TraceEvent]:
    return [*state.get("trace_events", []), TraceEvent(node=node, summary=summary)]


def _question_node(state: InterviewCoachState) -> InterviewCoachState:
    questions = generate_questions(state["role"], state["level"], state["topic"])
    return {
        "questions": questions,
        "completed_nodes": _completed(state, "generate_questions"),
        "trace_events": _trace(
            state,
            "generate_questions",
            f"Generated {len(questions)} {state['topic']} questions for {state['level']} {state['role']}.",
        ),
    }


def _evaluation_node(state: InterviewCoachState) -> InterviewCoachState:
    feedback_items, turns = evaluate_answers(state["questions"], state["answers"])
    return {
        "feedback_items": feedback_items,
        "turns": turns,
        "completed_nodes": _completed(state, "evaluate_answers"),
        "trace_events": _trace(
            state,
            "evaluate_answers",
            f"Evaluated {len(turns)} answer(s); {sum(1 for item in feedback_items if item.score < 3)} need improvement.",
        ),
    }


def _readiness_node(state: InterviewCoachState) -> InterviewCoachState:
    readiness = review_readiness(state["feedback_items"])
    return {
        "readiness_review": readiness,
        "completed_nodes": _completed(state, "review_readiness"),
        "trace_events": _trace(state, "review_readiness", readiness.status),
    }


def _route_after_readiness(state: InterviewCoachState) -> str:
    return "practice_review" if state["readiness_review"].requires_practice_review else "build_feedback_plan"


def _practice_review_node(state: InterviewCoachState) -> InterviewCoachState:
    return {
        "completed_nodes": _completed(state, "practice_review"),
        "trace_events": _trace(
            state,
            "practice_review",
            "Weak or incomplete answers were routed through targeted practice review before planning.",
        ),
    }


def _deterministic_plan(state: InterviewCoachState) -> FeedbackPlan:
    return build_feedback_plan(state["feedback_items"], state["readiness_review"])


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
            f"Readiness review: {state['readiness_review'].model_dump()}\n"
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
        "trace_events": _trace(
            state,
            "build_feedback_plan",
            f"Generated {execution_mode.lower()} coaching plan with {len(feedback_plan.roadmap)} roadmap items.",
        ),
    }


def _export_node(state: InterviewCoachState) -> InterviewCoachState:
    return {
        "session_log": export_session_log(
            state["role"],
            state["level"],
            state["topic"],
            state["turns"],
            state["feedback_plan"].roadmap,
            state["readiness_review"],
        ),
        "completed_nodes": _completed(state, "export_session_log"),
        "trace_events": _trace(state, "export_session_log", "Exported structured session log."),
    }


def build_graph():
    graph = StateGraph(InterviewCoachState)
    graph.add_node("generate_questions", _question_node)
    graph.add_node("evaluate_answers", _evaluation_node)
    graph.add_node("review_readiness", _readiness_node)
    graph.add_node("practice_review", _practice_review_node)
    graph.add_node("build_feedback_plan", _plan_node)
    graph.add_node("export_session_log", _export_node)
    graph.add_edge(START, "generate_questions")
    graph.add_edge("generate_questions", "evaluate_answers")
    graph.add_edge("evaluate_answers", "review_readiness")
    graph.add_conditional_edges(
        "review_readiness",
        _route_after_readiness,
        {
            "practice_review": "practice_review",
            "build_feedback_plan": "build_feedback_plan",
        },
    )
    graph.add_edge("practice_review", "build_feedback_plan")
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
            "trace_events": [],
            "warnings": [],
            "execution_mode": "Deterministic fallback",
        }
    )
