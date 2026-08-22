"""
E-BOOK 실패 항목 → OCR 매칭 파일 생성
224개 실패 항목을 OCR 결과와 매칭할 수 있도록 정리

사용법:
    python create_ocr_mapping.py
"""

import json
from pathlib import Path
from datetime import datetime


def normalize_code(code: str) -> str:
    """코드 정규화 (W-L-395 → W_L_395)"""
    return code.replace('-', '_')


def get_ocr_filename(code: str) -> str:
    """E-BOOK 코드 → OCR 파일명 변환

    E-BOOK: W_F_600 (원문)
    OCR PDF: W-F-600_제목.pdf → W_F_600.json

    주의: 하이픈과 언더스코어 변환 필요
    """
    normalized = normalize_code(code)
    return f"{normalized}.json"


def get_content_code(code: str) -> str:
    """원문(T_) → 해설(C_) 코드 변환

    T_F_001 → C_F_001
    W_F_600 → W_F_600 (해설 없음, 원본 유지)
    """
    normalized = normalize_code(code)
    if normalized.startswith('T_'):
        return 'C_' + normalized[2:]
    return normalized


def main():
    script_dir = Path(__file__).parent

    # 파일 경로
    failed_items_path = script_dir / '../../raw/ebook/_failed_items.json'
    myths_json_path = script_dir / '../../raw/crawled/jeju_myths_complete.json'
    ocr_dir = script_dir / '../../raw/ocr'
    output_path = script_dir / '../../raw/ebook/_ocr_mapping.json'

    # 실패 항목 로드
    with open(failed_items_path, 'r', encoding='utf-8') as f:
        failed_data = json.load(f)

    # 원본 설화 목록 로드
    with open(myths_json_path, 'r', encoding='utf-8') as f:
        myths_data = json.load(f)

    # 코드 → 설화 정보 인덱스 생성
    code_to_myth = {}
    for category, items in myths_data.get('by_category', {}).items():
        for item in items:
            code_to_myth[item['code']] = item

    # 기존 OCR 파일 목록
    existing_ocr = set()
    if ocr_dir.exists():
        existing_ocr = {f.stem for f in ocr_dir.glob('*.json')}

    # 매칭 결과 생성
    mapping_results = {
        'created_at': datetime.now().isoformat(),
        'description': 'E-BOOK 텍스트 추출 실패 항목 → OCR 매칭 정보',
        'total_failed': failed_data['total_failed'],
        'summary': {
            'ocr_found': 0,
            'ocr_missing': 0,
            'has_content_pair': 0  # C_ 해설 버전 존재
        },
        'items': []
    }

    for item in failed_data['items']:
        code = item['code']
        normalized_code = normalize_code(code)

        # 원본 설화 정보
        myth_info = code_to_myth.get(code, {})

        # OCR 파일 존재 여부
        ocr_filename = get_ocr_filename(code)
        ocr_exists = normalized_code in existing_ocr

        # 해설 버전 (C_) 존재 여부
        content_code = get_content_code(code)
        content_ocr_exists = content_code in existing_ocr if content_code != normalized_code else False

        mapping_item = {
            'ebook_code': code,
            'normalized_code': normalized_code,
            'title': myth_info.get('title', ''),
            'category': myth_info.get('category', ''),
            'sub_category': myth_info.get('sub_category', ''),
            'type': myth_info.get('type', ''),  # 원문/해설
            'ebook_url': myth_info.get('ebook_url', ''),
            'pdf_url': myth_info.get('pdf_url', ''),
            'ocr_mapping': {
                'expected_file': ocr_filename,
                'ocr_exists': ocr_exists,
                'content_code': content_code if content_code != normalized_code else None,
                'content_ocr_exists': content_ocr_exists
            },
            'fail_reason': item.get('reason', 'unknown'),
            'resolution': 'use_ocr' if ocr_exists else ('use_content_ocr' if content_ocr_exists else 'pending_ocr')
        }

        mapping_results['items'].append(mapping_item)

        # 통계 업데이트
        if ocr_exists:
            mapping_results['summary']['ocr_found'] += 1
        else:
            mapping_results['summary']['ocr_missing'] += 1

        if content_ocr_exists:
            mapping_results['summary']['has_content_pair'] += 1

    # 결과 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mapping_results, f, ensure_ascii=False, indent=2)

    # 요약 출력
    print("\n" + "="*60)
    print("📊 E-BOOK 실패 항목 → OCR 매칭 결과")
    print("="*60)
    print(f"총 실패 항목: {mapping_results['total_failed']}개")
    print(f"✅ OCR 파일 존재: {mapping_results['summary']['ocr_found']}개")
    print(f"❌ OCR 파일 없음: {mapping_results['summary']['ocr_missing']}개")
    print(f"📝 해설(C_) 버전 존재: {mapping_results['summary']['has_content_pair']}개")
    print("="*60)
    print(f"📁 매칭 파일 저장: {output_path}")

    # 카테고리별 분석
    print("\n📂 카테고리별 분포:")
    category_counts = {}
    for item in mapping_results['items']:
        cat = item.get('category', '미분류')
        category_counts[cat] = category_counts.get(cat, 0) + 1

    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  - {cat}: {count}개")


if __name__ == '__main__':
    main()
