const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const https = require('https');

const OUTPUT_DIR = path.join(__dirname, 'web-crawled');

// Node.js native https로 XML 가져오기
function fetchXml(url) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => resolve(data));
    }).on('error', reject);
  });
}

async function crawlSingleMythContent() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();

  const testMyth = {
    title: "개와 닭의 원한",
    code: "T_F_001",
    pdf_url: "https://jeju.go.kr/tool/synap/convert.jsp?seq=1041615&no=1"
  };

  console.log(`📖 "${testMyth.title}" 본문 추출 테스트\n`);

  // PDF 경로 찾기
  const page = await context.newPage();
  let pdfBasePath = null;

  page.on('response', response => {
    const url = response.url();
    if (url.includes('.pdf.xml') && !url.includes('.files/')) {
      pdfBasePath = url.replace('.xml', '').replace(/\?.*$/, '');
    }
  });

  await page.goto(testMyth.pdf_url, { waitUntil: 'networkidle', timeout: 60000 });
  await page.close();
  await browser.close();

  if (!pdfBasePath) {
    console.log('   ❌ PDF 경로를 찾을 수 없음');
    return null;
  }

  console.log('   📁 PDF 경로:', pdfBasePath);

  // Node.js로 직접 XML 가져오기
  console.log('\n   📄 XML 파일 직접 다운로드 중...');

  let fullText = '';
  const pdfFileName = path.basename(pdfBasePath);

  for (let pageNum = 1; pageNum <= 20; pageNum++) {
    const xmlUrl = `${pdfBasePath}.files/${pdfFileName}_${pageNum}.xml`;

    try {
      const xmlContent = await fetchXml(xmlUrl);

      if (xmlContent && xmlContent.length > 100) {
        // c="문자" 패턴 추출
        const charMatches = xmlContent.match(/c="([^"]{1,3})"/g);

        if (charMatches && charMatches.length > 0) {
          let pageText = charMatches
            .map(m => {
              const match = m.match(/c="([^"]+)"/);
              return match ? match[1] : '';
            })
            .join('');

          if (pageText.length > 10) {
            fullText += pageText + '\n';
            console.log(`      페이지 ${pageNum}: ${pageText.length}자 - "${pageText.slice(0, 30)}..."`);
          }
        }
      }
    } catch (error) {
      // 404 = 페이지 끝
      if (pageNum > 1) break;
    }
  }

  // 결과
  console.log('\n✅ 추출 완료!');
  console.log(`   총 ${fullText.length}자\n`);

  if (fullText.length > 0) {
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
  } else {
    console.log('⚠️ 텍스트 추출 실패');

    // 디버그: 첫 페이지 XML 원본 확인
    const debugUrl = `${pdfBasePath}.files/${pdfFileName}_1.xml`;
    console.log('\n디버그 URL:', debugUrl);
    try {
      const debugContent = await fetchXml(debugUrl);
      console.log('XML 길이:', debugContent.length);
      console.log('XML 처음 500자:\n', debugContent.slice(0, 500));
    } catch(e) {
      console.log('디버그 실패:', e.message);
    }
  }

  return null;
}

crawlSingleMythContent().catch(console.error);
