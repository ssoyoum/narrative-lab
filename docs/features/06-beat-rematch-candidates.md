# 06. Beat별 재매칭 후보

## 목적

중심 Story Pack 외에도 각 Beat에 더 잘 맞을 수 있는 다른 설화를 탐색할 수 있게 한다.

## 동작

각 Beat마다 canonical Beat가 같은 record를 검색하고, 같은 설화가 반복되지 않도록 source story 기준으로 최대 3개 후보를 반환한다.

```text
Ki       → 설화 A / 설화 B / 설화 C
Shō      → 설화 A / 설화 D / 설화 E
Trial    → 설화 B / 설화 F / 설화 G
```

## 후보 카드 정보

- 원천 설화 제목
- 사건 텍스트
- 상대 적합도
- raw retrieval score
- matched terms
- 현재 중심 Pack인지 여부
- `이 후보 적용 ↗` 버튼

## 기본 후보와 실제 적용의 차이

후보 목록을 보는 것만으로 생성 결과가 바뀌지는 않는다. 후보 카드를 클릭해야 `beat_overrides`가 API에 전달되고 실제 Bound Beat가 교체된다.

## 현재 한계

- 후보의 적합도는 lexical score 중심이다.
- 후보 간 의미적 차이와 인과 호환성은 자동 판정하지 않는다.
