# Module Structure

## Repository Structure

```bash
narrative-lab/
├── app.py
├── index.html
├── script.js
├── styles.css
├── data/
│   └── story_modules.json
├── team-data/
│   └── jeju-stories/chroma_db/chroma.sqlite3
├── tests/
│   ├── test_mvp1_1.py
│   ├── test_mvp1_3.py
│   └── test_mvp2.py
└── docs/
    ├── ARCHITECTURE.md
    ├── architecture/
    └── features/
```

## Responsibility Map

| File / 영역 | 책임 |
|---|---|
| `app.py` Data Loader | SQLite collections를 읽고 Beat records로 정규화 |
| `app.py` Retrieval | token overlap, IDF, raw score 계산 |
| `app.py` DNA Builder | User Intent를 Generative DNA로 변환 |
| `app.py` Blueprint | 주인공·목표·갈등·세계·Beat Plan 구성 |
| `app.py` Binding | Beat별 원천 사건과 DNA focus 연결 |
| `app.py` Remix | `beat_overrides`를 적용해 사건 교체 |
| `app.py` Generator | Bound Beat와 DNA를 문장으로 결합 |
| `index.html` | 입력·결과 화면의 구조 |
| `script.js` | API 호출·결과 렌더링·후보 클릭 처리 |
| `styles.css` | 다크 결과 패널·Match Report·Remix UI |
| `tests/` | API contract와 Remix 흐름 검증 |

## API Entry Point

```text
POST /api/generate
  → build_result()
  → build_engine_result()
```

기존 MVP1의 자유 TXT 입력 경로도 하위 호환을 위해 유지한다.
