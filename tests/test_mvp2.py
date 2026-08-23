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
        source_ids = {module["source_story"] for module in result["retrieved"]}
        self.assertEqual(len(source_ids), 1)
        self.assertEqual(result["narrative_blueprint"]["source_pack"]["source_story_title"], next(iter(source_ids)))
        self.assertGreater(len(result["generated"]["text"]), 100)
        self.assertIn("generative story DNA", result["generated"]["generation_mode"])
        self.assertIn("가족과 연결", result["generated"]["title"])

    def test_each_beat_is_bound_to_a_dna_role_and_source_story(self):
        result = self.make_result(theme="human_nature", location="forest")
        bound = result["bound_beats"]
        self.assertEqual(list(bound), ["Ki", "Shō", "Trial", "Crisis", "Climax", "Ketsu"])
        self.assertEqual(bound["Ki"]["dna_focus"], "the_lack")
        self.assertEqual(bound["Trial"]["dna_focus"], "the_cost")
        self.assertEqual(bound["Crisis"]["dna_focus"], "the_irony")
        source_ids = {item["source_story_id"] for item in bound.values()}
        self.assertEqual(len(source_ids), 1)
        self.assertTrue(any(item["event_text"] in result["generated"]["text"] for item in bound.values()))


if __name__ == "__main__":
    unittest.main()
