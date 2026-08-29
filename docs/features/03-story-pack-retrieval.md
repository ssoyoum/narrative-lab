# 03. Story Pack 검색·선택

## 목적

Beat마다 서로 다른 원천을 무작위로 섞기 전에, 전체 이야기의 기준이 될 중심 설화를 선택한다.

## 데이터 소스

```text
team-data/jeju-stories/chroma_db/chroma.sqlite3
stories: 246
beats: 1,264
modules: 1,431
plot_patterns: 246
```

각 Beat record는 제목, 원천 설화 ID, canonical Beat, 사건 텍스트, Story DNA metadata, 검색 텍스트를 가진다.

## 검색 방식

현재는 Chroma vector query가 아니라 SQLite metadata를 사용하는 투명한 lexical baseline이다.

```text
User Intent + Generative DNA
  ↓ token query
record search_text와 overlap 계산
  ↓
TF-IDF raw score
  ↓
설화별 점수 합산
  ↓
중심 Story Pack 선택
```

## 중심 Pack 선택 기준

```text
aggregate score
→ Beat coverage
→ matched term count
→ stable story id
```

중심 Pack은 기본 생성에서 모든 모듈을 같은 원천으로 유지해 서사 일관성을 확보한다.

## 중요한 구분

- `BASE STORY PACK`: 기본 생성에 사용하는 중심 원천
- `BEAT별 재매칭 후보`: 각 Beat에서 탐색 가능한 대안 원천
- `ACTIVE REMIX MODULES`: 사용자가 후보를 선택한 뒤 실제 생성에 적용된 원천

## 현재 한계

- lexical matching이므로 동의어·문맥·사건 인과를 충분히 이해하지 못한다.
- 중심 Pack 선택과 후보 추천의 점수는 문학적 품질 점수가 아니다.
