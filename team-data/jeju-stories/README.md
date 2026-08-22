# 제주 설화 데이터베이스 (Jeju Folklore Database)

제주도 설화를 체계적으로 정리한 데이터베이스입니다.
"오래된 그루터기의 이야기" 프로젝트에서 여행지 맞춤형 스토리텔링 컨텐츠의 재료로 활용됩니다.

## 폴더 구조

```
jeju-stories/
├── data/                    # 📦 최종 사용 데이터
│   ├── stories/             # 정제된 설화 JSON (58개)
│   │   ├── myths/           # 신화 (15개) - 창조신화, 본풀이
│   │   ├── legends/         # 전설 (16개) - 지명유래, 역사전설
│   │   └── folktales/       # 민담 (27개) - 교훈담, 동물담
│   ├── locations/           # 지역별 데이터 (GPS 연동)
│   │   └── seongsan/        # 성산권 시범 데이터
│   └── meta/                # 메타데이터
│       └── classification/  # 분류체계 (본풀이 등)
│
├── raw/                     # 📥 원본 데이터
│   └── crawled/             # 웹 크롤링 원본
│       ├── jeju_myths_complete.json  # 1,563건 메타데이터
│       ├── encykorea/       # 한국민족문화대백과
│       ├── grandculture/    # 디지털제주문화대전
│       └── namuwiki/        # 나무위키
│
├── tools/                   # 🔧 스크립트/도구
│   ├── converters/          # 변환 도구
│   │   ├── pdf_to_json.py   # OCR 기반 PDF→JSON 변환기
│   │   └── requirements.txt
│   └── crawlers/            # 웹 크롤러
│
├── docs/                    # 📚 문서
│   ├── data-classification.md   # 분류 체계 설명
│   ├── source-list.md           # 수집 소스 목록
│   └── PDF_CONVERSION_README.md # OCR 변환 가이드
│
└── schema.md                # 데이터 스키마 정의
```

## 데이터 현황

| 유형 | 개수 | 상태 | 설명 |
|------|------|------|------|
| 신화 (myths) | 15 | ✅ 정제 완료 | 설문대할망, 본풀이 등 |
| 전설 (legends) | 16 | ✅ 정제 완료 | 백록담, 영실기암 등 |
| 민담 (folktales) | 27 | ✅ 정제 완료 | 교훈담, 동물담 등 |
| PDF 원본 | 1,555 | ⏳ OCR 대기 | D:\jeju_myths에 저장 |

## JSON 스키마 예시

```json
{
  "id": "myth_seolmundae",
  "title": "설문대할망",
  "type": "myth",
  "category": "창조신화",
  "content": {
    "summary": "제주도를 창조한 거인 여신...",
    "episodes": [...]
  },
  "elements": {
    "characters": ["설문대할망"],
    "locations": [{"name": "한라산", "type": "산"}],
    "keywords": ["창조신화", "거인"]
  },
  "sources": [...]
}
```

## 활용 방법

### 1. 스토리 검색
```python
import json
from pathlib import Path

# 모든 신화 로드
myths = Path("data/stories/myths").glob("*.json")
for myth in myths:
    data = json.loads(myth.read_text())
    print(f"{data['title']}: {data['content']['summary'][:50]}...")
```

### 2. GPS 기반 스토리 매칭
```python
# 성산권 스토리 조회
seongsan = json.loads(Path("data/locations/seongsan/stories.json").read_text())
```

### 3. PDF → JSON 변환

#### 단계 1: OCR 추출
```bash
cd tools/converters
pip install -r requirements_ocr.txt

# 샘플 테스트
./test_ocr_sample.sh

# 배치 변환 (개별 JSON 생성)
python pdf_to_json_converter.py --input /mnt/d/jeju_myths --output ../../raw/ocr
```

#### 단계 2: C_/T_ 파일 병합
```bash
# 개별 OCR 결과를 설화 단위로 병합
python merge_paired_stories.py --ocr-dir ../../raw/ocr --output ../../data/stories
```

## 관련 문서

- [데이터 분류 체계](docs/data-classification.md)
- [PDF 변환 파이프라인](docs/PDF_CONVERSION_PIPELINE.md)
- [스키마 정의](schema.md)

## 담당자

- 설화 데이터 정리: tiger 브랜치
