"""Run a fixed intent set and export structural evidence plus a human review sheet."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import app  # noqa: E402

BEATS = ("Ki", "Shō", "Trial", "Crisis", "Climax", "Ketsu")
RUBRIC = ("constraint_adherence", "source_consistency", "character_consistency", "place_consistency", "plot_coherence")


def evaluate_case(case: dict, mode: str) -> dict:
    if mode == "baseline":
        # Use the same retrieval/binding path and force the deterministic draft,
        # even if the developer machine has an API key configured.
        with patch.object(app, "generate_engine_folktale", side_effect=lambda dna, blueprint, beats, baseline: baseline):
            result = app.build_result({"engine": case["engine"]})
    else:
        result = app.build_result({"engine": case["engine"]})
    dna = result["generative_story_dna"]
    blueprint = result["narrative_blueprint"]
    bound = result["bound_beats"]
    generated = result["generated"]
    text = generated.get("text", "")
    source_id = blueprint["source_pack"]["source_story_id"]
    structural = {
        "six_beat_plan": all(beat in blueprint["beat_plan"] for beat in BEATS),
        "six_beat_bindings": all(beat in bound and bound[beat].get("module_id") for beat in BEATS),
        "single_source_binding": bool(source_id) and all(
            item.get("source_story_id") == source_id for item in bound.values() if item.get("module_id")
        ),
        "location_literal_present": dna["location"] in text,
        "character_literal_present": dna["character_type"] in text,
        "ending_literal_present": dna["ending_style"] in text,
    }
    return {
        "id": case["id"],
        "engine": case["engine"],
        "data_source": result["data_source"],
        "source_story_id": source_id,
        "bound_beats": {
            beat: {
                key: bound.get(beat, {}).get(key)
                for key in ("module_id", "source_story_id", "source_story", "event_text", "dna_focus", "reused")
            }
            for beat in BEATS
        },
        "missing_bound_beats": [beat for beat in BEATS if not bound.get(beat, {}).get("module_id")],
        "generative_story_dna": dna,
        "blueprint": {key: blueprint[key] for key in ("protagonist", "goal", "conflict", "world", "beat_plan")},
        "generation_provider": generated.get("generation_provider", "recombined baseline"),
        "generation_status": generated.get("generation_status", "baseline"),
        "generated_title": generated.get("title", ""),
        "generated_text": text,
        "structural": structural,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=ROOT / "evaluation/cases.jsonl")
    parser.add_argument("--output", type=Path, default=ROOT / "evaluation/results")
    parser.add_argument("--mode", choices=("baseline", "configured"), default="baseline")
    args = parser.parse_args()
    cases = [json.loads(line) for line in args.cases.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len({case["id"] for case in cases}) != len(cases):
        parser.error("Case IDs must be unique.")
    if args.mode == "configured" and not app.OPENAI_API_KEY:
        parser.error("Configured mode needs OPENAI_API_KEY; baseline mode runs offline.")

    args.output.mkdir(parents=True, exist_ok=True)
    rows = [evaluate_case(case, args.mode) for case in cases]
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    metadata = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "revision": revision,
        "mode": args.mode,
        "configured_model": app.OPENAI_MODEL if args.mode == "configured" else None,
        "case_count": len(rows),
        "data_source": app.DATA_STATS,
        "generation_status_counts": {
            status: sum(row["generation_status"] == status for row in rows)
            for status in sorted({row["generation_status"] for row in rows})
        },
        "structural_pass_counts": {key: sum(bool(row["structural"][key]) for row in rows) for key in rows[0]["structural"]},
    }
    (args.output / "run.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (args.output / "outputs.jsonl").open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    with (args.output / "review.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("id", "generation_provider", *RUBRIC, "reviewer", "notes"))
        writer.writeheader()
        for row in rows:
            writer.writerow({"id": row["id"], "generation_provider": row["generation_provider"]})
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
