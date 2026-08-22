# PDF 파일 변환 가이드

## PDF 파일 구조

### 접두사 설명
| 접두사 | 의미 | 내용 |
|--------|------|------|
| C_ | Content | 해설/요약 (표준어) - 개요, 내용, 특징, 핵심어, 원전 서지사항 |
| T_ | Text | 원문 채록 (제주어) - 실제 구연 내용, 제주 방언 |
| W_ | Interview | 현장 조사 인터뷰 (2017년) - 조사자/제보자 대화 형식 |

### 카테고리 코드
| 코드 | 분류 |
|------|------|
| M | 신화 (Myth) |
| L | 전설 (Legend) |
| F | 민담 (Folktale) |

### 파일명 패턴
```
{접두사}_{카테고리}_{번호}_{제목}.pdf
예: C_F_001_개와 닭의 원한.pdf
    T_F_001_개와 닭의 원한.pdf
```

## 파일 현황 (총 1,555개)

### 신화 (182개)
- C_M_*: 85개 (해설)
- T_M_*: 85개 (원문)
- W_M_*: 12개 (인터뷰)

### 민담 (322개)
- C_F_*: 13개 (해설)
- T_F_*: 13개 (원문)
- W_F_*: 296개 (인터뷰)

### 전설 (~1,051개)
- C_L_*: 151개 (해설)
- T_L_*: 171개 (원문)
- W_L_*: 525개+ (인터뷰)

## C_/T_ 매칭 쌍

같은 번호의 C_와 T_ 파일은 동일한 설화의 해설과 원문입니다.
- C_F_001 ↔ T_F_001 (같은 설화)
- C_M_010 ↔ T_M_010 (같은 설화)

## JSON 변환 스키마

```json
{
  "id": "folktale_xxx",
  "title": "설화 제목",
  "title_alt": [],
  "type": "folktale|legend|myth",
  "category": "민담|전설|신화",

  "content": {
    "summary": "개요에서 추출",
    "episodes": [
      {"title": "에피소드 제목", "content": "내용"}
    ],
    "moral": "교훈 (있는 경우)",
    "themes": ["주제1", "주제2"]
  },

  "elements": {
    "characters": [
      {"name": "이름", "role": "역할"}
    ],
    "locations": [
      {"name": "장소", "type": "유형", "region": "지역"}
    ],
    "keywords": ["핵심어에서 추출"]
  },

  "sources": [
    {
      "type": "pdf",
      "content_file": "C_파일명.pdf",
      "text_file": "T_파일명.pdf",
      "original_reference": "원전 서지사항",
      "informant": {"name": "제보자", "gender": "성별", "age": 나이}
    }
  ],

  "dialect_sample": {
    "note": "제주어 원문 샘플",
    "sample": "원문 일부"
  },

  "metadata": {
    "created_at": "날짜",
    "data_quality": "high|medium",
    "has_dialect_text": true|false
  }
}
```

## 변환 우선순위

1. **C_/T_ 매칭 쌍** (해설+원문 완비): 183개
   - 신화: 85쌍
   - 민담: 13쌍
   - 전설: ~85쌍 (C_와 T_ 중 적은 수 기준)

2. **W_ 단독 파일** (인터뷰 자료): ~833개
   - 별도 스키마로 변환 필요

## 자동화 스크립트 요구사항

PDF 텍스트 추출을 위해 필요한 도구:
- Python + PyPDF2 또는 pdfplumber
- 한글 인코딩 처리

## 수동 변환 완료 목록

- [x] C_F_001/T_F_001 개와 닭의 원한 → gae-dak-wonhan.json
