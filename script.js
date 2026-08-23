const workspace = document.querySelector('.workspace');
const inputPanel = document.querySelector('.input-panel');
const generateButton = document.querySelector('#generate-button');
const emptyState = document.querySelector('#empty-state');
const result = document.querySelector('#result');
const resultPanel = document.querySelector('.result-panel');
const errorMessage = document.querySelector('#error-message');
let engineSteps = [];
let currentStep = 0;
let nextButton;
let backButton;
let progressLabel;
let progressFill;

const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;'
}[character]));

const selectedValue = (name) => document.querySelector(`input[name="${name}"]:checked`)?.value || '';

function addStartButtons() {
  const introCopy = document.querySelector('.intro > div');
  const startButton = document.createElement('button');
  startButton.type = 'button';
  startButton.className = 'start-button';
  startButton.textContent = '설화 설계 시작하기 ↗';
  startButton.addEventListener('click', () => {
    workspace.hidden = false;
    startButton.hidden = true;
    randomButton.hidden = true;
    workspace.scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  introCopy.append(startButton);

  const randomButton = document.createElement('button');
  randomButton.type = 'button';
  randomButton.className = 'random-button';
  randomButton.textContent = '조건 없이 랜덤 설화 설계';
  randomButton.addEventListener('click', () => {
    workspace.hidden = false;
    startButton.hidden = true;
    randomButton.hidden = true;
    fillRandomEngine();
    showStep(engineSteps.length - 1);
    workspace.scrollIntoView({ behavior: 'smooth', block: 'start' });
    window.setTimeout(() => generateButton.click(), 250);
  });
  introCopy.append(randomButton);
}

function pickRandom(nodes) {
  const options = [...nodes];
  return options[Math.floor(Math.random() * options.length)];
}

function fillRandomEngine() {
  document.querySelectorAll('.checkin-question').forEach((step) => {
    const radios = step.querySelectorAll('input[type="radio"]');
    if (radios.length) pickRandom(radios).checked = true;
  });
}

function setupWizard() {
  const form = document.querySelector('.checkin-form');
  engineSteps = [...form.querySelectorAll('.checkin-question')];
  const progress = document.createElement('div');
  progress.className = 'checkin-progress';
  progress.innerHTML = '<div class="progress-meta"><span id="progress-label">INTENT 01 / 05</span><span>설화 생성 조건</span></div><div class="progress-track"><i id="progress-fill"></i></div>';
  form.before(progress);

  const nav = document.createElement('div');
  nav.className = 'checkin-nav';
  nav.innerHTML = '<button id="back-button" class="ghost-button" type="button">← 이전</button><button id="next-button" class="primary-button" type="button"><span>다음 조건</span><span>→</span></button>';
  form.after(nav);
  nextButton = nav.querySelector('#next-button');
  backButton = nav.querySelector('#back-button');
  progressLabel = progress.querySelector('#progress-label');
  progressFill = progress.querySelector('#progress-fill');
  generateButton.hidden = true;
  showStep(0);

  nextButton.addEventListener('click', () => {
    if (!engineSteps[currentStep]?.querySelector('input:checked')) {
      errorMessage.textContent = '이야기의 조건을 하나 선택해주세요.';
      return;
    }
    errorMessage.textContent = '';
    showStep(currentStep + 1);
  });
  backButton.addEventListener('click', () => {
    if (currentStep === 0) return;
    errorMessage.textContent = '';
    showStep(currentStep - 1);
  });
}

function showStep(index) {
  const last = engineSteps.length - 1;
  engineSteps.forEach((step, stepIndex) => { step.hidden = stepIndex !== index; });
  currentStep = index;
  progressLabel.textContent = `INTENT ${String(index + 1).padStart(2, '0')} / ${String(engineSteps.length).padStart(2, '0')}`;
  progressFill.style.width = `${((index + 1) / engineSteps.length) * 100}%`;
  backButton.disabled = index === 0;
  nextButton.hidden = index === last;
  generateButton.hidden = index !== last;
}

function collectEngine() {
  return {
    atmosphere: selectedValue('atmosphere'),
    theme: selectedValue('theme'),
    location: selectedValue('location'),
    character: selectedValue('character'),
    ending: selectedValue('ending'),
  };
}

function renderResult(data) {
  workspace.classList.add('completed');
  inputPanel.hidden = true;
  emptyState.hidden = true;
  result.hidden = false;
  document.querySelector('#retrieval-method').textContent = `${data.analysis_method} · ${data.retrieval_method}`;

  const dna = data.generative_story_dna;
  const blueprint = data.narrative_blueprint;
  const dnaLabels = {
    the_question: 'THE QUESTION', the_lack: 'THE LACK', the_cost: 'THE COST', the_irony: 'THE IRONY',
  };
  document.querySelector('#generative-dna').innerHTML = Object.entries(dnaLabels).map(([key, label]) => `
    <div class="dna-item"><span>${label}</span><strong>${escapeHtml(dna[key])}</strong></div>
  `).join('');

  const blueprintFields = [
    ['SOURCE STORY PACK', `${blueprint.source_pack.source_story_title} · ${blueprint.source_pack.beat_coverage}/5 Beat coverage`],
    ['PROTAGONIST', blueprint.protagonist], ['GOAL', blueprint.goal], ['CONFLICT', blueprint.conflict], ['WORLD', blueprint.world],
  ];
  document.querySelector('#blueprint').innerHTML = blueprintFields.map(([label, value]) => `
    <div class="blueprint-card"><span>${label}</span><p>${escapeHtml(value)}</p></div>
  `).join('');
  document.querySelector('#beat-plan').innerHTML = Object.entries(blueprint.beat_plan).map(([beat, purpose], index) => `
    <div class="beat"><b>${String(index + 1).padStart(2, '0')} / ${escapeHtml(beat)}</b><p>${escapeHtml(purpose)}</p></div>
  `).join('');
  document.querySelector('#modules').innerHTML = data.retrieved.map((module) => {
    const source = [module.source_story, module.category].filter(Boolean).join(' · ');
    return `<article class="module"><div class="module-head"><h4>${escapeHtml(module.title)}</h4><span class="module-score">${module.score}</span></div><div class="module-source">${escapeHtml(source)}</div><p>${escapeHtml(module.text)}</p><div class="module-tags">${escapeHtml(module.beat)} · ${escapeHtml(module.match_reason || 'source resonance')}</div></article>`;
  }).join('');

  const controls = data.generated.controls;
  document.querySelector('#generated-controls').textContent = `${controls.location} · ${controls.mood} · ${controls.tone} · ${controls.ending} · ${data.generated.generation_mode}`;
  document.querySelector('#generated-title').textContent = data.generated.title;
  document.querySelector('#generated-text').textContent = data.generated.text;
  if (!document.querySelector('#restart-button')) {
    const restartButton = document.createElement('button');
    restartButton.id = 'restart-button';
    restartButton.type = 'button';
    restartButton.className = 'ghost-button restart-button';
    restartButton.textContent = '새 설화 설계';
    restartButton.addEventListener('click', resetEngine);
    document.querySelector('.result-header').append(restartButton);
  }
  resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetEngine() {
  workspace.classList.remove('completed');
  inputPanel.hidden = false;
  emptyState.hidden = false;
  result.hidden = true;
  document.querySelectorAll('input[type="radio"]').forEach((input) => { input.checked = false; });
  errorMessage.textContent = '';
  generateButton.hidden = true;
  showStep(0);
  workspace.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

generateButton.addEventListener('click', async () => {
  errorMessage.textContent = '';
  generateButton.disabled = true;
  generateButton.querySelector('span:first-child').textContent = 'Story DNA 설계 중...';
  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ engine: collectEngine(), context: {} }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '설화 설계에 실패했습니다.');
    renderResult(data);
  } catch (error) {
    errorMessage.textContent = error.message.includes('Failed to fetch') ? '먼저 python app.py로 로컬 서버를 실행해주세요.' : error.message;
  } finally {
    generateButton.disabled = false;
    generateButton.querySelector('span:first-child').textContent = '설화 설계하기';
  }
});

addStartButtons();
setupWizard();
