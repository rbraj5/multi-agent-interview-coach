from __future__ import annotations

import logging
import os
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.graph import run_interview_coach_workflow
from src.tools import QUESTION_BANK

PROJECT_NAME = "Multi-Agent Interview Coach"
WORKFLOW_NODES = [
    "generate_questions",
    "evaluate_answers",
    "review_readiness",
    "practice_review",
    "build_feedback_plan",
    "export_session_log",
]

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("interview_coach_api")

app = FastAPI(
    title=PROJECT_NAME,
    version=os.getenv("APP_VERSION", "0.1.0"),
    description="Production-ready FastAPI wrapper for the LangGraph interview coaching workflow.",
)


class HealthResponse(BaseModel):
    service: str
    version: str
    status: str
    environment: str


class MetadataResponse(BaseModel):
    service: str
    workflow_nodes: list[str]
    execution_modes: list[str]
    supported_topics: list[str]
    llm_configured: bool


class InterviewWorkflowRequest(BaseModel):
    role: str = Field(..., min_length=1)
    level: str = Field(..., min_length=1)
    topic: str = Field(..., min_length=1)
    answers: list[str] = Field(..., min_length=1)


class InterviewWorkflowResponse(BaseModel):
    request_id: str
    execution_mode: str
    completed_nodes: list[str]
    trace_events: list[dict]
    warnings: list[str]
    questions: list[str]
    turns: list[dict]
    readiness_review: dict
    feedback_plan: dict
    session_log: dict


@app.get("/health", response_model=HealthResponse, summary="Container health check")
def health() -> HealthResponse:
    return HealthResponse(
        service=PROJECT_NAME,
        version=os.getenv("APP_VERSION", "0.1.0"),
        status="healthy",
        environment=os.getenv("APP_ENV", "local"),
    )


@app.get("/ready", response_model=HealthResponse, summary="Runtime readiness check")
def ready() -> HealthResponse:
    return HealthResponse(
        service=PROJECT_NAME,
        version=os.getenv("APP_VERSION", "0.1.0"),
        status="ready",
        environment=os.getenv("APP_ENV", "local"),
    )


@app.get("/metadata", response_model=MetadataResponse, summary="Workflow metadata")
def metadata() -> MetadataResponse:
    return MetadataResponse(
        service=PROJECT_NAME,
        workflow_nodes=WORKFLOW_NODES,
        execution_modes=["Deterministic fallback", "LLM-assisted synthesis"],
        supported_topics=sorted(QUESTION_BANK),
        llm_configured=bool(os.getenv("OPENAI_API_KEY")),
    )


@app.post("/workflow", response_model=InterviewWorkflowResponse, summary="Run the LangGraph interview coaching workflow")
def workflow(payload: InterviewWorkflowRequest) -> InterviewWorkflowResponse:
    request_id = str(uuid4())
    logger.info("running interview coach workflow request_id=%s topic=%s", request_id, payload.topic)
    state = run_interview_coach_workflow(payload.role, payload.level, payload.topic, payload.answers)
    return InterviewWorkflowResponse(
        request_id=request_id,
        execution_mode=state["execution_mode"],
        completed_nodes=state["completed_nodes"],
        trace_events=[event.model_dump() for event in state.get("trace_events", [])],
        warnings=state.get("warnings", []),
        questions=state["questions"],
        turns=[turn.model_dump() for turn in state.get("turns", [])],
        readiness_review=state["readiness_review"].model_dump(),
        feedback_plan=state["feedback_plan"].model_dump(),
        session_log=state["session_log"],
    )
