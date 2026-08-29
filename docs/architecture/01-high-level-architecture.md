# High-Level Architecture

## Overview

Narrative Engine은 사용자의 생성 의도를 Generative Story DNA로 변환하고, 제주 설화 데이터에서 원천 사건을 검색·바인딩해 이야기를 생성합니다.

```mermaid
graph TB
    subgraph Client["Client Layer"]
        Browser["Browser UI<br/>HTML · CSS · JavaScript"]
        Wizard["Intent Wizard"]
        Result["Result Workspace"]
    end

    subgraph Application["Application Layer"]
        Server["Python HTTP Server"]
        API["POST /api/generate"]
        Engine["Narrative Orchestrator"]
    end

    subgraph Narrative["Narrative Layer"]
        DNA["Generative Story DNA"]
        Blueprint["Narrative Blueprint"]
        Binding["Beat DNA Binding"]
        Generator["Narrative Generator"]
    end

    subgraph Retrieval["Retrieval Layer"]
        Loader["Team Data Loader"]
        Search["TF-IDF Lexical Baseline"]
        Pack["Story Pack Selector"]
        Report["Match Report"]
        Remix["Cross-Story Remix"]
    end

    subgraph Data["Data Layer"]
        SQLite["Chroma SQLite Export"]
        Memory["In-Memory Beat Records"]
    end

    Browser --> Wizard
    Wizard --> API
    API --> Server --> Engine
    Engine --> DNA --> Blueprint
    Engine --> Loader --> SQLite
    Loader --> Memory --> Search --> Pack
    Pack --> Binding
    Blueprint --> Binding
    Binding --> Report
    Binding --> Remix
    Remix --> Generator
    Binding --> Generator
    DNA --> Generator
    Generator --> Result
    Report --> Result
```

## Design Principle

검색용 Story DNA와 생성용 Story DNA를 분리한다.

```text
Stored Story Metadata
  → Retrieval
  → Generative Story DNA
  → Blueprint Constraint
  → Bound Beat
  → Narrative Draft
```

## Runtime Modes

- Coherent Story Pack mode: 하나의 원천 설화로 기본 생성
- Cross-Story Remix mode: 사용자가 Beat 후보를 선택한 경우 여러 원천 설화를 조합
