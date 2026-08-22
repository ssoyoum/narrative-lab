"""
제주 설화 PDF → JSON 변환 스크립트
PDF 이미지에서 OCR로 텍스트 추출 후 구조화된 JSON으로 변환

사용법:
    python pdf_to_json_converter.py --input /path/to/pdfs --output /path/to/json
    python pdf_to_json_converter.py --sample /path/to/single.pdf  # 샘플 테스트
"""

import os
import re
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

# PDF/이미지 처리
import fitz  # PyMuPDF

# OCR
import easyocr

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JejuFolkloreConverter:
    """제주 설화 PDF를 JSON으로 변환하는 클래스"""

    def __init__(self, use_gpu=True):
        """
        Args:
            use_gpu: GPU 사용 여부 (CUDA 가능시)
        """
        logger.info("EasyOCR 초기화 중... (첫 실행시 모델 다운로드)")
        self.reader = easyocr.Reader(['ko', 'en'], gpu=use_gpu)
        logger.info("EasyOCR 초기화 완료")

        # 섹션 패턴 정의
        self.section_patterns = {
            'summary': r'[①1]\s*개요',
            'content': r'[②2]\s*내용',
            'features': r'[③3]\s*특징',
            'keywords': r'[④4]\s*핵심어',
            'source': r'[⑤5]\s*원전\s*서지사항',
            'related': r'[⑥6]\s*관련\s*자료'
        }

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """PDF에서 텍스트 추출 (OCR 사용)"""
        doc = fitz.open(pdf_path)
        full_text = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            # 고해상도로 이미지 렌더링
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")

            # OCR 수행
            results = self.reader.readtext(img_bytes, detail=0, paragraph=True)
            page_text = '\n'.join(results)
            full_text.append(page_text)

            logger.debug(f"페이지 {page_num + 1} OCR 완료")

        doc.close()
        return '\n\n'.join(full_text)

    def parse_file_code(self, filename: str) -> dict:
        """파일명에서 코드 정보 추출

        예: C_F_001_개와 닭의 원한.pdf
            - type_code: C (Content) / T (Text)
            - category_code: F (Folktale) / M (Myth) / L (Legend)
            - number: 001
        """
        match = re.match(r'([CT])_([FML])_(\d+)_(.+)\.pdf', filename)
        if not match:
            # W- 형식도 처리 (예: W-F-001)
            match = re.match(r'([WCT])-([FML])-(\d+)_(.+)\.pdf', filename)

        if match:
            type_map = {'C': 'content', 'T': 'text', 'W': 'web'}
            category_map = {'F': 'folktale', 'M': 'myth', 'L': 'legend'}

            return {
                'type_code': match.group(1),
                'type': type_map.get(match.group(1), 'unknown'),
                'category_code': match.group(2),
                'category': category_map.get(match.group(2), 'unknown'),
                'number': match.group(3),
                'title': match.group(4)
            }
        return None

    def parse_sections(self, text: str) -> dict:
        """텍스트에서 섹션별 내용 추출"""
        sections = {
            'summary': '',
            'content': '',
            'features': '',
            'keywords': [],
            'source': '',
            'related': ''
        }

        # 섹션 위치 찾기
        section_positions = []
        for section_name, pattern in self.section_patterns.items():
            match = re.search(pattern, text)
            if match:
                section_positions.append((match.start(), section_name, match.end()))

        # 위치순 정렬
        section_positions.sort(key=lambda x: x[0])

        # 각 섹션 내용 추출
        for i, (start, name, content_start) in enumerate(section_positions):
            if i + 1 < len(section_positions):
                end = section_positions[i + 1][0]
            else:
                end = len(text)

            content = text[content_start:end].strip()

            if name == 'keywords':
                # 키워드는 쉼표나 마침표로 분리
                keywords = re.split(r'[,，.。\n]', content)
                sections[name] = [kw.strip() for kw in keywords if kw.strip()]
            else:
                sections[name] = content

        return sections

    def extract_characters(self, text: str) -> list:
        """텍스트에서 등장인물 추출 (간단한 휴리스틱)"""
        characters = []

        # 일반적인 등장인물 패턴
        patterns = [
            r'설문대할망', r'오백장군', r'영등신', r'삼승할망',
            r'할아버지', r'할머니', r'할망', r'하르방',
            r'장닭', r'사왕', r'용왕', r'도깨비', r'도채비',
            r'부자', r'선비', r'처녀', r'총각'
        ]

        for pattern in patterns:
            if re.search(pattern, text):
                characters.append(pattern)

        return list(set(characters))

    def extract_locations(self, text: str) -> list:
        """텍스트에서 장소 추출"""
        locations = []

        # 제주 지명 패턴
        patterns = [
            r'한라산', r'백록담', r'성산일출봉', r'우도',
            r'산방산', r'송악산', r'영실', r'물영아리',
            r'효돈천', r'쇠소깍', r'천지연', r'정방폭포',
            r'[\w]+리', r'[\w]+동', r'[\w]+읍'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            locations.extend(matches)

        return list(set(locations))

    def convert_pdf_to_json(self, pdf_path: str) -> dict:
        """PDF 파일을 JSON 구조로 변환"""
        pdf_path = Path(pdf_path)
        filename = pdf_path.name

        logger.info(f"변환 중: {filename}")

        # 파일 코드 파싱
        file_info = self.parse_file_code(filename)
        if not file_info:
            logger.warning(f"파일명 형식 인식 불가: {filename}")
            file_info = {
                'type': 'unknown',
                'type_code': 'U',
                'category': 'unknown',
                'category_code': 'U',
                'number': '000',
                'title': pdf_path.stem
            }

        # OCR로 텍스트 추출
        raw_text = self.extract_text_from_pdf(str(pdf_path))

        # 섹션 파싱
        sections = self.parse_sections(raw_text)

        # 등장인물/장소 추출
        characters = self.extract_characters(raw_text)
        locations = self.extract_locations(raw_text)

        # JSON 구조 생성
        story_json = {
            "id": f"story_{file_info['category_code']}_{file_info['number']}",
            "title": file_info['title'],
            "type": file_info['category'],
            "category": self._determine_category(sections.get('content', '')),

            "content": {
                "summary": sections.get('summary', ''),
                "full_text": sections.get('content', ''),
                "features": sections.get('features', ''),
                "raw_text": raw_text  # 원본 OCR 텍스트 보존
            },

            "elements": {
                "characters": characters,
                "locations": locations,
                "keywords": sections.get('keywords', [])
            },

            "sources": [{
                "type": "pdf",
                "file": filename,
                "reference": sections.get('source', '')
            }],

            "metadata": {
                "source_type": file_info['type'],  # content or text
                "source_id": f"{file_info['type_code']}_{file_info['category_code']}_{file_info['number']}",
                "converted_at": datetime.now().isoformat(),
                "converter_version": "2.0.0",
                "ocr_confidence": self._calculate_confidence(raw_text)
            }
        }

        return story_json

    def _calculate_confidence(self, text: str) -> float:
        """OCR 신뢰도 추정 (휴리스틱)"""
        if not text:
            return 0.0

        # 한글 비율 체크
        korean_chars = len(re.findall(r'[가-힣]', text))
        total_chars = len(text.replace(' ', '').replace('\n', ''))

        if total_chars == 0:
            return 0.0

        korean_ratio = korean_chars / total_chars

        # 특수문자/깨진 문자 비율 체크
        broken_chars = len(re.findall(r'[□■◆◇○●]', text))
        broken_ratio = broken_chars / total_chars if total_chars > 0 else 0

        # 신뢰도 계산 (한글 비율 높을수록, 깨진 문자 적을수록 높음)
        confidence = min(1.0, korean_ratio * 1.2) * (1 - broken_ratio * 2)
        return round(max(0.0, confidence), 2)

    def _determine_category(self, content: str) -> str:
        """내용 기반 세부 카테고리 추정"""
        if any(kw in content for kw in ['창조', '만들', '생겨']):
            return '창조신화'
        elif any(kw in content for kw in ['지명', '이름', '불리']):
            return '지명유래'
        elif any(kw in content for kw in ['굿', '제사', '신앙']):
            return '의례'
        elif any(kw in content for kw in ['도깨비', '도채비', '귀신']):
            return '자연전설'
        else:
            return '기타'

    def process_directory(self, input_dir: str, output_dir: str, limit: int = None):
        """디렉토리 내 모든 PDF 처리"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        pdf_files = list(input_path.glob('**/*.pdf'))
        if limit:
            pdf_files = pdf_files[:limit]

        logger.info(f"총 {len(pdf_files)}개 PDF 파일 발견")

        results = {
            'success': 0,
            'failed': 0,
            'files': []
        }

        for i, pdf_file in enumerate(pdf_files, 1):
            try:
                logger.info(f"[{i}/{len(pdf_files)}] 처리 중: {pdf_file.name}")

                story_json = self.convert_pdf_to_json(str(pdf_file))

                # JSON 저장 (source_id로 저장하여 C_/T_ 구분 유지)
                source_id = story_json['metadata']['source_id']  # C_F_001 또는 T_F_001
                output_file = output_path / f"{source_id}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(story_json, f, ensure_ascii=False, indent=2)

                results['success'] += 1
                results['files'].append({
                    'input': str(pdf_file),
                    'output': str(output_file),
                    'status': 'success'
                })

            except Exception as e:
                logger.error(f"변환 실패 [{pdf_file.name}]: {e}")
                results['failed'] += 1
                results['files'].append({
                    'input': str(pdf_file),
                    'output': None,
                    'status': 'failed',
                    'error': str(e)
                })

        # 결과 요약 저장
        summary_file = output_path / '_conversion_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        logger.info(f"변환 완료: 성공 {results['success']}, 실패 {results['failed']}")
        return results


def main():
    parser = argparse.ArgumentParser(
        description='제주 설화 PDF → JSON 변환기',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--input', '-i', help='입력 PDF 디렉토리')
    parser.add_argument('--output', '-o', help='출력 JSON 디렉토리')
    parser.add_argument('--sample', '-s', help='샘플 PDF 파일 (단일 파일 테스트)')
    parser.add_argument('--limit', '-l', type=int, help='처리 개수 제한')
    parser.add_argument('--no-gpu', action='store_true', help='GPU 사용 안함')

    args = parser.parse_args()

    converter = JejuFolkloreConverter(use_gpu=not args.no_gpu)

    if args.sample:
        # 단일 파일 테스트
        result = converter.convert_pdf_to_json(args.sample)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.input and args.output:
        # 디렉토리 일괄 처리
        converter.process_directory(args.input, args.output, limit=args.limit)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
