# Story 검색 평가: 기준선·gold·동일 질문 비교

기준 commit: `88a8208b7183b578568e860d481df51291e87861`, 확인일 2026-10-20. 최초 설계 이후 아래 실행 가능한 평가기를 추가해 2026-10-20 기준선을 측정했다. 기존 검색 알고리즘·데이터는 유지하며 모델 호출은 하지 않았다.

## 평가 대상과 데이터 고정

현재 메커니즘은 [기존 검색 문서](features/03-story-pack-retrieval.md), 실제 필드는 [데이터 모델](features/09-score-and-data-model.md)을 기준으로 한다.

- 운영 앱 기본 경로 A: Chroma SQLite의 story_catalog/story_beats/story_modules. `app.py:load_team_data`가 읽는 collection의 실제 ID·원문 export를 이번 환경에서 조회하지 못했다. 문서의 246/1,264/1,431은 과거 기록이며 현재 실측으로 재인용하지 않는다.
- 정적 검토 가능한 경로 B: `data/story_modules.json`의 **흥부전 한 이야기·4개 Beat**. 아래 18문항은 해당 파일의 현대어 annotation에서 기대 근거를 사전 정의했다. 원전 전체의 사실 검증이나 제주 전체 Story Pack 성능을 대표하지 않는다.
- `data/corpus/story_modules.json`의 영문 28개는 현재 FALLBACK_MODULE_FILE이 아니다. 파일 존재를 기본 검색 색인 포함으로 간주하지 않는다.
- A와 B의 결과는 분리한다. 데이터 source·파일 hash·레코드 수·Beat 라벨 검토 버전과 코드 commit을 각 보고서에 저장한다. B는 한 Pack이라 Pack Recall/MRR가 쉽게 1이 되는 퇴화 평가다. **Beat 검색의 근거 회수와 보류**를 우선 측정하고 다중 Pack 성능은 A gold 확정 뒤 평가한다.

## 18문항의 사전 기대 근거

Pack ID는 전부 `heungbu-1865-gyeongpan-25`다. 아래 S/C/K/R은 파일의 정확한 module ID 축약이다.

- S = `heungbu-1865-gyeongpan-25-setup`: 흥부·놀부 형제, 놀부의 재산 독차지·흥부 가족 축출.
- C = `heungbu-1865-gyeongpan-25-conflict`: 품팔이·형에게 도움 요청·거절·가난.
- K = `heungbu-1865-gyeongpan-25-climax`: 다친 제비 다리 치료, 이듬해 박씨, 심고 기다림.
- R = `heungbu-1865-gyeongpan-25-resolution`: 보물·가난 탈출, 놀부 모방과 재앙.

gold 근거는 `text` 필드 기준이다. annotation_status는 human review pending이며 Beat 라벨 자체의 문학적 정답성은 별도 검토해야 한다.

| ID | 유형 / 질문 | 기대 근거 | 정답 핵심·판독 경계 |
|---|---|---|---|
| Q01 | 정확 일치: 흥부와 놀부는 어떤 사이인가? | S | 형제. 다른 가족관계 추가 금지 |
| Q02 | 정확 일치: 흥부가 형에게 도움을 청한 뒤 어떻게 됐나? | C | 번번이 거절, 가난 지속 |
| Q03 | 정확 일치: 흥부는 다친 제비를 어떻게 했나? | K | 다리를 치료하고 날려 보냄 |
| Q04 | 정확 일치: 놀부의 박에서는 무엇이 나왔나? | R | 재앙과 꾸지람. 구체 항목 추가 금지 |
| Q05 | 동의어: 부모의 유산을 혼자 차지한 사람은? | S | 놀부. 재산/유산 표현 차이 |
| Q06 | 동의어: 가족의 생계를 위해 노동한 대목은? | C | 가족을 먹여 살리려고 품을 팜 |
| Q07 | 동의어: 상처 입은 새를 돌보는 장면을 찾아줘. | K | 다친 제비 치료. 새 이름 추정 아님 |
| Q08 | 동의어: 빈곤에서 벗어나는 결말은? | R | 박에서 보물이 나옴 |
| Q09 | 별칭: '형'은 어느 인물을 가리키나? | S+C | S의 관계와 C의 도움 요청. C 하나로 이름 단정하지 않음 |
| Q10 | 별칭: '동생'으로 해석할 인물의 가족이 쫓겨난 장면은? | S | 형제·놀부 축출에 근거한 흥부. 원문에 없는 별칭임을 표시 |
| Q11 | 관계: 누가 누구의 가족을 집에서 내쫓았나? | S | 놀부 → 흥부 가족 |
| Q12 | 관계: 흥부의 도움 요청을 거절한 사람과 두 사람 관계는? | S+C | 놀부/형제 근거를 함께 회수 |
| Q13 | 사건 순서: 치료와 박씨를 심는 일 중 무엇이 먼저인가? | K | 치료 → 이듬해 박씨 → 심음 |
| Q14 | 사건 순서: 축출과 형에게 도움 요청을 연결하는 두 장면은? | S+C | 두 근거 필요. 상세 날짜·간격은 없음 |
| Q15 | 인과 경계: 박씨를 얻은 이유가 제비 치료의 보답이라고 명시돼 있나? | K | 치료 후 박씨는 확인. annotation만으로 제비의 의도·감사 인과를 확정하지 않음 |
| Q16 | 문맥: 가족이 배척당한 뒤 생계를 버티는 이야기의 근거는? | S+C | 축출·품팔이·거절·가난. 다른 작품 사건 혼합 금지 |
| Q17 | 자료 없음: 제비 다리에 바른 약 이름은? | 없음 | annotation에 약 이름 없음. 추정 보류 |
| Q18 | 자료 없음: 흥부가 박씨를 심은 정확한 연월일은? | 없음 | 이듬해라는 상대 표현뿐. 날짜 생성 금지 |

