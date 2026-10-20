# 09. 점수와 데이터 모델

## 데이터 모델

```text
Story Catalog
  ├─ story_id
  ├─ title
  ├─ category
  └─ stored narrative metadata

Story Beat
  ├─ beat_id
  ├─ source_story_id
  ├─ raw_beat
  ├─ canonical beat
  └─ event_text

Module
  ├─ character
  ├─ place
  ├─ event
  ├─ mood
  └─ wisdom
```

## Raw retrieval score

모듈 카드의 `7.1` 같은 값은 퍼센트가 아니다. 검색 query와 record의 overlap에 IDF 가중치를 적용한 원시 점수다.

예시:

```text
matched terms: 5.1
setting match: 2.0
raw score: 7.1
```

점수 구성요소는 카드의 `점수 구성`에서 확인한다.

## 상대 적합도

후보 카드의 `100%`는 같은 Beat 후보군에서 가장 높은 raw score를 100으로 환산한 값이다.

따라서:

- 동점 후보가 여러 개면 여러 카드가 100%일 수 있다.
- 100%는 문학적 품질이나 정답을 의미하지 않는다.
- raw score와 matched terms를 함께 확인해야 한다.

## 동점 처리

서버의 안정적인 선택 기준은 다음과 같다.

```text
aggregate score
→ Beat coverage
→ matched term count
→ stable story id
```

## 포트폴리오에서의 의미

이 점수 시스템의 목적은 “좋은 설화”를 판정하는 것이 아니라, 검색·선택·재조합 과정을 설명 가능하게 만드는 것이다.

## 실제 스키마와 최소 관계 후보 (2026-10-20 코드 대조)

기준 commit: `88a8208b7183b578568e860d481df51291e87861`. 코드 위치는 모두 저장소 루트 `app.py`다. Story Pack은 새 DB 테이블이 아니라 **검색 결과를 story_id별로 묶은 런타임 dict**다.

### 저장 자료 → 정규화 모델

`load_team_data → _read_collection`은 SQLite를 read-only로 열어 `embeddings → segments → collections`, `embedding_metadata`를 JOIN한다. embedding_id를 record id로 삼고 metadata key별 string/int/float/bool 값을 복원한다. 기존 Chroma DB의 물리 스키마를 사용하며 이 앱에는 CREATE TABLE·migration이 없다.

| 개념 | 실제 사용 필드·키 | 관계·주의점 |
|---|---|---|
| Story Catalog | story_id 또는 record id, title, category, emotion, conflict; wounds_addressed, desires_fulfilled, primary_wound, primary_desire, resonance_triggers, narrative_themes, emotional_arc | catalog의 story_id를 사전 key로 사용. 일부 필드는 없을 수 있음 |
| Story Beat 정규화 | id(beat_id 또는 record id), story_id(source_story_id), story_title, title, category, event_text, beat, raw_beat, search_text, story_dna, structural_attributes, supporting_modules | story_id로 catalog 결합. schema 검증된 독립 Event 테이블이 아님 |
| Module metadata | source_story_id, character_name, place_name, wisdom_summary, mood_emotion | 같은 이야기의 이름·요약을 모아 Beat search_text에 추가. 인물별 고유 entity ID를 부여하지 않음 |
| Source Story Pack | source_story_id, source_story_title, score, fit_score, beat_coverage, matched_terms, top_candidates 등 | select_story_pack가 계산. 저장된 정답·문학 품질 점수 아님 |
| Generative Story DNA | the_question, the_lack, the_cost, the_irony, theme, atmosphere, location, character_type, ending_style, user_intent | build_generative_story_dna의 템플릿 기반 **생성 제약**. 저장 원천의 story_dna 검색 문자열과 구분 |
| Blueprint | protagonist, goal, conflict, world, question, lack, cost, irony, beat_plan | build_narrative_blueprint. beat_plan은 Ki, Shō, Trial, Crisis, Climax, Ketsu 순서 |
| Bound Beat | beat, dna_focus, dna_value, purpose, event_text, source_story_id, source_story, original_beat, module_id, score, matched_terms, structural_attributes, reused | bind_story_pack_to_dna 결과. 부족한 Beat placeholder에는 일부 필드가 없음 |
| Character / Place / Event | 별도 정규화 모델 없음 | 이름/장소는 metadata 문자열, 사건은 event_text. 독립 ID·alias·시점·인과 edge 구현은 확인되지 않음 |

fallback은 `data/story_modules.json`의 4개 흥부전 레코드다. 실제 필드는 id, source_story_id, beat, title, tags, text, source_excerpt, derived_from, source_url, license, annotation_status다. `_fallback_data`는 이 중 일부만 표준 Beat로 내보낸다. source_url·license·원문 excerpt를 정규화 출력의 독립 필드로 보존하지 않으므로 “모든 출력에 출처 URL이 붙는다”고 설명하지 않는다. `data/corpus/story_modules.json`의 영문 28개는 현재 기본 로더 경로와 다르다.

### 출처·최신성·호환성

현재 앱은 import 시 `BEATS, TEAM_MODULES, DATA_STATS`와 IDF를 한 번 구성한다. DB 변경의 자동 반영·레코드별 updated_at·원본 hash·source revision 검증은 구현되지 않았다. DATA_STATS의 source·건수는 현재 읽은 경로의 설명이지 갱신 시각 증명이 아니다. DB 파일/collection 읽기 실패 시 fallback이므로 source를 기록하지 않으면 서로 다른 데이터셋을 같은 기준선으로 오인할 수 있다.

제안 필드(현재 스키마 아님): source_document_id, source_url, source_revision/sha256, updated_at, annotation_version, entity_id, aliases, relation_evidence. 기존 id·source_story_id·beat 값을 바꾸지 않고 선택 필드로 시험하며, 누락은 null/미확인으로 둔다. 데이터 변경 실험 시 기존 Story Pack ID·override module ID의 유효성을 먼저 확인한다.

### Ontology는 관계 실패가 반복될 때만

최소 후보는 Story–HAS_BEAT→Beat, Character–PARTICIPATES_IN→Event, Event–OCCURS_AT→Place, Event–PRECEDES→Event, Event–CAUSES→Event다. 앞의 story/beat 연결 외에는 **제안**이며 “인접 Beat라서 원인이다”라고 자동 생성하지 않는다. 서로 다른 이야기에서 같은 이름의 인물은 같은 개체로 병합하지 않는다. 각 edge에 story_id·근거 문장·검토 상태를 둔다.

현재 태그/문자열만으로 해결되는 검색에는 ontology가 필요 없다. 별칭·시간 순서·인과의 누락으로 실패한 질문을 [검색 평가](../STORY_RETRIEVAL_EVALUATION.md)에 먼저 남기고, 관계 정보가 실제로 필요하다는 근거가 생긴 경우에만 작은 JSON/SQLite 관계 실험을 검토한다. Graph DB는 아직 도입하지 않는다.


