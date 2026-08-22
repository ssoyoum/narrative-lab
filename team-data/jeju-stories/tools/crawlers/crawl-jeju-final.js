const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, 'web-crawled');
const BASE_URL = 'https://jeju.go.kr';

async function crawlJejuMythsFinal() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const allMyths = [];
  let pageNum = 1;
  let hasMore = true;

  console.log('🚀 제주도청 설화 전체 크롤링 시작 (수정된 버전)...\n');

  while (hasMore && pageNum <= 100) {
    try {
      const url = `${BASE_URL}/culture/myth/list/all.htm?page=${pageNum}`;
      console.log(`📄 페이지 ${pageNum} 크롤링 중...`);

      await page.goto(url, {
        waitUntil: 'networkidle',
        timeout: 30000
      });

      // 정확한 테이블 구조로 파싱
      // 헤더: No., 형태, 대분류, 중분류, 코드번호, 설화명, E-BOOK, PDF
      const myths = await page.$$eval('table tbody tr', rows => {
        return rows.map(row => {
          const cells = row.querySelectorAll('td');
          if (cells.length >= 8) {
            return {
              no: cells[0]?.innerText?.trim(),
              type: cells[1]?.innerText?.trim(),           // 형태 (원문)
              category: cells[2]?.innerText?.trim(),       // 대분류 (신화/전설/민담)
              sub_category: cells[3]?.innerText?.trim(),   // 중분류
              code: cells[4]?.innerText?.trim(),           // 코드번호
              title: cells[5]?.innerText?.trim(),          // 설화명
              ebook_url: cells[6]?.querySelector('a')?.href || null,
              pdf_url: cells[7]?.querySelector('a')?.href || null
            };
          }
          return null;
        }).filter(item => item && item.title && item.title !== '설화명');
      });

      if (myths.length === 0) {
        console.log(`   ⏹️ 더 이상 데이터 없음\n`);
        hasMore = false;
      } else {
        allMyths.push(...myths);
        console.log(`   ✅ ${myths.length}개 수집 (총 ${allMyths.length}개)\n`);
        pageNum++;
      }

      await page.waitForTimeout(300);

    } catch (error) {
      console.log(`   ❌ 페이지 ${pageNum} 실패: ${error.message}\n`);
      pageNum++;
      if (pageNum > 5 && allMyths.length === 0) {
        hasMore = false;
      }
    }
  }

  await browser.close();

  // 카테고리별 분류
  const byCategory = {};
  allMyths.forEach(myth => {
    const cat = myth.category || '기타';
    if (!byCategory[cat]) byCategory[cat] = [];
    byCategory[cat].push(myth);
  });

  // 결과 저장
  const result = {
    crawled_at: new Date().toISOString(),
    source: 'jeju.go.kr/culture/myth/list/all.htm',
    total_count: allMyths.length,
    categories_summary: Object.entries(byCategory).map(([k, v]) => ({ category: k, count: v.length })),
    by_category: byCategory,
    all_myths: allMyths
  };

  const outputFile = path.join(OUTPUT_DIR, 'jeju_myths_complete.json');
  fs.writeFileSync(outputFile, JSON.stringify(result, null, 2));
  console.log(`💾 저장 완료: ${outputFile}`);

  // 요약
  console.log('\n📊 크롤링 요약:');
  console.log(`   총 설화: ${allMyths.length}개`);
  console.log('\n   카테고리별:');
  result.categories_summary.forEach(({ category, count }) => {
    console.log(`   - ${category}: ${count}개`);
  });

  // PDF 링크가 있는 설화 수
  const withPdf = allMyths.filter(m => m.pdf_url).length;
  const withEbook = allMyths.filter(m => m.ebook_url).length;
  console.log(`\n   E-BOOK 링크: ${withEbook}개`);
  console.log(`   PDF 링크: ${withPdf}개`);

  return result;
}

crawlJejuMythsFinal().catch(console.error);
