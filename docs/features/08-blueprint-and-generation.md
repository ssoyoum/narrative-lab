# 08. Narrative Blueprint와 생성

## 목적

Generative DNA와 Bound Beat를 실제 이야기의 설계도와 문장으로 변환한다.

## Blueprint 필드

```text
Protagonist
Goal
Conflict
World
Question
Lack
Cost
Irony
Beat Plan
```

각 Beat Plan은 사건의 기능을 정의한다.

```text
Ki: 결핍과 세계의 규칙
Shō: 핵심 질문의 발생
Trial: 대가의 증가
Crisis: 아이러니의 노출
Climax: 질문에 대한 선택
Ketsu: 선택의 결과
```

## 생성 방식

현재는 `generate_blueprint_story()`가 DNA 문장과 각 Beat의 `event_text`를 순서대로 결합하는 규칙 기반 draft generator다.

```text
Lack + Ki event
Question + Shō event
Cost + Trial event
Irony + Crisis event
Question에 대한 선택 + Climax/Ketsu event
```

## 생성 모드

- `generative story DNA + bound beats`: 중심 Story Pack 기본 생성
- `cross-story remix + generative story DNA`: 하나 이상의 Beat override가 적용된 생성

## 현재 한계

- 사건 문장을 새 문체로 변환하지 않고 원문 요약을 삽입한다.
- 일부 사건은 선택한 인물·장소와 의미적으로 충돌할 수 있다.
- 다음 단계는 사건 변환, 문장 연결, DNA Validation이다.
