# PDF → JSON 변환 파이프라인 설계

## 개요

1,555개 PDF 파일을 OCR로 텍스트 추출 후 구조화된 JSON으로 변환하는 파이프라인.

## 1. 파일 구조 분석

### PDF 파일 명명 규칙
```
[Type]_[Category]_[Number]_[Title].pdf

Type:
  C = Content (해설/표준어)
  T = Text (원문/제주어)

Category:
  M = Myth (신화)
  F = Folktale (민담)
  L = Legend (전설)

예시:
  C_F_001_개와 닭의 원한.pdf  ← 해설 버전
  T_F_001_개와 닭의 원한.pdf  ← 제주어 원문
```

### C_/T_ 파일 관계
- **C_ (Content)**: 표준어로 정리된 해설/요약
  - 섹션 구조: ① 개요, ② 내용, ③ 특징, ④ 핵심어, ⑤ 원전, ⑥ 관련자료

- **T_ (Text)**: 제주어 구술 채록 원문
  - 구연자 정보 포함 (이름, 성별, 나이)
  - 실제 발화 내용

## 2. 변환 전략

### Phase 1: 개별 OCR 추출
```
D:\jeju_myths/
├── 민담/
│   ├── C_F_001_xxx.pdf → raw/ocr/C_F_001.json
│   └── T_F_001_xxx.pdf → raw/ocr/T_F_001.json
├── 신화/
│   ├── C_M_001_xxx.pdf → raw/ocr/C_M_001.json
│   └── T_M_001_xxx.pdf → raw/ocr/T_M_001.json
└── 전설/
    ├── C_L_001_xxx.pdf → raw/ocr/C_L_001.json
    └── T_L_001_xxx.pdf → raw/ocr/T_L_001.json
```

### Phase 2: C_/T_ 병합
```python
# 병합 규칙
merged_story = {
    "id": "story_F_001",
    "title": extracted_from_filename,
    "type": "folktale",

    "content": {
        "summary": C_file.sections.summary,
        "full_text": C_file.sections.content,
        "original_text": T_file.full_text,
        "narrator": T_file.narrator_info,
        "features": C_file.sections.features
    },

    "elements": {
        "characters": extracted_characters,
        "locations": extracted_locations,
        "keywords": C_file.sections.keywords
    },

    "sources": [
        {"type": "pdf", "file": "C_F_001.pdf", "content_type": "content"},
        {"type": "pdf", "file": "T_F_001.pdf", "content_type": "text"}
    ]
}
```

### Phase 3: 정제 및 저장
```
data/stories/
├── myths/
│   └── story_M_001.json (C_M_001 + T_M_001 병합)
├── legends/
│   └── story_L_001.json (C_L_001 + T_L_001 병합)
└── folktales/
    └── story_F_001.json (C_F_001 + T_F_001 병합)
```

## 3. 출력 JSON 스키마

```json
{
  "$schema": "jeju-story-v2",
  "id": "story_F_001",
  "title": "개와 닭의 원한",
  "title_alt": [],
  "type": "folktale",
  "category": "동물담",

  "content": {
    "summary": "개요 섹션 내용",
    "full_text": "내용 섹션 전문 (표준어)",
    "original_text": "제주어 구술 원문",
    "features": "특징 섹션 내용",
    "narrator": {
      "name": "구연자 이름",
      "gender": "남/여",
      "age": 83,
      "location": "채록 지역"
    }
  },

  "elements": {
    "characters": ["등장인물1", "등장인물2"],
    "locations": [
      {"name": "장소명", "type": "마을|산|바다|오름", "gps": null}
    ],
    "keywords": ["키워드1", "키워드2"],
    "themes": ["교훈", "유래", "신앙"]
  },

  "sources": [
    {
      "type": "pdf",
      "file": "C_F_001_개와 닭의 원한.pdf",
      "content_type": "content",
      "reference": "원전 서지사항"
    },
    {
      "type": "pdf",
      "file": "T_F_001_개와 닭의 원한.pdf",
      "content_type": "text"
    }
  ],

  "metadata": {
    "source_ids": ["C_F_001", "T_F_001"],
    "has_dialect": true,
    "converted_at": "2024-12-03T10:00:00",
    "converter_version": "2.0.0",
    "ocr_confidence": 0.85
  }
}
```

## 4. 변환기 실행

### 단일 파일 테스트
```bash
python pdf_to_json_converter.py \
  --sample "/mnt/d/jeju_myths/민담/C_F_001_개와 닭의 원한.pdf"
```

### 배치 변환
```bash
python pdf_to_json_converter.py \
  --input /mnt/d/jeju_myths \
  --output ../../raw/ocr \
  --limit 10  # 테스트용 제한
```

### C_/T_ 병합
```bash
python merge_paired_stories.py \
  --ocr-dir ../../raw/ocr \
  --output ../../data/stories
```

## 5. 품질 관리

### OCR 품질 검증
- 신뢰도 점수 저장 (`ocr_confidence`)
- 제주어 특수 문자 검증
- 섹션 파싱 성공률 모니터링

### 데이터 검증
- 필수 필드 존재 확인
- C_/T_ 쌍 매칭 검증
- 중복 설화 탐지

## 6. 예상 결과

| 유형 | C_ 파일 | T_ 파일 | 병합 결과 |
|------|---------|---------|-----------|
| 신화 | ~50 | ~50 | ~50 stories |
| 전설 | ~100 | ~100 | ~100 stories |
| 민담 | ~249 | ~269 | ~249 stories |
| **합계** | **~400** | **~420** | **~400** |

> 일부 T_ 파일은 C_ 파일 없이 존재할 수 있음 (별도 처리)
