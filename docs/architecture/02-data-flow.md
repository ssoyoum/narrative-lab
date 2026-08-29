# Data Flow

## Initial Generation

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant A as API
    participant D as SQLite Data
    participant E as Narrative Engine

    U->>B: Select atmosphere / theme / location / character / ending
    B->>A: POST /api/generate
    A->>E: build_engine_result()
    E->>E: Build Generative Story DNA
    E->>D: Read story_catalog / story_beats / story_modules
    D-->>E: Normalized Story Beat records
    E->>E: Token overlap + IDF score
    E->>E: Select Story Pack
    E->>E: Build Blueprint and Beat Plan
    E->>E: Bind events to DNA roles
    E->>E: Build Match Report and Beat Candidates
    E->>E: Generate Narrative Draft
    E-->>A: JSON response
    A-->>B: Render result workspace
```

## Cross-Story Remix

```mermaid
sequenceDiagram
    participant U as User
    participant B as Browser
    participant A as API
    participant E as Engine

    U->>B: Click Beat candidate
    B->>B: Store beat_overrides[Beat] = module_id
    B->>A: POST /api/generate + overrides
    A->>E: Rebuild request
    E->>E: Preserve User Intent and Generative DNA
    E->>E: Replace selected Bound Beat
    E->>E: Build ACTIVE REMIX MODULES
    E->>E: Recalculate Remix Report
    E->>E: Generate Cross-Story Remix
    E-->>B: Updated narrative and modules
```

## Main State Objects

```text
engine
  → user selection values

generative_story_dna
  → Question / Lack / Cost / Irony

narrative_blueprint
  → protagonist / goal / conflict / world / beat_plan

bound_beats
  → Beat / DNA focus / source story / event text

beat_overrides
  → user-selected Beat replacement map

generated
  → title / text / generation_mode
```
