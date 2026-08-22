# 스토리 생성 프로세스 비교 분석

> Bullks/AWS vs Tiger 시스템의 **이야기가 만들어지는 과정** 중심 비교

---

## 1. 이야기 생성의 시작점: 사용자 입력

### Bullks/AWS 시스템
```
사용자 → [나이, 성별, 직업, MBTI, 현재 상황, 위치(GPS)]
```
- **관점**: "당신은 어떤 사람인가?" (사회적 정체성 중심)
- **핵심 질문**: 직업/MBTI가 주인공의 행동 패턴을 결정
- **예시 입력**: 30세 남성, 개발자, INTJ, "코드 버그로 지쳤다", 한라산 둘레길

### Tiger 시스템
```
사용자 → [원하는 감정, 갈등 유형, 위치, 심리적 상처/갈망]
```
- **관점**: "당신은 무엇을 느끼고 싶은가?" (내면 상태 중심)
- **핵심 질문**: 사용자의 심리적 결핍과 원하는 감정적 여정
- **예시 입력**: Thriller 감정, Inner_Conflict 갈등, 성산읍, "외로움/연결에 대한 갈망"

`★ Insight ─────────────────────────────────────`
두 시스템의 철학적 차이:
- **Bullks**: "당신의 직업적 관점으로 세상을 바라보게 해주겠다" → 개발자면 버그/디버깅 은유
- **Tiger**: "당신의 상처가 이야기 속에서 치유되게 해주겠다" → 심리적 공명 추구
`─────────────────────────────────────────────────`

---

## 2. Stage 1: 이야기의 뼈대 결정

### 공통점
둘 다 **Beat 구조** (Ki-Sho-Ten-Ketsu 변형)를 사용하여 이야기의 골격을 결정

### Bullks/AWS: "10챕터 고정 구조"
```
Ch1(Hook) → Ch2(Encounter) → Ch3(Trap) → Ch4(Conflict) → Ch5(Dialogue)
→ Ch6(Crisis) → Ch7(Logic) → Ch8(Action) → Ch9(Climax) → Ch10(Survivor)
```
- **특징**: 감정(장르)에 따라 2가지 구조 중 선택 (Thriller형 vs Emotional형)
- **제약**: 10화 고정, 챕터당 약 200자
- **현장성**: "1시간 내, 반경 500m 내" 물리적 제약 적용

```yaml
# Thriller 구조 예시
Ch1: 일상을 깨트리는 기이한 발견 [Status: Alone]
Ch2: 누군가 나타나 내 길을 막는다 [Status: Together]
Ch3: 퇴로 차단, {key_item} 획득 [Status: Together]
...
Ch10: 환상이 걷히고, 발걸음을 떼며 마무리 [Status: Alone]
```

### Tiger: "가변 Beat 구조"
```
Ki → [Sho] → Trial → [Crisis] → Ten → [Climax] → Ketsu
     (선택)       (선택)       (선택)
```
- **특징**: 사용자가 원하는 Beat 수 (3~7개) 선택 가능
- **유연성**: PLOT_PATTERNS DB에서 emotion+conflict 조합에 맞는 구조 검색
- **제약 없음**: 시간/공간 제약 없이 서사 자체의 흐름에 집중

```python
# 동적 Beat 선택 예시
plot_result = {
    "beat_sequence": ["Ki", "Trial", "Ten", "Ketsu"],  # 4-beat
    "reference_story_id": "F_007",
    "beat_count": 4
}
```

`★ Insight ─────────────────────────────────────`
구조 철학의 차이:
- **Bullks**: 영화/드라마 같은 **에피소드 형식** → 예측 가능한 리듬감
- **Tiger**: 설화 본연의 **유기적 흐름** → 이야기마다 다른 호흡
`─────────────────────────────────────────────────`

---

## 3. Stage 2: Story DNA 생성 (이야기의 영혼)

이 단계가 **가장 중요**. 이야기의 의미와 방향이 결정됨.

### 공통 DNA 4요소
```
1. The Question: 이 이야기가 던지는 질문
2. The Lack: 주인공의 내적 결핍
3. The Cost: 원하는 것을 얻기 위한 대가
4. The Irony: 표면과 이면의 괴리
```

