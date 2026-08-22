const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, 'web-crawled');
const BASE_URL = 'https://jeju.go.kr';

async function crawlAllMyths() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const allMyths = [];
  let pageNum = 1;
  let hasMore = true;

  console.log('🚀 제주도청 설화 전체 크롤링 시작...\n');

  // 페이지네이션 크롤링
  while (hasMore && pageNum <= 100) {  // 최대 100페이지
    try {
      const url = `${BASE_URL}/culture/myth/list/all.htm?page=${pageNum}`;
      console.log(`📄 페이지 ${pageNum} 크롤링 중...`);

      await page.goto(url, {
        waitUntil: 'networkidle',
        timeout: 30000
      });

      // 테이블에서 설화 목록 추출
      const myths = await page.$$eval('table tbody tr', rows => {
        return rows.map(row => {
          const cells = row.querySelectorAll('td');
          if (cells.length >= 4) {
            const linkEl = cells[2]?.querySelector('a');
            return {
              category: cells[0]?.innerText?.trim(),
              sub_category: cells[1]?.innerText?.trim(),
              title: cells[2]?.innerText?.trim(),
              region: cells[3]?.innerText?.trim(),
              link: linkEl?.href || null
            };
          }
          return null;
        }).filter(item => item && item.title && item.title !== '제목');
      });

      if (myths.length === 0) {
        console.log(`   ⏹️ 더 이상 데이터 없음\n`);
        hasMore = false;
      } else {
        allMyths.push(...myths);
        console.log(`   ✅ ${myths.length}개 수집 (총 ${allMyths.length}개)\n`);
        pageNum++;
      }

      // 요청 간 딜레이
      await page.waitForTimeout(500);

    } catch (error) {
      console.log(`   ❌ 페이지 ${pageNum} 실패: ${error.message}\n`);
      // 에러 발생시에도 다음 페이지 시도
      pageNum++;
      if (pageNum > 5 && allMyths.length === 0) {
        hasMore = false;  // 5페이지까지 데이터 없으면 종료
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
    source: 'jeju.go.kr',
    total_count: allMyths.length,
    by_category: byCategory,
    all_myths: allMyths
  };

  const outputFile = path.join(OUTPUT_DIR, 'jeju_all_myths.json');
  fs.writeFileSync(outputFile, JSON.stringify(result, null, 2));
  console.log(`💾 저장 완료: ${outputFile}`);

  // 요약
  console.log('\n📊 크롤링 요약:');
  console.log(`   총 설화: ${allMyths.length}개`);
  console.log('\n   카테고리별:');
  Object.entries(byCategory).forEach(([cat, items]) => {
    console.log(`   - ${cat}: ${items.length}개`);
  });

  return result;
}

crawlAllMyths().catch(console.error);
