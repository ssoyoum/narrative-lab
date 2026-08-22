# Vector DB Schema: 제주 설화 4-Collection 구조

**버전**: 3.1
**최종 수정**: 2025-12-19

---

## 1. 데이터 흐름 전체도

### 1.1. End-to-End 파이프라인

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     PHASE 1: INGEST (데이터 적재)                                │
│                                                                                  │
│   Enriched JSON (246개 설화)                                                    │
│          ↓                                                                       │
│   ┌────────────────────────────────────────────────────────────────────────┐    │
│   │                    4-Collection으로 분해                                │    │
│   │                                                                        │    │
│   │  beats[]           → PLOT_PATTERNS    (246개) "어떤 구조?"            │    │
│   │  summary, emotion  → STORY_CATALOG    (246개) "어떤 설화?"            │    │
│   │  beats[].event     → STORY_BEATS    (~1,255개) "어떤 사건?"            │    │
│   │  entities, places  → STORY_MODULES  (~2,590개) "어떤 재료?"            │    │
│   └────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     PHASE 2: QUERY (이야기 생성)                                 │
│                                                                                  │
│   User Input (mood, weather, location)                                          │
│          ↓                                                                       │
│   ┌──────────────────────────────────────────────────────────────────┐          │
│   │ User DNA 추론 (engine_integration.py)                            │          │
│   │   the_wound: "exhaustion"                                        │          │
│   │   the_desire: "rest"                                             │          │
│   │   resonance_keywords: ["적막", "떠남", "안식"]                    │          │
│   └──────────────────────────────────────────────────────────────────┘          │
│          ↓                                                                       │
│   ┌──────────────────────────────────────────────────────────────────┐          │
│   │ 4-Stage Pipeline (story_generator.py)                            │          │
│   │                                                                  │          │
│   │ Stage 1: PLOT_PATTERNS 검색 → Beat Sequence 선택                 │          │
│   │ Stage 2: STORY_CATALOG 검색 + LLM → Generated Story DNA 생성     │          │
│   │ Stage 3: STORY_BEATS + STORY_MODULES 검색 → 재료 조립            │          │
│   │ Stage 4: LLM → 최종 이야기 생성                                   │          │
│   │                                                                  │          │
│   │ ※ User DNA는 Stage 2, 4의 LLM 프롬프트에 주입                    │          │
│   └──────────────────────────────────────────────────────────────────┘          │
│          ↓                                                                       │
│   Personalized Story Output                                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2. 4-Collection 구조

| Collection | 개수 | 역할 | 검색 기준 |
|------------|------|------|----------|
| **PLOT_PATTERNS** | 246개 | 플롯 구조 템플릿 선택 | beat_count, emotion, conflict |
| **STORY_CATALOG** | 246개 | 참조 설화 식별 & 필터링 | title, emotion, conflict, region |
| **STORY_BEATS** | ~1,255개 | Beat별 원본 사건 참고 | beat 종류, function |
| **STORY_MODULES** | ~2,590개 | 재조합 가능한 소재 | module_type, role, usable_beats |

**데이터 경로**:
- **원본**: `jeju-stories/enriched/` (246개 enriched JSON)
- **Vector DB**: `jeju-stories/chroma_db/` (ChromaDB)
- **임베딩 모델**: `intfloat/multilingual-e5-large`

---

## 2. 4-Stage Pipeline별 Collection 활용

### Stage 1: 구조 선택 (Plot Pattern Selection)

```
입력: emotion, conflict, preferences
    ↓
┌───────────────────────────────────────┐
│ PLOT_PATTERNS 검색                    │
│ where = {                             │
│   "emotion": "Healing",               │
│   "conflict": "Inner_Conflict",       │
│   "beat_count": {"$gte": 5}           │
│ }                                     │
└───────────────────────────────────────┘
    ↓
출력: Beat Sequence (예: "Ki → Shō → Trial → Crisis → Ketsu")
```

### Stage 2: 의미 설계 (Story DNA Generation)

```
입력: location, Beat Sequence, preferences (← User DNA 포함)
    ↓
┌───────────────────────────────────────┐
│ STORY_CATALOG 검색 (참조 설화 획득)   │
│ where = {                             │
│   "emotion": "Healing",               │
│   "admin_region": {"$contains": 위치} │
│ }                                     │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ LLM 프롬프트 생성                     │
│ - 참조 설화 요약 포함                 │
│ - User DNA (wound, desire) 주입      │ ← 개인화
│ - EMOTION_DNA_GUIDES 적용            │
└───────────────────────────────────────┘
    ↓
출력: Generated Story DNA
      {
        "the_question": "...",
        "the_lack": "...",      ← User wound 반영
        "the_cost": "...",
        "the_irony": "..."      ← User desire 반영
      }
```

