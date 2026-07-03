from __future__ import annotations

import os
import unittest

from fastapi.testclient import TestClient

from src.api import app


class InterviewCoachApiTest(unittest.TestCase):
    def setUp(self) -> None:
        os.environ.pop("OPENAI_API_KEY", None)
        self.client = TestClient(app)

    def test_health_ready_and_metadata(self) -> None:
        self.assertEqual(self.client.get("/health").status_code, 200)
        self.assertEqual(self.client.get("/ready").status_code, 200)
        metadata = self.client.get("/metadata").json()
        self.assertIn("review_readiness", metadata["workflow_nodes"])
        self.assertIn("Python", metadata["supported_topics"])

    def test_workflow_returns_structured_response(self) -> None:
        response = self.client.post(
            "/workflow",
            json={
                "role": "Junior Data Analyst",
                "level": "Junior",
                "topic": "Python",
                "answers": ["I used pandas in a project because data quality mattered and I validated the result with metrics."],
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["execution_mode"], "Deterministic fallback")
        self.assertIn("request_id", payload)
        self.assertIn("review_readiness", payload["completed_nodes"])
        self.assertIn("readiness_review", payload)
        self.assertIn("session_log", payload)

    def test_invalid_payload_is_rejected(self) -> None:
        self.assertEqual(
            self.client.post(
                "/workflow",
                json={"role": "", "level": "Junior", "topic": "Python", "answers": ["answer"]},
            ).status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()
