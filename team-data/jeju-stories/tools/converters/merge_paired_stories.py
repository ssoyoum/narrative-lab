"""
C_/T_ 파일 쌍 병합 스크립트
OCR로 추출된 개별 JSON 파일들을 하나의 설화 JSON으로 병합

사용법:
    python merge_paired_stories.py --ocr-dir ../../raw/ocr --output ../../data/stories
"""

import os
import re
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StoryMerger:
    """C_/T_ 설화 파일 병합기"""

    # 카테고리 매핑
    CATEGORY_MAP = {
        'M': {'type': 'myth', 'folder': 'myths', 'name_ko': '신화'},
        'F': {'type': 'folktale', 'folder': 'folktales', 'name_ko': '민담'},
        'L': {'type': 'legend', 'folder': 'legends', 'name_ko': '전설'}
    }

    # 세부 카테고리 추정 키워드
    SUBCATEGORY_PATTERNS = {
        '창조신화': ['창조', '만들', '생겨', '태초', '세상'],
        '본풀이': ['본풀이', '굿', '제사', '신앙', '무속'],
        '지명유래': ['지명', '이름', '불리', '마을', '오름'],
        '역사전설': ['역사', '조선', '왕', '장수', '전쟁'],
        '인물전설': ['인물', '효자', '열녀', '선비', '부자'],
        '자연전설': ['도깨비', '도채비', '귀신', '용', '뱀'],
        '동물담': ['개', '닭', '소', '말', '돼지', '동물'],
        '교훈담': ['교훈', '착한', '욕심', '벌', '복']
    }

    def __init__(self, ocr_dir: str, output_dir: str):
        self.ocr_dir = Path(ocr_dir)
        self.output_dir = Path(output_dir)
        self.stats = {
            'paired': 0,
            'c_only': 0,
            't_only': 0,
            'merged': 0,
            'errors': 0
        }

    def parse_file_id(self, filename: str) -> dict:
        """파일명에서 ID 정보 추출

        예: C_F_001_개와 닭의 원한.json
        """
        # .json 확장자 제거
        name = filename.replace('.json', '')

        # 패턴 매칭
        match = re.match(r'([CT])_([FML])_(\d+)_(.+)', name)
        if match:
            return {
                'content_type': 'content' if match.group(1) == 'C' else 'text',
                'type_code': match.group(1),
                'category_code': match.group(2),
                'number': match.group(3),
                'title': match.group(4),
                'pair_key': f"{match.group(2)}_{match.group(3)}"  # 매칭 키
            }
        return None

    def find_pairs(self) -> dict:
        """C_/T_ 파일 쌍 찾기"""
        pairs = defaultdict(lambda: {'C': None, 'T': None})

        for json_file in self.ocr_dir.glob('*.json'):
            if json_file.name.startswith('_'):  # 메타 파일 제외
                continue

            info = self.parse_file_id(json_file.name)
            if info:
                pair_key = info['pair_key']
                pairs[pair_key][info['type_code']] = {
                    'file': json_file,
                    'info': info
                }

        return dict(pairs)

    def extract_narrator(self, text: str) -> dict:
        """T_ 파일에서 구연자 정보 추출"""
        narrator = {}

        # 구연자 이름 패턴
        name_match = re.search(r'구연자[:\s]*([가-힣]+)', text)
        if name_match:
            narrator['name'] = name_match.group(1)

        # 성별 패턴
        if re.search(r'[남자|남성|할아버지|하르방]', text):
            narrator['gender'] = '남'
        elif re.search(r'[여자|여성|할머니|할망]', text):
            narrator['gender'] = '여'

        # 나이 패턴
        age_match = re.search(r'(\d{2,3})\s*세', text)
        if age_match:
            narrator['age'] = int(age_match.group(1))

        # 지역 패턴
        location_match = re.search(r'([가-힣]+[리읍면동])', text)
        if location_match:
            narrator['location'] = location_match.group(1)

        return narrator if narrator else None

    def determine_subcategory(self, content: str, category_code: str) -> str:
        """내용 기반 세부 카테고리 추정"""
        for category, keywords in self.SUBCATEGORY_PATTERNS.items():
            if any(kw in content for kw in keywords):
                return category

        # 기본값
        defaults = {'M': '기타 신화', 'F': '기타 민담', 'L': '기타 전설'}
        return defaults.get(category_code, '기타')

    def merge_pair(self, pair_key: str, c_data: dict, t_data: dict) -> dict:
        """C_/T_ 쌍을 하나의 JSON으로 병합"""
        # 기본 정보 (C_ 파일 우선, 없으면 T_ 파일)
        primary = c_data or t_data
        info = primary['info']

        category_info = self.CATEGORY_MAP.get(info['category_code'], {})

        # 파일 내용 로드
        c_content = {}
        t_content = {}

        if c_data:
            with open(c_data['file'], 'r', encoding='utf-8') as f:
                c_content = json.load(f)

        if t_data:
            with open(t_data['file'], 'r', encoding='utf-8') as f:
                t_content = json.load(f)

        # 텍스트 추출
        c_text = c_content.get('content', {}).get('raw_text', '')
        t_text = t_content.get('content', {}).get('raw_text', '')

        # 구연자 정보 추출 (T_ 파일에서)
        narrator = None
        if t_text:
            narrator = self.extract_narrator(t_text)

        # 세부 카테고리 추정
        combined_text = c_text + t_text
        subcategory = self.determine_subcategory(combined_text, info['category_code'])

        # 병합된 JSON 생성
        merged = {
            "id": f"story_{info['category_code']}_{info['number']}",
            "title": info['title'],
            "title_alt": [],
            "type": category_info.get('type', 'unknown'),
            "category": subcategory,

            "content": {
                "summary": c_content.get('content', {}).get('summary', ''),
                "full_text": c_content.get('content', {}).get('full_text', ''),
                "original_text": t_content.get('content', {}).get('raw_text', ''),
                "features": c_content.get('content', {}).get('features', ''),
                "narrator": narrator
            },

            "elements": {
                "characters": list(set(
                    c_content.get('elements', {}).get('characters', []) +
                    t_content.get('elements', {}).get('characters', [])
                )),
                "locations": list(set(
                    c_content.get('elements', {}).get('locations', []) +
                    t_content.get('elements', {}).get('locations', [])
                )),
                "keywords": c_content.get('elements', {}).get('keywords', []),
                "themes": []
            },

            "sources": [],

            "metadata": {
                "source_ids": [],
                "has_dialect": bool(t_text),
                "converted_at": datetime.now().isoformat(),
                "converter_version": "2.0.0"
            }
        }

        # 소스 정보 추가
        if c_data:
            merged['sources'].append({
                "type": "pdf",
                "file": c_data['file'].name.replace('.json', '.pdf'),
                "content_type": "content",
                "reference": c_content.get('sources', [{}])[0].get('reference', '')
            })
            merged['metadata']['source_ids'].append(
                f"C_{info['category_code']}_{info['number']}"
            )

        if t_data:
            merged['sources'].append({
                "type": "pdf",
                "file": t_data['file'].name.replace('.json', '.pdf'),
                "content_type": "text"
            })
            merged['metadata']['source_ids'].append(
                f"T_{info['category_code']}_{info['number']}"
            )

        return merged, category_info.get('folder', 'unknown')

    def process_all(self):
        """모든 파일 쌍 처리"""
        pairs = self.find_pairs()
        logger.info(f"총 {len(pairs)}개 설화 쌍 발견")

        # 출력 폴더 생성
        for cat_info in self.CATEGORY_MAP.values():
            (self.output_dir / cat_info['folder']).mkdir(parents=True, exist_ok=True)

        for pair_key, pair in pairs.items():
            try:
                c_data = pair['C']
                t_data = pair['T']

                # 통계 업데이트
                if c_data and t_data:
                    self.stats['paired'] += 1
                elif c_data:
                    self.stats['c_only'] += 1
                else:
                    self.stats['t_only'] += 1

                # 병합
                merged, folder = self.merge_pair(pair_key, c_data, t_data)

                # 저장
                output_file = self.output_dir / folder / f"{merged['id']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(merged, f, ensure_ascii=False, indent=2)

                self.stats['merged'] += 1
                logger.debug(f"병합 완료: {merged['id']}")

            except Exception as e:
                logger.error(f"병합 실패 [{pair_key}]: {e}")
                self.stats['errors'] += 1

        # 결과 요약
        self.print_summary()

    def print_summary(self):
        """처리 결과 요약 출력"""
        print("\n" + "="*50)
        print("📊 병합 결과 요약")
        print("="*50)
        print(f"✅ 성공적으로 병합: {self.stats['merged']}")
        print(f"   - C_+T_ 쌍: {self.stats['paired']}")
        print(f"   - C_만 존재: {self.stats['c_only']}")
        print(f"   - T_만 존재: {self.stats['t_only']}")
        print(f"❌ 오류: {self.stats['errors']}")
        print("="*50)


def main():
    parser = argparse.ArgumentParser(
        description='C_/T_ 설화 파일 쌍 병합기'
    )

    parser.add_argument('--ocr-dir', '-i', required=True,
                        help='OCR 추출된 JSON 디렉토리')
    parser.add_argument('--output', '-o', required=True,
                        help='병합 결과 저장 디렉토리')

    args = parser.parse_args()

    merger = StoryMerger(args.ocr_dir, args.output)
    merger.process_all()


if __name__ == '__main__':
    main()
