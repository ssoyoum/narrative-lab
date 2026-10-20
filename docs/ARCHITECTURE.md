# Narrative Engine System Architecture

## Overview

Narrative Engine은 제주 설화 데이터의 검색용 Narrative Metadata를 이용해 새로운 이야기의 생성용 Story DNA를 설계하고, 원천 사건을 Beat 제약에 연결한 뒤 새로운 서사를 생성하는 로컬 Narrative AI입니다.

현재 검색·DNA·규칙 초안은 Python 표준 라이브러리와 팀 SQLite metadata(부재 시 로컬 fallback)로 실행됩니다. 다만 `app.py:generate_engine_folktale → generate_llm_folktale → call_llm`은 키가 있으면 OpenAI Responses API를 호출하고, 사용 불가 시 규칙 초안으로 돌아옵니다. 아래 도식과 Zero-Cost/미구현 목록은 초기 baseline 설명이며 선택적 모델 경로의 현재 상태와 구분해야 합니다.

2026-10-20 코드 대조: [실제 검색 흐름·개선 선택지](features/03-story-pack-retrieval.md), [실제 필드·제안 관계](features/09-score-and-data-model.md), [검색 평가 18문항](STORY_RETRIEVAL_EVALUATION.md), [일관성 규칙](STORY_CONSISTENCY_RULES.md). 자동 DNA 의미 검증·벡터/그래프 검색은 미구현이며 이번에는 테스트·모델 호출을 실행하지 않았습니다.

세부 문서는 [architecture 문서 목록](architecture/README.md)에서 확인할 수 있습니다.

---

## High-Level Architecture

```mermaid
graph TB
    subgraph Client["🖥️ Client Layer"]
        Browser["Browser UI<br/>HTML · CSS · JavaScript"]
        Wizard["Intent Wizard<br/>분위기 · 주제 · 장소 · 인물 · 결말"]
        Result["Result Workspace<br/>DNA · Report · Remix · Narrative"]
    end

    subgraph API["⚙️ Application Layer"]
        Server["Python HTTP Server<br/>app.py"]
        Endpoint["POST /api/generate"]
        Orchestrator["Narrative Orchestrator<br/>build_engine_result()"]
    end

    subgraph Narrative["🧠 Narrative Layer"]
        Intent["User Intent Mapper"]
        DNA["Generative Story DNA<br/>Question · Lack · Cost · Irony"]
        Blueprint["Narrative Blueprint<br/>Goal · Conflict · World · Beat Plan"]
        Binding["Beat DNA Binding<br/>Ki · Shō · Trial · Crisis · Climax · Ketsu"]
        Generator["Narrative Generator<br/>Rule-based Draft"]
    end

    subgraph Retrieval["🔎 Retrieval & Explanation Layer"]
        Loader["Team Data Loader"]
        TFIDF["TF-IDF Lexical Baseline"]
        Pack["Story Pack Selector"]
        Report["Match Report"]
        Candidates["Beat Rematch Candidates"]
        Remix["Cross-Story Remix"]
    end

    subgraph Data["💾 Data Layer"]
        SQLite["Chroma SQLite Export<br/>story_catalog · story_beats · story_modules"]
        Memory["In-Memory Records<br/>BEATS · DATA_STATS"]
    end

    subgraph Optional["🧩 Optional Local AI"]
        Ollama["Ollama<br/>Optional natural-language transformation"]
    end

    Browser --> Wizard
    Wizard --> Endpoint
    Endpoint --> Server
    Server --> Orchestrator
    Orchestrator --> Intent
    Intent --> DNA
    DNA --> Blueprint
    Orchestrator --> Loader
    Loader --> SQLite
    Loader --> Memory
    Memory --> TFIDF
    TFIDF --> Pack
    Pack --> Binding
    Blueprint --> Binding
    Binding --> Report
    Binding --> Candidates
    Candidates --> Remix
    Remix --> Generator
    Binding --> Generator
    DNA --> Generator
    Generator --> Result
    Report --> Result
    Ollama -. optional .-> Generator
```

---

## Data Flow

### Initial Generation

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant A as Python API
    participant D as Team SQLite Data
    participant E as Narrative Engine
    participant R as Result UI

    U->>B: Select User Intent
    B->>A: POST /api/generate
    A->>E: build_engine_result()
    E->>E: Build Generative Story DNA
    E->>D: Load Story Catalog / Beats / Modules
    D-->>E: Stored Story Metadata
    E->>E: TF-IDF Retrieval
    E->>E: Select Coherent Story Pack
    E->>E: Build Narrative Blueprint
    E->>E: Bind Beat to DNA Role
    E->>E: Build Match Report and Candidates
    E->>E: Generate Narrative Draft
    E-->>A: JSON Result
    A-->>B: Render Result Workspace
    B-->>R: DNA · Report · Beat Candidates · Narrative
```

### Cross-Story Remix

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant A as Python API
    participant E as Narrative Engine

    U->>B: Click “이 후보 적용”
    B->>B: Add beat_overrides[Beat] = module_id
    B->>A: POST /api/generate + beat_overrides
    A->>E: Rebuild with selected overrides
    E->>E: Keep User Intent and Generative DNA
    E->>E: Replace selected Bound Beat
    E->>E: Recalculate Remix Coverage
    E->>E: Generate Cross-Story Remix
    E-->>B: ACTIVE REMIX MODULES + updated narrative
```

