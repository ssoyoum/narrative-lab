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
let selectedOverrides = {};

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

function renderMatchReport(report) {
  const isRemix = report?.mode === 'cross-story remix';
  const dimensions = report?.dimensions || [];
  const stats = report?.statistics || {};
  const candidates = report?.top_candidates || [];
  const terms = report?.matched_terms || [];
  document.querySelector('#match-report').innerHTML = `
    <div class="match-summary">
      <div class="fit-score"><strong>${escapeHtml(report?.overall_score || 0)}</strong><span>/ 100</span></div>
      <div><p class="fit-label">${isRemix ? 'CROSS-STORY REMIX FIT' : 'OVERALL STORY PACK FIT'} · ${escapeHtml(report?.grade || '측정 중')}</p><p class="fit-description">${isRemix ? '사용자가 선택한 Beat 후보를 반영한 리믹스 결과입니다. 원천 혼합은 감점이 아니라 이 모드의 의도입니다.' : '선택한 조건과 생성용 DNA를 기준으로 가장 구조적으로 호환되는 원천 설화를 선택했습니다.'}</p></div>
    </div>
    <div class="match-dimensions">${dimensions.map((item) => `
      <div class="match-dimension"><div class="dimension-head"><span>${escapeHtml(item.label)}</span><strong>${escapeHtml(item.score)}%</strong></div><div class="dimension-track"><i style="width:${Math.max(0, Math.min(100, Number(item.score) || 0))}%"></i></div><p>${escapeHtml(item.detail)}</p></div>
    `).join('')}</div>
    <div class="match-detail-grid">
      <div class="match-detail"><span>MATCHED TERMS</span><p>${terms.length ? terms.map(escapeHtml).join(' · ') : '직접 겹치는 핵심어 없음 · 구조 점수로 보완'}</p></div>
      <div class="match-detail"><span>RETRIEVAL STATISTICS</span><p>후보 설화 ${escapeHtml(stats.candidate_stories || 0)}개 · 모듈 ${escapeHtml(stats.retrieved_modules || 0)}개 · 바인딩 Beat ${escapeHtml(stats.bound_beats || 0)}개${isRemix ? ` · 리믹스 Beat ${escapeHtml(stats.remix_beats || 0)}개` : ''}</p></div>
    </div>
    <div class="candidate-list"><span class="candidate-title">TOP CANDIDATES</span>${candidates.map((item, index) => `
      <div class="candidate-row"><b>${String(index + 1).padStart(2, '0')}</b><span>${escapeHtml(item.source_story_title)}</span><em>${escapeHtml(item.fit_score)}% · ${escapeHtml(item.beat_coverage)} Beat</em></div>
    `).join('')}</div>
    <p class="match-method-note">선택 기준: ${escapeHtml(report?.selection_rule || '')}<br />${escapeHtml(report?.method_note || '')}<br />데이터셋: 설화 ${escapeHtml(stats.dataset_stories || 0)}개 · Beat ${escapeHtml(stats.dataset_beats || 0)}개 · 모듈 ${escapeHtml(stats.dataset_modules || 0)}개</p>
  `;
}

function renderBeatRecommendations(recommendations, sourcePack) {
  const entries = Object.entries(recommendations || {});
  document.querySelector('#beat-recommendations').innerHTML = entries.map(([beat, item]) => `
    <article class="beat-rematch-card">
      <div class="rematch-head"><b>${escapeHtml(beat)}</b><span>DNA · ${escapeHtml(item.dna_focus || 'blueprint')}</span></div>
      <div class="rematch-candidates">${(item.candidates || []).map((candidate) => `
        <button type="button" class="rematch-candidate ${candidate.source_story_id === sourcePack?.source_story_id ? 'is-center-pack' : ''} ${candidate.selected ? 'is-selected' : ''}" data-rematch-beat="${escapeHtml(beat)}" data-rematch-id="${escapeHtml(candidate.module_id)}" onclick="window.applyBeatRematch('${escapeHtml(beat)}', '${escapeHtml(candidate.module_id)}'); return false;">
          <div class="rematch-candidate-head"><strong>${escapeHtml(candidate.source_story)}</strong><em>${escapeHtml(candidate.fit_score)}%</em></div>
          <p>${escapeHtml(candidate.event_text)}</p>
          <small>${candidate.source_story_id === sourcePack?.source_story_id ? '현재 생성에 사용된 중심 Story Pack' : '재매칭 후보'} · 원점수 ${escapeHtml(candidate.score)}${candidate.matched_terms?.length ? ` · ${escapeHtml(candidate.matched_terms.join(' · '))}` : ''}</small><span class="rematch-apply">${candidate.selected ? '현재 적용됨 ✓' : '이 후보 적용 ↗'}</span>
        </button>
      `).join('')}</div>
    </article>
  `).join('') || '<p class="rematch-empty">이 Beat에 대한 별도 후보가 없습니다.</p>';
}

