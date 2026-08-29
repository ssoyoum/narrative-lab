# Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| UI | HTML5 | Wizard와 결과 영역 구조 |
| Styling | CSS3 | 반응형 레이아웃과 결과 시각화 |
| Client Logic | Vanilla JavaScript | API 호출과 Remix 상호작용 |
| Backend | Python 3.10+ | 로컬 HTTP 서버와 Engine orchestration |
| Data | SQLite / Chroma export | 팀 제주 설화 데이터 저장 |
| Retrieval | TF-IDF-style lexical baseline | 설명 가능한 metadata 검색 |
| Testing | Python `unittest` | MVP contract 검증 |
| Optional AI | Ollama | 선택적 로컬 자연어 변환 |
| Runtime | Local process | `python app.py` |

## Why This Stack

- 외부 API 없이 실행할 수 있다.
- 별도 프론트엔드 빌드 도구가 없어 구조가 단순하다.
- 검색 점수와 생성 규칙을 코드로 추적할 수 있다.
- 팀 프로젝트 데이터를 개인 Narrative Engine에서 재사용할 수 있다.

## Runtime Command

```bash
python app.py
```

기본 포트는 `8000`이며, 충돌을 피하려면 다음처럼 지정할 수 있다.

```powershell
$env:NARRATIVE_PORT = "8133"
python app.py
```