Q09/Q12/Q14/Q16은 관계/다중 근거 질문이지만 작은 동일 Pack 내 두 Beat 회수로 충분할 수 있다. 이 실패만으로 graph DB가 필요하다고 결론내리지 않는다. Q15는 “인과 추론 성공”보다 자료로 말할 수 있는 경계를 평가한다.

## 실행 경로와 입력 통제 — 후속 실험 제안

현재 API는 일반 검색 질문 문자열 하나를 받는 검색 endpoint가 아니다. `build_result`의 engine 조건과 legacy story/context 경로가 별개다. 자연어 문항을 그대로 /api/generate에 넣고 질문 응답 정확도를 평가했다고 보고하면 안 된다.

검색만 비교할 후속 평가 harness는 다음 계약을 따른다(이번에 생성하지 않음).

1. B 평가에서는 `_fallback_data()`의 BEATS와 그 데이터로 계산한 IDF를 격리한 프로세스에서 사용한다. A에서는 기존 TEAM_DB를 그대로 사용하고 source/통계를 기록한다.
2. 각 질문 q를 `dna={setting:[q], characters:[], emotion:[], conflict:[], beats:[]}`, context={}, personal_context={}로 고정한다. `dna.keywords`만 채우면 query에 들어가지 않는 구현을 주의한다. 이는 모델 해석 없는 **검색 진단용 adapter 제안**이다.
3. `_rank_retrieval_records`의 원시 top-k와 `select_story_pack`, `retrieve_modules`의 반환을 각각 저장한다. Beat 다양성 정렬을 raw MRR로 오인하지 않는다.
4. 기준선의 ID·점수·matched_terms를 먼저 파일로 저장하고, 기대 근거를 잠근 뒤 후보를 측정한다. 새 사전/필터를 결과를 보고 gold에 맞추지 않는다.
5. 별도 생성 실험은 동일 engine/context/beat_overrides·동일 검색 snapshot·동일 provider/model 설정을 사용한다. 검색은 고정하고 생성만 비교하는 실험도 분리한다. 실제 Live 생성은 비용·개인 입력 전송 범위를 정한 뒤 승인받아 수행한다.

생성 경로는 키가 있으면 OpenAI를 호출할 수 있다. 함수 import만으로는 생성하지 않지만 `build_result`·기존 test_mvp2·smoke 실행은 환경에 따라 호출될 수 있으므로 키·Ollama 설정을 차단한 격리 환경이 필요하다. 일부 테스트는 팀 DB의 충분한 후보 수를 전제하므로 4개 fallback으로 같은 결과를 기대하지 않는다.

## 지표 선택과 분모

| 지표 | 계산·용도 |
|---|---|
| Beat Recall@1/@3 | relevant module ID 중 top-k에 포함된 비율. 여러 근거 문항은 전체 근거 회수율도 별도 |
| MRR@3 | 첫 관련 Beat의 reciprocal rank. 두 근거가 모두 필요한 질문의 완료를 뜻하지 않음 |
| All-evidence@3 | gold가 2개인 질문에서 둘 다 회수한 비율 |
| Precision@3 / 관련성 | 정답 근거·배경 관련·무관의 2/1/0 사전 라벨. 평가자 검토 후 확정 |
| 올바른 보류율 | Q17/Q18에서 근거 없음 판단 비율. 현재 검색은 무관 후보도 반환하므로 **보류 기능은 미구현 기준선** |
| 근거 일치율 / 오답률 | 검색 후보가 아니라 주장 단위의 source·주어·시점·단위 대조. 검색 지표와 분리 |
| 설정 위반률 | [일관성 규칙](STORY_CONSISTENCY_RULES.md)의 적용 가능한 규칙 중 위반 수 |
| latency | 동일 장비에서 raw retrieval·pack 선택·생성을 별도 측정. cold load와 warm 검색 분리 |

자료 없음 문항의 Recall/MRR는 N/A다. 관련 후보가 없다고 임의로 1점을 주지 않는다. 보류 출력이 없는 현재 검색에서는 “후보 반환”과 “자료에 답이 있음”을 분리해 수동 판독한다.

