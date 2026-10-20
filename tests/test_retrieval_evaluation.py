import unittest
from evaluation.retrieval import corpus, metrics, validate_cases


class EvaluationTests(unittest.TestCase):
    def test_partial_recall_is_not_all_evidence(self):
        result = metrics(["a", "b"], [{"id": "c"}, {"id": "b"}])
        self.assertEqual(result["recall_at_3"], 0.5)
        self.assertEqual(result["mrr_at_3"], 0.5)
        self.assertEqual(result["all_evidence_at_3"], 0)

    def test_no_answer_has_no_recall_denominator(self):
        self.assertIsNone(metrics([], [{"id": "a"}])["recall_at_3"])

    def test_wrong_corpus_and_unsupported_gold_fail(self):
        case = dict(id="bad", gold=["unknown"], answerable=True, evidence=[])
        with corpus("fallback") as (beats, _, _):
            with self.assertRaises(ValueError):
                validate_cases([case], beats)
            case.update(gold=[beats[0]["id"]], evidence=["not in source"])
            with self.assertRaises(ValueError):
                validate_cases([case], beats)