---

## Module Structure

```bash
narrative-lab/
├── app.py                         # HTTP server and Narrative Engine
├── index.html                     # Intent wizard and result layout
├── script.js                      # API calls, rendering, rematch interaction
├── styles.css                     # UI styling and responsive layout
├── data/
│   └── story_modules.json         # Local fallback data
├── team-data/
│   └── jeju-stories/
│       └── chroma_db/
│           └── chroma.sqlite3     # Team Story Pack source
├── tests/
│   ├── test_mvp1_1.py             # Legacy / personal narrative compatibility
│   ├── test_mvp1_3.py             # MVP1.3 scenarios
│   └── test_mvp2.py               # DNA, retrieval, rematch, remix tests
├── docs/
│   ├── ARCHITECTURE.md            # This document
│   └── features/                  # Feature-level specifications
└── README.md
```

### `app.py` 내부 책임

| 영역 | 주요 책임 |
|---|---|
| Data Loader | SQLite collection을 읽고 Story Beat record로 정규화 |
| Retrieval | query token과 `search_text`의 TF-IDF lexical score 계산 |
| Story Pack | 중심 원천 설화 선택 |
| DNA Builder | User Intent를 Question·Lack·Cost·Irony로 변환 |
| Blueprint | 주인공·목표·갈등·세계·Beat Plan 생성 |
| Binding | 각 Beat와 원천 사건 및 DNA 역할 연결 |
| Match Report | 점수·커버리지·바인딩·리믹스 범위 설명 |
| Remix | `beat_overrides`로 선택 사건 교체 |
| Generator | Bound Beat와 DNA를 결합해 서사 초안 생성 |
| HTTP Handler | 정적 파일과 `/api/generate` 제공 |

---

## Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | HTML5, CSS3, Vanilla JavaScript | Wizard, result workspace, remix interaction |
| Backend | Python 3.10+ standard library | Local HTTP API and engine orchestration |
| Data | SQLite / Chroma export | Team Story Pack storage |
| Retrieval | TF-IDF-style lexical baseline | Transparent metadata matching |
| Test | Python `unittest` | API contract and narrative flow verification |
| Optional AI | Ollama | Optional local natural-language transformation |
| Hosting | Local process | `python app.py` |

---

## Zero-Cost Strategy

```mermaid
graph LR
    A[User Intent] --> B[Local Python Engine]
    B --> C[SQLite Metadata]
    C --> D[TF-IDF Retrieval]
    D --> E[Rule-based DNA / Blueprint]
    E --> F[Generated Draft]
    F --> G[Browser Result]
    H[Optional Ollama] -. optional .-> F
```

| Resource | Cost | Strategy |
|---|---:|---|
| External LLM API | ₩0 | MVP baseline uses deterministic rules |
| Vector database service | ₩0 | Existing SQLite export is read locally |
| Backend hosting | ₩0 | Local Python server |
| Dataset | ₩0 | Existing team Story Pack reuse |
| Optional local LLM | Local machine cost | Ollama can be enabled only when available |

The zero-cost strategy trades model-level semantic quality for reproducibility, inspectable scores, and a low-friction portfolio demo.

---

## API Contract

### `POST /api/generate`

#### Basic request

```json
{
  "engine": {
    "atmosphere": "mysterious",
    "theme": "forbidden_promise",
    "location": "cave",
    "character": "outsider",
    "ending": "echo"
  },
  "context": {}
}
```

#### Remix request

```json
{
  "engine": {
    "atmosphere": "mysterious",
    "theme": "forbidden_promise",
    "location": "cave",
    "character": "outsider",
    "ending": "echo"
  },
  "context": {},
  "beat_overrides": {
    "Ki": "L_050_Ki",
    "Shō": "L_166_Shō"
  }
}
```

#### Main response groups

```text
generative_story_dna
narrative_blueprint
match_report
beat_recommendations
bound_beats
active_modules
remix
generated
data_source
```

---

## Current MVP Boundaries

### Implemented

- User Intent wizard
- Generative Story DNA
- Coherent Story Pack retrieval
- Match Report
- Beat-level candidate recommendations
- Click-to-remix `beat_overrides`
- Active Remix module display
- Rule-based narrative draft
- Legacy MVP input compatibility

### Not yet implemented

- Automatic DNA Validation of generated prose
- Semantic embedding retrieval
- Natural-language transformation of source events
- Persistent user sessions or saved remix history
- Production hosting and multi-user concurrency

---

## Verification Targets

The architecture should be evaluated with the following checks:

| Check | Question |
|---|---|
| Retrieval | Does the selected Story Pack match the User Intent? |
| Binding | Does each Beat have the correct DNA role? |
| Remix | Does clicking a candidate replace the correct Beat? |
| Visibility | Do `ACTIVE REMIX MODULES` and generated prose reflect the override? |
| Validation | Does the final prose preserve Question·Lack·Cost·Irony? |

---

*Last updated: 2026-08-25*

