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

- [ ] 실제 브라우저 클릭을 자동 검증하는 E2E 테스트
- [ ] 생성문에 대한 자동 DNA Validation
- [ ] 원천 사건을 자연스러운 새 문장으로 변환
- [ ] Remix 결과 저장·공유

## 현재 blocker

### 핵심 흐름의 실행 검증 부족 — 해결됨

백엔드 단위 테스트만으로는 전체 흐름을 재현할 수 없었으나, `scripts/smoke_test.py`를 추가해 홈페이지·기본 생성·후보·Remix API·Active Remix Modules 응답을 한 번에 검증할 수 있게 했다. 브라우저 실제 클릭 검증은 아직 남아 있다.

## 다음 작업 1~3개

1. [x] 로컬 서버 실행과 `/api/generate` 기본·Remix 요청을 검증하는 smoke test 추가
2. [ ] 브라우저에서 후보 클릭 후 결과 갱신을 확인하는 최소 E2E 검증 방법 결정
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
- [ ] 동일 데이터·질문으로 raw 검색 기준선 저장 및 동의어 개선 비교 — **미실행**
- [ ] 팀 SQLite의 실제 Pack/Beat gold 확정 — 이번 환경에서는 DB 내부 미조회
- [ ] 생성 본문 자동 DNA Validation — **미구현**, 규칙/판독 설계만 완료

이 작업은 Markdown 변경만 수행했다. 테스트·API smoke·브라우저·Live 생성 결과를 새로 얻지 않았다. 기존 E2E 우선순위와 완료된 기능 표시를 변경하지 않는다.


