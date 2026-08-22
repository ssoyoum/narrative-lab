"""
E-BOOK 텍스트 품질 정리 스크립트
- 누락 글자, 공백 문제, 구조화 등 자동 감지 및 수정
- 원본 text 보존, text_cleaned 필드에 정리본 저장
- cleaning_notes에 수정 내역 기록

사용법:
    python clean_ebook_text.py                    # 전체 처리
    python clean_ebook_text.py --sample 10        # 샘플 10개만
    python clean_ebook_text.py --dry-run          # 저장 없이 확인
    python clean_ebook_text.py --file T_L_006     # 특정 파일만
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class EbookTextCleaner:
    """E-BOOK 텍스트 정리기"""

    def __init__(self):
        # 흔한 누락 패턴
        self.missing_char_patterns = [
            # (패턴, 수정, 설명)
            (r'일름\s*\(이름\)', '이름', '누락글자: 일름→이름'),
            (r'써\s+개\s+돋', '날개 돋', '누락글자: 써 개→날개'),
            (r'멍청\s+늠', '멍청한 놈', '누락글자: 멍청 늠→멍청한 놈'),
            (r'멍청\s+식', '멍청한 새끼', '누락글자: 멍청 식→멍청한 새끼'),
            (r'(?<![가-힣])늠(?![가-힣])', '놈', '표기: 늠→놈'),
            (r'(?<![가-힣])뒈(?![가-힣])', '되', '표기: 뒈→되'),
        ]

        # 한자 표기 정리 패턴
        self.hanja_patterns = [
            (r'\(消\)민', '소멸하면', '한자표기: (消)민→소멸하면'),
            (r'\(斬\)해', '참(斬)해', '한자표기: (斬)해→참(斬)해'),
        ]

        # 섹션 구분 패턴
        self.section_markers = {
            'recording_info': r'^[A-Z]_[A-Z]_\d+',  # 코드 시작
            'summary': r'\*\s*줄거리\s*[：:]?',
            'main_text': r'\*?\s*1\)',  # 주석 시작 = 본문 끝
            'notes': r'\d+\)',
            'source': r'[가-힣]+[,·].*제주[대설]',
        }

    def clean_text(self, text: str, metadata: dict) -> Tuple[str, Dict]:
        """텍스트 정리 및 수정 내역 반환"""
        issues = []
        cleaned = text

        # 1. 과도한 공백 정리
        original_spaces = len(re.findall(r'\s{2,}', cleaned))
        cleaned = re.sub(r'\s{3,}', '  ', cleaned)  # 3개 이상 → 2개
        cleaned = re.sub(r'[ \t]{2,}', ' ', cleaned)  # 탭/스페이스 정리
        if original_spaces > 5:
            issues.append({
                'type': '공백정리',
                'original': f'{original_spaces}개 다중공백',
                'fixed': '단일공백으로 정리',
                'note': '불필요 공백 제거'
            })

        # 2. 줄바꿈 정리
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # 3. 누락 글자 패턴 수정
        for pattern, replacement, note in self.missing_char_patterns:
            matches = re.findall(pattern, cleaned)
            if matches:
                cleaned = re.sub(pattern, replacement, cleaned)
                issues.append({
                    'type': '누락글자',
                    'original': matches[0] if matches else pattern,
                    'fixed': replacement,
                    'note': note
                })

        # 4. 한자 표기 정리
        for pattern, replacement, note in self.hanja_patterns:
            if re.search(pattern, cleaned):
                cleaned = re.sub(pattern, replacement, cleaned)
                issues.append({
                    'type': '표기오류',
                    'original': pattern.replace('\\', ''),
                    'fixed': replacement,
                    'note': note
                })

        # 5. 구조화 시도
        structured, structure_note = self._structurize_text(cleaned, metadata)
        if structure_note:
            cleaned = structured
            issues.append({
                'type': '구조화',
                'original': '연속텍스트',
                'fixed': '섹션분리',
                'note': structure_note
            })

        # 정리 노트 생성
        cleaning_notes = {
            'issues_found': issues,
            'dialect_preserved': True,
            'cleaned_at': datetime.now().strftime('%Y-%m-%d'),
            'confidence': self._calculate_confidence(issues, text, cleaned),
            'original_char_count': len(text),
            'cleaned_char_count': len(cleaned)
        }

        return cleaned, cleaning_notes

    def _structurize_text(self, text: str, metadata: dict) -> Tuple[str, Optional[str]]:
        """텍스트 구조화 (섹션 분리)"""
        # 줄거리 찾기
        summary_match = re.search(r'\*\s*줄거리\s*[：:]?\s*(.+?)(?=\*?\s*1\)|$)', text, re.DOTALL)

        # 본문 찾기 (줄거리 이후 ~ 출처 전)
        main_match = re.search(r'(?:\*\s*1\)|1\))\s*(.+?)(?=[가-힣]+[,·].*제주|$)', text, re.DOTALL)

        # 출처 찾기
        source_match = re.search(r'([가-힣]+[,·][가-힣·]+,\s*제주.+?(?:\d{4}|pp?\.\d+).+?)$', text)

        if not summary_match:
            return text, None

        # 구조화된 텍스트 생성
        title = metadata.get('title', '')
        category = metadata.get('category', '')
        sub_category = metadata.get('sub_category', '')

        sections = []
        sections.append(f"{title}\n")

        if category:
            sections.append(f"[분류] {category}" + (f" > {sub_category}" if sub_category else ""))

        # 채록정보 추출
        recording_match = re.search(r'([가-힣]+[읍면리동]\s*[0-9가-힣]*,\s*\d{4}\.\s*\d+\.\s*\d+\..*?조사.*?[남여][·\s]\d+)', text)
        if recording_match:
            sections.append(f"\n[채록정보] {recording_match.group(1).strip()}")

        # 줄거리
        if summary_match:
            summary = summary_match.group(1).strip()
            summary = re.sub(r'\s+', ' ', summary)
            sections.append(f"\n[줄거리]\n{summary}")

        # 본문
        if main_match:
            main_text = main_match.group(1).strip()
            # 대화 형식으로 정리
            main_text = re.sub(r'"([^"]+)"', r'\n"\1"', main_text)
            main_text = re.sub(r'\n{3,}', '\n\n', main_text)
            sections.append(f"\n[본문 - 제주방언 구술채록]\n{main_text}")

        # 주석 추출
        notes = re.findall(r'(\d+\)\s*[^0-9]+?)(?=\d+\)|[가-힣]+[,·].*제주|$)', text)
        if notes:
            sections.append("\n[주석]")
            for note in notes[:5]:  # 최대 5개
                sections.append(note.strip())

        # 출처
        if source_match:
            sections.append(f"\n[출처] {source_match.group(1).strip()}")

        structured = '\n'.join(sections)
        return structured, '채록정보/줄거리/본문/주석/출처 분리'

    def _calculate_confidence(self, issues: List[Dict], original: str, cleaned: str) -> float:
        """정리 신뢰도 계산"""
        base_confidence = 0.9

        # 수정 항목이 많으면 신뢰도 하락
        if len(issues) > 10:
            base_confidence -= 0.1
        elif len(issues) > 5:
            base_confidence -= 0.05

        # 길이 차이가 크면 신뢰도 하락
        len_ratio = len(cleaned) / max(len(original), 1)
        if len_ratio < 0.5 or len_ratio > 1.5:
            base_confidence -= 0.15

        # 추정 수정이 있으면 신뢰도 하락
        for issue in issues:
            if '추정' in issue.get('note', ''):
                base_confidence -= 0.05

        return round(max(0.5, min(1.0, base_confidence)), 2)


def process_ebook_files(ebook_dir: Path, sample: int = None, dry_run: bool = False,
                        specific_file: str = None) -> Dict:
    """E-BOOK 파일들 배치 처리"""
    cleaner = EbookTextCleaner()

    stats = {
        'total': 0,
        'cleaned': 0,
        'skipped': 0,
        'errors': 0,
        'already_cleaned': 0
    }

    # 파일 목록
    if specific_file:
        files = list(ebook_dir.glob(f'ebook_{specific_file}.json'))
        if not files:
            files = list(ebook_dir.glob(f'*{specific_file}*.json'))
    else:
        files = sorted(ebook_dir.glob('ebook_*.json'))

    if sample:
        files = files[:sample]

    stats['total'] = len(files)

    print(f"\n{'='*60}")
    print(f"📝 E-BOOK 텍스트 정리 시작")
    print(f"{'='*60}")
    print(f"대상 파일: {len(files)}개")
    if dry_run:
        print("⚠️ DRY-RUN 모드: 실제 저장하지 않음")
    print(f"{'='*60}\n")

    for i, file_path in enumerate(files, 1):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 이미 정리된 파일 스킵
            if 'text_cleaned' in data.get('content', {}):
                stats['already_cleaned'] += 1
                continue

            # 텍스트 없으면 스킵
            text = data.get('content', {}).get('text', '')
            if not text or len(text) < 50:
                stats['skipped'] += 1
                continue

            # 메타데이터 준비
            metadata = {
                'title': data.get('title', ''),
                'category': data.get('category', ''),
                'sub_category': data.get('sub_category', ''),
                'type': data.get('type', '')
            }

            # 정리 수행
            cleaned_text, cleaning_notes = cleaner.clean_text(text, metadata)

            # 결과 저장
            data['content']['text_cleaned'] = cleaned_text
            data['content']['cleaning_notes'] = cleaning_notes

            if not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            stats['cleaned'] += 1

            # 진행 상황 출력
            issues_count = len(cleaning_notes['issues_found'])
            confidence = cleaning_notes['confidence']
            code = data.get('code', file_path.stem)

            if issues_count > 0:
                print(f"[{i}/{len(files)}] ✅ {code}: {issues_count}개 이슈 수정 (신뢰도: {confidence})")
            else:
                print(f"[{i}/{len(files)}] ✓ {code}: 양호")

        except Exception as e:
            stats['errors'] += 1
            print(f"[{i}/{len(files)}] ❌ {file_path.name}: {str(e)}")

    return stats


def main():
    parser = argparse.ArgumentParser(description='E-BOOK 텍스트 품질 정리')
    parser.add_argument('--sample', type=int, help='샘플 개수만 처리')
    parser.add_argument('--dry-run', action='store_true', help='저장 없이 확인만')
    parser.add_argument('--file', type=str, help='특정 파일만 처리 (예: T_L_006)')
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    ebook_dir = script_dir / '../../raw/ebook'

    stats = process_ebook_files(
        ebook_dir=ebook_dir,
        sample=args.sample,
        dry_run=args.dry_run,
        specific_file=args.file
    )

    # 결과 요약
    print(f"\n{'='*60}")
    print(f"📊 E-BOOK 텍스트 정리 결과")
    print(f"{'='*60}")
    print(f"전체 파일: {stats['total']}개")
    print(f"✅ 정리 완료: {stats['cleaned']}개")
    print(f"⏭️ 이미 정리됨: {stats['already_cleaned']}개")
    print(f"⏭️ 스킵 (텍스트 없음): {stats['skipped']}개")
    print(f"❌ 오류: {stats['errors']}개")
    print(f"{'='*60}")

    if args.dry_run:
        print("\n⚠️ DRY-RUN 모드였습니다. 실제 저장하려면 --dry-run 없이 실행하세요.")


if __name__ == '__main__':
    main()
