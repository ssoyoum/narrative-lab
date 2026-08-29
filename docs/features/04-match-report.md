# 04. Match Report

## 목적

생성된 이야기뿐 아니라 “왜 이 원천 설화와 사건이 선택됐는가”를 사용자에게 설명한다.

## 기본 모드 지표

| 지표 | 의미 |
|---|---|
| Story Pack 적합도 | 전체 후보 중 중심 설화의 상대 순위 |
| Beat 구조 커버리지 | setup·transition·conflict·climax·resolution 확보 비율 |
| DNA 바인딩률 | DNA 역할이 실제 사건에 연결된 비율 |
| 원천 일관성 | 하나의 Story Pack에서 모듈을 선택했는지 |

## Remix 모드 지표

리믹스에서는 여러 원천을 섞는 것이 의도이므로 `원천 일관성`을 감점하지 않는다.

| 지표 | 의미 |
|---|---|
| 기준 Story Pack 커버리지 | 리믹스 전 중심 Pack의 구조 커버리지 |
| 리믹스 적용 범위 | 6개 Beat 중 사용자가 교체한 Beat 수 |
| DNA 바인딩률 | 생성용 DNA 역할과 사건의 연결 비율 |

혼합된 원천 설화 수는 품질 감점이 아니라 Remix 결과를 설명하는 통계로 표시한다.

## API 응답 예시

```json
{
  "mode": "cross-story remix",
  "statistics": {
    "remix_beats": 3,
    "remix_sources": 3
  },
  "dimensions": [
    {
      "key": "remix_coverage",
      "score": 50,
      "detail": "3 / 6개 Beat를 후보 설화로 교체"
    }
  ]
}
```

## 주의

100%는 전체 문학적 품질이 아니라 후보군 내부의 상대 점수다. 동점이면 여러 후보가 100%가 될 수 있으므로 raw score와 matched terms를 함께 확인해야 한다.
