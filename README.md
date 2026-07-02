# Multi-Agent Interview Coach

Multi-Agent Interview Coach is a Streamlit application for structured interview practice and feedback generation. It coordinates question generation, answer evaluation, and improvement planning into a repeatable review workflow.

## Operational Context

The system supports interview preparation, mentoring, and skills-development sessions where consistent feedback is useful across candidates or practice rounds. It stores a local JSON session log for auditability and follow-up review.

## Agent Workflow

- **Question Generator:** creates role, level, and topic-specific practice questions.
- **Answer Evaluator:** scores answers using detail, reasoning, and practical-context signals.
- **Feedback Coach:** produces an improvement roadmap based on the evaluated answers.

## Capabilities

- Role, level, and topic configuration
- Five generated practice questions per session
- Structured answer capture
- Per-answer feedback and scoring
- Final improvement roadmap
- Downloadable JSON session log

## Repository Structure

```text
multi-agent-interview-coach/
|-- app.py
|-- sample_data/
|   `-- sample_interview_log.json
|-- screenshots/
|   `-- .gitkeep
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

## Usage Flow

1. Launch the Streamlit application.
2. Select the target role, experience level, and interview topic.
3. Generate the practice question set.
4. Capture candidate answers.
5. Review feedback, improvement roadmap, and exported session log.

## Notes

Feedback is generated through deterministic scoring rules. The output is designed as a coaching aid rather than a final assessment of candidate suitability.
