# 이야기 일관성 규칙과 검증 경계

기준 commit: `88a8208b7183b578568e860d481df51291e87861`, 2026-10-20 정적 검토. 최초 정적 검토 기록이다. 아래에 이후 코드 수정·테스트 실행 결과를 별도로 기록한다. 모델 호출은 하지 않았다.

## 구현된 제약과 미구현 검증

| 영역 | 현재 코드에서 강제하는 것 | 보장하지 못하는 것 |
|---|---|---|
| 생성 DNA | `app.py:build_generative_story_dna`의 고정 theme/intent 매핑 | 본문이 Question/Lack/Cost/Irony를 실제로 구현하는지 |
| Beat 목적·순서 | `build_narrative_blueprint`, `BEAT_DNA_BINDINGS`의 6개 순서·focus | 이야기 내부 실제 시간·원인 순서 |
| 원천 통일 | `select_story_pack`, `bind_story_pack_to_dna`의 story_id 제한 | 같은 원천이면 문장·설정이 자연스럽다는 보장 |
| override | 지정 module ID와 raw/canonical Beat 호환성 확인 | 인물 동일성·세계관·인과 호환성 검증 |
| 원천 부족 | 없는 Beat는 placeholder, reused 표시 | 충분한 근거가 있다는 보장, 일반 검색의 자동 abstention |
| 생성 prompt | `build_generation_prompt`가 선택 조건·DNA·추상 패턴을 전달, 원문/고유 사건 복사 금지 지시 | 지시 준수·표절 방지·환각 검증. prompt는 validator가 아님 |
| 모델 장애 | `generate_engine_folktale`가 LLMUnavailableError를 규칙 초안으로 대체 | fallback의 문학적 일관성과 모든 기능 품질 |

현재 `_parse_generated_folktale`는 비어 있지 않은 제목·본문 형식만 확인하며 의미 검증을 하지 않는다. Match Report는 연결/커버리지 설명이며 설정 위반률 검증 결과가 아니다.

## 제안 규칙을 테스트 가능한 관찰로 바꾸기

다음은 **후속 검증 후보**다. 인물·관계 entity 테이블이나 자동 DNA validator가 이미 구현됐다는 뜻이 아니다.

| ID | 충돌 유형·재현 입력 | 기대 판정·필요 근거 | 테스트 변환 방식 |
|---|---|---|---|
| C01 | engine.character=haenyeo인데 본문이 다른 주인공만 묘사 | 선택 인물 제약 위반 여부를 사람이 판독 | 입력 enum 매핑은 구조 검사, 주인공 의미는 라벨된 본문 fixture |
| C02 | 같은 이름이 서로 다른 원천에서 형/동생·부모/자식으로 충돌 | story_id와 원천 관계를 먼저 고정 | 동명이인 fixture와 인물 role 라벨. 이름 문자열만으로 동일인 병합 금지 |
| C03 | goal과 반대 선택을 했는데 결과·동기 설명이 없음 | 목표 변화가 텍스트로 설명되는지 | goal, 선택, 결과의 근거 구간을 수동 라벨 |
| C04 | 동굴에서 시작했는데 이동 없이 해안 사건으로 바뀜 | 장소 이동 설명 여부 | Beat별 장소/이동 evidence를 사전 정의한 fixture |
| C05 | 세계관의 금기를 어기고 대가·예외 설명 없음 | 규칙·위반·결과의 근거가 함께 있어야 함 | forbidden_promise theme에 rule/exception/cost 라벨 |
| C06 | 죽음/치료·귀환 등 사건의 선후가 뒤집힘 | 원천/새 설정의 순서 관계와 비교 | PRECEDES 후보를 작은 수동 목록으로 정의. Beat 배열 순서만으로 pass 금지 |
| C07 | 사건 A 뒤 B가 나온 것을 원인으로 단정 | 인과가 명시됐는지, 단순 선후인지 | [검색 평가](STORY_RETRIEVAL_EVALUATION.md)의 Q15 활용. 미명시 인과는 보류 |
| C08 | 유효하지 않은 override ID·Beat 종류·다른 story ID | 현재 코드의 fallback/무시 동작과 요청 적용 여부 구분 | 실제 applied bound.module_id를 비교. remix.active만으로 성공 판정 금지 |
| C09 | 기본 Pack에 없는 Beat를 다른 원천 override로 보충 | 코드상 후보 없음 continue가 override 전에 있음 | 누락 Beat+유효 대안 fixture로 실제 적용 결과를 검증. 현재는 위험 후보, 재현 미실행 |
| C10 | 모델 결과가 원천 event_text를 복사 | prompt에서 원문을 빼도 결과 복사 가능성은 별도 | prompt 구조 검사와 최종문 유사도/고유명 판독을 별개로 측정 |

