"""Build the Korean MVP corpus from the verified 1865 Heungbu edition."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
PAGES = ROOT / "data" / "sources" / "heungbu_pages"
CORPUS = ROOT / "data" / "corpus"
MODULES = ROOT / "data" / "story_modules.json"
SOURCE_URL = "https://ko.wikisource.org/wiki/흥부전_(경판_25장본)"

MODERN_MODULE_TEXT = {
    "setup": "경상도 어느 고을에 흥부와 놀부 형제가 살았습니다. 욕심 많은 놀부는 부모의 재산을 독차지하고, 착하지만 가난한 흥부 가족을 집에서 내쫓았습니다.",
    "conflict": "흥부는 가족을 먹여 살리기 위해 품을 팔고 형에게 도움을 청했지만 번번이 거절당했습니다. 가난은 계속되었고, 가족들은 하루하루를 버티며 살아갔습니다.",
    "climax": "어느 봄날 흥부는 다친 제비의 다리를 정성껏 치료해 날려 보냈습니다. 이듬해 제비가 박씨를 물어오자 흥부는 그 씨앗을 심고 기다렸습니다.",
    "resolution": "박을 타자 금은보화와 온갖 보물이 쏟아져 나와 흥부 가족은 가난에서 벗어났습니다. 이 소식을 들은 놀부도 욕심을 내어 제비를 괴롭혔지만, 그의 박에서는 재앙과 꾸지람만 나왔습니다.",
}


def clean_wikitext(value: str) -> str:
    value = re.sub(r"<noinclude>.*?</noinclude>", "", value, flags=re.S)
    value = re.sub(r"<references\s*/?>", "", value)
    value = re.sub(r"\{\{왼쪽 여백\|[^|]+\|([^{}]*)\}\}", r"\1", value)
    value = re.sub(r"\{\{[^{}]*\}\}", "", value)
    value = re.sub(r"\{\{[^{}]*\}\}", "", value)
    value = re.sub(r"\[\[[^|\]]+\|([^\]]+)\]\]", r"\1", value)
    value = re.sub(r"\[\[([^\]]+)\]\]", r"\1", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def main() -> None:
    page_files = sorted(PAGES.glob("page_*.wikitext"))
    page_texts = [clean_wikitext(page.read_text(encoding="utf-8")) for page in page_files]
    page_texts = [text for text in page_texts if text]
    full_text = "".join(page_texts)
    story_id = "heungbu-1865-gyeongpan-25"
    beats = ("setup", "conflict", "climax", "resolution")
    chunks = []
    for index, beat in enumerate(beats):
        start = round(len(full_text) * index / len(beats))
        end = round(len(full_text) * (index + 1) / len(beats))
        chunks.append((beat, full_text[start:end]))

    story = {
        "id": story_id,
        "title": "흥부전 (경판 25장본)",
        "author": "작자 미상",
        "edition_year": 1865,
        "language": "ko",
        "source": "위키문헌 / 장서각 소장본 기반 전사",
        "source_url": SOURCE_URL,
        "license": "Public domain / PD-old",
        "annotation_status": "baseline page segmentation; human review pending",
        "page_count": len(page_texts),
        "text": full_text,
    }
    modules = []
    for beat, text in chunks:
        modules.append({
            "id": f"{story_id}-{beat}",
            "source_story_id": story_id,
            "beat": beat,
            "title": f"흥부전 / {beat}",
            "tags": ["흥부전", "형제", "가난", "박", "권선징악", beat],
                "text": MODERN_MODULE_TEXT[beat],
                "source_excerpt": text[:600],
                "derived_from": "Personal modern Korean baseline annotation of the public-domain edition",
            "source_url": SOURCE_URL,
            "license": "Public domain / PD-old",
            "annotation_status": "baseline page segmentation; human review pending",
        })

    CORPUS.mkdir(parents=True, exist_ok=True)
    (CORPUS / "korean_stories.jsonl").write_text(json.dumps(story, ensure_ascii=False) + "\n", encoding="utf-8")
    (CORPUS / "korean_story_modules.json").write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MODULES.write_text(json.dumps(modules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(page_texts)} Korean source pages and {len(modules)} modules.")


if __name__ == "__main__":
    main()
