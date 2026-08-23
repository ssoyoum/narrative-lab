# Narrative AI — MVP1.3

사용자의 상황을 하나의 심리 진단 결과로 고정하지 않고, 현재 지나고 있는 **이야기의 장면**으로 구조화하는 Personal Narrative AI입니다.

사용자 입력을 `Personal Narrative Context`로 정리한 뒤, 제주 설화 pack의 Story DNA·Beat·Module과 공명시키고 새로운 이야기로 재조합합니다.

> 이 프로젝트는 임상 심리검사나 정신건강 진단 도구가 아닙니다. 입력한 이야기를 다시 바라보기 위한 비임상적 서사 자기점검 시스템입니다.

## 프로젝트 질문

```text
무작위로 입력된 개인의 상황을
어떻게 장면·정서·욕구·갈등의 구조로 바꾸고,
기존 설화의 서사 모듈과 연결할 수 있을까?
```

## 사용자 흐름

```text
소개 화면
  → Narrative Check-in 한 질문씩 진행
  → 선택적 자유 TXT 입력
  → Personal Narrative Context 분석
  → Narrative Assessment v1 생성
  → 평가 근거 표시
  → 제주 설화 Story Module 매칭
  → 새로운 서사 재조합
  → 평가 리포트 .txt 저장
```

선택이 번거로운 사용자를 위해 첫 화면에서 `랜덤 이야기 생성`도 제공합니다. 모든 선택값을 무작위로 채우고 결과까지 자동 생성합니다.

## 핵심 기능

- 장면·마음의 날씨·목적지·배경·시간·속도·내려놓을 것·가지고 갈 것·동행자·미래 장면을 사용하는 은유형 Check-in
- 자유 TXT 입력 또는 Check-in 단독 입력
- 장소·정서·심리적 부담·현재의 욕구·갈등·키워드 추출
- `Narrative Assessment v1` 비임상적 자기평가 리포트
- TXT 단서·Check-in 신호·도출된 해석을 분리한 평가 근거 표시
- 평가 리포트 `.txt` 다운로드
- 제주 설화 Story DNA와 사용자 Context 공명 매칭
- 검색된 Beat와 Module을 새로운 이야기로 재조합
- Ollama 로컬 LLM 선택 연결
- 외부 API 없이 동작하는 규칙 기반 fallback

## 시스템 구조

```text
Personal TXT / Narrative Check-in
            ↓
Personal Narrative Context
  ├─ 현재 장면
  ├─ 정서적 기후
  ├─ 심리적 부담
  ├─ 현재의 욕구
  └─ 내적 긴장
            ↓
Narrative Assessment v1 + Evidence
            ↓
Story DNA Resonance Matching
            ↓
Beat / Module Retrieval
            ↓
Context Recombination
            ↓
Generated Narrative
```

## 데이터

현재 MVP는 팀 프로젝트의 제주 설화 pack을 개인 프로젝트의 분석 데이터로 연결합니다.

```text
source: team-data/jeju-stories/chroma_db/chroma.sqlite3
stories: 246
beats: 1,264
modules: 1,431
plot_patterns: 246
```

MVP에서는 Chroma 패키지나 원격 임베딩 API를 호출하지 않습니다. SQLite에 저장된 설화 메타데이터를 읽고 TF-IDF lexical baseline으로 모듈을 검색합니다.

## 실행

Python 3.10 이상에서 외부 패키지 없이 실행할 수 있습니다.

```bash
python app.py
```

브라우저에서 [http://127.0.0.1:8000](http://127.0.0.1:8000)을 엽니다.

서버 코드를 수정한 뒤에는 기존 서버를 `Ctrl + C`로 종료하고 다시 실행합니다. 브라우저는 `Ctrl + F5`로 새로고침합니다.

## 테스트

```bash
python -m unittest discover -s tests -v
```

현재 자동 테스트는 다음을 검증합니다.

- 코인 하락 후 도피한 사용자 시나리오
- 퇴사 후 방향을 찾는 사용자 시나리오
- 새로운 시작을 앞둔 사용자 시나리오
- 자유 TXT 없이 Check-in만 입력하는 흐름
- 평가 근거가 입력 단서를 포함하는지 여부
- 5개의 설화 모듈과 생성 이야기 결과 계약
- 기본 입력의 장소가 제주로 고정되지 않는지 여부

## 선택적 로컬 LLM

Ollama와 모델이 설치되어 있다면 자연어 분석을 선택적으로 사용할 수 있습니다.

```powershell
$env:NARRATIVE_USE_OLLAMA = "1"
$env:NARRATIVE_OLLAMA_MODEL = "qwen2.5:3b"
python app.py
```

Ollama가 없거나 호출에 실패하면 규칙 기반 분석으로 자동 전환됩니다. 기본 MVP에는 유료 API 키가 필요하지 않습니다.

## 포트폴리오에서 보여줄 점

1. 임의의 개인 TXT를 입력한다.
2. 입력에서 심리적 부담·현재의 욕구·갈등을 추출한다.
3. 결과가 만들어진 근거를 TXT 단서와 Check-in 신호로 설명한다.
4. 팀의 제주 설화 데이터와 개인 상황을 연결한다.
5. 매칭된 서사 모듈을 새로운 이야기로 재조합한다.
6. 평가 결과를 TXT 파일로 저장한다.

## 한계와 다음 단계

- 현재 분석은 규칙 기반 키워드와 선택값 매핑 중심입니다.
- 표준화 점수, 임상적 신뢰도, 위험도 판정은 제공하지 않습니다.
- 설화 원문과 라벨의 출처·저작권 검수는 별도의 데이터 작업입니다.
- 다음 단계는 테스트 케이스 확대, 실제 사용자 피드백, 결과 품질 비교입니다.
- 이후 필요할 때만 로컬 LLM을 추가해 자연어 해석 범위를 넓힙니다.