### Bullks/AWS의 DNA 생성 과정
```
[사용자 프로필] + [MBTI 키워드] + [RAG 검색]
         ↓
    LLM에게 질문: "이 사람에게 어떤 질문/결핍/대가가 적절한가?"
         ↓
    Story DNA 4요소 생성
```

**MBTI 기반 개인화 예시**:
```python
# INTJ 사용자
MBTI_TRAITS["I"] = {"keywords": ["사색", "혼자", "분석"], "action_style": "조용히 계획"}
MBTI_TRAITS["N"] = {"keywords": ["패턴", "의미", "숨겨진", "상징"], "action_style": "의미 찾기"}
MBTI_TRAITS["T"] = {"keywords": ["논리", "분석", "비교", "원리"], "action_style": "논리로 결정"}
MBTI_TRAITS["J"] = {"keywords": ["구조", "계획", "순서", "완성"], "action_style": "체계적 접근"}

# → LLM 프롬프트에 주입: "사색, 분석, 패턴, 논리, 구조" 키워드 반영
```

**직업별 어휘 적용**:
```python
# 개발자인 경우
JOB_VOCAB_MAP["개발자"] = {
    "pos": ["버그", "루프", "디버깅", "알고리즘", "리팩터링"],
    "neg": []  # 사용 금지 어휘 없음
}

# → 이야기 속 은유: "이 문제는 무한 루프에 빠진 것 같았다"
```

### Tiger의 DNA 생성 과정
```
[사용자 감정/갈등] + [User DNA (상처/갈망)] + [RAG 검색]
         ↓
    LLM에게 질문: "이 감정에 맞는 의미있는 질문은?"
         ↓
    Story DNA 4요소 생성 (후보 3개씩 → 최적 조합 선택)
```

**User DNA 기반 개인화 예시**:
```python
preferences = {
    'user_dna_wound': '외로움',      # 내적 상처
    'user_dna_desire': '연결',       # 갈망
    'resonance_keywords': ['바다', '해변', '파도']  # 공명하는 키워드
}

# → Story DNA 생성 시:
# - The Lack: 사용자의 Wound(외로움)를 반영하는 내적 결핍
# - The Question: 사용자의 Desire(연결)를 향한 철학적 질문
```

**장르별 DNA 가이드 (v5.1)**:
```python
EMOTION_DNA_GUIDES["Thriller"] = """
## 🔪 Thriller DNA 설계 가이드
- the_question: 생존/탈출/진실 관련 질문
- the_lack: 생존에 필요한 내적 역량 (경계심, 판단력)
- the_cost: 안전, 평화, 순수함 (긴장감을 높이는 대가)
- the_irony: 도망치던 곳이 덫이었다는 식의 반전
"""
```

`★ Insight ─────────────────────────────────────`
개인화 철학의 차이:
- **Bullks**: "당신의 사회적 역할(직업/MBTI)로 세상을 해석하라"
- **Tiger**: "당신의 내면의 상처와 갈망을 이야기에 투영하라"
`─────────────────────────────────────────────────`

---

## 4. Stage 2.5: Story Bible (Bullks 전용)

### Bullks만의 독특한 단계: "일관성 설정서"

```yaml
story_bible:
  protagonist:
    name: "지훈"
    age: 30
    job: "개발자"
    mbti: "INTJ"

  npc_persona:
    name: "강당장 할머니"  # RAG에서 검색된 설화 인물
    role: "주인공을 시험하고 이끄는 존재"
    voice: "설화적 어투"

  key_item: "낡은 USB 메모리"  # 3화에서 획득, 8화에서 활용

  narrative_style: "관찰자 시점 (3인칭)"
  reality_rule: "모든 현상은 심리적/물리적 이유가 있어야 함"
  tone: "신비로우면서도 현실적"
```

**Story Bible의 역할**:
1. **NPC 일관성**: 10화 동안 같은 인물이 같은 말투로 등장
2. **아이템 연속성**: 3화에서 획득 → 8화에서 반드시 활용
3. **문체 통일**: 전체 이야기에서 같은 톤 유지

### Tiger는 Story Bible이 없음
- 대신 **Story DNA 자체**가 일관성을 보장
- 각 Beat에서 DNA focus (the_lack, the_cost, the_irony)를 참조

