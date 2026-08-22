const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function extractEbookContent() {
  const browser = await chromium.launch({ headless: false }); // 브라우저 보이게
  const context = await browser.newContext();
  const page = await context.newPage();

  // 작동하는 E-BOOK 링크
  const url = "https://jeju.go.kr/files/ebook/cul-ebook/001/1928/T_F_001/e-book.html";

  console.log('📖 E-BOOK 페이지 분석 중...\n');

  await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });

  // 페이지 구조 분석
  const analysis = await page.evaluate(() => {
    const result = {
      title: document.title,
      iframes: [],
      images: [],
      links: [],
      scripts: []
    };

    // iframe 찾기
    document.querySelectorAll('iframe').forEach(iframe => {
      result.iframes.push({
        src: iframe.src,
        id: iframe.id
      });
    });

    // 이미지 찾기 (E-BOOK은 보통 이미지 기반)
    document.querySelectorAll('img').forEach(img => {
      if (img.src && !img.src.includes('icon')) {
        result.images.push(img.src);
      }
    });

    // 링크 찾기
    document.querySelectorAll('a').forEach(a => {
      if (a.href && a.href.includes('pdf')) {
        result.links.push({ text: a.innerText, href: a.href });
      }
    });

    // 본문 텍스트
    result.bodyText = document.body.innerText?.slice(0, 1000);

    return result;
  });

  console.log('제목:', analysis.title);
  console.log('\niframes:', analysis.iframes);
  console.log('\n이미지 수:', analysis.images.length);
  console.log('이미지 샘플:', analysis.images.slice(0, 5));
  console.log('\nPDF 링크:', analysis.links);
  console.log('\n본문:', analysis.bodyText?.slice(0, 300));

  // 10초 대기 (수동 확인)
  console.log('\n⏳ 10초 대기... 브라우저에서 구조 확인');
  await page.waitForTimeout(10000);

  await browser.close();
}

extractEbookContent().catch(console.error);
