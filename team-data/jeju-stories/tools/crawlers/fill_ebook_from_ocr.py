"""
E-BOOK 실패 항목을 OCR 결과로 보완
224개 실패 항목 중 OCR 파일이 있는 것을 E-BOOK 형식으로 변환하여 저장

사용법:
    python fill_ebook_from_ocr.py
    python fill_ebook_from_ocr.py --dry-run  # 실제 저장 없이 확인만

OCR 완료 후 실행하세요!
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def normalize_code(code: str) -> str:
    """코드 정규화 (W-L-395 → W_L_395)"""
    return code.replace('-', '_')


def convert_ocr_to_ebook_format(ocr_data: dict, mapping_item: dict) -> dict:
    """OCR JSON을 E-BOOK JSON 형식으로 변환"""

    # OCR 텍스트 추출 (full_text 또는 raw_text)
    content = ocr_data.get('content', {})
    text = content.get('full_text', '') or content.get('raw_text', '')

    # E-BOOK 형식으로 변환
    ebook_format = {
        'code': mapping_item['normalized_code'],
        'title': mapping_item['title'] or ocr_data.get('title', ''),
        'category': mapping_item['category'] or ocr_data.get('category', ''),
        'sub_category': mapping_item['sub_category'] or '',
        'type': mapping_item['type'] or ocr_data.get('type', ''),
        'content': {
            'text': text,
            'char_count': len(text)
        },
        'source': {
            'ebook_url': mapping_item.get('ebook_url', ''),
            'pdf_url': mapping_item.get('pdf_url', ''),
            'ocr_source': True  # OCR에서 가져왔음을 표시
        },
        'metadata': {
            'crawled_at': datetime.now().isoformat(),
            'crawler_version': '1.0.0',
            'source_type': 'ocr_fallback',
            'original_ocr_file': f"{mapping_item['normalized_code']}.json"
        }
    }

    return ebook_format


def main():
    parser = argparse.ArgumentParser(description='E-BOOK 실패 항목을 OCR로 보완')
    parser.add_argument('--dry-run', action='store_true', help='실제 저장 없이 확인만')
    args = parser.parse_args()

    script_dir = Path(__file__).parent

    # 파일 경로
    mapping_path = script_dir / '../../raw/ebook/_ocr_mapping.json'
    ocr_dir = script_dir / '../../raw/ocr'
    ebook_dir = script_dir / '../../raw/ebook'

    # 매핑 파일 로드
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping_data = json.load(f)

    # 통계
    stats = {
        'total': len(mapping_data['items']),
        'filled': 0,
        'missing_ocr': 0,
        'already_exists': 0,
        'errors': 0
    }

    print("\n" + "="*60)
    print("📥 E-BOOK 실패 항목 → OCR 보완 시작")
    print("="*60)

    if args.dry_run:
        print("⚠️  DRY-RUN 모드: 실제 저장하지 않음\n")

    for item in mapping_data['items']:
        code = item['normalized_code']
        ebook_file = ebook_dir / f"ebook_{code}.json"

        # 이미 E-BOOK 파일 존재하면 스킵
        if ebook_file.exists():
            stats['already_exists'] += 1
            continue

        # OCR 파일 확인
        ocr_file = ocr_dir / f"{code}.json"

        if not ocr_file.exists():
            stats['missing_ocr'] += 1
            continue

        try:
            # OCR 파일 로드
            with open(ocr_file, 'r', encoding='utf-8') as f:
                ocr_data = json.load(f)

            # E-BOOK 형식으로 변환
            ebook_data = convert_ocr_to_ebook_format(ocr_data, item)

            # 저장
            if not args.dry_run:
                with open(ebook_file, 'w', encoding='utf-8') as f:
                    json.dump(ebook_data, f, ensure_ascii=False, indent=2)

            stats['filled'] += 1
            print(f"✅ {code}: {item['title'][:30]}...")

        except Exception as e:
            stats['errors'] += 1
            print(f"❌ {code}: {str(e)}")

    # 결과 요약
    print("\n" + "="*60)
    print("📊 E-BOOK 보완 결과")
    print("="*60)
    print(f"전체 실패 항목: {stats['total']}개")
    print(f"✅ OCR로 보완됨: {stats['filled']}개")
    print(f"⏭️ 이미 존재: {stats['already_exists']}개")
    print(f"❌ OCR 파일 없음: {stats['missing_ocr']}개")
    print(f"⚠️ 오류 발생: {stats['errors']}개")
    print("="*60)

    if args.dry_run:
        print("\n⚠️ DRY-RUN 모드였습니다. 실제 저장하려면 --dry-run 없이 실행하세요.")

    # 매핑 파일 업데이트
    if not args.dry_run and stats['filled'] > 0:
        mapping_data['summary']['ocr_found'] = stats['filled'] + stats['already_exists']
        mapping_data['summary']['ocr_missing'] = stats['missing_ocr']
        mapping_data['last_filled_at'] = datetime.now().isoformat()

        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(mapping_data, f, ensure_ascii=False, indent=2)
        print(f"\n📁 매핑 파일 업데이트됨: {mapping_path}")


if __name__ == '__main__':
    main()
