"""
제주 설화 E-BOOK 텍스트 크롤러
book_config.js에서 직접 텍스트 추출 (OCR 불필요!)

사용법:
    python ebook_text_crawler.py --output ../../raw/ebook
    python ebook_text_crawler.py --limit 10  # 테스트용
"""

import json
import re
import time
import argparse
import logging
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.request
import urllib.error

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EbookTextCrawler:
    """E-BOOK book_config.js에서 텍스트 추출"""

    def __init__(self, output_dir: str, delay: float = 0.5):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.delay = delay  # 요청 간 딜레이 (서버 부하 방지)
        self.stats = {'success': 0, 'failed': 0, 'skipped': 0}

    def get_book_config_url(self, ebook_url: str) -> str:
        """E-BOOK URL에서 book_config.js URL 생성"""
        # https://jeju.go.kr/files/ebook/cul-ebook/001/1928/T_F_001/e-book.html
        # → https://jeju.go.kr/files/ebook/cul-ebook/001/1928/T_F_001/files/search/book_config.js
        base_url = ebook_url.replace('/e-book.html', '')
        return f"{base_url}/files/search/book_config.js"

    def extract_text_from_config(self, js_content: str) -> str:
        """book_config.js에서 textForPages 배열 추출"""
        # var textForPages = ["텍스트1", "텍스트2"];
        # 세미콜론 전까지 전체 매칭 (DOTALL로 줄바꿈 포함)
        match = re.search(r'var\s+textForPages\s*=\s*\[(.*?)\];\s*var\s+positionForPages', js_content, re.DOTALL)
        if not match:
            # 다른 패턴 시도
            match = re.search(r'var\s+textForPages\s*=\s*\[(.*?)\];', js_content, re.DOTALL)

        if match:
            array_content = match.group(1).strip()

            # JSON 배열로 파싱 시도
            try:
                array_str = '[' + array_content + ']'
                pages = json.loads(array_str)
                # 빈 문자열 제거하고 합치기
                text_parts = [p.strip() for p in pages if p.strip()]
                return '\n\n'.join(text_parts)
            except json.JSONDecodeError:
                # 따옴표로 감싸진 텍스트 직접 추출
                text_parts = re.findall(r'"([^"]+)"', array_content)
                return '\n\n'.join(text_parts)
        return ""

    def fetch_ebook_text(self, item: dict) -> dict:
        """단일 E-BOOK 텍스트 가져오기"""
        code = item.get('code', 'unknown')
        ebook_url = item.get('ebook_url', '')

        if not ebook_url:
            return {'code': code, 'status': 'skipped', 'reason': 'no_url'}

        config_url = self.get_book_config_url(ebook_url)

        try:
            # 브라우저처럼 보이는 헤더 (WAF 우회)
            req = urllib.request.Request(
                config_url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Referer': ebook_url
                }
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                content = response.read().decode('utf-8-sig')  # BOM 자동 제거

            text = self.extract_text_from_config(content)

            if not text:
                return {'code': code, 'status': 'failed', 'reason': 'no_text_found'}

            # 결과 JSON 생성
            result = {
                'code': code,
                'title': item.get('title', ''),
                'category': item.get('category', ''),
                'sub_category': item.get('sub_category', ''),
                'type': item.get('type', ''),  # 원문/해설
                'content': {
                    'text': text,
                    'char_count': len(text)
                },
                'source': {
                    'ebook_url': ebook_url,
                    'config_url': config_url
                },
                'metadata': {
                    'crawled_at': datetime.now().isoformat(),
                    'crawler_version': '1.0.0'
                }
            }

            return {'code': code, 'status': 'success', 'data': result}

        except urllib.error.HTTPError as e:
            return {'code': code, 'status': 'failed', 'reason': f'http_{e.code}'}
        except Exception as e:
            return {'code': code, 'status': 'failed', 'reason': str(e)}

    def crawl_all(self, myths_json_path: str, limit: int = None, workers: int = 5):
        """전체 설화 크롤링"""
        # JSON 로드
        with open(myths_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 모든 항목 수집
        all_items = []
        for category, items in data.get('by_category', {}).items():
            all_items.extend(items)

        if limit:
            all_items = all_items[:limit]

        total = len(all_items)
        logger.info(f"총 {total}개 E-BOOK 크롤링 시작 (workers={workers})")

        results = []

        # 순차 처리 (서버 부하 방지)
        for i, item in enumerate(all_items, 1):
            result = self.fetch_ebook_text(item)
            results.append(result)

            if result['status'] == 'success':
                self.stats['success'] += 1
                # JSON 저장 (ebook_ 접두사로 OCR과 구분)
                output_file = self.output_dir / f"ebook_{result['code']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result['data'], f, ensure_ascii=False, indent=2)
                logger.info(f"[{i}/{total}] ✅ {result['code']}")
            elif result['status'] == 'skipped':
                self.stats['skipped'] += 1
                logger.debug(f"[{i}/{total}] ⏭️ {result['code']} - {result.get('reason')}")
            else:
                self.stats['failed'] += 1
                logger.warning(f"[{i}/{total}] ❌ {result['code']} - {result.get('reason')}")

            # 딜레이
            if i < total:
                time.sleep(self.delay)

        # 결과 요약 저장
        summary = {
            'crawled_at': datetime.now().isoformat(),
            'total': total,
            'success': self.stats['success'],
            'failed': self.stats['failed'],
            'skipped': self.stats['skipped'],
            'results': results
        }

        summary_file = self.output_dir / '_crawl_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        self.print_summary()

    def print_summary(self):
        """결과 요약 출력"""
        print("\n" + "="*50)
        print("📊 E-BOOK 크롤링 결과")
        print("="*50)
        print(f"✅ 성공: {self.stats['success']}")
        print(f"❌ 실패: {self.stats['failed']}")
        print(f"⏭️ 스킵: {self.stats['skipped']}")
        print("="*50)


def main():
    parser = argparse.ArgumentParser(description='제주 설화 E-BOOK 텍스트 크롤러')
    parser.add_argument('--input', '-i',
                        default='../../raw/crawled/jeju_myths_complete.json',
                        help='설화 목록 JSON 파일')
    parser.add_argument('--output', '-o',
                        default='../../raw/ebook',
                        help='출력 디렉토리')
    parser.add_argument('--limit', '-l', type=int, help='처리 개수 제한')
    parser.add_argument('--delay', '-d', type=float, default=0.3,
                        help='요청 간 딜레이 (초)')

    args = parser.parse_args()

    # 상대 경로 해결
    script_dir = Path(__file__).parent
    input_path = script_dir / args.input
    output_path = script_dir / args.output

    crawler = EbookTextCrawler(str(output_path), delay=args.delay)
    crawler.crawl_all(str(input_path), limit=args.limit)


if __name__ == '__main__':
    main()
