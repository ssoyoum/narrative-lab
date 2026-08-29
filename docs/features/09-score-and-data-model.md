# 09. 점수와 데이터 모델

## 데이터 모델

```text
Story Catalog
  ├─ story_id
  ├─ title
  ├─ category
  └─ stored narrative metadata

Story Beat
  ├─ beat_id
  ├─ source_story_id
  ├─ raw_beat
  ├─ canonical beat
  └─ event_text

Module
  ├─ character
  ├─ place
  ├─ event
  ├─ mood
  └─ wisdom
```

## Raw retrieval score

모듈 카드의 `7.1` 같은 값은 퍼센트가 아니다. 검색 query와 record의 overlap에 IDF 가중치를 적용한 원시 점수다.

예시:

```text
matched terms: 5.1
setting match: 2.0
raw score: 7.1
```

점수 구성요소는 카드의 `점수 구성`에서 확인한다.

## 상대 적합도

후보 카드의 `100%`는 같은 Beat 후보군에서 가장 높은 raw score를 100으로 환산한 값이다.

따라서:

- 동점 후보가 여러 개면 여러 카드가 100%일 수 있다.
- 100%는 문학적 품질이나 정답을 의미하지 않는다.
- raw score와 matched terms를 함께 확인해야 한다.

## 동점 처리

서버의 안정적인 선택 기준은 다음과 같다.

```text
aggregate score
→ Beat coverage
→ matched term count
→ stable story id
```

## 포트폴리오에서의 의미

이 점수 시스템의 목적은 “좋은 설화”를 판정하는 것이 아니라, 검색·선택·재조합 과정을 설명 가능하게 만드는 것이다.