### Stage 3: 모듈 조립 (Beat-Module Assembly)

```
입력: Beat Sequence, Generated Story DNA
    ↓
┌───────────────────────────────────────┐
│ STORY_BEATS 검색 (Beat별 참고 사건)   │
│ where = {                             │
│   "beat": "Ki",                       │
│   "emotion": "Healing"                │
│ }                                     │
└───────────────────────────────────────┘
    ↓
┌───────────────────────────────────────┐
│ STORY_MODULES 검색 (재료 조합)        │
│ - Character: 주인공, 조력자           │
│ - Place: 성산일출봉, 오름             │
│ - Event: 시련, 반전 사건              │
│ - Mood: 분위기 키워드                 │
│ - Wisdom: 교훈                        │
└───────────────────────────────────────┘
    ↓
출력: Beat별 Module 조합 (Context)
```

> **Note**: Stage 3에서는 User DNA가 직접 개입하지 않습니다. Generated Story DNA가 이미 User DNA를 반영하고 있으므로, DNA 기반 검색만으로 개인화가 이루어집니다.

### Stage 4: 이야기 생성 (Story Generation)

```
입력: Generated Story DNA, Beat-Module Context, preferences (← User DNA 포함)
    ↓
┌───────────────────────────────────────┐
│ LLM 프롬프트 생성                     │
│ - Generated Story DNA 포함           │
│ - Beat별 Module Context 포함         │
│ - User DNA (wound, desire) 주입      │ ← 개인화
│ - EMOTION_GUIDES 적용                │
└───────────────────────────────────────┘
    ↓
출력: 완성된 이야기 텍스트
```

---

## 3. 개인화: User DNA → Generated Story DNA

User DNA는 **preferences dict**를 통해 4-Stage Pipeline에 전달되어, **Stage 2**와 **Stage 4**의 LLM 프롬프트에 주입됩니다.

```
User Input (mood, weather, location)
        ↓
┌───────────────────────────────────────────────────┐
│ User DNA 추론 (engine_integration.py)             │
│   the_wound: "exhaustion"                         │
│   the_desire: "rest"                              │
│   resonance_keywords: ["적막", "떠남", "안식"]    │
└───────────────────────────────────────────────────┘
        ↓
   preferences dict로 변환
        ↓
┌───────────────────────────────────────────────────┐
│ Stage 2: _build_dna_prompt()                      │
│ LLM 프롬프트에 삽입:                               │
│   ## 사용자 심리 상태                              │
│   - **상처 (Wound)**: {wound}                     │
│   - **갈망 (Desire)**: {desire}                   │
│                                                   │
│ 결과: Generated Story DNA                         │
│   the_lack ← wound 반영                           │
│   the_question ← desire 반영                      │
└───────────────────────────────────────────────────┘
        ↓
┌───────────────────────────────────────────────────┐
│ Stage 4: _build_generation_prompt()               │
│ LLM 프롬프트에 삽입:                               │
│   ## 개인화 지침                                   │
│   1. 주인공: {wound}의 고통을 겪는 인물            │
│   2. 여정: {desire}를 향한 과정을 반영             │
│   3. 분위기: 공명 키워드로 배경 묘사               │
└───────────────────────────────────────────────────┘
        ↓
   Personalized Story Output
```

> **⚠️ 주의**: Generated Story DNA (`the_question`, `the_lack`, `the_cost`, `the_irony`)는 Vector DB에 저장되지 않습니다. 이 4요소는 매번 Stage 2에서 LLM이 동적으로 생성합니다.

---

## 4. Collection 상세 스키마

### 4.1. PLOT_PATTERNS (246개)

**목적**: 플롯 구조 템플릿 선택

**Document**:
```python
document = f"""
플롯 구조: Ki → Shō → Trial → Ten → Crisis → Climax → Ketsu
단계 수: 7단계
감정: Sweet_Potato
갈등: Rivalry
"""
```

**Metadata**:
| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| story_id | String | 원본 설화 ID | "F_001" |
| title | String | 설화 제목 | "개와 닭의 원한" |
| beat_sequence | String | Beat 순서 | "Ki,Shō,Trial,Ten,Crisis,Climax,Ketsu" |
| beat_count | Integer | Beat 개수 | 7 |
| has_basic_4beat | Boolean | 기본 4Beat 여부 | False |
| emotion | String | 감정 | "Sweet_Potato" |
| conflict | String | 갈등 유형 | "Rivalry" |

**검색 예시**:
```python
# 6단계 이상, Thriller 감정의 구조 찾기
results = plot_patterns.query(
    query_texts=["긴장감 있는 전개와 반전"],
    where={
        "beat_count": {"$gte": 6},
        "emotion": "Thriller"
    }
)
```

