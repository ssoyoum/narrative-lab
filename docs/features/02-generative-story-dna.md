# 02. Generative Story DNA

## 목적

사용자의 선택 조건을 단순 태그가 아니라 새 이야기의 인과 구조로 변환한다.

## 핵심 필드

```json
{
  "the_question": "약속을 지키기 위해 어디까지 감수할 수 있는가?",
  "the_lack": "주인공은 자신이 한 약속의 의미를 끝까지 이해하지 못한다.",
  "the_cost": "약속을 지키려면 가장 안전한 길과 익숙한 관계를 포기해야 한다.",
  "the_irony": "약속이 자신을 묶은 것이 아니라 구했다는 것을 알게 된다."
}
```

구조는 다음과 같이 연결된다.

```text
The Question
  ↓
The Lack
  ↓
The Cost
  ↓
The Irony
```

## 구현 방식

현재는 외부 LLM 없이 `ENGINE_THEMES`, `ENGINE_ATMOSPHERES`, `ENGINE_LOCATIONS`, `ENGINE_CHARACTERS`, `ENGINE_ENDINGS` 규칙 테이블로 생성한다.

`user_intent`에는 사용자가 선택한 분위기·주제·장소·인물·결말을 함께 반환한다. 후보 설화를 바꾸어도 같은 요청 안에서는 Generative DNA가 유지된다.

## Beat 연결

| Beat | 담당 DNA |
|---|---|
| Ki | `the_lack` |
| Shō | `the_question` |
| Trial | `the_cost` |
| Crisis | `the_irony` |
| Climax | `the_question` |
| Ketsu | `the_irony` |

## 현재 한계

- DNA 문장이 주제별 템플릿에 기반한다.
- 후보 설화의 사건이 DNA 의미를 실제로 반영하는지는 아직 별도 Validation 단계다.
