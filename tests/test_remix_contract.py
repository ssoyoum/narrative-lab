import unittest
from unittest.mock import patch
import app


class RemixContractTests(unittest.TestCase):
    def bind(self, overrides):
        dna = app.build_generative_story_dna({"theme": "loss_recovery", "location": "sea"})
        blueprint = app.build_narrative_blueprint({}, dna)
        return app.bind_story_pack_to_dna("base", dna, blueprint, {}, {}, overrides)

    def setUp(self):
        self.beats = [
            dict(id="base-ki", story_id="base", story_title="Base", beat="setup", raw_beat="Ki", event_text="start", search_text="start"),
            dict(id="other-climax", story_id="other", story_title="Other", beat="climax", raw_beat="Climax", event_text="choice", search_text="choice"),
        ]

    def test_valid_override_fills_beat_missing_from_base_pack(self):
        with patch.object(app, "BEATS", self.beats):
            bound = self.bind({"Climax": "other-climax"})
        self.assertEqual(bound["Climax"]["module_id"], "other-climax")
        self.assertEqual(bound["Climax"]["source_story_id"], "other")
        self.assertNotIn("module_id", bound["Trial"])

    def test_invalid_requests_are_rejected_instead_of_claiming_remix_applied(self):
        with patch.object(app, "BEATS", self.beats):
            for overrides in ({"bogus": "base-ki"}, {"Ki": "missing"}, {"Ki": "other-climax"}):
                with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                    self.bind(overrides)

    def test_no_override_keeps_missing_evidence_explicit(self):
        with patch.object(app, "BEATS", self.beats):
            bound = self.bind({})
        self.assertEqual(bound["Climax"]["score"], 0)
        self.assertNotIn("module_id", bound["Climax"])
