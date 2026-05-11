import os
import unittest

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

import app as study_buddy


class _FakeStream:
    def __init__(self, text):
        self.text_stream = [text]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeMessages:
    def __init__(self):
        self.calls = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return _FakeStream("# Outline\n\n- Paragraph 1: establish the argument.")


class _FakeClient:
    def __init__(self):
        self.messages = _FakeMessages()


class PlannerBackendTest(unittest.TestCase):
    def setUp(self):
        self.original_client = study_buddy.client
        self.fake_client = _FakeClient()
        study_buddy.client = self.fake_client
        self.client = study_buddy.app.test_client()

    def tearDown(self):
        study_buddy.client = self.original_client

    def test_plan_rejects_empty_assignment_text(self):
        res = self.client.post("/api/plan", json={"assignment": "   "})

        self.assertEqual(res.status_code, 400)
        self.assertIn("No assignment text provided", res.get_json()["error"])

    def test_plan_streams_outline_and_uses_context(self):
        res = self.client.post("/api/plan", json={
            "assignment": "Write a 1500 word essay on monetary policy.",
            "target_word_count": "1500",
            "context": {
                "subject": "Economics",
                "type": "Essay",
                "topic": "Monetary policy",
                "notes": "Second-year undergraduate",
            },
        })

        self.assertEqual(res.status_code, 200)
        self.assertIn("# Outline", res.get_data(as_text=True))
        call = self.fake_client.messages.calls[0]
        self.assertEqual(call["model"], "claude-sonnet-4-6")
        self.assertEqual(call["system"][0]["cache_control"]["type"], "ephemeral")
        self.assertIn("1500", call["messages"][0]["content"])
        self.assertIn("Economics", call["messages"][0]["content"])
        self.assertIn("paragraph-level essay outline", call["system"][0]["text"])

    def test_draft_rejects_empty_text(self):
        res = self.client.post("/api/draft", json={"text": "   \n\n  "})

        self.assertEqual(res.status_code, 400)
        self.assertIn("No draft text provided", res.get_json()["error"])

    def test_draft_converts_pasted_text_to_paragraphs(self):
        res = self.client.post("/api/draft", json={
            "text": " First paragraph. \r\nstill first.\n\nSecond paragraph.\n\n  Third paragraph.  "
        })

        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["paragraphs"], [
            "First paragraph.\nstill first.",
            "Second paragraph.",
            "Third paragraph.",
        ])
        self.assertFalse(data["truncated"])
        self.assertEqual(data["char_count"], sum(len(p) for p in data["paragraphs"]))

    def test_plain_text_without_blank_lines_falls_back_to_lines(self):
        self.assertEqual(
            study_buddy.parse_plain_text("One line\nSecond line\n  \n"),
            ["One line", "Second line"],
        )


if __name__ == "__main__":
    unittest.main()