모든 제안 규칙에 `rule_id, input, source_ids, expected, evidence_spans, applicability, reviewer, annotation_version`을 기록한다. 데이터가 없거나 의도적으로 각색한 경우 N/A/검토 필요를 허용하고 자동 실패/성공으로 바꾸지 않는다.

## 기존 테스트의 범위

- `tests/test_mvp2.py`: DNA 필드·Blueprint·바인딩·후보·Remix 응답 검사.
- `tests/test_llm_generation.py`: 추상화에서 원문 제외, prompt section, mocked provider 응답 parsing, 키 없는 fallback.
- `tests/test_mvp1_1.py`, `tests/test_mvp1_3.py`: legacy 개인 맥락·기존 API 호환 경로.
- `scripts/smoke_test.py`: 서버가 실행 중일 때 API 흐름 확인. 실제 브라우저 클릭 E2E와 다름.

기존 테스트가 생성문을 deterministic baseline 문자열로 기대하는 부분과 선택적 OpenAI 경로는 실행 환경별로 결과가 달라질 수 있다. 이번에는 실행하지 않았으므로 통과/실패를 추정하지 않는다.

## 평가·도입 판단

검색 Recall이 좋아져도 설정 위반은 별도로 악화될 수 있다. 동일 검색 결과로 규칙 초안과 모델 생성을 비교하고, 동일 생성 조건에서 검색만 바꾸는 실험을 분리한다. Live 생성에는 승인된 비용·모델·최대 요청량이 필요하다.

먼저 기존 필드/사람 판독으로 C01~C10을 검사한다. 별칭·시간·인과 오류가 반복되어 현재 문자열 모델로 판정하기 어렵다는 사례가 쌓일 때만 entity ID/관계 annotation을 제안한다. ontology나 graph DB부터 추가하지 않는다.


## 재현 후 수정한 규칙 (2026-10-20)

C08/C09는 `tests/test_remix_contract.py`의 합성 fixture로 검증했다. 기본 Pack에 climax가 없어도 다른 Pack의 유효한 override를 먼저 적용한다. 알 수 없는 Beat·없는 ID·호환되지 않는 Beat는 ValueError로 거절하며 기존 API가 HTTP 400으로 반환한다. 요청 성공/Remix 표시만 보고 적용됐다고 추정하던 위험을 줄인다. 누락 원천은 계속 placeholder로 남긴다. 전체 unittest 27개 통과. 인물 성격·시간·인과·생성 본문 DNA 반영의 의미 검증은 여전히 미구현이다.

## 선택적 모델의 실패 격리 (2026-10-21)

`app.py:call_llm` → `_extract_openai_text` → `_parse_generated_folktale`에서 응답 구조와 최소 형식을 확인한다. JSON 최상위가 객체가 아니거나 output/content 타입이 잘못된 경우, 명시된 응답/메시지 상태가 completed가 아닌 경우, provider error·refusal·잘못된 UTF-8/JSON·빈 응답·제목만 있는 출력은 `LLMUnavailableError`로 정리한다. 상태 필드가 없는 기존 output_text 응답은 호환성을 유지한다. 중첩 output에서는 assistant message의 문자열 output_text만 사용하고 reasoning 등은 본문으로 만들지 않는다.

`generate_engine_folktale`는 기존 `generation_status=fallback`, `generation_provider=recombined baseline`과 규칙 초안을 유지한다. provider 응답 본문·오류 상세를 generation_notice에 복사하지 않는다. API의 새로운 상태나 자동 재시도는 추가하지 않았다. 정상 제목·본문을 가진 출력도 인물·장소·DNA·시간·인과의 의미 검사를 통과했다는 뜻은 아니다. 6개 단락 조건이나 한국어 여부를 자동으로 판정하지 않는다.

`tests/test_provider_boundary.py`는 네트워크 함수를 mock하여 정상 출력 2형식, 구조/타입 오류, 불완전/실패 응답, refusal, UTF-8/JSON 오류, HTTP 429·시간 초과·연결 오류, 제목만 있는 출력을 검사한다. 같은 테스트를 변경 전 코드에 적용했을 때 하위 사례 실패 6건·오류 9건을 재현했고, 수정 후 전체 unittest 31개가 통과했다. 고정 검색 질문은 fallback 18개·팀 DB 18개에서 기존 지표와 같았다. 이 결과는 모델 호출 성공률이나 이야기 의미 정확도가 아니다. Live 모델은 호출하지 않았다.
