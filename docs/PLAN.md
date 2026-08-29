# Narrative Lab MVP Plan

## 프로젝트 목표

제주 설화 데이터의 검색용 Story Metadata를 이용해 생성용 Story DNA를 설계하고, 이를 Beat 제약으로 사용해 설명 가능한 새로운 이야기를 생성한다.

## 사용자의 핵심 흐름

```text
분위기·주제·장소·인물·결말 선택
  → Generative Story DNA 확인
  → 중심 Story Pack 및 Match Report 확인
  → Beat별 후보 선택
  → Cross-Story Remix 재생성
  → Blueprint·Active Remix Modules·Narrative 확인
```

## 현재 MVP 범위

- Python 로컬 서버와 브라우저 UI
- 팀 제주 설화 SQLite 데이터 사용
- 246개 설화, 1,264개 Beat, 1,431개 모듈 로드
- Generative Story DNA: Question·Lack·Cost·Irony
- Narrative Blueprint와 Beat DNA Binding
- TF-IDF 기반 Story Pack 검색
- Match Report와 Beat별 재매칭 후보
- `beat_overrides` 기반 Cross-Story Remix
- 규칙 기반 Narrative Draft 생성

## 이번 버전에서 하지 않을 것

- 새로운 데이터팩 추가
- 외부 유료 LLM API 연결
- 프론트엔드 프레임워크 전환
- 사용자 로그인·저장·공유 기능
- 대규모 리팩터링
- 자동 DNA Validation 고도화

## MVP 완료 조건

1. `python app.py`로 서버가 실행된다.
2. 사용자가 5개 조건을 선택해 결과를 생성할 수 있다.
3. Match Report와 Beat 후보가 표시된다.
4. 후보를 선택하면 `beat_overrides`가 적용된 Remix 결과가 생성된다.
5. 기본 모듈과 Active Remix Modules가 구분된다.
6. 기존 테스트와 핵심 API smoke test가 통과한다.
