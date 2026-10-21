"""Optional provider failures must preserve the offline story, without network I/O."""
import json
import os
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

import app


STORY = "달빛 우물\n\n여행자는 동굴에서 잃어버린 약속을 찾았다."


def response_payload(text=STORY):
    return {"status": "completed", "output": [
        {"type": "reasoning", "summary": []},
        {"type": "message", "role": "assistant", "status": "completed",
         "content": [{"type": "output_text", "text": text}]},
    ]}


class ProviderBoundaryTests(unittest.TestCase):
    def generate(self, raw=None, error=None):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = raw
        baseline = {"title": "기존 초안", "text": "자료 기반 규칙 초안"}
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only-never-sent"}), \
             patch.object(app.urllib.request, "urlopen", return_value=response, side_effect=error) as request:
            generated = app.generate_engine_folktale({}, {}, {}, baseline)
        request.assert_called_once()
        return generated

    def assert_fallback(self, generated):
        self.assertEqual(generated["title"], "기존 초안")
        self.assertEqual(generated["text"], "자료 기반 규칙 초안")
        self.assertEqual(generated["generation_status"], "fallback")
        self.assertEqual(generated["generation_provider"], "recombined baseline")
        self.assertNotIn("test-only-never-sent", generated["generation_notice"])
        self.assertNotIn("private-provider-detail", generated["generation_notice"])

    def test_completed_response_formats_preserve_title_and_body(self):
        for payload in (response_payload(), {"output_text": STORY}):
            with self.subTest(payload=payload):
                result = self.generate(json.dumps(payload).encode())
                self.assertEqual(result["generation_mode"], "LLM Generated")
                self.assertEqual(result["title"], "달빛 우물")
                self.assertEqual(result["text"], STORY.split("\n\n")[1])
                self.assertNotIn("generation_status", result)

    def test_provider_shapes_and_failed_or_incomplete_results_fall_back(self):
        invalid = [None, [], "private-provider-detail", 1,
                   {"output": None}, {"output": {}}, {"output": [None]},
                   {"output_text": 42}, {"output_text": " "},
                   {"status": "incomplete", "output_text": STORY},
                   {"status": "failed", "error": {"message": "private-provider-detail"}},
                   {"error": {"message": "private-provider-detail"}, "output_text": STORY}]
        for content in (None, 42, {}, [None], [{"type": "output_text", "text": {}}],
                        [{"type": "refusal", "refusal": "private-provider-detail"}]):
            payload = response_payload()
            payload["output"][1]["content"] = content
            invalid.append(payload)
        for field, value in (("role", "user"), ("status", "incomplete")):
            payload = response_payload()
            payload["output"][1][field] = value
            invalid.append(payload)
        for payload in invalid:
            with self.subTest(payload=payload):
                self.assert_fallback(self.generate(json.dumps(payload).encode()))

    def test_invalid_encoding_json_and_network_errors_fall_back(self):
        for raw in (b"\xff", b"{broken-json"):
            with self.subTest(raw=raw):
                self.assert_fallback(self.generate(raw))
        errors = [TimeoutError("private-provider-detail"),
                  urllib.error.URLError("private-provider-detail"),
                  urllib.error.HTTPError(app.OPENAI_URL, 429, "private-provider-detail", {}, None)]
        for error in errors:
            with self.subTest(error=type(error).__name__):
                self.assert_fallback(self.generate(error=error))

    def test_empty_or_title_only_story_falls_back_instead_of_claiming_success(self):
        for text in ("", "  ", "제목뿐", "#\n\n본문뿐"):
            with self.subTest(text=text):
                self.assert_fallback(self.generate(json.dumps(response_payload(text)).encode()))


if __name__ == "__main__":
    unittest.main()
