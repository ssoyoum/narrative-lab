"""Narrative AI MVP2.0.

The app keeps the MVP dependency-free, but now reads the team's existing
Chroma SQLite export. Chroma's vectors are not queried directly here: the
MVP uses the stored story/beat/module metadata with a transparent lexical
baseline so it can run on a fresh Python installation.

Run with: python app.py
Then open: http://127.0.0.1:8000
"""

from __future__ import annotations

import json
import math
import os
import re
import sqlite3
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).parent
TEAM_DB = ROOT / "team-data" / "jeju-stories" / "chroma_db" / "chroma.sqlite3"
FALLBACK_MODULE_FILE = ROOT / "data" / "story_modules.json"
OLLAMA_URL = os.environ.get("NARRATIVE_OLLAMA_URL", "http://127.0.0.1:11434/api/chat")
OLLAMA_MODEL = os.environ.get("NARRATIVE_OLLAMA_MODEL", "qwen2.5:3b")
USE_OLLAMA = os.environ.get("NARRATIVE_USE_OLLAMA", "0").lower() in {"1", "true", "yes"}

TOKEN_RE = re.compile(r"[A-Za-z0-9가-힣]{1,}")
SENTENCE_RE = re.compile(r"(?<=[.!?。！？])\s+|\n+")
STOPWORDS = {
    "그리고", "하지만", "그러나", "있는", "있었다", "그녀는", "그는", "이야기", "것을", "위해",
    "하며", "했다", "에서", "으로", "에게", "그날", "누군가", "모든", "이후", "때문에", "the", "and",
}
TARGET_BEATS = ("setup", "transition", "conflict", "climax", "resolution")


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
    return "transition", "사건이 이동하고 다음 변화의 단서가 놓입니다."


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
        "keywords": list(dict.fromkeys(tokens(text)))[:16],
    }
    return {"beats": beats, "dna": dna, "sentence_count": len(parts)}


WOUND_RULES = {
    "loss": ("잃", "손실", "하락", "무너", "끝났", "상실"),
    "fear": ("불안", "두렵", "걱정", "무섭", "공포", "실패", "하락장"),
    "exhaustion": ("지쳤", "피곤", "번아웃", "소진", "쉬고", "도피"),
    "disconnection": ("혼자", "외롭", "단절", "아무도", "멀어", "떠났"),
    "stagnation": ("막혔", "멈춰", "답답", "정체", "방향을 잃"),
    "grief": ("슬프", "그립", "상실", "장례", "떠나보"),
    "insignificance": ("무시", "쓸모없", "작아", "무력", "인정받지"),
}
DESIRE_RULES = {
    "rest": ("쉬고", "휴식", "도피", "벗어나", "멈추"),
    "healing": ("회복", "낫", "치유", "괜찮아"),
    "transformation": ("바꾸", "새로", "변화", "전환", "다시 시작"),
    "reconnection": ("돌아", "연결", "만나", "관계", "가족", "친구"),
    "meaning": ("의미", "왜", "이유", "방향", "무엇을"),
    "courage": ("용기", "맞서", "극복", "시작"),
    "peace": ("평온", "안정", "조용", "안식"),
    "discovery": ("찾", "알고 싶", "탐험", "발견"),
}
EMOTION_RULES = {
    "불안": ("불안", "걱정", "하락", "두렵", "무섭", "초조"),
    "피로": ("지쳤", "피곤", "번아웃", "소진"),
    "고립": ("혼자", "외롭", "아무도", "단절"),
    "상실감": ("잃", "손실", "상실", "무너"),
    "희망": ("희망", "기대", "다시", "시작"),
    "그리움": ("그립", "보고 싶", "떠나보"),
    "분노": ("화가", "분노", "억울", "복수"),
}
LOCATION_TERMS = [
    "제주", "포항", "부산", "서울", "대구", "강릉", "바다", "해안", "마을", "산", "숲", "동굴",
    "섬", "오름", "성산", "한라산", "집", "도시", "시골",
]


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _rule_matches(text: str, rules: dict[str, tuple[str, ...]]) -> list[str]:
    return [label for label, phrases in rules.items() if any(phrase in text for phrase in phrases)]


def _extract_location(text: str) -> str:
    matches = find_terms(text, LOCATION_TERMS)
    if matches:
        return matches[0]
    generic = re.findall(r"([가-힣A-Za-z]{2,12})(?:에|에서|으로|로)", text)
    excluded = {"하락장", "이유로", "때문에", "위해서", "곳으로", "앞으로"}
    return next((candidate for candidate in generic if candidate not in excluded), "장소 미확인")


def _fallback_personal_context(text: str) -> dict[str, Any]:
    wounds = _rule_matches(text, WOUND_RULES)
    desires = _rule_matches(text, DESIRE_RULES)
    emotions = _rule_matches(text, EMOTION_RULES)
    setting = _extract_location(text)
    keywords = _unique(tokens(text))[:18]
    if not wounds:
        wounds = ["stagnation"]
    if not desires:
        desires = ["meaning"]
    if not emotions:
        emotions = ["호기심"]
    if "도피" in text or "떠났" in text or "떠나" in text:
        conflict = "현재의 압박에서 벗어나고 싶지만, 떠난 뒤의 방향도 찾아야 하는 상태"
    elif "하락" in text or "손실" in text or "잃" in text:
        conflict = "상실의 충격과 다시 시작하고 싶은 욕망 사이의 갈등"
    else:
        conflict = "현재의 상황과 원하는 변화 사이의 갈등"
    return {
        "summary": sentences(text)[0][:140],
        "setting": setting,
        "emotions": emotions,
        "wounds": wounds,
        "desires": desires,
        "conflict": conflict,
        "keywords": keywords,
        "method": "rule-based fallback",
    }


