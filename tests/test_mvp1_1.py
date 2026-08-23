import unittest

import app


class PersonalNarrativeContextTests(unittest.TestCase):
    def test_context_is_not_fixed_to_the_default_jeju_location(self):
        context = app.analyze_personal_context("나는 코인트레이더야. 하락장을 피해 포항으로 도피했다.")
        self.assertEqual(context["setting"], "포항")
        self.assertIn("loss", context["wounds"])
        self.assertIn("rest", context["desires"])

    def test_result_contains_resonant_story_modules(self):
        result = app.build_result({
            "story": "퇴사 후 혼자 바닷가 마을에 머물며 다음 방향을 찾고 있다.",
            "context": {"location": "", "mood": "쓸쓸한", "tone": "잔잔한", "ending": "열린 결말"},
        })
        self.assertEqual(result["data_source"]["stories"], 246)
        self.assertEqual(len(result["retrieved"]), 5)
        self.assertTrue(all(item["source_story"] for item in result["retrieved"]))
        self.assertTrue(result["generated"]["controls"]["location"])

    def test_guided_checkin_can_run_without_free_text(self):
        result = app.build_result({
            "story": "",
            "survey": {"situation": "pressure", "emotion": "anxiety", "desire": "rest", "landscape": "바다"},
            "context": {"location": "포항", "mood": "긴장되는", "tone": "서정적인", "ending": "열린 결말"},
        })
        self.assertEqual(result["analysis"]["personal_context"]["method"], "guided narrative check-in")
        self.assertIn("fear", result["analysis"]["personal_context"]["wounds"])
        self.assertEqual(result["generated"]["controls"]["location"], "포항")

    def test_metaphor_checkin_preserves_scene_and_time(self):
        result = app.build_result({
            "story": "",
            "survey": {
                "scene": "crossroads",
                "weather": ["cloudy", "brightening"],
                "destination": "high_place",
                "landscape": "바다",
                "time": "해질녘",
                "speed": "circling",
                "release": "comparison",
                "carry": "curiosity",
                "companion": "guide",
                "glimpse": "arrival",
            },
            "context": {"location": "", "mood": "신비로운", "tone": "잔잔한", "ending": "열린 결말"},
        })
        personal = result["analysis"]["personal_context"]
        self.assertEqual(personal["method"], "guided narrative check-in")
        self.assertEqual(personal["setting"], "바다")
        self.assertEqual(personal["time"], "해질녘")
        self.assertIn("fear", personal["wounds"])
        self.assertIn("direction", personal["desires"])
        self.assertIn("NARRATIVE ASSESSMENT v1", result["analysis"]["personal_assessment"])
        self.assertIn("비임상적 서사 자기평가", result["analysis"]["personal_assessment"])
        self.assertIn("불안", result["analysis"]["personal_context"]["wounds_display"])
        self.assertIn("방향", result["analysis"]["personal_context"]["desires_display"])
        evidence = result["analysis"]["assessment_evidence"]
        self.assertEqual(evidence["input_mode"], "Narrative Check-in")
        self.assertIn("현재 장면", " ".join(evidence["checkin_signals"]))
        self.assertIn("심리적 부담", " ".join(evidence["derived_signals"]))

    def test_short_input_is_rejected(self):
        with self.assertRaises(ValueError):
            app.build_result({"story": "짧은 입력"})


if __name__ == "__main__":
    unittest.main()
