"""Smoke test for the local Narrative Engine API.

Run the server first, then:
    python scripts/smoke_test.py

Optional:
    $env:NARRATIVE_BASE_URL = "http://127.0.0.1:8134"
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


BASE_URL = os.environ.get("NARRATIVE_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
ENGINE = {
    "atmosphere": "mysterious",
    "theme": "forbidden_promise",
    "location": "cave",
    "character": "traveler",
    "ending": "echo",
}


def request(path: str, payload: dict | None = None) -> dict | str:
    url = f"{BASE_URL}{path}"
    if payload is None:
        request_obj = urllib.request.Request(url, method="GET")
    else:
        body = json.dumps(payload).encode("utf-8")
        request_obj = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
    with urllib.request.urlopen(request_obj, timeout=10) as response:
        content = response.read().decode("utf-8")
        if response.headers.get_content_type() == "application/json":
            return json.loads(content)
        return content


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    try:
        homepage = request("/")
        require(isinstance(homepage, str) and "NARRATIVE" in homepage, "homepage did not load")

        result = request("/api/generate", {"engine": ENGINE, "context": {}})
        require(isinstance(result, dict), "initial response was not JSON")
        require(result.get("generative_story_dna"), "Generative Story DNA is missing")
        require(result.get("narrative_blueprint"), "Narrative Blueprint is missing")
        require(result.get("match_report"), "Match Report is missing")
        require(result.get("beat_recommendations"), "Beat recommendations are missing")
        require(result.get("generated", {}).get("text"), "generated narrative is missing")

        beat = next(iter(result["beat_recommendations"]))
        candidates = result["beat_recommendations"][beat]["candidates"]
        require(candidates, f"no candidates returned for {beat}")
        override = {"beat_overrides": {beat: candidates[0]["module_id"]}}
        remix = request("/api/generate", {"engine": ENGINE, "context": {}, **override})
        require(remix.get("remix", {}).get("active"), "remix was not activated")
        require(remix.get("active_modules"), "active remix modules are missing")
        require("remix" in remix.get("generated", {}).get("generation_mode", ""), "remix mode is missing")

        print(f"SMOKE OK: {BASE_URL} | beat={beat} | module={candidates[0]['module_id']}")
        return 0
    except (AssertionError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
        print(f"SMOKE FAILED: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
