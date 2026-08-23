import unittest

import app


FREE_TEXT_CASES = (
    {
        "name": "coin_trader_escape",
        "story": "나는 코인트레이더다. 하락장 이후 포항으로 떠나 잠시 숨을 고르고 다음 방향을 찾고 있다.",
        "setting": "포항",
        "wounds": {"loss", "fear", "exhaustion"},
        "desires": {"rest", "meaning"},
    },
    {
        "name": "resignation_search",
        "story": "퇴사 후 바다 마을에 혼자 머물며 내가 앞으로 무엇을 하고 싶은지 천천히 찾고 있다.",
        "setting": "바다",
        "wounds": {"disconnection"},
        "desires": {"meaning", "discovery"},
    },
    {
        "name": "new_beginning",
        "story": "새로운 일을 시작하고 싶지만 실패했던 기억이 남아 있어 조심스럽게 첫발을 준비하고 있다.",
        "setting": "장소 미확인",
        "wounds": {"fear"},
        "desires": {"courage", "transformation"},
    },
)


class NarrativeMvp13Tests(unittest.TestCase):
    def test_free_text_scenarios_keep_context_and_generate_story(self):
        for case in FREE_TEXT_CASES:
            with self.subTest(case=case["name"]):
                result = app.build_result({"story": case["story"], "context": {}})
                personal = result["analysis"]["personal_context"]
                self.assertEqual(personal["setting"], case["setting"])
                self.assertTrue(case["wounds"] & set(personal["wounds"]), personal)
                self.assertTrue(case["desires"] & set(personal["desires"]), personal)
                self.assertGreater(len(result["generated"]["text"]), 100)

    def test_empty_free_text_checkin_is_a_valid_input_mode(self):
        result = app.build_result({
            "story": "",
            "survey": {
                "scene": "restart",
                "weather": ["brightening"],
                "destination": "start",
                "landscape": "산",
                "time": "아침",
                "speed": "starting",
                "carry": "hope",
                "companion": "guide",
                "glimpse": "beginning",
            },
            "context": {},
        })
        self.assertEqual(result["analysis"]["assessment_evidence"]["input_mode"], "Narrative Check-in")
        self.assertEqual(result["analysis"]["personal_context"]["setting"], "산")
        self.assertTrue(result["generated"]["text"])

    def test_assessment_evidence_explains_free_text_mapping(self):
        result = app.build_result({
            "story": "하락장 뒤에 포항으로 떠났다. 피곤하지만 다시 방향을 찾고 싶다.",
            "context": {},
        })
        evidence = result["analysis"]["assessment_evidence"]
        self.assertEqual(evidence["input_mode"], "자유 TXT + Narrative Check-in")
        self.assertIn("하락장", evidence["text_signals"])
        self.assertTrue(any("심리적 부담" in item for item in evidence["derived_signals"]))
        self.assertTrue(any("현재의 욕구" in item for item in evidence["derived_signals"]))

    def test_result_contract_has_five_story_modules(self):
        result = app.build_result({
            "story": "낯선 도시에서 잠시 멈춰 지난 일을 돌아보고 다음 장면을 준비한다.",
            "context": {"location": "포항", "mood": "긴장되는", "tone": "서정적인", "ending": "열린 결말"},
        })
        self.assertEqual(len(result["retrieved"]), 5)
        self.assertTrue(all(module["beat"] for module in result["retrieved"]))
        self.assertTrue(all(module["source_story"] for module in result["retrieved"]))
        self.assertTrue(result["generated"]["title"].startswith("포항"))


if __name__ == "__main__":
    unittest.main()
