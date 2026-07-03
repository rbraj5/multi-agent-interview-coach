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
            [
                "generate_questions",
                "evaluate_answers",
                "review_readiness",
                "practice_review",
                "build_feedback_plan",
                "export_session_log",
            ],
        )
        self.assertEqual(state["turns"][0].score, 0)
        self.assertGreater(state["turns"][1].score, 0)
        self.assertTrue(state["readiness_review"].requires_practice_review)
        self.assertGreaterEqual(len(state["trace_events"]), 5)
        self.assertIn("roadmap", state["session_log"])
        self.assertIn("readiness_review", state["session_log"])

    def test_strong_answers_skip_practice_review(self) -> None:
        answer = (
            "In my project, I used pandas because the data had missing values and inconsistent categories. "
            "For example, I tested median imputation, validated the result with metrics, and documented the tradeoff "
            "so that another user could reproduce the workflow."
        )

        state = run_interview_coach_workflow(
            "Junior Data Analyst",
            "Junior",
            "Python",
            [answer] * 5,
        )

        self.assertFalse(state["readiness_review"].requires_practice_review)
        self.assertNotIn("practice_review", state["completed_nodes"])
        self.assertGreaterEqual(state["readiness_review"].average_score, 4)

    def test_incomplete_session_is_flagged(self) -> None:
        state = run_interview_coach_workflow(
            "Junior Data Analyst",
            "Junior",
            "SQL",
            ["", "", ""],
        )

        self.assertTrue(state["readiness_review"].requires_practice_review)
        self.assertIn("answer(s) were missing", " ".join(state["readiness_review"].risk_flags))
        self.assertIn("practice_review", state["completed_nodes"])


if __name__ == "__main__":
    unittest.main()
