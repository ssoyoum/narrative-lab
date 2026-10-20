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

## 검색·생성 연결의 실제 경로 (2026-10-20)

기준 commit: `88a8208b7183b578568e860d481df51291e87861`. 이 절을 STORY_RETRIEVAL_ARCHITECTURE 및 SEMANTIC_SEARCH_OPTIONS 역할로 재사용한다. 코드·DB·검색 알고리즘은 변경하지 않았다.

1. `app.py:load_team_data`가 Chroma SQLite의 story_catalog/story_beats/story_modules metadata를 읽는다. DB 부재·SQLite 오류 시 `_fallback_data`로 전환한다. import 시 메모리에 적재하므로 매 요청에 SQL 검색하는 구조가 아니다.
2. `idf_scores(BEATS)`는 search_text의 token 집합으로 문서빈도를 계산한다. `tokens`는 영문/숫자/한글 정규식·소문자·고정 불용어이며 형태소 분석·일반 동의어 사전은 아니다.
3. `_retrieval_query`는 DNA의 setting/characters/emotion/conflict/beats, personal_context, context의 location/mood/tone/ending을 문자열로 묶는다. **dna.keywords는 직접 읽지 않는다.**
4. `_rank_retrieval_records`는 query와 record token **집합 교집합의 IDF 합**에 구조 1.5, setting/location/mood 각각 2, wounds/desires의 story_dna 문자열 일치 각각 3을 더한다. TF 반복빈도·cosine normalization은 없으므로 정확히는 IDF 기반 lexical 가산점 기준선이다.
5. Beat 순위는 점수 내림차순 → 일치 token 수 → stable id. `select_story_pack`는 이야기별 상위 5개 Beat 점수에 1/(index+1) 가중치를 주고 canonical Beat coverage×2를 더한다. 동점은 coverage → 일치 token 수 → story id.
6. `retrieve_modules`는 선택 story_id로 후보를 제한한 뒤 TARGET_BEATS 순서로 하나씩 고르고 나머지를 채운다. **반환 순서는 순수 검색 점수 순위가 아니라 Beat 다양성 배치**다. MRR 측정 시 이 리스트와 raw ranking을 혼동하지 않는다.
7. `retrieve_beat_recommendations`는 raw Beat 우선/canonical Beat 대체, story별 중복 제거로 대안을 만든다. `bind_story_pack_to_dna`는 기본 Pack과 override ID/Beat 호환성으로 실제 사용 사건을 결정한다.
8. `build_engine_result`가 선택·바인딩·Match Report·규칙 초안을 구성하고 `generate_engine_folktale`를 호출한다. `build_generation_prompt → build_source_patterns → abstract_story_beat`는 원천 event_text 대신 추상 패턴을 전달한다. OpenAI 사용 불가 시 규칙 기반 결과를 반환한다. 원천 사건과 같은 문장을 생성하는 것이 LLM 경로의 목표는 아니다.

### 실제 지원하는 제한과 지원하지 않는 필터

- story_id 제한은 retrieve_modules 내부 함수 인자. API에 범용 SQL/metadata filter DSL은 없다.
- Beat 종류·override module ID 호환성 제한, 후보 목록의 원천 설화 중복 제거는 구현되어 있다.
- context.location/mood는 점수 가산점이며 **해당 장소/감정을 강제로 만족시키는 필터가 아니다**. tone/ending은 query 문자열에 들어갈 뿐 별도 점수 항목이 없다.
- source_url, 연도, license, 인물 관계, 사건 시간범위 필터와 alias resolution은 확인되지 않았다.
- Chroma vector query, embedding similarity, GraphRAG, ontology inference는 현재 경로에 없다.

### 측정할 실패와 이미 보이는 제약

| 구분 | 코드에서 확인한 제한 | 아직 측정하지 않은 것 |
|---|---|---|
| 어휘 차이 | tokens의 완전 token 일치. 조사가 붙은 단어·다른 표현은 별개 | 동의어 질문의 Recall 하락 폭 |
| 관계·다중 단계 | 이야기 내 인물·사건 신호를 search_text에 합치며 edge traversal 없음 | 관계 오해가 실제 최종문에 생기는 비율 |
| 자료 없음 | 전체 record를 점수 0이어도 순위에 남김. Pack의 “참고 설화 없음”은 후보 자체가 없을 때만 | 관련 없는 질문의 올바른 보류율 |
| 오래된 자료 | import 후 DB 갱신 자동 탐지 없음 | 변경 자료가 화면에 반영되기까지 시간 |
| 구조 부족 | fallback 흥부전 4 Beat에는 transition이 없음 | 팀 DB와 fallback에서 바인딩·테스트 차이 |
| override | 바인딩에서 기본 Pack 후보가 없으면 placeholder로 continue한 뒤 override 선택에 도달하지 않음 | 없는 Beat를 대안 원천으로 채울 때 영향 |
| 근거 표시 | fallback 정규화에서 URL·license 개별 필드 소실 | 사용자가 실제 원문을 추적할 수 있는 비율 |

이 표의 영향은 실험 전 가설이며 재현된 버그 수로 세지 않는다. 특히 confidence/fit_score 100은 후보 내 상대값이며 자료 충분성·사실 정확도 임계값이 아니다.

### 개선 선택지와 중단 기준 — 모두 미구현

| 후보 | 먼저 적용할 실패 | 비용·복잡성 | 동일 질문 비교 |
|---|---|---|---|
| metadata hard filter | 명시한 story/Beat/출처 조건 위반 | 기존 SQLite/인메모리 재사용, 낮음 | 조건 위반률과 recall을 함께 봄 |
| 작은 동의어·표기 정규화 | 형/형님, 별칭, 조사·표기 차이 | 낮음. 사전 편향·오탐 검토 필요 | 정확 일치 질문 회귀와 동의어 Recall/MRR |
| 로컬 embedding + 선형 similarity | 어휘는 다르나 같은 상황 질문 | 모델 크기·추론 비용·버전 관리 추가 | 동의어 개선과 latency·false positive |
| 관계 JSON/SQLite join | 이름 동명이인·사건 선후·근거 경로 | annotation·검토 비용이 핵심 | 관계 질문의 근거 완전성·설정 위반 |
| GraphRAG/graph DB | 위 대안으로 못 푼 반복 다중 관계 실패 | 추출 오류·색인·운영·갱신 비용 큼 | 관계 subset에서만 이득인지 구분 |

1차 실험은 기존 BEATS와 동일 데이터 snapshot으로 lexical 기준선을 저장한 뒤 작은 동의어 정규화 후보와 비교한다. 현재 gold는 [STORY_RETRIEVAL_EVALUATION.md](../STORY_RETRIEVAL_EVALUATION.md)에 사전 정의한다. 새로운 DB나 프레임워크는 필요하지 않다.

**제안 채택 기준:** 검토된 관계 질문이 최소 5개 확보되고 단순 필터·동의어로 해결되지 않을 때만 관계 실험으로 넘어간다. 관련 질문 근거 성공률 10%p 이상 개선, 정확 일치 subset 악화 없음, 생성 설정 위반률 악화 없음, 동일 장비 검색 p95 2배 이내를 초기 판단 기준으로 둔다. 이는 측정 결과가 아닌 사전 목표다. 2회 제한 실험에서 개선이 없거나 annotation 근거가 부족하면 중단하고 lexical 기준선을 유지한다.


