"""Build a provenance-aware story corpus from the downloaded public-domain source."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
SOURCE = ROOT / "data" / "sources" / "korean_tales_allen_1889.txt"
CORPUS = ROOT / "data" / "corpus"
MODULES = ROOT / "data" / "story_modules.json"
SOURCE_URL = "https://www.gutenberg.org/files/55539/55539-0.txt"

STORIES = [
    ("allen-rabbit", "The Rabbit and Other Legends", "THE RABBIT, AND OTHER LEGENDS.", "THE ENCHANTED WINE-JUG;", ["animal", "cleverness", "survival"]),
    ("allen-wine-jug", "The Enchanted Wine-Jug", "THE ENCHANTED WINE-JUG;", "CHING YUH AND KYAIN OO.", ["magic", "origin", "family"]),
    ("allen-lovers", "Ching Yuh and Kyain Oo", "CHING YUH AND KYAIN OO.", "HYUNG BO AND NAHL BO;", ["love", "separation", "stars"]),
    ("allen-hyungbo", "Hyung Bo and Nahl Bo", "HYUNG BO AND NAHL BO;", "CHUN YANG,", ["siblings", "reward", "justice"]),
    ("allen-chunyang", "Chun Yang", "CHUN YANG,", "SIM CHUNG,", ["love", "promise", "loyalty"]),
    ("allen-simchung", "Sim Chung", "SIM CHUNG,", "HONG KIL TONG;", ["daughter", "sacrifice", "devotion"]),
    ("allen-honggiltong", "Hong Kil Tong", "HONG KIL TONG;", "THE END.", ["hero", "identity", "justice"]),
]


def normalize(text: str) -> str:
    text = text.replace("\ufeff", "").replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def paragraphs(text: str) -> list[str]:
    result = []
    for block in re.split(r"\n\s*\n", text):
        value = re.sub(r"\s+", " ", block).strip()
        if len(value) >= 90 and not value.startswith("[Illustration"):
            result.append(value)
    return result


def beat_paragraphs(items: list[str]) -> list[tuple[str, str]]:
    if len(items) < 4:
        return [(beat, items[min(index, len(items) - 1)]) for index, beat in enumerate(("setup", "conflict", "climax", "resolution"))]
    indexes = [0, len(items) // 3, (len(items) * 2) // 3, len(items) - 1]
    beats = ("setup", "conflict", "climax", "resolution")
    return [(beat, items[index]) for beat, index in zip(beats, indexes)]


def main() -> None:
    raw = normalize(SOURCE.read_text(encoding="utf-8"))
    stories = []
    modules = []
    for story_id, title, start_heading, end_heading, tags in STORIES:
        start = raw.index(start_heading) + len(start_heading)
        end = raw.index(end_heading, start)
        body = raw[start:end].strip()
        story_paragraphs = paragraphs(body)
        story = {
            "id": story_id,
            "title": title,
            "author": "Horace Newton Allen",
            "original_publication_year": 1889,
            "language": "en",
            "source": "Project Gutenberg eBook 55539",
            "source_url": SOURCE_URL,
            "license": "Project Gutenberg License; public domain in the USA",
            "annotation_status": "baseline paragraph sampling; human review pending",
            "text": "\n\n".join(story_paragraphs),
            "paragraph_count": len(story_paragraphs),
        }
        stories.append(story)
        for beat, paragraph in beat_paragraphs(story_paragraphs):
            modules.append({
                "id": f"{story_id}-{beat}",
                "source_story_id": story_id,
                "beat": beat,
                "title": f"{title} / {beat.title()}",
                "tags": tags + [beat],
                "text": paragraph,
                "source_url": SOURCE_URL,
                "license": "Project Gutenberg License; public domain in the USA",
                "annotation_status": "baseline paragraph sampling; human review pending",
            })

    CORPUS.mkdir(parents=True, exist_ok=True)
    with (CORPUS / "stories.jsonl").open("w", encoding="utf-8") as file:
        for story in stories:
            file.write(json.dumps(story, ensure_ascii=False) + "\n")
    (CORPUS / "story_modules.json").write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MODULES.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(stories)} stories and {len(modules)} story modules.")


if __name__ == "__main__":
    main()
