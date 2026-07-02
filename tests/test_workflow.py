from __future__ import annotations

import os
import unittest

from src.graph import run_interview_coach_workflow


class InterviewCoachWorkflowTest(unittest.TestCase):
    def setUp(self) -> None:
        os.environ.pop("OPENAI_API_KEY", None)

    def test_empty_and_detailed_answers_are_scored(self) -> None:
        state = run_interview_coach_workflow(
            "Junior Data Analyst",
            "Junior",
            "Python",
            [
                "",
                "I used pandas in a project because the data had missing values, so I tested median imputation and checked the result with validation metrics.",
            ],
        )

        self.assertEqual(state["execution_mode"], "Deterministic fallback")
        self.assertEqual(
            state["completed_nodes"],
            ["generate_questions", "evaluate_answers", "build_feedback_plan", "export_session_log"],
        )
        self.assertEqual(state["turns"][0].score, 0)
        self.assertGreater(state["turns"][1].score, 0)
        self.assertIn("roadmap", state["session_log"])


if __name__ == "__main__":
    unittest.main()
