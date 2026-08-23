const sampleStory = '제주 바닷가 마을에는 밤마다 검은 파도 속에서 빛나는 돌이 나타난다는 이야기가 전해졌다. 어느 날 한 소녀가 사라진 할머니의 약속을 찾기 위해 해안으로 향했다. 하지만 폭풍이 갑자기 몰려오며 바다는 소녀 앞의 길을 닫아버렸다. 소녀는 빛나는 돌을 들어 올려 바다와 마주했고, 다음 날 마을에는 조용한 물결이 돌아왔다.';
const workspace = document.querySelector('.workspace');
const inputPanel = document.querySelector('.input-panel');
const storyInput = document.querySelector('#story-input');
const generateButton = document.querySelector('#generate-button');
const sampleButton = document.querySelector('#sample-button');
const emptyState = document.querySelector('#empty-state');
const result = document.querySelector('#result');
const resultPanel = document.querySelector('.result-panel');
const errorMessage = document.querySelector('#error-message');
const assessmentText = document.querySelector('#assessment-text');
let checkinSteps = [];
let currentStep = 0;
let nextButton;
let backButton;
let progressLabel;
let progressFill;

const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;'
}[character]));

const selectedValue = (name) => document.querySelector(`input[name="${name}"]:checked`)?.value || '';
const selectedValues = (name) => [...document.querySelectorAll(`input[name="${name}"]:checked`)].map((node) => node.value);

function addStartButton() {
  const introCopy = document.querySelector('.intro > div');
  const startButton = document.createElement('button');
  startButton.type = 'button';
  startButton.className = 'start-button';
  startButton.textContent = '지금의 장면 바라보기 ↗';
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
  randomButton.textContent = '선택 없이 랜덤 이야기 생성';
  randomButton.addEventListener('click', () => {
    workspace.hidden = false;
    startButton.hidden = true;
    randomButton.hidden = true;
    fillRandomCheckin();
    showStep(checkinSteps.length - 1);
    workspace.scrollIntoView({ behavior: 'smooth', block: 'start' });
    window.setTimeout(() => generateButton.click(), 250);
  });
  introCopy.append(randomButton);
}

function pickRandom(nodes) {
  const options = [...nodes];
  return options[Math.floor(Math.random() * options.length)];
}

function fillRandomCheckin() {
  document.querySelectorAll('.checkin-question:not(.free-text-step)').forEach((step) => {
    const radios = step.querySelectorAll('input[type="radio"]');
    const checkboxes = step.querySelectorAll('input[type="checkbox"]');
    if (radios.length) pickRandom(radios).checked = true;
    if (checkboxes.length) {
      const count = Math.random() > 0.65 ? 2 : 1;
      [...checkboxes].sort(() => Math.random() - 0.5).slice(0, count).forEach((input) => { input.checked = true; });
    }
  });
  document.querySelectorAll('.controls select').forEach((select) => {
    const option = pickRandom(select.options);
    select.value = option.value;
  });
  storyInput.value = '';
}

function setupWizard() {
  const checkinForm = document.querySelector('.checkin-form');
  const freeLabel = storyInput.previousElementSibling;
  const controls = document.querySelector('.controls');
  const freeStep = document.createElement('div');
  freeStep.className = 'checkin-question free-text-step';
  freeStep.innerHTML = '<legend>아직 선택지 안에 없었던 이야기가 있나요?</legend><p class="question-hint">비워두어도 괜찮아요. 오늘의 나에게 제목을 붙이거나, 설명하지 못했던 한 문장을 적어보세요.</p>';
  freeStep.append(freeLabel, storyInput, controls);
  checkinForm.append(freeStep);
  checkinSteps = [...checkinForm.querySelectorAll('.checkin-question')];

  const progress = document.createElement('div');
  progress.className = 'checkin-progress';
  progress.innerHTML = '<div class="progress-meta"><span id="progress-label">SCENE 01 / 11</span><span>진단이 아닌 장면 바라보기</span></div><div class="progress-track"><i id="progress-fill"></i></div>';
  checkinForm.before(progress);

  const nav = document.createElement('div');
  nav.className = 'checkin-nav';
  nav.innerHTML = '<button id="back-button" class="ghost-button" type="button">← 이전</button><button id="next-button" class="primary-button" type="button"><span>다음 장면</span><span>→</span></button>';
  checkinForm.after(nav);
  nextButton = nav.querySelector('#next-button');
  backButton = nav.querySelector('#back-button');
  progressLabel = progress.querySelector('#progress-label');
  progressFill = progress.querySelector('#progress-fill');

  generateButton.hidden = true;
  showStep(0);

  nextButton.addEventListener('click', () => {
    if (!hasAnswer(checkinSteps[currentStep])) {
      errorMessage.textContent = '이 장면에 가까운 선택지를 하나 골라주세요.';
      return;
    }
    errorMessage.textContent = '';
    currentStep += 1;
    showStep(currentStep);
  });
  backButton.addEventListener('click', () => {
    if (currentStep === 0) return;
    errorMessage.textContent = '';
    currentStep -= 1;
    showStep(currentStep);
  });
}

