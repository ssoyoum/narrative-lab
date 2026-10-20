"""Offline retrieval diagnostic. Never calls generation, Ollama or OpenAI.

python evaluation/retrieval.py --output evaluation/results/baseline.json
python evaluation/retrieval.py --variant synonyms --baseline evaluation/results/baseline.json --output evaluation/results/synonyms.json
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import app

# Diagnostic query expansion only; app defaults and stored records stay unchanged.
# General lexical alternatives, not character names or gold module IDs.
SYNONYMS = {
    "유산": "재산을 독차지하고", "노동": "품을 팔고", "생계": "먹여 살리기",
    "상처": "다친", "새": "제비의", "빈곤": "가난에서", "축출": "내쫓았습니다",
    "배척": "내쫓았습니다", "쫓겨난": "내쫓았습니다",
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@contextmanager
def corpus(source):
    if source == "fallback":
        beats, modules, stats = app._fallback_data()
        path = app.FALLBACK_MODULE_FILE
    else:
        beats, modules, stats = app.load_team_data()
        path = app.TEAM_DB
        if not path.is_file() or stats["source"] == "local fallback modules":
            raise ValueError("Team database unavailable; cannot silently evaluate fallback")
    with patch.multiple(app, BEATS=beats, TEAM_MODULES=modules, DATA_STATS=stats, IDF=app.idf_scores(beats)):
        yield beats, stats, path


def validate_cases(cases, beats):
    records = {r["id"]: r for r in beats}
    ids = [c["id"] for c in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate case IDs")
    for case in cases:
        if bool(case["gold"]) != case["answerable"]:
            raise ValueError(f"{case['id']}: answerability/gold conflict")
        if any(i not in records for i in case["gold"]):
            raise ValueError(f"{case['id']}: gold ID not in selected corpus")
        evidence = " ".join(records[i]["event_text"] for i in case["gold"])
        if any(fragment not in evidence for fragment in case["evidence"]):
            raise ValueError(f"{case['id']}: evidence fragment not in gold text")


def metrics(gold, ranked, k=3):
    if not gold:
        return {"recall_at_1": None, "recall_at_3": None, "mrr_at_3": None, "all_evidence_at_3": None}
    found = [row["id"] for row in ranked[:k]]
    ranks = [i + 1 for i, module in enumerate(found) if module in gold]
    return {
        "recall_at_1": len(set(found[:1]) & set(gold)) / len(gold),
        "recall_at_3": len(set(found) & set(gold)) / len(gold),
        "mrr_at_3": 1 / min(ranks) if ranks else 0,
        "all_evidence_at_3": float(set(gold) <= set(found)),
    }


def run_case(case, variant):
    query = case["query"]
    if variant == "synonyms":
        query += " " + " ".join(value for key, value in SYNONYMS.items() if key in query)
    dna = {"setting": [query], "characters": [], "emotion": [], "conflict": [], "beats": []}
    start = perf_counter()
    ranked = [
        {"id": record["id"], "story_id": record["story_id"], "score": score, "matched_terms": terms}
        for score, record, terms in app._rank_retrieval_records(dna, {}, {})
    ]
    elapsed = (perf_counter() - start) * 1000
    pack = app.select_story_pack(dna, {}, {})
    selected = app.retrieve_modules(dna, {}, {}, source_story_id=pack["source_story_id"] or None)
    return {
        **case, "effective_query": query, "raw_top3": ranked[:3],
        "pack_id": pack["source_story_id"], "selected_ids": [r["id"] for r in selected],
        "metrics": metrics(case["gold"], ranked), "raw_retrieval_ms": round(elapsed, 3),
        # Returning candidates is not answering a fact question; this app has no QA abstention contract.
        "abstained": None, "answer_evaluation": "not_run", "consistency_evaluation": "not_run",
    }


def summarize(rows):
    answerable = [r for r in rows if r["answerable"]]
    return {
        "cases": len(rows), "answerable_cases": len(answerable), "no_answer_cases": len(rows) - len(answerable),
        **{name: sum(r["metrics"][name] for r in answerable) / len(answerable) if answerable else None
           for name in ("recall_at_1", "recall_at_3", "mrr_at_3", "all_evidence_at_3")},
        "abstention_rate": None, "model_requests": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=ROOT / "evaluation/retrieval_cases.json")
    parser.add_argument("--source", choices=["fallback", "team"], default="fallback")
    parser.add_argument("--variant", choices=["baseline", "synonyms"], default="baseline")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; choose a new path to preserve prior raw results")
    if args.variant != "baseline" and not args.baseline:
        parser.error("Save and supply --baseline before measuring a candidate")
    case_data = json.loads(args.cases.read_text(encoding="utf-8"))
    if case_data["source"] != args.source:
        parser.error("Gold corpus and --source differ")
    with corpus(args.source) as (beats, stats, data_path):
        validate_cases(case_data["cases"], beats)
        identity = {"source": args.source, "data_sha256": digest(data_path), "cases_sha256": digest(args.cases)}
        prior = json.loads(args.baseline.read_text()) if args.baseline else None
        if prior and (prior["identity"] != identity or prior["variant"] != "baseline"):
            parser.error("Baseline must use identical corpus and frozen questions")
        if prior and (prior["app_sha256"] != digest(ROOT / "app.py") or prior["harness_sha256"] != digest(__file__)):
            parser.error("Retrieval code changed; save a new baseline before comparing variants")
        rows = [run_case(c, args.variant) for c in case_data["cases"]]
        result = {"identity": identity, "variant": args.variant, "data_stats": stats,
                  "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  "harness_sha256": digest(__file__), "app_sha256": digest(ROOT / "app.py"),
                  "annotation_review": case_data["annotation_review"], "summary": summarize(rows), "rows": rows}
        if prior:
            before = {r["id"]: r for r in prior["rows"]}
            result["comparison"] = {
                "baseline_sha256": digest(args.baseline),
                "regressions": [r["id"] for r in rows if r["answerable"] and
                                r["metrics"]["recall_at_3"] < before[r["id"]]["metrics"]["recall_at_3"]],
                "improvements": [r["id"] for r in rows if r["answerable"] and
                                 r["metrics"]["recall_at_3"] > before[r["id"]]["metrics"]["recall_at_3"]],
                "adopted_in_app": False,
            }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive create protects saved results, including races with another run.
        with args.output.open("x", encoding="utf-8") as handle:
            json.dump(result, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        print(json.dumps({"summary": result["summary"], "comparison": result.get("comparison")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
