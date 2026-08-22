# 제주 설화 데이터 분류 체계

## 분류 기준

수집된 자료를 **콘텐츠 유형**에 따라 2가지로 분류:

### 1. 설화 콘텐츠 (stories/)
실제 설화 내용, 줄거리, 원문을 포함한 자료

**판별 기준:**
- 설화의 줄거리/스토리가 있음
- 등장인물의 행동, 대화가 있음
- 시작-전개-결말 구조가 있음

### 2. 메타/분석 자료 (meta/)
설화에 대한 분류, 구조, 학술적 분석 자료

**판별 기준:**
- 설화 자체보다 설화의 "분류 체계"를 설명
- 학술적 정의, 의의, 특징 분석
- 콘텐츠 없이 구조만 나열

---

## 현재 자료 분류 결과

### PDF 자료 (jeju_myths/)

| 분류 | 접두어 | 내용 | 개수 |
|------|--------|------|------|
| **C_** | Content | 설화 해설/요약 (표준어) | ~249 |
| **T_** | Text | 원문 구술 채록 (제주어) | ~269 |

**매칭 관계:**
- `C_M_xxx` ↔ `T_M_xxx` (신화)
- `C_F_xxx` ↔ `T_F_xxx` (민담)
- `C_L_xxx` ↔ `T_L_xxx` (전설)

### 웹 크롤링 자료 (web-crawled/)

| 파일 | 유형 | 분류 | 이유 |
|------|------|------|------|
| grandculture/seolmundae.md | 설화 콘텐츠 | **stories/** | 지형창조, 옷감설화, 죽음 등 줄거리 포함 |
| grandculture/bonpuri.md | 메타/분석 | **meta/** | 본풀이 분류 체계만 설명, 개별 스토리 없음 |
| namuwiki/seolmundae.md | 설화 콘텐츠 | **stories/** | 지형창조, 미완성된 다리, 일제강점기 일화 등 |
| encykorea/seolmundae.md | 설화 콘텐츠 | **stories/** | 지형창조, 죽음 등 줄거리 포함 |
| encykorea/cheonjiwang.md | 설화 콘텐츠 | **stories/** | 창세신화 전체 줄거리 포함 |
| encykorea/yeongsilgiam.md | 혼합 | **stories/** | 오백장군 설화 줄거리 포함 |

---

## 저장 구조

```
team-data/jeju-stories/
├── sources/                    # 원본 소스
│   ├── pdf-downloads/          # 다운로드된 PDF
│   └── web-crawled/            # 크롤링된 마크다운
│
└── cleaned/                    # 클린징된 데이터
    ├── stories/                # 설화 콘텐츠
    │   ├── myths/              # 신화 (본풀이 등)
    │   ├── legends/            # 전설 (지명유래 등)
    │   └── folktales/          # 민담
    │
    └── meta/                   # 메타/분석 자료
        ├── classification/     # 분류 체계
        ├── analysis/           # 학술 분석
        └── references/         # 참고문헌 목록
```

---

## 설화 콘텐츠 JSON 스키마

```json
{
  "id": "story_001",
  "title": "설문대할망",
  "title_alt": ["선문대할망", "세명주할망"],
  "type": "myth",                    // myth, legend, folktale
  "category": "창조신화",

  "content": {
    "summary": "제주도를 창조한 거인 여신 이야기",
    "full_text": "옛날 옛적에...",    // 해설 버전 (C_)
    "original_text": "경 허난...",    // 원문 제주어 (T_)
    "narrator": {                     // T_ 파일에서 추출
      "name": "성계천",
      "gender": "남",
      "age": 83
    }
  },

  "elements": {
    "characters": ["설문대할망", "오백장군"],
    "locations": ["한라산", "백록담", "산방산"],
    "keywords": ["창조", "거인", "지형"]
  },

  "sources": [
    {
      "type": "pdf",
      "file": "C_M_xxx.pdf",
      "reference": "현용준, 『제주도무가』, 1996"
    }
  ],

  "metadata": {
    "created_at": "2024-12-03",
    "source_ids": ["C_M_001", "T_M_001"]
  }
}
```

---

## 메타/분석 자료 JSON 스키마

```json
{
  "id": "meta_001",
  "title": "본풀이 분류 체계",
  "type": "classification",

  "content": {
    "definition": "본풀이란...",
    "categories": [
      {
        "name": "일반신 본풀이",
        "items": ["천지왕본풀이", "삼승할망본풀이"]
      }
    ]
  },

  "related_stories": ["story_001", "story_002"],

  "sources": [
    {
      "type": "web",
      "url": "https://jeju.grandculture.net/...",
      "file": "grandculture/bonpuri.md"
    }
  ]
}
```

---

## 다음 단계

1. [ ] `cleaned/` 폴더 구조 생성
2. [ ] PDF 자료 C_/T_ 매칭 및 JSON 변환
3. [ ] 웹 크롤링 자료 분류 및 JSON 변환
4. [ ] 중복 설화 병합 (설문대할망 3개 소스 → 1개 통합)