## 기준선·변경 후 기록 형식

| run / case | commit·data hash·source | query/입력 | gold ID | raw top3 ID·score·terms | Pack·최종 반환 | Recall/MRR/All-evidence | 보류·근거·설정 위반 | 검색/생성 ms | 판독 |
|---|---|---|---|---|---|---|---|---|---|
| baseline / Q01~18 | 실행 전 고정 | 동일 입력 | 위 표 | **미측정** | 미측정 | 미측정 | 미측정 | 미측정 | 원본 report 경로 |
| candidate / 동일 문항 | 후보 commit, 같은 자료 | 동일 입력 | 변경 금지 | 미측정 | 미측정 | 미측정 | 미측정 | 미측정 | 개선/회귀 사례 |

이 Markdown은 기록 양식이지 새 결과 데이터 파일이 아니다. 재평가는 tokenizer·동의어·가중치·source 데이터·Beat 정규화·prompt/provider가 바뀔 때 해당 질문 subset과 정확 일치 회귀 subset으로 수행한다.

## 다음 실험 하나

B의 18문항 raw 기준선을 저장해 어휘 실패와 두 근거 회수 실패를 분류한다. 이후 A DB에서 실제 제주 Story Pack ID와 원문을 확보한 gold를 추가한 뒤 동의어 정규화와 비교한다. 단일 Pack 결과만으로 embedding/ontology/GraphRAG 채택을 결정하지 않는다.


## 실제 구현·실행 기록 (2026-10-20)

`evaluation/retrieval.py`는 기존 검색 함수에 위 진단 adapter를 적용한다. corpus와 gold ID·본문 근거를 검사하고 자료/질문/app/평가기의 SHA-256, 원시 top3와 Pack·최종 선택, 분모가 다른 지표를 JSON에 남긴다. 기존 결과 파일을 덮어쓰지 않으며 후보 실험은 동일 자료·gold·코드의 baseline을 먼저 요구한다. 후보는 평가기 내부의 제한된 동의어 확장이며 앱 기본 검색은 바꾸지 않았다.

```bash
python evaluation/retrieval.py --output /tmp/fallback-baseline.json
python evaluation/retrieval.py --variant synonyms --baseline /tmp/fallback-baseline.json --output /tmp/fallback-synonyms.json
python evaluation/retrieval.py --source team --cases evaluation/team_cases.json --output /tmp/team-baseline.json
python evaluation/retrieval.py --source team --cases evaluation/team_cases.json --variant synonyms --baseline /tmp/team-baseline.json --output /tmp/team-synonyms.json
```

새 출력 경로로 실행한다. import 시 팀 metadata를 읽지만 생성 함수는 호출하지 않는다. 보고서는 [evaluation/results](../evaluation/results/)에 보존했다. 최초 보고서의 app/평가기 해시는 해당 실행 당시 버전이며 이후 Remix 수정과 평가기 hash guard 추가를 현재 실행과 혼동하지 않는다.

| 데이터·개발용 질문 | Recall@1 | Recall@3 | MRR@3 | All-evidence@3 |
|---|---:|---:|---:|---:|
| fallback 기준선 — 16 answerable + 2 자료 없음 | 0.59375 | 0.84375 | 0.77083 | 0.75000 |
| 같은 fallback·동의어 후보 | 0.81250 | 0.96875 | 0.93750 | 0.93750 |
| 팀 DB 기준선 — 15 answerable + 3 자료 없음 | 0.63333 | 0.76667 | 0.78889 | 0.66667 |
| 같은 팀 DB·동의어 후보 | 0.63333 | 0.76667 | 0.78889 | 0.66667 |

실제 로드 수는 246 Story·1,264 Beat·1,431 Module·246 plot pattern이다. 팀 gold는 F_001~F_005의 저장 event_text를 먼저 읽고 정의한 개발용 18문항이다. 독립 사람 검토·holdout이 아니며 원전의 역사적 사실성도 검증하지 않았다. 전체 제주 설화 성능으로 일반화하지 않는다. 두 자료의 지표를 합산하지 않는다.

후보는 fallback Q10/Q14/Q16의 Recall@3를 높였고 회귀 문항은 없었으나 팀 질문에서는 개선이 없었다. **기본 검색에 채택하지 않는다.** GraphRAG/벡터 DB 도입도 정당화되지 않는다. 어휘·조사 차이와 다중 근거 누락을 추가 gold에서 분리할 필요가 있다.

자료 없음 질문은 검색 후보가 반환돼도 사실 답변으로 처리하지 않는다. 현재 QA 보류 계약이 없어 abstention은 null/N/A로 기록했다. 생성문·근거 주장·의미 일관성 평가도 미실행으로 분리했다. Live LLM 호출은 0회다. `.github/workflows/ci.yml`은 unittest와 동일 질문의 raw 기준선을 매번 실행하고 보고서를 7일 보관한다. CI가 실행된 사실·결과는 해당 commit Actions에서 별도 확인한다.
