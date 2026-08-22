const { chromium } = require('playwright');

async function extractPdfUrl() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // PDF 뷰어 페이지
  const url = "https://jeju.go.kr/tool/synap/convert.jsp?seq=1041615&no=1";

  console.log('📄 PDF 뷰어 페이지 분석 중...\n');

  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });

  // 페이지 구조 분석
  const analysis = await page.evaluate(() => {
    const result = {
      title: document.title,
      iframes: [],
      embeds: [],
      objects: [],
      links: [],
      bodyHtml: document.body.innerHTML?.slice(0, 2000)
    };

    // iframe 찾기
    document.querySelectorAll('iframe').forEach(iframe => {
      result.iframes.push({ src: iframe.src, id: iframe.id });
    });

    // embed 태그 찾기
    document.querySelectorAll('embed').forEach(embed => {
      result.embeds.push({ src: embed.src, type: embed.type });
    });

    // object 태그 찾기
    document.querySelectorAll('object').forEach(obj => {
      result.objects.push({ data: obj.data, type: obj.type });
    });

    // 모든 링크에서 pdf 관련 찾기
    document.querySelectorAll('a[href*="pdf"], a[href*="download"]').forEach(a => {
      result.links.push({ text: a.innerText, href: a.href });
    });

    return result;
  });

  console.log('제목:', analysis.title);
  console.log('\niframes:', analysis.iframes);
  console.log('\nembeds:', analysis.embeds);
  console.log('\nobjects:', analysis.objects);
  console.log('\nPDF 링크:', analysis.links);
  console.log('\nHTML 일부:', analysis.bodyHtml?.slice(0, 500));

  // 네트워크 요청 모니터링
  console.log('\n🔍 네트워크 요청 확인 중...');

  page.on('response', response => {
    const url = response.url();
    if (url.includes('pdf') || url.includes('download') || url.includes('file')) {
      console.log('   발견:', url);
    }
  });

  // 페이지 새로고침하면서 네트워크 요청 캡처
  await page.reload({ waitUntil: 'networkidle' });

  console.log('\n⏳ 10초 대기...');
  await page.waitForTimeout(10000);

  await browser.close();
}

extractPdfUrl().catch(console.error);