---

### 4.2. STORY_CATALOG (246개)

**목적**: 설화 식별 & 필터링 (가벼운 메타데이터만)

**Document**:
```python
document = f"""
제목: 개와 닭의 원한
분류: 민담
요약: 옛날 개와 닭이 함께 살았으나...
감정: Sweet_Potato
갈등: Rivalry
지역: 제주 전역
"""
```

**Metadata** (필터링용 + 개인화 매칭용):
| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| story_id | String | 설화 ID | "F_001" |
| title | String | 제목 | "개와 닭의 원한" |
| category | String | 분류 | "민담" |
| emotion | String | 감정 | "Sweet_Potato" |
| conflict | String | 갈등 | "Rivalry" |
| admin_region | String | 행정 구역 | "제주 전역" |
| beat_count | Integer | Beat 개수 | 7 |
| has_commentary | Boolean | 학술해설 여부 | False |
| **wounds_addressed** | String (JSON) | 다루는 상처 유형 | "[\"loss\", \"insignificance\"]" |
| **desires_fulfilled** | String (JSON) | 채워주는 갈망 | "[\"reconnection\", \"meaning\"]" |
| **primary_wound** | String | 대표 상처 | "loss" |
| **primary_desire** | String | 대표 갈망 | "reconnection" |
| **resonance_triggers** | String (JSON) | 공명 키워드 | "[\"개\", \"닭\", \"원한\"]" |

> **Note**: entity_names, terrain_types 등 상세 정보는 STORY_MODULES에서 검색

### 저장용 Story DNA 필드 (개인화용)

> **상세 설명**: Section 4 "개인화: User DNA ↔ Vector DB 연동" 참조

| 필드 | 용도 | 허용값 |
|------|------|--------|
| **wounds_addressed** | 이 설화가 다루는 상처 유형 (다중 선택) | exhaustion, loss, stagnation, disconnection, insignificance, arrogance, fear, grief |
| **desires_fulfilled** | 이 설화가 채워주는 갈망 (다중 선택) | rest, meaning, transformation, reconnection, discovery, healing, courage, peace, legacy |
| **resonance_triggers** | User DNA 키워드와 매칭할 공명 키워드 | 자유 형식 (한글) |

**검색 예시**:
```python
# 성산 지역, Healing 감정 설화 찾기
results = story_catalog.query(
    query_texts=["성산일출봉 평화로운 이야기"],
    where={
        "emotion": "Healing",
        "admin_region": {"$contains": "성산"}
    }
)

# User DNA 기반 개인화 검색 (Resonance Scoring)
results = story_catalog.query(
    query_texts=["쉼과 평화를 찾는 이야기"],
    where={
        "primary_wound": "exhaustion",
        "primary_desire": "rest"
    }
)
```

---

### 4.3. STORY_BEATS (~1,255개)

**목적**: Beat별 원본 사건 참고

**구조**: 각 설화의 각 Beat마다 1개 Document 생성
```
F_001 "개와 닭의 원한" (7 Beats)
  ├─ F_001_Ki
  ├─ F_001_Shō
  ├─ F_001_Trial
  ├─ F_001_Ten
  ├─ F_001_Crisis
  ├─ F_001_Climax
  └─ F_001_Ketsu
```

**Document**:
```python
document = f"""
Beat: Ki
사건: 부잣집에서 오래 기른 닭과 개가 함께 살았다
기능: 배경/초자연적 설정
"""
```

**Metadata**:
| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| beat_id | String | Beat 고유 ID | "F_001_Ki" |
| source_story_id | String | 원본 설화 ID | "F_001" |
| story_title | String | 설화 제목 | "개와 닭의 원한" |
| beat | String | Beat 종류 | "Ki" |
| beat_position | Integer | Beat 순서 | 1 |
| total_beats | Integer | 전체 Beat 수 | 7 |
| event_text | String | 사건 내용 | "부잣집에서 오래 기른..." |
| function | String | 서사적 기능 | "배경/초자연적 설정" |
| emotion | String | 설화 감정 | "Sweet_Potato" |
| conflict | String | 설화 갈등 | "Rivalry" |

**검색 예시**:
```python
# 평화로운 Ki Beat 참고
results = story_beats.query(
    query_texts=["평화로운 마을에서 시작"],
    where={
        "beat": "Ki",
        "emotion": "Healing"
    }
)

# 특정 설화의 모든 Beat 가져오기
results = story_beats.query(
    where={"source_story_id": "F_001"}
)
```

---

### 4.4. STORY_MODULES (~2,590개)

**목적**: 재조합 가능한 상세 소재 (Cross-Story)

