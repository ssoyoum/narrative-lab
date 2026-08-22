"""Narrative AI MVP1: story analysis, module retrieval, and recombination.

Run with: python app.py
Then open: http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import math
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
MODULES = json.loads((ROOT / "data" / "story_modules.json").read_text(encoding="utf-8"))
TOKEN_RE = re.compile(r"[A-Za-z0-9가-힣]{2,}")
SENTENCE_RE = re.compile(r"(?<=[.!?。！？])\s+|\n+")
STOPWORDS = {
    "그리고", "하지만", "그러나", "있는", "있었다", "그녀는", "그는", "이야기", "것을", "위해",
    "하며", "했다", "하며", "에서", "으로", "에게", "그날", "누군가", "모든", "the", "and",
}


def tokens(text: str) -> list[str]:
    return [word.lower() for word in TOKEN_RE.findall(text) if word.lower() not in STOPWORDS]


def sentences(text: str) -> list[str]:
    result = [part.strip() for part in SENTENCE_RE.split(text.strip()) if part.strip()]
    return result or [text.strip()]


def find_terms(text: str, terms: list[str]) -> list[str]:
    return [term for term in terms if term in text]


def classify_beat(sentence: str, index: int, total: int) -> tuple[str, str]:
    if index == 0:
        return "setup", "장소와 인물이 등장하고 이야기의 세계가 열립니다."
    if index == total - 1:
        return "resolution", "사건의 결과와 변화가 남습니다."
    if any(word in sentence for word in ("결국", "마침내", "절정", "맞섰", "깨달", "폭풍", "마지막")):
        return "climax", "갈등이 가장 높은 지점에 도달합니다."
    if any(word in sentence for word in ("하지만", "그러나", "위기", "두려", "잃", "사라", "금지", "갈등")):
        return "conflict", "인물의 목표를 막는 갈등과 위험이 나타납니다."
    return ("transition", "사건이 이동하고 다음 변화의 단서가 놓입니다.")


def analyze_story(text: str) -> dict[str, Any]:
    parts = sentences(text)
    beats = []
    for index, sentence in enumerate(parts):
        beat_type, role = classify_beat(sentence, index, len(parts))
        beats.append({"index": index + 1, "type": beat_type, "role": role, "text": sentence})

    settings = find_terms(text, ["제주", "바다", "오름", "숲", "동굴", "마을", "해안", "산", "바람", "성산", "한라"])
    characters = find_terms(text, ["해녀", "아이", "소녀", "소년", "노인", "할머니", "할아버지", "용", "신", "왕", "어부"])
    emotions = find_terms(text, ["두려", "슬픔", "기쁨", "외로", "분노", "그리움", "용기", "희망", "불안", "사랑"])
    conflicts = find_terms(text, ["저주", "약속", "금지", "사라", "잃", "막", "위기", "갈등", "폭풍", "비밀"])
    dna = {
        "setting": settings or ["제주", "바닷가"],
        "characters": characters or ["방문자", "알 수 없는 존재"],
        "emotion": emotions or ["호기심", "긴장"],
        "conflict": conflicts or ["낯선 장소에서 마주한 선택"],
        "beats": [beat["type"] for beat in beats],
        "keywords": list(dict.fromkeys(tokens(text)))[:12],
    }
    return {"beats": beats, "dna": dna, "sentence_count": len(parts)}


def idf_scores() -> dict[str, float]:
    document_count = len(MODULES)
    document_frequency: dict[str, int] = {}
    for module in MODULES:
        words = set(tokens(" ".join([module["title"], module["text"], *module["tags"]])))
        for word in words:
            document_frequency[word] = document_frequency.get(word, 0) + 1
    return {word: math.log((document_count + 1) / (frequency + 1)) + 1 for word, frequency in document_frequency.items()}


def retrieve_modules(dna: dict[str, Any], context: dict[str, str], limit: int = 4) -> list[dict[str, Any]]:
    idf = idf_scores()
    query_words = set(tokens(" ".join([
        " ".join(dna["setting"]), " ".join(dna["characters"]), " ".join(dna["emotion"]),
        " ".join(dna["conflict"]), " ".join(dna["beats"]), context.get("location", ""),
        context.get("mood", ""), context.get("tone", ""), context.get("ending", ""),
    ])))
    ranked = []
    for module in MODULES:
        module_words = set(tokens(" ".join([module["title"], module["text"], *module["tags"]])))
        overlap = query_words & module_words
        score = sum(idf.get(word, 1) for word in overlap)
        if module["beat"] in dna["beats"]:
            score += 1.5
        if context.get("mood") and context["mood"] in module["tags"]:
            score += 2
        ranked.append((score, module, sorted(overlap)))
    ranked.sort(key=lambda item: item[0], reverse=True)
    selected = []
    selected_ids = set()
    for beat in ("setup", "conflict", "climax", "resolution"):
        candidate = next((item for item in ranked if item[1]["beat"] == beat), None)
        if candidate and candidate[1]["id"] not in selected_ids:
            selected.append(candidate)
            selected_ids.add(candidate[1]["id"])
    for item in ranked:
        if len(selected) >= limit:
            break
        if item[1]["id"] not in selected_ids:
            selected.append(item)
            selected_ids.add(item[1]["id"])
    return [{**module, "score": round(score, 2), "matched_terms": matched} for score, module, matched in selected[:limit]]


def module_for(beat: str, retrieved: list[dict[str, Any]], fallback: dict[str, Any]) -> dict[str, Any]:
    for module in retrieved:
        if module["beat"] == beat:
            return module
    return next((module for module in retrieved if module["beat"] == fallback["beat"]), retrieved[0] if retrieved else fallback)


def generate_story(analysis: dict[str, Any], retrieved: list[dict[str, Any]], context: dict[str, str]) -> dict[str, str]:
    location = context.get("location") or (analysis["dna"]["setting"][0] if analysis["dna"]["setting"] else "제주")
    mood = context.get("mood") or "신비로운"
    tone = context.get("tone") or "잔잔한"
    ending = context.get("ending") or "여운이 남는 결말"
    by_beat = {module["beat"]: module for module in retrieved}
    fallback = retrieved[0] if retrieved else {"beat": "setup", "text": "아직 이름 붙지 않은 이야기가 시작되었다."}
    opening = module_for("setup", retrieved, fallback)["text"]
    conflict = module_for("conflict", retrieved, fallback)["text"]
    climax = module_for("climax", retrieved, fallback)["text"]
    resolution = module_for("resolution", retrieved, fallback)["text"]
    title = f"{location}, {mood} 분위기의 파도 기록"
    paragraphs = [
        f"{location}에 {tone}한 빛이 내려앉은 날, {opening}",
        f"그러나 익숙한 풍경 안에서 작은 균열이 생겼다. {conflict}",
        f"선택을 미룰 수 없게 된 순간, {climax}",
        f"그 뒤의 {ending} 속에서 {resolution}",
    ]
    return {"title": title, "text": "\n\n".join(paragraphs), "controls": {"location": location, "mood": mood, "tone": tone, "ending": ending}}


def build_result(payload: dict[str, Any]) -> dict[str, Any]:
    story = str(payload.get("story", "")).strip()
    if len(story) < 20:
        raise ValueError("20자 이상의 이야기를 입력해주세요.")
    context = payload.get("context") or {}
    analysis = analyze_story(story)
    retrieved = retrieve_modules(analysis["dna"], context)
    generated = generate_story(analysis, retrieved, context)
    return {"analysis": analysis, "retrieved": retrieved, "generated": generated, "retrieval_method": "TF-IDF lexical baseline / MVP1"}


class NarrativeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_json(self, status: int, body: dict[str, Any]) -> None:
        encoded = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            self.send_json(200, {"status": "ok", "version": "mvp1"})
            return
        super().do_GET()

    def do_POST(self) -> None:
        if self.path != "/api/generate":
            self.send_json(404, {"error": "Not found"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(size).decode("utf-8"))
            self.send_json(200, build_result(payload))
        except (ValueError, json.JSONDecodeError) as error:
            self.send_json(400, {"error": str(error)})
        except Exception as error:  # Keep the MVP API response readable during local development.
            self.send_json(500, {"error": f"처리 중 오류가 발생했습니다: {error}"})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), NarrativeHandler)
    print("Narrative AI MVP1 running at http://127.0.0.1:8000")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()
