# 제주 설화 PDF → JSON 변환기

## 개요

제주도청에서 다운로드한 설화 PDF 파일을 구조화된 JSON으로 변환하는 도구입니다.

PDF는 이미지 형태로 저장되어 있어 OCR(EasyOCR)을 사용하여 텍스트를 추출합니다.

## 설치

```bash
pip install -r requirements_ocr.txt
```

## 사용법

### 1. 단일 파일 테스트
```bash
python pdf_to_json_converter.py --sample /path/to/C_F_001_개와닭의원한.pdf
```

### 2. 디렉토리 일괄 변환
```bash
python pdf_to_json_converter.py \
    --input /mnt/d/jeju_myths \
    --output /path/to/output/json
```

### 3. 테스트용 (개수 제한)
```bash
python pdf_to_json_converter.py \
    --input /mnt/d/jeju_myths \
    --output ./output \
    --limit 10
```

### 4. GPU 비활성화 (CPU만 사용)
```bash
python pdf_to_json_converter.py --sample test.pdf --no-gpu
```

## PDF 파일명 규칙

| 접두어 | 의미 | 설명 |
|--------|------|------|
| `C_` | Content | 설화 해설/요약 (표준어) |
| `T_` | Text | 원문 구술 채록 (제주어) |
| `M` | Myth | 신화 |
| `F` | Folktale | 민담 |
| `L` | Legend | 전설 |

예: `C_F_001_개와 닭의 원한.pdf` = 민담 1번 해설본

## 출력 JSON 구조

```json
{
  "id": "story_F_001",
  "title": "개와 닭의 원한",
  "type": "folktale",
  "category": "자연전설",

  "content": {
    "summary": "개요 섹션 내용",
    "full_text": "내용 섹션 전문",
    "features": "특징 섹션 내용",
    "raw_text": "OCR 원본 텍스트"
  },

  "elements": {
    "characters": ["장닭", "사왕"],
    "locations": [],
    "keywords": ["개", "닭", "삼해유"]
  },

  "sources": [{
    "type": "pdf",
    "file": "C_F_001_개와 닭의 원한.pdf",
    "reference": "출처 정보"
  }],

  "metadata": {
    "source_type": "content",
    "source_id": "C_F_001",
    "converted_at": "2024-12-03T...",
    "converter_version": "1.0.0"
  }
}
```

## 다음 단계

1. C_/T_ 파일 쌍 자동 매칭 및 병합
2. 제주 방언 → 표준어 번역 추가
3. GPS 좌표 매핑 (지명 → 좌표)
4. 웹 크롤링 자료와 통합

## 관련 파일

- `data-classification.md` - 데이터 분류 체계
- `../schema.md` - JSON 스키마 정의
