const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const OUTPUT_DIR = path.join(__dirname, 'web-crawled');
const BASE_URL = 'https://jeju.go.kr';

// 크롤링할 카테고리
const CATEGORIES = [
  { name: '개벽신화', url: '/culture/myth/mythInfo/beganMyth.htm' },
  { name: '개국신화', url: '/culture/myth/mythInfo/openMyth.htm' },
  { name: '일반신화', url: '/culture/myth/mythInfo/generalMyth.htm' },
  { name: '당신화', url: '/culture/myth/mythInfo/villageMyths.htm' },
  { name: '전체목록', url: '/culture/myth/list/all.htm' }
];

// 애니메이션 설화 (상세 페이지 있음)
const ANIMATION_LEGENDS = [
  { name: '자청비', url: '/culture/myth/legend/legend01.htm' },
  { name: '고종달이와 제주의혈', url: '/culture/myth/legend/legend02.htm' },
  { name: '오백장군 이야기', url: '/culture/myth/legend/legend03.htm' },
  { name: '유반석과 무반석', url: '/culture/myth/legend/legend04.htm' },
  { name: '비양도', url: '/culture/myth/legend/legend05.htm' },
  { name: '대림선돌', url: '/culture/myth/legend/legend06.htm' },
  { name: '당산봉 삼반석', url: '/culture/myth/legend/legend07.htm' },
  { name: '좌랑못', url: '/culture/myth/legend/legend08.htm' },
  { name: '절부암', url: '/culture/myth/legend/legend09.htm' },
  { name: '막산이구석', url: '/culture/myth/legend/legend10.htm' },
  { name: '수월봉', url: '/culture/myth/legend/legend11.htm' },
  { name: '명월천', url: '/culture/myth/legend/legend13.htm' },
  { name: '김녕사굴', url: '/culture/myth/legend/legend14.htm' }
];

async function crawlJejuMyths() {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const allData = {
    crawled_at: new Date().toISOString(),
    source: 'jeju.go.kr',
    categories: {},
    legends: []
  };

  console.log('🚀 제주도청 설화 크롤링 시작...\n');

  // 1. 전체 목록 크롤링
  console.log('📋 전체 목록 크롤링 중...');
  try {
    await page.goto(BASE_URL + '/culture/myth/list/all.htm', {
      waitUntil: 'networkidle',
      timeout: 60000
    });

    // 테이블에서 설화 목록 추출
    const mythList = await page.$$eval('table tbody tr', rows => {
      return rows.map(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 4) {
          return {
            category: cells[0]?.innerText?.trim(),
            sub_category: cells[1]?.innerText?.trim(),
            title: cells[2]?.innerText?.trim(),
            region: cells[3]?.innerText?.trim(),
            link: cells[2]?.querySelector('a')?.href || null
          };
        }
        return null;
      }).filter(item => item && item.title);
    });

    allData.myth_list = mythList;
    console.log(`   ✅ ${mythList.length}개 설화 목록 수집\n`);

    // 목록 저장
    fs.writeFileSync(
      path.join(OUTPUT_DIR, 'jeju_myth_list.json'),
      JSON.stringify(mythList, null, 2)
    );

  } catch (error) {
    console.log(`   ❌ 전체 목록 크롤링 실패: ${error.message}\n`);
  }

  // 2. 애니메이션 설화 상세 크롤링 (스토리 내용 있음)
  console.log('📖 애니메이션 설화 상세 크롤링 중...');
  for (const legend of ANIMATION_LEGENDS) {
    try {
      console.log(`   📥 ${legend.name}...`);
      await page.goto(BASE_URL + legend.url, {
        waitUntil: 'networkidle',
        timeout: 30000
      });

      // 상세 내용 추출
      const content = await page.$$eval('.content, .story-content, .view-content, article, .bbs-view', elements => {
        return elements.map(el => el.innerText?.trim()).filter(t => t && t.length > 50).join('\n\n');
      });

      // 본문 영역 찾기 (다양한 선택자 시도)
      let storyContent = content;
      if (!storyContent || storyContent.length < 100) {
        storyContent = await page.$eval('body', el => {
          // 메인 콘텐츠 영역 찾기
          const main = el.querySelector('main, #content, .content-wrap, .sub-content');
          return main ? main.innerText?.trim() : el.innerText?.trim();
        });
      }

      allData.legends.push({
        name: legend.name,
        url: BASE_URL + legend.url,
        content: storyContent?.slice(0, 5000) || '내용 추출 실패'
      });

      console.log(`      ✅ ${storyContent?.length || 0}자 수집`);

    } catch (error) {
      console.log(`      ❌ 실패: ${error.message}`);
      allData.legends.push({
        name: legend.name,
        url: BASE_URL + legend.url,
        content: null,
        error: error.message
      });
    }
  }

  // 3. 카테고리별 신화 목록 크롤링
  console.log('\n📂 카테고리별 신화 크롤링 중...');
  for (const cat of CATEGORIES.slice(0, 4)) {  // 전체목록 제외
    try {
      console.log(`   📥 ${cat.name}...`);
      await page.goto(BASE_URL + cat.url, {
        waitUntil: 'networkidle',
        timeout: 30000
      });

      const categoryContent = await page.$eval('body', el => {
        const main = el.querySelector('main, #content, .content-wrap, .sub-content, .bbs-list');
        return main ? main.innerText?.trim() : '';
      });

      allData.categories[cat.name] = {
        url: BASE_URL + cat.url,
        content: categoryContent?.slice(0, 10000) || ''
      };

      console.log(`      ✅ ${categoryContent?.length || 0}자 수집`);

    } catch (error) {
      console.log(`      ❌ 실패: ${error.message}`);
    }
  }

  await browser.close();

  // 결과 저장
  const outputFile = path.join(OUTPUT_DIR, 'jeju_gov_myths.json');
  fs.writeFileSync(outputFile, JSON.stringify(allData, null, 2));
  console.log(`\n💾 저장 완료: ${outputFile}`);

  // 요약
  console.log('\n📊 크롤링 요약:');
  console.log(`   - 설화 목록: ${allData.myth_list?.length || 0}개`);
  console.log(`   - 상세 설화: ${allData.legends.length}개`);
  console.log(`   - 카테고리: ${Object.keys(allData.categories).length}개`);

  return allData;
}

crawlJejuMyths().catch(console.error);
