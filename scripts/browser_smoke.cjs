// Optional test tool only: resolve an existing Playwright installation through NODE_PATH.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');

(async () => {
  const base = process.env.NARRATIVE_BASE_URL || 'http://127.0.0.1:8000';
  const target = new URL(base);
  assert(['127.0.0.1', 'localhost'].includes(target.hostname), 'Use a local test server');
  const health = await fetch(`${base}/api/health`).then(r => r.json());
  assert(!health.openai_enabled && !health.ollama_enabled, 'Disable external models before browser generation');
  const browser = await chromium.launch();
  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(15000);
    await page.addInitScript(() => { Math.random = () => 0.5; });
    await page.goto(base);
    const pending = page.waitForResponse(r => r.url().endsWith('/api/generate') && r.request().method() === 'POST');
    await page.getByRole('button', { name: '조건 없이 랜덤 설화 설계', exact: true }).click();
    const initial = await (await pending).json();
    assert(initial.generative_story_dna && initial.narrative_blueprint);
    await page.locator('#result').waitFor({ state: 'visible' });
    const candidate = page.locator('.rematch-candidate:not(.is-center-pack)').first();
    const beat = await candidate.getAttribute('data-rematch-beat');
    const id = await candidate.getAttribute('data-rematch-id');
    const remixed = page.waitForResponse(r => r.url().endsWith('/api/generate') && r.request().method() === 'POST');
    await candidate.click();
    const response = await remixed;
    assert.equal(response.status(), 200);
    const body = await response.json();
    assert.equal(body.bound_beats[beat].module_id, id);
    assert(body.active_modules.some(r => r.id === id));
    assert(body.generated.generation_mode.includes('remix'));
    await page.locator('.rematch-candidate.is-selected').first().waitFor({ state: 'visible' });
    console.log(JSON.stringify({ browser: 'chromium', model_requests: 0, applied_beat: beat, module_id: id, result: 'pass' }));
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
