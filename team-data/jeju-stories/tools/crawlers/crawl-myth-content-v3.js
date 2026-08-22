const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, 'web-crawled');

async function crawlSingleMythContent() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();

  // 테스트: "개와 닭의 원한"
  const testMyth = {
    title: "개와 닭의 원한",
    code: "T_F_001",
    pdf_url: "https://jeju.go.kr/tool/synap/convert.jsp?seq=1041615&no=1"
  };

  console.log(`📖 "${testMyth.title}" 본문 추출 테스트\n`);

  // 먼저 PDF 경로 찾기
  const page1 = await context.newPage();
  let pdfBasePath = null;

  page1.on('response', response => {
    const url = response.url();
    if (url.includes('.pdf.xml') && !url.includes('.files/')) {
      pdfBasePath = url.replace('.xml', '').replace(/\?.*$/, '');
    }
  });

  await page1.goto(testMyth.pdf_url, { waitUntil: 'networkidle', timeout: 60000 });
  await page1.close();

  if (!pdfBasePath) {
    console.log('   ❌ PDF 경로를 찾을 수 없음');
    await browser.close();
    return null;
  }

  console.log('   📁 PDF 경로:', pdfBasePath);

  // 페이지별 XML에서 텍스트 추출
  console.log('\n   📄 페이지별 XML에서 텍스트 추출 중...');

  let fullText = '';
  const pdfFileName = path.basename(pdfBasePath);

  for (let pageNum = 1; pageNum <= 10; pageNum++) {
    const xmlUrl = `${pdfBasePath}.files/${pdfFileName}_${pageNum}.xml`;

    try {
      const page = await context.newPage();
      const response = await page.goto(xmlUrl, { timeout: 10000 });

      if (response && response.status() === 200) {
        const content = await page.content();

        // XML 응답에서 body 내용 추출
        const bodyText = await page.evaluate(() => document.body.innerText || document.body.textContent);

        // c="문자" 패턴 추출
        const charMatches = bodyText.match(/c="([^"]{1,3})"/g);

        if (charMatches && charMatches.length > 0) {
          let pageText = charMatches
            .map(m => {
              const match = m.match(/c="([^"]+)"/);
              return match ? match[1] : '';
            })
            .join('');

          if (pageText.length > 5) {
            fullText += pageText + '\n';
            console.log(`      페이지 ${pageNum}: ${pageText.length}자`);
          }
        }
      }

      await page.close();
    } catch (error) {
      // 페이지 없음 = 끝
      break;
    }
  }

  await browser.close();

  // 결과
  console.log('\n✅ 추출 완료!');
  console.log(`   총 ${fullText.length}자\n`);

  if (fullText.length > 0) {
    console.log('--- 본문 미리보기 ---');
    console.log(fullText.slice(0, 500));
    console.log('...\n');
  } else {
    console.log('⚠️ 텍스트 추출 실패 - XML 구조 확인 필요\n');

    // XML 원본 확인
    const debugPage = await browser.newPage();
    const xmlUrl = `${pdfBasePath}.files/${pdfFileName}_1.xml`;
    await debugPage.goto(xmlUrl);
    const rawContent = await debugPage.content();
    console.log('XML 원본 (처음 1000자):\n', rawContent.slice(0, 1000));
  }

  return { ...testMyth, content: fullText };
}

crawlSingleMythContent().catch(console.error);