SURVEY_SITUATIONS = {
    "loss": ("무언가를 잃었거나 결과가 무너진 느낌", ["loss"], ["healing"], "상실의 충격과 회복하고 싶은 마음 사이의 갈등"),
    "pressure": ("압박에서 잠시 벗어나고 싶은 상태", ["fear", "exhaustion"], ["rest"], "계속 버텨야 한다는 압박과 멈추고 싶은 욕망 사이의 갈등"),
    "stagnation": ("어디로 가야 할지 막막하고 멈춰 있는 상태", ["stagnation"], ["direction", "meaning"], "현재에 머물러 있지만 새로운 방향을 찾고 싶은 갈등"),
    "departure": ("익숙한 곳을 떠나 낯선 곳으로 이동한 상태", ["disconnection"], ["discovery", "rest"], "떠남으로 벗어나려는 마음과 새로운 소속을 찾는 갈등"),
    "transition": ("이전의 나를 지나 새로운 단계로 넘어가는 상태", ["stagnation"], ["transformation", "courage"], "변화하고 싶지만 익숙한 것을 놓기 어려운 갈등"),
}
SURVEY_EMOTIONS = {
    "anxiety": ("불안함", ["불안"], ["fear"]),
    "fatigue": ("지침", ["피로"], ["exhaustion"]),
    "isolation": ("고립감", ["고립"], ["disconnection"]),
    "anger": ("분노 또는 억울함", ["분노"], ["insignificance"]),
    "curiosity": ("호기심", ["호기심"], ["discovery"]),
    "hope": ("희망", ["희망"], ["courage"]),
}
SURVEY_DESIRES = {
    "rest": ("쉬고 싶다", ["rest"]),
    "direction": ("다음 방향을 찾고 싶다", ["meaning", "transformation"]),
    "connection": ("누군가 또는 무언가와 다시 연결되고 싶다", ["reconnection"]),
    "courage": ("다시 시작할 용기가 필요하다", ["courage"]),
    "meaning": ("이 경험의 의미를 알고 싶다", ["meaning", "discovery"]),
}
SCENE_METAPHORS = {
    "looking_back": ("무언가를 두고 온 뒤, 아직 뒤를 돌아보는 중", ["loss"], ["healing"], "지나간 것을 놓고 앞으로 가려는 갈등"),
    "waves": ("해야 할 것들이 파도처럼 밀려오는 중", ["fear", "exhaustion"], ["rest"], "밀려오는 의무와 잠시 멈추고 싶은 마음 사이의 갈등"),
    "seasons": ("같은 자리에서 계절만 바뀌는 것 같은 중", ["stagnation"], ["direction"], "변화가 필요하지만 어디서 시작할지 모르는 갈등"),
    "pre_departure": ("오래 있던 곳을 떠날 준비를 하는 중", ["disconnection"], ["courage"], "익숙함을 놓고 새로운 장면으로 갈지 망설이는 갈등"),
    "unknown_destination": ("이미 떠났지만 아직 목적지는 모르는 중", ["disconnection"], ["discovery"], "떠난 뒤의 자유와 불확실성을 함께 견디는 갈등"),
    "turning_page": ("하나의 이야기가 끝나고 다음 장을 넘기기 직전", ["loss"], ["transformation"], "끝난 것을 받아들이고 다음 장을 열려는 갈등"),
    "crossroads": ("예상하지 못했던 갈림길 앞에 선 중", ["fear"], ["courage", "direction"], "여러 가능성 중 하나를 선택해야 하는 갈등"),
    "restart": ("무언가를 다시 시작해보고 싶은 중", ["stagnation"], ["courage", "transformation"], "실패의 기억과 다시 움직이고 싶은 마음 사이의 갈등"),
    "inner_change": ("겉으로는 평범하지만 안에서는 큰 변화가 일어나는 중", ["stagnation"], ["transformation", "meaning"], "아직 보이지 않는 변화를 믿어야 하는 갈등"),
    "misaligned": ("딱히 무슨 일은 없는데 어딘가 어긋난 느낌", ["stagnation", "disconnection"], ["meaning"], "이름 붙이기 어려운 어긋남 속에서 방향을 찾는 갈등"),
    "unnamed": ("지금은 이름 붙이기 어려운 시기", ["fear"], ["meaning"], "정답을 서둘러 정하지 않고 상태를 바라보는 갈등"),
    "okay_scene": ("의외로 꽤 괜찮은 장면을 지나가는 중", [], ["peace", "discovery"], "괜찮은 순간을 알아보고 오래 머무를지 선택하는 갈등"),
}
WEATHER_METAPHORS = {
    "cloudy": ("이유 없이 흐린 날", "막연한 불안", ["fear"], []),
    "rain": ("하루 종일 비가 내린 뒤", "지침", ["exhaustion"], []),
    "empty_street": ("사람이 없는 새벽 거리", "고립감", ["disconnection"], []),
    "thunder": ("천둥이 오기 직전의 공기", "분노와 긴장", ["fear", "insignificance"], []),
    "wind": ("창문으로 들어오는 낯선 바람", "호기심", [], ["discovery"]),
    "brightening": ("멀리서 밝아지는 하늘", "희망", [], ["courage"]),
    "changing": ("날씨가 계속 바뀌는 오후", "혼란", ["fear", "stagnation"], []),
    "clear_void": ("너무 맑아서 멍한 날", "공허함", ["stagnation"], []),
    "umbrella": ("비가 그쳤는데 우산을 접지 못한 상태", "경계심", ["fear"], []),
    "travel": ("여행 전날 밤", "설렘과 불안", ["fear"], ["discovery"]),
    "warm_room": ("따뜻한 방에 들어온 순간", "안도", [], ["rest", "peace"]),
    "no_weather": ("특별한 날씨가 떠오르지 않는 상태", "무감각", ["stagnation"], []),
}
DESTINATION_METAPHORS = {
    "unfound": ("아무도 나를 찾지 않는 곳", ["rest"]),
    "high_place": ("길이 잘 보이는 높은 곳", ["direction", "meaning"]),
    "waiting": ("누군가 기다리고 있는 곳", ["reconnection"]),
    "unknown": ("아직 가본 적 없는 곳", ["courage", "discovery"]),
    "meaning": ("내가 왜 여기 있는지 알 수 있는 곳", ["meaning"]),
    "favorite": ("예전에 좋아했던 곳", ["healing", "reconnection"]),
    "start": ("무언가를 제대로 시작할 수 있는 곳", ["courage", "transformation"]),
    "distance": ("지금 있는 곳에서 조금만 멀어진 곳", ["rest", "peace"]),
    "freedom": ("특별한 목적 없이 흘러가는 곳", ["peace", "discovery"]),
    "stay": ("떠나지 않고 숨을 고를 수 있는 곳", ["rest", "peace"]),
    "explore": ("아직 어디로 가고 싶은지 모르는 상태", ["discovery", "meaning"]),
}
SPEED_METAPHORS = {
    "too_fast": ("너무 빨라 주변을 볼 틈이 없는 속도", ["exhaustion"], ["rest"]),
    "cannot_stop": ("멈추고 싶은데 계속 움직이는 속도", ["exhaustion", "fear"], ["rest"]),
    "walking": ("천천히 걷는 속도", ["peace"], ["meaning"]),
    "circling": ("어디로 갈지 몰라 같은 곳을 맴도는 속도", ["stagnation"], ["direction"]),
    "paused": ("잠시 멈춰 있는 속도", ["stagnation"], ["rest"]),
    "starting": ("이제 막 다시 걷기 시작한 속도", ["courage"], ["transformation"]),
    "running": ("뛰어보고 싶은 마음의 속도", ["hope"], ["courage"]),
    "drifting": ("흘러가는 대로 가는 속도", ["disconnection"], ["peace"]),
}
RELEASE_METAPHORS = {
    "expectations": ("다른 사람의 기대", "insignificance"),
    "must_do_well": ("잘해야 한다는 마음", "fear"),
    "regret": ("지나간 선택에 대한 후회", "grief"),
    "failure_fear": ("실패하면 안 된다는 두려움", "fear"),
    "alone": ("혼자 해결해야 한다는 생각", "exhaustion"),
    "comparison": ("끝없이 비교하는 습관", "insignificance"),
    "old_relation": ("너무 오래 붙잡고 있던 관계", "disconnection"),
    "finished": ("이미 끝난 일", "loss"),
    "right_answer": ("정답을 반드시 찾아야 한다는 마음", "stagnation"),
    "nothing": ("아직은 아무것도 내려놓고 싶지 않은 마음", ""),
}


