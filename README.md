# Narrative AI — MVP1.1

이 프로젝트는 사용자가 입력한 임의의 상황을 `Personal Narrative Context`로 구조화하고, 제주 설화 pack의 Story DNA·Beat·Module과 공명시키며, 새로운 서사로 재조합하는 로컬 MVP입니다.

현재 앱은 팀 프로젝트의 `team-data/jeju-stories/chroma_db/chroma.sqlite3`를 제주 설화 pack으로 읽습니다. 이 DB의 `story_catalog`, `story_full`, `story_beats`, `story_modules`, `plot_patterns` 중 MVP1.1에서는 설화 카탈로그·Story DNA·Beat·모듈 메타데이터를 사용합니다. Chroma 패키지나 외부 API 없이 SQLite의 저장 메타데이터를 읽고 TF-IDF lexical baseline으로 검색합니다.

## 현재 흐름

```text
Personal TXT Input
  → Personal Narrative Context Analysis
  → Story DNA Resonance Matching
  → Story Beat / Module Retrieval
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

- 장면·마음의 날씨·목적지·배경·시간·속도·내려놓을 것·가지고 갈 것·동행자·미래 장면을 사용하는 은유형 Narrative Check-in
- 선택적 자유 TXT 입력 지원
- 장소 / 감정 / 상처 / 욕망 / 갈등 / 키워드 추출
- Ollama 로컬 LLM 선택 연결 (`NARRATIVE_USE_OLLAMA=1`)
- Ollama가 없을 때 규칙 기반 fallback
- 심리 진단이 아닌 서사적 자기 점검 UX
- Narrative Assessment v1: 현재 장면·정서적 기후·심리적 부담·욕구·회복 자원을 정리하는 비임상적 TXT 리포트
- 팀 데이터의 Story DNA와 사용자 Context 공명 매칭
- 팀 데이터의 246개 설화, 1,264개 Beat, 1,431개 Story Module 검색
- TF-IDF lexical baseline 검색
- Location / Mood / Tone / Ending Context 반영
- 팀의 `Ki / Shō / Trial / Ten / Crisis / Climax / Ketsu` Beat를 MVP의 setup·transition·conflict·climax·resolution으로 매핑
- 검색된 Beat와 관련 인물·장소·감정 모듈을 재조합

현재 기본 실행은 외부 임베딩 질의나 원격 LLM을 사용하지 않는 baseline입니다. 이미 저장된 Chroma 벡터 자체를 질의하지 않고 메타데이터를 사용하므로 실행이 단순합니다. 더 유연한 자연어 분석이 필요하면 Ollama를 로컬에서 실행하고 환경 변수로 선택할 수 있습니다. 원문/출처의 저작권 검증과 Beat·모듈 라벨의 품질 검수는 별도 데이터 작업으로 남아 있습니다.

## 선택적 로컬 LLM

Ollama가 설치되어 있고 모델이 준비되어 있다면:

```powershell
$env:NARRATIVE_USE_OLLAMA = "1"
$env:NARRATIVE_OLLAMA_MODEL = "qwen2.5:3b"
python app.py
```

Ollama가 없거나 모델 호출에 실패하면 자동으로 규칙 기반 Personal Context 분석으로 처리합니다. 따라서 기본 MVP 실행에는 유료 API 키가 필요하지 않습니다.

## 데이터 연결 확인

앱을 실행한 뒤 `http://127.0.0.1:8000/api/health`에서 현재 연결된 데이터 규모를 확인할 수 있습니다.

```json
{
  "stories": 246,
  "beats": 1264,
  "modules": 1431,
  "plot_patterns": 246
}
```

`team-data`가 없거나 Chroma DB를 읽지 못하면 `data/story_modules.json`의 fallback 모듈로 실행됩니다.
