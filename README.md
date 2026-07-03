# Multi-Agent Interview Coach

## Overview
Multi-Agent Interview Coach is a production-ready local container service for structured interview practice and coaching feedback. It combines LangGraph orchestration, deterministic rubric evaluation, Pydantic validation, FastAPI backend integration, Docker packaging, and optional LangChain/OpenAI synthesis.

The service supports coaching and readiness practice. It does not make hiring decisions.

## Production Use Case
The application supports mentoring, skills-development, and interview-preparation workflows where consistent feedback is useful across practice sessions. It generates role-specific questions, evaluates answers with a deterministic rubric, routes weak sessions through a practice-review branch, builds a feedback plan, and exports a structured session log.

## Architecture
- FastAPI exposes the workflow as a service API with OpenAPI documentation at `/docs`.
- LangGraph controls state and conditional practice-review routing.
- Deterministic tools generate questions, score answers, review readiness, and build a coaching roadmap.
- Pydantic validates API requests and structures responses.
- Docker packages the API as a production-ready local container.
- Trace events, completed nodes, request IDs, and warnings provide lightweight observability.
- LangSmith tracing can be enabled through environment variables when needed.

## LangGraph Workflow
```text
generate_questions -> evaluate_answers -> review_readiness
review_readiness -> practice_review? -> build_feedback_plan -> export_session_log
```

- `generate_questions`: creates role, level, and topic-specific practice questions.
- `evaluate_answers`: scores answers using detail, reasoning, and practical-context signals.
- `review_readiness`: checks average score, weak answers, and incomplete responses before coaching.
- `practice_review`: routes weak sessions through targeted practice guidance before final planning.
- `build_feedback_plan`: creates a deterministic or LLM-assisted improvement roadmap.
- `export_session_log`: writes a structured JSON session log for review.

## API Usage
Run locally, then open the interactive API docs:

```powershell
http://localhost:8000/docs
```

Health and metadata:

```powershell
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metadata
```

Workflow request:

```powershell
$body = @{
  role = "Junior Data Analyst"
  level = "Junior"
  topic = "Python"
  answers = @("I used pandas in a project because the data had missing values and I validated the result with metrics.")
} | ConvertTo-Json
curl -X POST http://localhost:8000/workflow -H "Content-Type: application/json" -d $body
```

The response includes `request_id`, `execution_mode`, `completed_nodes`, `trace_events`, `questions`, `turns`, `readiness_review`, `feedback_plan`, `session_log`, and `warnings`.

## Docker Run
Build and run the API container locally:

```powershell
docker build -t multi-agent-interview-coach:local .
docker run --rm -p 8000:8000 --env-file .env.example multi-agent-interview-coach:local
```

The Docker health check calls `/health`. The container starts the API with:

```powershell
uvicorn src.api:app --host 0.0.0.0 --port 8000
```

## Local Streamlit/CLI Demo
The production API does not replace the Streamlit demo.

```powershell
streamlit run app.py
```

## Configuration
Use `.env.example` as the configuration template:

```text
APP_ENV=local
APP_VERSION=0.1.0
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o-mini
LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LOG_LEVEL=INFO
```

No OpenAI or LangSmith configuration is required for deterministic operation. Do not commit secrets or cloud credentials.

## Testing
Run local checks:

```powershell
python -m compileall .
python -m unittest discover -s tests
docker build -t multi-agent-interview-coach:local .
```

The test suite includes workflow tests, FastAPI endpoint tests, and README contract tests that enforce the required documentation structure.

## Azure Container Apps Deployment Path
This repo is Azure Container Apps ready, but no cloud deployment is required for the local demo.

Example deployment path:

```powershell
az group create --name rg-agentic-ai-demo --location uksouth
az containerapp env create --name cae-agentic-ai-demo --resource-group rg-agentic-ai-demo --location uksouth
az containerapp create `
  --name interview-coach-api `
  --resource-group rg-agentic-ai-demo `
  --environment cae-agentic-ai-demo `
  --image <registry>/multi-agent-interview-coach:latest `
  --target-port 8000 `
  --ingress external `
  --env-vars APP_ENV=azure APP_VERSION=0.1.0 LOG_LEVEL=INFO
```

Configure secrets such as `OPENAI_API_KEY` through Azure Container Apps secret management, not in source control.

## Production Readiness Notes
- FastAPI backend available.
- Docker image buildable.
- Health and readiness endpoints available.
- Pydantic request/response validation.
- Deterministic fallback without API key.
- Optional LangChain/OpenAI synthesis.
- Trace events returned in API responses.
- CI validates compile/tests/Docker build.
- Azure Container Apps deployment path documented.

## Limitations and Next Steps
- Authentication and rate limiting are not implemented.
- Session logs are returned per request and are not persisted by the API.
- Azure deployment commands are documented but not executed here.
- Future extensions would add calibrated rubrics by role family, reviewer notes, consent controls, longitudinal progress tracking, and human review for high-stakes evaluation.