def _coerce_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def _ollama_personal_context(text: str) -> dict[str, Any] | None:
    prompt = """사용자의 현재 상황을 Narrative Context로 분석하세요. 반드시 JSON 객체만 반환하세요.
필드: summary(문자열), setting(문자열), emotions(문자열 배열), wounds(영문 코드 배열), desires(영문 코드 배열), conflict(문자열), keywords(문자열 배열).
wounds 허용 코드: loss, fear, exhaustion, disconnection, stagnation, grief, insignificance.
desires 허용 코드: rest, healing, transformation, reconnection, meaning, courage, peace, discovery.
사용자의 금융·의료·법률 판단을 하지 말고, 입력된 상황을 서사적 맥락으로만 요약하세요.

입력:
""" + text
    body = json.dumps({
        "model": OLLAMA_MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {"role": "system", "content": "You extract structured narrative context. Return JSON only."},
            {"role": "user", "content": prompt},
        ],
    }).encode("utf-8")
    request = urllib.request.Request(OLLAMA_URL, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            payload = json.loads(response.read().decode("utf-8"))
        content = payload.get("message", {}).get("content", "")
        parsed = json.loads(content) if isinstance(content, str) else content
        if not isinstance(parsed, dict):
            return None
        result = {
            "summary": str(parsed.get("summary") or text[:140]),
            "setting": str(parsed.get("setting") or "장소 미확인"),
            "emotions": _coerce_list(parsed.get("emotions")),
            "wounds": _coerce_list(parsed.get("wounds")),
            "desires": _coerce_list(parsed.get("desires")),
            "conflict": str(parsed.get("conflict") or "현재의 상황과 원하는 변화 사이의 갈등"),
            "keywords": _coerce_list(parsed.get("keywords")),
            "method": f"local Ollama / {OLLAMA_MODEL}",
        }
        return result if result["emotions"] or result["wounds"] or result["desires"] else None
    except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def analyze_personal_context(text: str, survey: dict[str, Any] | None = None) -> dict[str, Any]:
    context = _fallback_personal_context(text)
    survey = survey or {}
    situation = str(survey.get("situation") or survey.get("scene") or "")
    emotion = str(survey.get("emotion") or "")
    desire = str(survey.get("desire") or survey.get("destination") or "")
    scene_summary = ""
    survey_keywords: list[str] = []
    if situation in SCENE_METAPHORS:
        scene_summary, wounds, desires, conflict = SCENE_METAPHORS[situation]
        context.update({"summary": scene_summary, "wounds": wounds, "desires": desires, "conflict": conflict})
        survey_keywords.append(scene_summary)
    if situation in SURVEY_SITUATIONS:
        label, wounds, desires, conflict = SURVEY_SITUATIONS[situation]
        context.update({"summary": label, "wounds": wounds, "desires": desires, "conflict": conflict})
    if emotion in SURVEY_EMOTIONS:
        label, emotions, wounds = SURVEY_EMOTIONS[emotion]
        context["emotions"] = emotions
        context["wounds"] = _unique(context["wounds"] + wounds)
        survey_keywords.extend([label, emotion])
    for weather in _coerce_list(survey.get("weather")):
        if weather in WEATHER_METAPHORS:
            label, weather_emotion, wounds, desires = WEATHER_METAPHORS[weather]
            context["emotions"] = _unique(context["emotions"] + [weather_emotion])
            context["wounds"] = _unique(context["wounds"] + wounds)
            context["desires"] = _unique(context["desires"] + desires)
            survey_keywords.extend([label, weather_emotion, weather])
    if desire in SURVEY_DESIRES:
        label, desires = SURVEY_DESIRES[desire]
        context["desires"] = _unique(context["desires"] + desires)
        survey_keywords.extend([label, desire])
    if desire in DESTINATION_METAPHORS:
        label, desires = DESTINATION_METAPHORS[desire]
        context["desires"] = _unique(context["desires"] + desires)
        survey_keywords.extend([label, desire])
    if survey.get("landscape"):
        context["landscape"] = str(survey["landscape"])
        survey_keywords.append(str(survey["landscape"]))
    for field, mapping in (("speed", SPEED_METAPHORS),):
        value = str(survey.get(field) or "")
        if value in mapping:
            label, wounds, desires = mapping[value]
            context[field] = label
            context["wounds"] = _unique(context["wounds"] + wounds)
            context["desires"] = _unique(context["desires"] + desires)
            survey_keywords.extend([label, value])
    for field in ("time", "release", "carry", "companion", "glimpse"):
        value = str(survey.get(field) or "")
        if value:
            context[field] = value
            survey_keywords.append(value)
    if situation or emotion or desire or survey.get("weather") or survey.get("speed"):
        context["method"] = "guided narrative check-in"
        context["keywords"] = _unique(context["keywords"] + survey_keywords)
        return context
    if USE_OLLAMA:
        refined = _ollama_personal_context(text)
        if refined:
            context = refined
    return context


WOUND_DISPLAY_LABELS = {
    "loss": "상실감", "fear": "불안", "exhaustion": "피로·소진",
    "disconnection": "단절감", "stagnation": "정체감", "grief": "애도",
    "insignificance": "무력감",
}
DESIRE_DISPLAY_LABELS = {
    "rest": "휴식", "healing": "회복", "transformation": "변화",
    "reconnection": "재연결", "meaning": "의미 찾기", "direction": "방향",
    "courage": "용기",
    "peace": "평온", "discovery": "탐색",
}


def _display_context_terms(values: Any, category: str) -> list[str]:
    labels = WOUND_DISPLAY_LABELS if category == "wound" else DESIRE_DISPLAY_LABELS
    return [labels.get(value, value) for value in _coerce_list(values)]


def build_narrative_assessment(personal_context: dict[str, Any]) -> str:
    """Create a non-clinical, psychological-assessment-style narrative report."""
    setting = str(personal_context.get("setting") or "장소 미확인")
    summary = str(personal_context.get("summary") or "아직 이름 붙지 않은 장면")
    emotions = " · ".join(_coerce_list(personal_context.get("emotions"))) or "아직 확인되지 않음"
    burdens = " · ".join(_display_context_terms(personal_context.get("wounds"), "wound")) or "아직 확인되지 않음"
    desires = " · ".join(_display_context_terms(personal_context.get("desires"), "desire")) or "아직 확인되지 않음"
    conflict = str(personal_context.get("conflict") or "현재의 장면과 원하는 변화 사이의 간극")
    carry = str(personal_context.get("carry") or "아직 확인되지 않음")
    companion = str(personal_context.get("companion") or "아직 확인되지 않음")
    glimpse = str(personal_context.get("glimpse") or "아직 정해지지 않은 다음 장면")
    time = str(personal_context.get("time") or "시간 미확인")
    speed = str(personal_context.get("speed") or "속도 미확인")
    return "\n".join([
        "[NARRATIVE ASSESSMENT v1]",
        "비임상적 서사 자기평가 · 답변에 따라 달라질 수 있음",
        "",
        f"1. 현재 장면\n   {summary}",
        f"   배경: {setting} · 시간: {time} · 움직임: {speed}",
        f"2. 정서적 기후\n   {emotions}",
        f"3. 심리적 부담\n   {burdens}",
        f"4. 현재의 욕구\n   {desires}",
        f"5. 내적 긴장\n   {conflict}",
        f"6. 회복 자원\n   가지고 가고 싶은 것: {carry}\n   함께하고 싶은 존재: {companion}",
        f"7. 다음 장면\n   {glimpse}",
        "",
        "이 결과는 진단이나 치료 권고가 아니라, 입력한 이야기를 다시 바라보기 위한 서사적 정리입니다.",
    ])


def build_assessment_evidence(
    free_text: str,
    survey: dict[str, Any],
    personal_context: dict[str, Any],
) -> dict[str, Any]:
    """Expose the input signals behind the non-clinical narrative assessment."""
    text_signals = _unique(tokens(free_text))[:8]
    checkin_signals = []
    if personal_context.get("summary"):
        checkin_signals.append(f"현재 장면: {personal_context['summary']}")
    if personal_context.get("emotions"):
        checkin_signals.append(f"정서적 기후: {' · '.join(_coerce_list(personal_context['emotions']))}")
    if personal_context.get("setting"):
        checkin_signals.append(f"배경: {personal_context['setting']}")
    if personal_context.get("time"):
        checkin_signals.append(f"시간: {personal_context['time']}")
    if personal_context.get("speed"):
        checkin_signals.append(f"움직임: {personal_context['speed']}")
    if personal_context.get("carry"):
        checkin_signals.append(f"회복 자원: {personal_context['carry']}")
    if personal_context.get("companion"):
        checkin_signals.append(f"동행자: {personal_context['companion']}")
    if personal_context.get("glimpse"):
        checkin_signals.append(f"다음 장면: {personal_context['glimpse']}")
    if not free_text:
        text_signals = ["자유 TXT 미입력 · Check-in 선택값 기반"]
    return {
        "method": "규칙 기반 키워드·선택값 매핑",
        "input_mode": "자유 TXT + Narrative Check-in" if free_text else "Narrative Check-in",
        "text_signals": text_signals,
        "checkin_signals": checkin_signals,
        "derived_signals": [
            f"심리적 부담 ← {' · '.join(personal_context.get('wounds_display', [])) or '아직 확인되지 않음'}",
            f"현재의 욕구 ← {' · '.join(personal_context.get('desires_display', [])) or '아직 확인되지 않음'}",
            f"내적 긴장 ← {personal_context.get('conflict') or '현재의 장면과 원하는 변화 사이의 간극'}",
        ],
        "survey_fields_used": [key for key, value in survey.items() if value],
    }


def _metadata_value(row: sqlite3.Row) -> Any:
    if row[2] is not None:
        return row[2]
    if row[3] is not None:
        return row[3]
    if row[4] is not None:
        return row[4]
    return row[5]


def _read_collection(connection: sqlite3.Connection, name: str) -> list[dict[str, Any]]:
    query = """
        SELECT e.embedding_id, em.key, em.string_value, em.int_value,
               em.float_value, em.bool_value
        FROM embeddings AS e
        JOIN segments AS s ON s.id = e.segment_id
        JOIN collections AS c ON c.id = s.collection
        JOIN embedding_metadata AS em ON em.id = e.id
        WHERE c.name = ?
        ORDER BY e.id
    """
    records: dict[str, dict[str, Any]] = {}
    connection.row_factory = sqlite3.Row
    for row in connection.execute(query, (name,)):
        record = records.setdefault(str(row[0]), {"id": str(row[0])})
        record[str(row[1])] = _metadata_value(row)
    return list(records.values())


def _document(record: dict[str, Any]) -> str:
    return str(record.get("chroma:document") or record.get("#document") or "")


def _metadata_text(record: dict[str, Any], keys: tuple[str, ...]) -> str:
    values: list[str] = []
    for key in keys:
        value = record.get(key)
        if value is None or value == "":
            continue
        if isinstance(value, str):
            try:
                decoded = json.loads(value)
                if isinstance(decoded, list):
                    values.extend(str(item) for item in decoded)
                else:
                    values.append(str(decoded))
            except json.JSONDecodeError:
                values.append(value)
        elif isinstance(value, list):
            values.extend(str(item) for item in value)
        else:
            values.append(str(value))
    return " ".join(values)


def canonical_beat(raw_beat: str, position: int | None = None) -> str:
    value = str(raw_beat or "").strip().lower()
    if value in {"ki", "setup", "introduction", "background"}:
        return "setup"
    if value in {"shō", "sho", "transition", "ten", "development"}:
        return "transition"
    if value in {"trial", "crisis", "conflict", "obstacle"}:
        return "conflict"
    if value in {"climax", "peak"}:
        return "climax"
    if value in {"ketsu", "resolution", "ending"}:
        return "resolution"
    if position == 1:
        return "setup"
    return "transition"


def _fallback_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    raw_modules = json.loads(FALLBACK_MODULE_FILE.read_text(encoding="utf-8"))
    beats = []
    for module in raw_modules:
        beats.append({
            "id": module.get("id", "fallback"),
            "story_id": module.get("source_story_id", "fallback"),
            "story_title": module.get("title", "기본 이야기"),
            "title": module.get("title", "기본 이야기"),
            "category": "fallback",
            "event_text": module.get("text", ""),
            "beat": module.get("beat", "transition"),
            "search_text": " ".join(str(value) for value in module.values()),
            "supporting_modules": [],
        })
    return beats, [], {"source": "local fallback modules", "stories": 0, "beats": len(beats), "modules": len(beats), "plot_patterns": 0}


def _collection_count(database: Path, name: str) -> int:
    try:
        with sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True) as connection:
            return int(connection.execute(
                """SELECT COUNT(*) FROM embeddings AS e
                   JOIN segments AS s ON s.id = e.segment_id
                   JOIN collections AS c ON c.id = s.collection
                   WHERE c.name = ?""",
                (name,),
            ).fetchone()[0])
    except sqlite3.Error:
        return 0


