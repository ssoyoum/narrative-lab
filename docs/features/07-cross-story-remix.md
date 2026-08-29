# 07. Cross-Story Remix

## 목적

사용자가 Beat 후보를 직접 선택해 서로 다른 제주 설화의 사건을 하나의 새 이야기 구조에 재배치한다.

## 사용자 흐름

```text
후보 카드 클릭
  ↓
beat_overrides에 Beat와 module_id 저장
  ↓
기존 선택 조건과 Generative DNA 유지
  ↓
선택된 사건만 Bound Beat 교체
  ↓
Cross-Story Remix 재생성
```

## API 입력

```json
{
  "engine": {
    "atmosphere": "mysterious",
    "theme": "forbidden_promise",
    "location": "cave",
    "character": "traveler",
    "ending": "echo"
  },
  "context": {},
  "beat_overrides": {
    "Ki": "L_050_Ki",
    "Shō": "L_166_Shō"
  }
}
```

## 결과 표시

리믹스가 활성화되면 다음이 바뀐다.

- 생성 제목: `Cross-Story Remix`
- Match Report: `리믹스 적용 범위`
- Blueprint: `ACTIVE REMIX`
- 모듈 섹션: `ACTIVE REMIX MODULES`
- 실제 선택된 Beat의 source story와 event text

기존에 선택한 Beat는 다음 후보를 클릭해도 유지된다. 따라서 여러 Beat를 순차적으로 바꿀 수 있다.

## 현재 한계

- 여러 사건을 섞은 뒤 문장 간 연결을 자연스럽게 변환하는 LLM 단계는 아직 baseline이다.
- DNA Validation이 아직 없어 어색한 조합도 생성될 수 있다.
