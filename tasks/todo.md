# Narrative Lab Tasks

## 현재 되는 것

- [x] User Intent Wizard
- [x] Generative Story DNA 생성
- [x] Narrative Blueprint 생성
- [x] Story Pack retrieval과 중심 원천 선택
- [x] Match Report
- [x] Beat별 재매칭 후보
- [x] `beat_overrides` 기반 Cross-Story Remix API
- [x] Active Remix Modules 응답
- [x] 규칙 기반 Narrative Draft 생성
- [x] MVP1 하위 호환 테스트

## 현재 안 되는 것

- [x] 실제 브라우저 클릭 자동 검증 — scripts/browser_smoke.cjs, 키 없는 Chromium 생성·Cross-Story 후보 클릭 통과
- [ ] 생성문에 대한 자동 DNA Validation
- [ ] 원천 사건을 자연스러운 새 문장으로 변환
- [ ] Remix 결과 저장·공유

## 현재 blocker

### 핵심 흐름의 실행 검증 부족 — 해결됨

`scripts/smoke_test.py`로 홈페이지·기본 생성·후보·Remix API·Active Remix Modules 응답을 검증하고, `scripts/browser_smoke.cjs`로 Chromium 실제 후보 클릭까지 확인했다. 생성 본문 의미 검증은 별도 미완료 작업이다.

## 다음 작업 1~3개

1. [x] 로컬 서버 실행과 `/api/generate` 기본·Remix 요청을 검증하는 smoke test 추가
2. [x] Chromium에서 후보 클릭 후 API 적용 ID·active_modules·선택 카드 갱신 검증 구현
3. [ ] E2E 확인 후 DNA Validation 설계

## 완료된 작업

- [x] 기능별 문서 작성
- [x] 아키텍처 문서 작성
- [x] Match Report와 점수 breakdown 추가
- [x] Cross-Story Remix 후보 선택 구현
- [x] 기본 Pack과 Active Remix Modules 분리
- [x] 원본 Beat 문장을 제외한 구조 추상화와 narrative pattern 생성
- [x] OpenAI Responses API 기반 신규 설화 생성 및 API key 미설정 fallback
- [x] Generated Folktale / Generation Mode / Based on UI 표시

## 지금 하지 않을 것

- 새로운 기능 확장
- 데이터셋 확장
- 새 라이브러리 도입
- UI 전면 재설계

## 2026-10-20 문서 분석 작업

- [x] 현재 검색 점수·SQLite metadata 로딩·생성 연결을 코드와 대조해 기존 검색/데이터 모델 문서 보완
- [x] 흥부전 fallback 근거를 명시한 검색 평가 18문항 및 이야기 일관성 규칙 설계
- [x] 선택적 OpenAI 생성 경로와 초기 무료 baseline 설명 구분
- [x] 동일 데이터·질문으로 raw 검색 기준선 저장 및 동의어 개선 비교 — fallback/팀 DB 각 18문항, evaluation/results. 팀 질문 개선 없어 기본 검색 미채택
- [x] 팀 SQLite 246 Story/1,264 Beat 조회 및 개발 gold 18문항 고정 — 독립 사람 검토 미완료
- [ ] 생성 본문 자동 DNA Validation — **미구현**, 규칙/판독 설계만 완료

이 작업은 Markdown 변경만 수행했다. 테스트·API smoke·브라우저·Live 생성 결과를 새로 얻지 않았다. 기존 E2E 우선순위와 완료된 기능 표시를 변경하지 않는다.



## 2026-10-20 실행 검증 보완

- [x] 무료·오프라인 unittest 27개 통과 (기존 21 + 평가 지표/근거 3 + Remix 계약 3)
- [x] Remix의 기본 Pack에 없는 Beat 보충과 잘못된 ID/Beat 요청 거절 구현
- [x] unittest·고정 검색 질문을 실행하는 GitHub Actions 추가
- [ ] 인물·시간·인과를 판독하는 의미 validator와 독립 gold 검토 — 단순 바인딩 검사를 완료로 세지 않음

위 최초 문서 작업의 미실행 기록 이후 수행한 결과다. Live 생성·DB 변경·검색 알고리즘 변경은 하지 않았다.

- [x] Chromium 실제 클릭: 랜덤 설계 → 중심 Pack 밖 후보 → API 적용 ID와 선택 카드 확인 (L_076_Ki). CI browser job에도 같은 검사 추가. 외부 모델 비활성 확인 후에만 실행한다.

## 2026-10-21 선택적 모델 응답 오류 처리

- [x] 잘못된 provider JSON 구조·불완전 응답·제목만 있는 출력을 기존 baseline fallback으로 처리
- [x] 정상 중첩 assistant 응답/기존 output_text 호환 및 오류 상세 미노출 검사
- [x] 변경 전 회귀 재현 후 전체 unittest 31개 통과, 고정 검색 질문 36개 지표 유지 — 실제 모델 호출 없음
- [ ] 생성 본문 자동 DNA Validation — 응답 형식 검증을 의미 검증 완료로 세지 않음

- [x] 같은 변경에서 키 없는 API smoke와 Chromium 실제 Cross-Story 후보 클릭 재검증 통과 (Ki/L_076_Ki), 서버 종료 확인