async function applyBeatRematch(beat, moduleId) {
  const status = document.querySelector('#rematch-status');
  const buttons = document.querySelectorAll('[data-rematch-beat]');
  buttons.forEach((button) => { button.disabled = true; });
  if (status) status.textContent = `${beat} 후보를 적용해 이야기를 다시 매칭하는 중...`;
  selectedOverrides = { ...selectedOverrides, [beat]: moduleId };
  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ engine: collectEngine(), context: {}, beat_overrides: selectedOverrides }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Beat 재매칭에 실패했습니다.');
    renderResult(data);
  } catch (error) {
    if (status) status.textContent = error.message;
    buttons.forEach((button) => { button.disabled = false; });
  }
}
window.applyBeatRematch = applyBeatRematch;

function renderResult(data) {
  workspace.classList.add('completed');
  inputPanel.hidden = true;
  emptyState.hidden = true;
  result.hidden = false;
  selectedOverrides = data.remix?.selected_overrides || selectedOverrides;
  document.querySelector('#retrieval-method').textContent = `${data.analysis_method} · ${data.retrieval_method}`;

  const dna = data.generative_story_dna;
  const blueprint = data.narrative_blueprint;
  const dnaLabels = {
    the_question: 'THE QUESTION', the_lack: 'THE LACK', the_cost: 'THE COST', the_irony: 'THE IRONY',
  };
  const intentLabels = { atmosphere: '분위기', theme: '주제', location: '장소', character: '인물', ending: '결말' };
  const userIntent = dna.user_intent || {};
  document.querySelector('#generative-dna').innerHTML = '<div class="dna-intro">GENERATIVE DNA<br /><span>사용자 선택으로 설계된 생성용 제약 · 후보 설화가 바뀌어도 이번 요청에서는 유지됩니다.</span></div><div class="intent-grid">' + Object.entries(intentLabels).map(([key, label]) => `
    <div class="intent-item"><span>${label}</span><strong>${escapeHtml(userIntent[key] || '')}</strong></div>
  `).join('') + '</div>' + Object.entries(dnaLabels).map(([key, label]) => `
    <div class="dna-item"><span>${label}</span><strong>${escapeHtml(dna[key])}</strong></div>
  `).join('');
  renderMatchReport(data.match_report);
  renderBeatRecommendations(data.beat_recommendations, blueprint.source_pack);
  const remixStatus = document.querySelector('#remix-status');
  if (remixStatus) remixStatus.textContent = data.remix?.active ? `현재 ${data.remix.source_stories.length}개 설화를 섞은 Cross-Story Remix 결과입니다.` : '후보 카드를 클릭하면 해당 Beat를 즉시 교체해 다시 생성합니다.';

  const blueprintFields = [
    ['BASE STORY PACK', `${blueprint.source_pack.source_story_title} · 기준 ${blueprint.source_pack.beat_coverage}/5 Beat coverage`],
    ...(data.remix?.active ? [['ACTIVE REMIX', `${data.remix.selected_count}/${data.remix.total_beats} Beat 교체 · ${data.remix.source_stories.length}개 원천 설화`]] : []),
    ['PROTAGONIST', blueprint.protagonist], ['GOAL', blueprint.goal], ['CONFLICT', blueprint.conflict], ['WORLD', blueprint.world],
  ];
  document.querySelector('#blueprint').innerHTML = blueprintFields.map(([label, value]) => `
    <div class="blueprint-card"><span>${label}</span><p>${escapeHtml(value)}</p></div>
  `).join('');
  document.querySelector('#beat-plan').innerHTML = Object.entries(blueprint.beat_plan).map(([beat, purpose], index) => {
    const binding = data.bound_beats?.[beat] || {};
    const dnaField = String(binding.dna_focus || '').replace('the_', '');
    const dnaValue = binding.dna_value || blueprint[dnaField] || '';
    return `
      <div class="beat"><b>${String(index + 1).padStart(2, '0')} / ${escapeHtml(beat)}<small>DNA · ${escapeHtml(binding.dna_focus || 'blueprint')}</small><small>${escapeHtml(dnaValue)}</small></b><p>${escapeHtml(purpose)}<small>${escapeHtml(binding.event_text || '바인딩된 원천 사건 없음')} · ${escapeHtml(binding.source_story || '')}</small></p></div>
    `;
  }).join('');
  const activeModules = data.active_modules || data.retrieved || [];
  document.querySelector('#modules-title').textContent = data.remix?.active ? 'ACTIVE REMIX MODULES' : 'CENTER STORY PACK MODULES';
  document.querySelector('#modules').innerHTML = activeModules.map((module) => {
    const source = [module.source_story, module.category].filter(Boolean).join(' · ');
    const breakdown = (module.score_breakdown || []).map((part) => `${part.label} +${part.value}`).join(' · ');
    return `<article class="module"><div class="module-head"><h4>${escapeHtml(module.title)}</h4><span class="module-score">TF-IDF ${escapeHtml(module.score)}</span></div><div class="module-source">${escapeHtml(source)}</div><p>${escapeHtml(module.text)}</p><div class="module-score-note">점수 구성: ${escapeHtml(breakdown || '기본 공명')}</div><div class="module-tags">${escapeHtml(module.beat)} · ${escapeHtml(module.match_reason || 'source resonance')}</div></article>`;
  }).join('');

  const generatedSectionTitle = document.querySelector('.generated-section h3');
  if (generatedSectionTitle) generatedSectionTitle.textContent = 'GENERATED FOLKTALE';
  const generatedStory = document.querySelector('.generated-story');
  if (generatedStory && !document.querySelector('#generated-mode')) {
    const modeNode = document.createElement('p');
    modeNode.id = 'generated-mode';
    modeNode.className = 'story-generation-mode story-controls';
    generatedStory.prepend(modeNode);
  }
  if (generatedStory && !document.querySelector('#generated-based-on')) {
    const basedOnNode = document.createElement('p');
    basedOnNode.id = 'generated-based-on';
    basedOnNode.className = 'story-based-on story-controls';
    generatedStory.append(basedOnNode);
  }
  const controls = data.generated.controls;
  const mode = data.generated.generation_mode || 'Recombined Baseline';
  const modeLabel = mode.toLowerCase().includes('llm') ? 'LLM Generated' : 'Recombined Baseline';
  const sourceStories = new Set((data.retrieved || []).map((item) => item.source_story).filter(Boolean));
  const sourceCount = data.remix?.source_stories?.length || sourceStories.size || 0;
  const patternCount = data.generated.source_patterns_count || 0;
  const generatedMode = document.querySelector('#generated-mode');
  if (generatedMode) generatedMode.textContent = `Generation Mode · ${modeLabel}${data.generated.generation_status === 'fallback' ? ' · fallback' : ''}`;
  document.querySelector('#generated-controls').textContent = `${controls.location} · ${controls.mood} · ${controls.tone} · ${controls.ending} · ${data.generated.generation_mode}`;
  document.querySelector('#generated-title').textContent = data.generated.title;
  document.querySelector('#generated-text').textContent = data.generated.text;
  const basedOn = document.querySelector('#generated-based-on');
  if (basedOn) {
    const notice = data.generated.generation_notice ? `${data.generated.generation_notice} ` : '';
    basedOn.textContent = `${notice}Based on: ${sourceCount} retrieved Jeju folktales · Story DNA · Narrative Blueprint · ${patternCount || 6} abstract narrative patterns`;
  }
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
  selectedOverrides = {};
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
