# 05. Beat DNA Binding

## 목적

각 Beat를 단순히 검색 결과로 채우지 않고, Generative Story DNA를 증명해야 하는 서사 단계로 정의한다.

## 바인딩 규칙

```python
BEAT_DNA_BINDINGS = {
    "Ki": ("setup", "the_lack"),
    "Shō": ("transition", "the_question"),
    "Trial": ("conflict", "the_cost"),
    "Crisis": ("conflict", "the_irony"),
    "Climax": ("climax", "the_question"),
    "Ketsu": ("resolution", "the_irony"),
}
```

## 처리

1. 중심 Story Pack 또는 사용자가 선택한 후보에서 사건을 찾는다.
2. 사건을 Beat에 연결한다.
3. 해당 Beat가 담당하는 `dna_focus`와 `dna_value`를 저장한다.
4. 생성기가 Beat 순서대로 사건을 사용한다.

## 결과 예시

```json
{
  "beat": "Shō",
  "dna_focus": "the_question",
  "dna_value": "약속을 지키기 위해 어디까지 감수할 수 있는가?",
  "source_story": "뱀굴",
  "event_text": "거북을 잡으려 하나 거북이 말을 함"
}
```

## 현재 한계

현재는 DNA 문장과 사건을 연결해 표시하지만, 사건의 의미가 DNA를 충분히 증명하는지는 다음 `DNA Validation` 단계에서 자동 평가해야 한다.