def load_team_data() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    if not TEAM_DB.exists():
        return _fallback_data()

    try:
        with sqlite3.connect(f"file:{TEAM_DB.as_posix()}?mode=ro", uri=True) as connection:
            catalog_rows = _read_collection(connection, "story_catalog")
            beat_rows = _read_collection(connection, "story_beats")
            module_rows = _read_collection(connection, "story_modules")
    except (sqlite3.Error, OSError):
        return _fallback_data()

    catalog = {}
    for record in catalog_rows:
        story_id = str(record.get("story_id") or record["id"])
        catalog[story_id] = record

    module_names: dict[str, list[str]] = {}
    for record in module_rows:
        story_id = str(record.get("source_story_id") or "")
        if not story_id:
            continue
        names = []
        for key in ("character_name", "place_name", "wisdom_summary", "mood_emotion"):
            value = record.get(key)
            if value:
                names.append(str(value))
        if names:
            module_names.setdefault(story_id, []).extend(names)

    beats = []
    for record in beat_rows:
        story_id = str(record.get("source_story_id") or "")
        story = catalog.get(story_id, {})
        position = int(record.get("beat_position") or 0)
        beat = canonical_beat(str(record.get("beat") or ""), position)
        title = str(record.get("story_title") or story.get("title") or story_id)
        event_text = str(record.get("event_text") or _document(record))
        signal_text = " ".join(module_names.get(story_id, []))
        story_dna_text = _metadata_text(story, (
            "wounds_addressed", "desires_fulfilled", "primary_wound", "primary_desire",
            "resonance_triggers", "narrative_themes", "emotional_arc",
        ))
        search_text = " ".join([
            title,
            str(story.get("category") or record.get("category") or ""),
            str(story.get("emotion") or record.get("emotion") or ""),
            str(story.get("conflict") or record.get("conflict") or ""),
            event_text,
            signal_text,
            story_dna_text,
        ])
        beats.append({
            "id": str(record.get("beat_id") or record["id"]),
            "story_id": story_id,
            "story_title": title,
            "title": f"{title} · {beat}",
            "category": str(story.get("category") or record.get("category") or "설화"),
            "event_text": event_text,
            "beat": beat,
            "raw_beat": str(record.get("beat") or ""),
            "search_text": search_text,
            "story_dna": story_dna_text,
            "supporting_modules": module_names.get(story_id, [])[:8],
        })

    stats = {
        "source": "team-data/jeju-stories/chroma_db/chroma.sqlite3",
        "stories": len(catalog_rows),
        "beats": len(beats),
        "modules": len(module_rows),
        "plot_patterns": _collection_count(TEAM_DB, "plot_patterns"),
    }
    return beats, module_rows, stats


