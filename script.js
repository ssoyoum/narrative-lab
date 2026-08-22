const sampleStory = document.querySelector('#story-input').value;
const storyInput = document.querySelector('#story-input');
const generateButton = document.querySelector('#generate-button');
const sampleButton = document.querySelector('#sample-button');
const emptyState = document.querySelector('#empty-state');
const result = document.querySelector('#result');
const errorMessage = document.querySelector('#error-message');

const escapeHtml = (value) => String(value).replace(/[&<>'"]/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;'
}[character]));

const values = (key) => [...document.querySelectorAll(`[data-${key}]`)].map((node) => node.textContent);

sampleButton.addEventListener('click', () => {
  storyInput.value = sampleStory;
  storyInput.focus();
});

function renderResult(data) {
  emptyState.hidden = true;
  result.hidden = false;
  document.querySelector('#retrieval-method').textContent = data.retrieval_method;

  const dnaLabels = { setting: 'SETTING', characters: 'CHARACTERS', emotion: 'EMOTION', conflict: 'CONFLICT', beats: 'BEATS' };
  document.querySelector('#dna-grid').innerHTML = Object.entries(dnaLabels).map(([key, label]) => `
    <div class="dna-item"><span>${label}</span><strong>${escapeHtml(data.analysis.dna[key].join(' · '))}</strong></div>
  `).join('');

  document.querySelector('#beats').innerHTML = data.analysis.beats.map((beat) => `
    <div class="beat"><b>${String(beat.index).padStart(2, '0')} / ${escapeHtml(beat.type)}</b><p>${escapeHtml(beat.text)}<small>${escapeHtml(beat.role)}</small></p></div>
  `).join('');

  document.querySelector('#modules').innerHTML = data.retrieved.map((module) => `
    <article class="module"><div class="module-head"><h4>${escapeHtml(module.title)}</h4><span class="module-score">${module.score}</span></div><p>${escapeHtml(module.text)}</p><div class="module-tags">${escapeHtml(module.beat)} · ${escapeHtml(module.matched_terms.join(' · ') || 'context match')}</div></article>
  `).join('');

  const controls = data.generated.controls;
  document.querySelector('#generated-controls').textContent = `${controls.location} · ${controls.mood} · ${controls.tone} · ${controls.ending}`;
  document.querySelector('#generated-title').textContent = data.generated.title;
  document.querySelector('#generated-text').textContent = data.generated.text;
}

generateButton.addEventListener('click', async () => {
  errorMessage.textContent = '';
  generateButton.disabled = true;
  generateButton.querySelector('span:first-child').textContent = 'PROCESSING STORY...';
  try {
    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        story: storyInput.value,
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
    generateButton.querySelector('span:first-child').textContent = 'ANALYZE & GENERATE';
  }
});
