# Narrative Engine 기능 문서

현재 MVP2.0의 기능을 구현 단위별로 정리한 문서입니다.

## 기능 목록

| 문서 | 기능 | 핵심 질문 |
|---|---|---|
| [01-user-intent.md](01-user-intent.md) | 사용자 생성 조건 입력 | 사용자는 어떤 이야기를 만들고 싶은가? |
| [02-generative-story-dna.md](02-generative-story-dna.md) | Generative Story DNA | 선택 조건을 어떻게 인과 구조로 바꾸는가? |
| [03-story-pack-retrieval.md](03-story-pack-retrieval.md) | Story Pack 검색·선택 | 어떤 원천 설화를 기준으로 삼을 것인가? |
| [04-match-report.md](04-match-report.md) | Match Report | 왜 이 설화가 선택됐는가? |
| [05-beat-dna-binding.md](05-beat-dna-binding.md) | Beat DNA Binding | 각 Beat가 어떤 DNA 역할을 맡는가? |
| [06-beat-rematch-candidates.md](06-beat-rematch-candidates.md) | Beat별 재매칭 후보 | 각 단계에 다른 설화를 어떻게 추천하는가? |
| [07-cross-story-remix.md](07-cross-story-remix.md) | Cross-Story Remix | 선택한 후보를 실제 생성에 어떻게 반영하는가? |
| [08-blueprint-and-generation.md](08-blueprint-and-generation.md) | Blueprint·Narrative 생성 | 설계된 제약으로 이야기를 어떻게 만드는가? |
| [09-score-and-data-model.md](09-score-and-data-model.md) | 점수·데이터 모델 | 검색 결과를 어떻게 설명 가능한 형태로 보여주는가? |

## 전체 흐름

```text
User Intent
  ↓
Generative Story DNA
  ↓
Source Story Retrieval
  ↓
Narrative Blueprint
  ↓
Beat DNA Binding
  ↓
Match Report + Beat Candidates
  ↓
Optional Cross-Story Remix
  ↓
Generated Narrative
```

기본 생성은 하나의 중심 Story Pack을 사용하고, 사용자가 후보 카드를 선택했을 때만 여러 설화를 섞는 Remix 모드로 전환됩니다.