BEATS, TEAM_MODULES, DATA_STATS = load_team_data()


def idf_scores(records: list[dict[str, Any]]) -> dict[str, float]:
    document_count = max(len(records), 1)
    document_frequency: dict[str, int] = {}
    for record in records:
        words = set(tokens(record.get("search_text", "")))
        for word in words:
            document_frequency[word] = document_frequency.get(word, 0) + 1
    return {word: math.log((document_count + 1) / (frequency + 1)) + 1 for word, frequency in document_frequency.items()}


IDF = idf_scores(BEATS)


def compact_story_text(text: str, max_chars: int = 260) -> str:
    cleaned = re.sub(r"\s+", " ", str(text)).strip()
    chunks = sentences(cleaned)
    compact = " ".join(chunks[:2])
    if len(compact) > max_chars:
        compact = compact[:max_chars].rsplit(" ", 1)[0] + "…"
    return compact


def retrieve_modules(
    dna: dict[str, Any],
    context: dict[str, str],
    personal_context: dict[str, Any] | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    personal_context = personal_context or {}
    query_text = " ".join([
        " ".join(dna["setting"]),
        " ".join(dna["characters"]),
        " ".join(dna["emotion"]),
        " ".join(dna["conflict"]),
        " ".join(dna["beats"]),
        str(personal_context.get("summary", "")),
        str(personal_context.get("setting", "")),
        str(personal_context.get("landscape", "")),
        str(personal_context.get("time", "")),
        str(personal_context.get("speed", "")),
        str(personal_context.get("carry", "")),
        str(personal_context.get("companion", "")),
        str(personal_context.get("glimpse", "")),
        " ".join(_coerce_list(personal_context.get("emotions"))),
        " ".join(_coerce_list(personal_context.get("wounds"))),
        " ".join(_coerce_list(personal_context.get("desires"))),
        str(personal_context.get("conflict", "")),
        " ".join(_coerce_list(personal_context.get("keywords"))),
        context.get("location", ""), context.get("mood", ""),
        context.get("tone", ""), context.get("ending", ""),
    ])
    query_words = set(tokens(query_text))
    ranked = []
    for record in BEATS:
        record_words = set(tokens(record["search_text"]))
        overlap = query_words & record_words
        score = sum(IDF.get(word, 1) for word in overlap)
        if record["beat"] in dna["beats"]:
            score += 1.5
        if personal_context.get("setting") and personal_context["setting"] in record["search_text"]:
            score += 2
        if context.get("location") and context["location"] in record["search_text"]:
            score += 2
        if context.get("mood") and context["mood"] in record["search_text"]:
            score += 2
        for dimension in ("wounds", "desires"):
            for value in _coerce_list(personal_context.get(dimension)):
                if value.lower() in record.get("story_dna", "").lower():
                    score += 3
        ranked.append((score, record, sorted(overlap)))
    ranked.sort(key=lambda item: (-item[0], item[1]["id"]))

    selected: list[tuple[float, dict[str, Any], list[str]]] = []
    selected_ids: set[str] = set()
    for target_beat in TARGET_BEATS:
        candidate = next((item for item in ranked if item[1]["beat"] == target_beat and item[1]["id"] not in selected_ids), None)
        if candidate:
            selected.append(candidate)
            selected_ids.add(candidate[1]["id"])
    for item in ranked:
        if len(selected) >= limit:
            break
        if item[1]["id"] not in selected_ids:
            selected.append(item)
            selected_ids.add(item[1]["id"])
    return [{
        "id": record["id"],
        "title": record["title"],
        "text": compact_story_text(record["event_text"]),
        "beat": record["beat"],
        "source_story": record["story_title"],
        "category": record["category"],
        "score": round(score, 2),
        "matched_terms": matched,
        "match_reason": " · ".join(matched) if matched else "서사 구조와 Story DNA의 기본 공명",
        "supporting_modules": record.get("supporting_modules", []),
    } for score, record, matched in selected[:limit]]


def module_for(beat: str, retrieved: list[dict[str, Any]], fallback: dict[str, Any]) -> dict[str, Any]:
    return next((module for module in retrieved if module["beat"] == beat), fallback)


def generate_story(
    analysis: dict[str, Any],
    retrieved: list[dict[str, Any]],
    context: dict[str, str],
    personal_context: dict[str, Any] | None = None,
) -> dict[str, str]:
    personal_context = personal_context or {}
    location = context.get("location") or personal_context.get("setting") or (analysis["dna"]["setting"][0] if analysis["dna"]["setting"] else "제주")
    mood = context.get("mood") or "신비로운"
    tone = context.get("tone") or "잔잔한"
    ending = context.get("ending") or "여운이 남는 결말"
    fallback = retrieved[0] if retrieved else {"beat": "setup", "text": "아직 이름 붙지 않은 이야기가 시작되었다."}
    opening = module_for("setup", retrieved, fallback)["text"]
    transition = module_for("transition", retrieved, fallback)["text"]
    conflict = module_for("conflict", retrieved, fallback)["text"]
    climax = module_for("climax", retrieved, fallback)["text"]
    resolution = module_for("resolution", retrieved, fallback)["text"]
    title = f"{location}, {mood} 분위기의 서사 기록"
    paragraphs = [
        f"{location}에 {tone} 빛이 내려앉은 날, {opening}",
        f"그 풍경을 지나 이야기는 다음 문턱으로 이동했다. {transition}",
        f"그러나 익숙한 세계 안에서 작은 균열이 생겼다. {conflict}",
        f"선택을 미룰 수 없게 된 순간, {climax}",
        f"그 뒤의 {ending} 속에서 {resolution}",
    ]
    return {"title": title, "text": "\n\n".join(paragraphs), "controls": {"location": location, "mood": mood, "tone": tone, "ending": ending}}


ENGINE_ATMOSPHERES = {
    "mysterious": "신비로운",
    "tense": "긴장되는",
    "lyrical": "서정적인",
    "dark": "어두운",
    "warm": "따뜻한",
    "adventurous": "모험적인",
}
ENGINE_THEMES = {
    "loss_recovery": {
        "label": "상실과 회복",
        "question": "무언가를 잃은 뒤에도 다시 살아갈 수 있는가?",
        "lack": "주인공은 잃어버린 것을 놓아주지 못한다.",
        "cost": "되찾고 싶다면 자신이 붙잡고 있던 기억의 일부를 내려놓아야 한다.",
        "irony": "되찾은 것은 과거의 물건이 아니라, 그것 없이도 걸어갈 수 있다는 사실이다.",
        "goal": "잃어버린 것의 의미를 확인하고 다음 장면으로 나아간다.",
        "conflict": "과거를 되찾으려는 마음과 앞으로 나아가야 하는 현실이 충돌한다.",
    },
    "forbidden_promise": {
        "label": "금기와 약속",
        "question": "약속을 지키기 위해 어디까지 감수할 수 있는가?",
        "lack": "주인공은 자신이 한 약속의 의미를 끝까지 이해하지 못한다.",
        "cost": "약속을 지키려면 가장 안전한 길과 익숙한 관계를 포기해야 한다.",
        "irony": "금지된 문을 연 순간, 주인공은 약속이 자신을 묶은 것이 아니라 구했다는 것을 알게 된다.",
        "goal": "오래된 약속의 진실을 찾아 그것을 완성한다.",
        "conflict": "약속을 지키려는 의무와 현재의 안전을 지키려는 본능이 충돌한다.",
    },
    "departure_return": {
        "label": "떠남과 귀환",
        "question": "떠나야만 다시 돌아갈 수 있는가?",
        "lack": "주인공은 자신이 어디에 속하는지 알지 못한다.",
        "cost": "새로운 길을 택하려면 돌아갈 수 있다는 확신을 포기해야 한다.",
        "irony": "멀리 떠난 뒤에야 주인공은 자신이 찾던 집이 장소가 아니었음을 깨닫는다.",
        "goal": "낯선 곳을 지나 자신이 돌아갈 수 있는 의미를 찾는다.",
        "conflict": "떠나고 싶은 욕망과 소속되고 싶은 마음이 서로를 밀어낸다.",
    },
    "transformation": {
        "label": "변신과 통과의례",
        "question": "새로운 내가 되기 위해 무엇을 버려야 하는가?",
        "lack": "주인공은 자신의 가능성을 믿지 못한 채 오래된 모습에 머문다.",
        "cost": "변화를 얻으려면 익숙한 이름과 역할을 벗어야 한다.",
        "irony": "가장 두려워하던 변신이 사실은 잃어버린 본래의 모습을 되찾는 일이었다.",
        "goal": "통과의례를 지나 자신의 새로운 역할을 받아들인다.",
        "conflict": "변하고 싶은 마음과 지금의 모습으로 남고 싶은 마음이 충돌한다.",
    },
    "human_nature": {
        "label": "인간과 자연의 균형",
        "question": "자연을 이기지 않고도 원하는 것을 얻을 수 있는가?",
        "lack": "주인공은 세계를 자신의 뜻대로 움직일 수 있다고 믿는다.",
        "cost": "바라는 것을 얻으려면 소유하려는 태도와 힘을 내려놓아야 한다.",
        "irony": "자연을 정복하려던 주인공이 결국 자연의 일부가 될 때 길을 얻는다.",
        "goal": "자연의 경고를 이해하고 인간과 세계 사이의 균형을 회복한다.",
        "conflict": "인간의 욕망과 자연의 질서가 하나의 장소에서 맞부딪힌다.",
    },
    "family_connection": {
        "label": "가족과 연결",
        "question": "서로를 이해하지 못해도 함께 남을 수 있는가?",
        "lack": "주인공은 가장 가까운 사람에게 자신의 진심을 전하지 못한다.",
        "cost": "연결을 회복하려면 오래 지켜온 자존심을 먼저 내려놓아야 한다.",
        "irony": "상대가 떠난 줄 알았던 시간 동안, 두 사람은 같은 약속을 지키고 있었다.",
        "goal": "단절된 관계의 흔적을 따라가 다시 대화할 기회를 만든다.",
        "conflict": "말하지 못한 진심과 이미 벌어진 시간이 두 사람 사이를 가로막는다.",
    },
}
ENGINE_LOCATIONS = {
    "sea": "바다", "oreum": "오름", "cave": "동굴", "forest": "숲",
    "village": "마을", "coast": "해안",
}
ENGINE_CHARACTERS = {
    "traveler": "떠도는 여행자", "child": "마을의 아이", "haenyeo": "바다를 지키는 해녀",
    "elder": "오래된 이야기를 기억하는 노인", "spirit": "경계에 머무는 수호신", "outsider": "마을에 들어온 이방인",
}
ENGINE_ENDINGS = {
    "warm": "따뜻한 결말", "reversal": "반전의 결말", "open": "열린 결말", "echo": "여운이 남는 결말",
}


def build_generative_story_dna(engine: dict[str, Any]) -> dict[str, Any]:
    theme = ENGINE_THEMES.get(str(engine.get("theme") or "loss_recovery"), ENGINE_THEMES["loss_recovery"])
    atmosphere = ENGINE_ATMOSPHERES.get(str(engine.get("atmosphere") or "mysterious"), "신비로운")
    location = ENGINE_LOCATIONS.get(str(engine.get("location") or "sea"), "바다")
    character = ENGINE_CHARACTERS.get(str(engine.get("character") or "traveler"), "떠도는 여행자")
    ending = ENGINE_ENDINGS.get(str(engine.get("ending") or "echo"), "여운이 남는 결말")
    return {
        "the_question": theme["question"],
        "the_lack": theme["lack"],
        "the_cost": theme["cost"],
        "the_irony": theme["irony"],
        "theme": theme["label"],
        "atmosphere": atmosphere,
        "location": location,
        "character_type": character,
        "ending_style": ending,
    }


def build_narrative_blueprint(engine: dict[str, Any], dna: dict[str, Any]) -> dict[str, Any]:
    theme = ENGINE_THEMES.get(str(engine.get("theme") or "loss_recovery"), ENGINE_THEMES["loss_recovery"])
    return {
        "protagonist": dna["character_type"],
        "goal": theme["goal"],
        "conflict": theme["conflict"],
        "world": f"{dna['atmosphere']} 분위기의 제주 {dna['location']}",
        "question": dna["the_question"],
        "lack": dna["the_lack"],
        "cost": dna["the_cost"],
        "irony": dna["the_irony"],
        "beat_plan": {
            "Ki": "주인공의 결핍과 세계의 규칙을 보여준다.",
            "Shō": "핵심 질문을 발생시키는 징조와 사건을 만든다.",
            "Trial": "목표를 위해 치러야 할 대가를 구체화한다.",
            "Crisis": "주인공이 피하고 싶던 아이러니를 드러낸다.",
            "Climax": "주인공이 질문에 대해 행동으로 답한다.",
            "Ketsu": "선택의 결과와 새로운 질서를 남긴다.",
        },
    }


def generate_blueprint_story(dna: dict[str, Any], blueprint: dict[str, Any]) -> dict[str, Any]:
    location = dna["location"]
    character = dna["character_type"]
    atmosphere = dna["atmosphere"]
    paragraphs = [
        f"{atmosphere} 제주 {location}, {character}는 {dna['the_lack']}",
        f"그곳에서 오래된 징조가 나타났다. {dna['the_question']}",
        f"목표에 다가갈수록 대가는 분명해졌다. {dna['the_cost']}",
        f"가장 어두운 순간, 진실은 예상과 다른 얼굴을 보였다. {dna['the_irony']}",
        f"주인공은 그 질문에 행동으로 답했고, {dna['ending_style']} 속에 새로운 질서가 남았다.",
    ]
    return {
        "title": f"{location}의 {dna['theme']}",
        "text": "\n\n".join(paragraphs),
        "controls": {
            "location": location,
            "mood": atmosphere,
            "tone": "서사적인",
            "ending": dna["ending_style"],
        },
        "generation_mode": "generative story DNA blueprint",
    }


def build_engine_result(payload: dict[str, Any], engine: dict[str, Any]) -> dict[str, Any]:
    context = payload.get("context") or {}
    dna = build_generative_story_dna(engine)
    blueprint = build_narrative_blueprint(engine, dna)
    planning_text = " ".join([
        dna["theme"], dna["atmosphere"], dna["location"], dna["character_type"],
        dna["the_question"], dna["the_lack"], dna["the_cost"], dna["the_irony"],
    ])
    analysis = analyze_story(planning_text)
    personal_context = {
        "summary": dna["theme"],
        "setting": dna["location"],
        "emotions": [dna["atmosphere"]],
        "wounds": [],
        "desires": [],
        "conflict": blueprint["conflict"],
        "keywords": [dna["theme"], dna["location"], dna["character_type"]],
        "method": "generative story DNA baseline",
    }
    analysis["personal_context"] = personal_context
    analysis["generative_story_dna"] = dna
    analysis["narrative_blueprint"] = blueprint
    analysis["dna"] = {
        "setting": [dna["location"]],
        "characters": [dna["character_type"]],
        "emotion": [dna["atmosphere"]],
        "conflict": [blueprint["conflict"]],
        "beats": list(blueprint["beat_plan"].keys()),
        "keywords": personal_context["keywords"],
    }
    retrieved = retrieve_modules(analysis["dna"], context, personal_context)
    generated = generate_blueprint_story(dna, blueprint)
    return {
        "analysis": analysis,
        "retrieved": retrieved,
        "generated": generated,
        "generative_story_dna": dna,
        "narrative_blueprint": blueprint,
        "retrieval_method": "User Intent → Stored Story DNA resonance / TF-IDF baseline",
        "analysis_method": "generative story DNA baseline",
        "data_source": DATA_STATS,
    }


def build_result(payload: dict[str, Any]) -> dict[str, Any]:
    engine = payload.get("engine") or {}
    if engine:
        return build_engine_result(payload, engine)
    story = str(payload.get("story", "")).strip()
    free_text = story
    context = payload.get("context") or {}
    survey = payload.get("survey") or {}
    survey_text = " ".join(str(value) for value in survey.values() if value)
    if len(story) < 20 and not survey_text:
        raise ValueError("자유 TXT를 입력하거나 Narrative Check-in 항목을 선택해주세요.")
    analysis_text = story if len(story) >= 20 else survey_text
    if len(story) < 20:
        story = survey_text
    analysis = analyze_story(analysis_text)
    personal_context = analyze_personal_context(analysis_text, survey)
    if context.get("location"):
        personal_context["setting"] = str(context["location"])
    elif personal_context.get("landscape"):
        personal_context["setting"] = str(personal_context["landscape"])
    personal_context["wounds_display"] = _display_context_terms(personal_context.get("wounds"), "wound")
    personal_context["desires_display"] = _display_context_terms(personal_context.get("desires"), "desire")
    analysis["personal_context"] = personal_context
    analysis["personal_assessment"] = build_narrative_assessment(personal_context)
    analysis["assessment_evidence"] = build_assessment_evidence(free_text, survey, personal_context)
    analysis["dna"] = {
        "setting": [personal_context.get("setting") or "장소 미확인"],
        "characters": analysis["dna"]["characters"],
        "emotion": _coerce_list(personal_context.get("emotions")) or ["호기심"],
        "conflict": [personal_context.get("conflict") or "현재의 상황과 원하는 변화 사이의 갈등"],
        "beats": analysis["dna"]["beats"],
        "keywords": _coerce_list(personal_context.get("keywords")) or analysis["dna"]["keywords"],
    }
    retrieved = retrieve_modules(analysis["dna"], context, personal_context)
    generated = generate_story(analysis, retrieved, context, personal_context)
    return {
        "analysis": analysis,
        "retrieved": retrieved,
        "generated": generated,
        "retrieval_method": "Personal Context → Story DNA resonance / team Chroma metadata + TF-IDF baseline",
        "analysis_method": personal_context.get("method", "rule-based fallback"),
        "data_source": DATA_STATS,
    }


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
            self.send_json(200, {
                "status": "ok",
                "version": "mvp2.0",
                "analysis_mode": "generative Story DNA baseline / local Ollama optional",
                "ollama_enabled": USE_OLLAMA,
                "ollama_model": OLLAMA_MODEL if USE_OLLAMA else None,
                "data_source": DATA_STATS,
            })
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
    port = int(os.environ.get("NARRATIVE_PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), NarrativeHandler)
    print(f"Narrative AI MVP2.0 running at http://127.0.0.1:{port}")
    print(f"Data source: {DATA_STATS}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
        server.server_close()
