# Narrative AI — MVP2.0

제주 설화 데이터의 검색용 Narrative Metadata를 이용해 새로운 이야기의 생성용 Story DNA를 설계하고, 그 DNA를 제약 조건으로 사용해 일관된 서사를 생성하는 로컬 Narrative Engine입니다.

이 프로젝트의 핵심은 단순한 설화 검색이나 Beat 조합이 아닙니다.

```text
Stored Story DNA
  → Generative Story DNA
  → Narrative Blueprint
  → Constraint-based Beat Plan
  → Module Binding
  → Generated Narrative
```

## 프로젝트 질문

```text
검색용으로 구조화된 기존 설화 데이터로부터
새로운 생성용 Story DNA를 설계하고,
이를 서사 생성의 제약 조건으로 사용하면
재조합 이야기의 일관성을 개선할 수 있는가?
```

## 사용자 흐름

사용자는 자기 상황이나 감정을 입력하지 않습니다. 다음 생성 의도만 선택합니다.

- 분위기: 신비로운, 긴장되는, 서정적인, 어두운, 따뜻한, 모험적인
- 주제: 상실과 회복, 금기와 약속, 떠남과 귀환, 변신, 인간과 자연, 가족과 연결
- 장소: 바다, 오름, 동굴, 숲, 마을, 해안
- 인물 유형: 여행자, 아이, 해녀, 노인, 수호신, 이방인
- 결말: 따뜻한 결말, 반전, 열린 결말, 여운이 남는 결말

선택 결과는 다음 단계로 전달됩니다.

```text
User Intent
  ↓
Source Story Retrieval
  ↓
Generative Story DNA Design
  ├─ The Question
  ├─ The Lack
  ├─ The Cost
  └─ The Irony
  ↓
Narrative Blueprint
  ├─ Protagonist
  ├─ Goal
  ├─ Conflict
  └─ World
  ↓
Beat Plan
  ├─ Ki: 결핍과 세계의 규칙
  ├─ Shō: 핵심 질문의 발생
  ├─ Trial: 대가의 증가
  ├─ Crisis: 아이러니의 노출
  ├─ Climax: 질문에 대한 선택
  └─ Ketsu: 선택의 결과
  ↓
Generated Narrative
```

## Story DNA 계층

### Stored Story DNA

제주 설화에 미리 저장된 검색·매칭용 메타데이터입니다.

- `wounds_addressed`
- `desires_fulfilled`
- `primary_wound`
- `primary_desire`
- `resonance_triggers`
- `emotional_arc`
- `narrative_themes`

### Generative Story DNA

새로운 이야기를 만들 때 동적으로 설계되는 의미 구조입니다.

```json
{
  "the_question": "무언가를 잃은 뒤에도 다시 살아갈 수 있는가?",
  "the_lack": "주인공은 잃어버린 것을 놓아주지 못한다.",
  "the_cost": "되찾고 싶다면 기억의 일부를 내려놓아야 한다.",
  "the_irony": "되찾은 것은 물건이 아니라 다시 걸어갈 수 있다는 사실이다."
}
```

이 네 요소는 독립적인 문장이 아니라 하나의 인과 구조로 설계됩니다.

```text
Question → Lack → Cost → Irony
```

## 데이터와 모듈

현재 MVP는 팀 프로젝트의 제주 설화 pack을 사용합니다.

```text
source: team-data/jeju-stories/chroma_db/chroma.sqlite3
stories: 246
beats: 1,264
modules: 1,431
plot_patterns: 246
```

설화는 다음 단위로 구조화되어 있습니다.

- Story Catalog: 제목, 분류, 감정, 갈등, 장소, Story DNA
- Story Beat: Ki, Shō, Trial, Crisis, Climax, Ketsu
- Character Module: 인물, 유형, 역할
- Place Module: 장소, 지형 유형
- Event Module: 사건, 원래 Beat, 기능
- Mood Module: 분위기, 감정, 키워드
- Wisdom Module: 교훈, 속담, 결말의 의미

현재 검색은 SQLite 메타데이터와 TF-IDF lexical baseline을 사용합니다. 외부 임베딩 API나 유료 LLM 없이 실행할 수 있습니다.

## 현재 구현 범위

- Engine 전용 입력 UI
- 한 질문씩 진행하는 생성 조건 선택
- 조건 없이 랜덤 설화 설계
- Stored Story DNA 기반 Source Story Retrieval
- 연결된 4요소 Generative Story DNA 생성
- Narrative Blueprint 생성
- Beat별 DNA 제약 계획 생성
- 설화 모듈과 생성용 Blueprint 결과 표시
- Blueprint 기반 Narrative Draft 생성
- 기존 MVP1 API 입력과 테스트의 하위 호환

## 실행

Python 3.10 이상에서 실행할 수 있습니다.

```bash
python app.py
```

브라우저에서 [http://127.0.0.1:8000](http://127.0.0.1:8000)을 엽니다.

서버 코드를 수정한 뒤에는 기존 서버를 `Ctrl + C`로 종료하고 다시 실행합니다. 브라우저는 `Ctrl + F5`로 새로고침합니다.

## 테스트

```bash
python -m unittest discover -s tests -v
```

현재 테스트는 다음을 검증합니다.

- 기존 MVP1 입력 호환
- 자유 TXT 시나리오 3종
- Engine 선택값 → Generative Story DNA 연결
- The Question / Lack / Cost / Irony 생성
- Beat별 DNA 제약 계획
- Blueprint 기반 이야기 생성
- 5개 설화 모듈 반환

## 선택적 로컬 LLM

현재 MVP2.0-A의 Generative Story DNA는 규칙 기반 baseline입니다. 이후 자연어 변형이 필요할 때만 Ollama를 연결할 수 있습니다.

```powershell
$env:NARRATIVE_USE_OLLAMA = "1"
$env:NARRATIVE_OLLAMA_MODEL = "qwen2.5:3b"
python app.py
```

## 다음 개발 단계

### MVP2.0-B — Story Pack Selection

Beat별로 서로 다른 설화를 가져오지 않고, 전체 점수를 기준으로 하나의 중심 설화 또는 구조적으로 호환되는 설화 그룹을 먼저 선택합니다.

### MVP2.0-C — Module Binding

Blueprint의 주인공·장소·갈등을 실제 Character·Place·Event·Mood·Wisdom Module에 연결합니다.

### MVP2.0-D — DNA Validation

생성 결과가 처음 설계한 Question·Lack·Cost·Irony를 유지하는지 자동 검증합니다.

## 포트폴리오 핵심

이 프로젝트에서 보여줄 개인 기여는 데이터 수집량이 아닙니다.

```text
검색용 Story DNA와 생성용 Story DNA를 분리하고,
생성용 DNA를 Narrative Blueprint와 Beat 제약으로 변환하여,
설화 재조합의 일관성을 개선하는 Engine 구조를 설계했다.
```
