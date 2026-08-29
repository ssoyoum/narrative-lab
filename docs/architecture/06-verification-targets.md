# Verification Targets

## Automated Tests

```bash
python -m unittest discover -s tests -v
```

## Test Areas

| 영역 | 검증 질문 |
|---|---|
| Intent | 선택 조건이 API payload로 전달되는가? |
| Generative DNA | Question·Lack·Cost·Irony가 생성되는가? |
| Beat Binding | Shō가 `the_question`에 연결되는가? |
| Story Pack | 기본 생성에서 중심 원천이 일관적인가? |
| Match Report | 점수와 데이터 통계가 반환되는가? |
| Candidate Retrieval | Beat마다 독립 후보가 반환되는가? |
| Remix | `beat_overrides`가 실제 Bound Beat를 교체하는가? |
| Active Modules | Remix 후 하단 모듈이 선택된 사건을 보여주는가? |
| Generation | Remix 모드가 `Cross-Story Remix`로 표시되는가? |

## Manual Review Checklist

1. `python app.py`로 서버 실행
2. User Intent 5개 선택
3. 결과에서 `MATCH REPORT` 확인
4. `BEAT별 재매칭 후보`의 `이 후보 적용 ↗` 클릭
5. `ACTIVE REMIX MODULES`로 섹션 제목이 바뀌는지 확인
6. `ACTIVE REMIX`에 교체 Beat 수가 반영되는지 확인
7. 생성 제목에 `Cross-Story Remix`가 표시되는지 확인
8. 생성문에 선택한 사건이 포함되는지 확인

## Not Yet a Production SLA

이 프로젝트는 현재 로컬 MVP이므로 운영 SLA, uptime, p95 latency, multi-user concurrency 수치는 측정·제시하지 않는다. 다음 단계에서 실제 사용 로그를 수집한 뒤 목표와 현재값을 분리해 기록한다.
