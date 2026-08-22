# Narrative AI — MVP1

이 프로젝트는 이야기를 구조화하고, Story Module을 검색한 뒤, Context에 맞춰 새로운 서사로 재조합하는 로컬 MVP입니다.

현재 앱은 한국어 `흥부전 (경판 25장본, 1865)`에서 만든 4개 baseline Story Module을 사용합니다. 영어 Project Gutenberg corpus는 비교·확장용으로 `data/corpus/`에 보관하고, 출처와 처리 이력은 [`data/PROVENANCE.md`](data/PROVENANCE.md)에 기록했습니다.

## 현재 흐름

```text
Story Input
  → Narrative Beat Analysis
  → Story DNA Extraction
  → Story Module Retrieval
  → Context Recombination
  → Generated Narrative
```

## 실행

Python 3.10 이상에서 외부 패키지 없이 실행할 수 있습니다.

```bash
python app.py
```

브라우저에서 `http://127.0.0.1:8000`을 엽니다.

## MVP1 범위

- 문장 단위 Story Beat 분류
- Setting / Characters / Emotion / Conflict 기반 Story DNA 추출
- 샘플 Story Module 9개 검색
- TF-IDF lexical baseline 검색
- Location / Mood / Tone / Ending Context 반영
- 검색된 모듈의 setup·conflict·climax·resolution 재조합

현재 검색기는 외부 임베딩이나 LLM을 사용하지 않는 baseline입니다. 한국어 모듈은 원문을 그대로 노출하지 않고, 원문을 바탕으로 만든 현대 한국어 baseline annotation입니다. 다음 단계에서 여러 한국어 판본을 추가하고 사람이 Beat 라벨을 검수합니다.
