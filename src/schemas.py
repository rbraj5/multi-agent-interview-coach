from __future__ import annotations

from typing import TypedDict

from pydantic import BaseModel, Field


class Feedback(BaseModel):
    score: int
    message: str
    next_step: str


class InterviewTurn(BaseModel):
    question: str
    answer: str
    score: int
    feedback: str
    next_step: str


class FeedbackPlan(BaseModel):
    roadmap: list[str] = Field(default_factory=list)
    report: str


class InterviewCoachState(TypedDict, total=False):
    role: str
    level: str
    topic: str
    answers: list[str]
    questions: list[str]
    feedback_items: list[Feedback]
    turns: list[InterviewTurn]
    feedback_plan: FeedbackPlan
    session_log: dict
    execution_mode: str
    completed_nodes: list[str]
    warnings: list[str]
