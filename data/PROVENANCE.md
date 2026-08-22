# Corpus provenance

## Source 001 — Korean Tales (1889)

- **Author:** Horace Newton Allen (1858–1932)
- **Title:** *Korean Tales: Being a Collection of Stories Translated from the Korean Folk Lore*
- **Original publication:** 1889
- **Source:** [Project Gutenberg eBook 55539](https://www.gutenberg.org/ebooks/55539)
- **Raw text:** [55539-0.txt](https://www.gutenberg.org/files/55539/55539-0.txt)
- **License status recorded by source:** Project Gutenberg License; public domain in the USA
- **Downloaded:** 2026-08-23
- **Language:** English translation
- **Included story groups:** The Rabbit and Other Legends; The Enchanted Wine-Jug; Ching Yuh and Kyain Oo; Hyung Bo and Nahl Bo; Chun Yang; Sim Chung; Hong Kil Tong

## Processing record

`scripts/build_corpus.py` extracts seven story groups from the raw source and creates:

- `data/corpus/stories.jsonl`: story-level records with source metadata
- `data/corpus/story_modules.json`: four baseline modules per story (`setup`, `conflict`, `climax`, `resolution`)
- `data/story_modules.json`: the module file used by the MVP API

The first annotation is a **baseline paragraph sampling**, not a final human annotation. It must be reviewed before treating the beat labels as research ground truth.

## Source 002 — 흥부전 (경판 25장본, 1865)

- **Title:** 흥부전 (경판 25장본)
- **Edition:** 1865
- **Author:** 작자 미상
- **Source:** [위키문헌 판본](https://ko.wikisource.org/wiki/%ED%9D%A5%EB%B6%80%EC%A0%84_%28%EA%B2%BD%ED%8C%90_25%EC%9E%A5%EB%B3%B8%29)
- **Original source:** 장서각 소장본 기반 전사
- **License status recorded by source:** Public domain / PD-old
- **Language:** Korean, original orthography and spacing preserved in the source pages
- **Downloaded pages:** 25 OCR/text pages, pages 3–27

The app-facing modules are not a verbatim copy of the old orthography. They are four modern Korean baseline annotations written from the public-domain source: `setup`, `conflict`, `climax`, and `resolution`. The original page text remains under `data/sources/heungbu_pages/`.

## Scope note

This corpus is a structure/retrieval prototype source, not a claim that every modern Korean translation or edition is public domain. New Korean-language editions will be added only after their specific source and license are checked.
