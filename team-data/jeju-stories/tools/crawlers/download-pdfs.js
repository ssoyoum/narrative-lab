const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const DOWNLOAD_DIR = path.join(__dirname, 'pdf-downloads');

// PDF 다운로드 목록
const PDF_SOURCES = [
  {
    name: '제주도_설화_연구',
    url: 'https://oak.jejunu.ac.kr/bitstream/2020.oak/5353/2/제주도%20설화%20연구.pdf'
  },
  {
    name: '제주_설화의_생태학적_인식',
    url: 'https://oak.jejunu.ac.kr/bitstream/2020.oak/18090/2/제주%20설화의%20생태학적%20인식.pdf'
  },
  {
    name: '천지왕본풀이_의례적_기능과_신화적_의미',
    url: 'https://oak.jejunu.ac.kr/bitstream/2020.oak/5299/2/천지왕본풀이의%20의례적%20기능과%20신화적%20의미.pdf'
  },
  {
    name: '제주_사료와_설화_속의_중국',
    url: 'https://jri.re.kr/contents/index.php?file_path=/periodical/4f9f91634b35b.pdf&job=download&mid=040905'
  }
];

async function downloadPDFs() {
  // 다운로드 폴더 확인
  if (!fs.existsSync(DOWNLOAD_DIR)) {
    fs.mkdirSync(DOWNLOAD_DIR, { recursive: true });
  }

  const browser = await chromium.launch({
    headless: true
  });

  console.log('🚀 PDF 다운로드 시작...\n');

  for (const source of PDF_SOURCES) {
    try {
      console.log(`📥 다운로드 중: ${source.name}`);

      // 각 다운로드마다 새 context 생성 (다운로드 경로 지정)
      const context = await browser.newContext({
        acceptDownloads: true
      });

      const page = await context.newPage();

      // 다운로드 이벤트 먼저 등록
      const downloadPromise = page.waitForEvent('download', { timeout: 60000 });

      // 페이지 이동 시도 (에러 무시 - 다운로드 시작되면 에러 발생함)
      page.goto(source.url, { timeout: 60000 }).catch(() => {});

      // 다운로드 완료 대기
      const download = await downloadPromise;

      // 파일 저장
      const filePath = path.join(DOWNLOAD_DIR, `${source.name}.pdf`);
      await download.saveAs(filePath);
      console.log(`   ✅ 저장됨: ${filePath}\n`);

      await context.close();
    } catch (error) {
      console.log(`   ❌ 실패: ${source.name} - ${error.message}\n`);
    }
  }

  await browser.close();
  console.log('🎉 다운로드 완료!');

  // 결과 확인
  const files = fs.readdirSync(DOWNLOAD_DIR).filter(f => f.endsWith('.pdf'));
  console.log(`\n📁 다운로드된 파일 (${files.length}개):`);
  files.forEach(f => console.log(`   - ${f}`));
}

downloadPDFs().catch(console.error);
