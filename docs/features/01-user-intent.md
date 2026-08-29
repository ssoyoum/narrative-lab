# 01. User Intent 입력

## 목적

사용자가 자유로운 장문 프롬프트를 작성하지 않아도 만들고 싶은 제주 설화의 방향을 구조화한다.

## 입력 항목

| 필드 | 예시 |
|---|---|
| `atmosphere` | `mysterious`, `tense`, `warm` |
| `theme` | `loss_recovery`, `forbidden_promise` |
| `location` | `sea`, `oreum`, `cave` |
| `character` | `traveler`, `haenyeo`, `outsider` |
| `ending` | `warm`, `reversal`, `open`, `echo` |

각 항목은 한 화면씩 진행하는 Wizard UI에서 선택한다. `랜덤 설화 설계`를 누르면 각 항목이 임의로 선택된다.

## 처리 흐름

```text
radio 선택
  → collectEngine()
  → POST /api/generate
  → engine payload
```

## API 예시

```json
{
  "engine": {
    "atmosphere": "mysterious",
    "theme": "forbidden_promise",
    "location": "cave",
    "character": "outsider",
    "ending": "echo"
  },
  "context": {}
}
```

## 현재 한계

- 선택지는 현재 제주 설화 MVP에 맞춰 고정되어 있다.
- 자연어 의도 해석이나 사용자 정의 주제 입력은 아직 지원하지 않는다.
- 입력 조건은 심리 진단이 아니라 창작 의도다.
