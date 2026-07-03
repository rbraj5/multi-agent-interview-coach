# Multi-Agent Interview Coach

Multi-Agent Interview Coach is a Streamlit application for structured interview practice and feedback generation. The application uses LangGraph to orchestrate question generation, answer evaluation, feedback planning, and session-log export, with optional LangChain/OpenAI synthesis for coaching reports.

## Operational Context

The system supports interview preparation, mentoring, and skills-development sessions where consistent feedback is useful across candidates or practice rounds. The scoring rubric is deterministic so feedback remains explainable and repeatable.

## LangGraph Workflow

```text
generate_questions -> evaluate_answers -> review_readiness
review_readiness -> practice_review? -> build_feedback_plan -> export_session_log
```

- **generate_questions:** creates role, level, and topic-specific practice questions.
- **evaluate_answers:** scores answers using detail, reasoning, and practical-context signals.
- **review_readiness:** checks average score, weak answers, and incomplete responses before coaching.
- **practice_review:** routes weak sessions through targeted practice guidance before final planning.
- **build_feedback_plan:** creates a deterministic or LLM-assisted improvement roadmap.
- **export_session_log:** writes a structured JSON session log for review.

## Execution Modes

- **Deterministic fallback:** runs without API keys and generates feedback from rubric scores.
- **LLM-assisted synthesis:** uses `langchain-openai` when `OPENAI_API_KEY` is configured. The model receives structured feedback and does not make hiring decisions.

## Capabilities

- Role, level, and topic configuration
- Five generated practice questions per session
- Structured answer capture
- LangGraph node execution trace in the UI
- Per-answer feedback and scoring
- Conditional readiness routing for weak or incomplete sessions
- Risk flags and focus areas for targeted practice
- Final improvement roadmap
- Downloadable JSON session log

## Production Design Notes

The application keeps interview evaluation deterministic by default: rubric scoring, readiness routing, and session logs are produced locally and are reproducible. Optional LLM synthesis is limited to wording the final coaching report from structured feedback, not making hiring decisions.

In a production mentoring or talent-development workflow, the next additions would be calibrated rubrics by role family, reviewer notes, consent controls, longitudinal progress tracking, and human review for high-stakes evaluation.

## Repository Structure

```text
multi-agent-interview-coach/
|-- app.py
|-- src/
|   |-- __init__.py
|   |-- graph.py
|   |-- schemas.py
|   `-- tools.py
|-- sample_data/
|   `-- sample_interview_log.json
|-- .env.example
|-- .gitignore
|-- LICENSE
|-- README.md
`-- requirements.txt
```

## Local Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Notes

Feedback is generated through deterministic scoring rules by default. LLM synthesis is an optional coaching layer, not a replacement for human evaluation.