`★ Insight ─────────────────────────────────────`
설계 철학의 차이:
- **Bullks**: 10화 시리즈를 위한 **상세한 제작 노트** 필요
- **Tiger**: 단편 이야기라 DNA만으로 **의미적 일관성** 확보
`─────────────────────────────────────────────────`

---

## 5. Stage 3: Beat-Module 조립

### 공통 개념
각 Beat에 필요한 **소재**를 RAG DB에서 검색하여 조립

```yaml
Beat별 필요 모듈:
  Ki: [place, mood] + [character?]
  Trial: [event_ref, character]
  Ten: [event_ref] + [wisdom?]
  Ketsu: [mood, wisdom]
```

### Bullks/AWS의 조립 방식
```python
# 각 Beat에 대해
for beat_name in ["Ki", "Sho", "Trial", ...]:
    # 1. 사건 검색 (STORY_BEATS)
    beat_events = rag.search_beat_events(beat_name, emotion)

    # 2. 모듈 검색 (STORY_MODULES)
    modules = {
        "place": rag.search_modules("Place", beat_name, location),
        "character": rag.search_modules("Character", beat_name, location),
        "mood": rag.search_modules("Mood", beat_name, location),
    }

    # 3. Fallback: 데이터 없으면 인접 Beat에서 빌려옴
    if beat_name == "Crisis" and not modules:
        modules = beat_modules["Trial"].copy()  # Trial 데이터 재사용
```

**특징**: Fallback 로직이 상세함 (Crisis→Trial, Ten→Trial, Sho→Ki)

### Tiger의 조립 방식
```python
# Story DNA focus에 따라 검색 쿼리 구성
dna_focus = BEAT_MODULE_MAP[beat]["story_dna_focus"]  # 예: "the_lack"
dna_element = getattr(story_dna, dna_focus)  # 예: "자기 자신을 이해하는 능력"

# DNA 요소를 검색에 반영
query = f"{query_hint} - {dna_element}"
results = story_modules.query(query_embeddings=..., where={"module_type": "Mood"})
```

**특징**: **Story DNA가 모듈 선택을 결정** → 의미적 연결 강화

`★ Insight ─────────────────────────────────────`
조립 철학의 차이:
- **Bullks**: "빈 칸을 채우는" 실용적 접근 (데이터 없으면 대체)
- **Tiger**: "의미가 연결되는" 유기적 접근 (DNA가 검색 가이드)
`─────────────────────────────────────────────────`

---

## 6. Stage 4: 최종 이야기 생성

### Bullks/AWS: "2화씩 블록 생성 + 이어붙이기"
```
생성 순서: [Ch1-2] → [Ch3-4] → [Ch5-6] → [Ch7-8] → [Ch9-10]
```

```python
# 이전 챕터의 마지막 3문장을 다음 블록에 전달
previous_context = _extract_last_sentences(chapters[-1], count=3)

# 블록 생성 프롬프트
prompt = f"""
[직전 맥락]
{previous_context}

[이번 블록 지시]
- Chapter {start_ch}: {structure[start_ch-1]['instruction']}
- Chapter {start_ch+1}: {structure[start_ch]['instruction']}

[Story Bible]
- 주인공: {bible['protagonist']['name']}, {bible['protagonist']['job']}
- NPC: {bible['npc_persona']['name']}
- Key Item: {bible['key_item']} (3화 획득, 8화 활용)
"""
```

**품질 평가 & 자동 수정**:
```python
# 생성된 텍스트 평가
eval_result = _evaluate_story(generated_text)
# {
#   "folklore_score": 7.5,  # 설화 요소 반영도
#   "profile_score": 8.0,   # 사용자 프로필 반영도
#   "improvements": ["MBTI 특성 더 반영 필요"]
# }

# 점수가 낮으면 재생성
if eval_result["folklore_score"] < 6.0:
    generated_text = _regenerate_with_feedback(improvements)
```

### Tiger: "한 번에 전체 생성"
```python
prompt = f"""
## Story DNA (이야기의 핵심 - 반드시 녹여내세요)
- 핵심 질문: {story_dna.the_question}
- 캐릭터 결핍: {story_dna.the_lack}
- 대가: {story_dna.the_cost}
- 아이러니: {story_dna.the_irony}

## Beat 구조
{' → '.join(beat_sequence)}

## Beat별 소재
{beat_materials}

## 6대 원칙 (각 장면에서 반드시 자문하세요)
1. 의미 있는 사건인가?
2. 대가 있는 선택인가?
3. 의미 있는 디테일인가?
...

{emotion_guide}  # 장르별 특별 지침

## 생성 지침
- 전체 길이: 500-800자
- Beat 구분 없이 자연스럽게 연결된 하나의 이야기로 작성
"""
```

