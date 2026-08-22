#!/bin/bash
# OCR 샘플 테스트 스크립트
# 사용법: ./test_ocr_sample.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/../.."
PDF_SOURCE="/mnt/d/jeju_myths"
OUTPUT_DIR="$PROJECT_DIR/raw/ocr_test"

echo "🔧 OCR 테스트 시작"
echo "================================"

# 1. 의존성 확인
echo "📦 의존성 확인 중..."
python3 -c "import fitz; import easyocr" 2>/dev/null || {
    echo "❌ 의존성이 설치되지 않았습니다."
    echo "실행: pip install -r $SCRIPT_DIR/requirements_ocr.txt"
    exit 1
}
echo "✅ 의존성 OK"

# 2. PDF 소스 확인
echo ""
echo "📁 PDF 소스 확인 중..."
if [ -d "$PDF_SOURCE" ]; then
    PDF_COUNT=$(find "$PDF_SOURCE" -name "*.pdf" 2>/dev/null | wc -l)
    echo "✅ PDF 소스 발견: $PDF_SOURCE ($PDF_COUNT개 파일)"
else
    echo "⚠️ PDF 소스 없음: $PDF_SOURCE"
    echo "   Windows 드라이브가 마운트되어 있는지 확인하세요."
fi

# 3. 출력 폴더 생성
mkdir -p "$OUTPUT_DIR"

# 4. 샘플 PDF 선택 (C_와 T_ 쌍으로)
echo ""
echo "📄 샘플 PDF 선택..."

# 민담에서 첫 번째 쌍 찾기
C_SAMPLE=$(find "$PDF_SOURCE" -name "C_F_001*.pdf" 2>/dev/null | head -1)
T_SAMPLE=$(find "$PDF_SOURCE" -name "T_F_001*.pdf" 2>/dev/null | head -1)

if [ -z "$C_SAMPLE" ] && [ -z "$T_SAMPLE" ]; then
    echo "⚠️ 샘플 PDF를 찾을 수 없습니다."
    echo "   수동으로 PDF 경로를 지정하세요:"
    echo "   python3 pdf_to_json_converter.py --sample <PDF_PATH>"
    exit 0
fi

# 5. OCR 변환 테스트
echo ""
echo "🔄 OCR 변환 테스트..."

if [ -n "$C_SAMPLE" ]; then
    echo "   C_ 파일: $(basename "$C_SAMPLE")"
    python3 "$SCRIPT_DIR/pdf_to_json_converter.py" \
        --sample "$C_SAMPLE" \
        --no-gpu > "$OUTPUT_DIR/C_F_001_sample.json" 2>&1 || {
        echo "   ⚠️ C_ 변환 중 오류 (GPU 없이 시도)"
    }
fi

if [ -n "$T_SAMPLE" ]; then
    echo "   T_ 파일: $(basename "$T_SAMPLE")"
    python3 "$SCRIPT_DIR/pdf_to_json_converter.py" \
        --sample "$T_SAMPLE" \
        --no-gpu > "$OUTPUT_DIR/T_F_001_sample.json" 2>&1 || {
        echo "   ⚠️ T_ 변환 중 오류"
    }
fi

# 6. 결과 확인
echo ""
echo "📊 결과 확인..."
echo "================================"

for json_file in "$OUTPUT_DIR"/*.json; do
    if [ -f "$json_file" ]; then
        echo ""
        echo "📄 $(basename "$json_file"):"
        python3 -c "
import json
with open('$json_file') as f:
    data = json.load(f)
print(f\"  제목: {data.get('title', 'N/A')}\")
print(f\"  유형: {data.get('type', 'N/A')}\")
print(f\"  OCR 신뢰도: {data.get('metadata', {}).get('ocr_confidence', 'N/A')}\")
content = data.get('content', {})
raw_len = len(content.get('raw_text', ''))
print(f\"  추출 텍스트 길이: {raw_len}자\")
" 2>/dev/null || echo "  (JSON 파싱 실패)"
    fi
done

echo ""
echo "================================"
echo "✅ 테스트 완료"
echo "📁 결과 위치: $OUTPUT_DIR"
