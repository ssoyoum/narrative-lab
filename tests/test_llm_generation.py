import os
import unittest
from unittest.mock import patch

import app


ENGINE = {
    "atmosphere": "mysterious",
    "theme": "forbidden_promise",
    "location": "cave",
    "character": "traveler",
    "ending": "echo",
}


class LlmGenerationTests(unittest.TestCase):
    def make_engine_result(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": ""}, clear=False), patch.object(app, "OPENAI_API_KEY", ""):
            return app.build_result({"engine": ENGINE, "context": {}})

    def test_abstract_story_beat_omits_source_prose(self):
        beat = {
            "beat": "setup",
            "event_text": "원본 설화의 고유한 문장과 인물",
            "source_story": "원천 설화 제목",
            "structural_attributes": {"function": "징조", "conflict": "금기"},
        }
        abstracted = app.abstract_story_beat(beat)
        self.assertNotIn(beat["event_text"], str(abstracted))
        self.assertNotIn(beat["source_story"], str(abstracted))
        self.assertTrue(abstracted["patterns"])

    def test_generation_prompt_contains_constraints_without_bound_event_text(self):
        result = self.make_engine_result()
        prompt = app.build_generation_prompt(
            result["generative_story_dna"]["user_intent"],
            result["generative_story_dna"],
            result["narrative_blueprint"],
            result["narrative_blueprint"]["beat_plan"],
            result["bound_beats"],
        )
        for section in ("[USER INTENT]", "[STORY DNA]", "[NARRATIVE BLUEPRINT]", "[BEAT PLAN]", "[FOLKTALE PATTERNS]"):
            self.assertIn(section, prompt)
        for field in ("Question", "Lack", "Cost", "Irony"):
            self.assertIn(field, prompt)
        for bound in result["bound_beats"].values():
            self.assertNotIn(bound["event_text"], prompt)

    def test_llm_generation_parses_provider_response(self):
        result = self.make_engine_result()
        with patch.object(app, "call_llm", return_value="달빛 우물\n\n새로운 첫 문장이다.\n\n주인공은 자신의 선택을 받아들였다.") as call:
            generated = app.generate_llm_folktale(
                result["generative_story_dna"]["user_intent"],
                result["generative_story_dna"],
                result["narrative_blueprint"],
                result["narrative_blueprint"]["beat_plan"],
                result["bound_beats"],
            )
        self.assertEqual(generated["generation_mode"], "LLM Generated")
        self.assertEqual(generated["title"], "달빛 우물")
        self.assertIn("새로운 첫 문장이다.", generated["text"])
        call.assert_called_once()

    def test_missing_api_key_keeps_server_result_with_baseline_fallback(self):
        result = self.make_engine_result()
        generated = result["generated"]
        self.assertEqual(generated["generation_status"], "fallback")
        self.assertIn("recombined baseline", generated["generation_mode"])
        self.assertIn("OPENAI_API_KEY", generated["generation_notice"])
        self.assertEqual(generated["source_patterns_count"], 6)


if __name__ == "__main__":
    unittest.main()