**Module 분류**:
- **Character**: ~615개 (인물, 동물, 신령)
- **Place**: ~400개 (지형, 장소)
- **Event**: ~1,255개 (핵심 사건)
- **Mood**: 246개 (분위기)
- **Wisdom**: ~74개 (교훈, 속담)

> 실제 개수는 enriched 데이터 구조에 따라 변동됩니다.

### Module Type 1: Character

**Document**:
```python
document = f"""
인물: 개
유형: Animal
역할: Victim
설명: 뱀을 물리친 진짜 공로자
"""
```

**Metadata**:
| 필드 | 타입 | 설명 |
|------|------|------|
| module_type | String | "Character" |
| module_subtype | String | Human, Animal, Spirit, Monster |
| character_name | String | 인물 이름 |
| character_role | String | Protagonist, Antagonist, Helper, Victim, Trickster, Neutral |
| usable_in_beats | String | 사용 가능 Beat (쉼표 구분) |
| source_story_id | String | 원본 설화 ID |
| story_emotion | String | 원본 설화 감정 |

### Module Type 2: Place

**Document**:
```python
document = f"""
장소: 마을
유형: Village
설명: 개와 닭이 함께 사는 곳
"""
```

**Metadata**:
| 필드 | 타입 | 설명 |
|------|------|------|
| module_type | String | "Place" |
| place_type | String | Village, Mountain, Sea, Cave, Forest, River, Other |
| place_name | String | 장소 이름 |
| usable_in_beats | String | 사용 가능 Beat |
| source_story_id | String | 원본 설화 ID |

### Module Type 3: Event

**Document**:
```python
document = f"""
사건: 장남이 닭장에서 이야기를 엿듣고 부친에게 보고했다
Beat: Ten
기능: 반전/음모 발각
"""
```

**Metadata**:
| 필드 | 타입 | 설명 |
|------|------|------|
| module_type | String | "Event" |
| module_subtype | String | 서사적 기능 (function 필드) |
| event_summary | String | 사건 요약 (100자) |
| original_beat | String | 원본 Beat |
| usable_in_beats | String | 사용 가능 Beat |
| related_conflict | String | 관련 갈등 |
| source_story_id | String | 원본 설화 ID |

### Module Type 4: Mood

**Metadata**:
| 필드 | 타입 | 설명 |
|------|------|------|
| module_type | String | "Mood" |
| mood_emotion | String | 감정 |
| mood_conflict | String | 갈등 |
| mood_keywords | String | 분위기 키워드 |
| source_story_id | String | 원본 설화 ID |

### Module Type 5: Wisdom

**Metadata**:
| 필드 | 타입 | 설명 |
|------|------|------|
| module_type | String | "Wisdom" |
| module_subtype | String | Commentary |
| wisdom_summary | String | 교훈 요약 |
| usable_in_beats | String | "Ketsu" |
| source_story_id | String | 원본 설화 ID |

---

## 5. 이야기 생성 플로우 예시

### 예시: "성산일출봉 Healing 이야기, 내적 갈등 극복"

**1단계: PLOT_PATTERNS** → 구조 선택
```python
where = {"emotion": "Healing", "conflict": "Inner_Conflict", "beat_count": {"$gte": 5}}
# 결과: "Ki → Shō → Trial → Crisis → Ketsu" 구조 선택
```

**2단계: STORY_CATALOG** → 참고 설화 ID 추출
```python
where = {"emotion": "Healing", "admin_region": {"$contains": "성산"}}
# 결과: story_id 3개 추출 (F_023, L_045, M_012)
```

**3단계: STORY_BEATS** → Beat별 참고
```python
where = {"beat": "Ki", "emotion": "Healing"}  # Ki 시작 방식 참고
where = {"beat": "Trial", "conflict": "Inner_Conflict"}  # Trial 전개 참고
```

**4단계: STORY_MODULES** → 상세 재료 조합
```python
where = {"module_type": "Place", "place_type": "Mountain"}  # 성산일출봉
where = {"module_type": "Character", "character_role": "Protagonist"}  # 주인공
where = {"module_type": "Event", "original_beat": "Trial"}  # 시련 사건
where = {"module_type": "Mood", "mood_emotion": "Healing"}  # 분위기
where = {"module_type": "Wisdom"}  # 교훈
```

**5단계: LLM 프롬프트 생성** → 이야기 작성

---

## 6. 통계 및 참고

### Collection별 예상 Document 수
- PLOT_PATTERNS: 246개 (설화당 1개)
- STORY_CATALOG: 246개 (설화당 1개)
- STORY_BEATS: ~1,255개 (Beat당 1개)
- STORY_MODULES: ~2,590개 (요소당 1개)

### Beat 분포 (246개 설화)
- 4 Beat (기본): 129개 (52%)
- 5-6 Beat: 62개 (25%)
- 7-8 Beat: 55개 (22%)