function hasAnswer(step) {
  if (!step || step.classList.contains('free-text-step')) return true;
  return Boolean(step.querySelector('input:checked'));
}

function showStep(index) {
  const last = checkinSteps.length - 1;
  checkinSteps.forEach((step, stepIndex) => { step.hidden = stepIndex !== index; });
  currentStep = index;
  progressLabel.textContent = `SCENE ${String(index + 1).padStart(2, '0')} / ${String(checkinSteps.length).padStart(2, '0')}`;
  progressFill.style.width = `${((index + 1) / checkinSteps.length) * 100}%`;
  backButton.disabled = index === 0;
  nextButton.hidden = index === last;
  generateButton.hidden = index !== last;
}

function collectSurvey() {
  return {
    scene: selectedValue('scene'),
    weather: selectedValues('weather'),
    destination: selectedValue('destination'),
    landscape: selectedValue('landscape'),
    time: selectedValue('time'),
    speed: selectedValue('speed'),
    release: selectedValue('release'),
    carry: selectedValue('carry'),
    companion: selectedValue('companion'),
    glimpse: selectedValue('glimpse'),
  };
}

function renderResult(data) {
  workspace.classList.add('completed');
  inputPanel.hidden = true;
  emptyState.hidden = true;
  result.hidden = false;
  document.querySelector('#retrieval-method').textContent = `${data.analysis_method || 'rule-based fallback'} · ${data.retrieval_method || 'story module resonance'}`;
  const context = data.analysis.personal_context || {
    summary: '선택한 장면으로 구성한 이야기',
    setting: data.generated?.controls?.location || data.analysis.dna?.setting?.[0] || '제주',
    wounds: [],
    desires: [],
  };
  const displayWounds = context.wounds_display || context.wounds || [];
  const displayDesires = context.desires_display || context.desires || [];
  document.querySelector('#context-summary').textContent = `상황 요약 · ${context.summary} / 장소 · ${context.setting} / 심리적 부담 · ${displayWounds.join(' · ')} / 현재의 욕구 · ${displayDesires.join(' · ')}`;
  assessmentText.textContent = data.analysis.personal_assessment || [
    '[NARRATIVE ASSESSMENT v1]',
    '비임상적 서사 자기평가',
    '',
    `현재 장면: ${context.summary}`,
    `정서적 기후: ${context.emotions?.join(' · ') || '아직 확인되지 않음'}`,
    `심리적 부담: ${displayWounds.join(' · ') || '아직 확인되지 않음'}`,
    `현재의 욕구: ${displayDesires.join(' · ') || '아직 확인되지 않음'}`,
    `내적 긴장: ${context.conflict || '현재의 장면과 원하는 변화 사이의 간극'}`,
    '',
    '이 결과는 진단이 아니라 입력한 이야기를 다시 바라보기 위한 서사적 정리입니다.',
  ].join('\n');

  if (!document.querySelector('#download-assessment')) {
    const downloadButton = document.createElement('button');
    downloadButton.id = 'download-assessment';
    downloadButton.type = 'button';
    downloadButton.className = 'ghost-button';
    downloadButton.textContent = 'SAVE .TXT ↗';
    downloadButton.addEventListener('click', () => {
      const blob = new Blob([assessmentText.textContent], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `narrative-assessment-v1-${new Date().toISOString().slice(0, 10)}.txt`;
      link.click();
      URL.revokeObjectURL(url);
    });
    document.querySelector('.assessment-section .result-section-title').append(downloadButton);
  }

  const evidence = data.analysis.assessment_evidence;
  if (evidence && !document.querySelector('#assessment-evidence')) {
    const evidenceSection = document.createElement('section');
    const renderEvidenceList = (items) => items?.length
      ? `<ul class="evidence-list">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>`
      : '<p class="evidence-empty">확인된 입력 신호가 없습니다.</p>';
    evidenceSection.id = 'assessment-evidence';
    evidenceSection.className = 'result-section evidence-section';
    evidenceSection.innerHTML = `
      <div class="result-section-title"><span>EVIDENCE</span><h3>WHY THIS RESULT?</h3></div>
      <p class="evidence-method">${escapeHtml(evidence.input_mode)} · ${escapeHtml(evidence.method)}</p>
      <div class="evidence-grid">
        <div class="evidence-card"><strong>TXT 단서</strong>${renderEvidenceList(evidence.text_signals)}</div>
        <div class="evidence-card"><strong>Check-in 신호</strong>${renderEvidenceList(evidence.checkin_signals)}</div>
        <div class="evidence-card"><strong>도출된 해석</strong>${renderEvidenceList(evidence.derived_signals)}</div>
      </div>`;
    document.querySelector('.assessment-section').after(evidenceSection);
  }

  const dnaLabels = { setting: 'SETTING', characters: 'CHARACTERS', emotion: 'EMOTION', conflict: 'CONFLICT', beats: 'BEATS' };
  document.querySelector('#dna-grid').innerHTML = Object.entries(dnaLabels).map(([key, label]) => `
    <div class="dna-item"><span>${label}</span><strong>${escapeHtml(data.analysis.dna[key].join(' · '))}</strong></div>
  `).join('');

  document.querySelector('#beats').innerHTML = data.analysis.beats.map((beat) => `
    <div class="beat"><b>${String(beat.index).padStart(2, '0')} / ${escapeHtml(beat.type)}</b><p>${escapeHtml(beat.text)}<small>${escapeHtml(beat.role)}</small></p></div>
  `).join('');

  document.querySelector('#modules').innerHTML = data.retrieved.map((module) => {
    const source = [module.source_story, module.category].filter(Boolean).join(' · ');
    const supporting = (module.supporting_modules || []).slice(0, 4).join(' · ');
    return `
      <article class="module"><div class="module-head"><h4>${escapeHtml(module.title)}</h4><span class="module-score">${module.score}</span></div><div class="module-source">${escapeHtml(source)}</div><p>${escapeHtml(module.text)}</p><div class="module-tags">${escapeHtml(module.beat)} · ${escapeHtml(module.match_reason || module.matched_terms.join(' · ') || 'context match')}</div>${supporting ? `<div class="module-support">MODULES · ${escapeHtml(supporting)}</div>` : ''}</article>
    `;
  }).join('');

  const controls = data.generated.controls;
  document.querySelector('#generated-controls').textContent = `${controls.location} · ${controls.mood} · ${controls.tone} · ${controls.ending}`;
  document.querySelector('#generated-title').textContent = data.generated.title;
  document.querySelector('#generated-text').textContent = data.generated.text;

  if (!document.querySelector('#restart-button')) {
    const restartButton = document.createElement('button');
    restartButton.id = 'restart-button';
    restartButton.type = 'button';
    restartButton.className = 'ghost-button restart-button';
    restartButton.textContent = '새 장면 시작';
    restartButton.addEventListener('click', resetWizard);
    document.querySelector('.result-header').append(restartButton);
  }
  resultPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function resetWizard() {
  workspace.classList.remove('completed');
  inputPanel.hidden = false;
  emptyState.hidden = false;
  result.hidden = true;
  currentStep = 0;
  document.querySelectorAll('input[type="radio"], input[type="checkbox"]').forEach((input) => { input.checked = false; });
  storyInput.value = '';
  generateButton.hidden = true;
  showStep(0);
  workspace.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

sampleButton.addEventListener('click', () => {
  storyInput.value = sampleStory;
  currentStep = checkinSteps.length - 1;
  showStep(currentStep);
  storyInput.focus();
});

generateButton.addEventListener('click', async () => {
  errorMessage.textContent = '';
  generateButton.disabled = true;
  generateButton.querySelector('span:first-child').textContent = '장면을 펼치는 중...';
  try {
    const freeText = storyInput.value.trim();
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        // Survey answers are the actual input when the optional free-text box is empty.
        // The short fallback also keeps the client compatible with an older local server.
        story: freeText || '선택한 장면을 따라 새로운 이야기를 시작합니다.',
        survey: collectSurvey(),
        context: {
          location: document.querySelector('#location').value,
          mood: document.querySelector('#mood').value,
          tone: document.querySelector('#tone').value,
          ending: document.querySelector('#ending').value,
        },
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '분석에 실패했습니다.');
    renderResult(data);
  } catch (error) {
    errorMessage.textContent = error.message.includes('Failed to fetch') ? '먼저 python app.py로 로컬 서버를 실행해주세요.' : error.message;
  } finally {
    generateButton.disabled = false;
    generateButton.querySelector('span:first-child').textContent = '이야기 계속하기';
  }
});

addStartButton();
setupWizard();
