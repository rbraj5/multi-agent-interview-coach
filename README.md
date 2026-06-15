# Multi-Agent Interview Coach

A Streamlit app for practicing junior-level interviews with a small multi-agent workflow.

Agents:

- Question Generator
- Answer Evaluator
- Feedback Coach

The app works without paid APIs and saves a simple `interview_log.json` session file.

## Features

- Choose role, experience level, and topic
- Generate five practice questions
- Write answers directly in the app
- Receive per-answer feedback
- Get a final improvement roadmap
- Download the session log as JSON

## Project Structure

```text
multi-agent-interview-coach/
├── app.py
├── sample_data/
│   └── sample_interview_log.json
├── screenshots/
│   └── .gitkeep
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Usage

1. Select a target role, level, and topic.
2. Generate questions.
3. Write answers.
4. Review feedback and the final roadmap.
5. Download the JSON session log.

