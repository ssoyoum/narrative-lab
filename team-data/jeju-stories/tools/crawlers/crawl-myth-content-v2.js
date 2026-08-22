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
  let xmlContent = null;

  page.on('response', async response => {
    const url = response.url();
    // 메인 XML 파일 캡처 (페이지별 XML이 아닌 전체 메타 XML)
    if (url.includes('.pdf.xml') && !url.includes('.files/')) {
      pdfBasePath = url.replace('.xml', '').split('?')[0];
      console.log('   📁 PDF 메타 XML:', url);
      try {
        xmlContent = await response.text();
      } catch(e) {}
    }
  });

  await page.goto(testMyth.pdf_url, { waitUntil: 'networkidle', timeout: 60000 });

  if (!pdfBasePath) {
    console.log('   ❌ PDF 경로를 찾을 수 없음');
    await browser.close();
    return null;
  }

  // 페이지별 XML에서 텍스트 추출
  console.log('\n   📄 페이지별 XML에서 텍스트 추출 중...');

  let fullText = '';
  let pageNum = 1;
  let consecutiveErrors = 0;

  while (consecutiveErrors < 3 && pageNum <= 50) {
    const pdfFileName = path.basename(pdfBasePath);
    const xmlUrl = `${pdfBasePath}.files/${pdfFileName}_${pageNum}.xml`;

    try {
      const response = await page.evaluate(async (url) => {
        try {
          const res = await fetch(url);
          if (res.ok) {
            return await res.text();
          }
          return null;
        } catch(e) {
          return null;
        }
      }, xmlUrl);

      if (response) {
        // XML에서 텍스트만 추출
        // <char ... c="가"/> 형태에서 c 값 추출
        const charMatches = response.match(/\bc="([^"]{1,5})"/g);
        if (charMatches) {
          let pageText = charMatches
            .map(m => {
              const match = m.match(/c="([^"]+)"/);
              return match ? match[1] : '';
            })
            .filter(c => !c.includes('http') && !c.includes('cdn') && c.length <= 2)
            .join('');

          if (pageText.length > 10) {
            fullText += pageText + '\n';
            console.log(`      페이지 ${pageNum}: ${pageText.length}자 - "${pageText.slice(0, 30)}..."`);
            consecutiveErrors = 0;
          }
        }
        pageNum++;
      } else {
        consecutiveErrors++;
        pageNum++;
      }
    } catch (error) {
      consecutiveErrors++;
      pageNum++;
    }
  }

  await browser.close();

  // 결과
  console.log('\n✅ 추출 완료!');
  console.log(`   총 ${fullText.length}자\n`);
  console.log('--- 본문 미리보기 ---');
  console.log(fullText.slice(0, 800));
  console.log('...\n');

  // 저장
  const result = {
    ...testMyth,
    content: fullText.trim(),
    char_count: fullText.length,
    extracted_at: new Date().toISOString()
  };

  fs.writeFileSync(
    path.join(OUTPUT_DIR, 'test_myth_content.json'),
    JSON.stringify(result, null, 2)
  );

  console.log('💾 저장됨: test_myth_content.json');
  return result;
}

crawlSingleMythContent().catch(console.error);
