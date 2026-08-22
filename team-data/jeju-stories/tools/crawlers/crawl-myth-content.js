const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, 'web-crawled');

async function crawlSingleMythContent() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 테스트: "개와 닭의 원한"
  const testMyth = {
    title: "개와 닭의 원한",
    code: "T_F_001",
    pdf_url: "https://jeju.go.kr/tool/synap/convert.jsp?seq=1041615&no=1"
  };

  console.log(`📖 "${testMyth.title}" 본문 추출 테스트\n`);

  // PDF 뷰어에서 실제 PDF 경로 추출
  let pdfBasePath = null;

  page.on('response', response => {
    const url = response.url();
    if (url.includes('.pdf.xml')) {
      // XML 파일 경로에서 base path 추출
      const match = url.match(/(https:\/\/[^?]+\.pdf)/);
      if (match && !pdfBasePath) {
        pdfBasePath = match[1];
        console.log('   📁 PDF 경로 발견:', pdfBasePath);
      }
    }
  });

  await page.goto(testMyth.pdf_url, { waitUntil: 'networkidle', timeout: 60000 });

  if (!pdfBasePath) {
    console.log('   ❌ PDF 경로를 찾을 수 없음');
    await browser.close();
    return null;
  }

  // XML 파일에서 텍스트 추출
  console.log('\n   📄 XML에서 텍스트 추출 중...');

  let fullText = '';
  let pageNum = 1;
  let hasMore = true;

  while (hasMore && pageNum <= 20) {  // 최대 20페이지
    const xmlUrl = `${pdfBasePath}.files/${path.basename(pdfBasePath)}_${pageNum}.xml`;

    try {
      const response = await page.goto(xmlUrl, { timeout: 10000 });

      if (response.status() === 200) {
        const xmlContent = await response.text();

        // XML에서 텍스트 추출 (char 태그의 c 속성)
        const charMatches = xmlContent.match(/c="([^"]+)"/g);
        if (charMatches) {
          const pageText = charMatches
            .map(m => m.match(/c="([^"]+)"/)[1])
            .join('');
          fullText += pageText + '\n\n';
          console.log(`      페이지 ${pageNum}: ${pageText.length}자`);
        }
        pageNum++;
      } else {
        hasMore = false;
      }
    } catch (error) {
      hasMore = false;
    }
  }

  await browser.close();

  // 결과
  console.log('\n✅ 추출 완료!');
  console.log(`   총 ${fullText.length}자\n`);
  console.log('--- 본문 미리보기 ---');
  console.log(fullText.slice(0, 500));
  console.log('...\n');

  // 저장
  const result = {
    ...testMyth,
    content: fullText,
    extracted_at: new Date().toISOString()
  };

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'test_myth_content.json'),
    JSON.stringify(result, null, 2)
  );

  return result;
}

crawlSingleMythContent().catch(console.error);
