import unittest

import app


class GenerativeStoryDnaTests(unittest.TestCase):
    def make_result(self, **overrides):
        engine = {
            "atmosphere": "mysterious",
            "theme": "loss_recovery",
            "location": "sea",
            "character": "traveler",
            "ending": "echo",
        }
        engine.update(overrides)
        return app.build_result({"engine": engine, "context": {}})

    def test_engine_creates_connected_four_part_dna(self):
        result = self.make_result(theme="forbidden_promise", location="cave", character="outsider")
        dna = result["generative_story_dna"]
        blueprint = result["narrative_blueprint"]
        for field in ("the_question", "the_lack", "the_cost", "the_irony"):
            self.assertTrue(dna[field])
            self.assertIn(dna[field], blueprint[field.replace("the_", "")])
        self.assertEqual(dna["theme"], "금기와 약속")
        self.assertEqual(dna["location"], "동굴")
        self.assertEqual(dna["character_type"], "마을에 들어온 이방인")

    def test_blueprint_defines_each_beat_as_a_dna_constraint(self):
        result = self.make_result(theme="transformation")
        beat_plan = result["narrative_blueprint"]["beat_plan"]
        self.assertEqual(list(beat_plan), ["Ki", "Shō", "Trial", "Crisis", "Climax", "Ketsu"])
        self.assertIn("결핍", beat_plan["Ki"])
        self.assertIn("대가", beat_plan["Trial"])
        self.assertIn("질문", beat_plan["Climax"])
        self.assertIn("결과", beat_plan["Ketsu"])

    def test_engine_returns_story_draft_and_source_modules(self):
        result = self.make_result(atmosphere="warm", theme="family_connection", ending="warm")
        self.assertEqual(result["analysis_method"], "generative story DNA baseline")
        self.assertEqual(len(result["retrieved"]), 5)
        self.assertGreater(len(result["generated"]["text"]), 100)
        self.assertIn("generative story DNA", result["generated"]["generation_mode"])
        self.assertIn("가족과 연결", result["generated"]["title"])


if __name__ == "__main__":
    unittest.main()
