from __future__ import annotations

from typing import TypedDict

from pydantic import BaseModel, Field


class Feedback(BaseModel):
    score: int
    message: str
    next_step: str
    signals: list[str] = Field(default_factory=list)


class InterviewTurn(BaseModel):
    question: str
    answer: str
    score: int
    feedback: str
    next_step: str


class FeedbackPlan(BaseModel):
    roadmap: list[str] = Field(default_factory=list)
    report: str


class ReadinessReview(BaseModel):
    status: str
    average_score: float
    requires_practice_review: bool
    weak_question_indexes: list[int] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    focus_areas: list[str] = Field(default_factory=list)


class TraceEvent(BaseModel):
    node: str
    summary: str


class InterviewCoachState(TypedDict, total=False):
    role: str
    level: str
    topic: str
    answers: list[str]
    questions: list[str]
    feedback_items: list[Feedback]
    turns: list[InterviewTurn]
    readiness_review: ReadinessReview
    feedback_plan: FeedbackPlan
    session_log: dict
    trace_events: list[TraceEvent]
    execution_mode: str
    completed_nodes: list[str]
    warnings: list[str]