**장르별 특별 지침 (EMOTION_GUIDES)**:
```python
EMOTION_GUIDES["Thriller"] = """
## Thriller 특별 지침
- 말하지 마라: 위협의 정체를 최대한 늦게 보여줘라
- 선택에 시간제한: "해가 지기 전에 결정해야 한다"
- 탈출구를 막아라: 도망가면 더 나쁜 일이 생긴다
- 감각을 써라: "뭔가 잘못됐다"를 설명하지 말고 느끼게 해라
"""

EMOTION_GUIDES["Healing"] = """
## Healing 특별 지침
- 큰 사건 금지: 드라마틱한 화해 장면 NO
- 일상의 디테일: 밥 짓는 소리, 빨래 걷는 손
- 천천히: 치유는 한 순간에 오지 않는다
- 완전한 해결 금지: 상처는 남되, 함께 살아가는 법을 배운다
"""
```

`★ Insight ─────────────────────────────────────`
생성 철학의 차이:
- **Bullks**: **분할 정복** → 10화 시리즈를 2화씩 쪼개서 일관성 유지
- **Tiger**: **전체 조망** → 단편의 유기적 흐름을 한 번에 포착
`─────────────────────────────────────────────────`

---

## 7. 사용자 경험 흐름 비교

### Bullks/AWS 사용자 여정
```
1. 앱 실행 → GPS 위치 확인
2. 프로필 입력 (나이/성별/직업/MBTI/상황)
3. [대기] 10화 시리즈 생성 (30초~1분)
4. 한 화씩 읽으며 걷기
5. 다음 핫스팟 도착 → 다음 화 열림
6. 10화까지 완주 → 완결
```

**강점**:
- Walk-through 모드로 실제 여행과 이야기 연동
- GPS 기반 Geofencing으로 장소에서 이야기 unlock

### Tiger 사용자 여정
```
1. 감정/갈등/위치 선택
2. (선택) 심리적 상태 입력 (User DNA)
3. [대기] 단편 이야기 생성 (15초~30초)
4. 한 편의 완결된 이야기 읽기
5. Pipeline Trace로 "왜 이 이야기가 나왔는지" 확인
```

**강점**:
- Explainability (설명 가능성) - 각 Stage에서 무슨 일이 일어났는지 추적
- User DNA로 심리적 공명

---

## 8. 핵심 차이 요약

| 관점 | Bullks/AWS | Tiger |
|------|------------|-------|
| **이야기 형식** | 10화 시리즈 (2000자) | 단편 (500-800자) |
| **개인화 축** | 사회적 정체성 (직업/MBTI) | 심리적 상태 (상처/갈망) |
| **구조 철학** | 고정 에피소드 (영화식) | 유기적 흐름 (설화식) |
| **일관성 도구** | Story Bible | Story DNA |
| **생성 방식** | 2화씩 블록 생성 | 전체 한 번에 생성 |
| **품질 관리** | 자동 평가 + 재생성 | 장르별 가이드라인 |
| **사용 맥락** | 걸으며 읽기 (여행) | 앉아서 읽기 (몰입) |

---

## 9. 통합 가능성

두 시스템의 장점을 결합한다면:

### Tiger에서 가져올 수 있는 것 → Bullks로
- **User DNA 개념**: MBTI/직업 외에 심리적 상처/갈망 입력 추가
- **장르별 DNA 가이드**: Story DNA 생성 시 장르 특성 반영

### Bullks에서 가져올 수 있는 것 → Tiger로
- **Story Bible**: 더 긴 이야기 생성 시 일관성 도구로 활용
- **품질 평가 루프**: 생성 후 자동 평가 및 개선 제안
- **MBTI/직업 어휘**: 개인화 옵션 확장

---

*분석 일자: 2024-12-19*
*비교 대상: bullks/AWS 브랜치 vs tiger 브랜치*
