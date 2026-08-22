# 🎭 Narrative Engine Architecture
## 제주 설화 기반 "재미있는 이야기" 생성 엔진 PRD

> **Version**: 5.2
> **Last Updated**: 2025-12-19
> **Status**: Personalization Layer Implemented (Generation Mode User DNA 흐름 명세 추가)

---

## 목차

1. [Executive Summary](#1-executive-summary)
2. [문제 정의: 왜 LLM 이야기가 재미없는가](#2-문제-정의)
3. [핵심 솔루션: 3계층 프레임워크](#3-핵심-솔루션)
4. [4-Stage 생성 파이프라인](#4-4-stage-생성-파이프라인)
5. [Stage별 상세 명세](#5-stage별-상세-명세)
6. [6대 원칙과 Emotion별 가이드](#6-6대-원칙과-emotion별-가이드)
7. [RAG 전략 및 검색 로직](#7-rag-전략-및-검색-로직)
8. [핵심 프롬프트/컨텍스트 엔지니어링](#8-핵심-프롬프트컨텍스트-엔지니어링)
9. [코드베이스 설계](#9-코드베이스-설계)
10. [품질 검증 체계](#10-품질-검증-체계)
11. [구현 로드맵](#11-구현-로드맵)
12. [**NEW** Personalization Layer](#12-personalization-layer)

---

## 1. Executive Summary

### 1.1. 프로젝트 목표

**Mission**: 제주 설화 246편을 기반으로, LLM이 생성하는 이야기의 근본적 한계("앙꼬 빠진 느낌")를 극복하고 **진짜 재미있는 이야기**를 생성하는 Narrative Engine 구축

### 1.2. 핵심 차별점

| 기존 LLM 스토리텔링 | 본 엔진 |
|-------------------|--------|
| "이야기를 써라" | "이 의미를 담은 이야기를 써라" |
| 패턴 기반 (다음 단어 예측) | 의미 기반 (Story DNA 우선 설계) |
| 규칙 제공 → 형식만 따름 | 질문 제공 → 생각하게 함 |
| 모든 것 설명 | 빈 공간 남김 (독자가 채움) |

### 1.3. 기술 스택

- **Vector DB**: ChromaDB (4-Collection 구조)
- **Embedding**: `intfloat/multilingual-e5-large`
- **LLM**: Gemini 2.0 Flash (GeminiWrapper)
- **Backend**: Python 3.11+

---

## 2. 문제 정의

### 2.1. LLM 이야기가 "앙꼬 빠진" 이유

```
┌─────────────────────────────────────────────────────────────┐
│  근본 원인: LLM은 "보이는 패턴"을 학습                         │
│            이야기의 핵심은 "보이지 않는 의미"                  │
└─────────────────────────────────────────────────────────────┘
```

| 영역 | LLM 방식 | 사람 방식 | 차이 |
|------|---------|----------|------|
| **사건** | "괴물이 나타났다. 싸워서 이겼다." | "괴물은 차라리 반가운 적이었다. 누군가를 미워해도 되는 대상." | 사건 자체 vs 사건의 의미 |
| **디테일** | "빨간 지붕의 예쁜 집" | "지붕을 빨갛게 칠한 건 할아버지. 바다에서 돌아오는 길에 멀리서도 찾을 수 있게." | 장식 vs 스토리 연결 |
| **선택** | 위험 → 당연히 도망 | "도망가면 평생 후회할 것 같다" | 당연한 선택 vs 어려운 선택 |
| **감정** | "슬펐다" (직접 서술) | 말없이 밥상을 차린다 (행동으로 보여줌) | 설명 vs 암시 |

### 2.2. 이미지/음악 vs 이야기의 차이

```
이미지: 빨간 사과 → 눈에 보이는 것이 전부
음악:  슬픈 멜로디 → 귀에 들리는 것이 전부
이야기: "그는 떠났다" → 왜? 어디로? 돌아올까? 누구에게 영향?

→ 이야기는 "보이지 않는 의미의 그물망"
```

### 2.3. 해결해야 할 핵심 문제

1. **사건의 부재**: 일어나는 일은 있지만 "의미 있는 사건"이 없음
2. **기승전결의 부재**: 나열은 있지만 연결/긴장/해소가 없음
3. **개연성의 부재**: 그래서? 왜? 에 대한 답이 없음
4. **구체성의 부재**: 어디에나 적용 가능한 일반적 묘사

---

## 3. 핵심 솔루션

### 3.1. 3계층 프레임워크

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer A: STORY DNA (의미의 뼈대)                               │
│     이야기 생성 전 먼저 결정                                     │
│     → The Question, The Lack, The Cost, The Irony              │
│     "이 이야기가 무슨 말을 하려는가?"                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer B: 6대 원칙 (모든 이야기 공통)                            │
│     "규칙"이 아닌 "질문"으로                                     │
│     → 의미있는 사건, 대가있는 선택, 의미있는 디테일...            │
│     "각 장면에서 자문해야 할 것"                                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Layer C: Emotion별 강조점                                      │
│     유형에 따라 어떤 원칙을 특히 강조할지                         │
│     → Thriller: "말하지 않는 것" + "대가있는 선택"               │
│     "이 감정을 위해 특히 중요한 것"                              │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2. Story DNA 상세

#### ⚠️ 용어 구분: 저장용 vs 생성용 Story DNA

시스템에서 "Story DNA"라는 용어는 두 가지 다른 개념으로 사용됩니다:

| 구분 | 저장용 Story DNA | 생성용 Story DNA |
|------|-----------------|-----------------|
| **필드** | wounds_addressed, desires_fulfilled, resonance_triggers, emotional_arc, narrative_themes | the_question, the_lack, the_cost, the_irony |
| **목적** | User DNA ↔ 설화 매칭/검색 | 새 이야기의 의미/주제 설계 |
| **저장 위치** | enriched JSON + ChromaDB | 메모리 (생성 중에만 존재) |
| **생성 시점** | 미리 추출 (배치) | **Stage 2에서 LLM이 동적 생성** |
| **특성** | Categorical (enum 기반) | Free-form (자유 텍스트) |

**중요**: 아래 표의 4요소(The Question, The Lack, The Cost, The Irony)는 **Stage 2에서 동적으로 생성**되며, enriched JSON이나 ChromaDB에 미리 저장되지 않습니다.

#### 생성용 Story DNA 4요소

| DNA 요소 | 정의 | 역할 | 예시 |
|----------|------|------|------|
| **The Question** | 이야기가 답하려는 질문 | 독자가 끝에 생각하게 될 것 | "진정한 용기란 무엇인가?" |
| **The Lack** | 주인공의 내적 결핍 | 외적이 아닌 내적 부족함 | 자신감, 용서, 소속감 |
| **The Cost** | 원하는 걸 얻기 위한 대가 | 공짜는 없다 | "안전함을 버려야 자유를 얻는다" |
| **The Irony** | 표면과 이면의 괴리 | 예상과 다른 진실 | "영웅이 사실은 도망치고 싶다" |

#### 생성용 Story DNA 이론적 근거

**1. Narrative Identity Theory (Dan McAdams, 1985)**
> "인간은 자신의 삶을 이야기로 구성하며, 이 서사를 통해 정체성을 형성한다. 좋은 이야기는 '결핍(Lack)'에서 시작해 '대가(Cost)'를 치르고 '통찰(Insight)'에 도달한다."

- **the_lack**: McAdams의 "핵심 갈등(Nuclear Episode)" → 주인공의 결핍
- **the_cost**: "전환점(Turning Point)" → 변화를 위한 희생
- **the_irony**: "해석적 통합(Interpretive Integration)" → 역설적 깨달음

**2. Aristotle's Poetics - Anagnorisis (335 BC)**
> "비극의 핵심은 '아나그노리시스(인식/발견)'와 '페리페테이아(반전)'이다. 주인공이 진실을 깨닫는 순간 서사가 완성된다."

- **the_irony**: 아나그노리시스 → 역설적 깨달음의 순간
- **the_question**: 관객(독자)에게 던지는 카타르시스적 질문

### 3.3. Story DNA가 Beat를 결정하는 방식

```
Story DNA 설정 예시:
├─ The Question: "용서란 무엇인가?"
├─ The Lack: 주인공은 아버지를 용서하지 못함
├─ The Cost: 용서하려면 자존심을 버려야 함
└─ The Irony: 아버지도 할아버지를 용서하지 못했다

           ↓ 각 Beat의 역할이 명확해짐

Ki:    아버지와의 갈등 상황 (The Lack 드러남)
Trial: 용서해야 할 상황 발생 (The Cost 직면)
Ten:   아버지의 과거 발견 (The Irony 드러남)
Ketsu: 완전하지 않은 화해 (The Question에 대한 열린 답)
```

---

## 4. 4-Stage 생성 파이프라인

### 4.1. 전체 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER INPUT                                       │
│  {emotion, location, conflict, travel_context, preferences}             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 1: PLOT_PATTERNS 검색                                            │
│  ─────────────────────────────────────────────────────────────────────  │
│  Input:  emotion, conflict, beat_count 선호도                           │
│  Process: 유사 플롯 구조 검색 (semantic + filter)                        │
│  Output: beat_sequence (예: "Ki → Trial → Shō → Ten → Ketsu")           │
│                                                                         │
│  RAG Query: "긴장감 있는 전개와 반전"                                    │
│  Filter: {emotion: "Thriller", beat_count: {$gte: 5}}                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 2: STORY_CATALOG 검색 + STORY DNA 생성                           │
│  ─────────────────────────────────────────────────────────────────────  │
│  Input:  emotion, conflict, location                                    │
│  Process:                                                               │
│    2-1. STORY_CATALOG에서 유사 설화 3-5개 검색                          │
│    2-2. 해당 설화들의 핵심 요소 분석                                     │
│    2-3. LLM으로 Story DNA 4요소 생성                                    │
│  Output: story_dna {the_question, the_lack, the_cost, the_irony}        │
│                                                                         │
│  ★ 핵심: Story DNA가 이후 모든 선택을 결정                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 3: STORY_BEATS + STORY_MODULES 조합                              │
│  ─────────────────────────────────────────────────────────────────────  │
│  Input:  beat_sequence, story_dna, location                             │
│  Process:                                                               │
│    각 Beat마다:                                                         │
│    3-1. STORY_BEATS에서 해당 Beat 유형의 참고 사건 검색                  │
│    3-2. STORY_MODULES에서 Beat에 맞는 소재 선택                          │
│         - Character (역할 매칭)                                         │
│         - Place (위치 매칭)                                             │
│         - Mood (감정 매칭)                                              │
│         - Wisdom (Ketsu용)                                              │
│    3-3. Story DNA와 연결되는 Module 우선 선택                           │
│  Output: beat_modules {Ki: {...}, Trial: {...}, ...}                    │
│                                                                         │
│  ★ Cross-Story 조합: 여러 설화의 요소를 창의적으로 혼합                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  STAGE 4: 이야기 생성 (LLM)                                             │
│  ─────────────────────────────────────────────────────────────────────  │
│  Input:  story_dna, beat_modules, emotion_guide, 6대 원칙               │
│  Process:                                                               │
│    4-1. Story DNA를 프롬프트 최상단에 배치                              │
│    4-2. 6대 원칙을 "질문"으로 변환하여 포함                             │
│    4-3. Emotion별 특별 지침 적용                                        │
│    4-4. Beat 순서대로 이야기 생성                                       │
│  Output: 완성된 이야기 (500-800자)                                      │
│                                                                         │
│  ★ 핵심: 규칙이 아닌 질문으로 LLM이 "생각"하게 함                       │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2. Stage별 Input/Output 명세

| Stage | Input | Output | DB Collection | LLM 사용 |
|-------|-------|--------|---------------|----------|
| 1 | emotion, conflict, beat_count | beat_sequence | PLOT_PATTERNS | ❌ |
| 2 | emotion, conflict, location | story_dna (4요소) | STORY_CATALOG | ✅ |
| 3 | beat_sequence, story_dna | beat_modules | STORY_BEATS, STORY_MODULES | ❌ |
| 4 | story_dna, beat_modules, emotion_guide | final_story | - | ✅ |

---

## 5. Stage별 상세 명세

### 5.1. Stage 1: Plot Pattern Selection

```python
class Stage1_PlotSelector:
    """
    목적: 사용자 요청에 맞는 Beat 구조 선택

    Input:
        - emotion: str (Thriller, Healing, Sweet_Potato, Cider, Bizarre, Romantic)
        - conflict: str (갈등 유형)
        - beat_count_preference: int (원하는 Beat 수, default=5)

    Output:
        - beat_sequence: List[str] (예: ["Ki", "Trial", "Shō", "Ten", "Ketsu"])
        - reference_story_id: str (참고 설화 ID)
    """

    def select_plot(self, emotion: str, conflict: str,
                    beat_count_pref: int = 5) -> Dict:

        # 1. Semantic 검색 쿼리 구성
        query = f"{emotion} 감정의 {conflict} 갈등을 다루는 이야기 구조"

        # 2. PLOT_PATTERNS 검색
        results = self.plot_patterns.query(
            query_texts=[query],
            where={
                "$and": [
                    {"emotion": emotion},
                    {"beat_count": {"$gte": beat_count_pref - 1}},
                    {"beat_count": {"$lte": beat_count_pref + 2}}
                ]
            },
            n_results=3
        )

        # 3. 최적 플롯 선택 (beat_count가 가장 가까운 것)
        best_match = self._select_best_match(results, beat_count_pref)

        return {
            "beat_sequence": best_match["beat_sequence"].split(","),
            "reference_story_id": best_match["story_id"],
            "beat_count": best_match["beat_count"]
        }
```

### 5.2. Stage 2: Story DNA Generation

```python
class Stage2_StoryDNAGenerator:
    """
    목적: Story DNA 4요소 생성

    ★ 가장 중요한 Stage - 이야기의 "의미"를 결정

    Input:
        - emotion: str
        - conflict: str
        - location: str

    Output:
        - story_dna: {
            "the_question": str,  # 이 이야기가 답하려는 질문
            "the_lack": str,      # 주인공의 내적 결핍
            "the_cost": str,      # 대가
            "the_irony": str      # 아이러니
          }
    """

    def generate_dna(self, emotion: str, conflict: str,
                     location: str) -> Dict:

        # 1. STORY_CATALOG에서 유사 설화 검색
        similar_stories = self.story_catalog.query(
            query_texts=[f"{location} 배경 {emotion} 감정"],
            where={"emotion": emotion},
            n_results=5
        )

        # 2. 해당 설화들의 Beat 패턴 분석 (선택적)
        story_ids = [m["story_id"] for m in similar_stories["metadatas"][0]]

        # 3. LLM으로 Story DNA 생성
        dna_prompt = self._build_dna_prompt(
            emotion=emotion,
            conflict=conflict,
            location=location,
            reference_stories=similar_stories["documents"][0]
        )

        response = self.llm.generate(dna_prompt)
        story_dna = self._parse_dna_response(response)

        return story_dna

    def _build_dna_prompt(self, emotion, conflict, location,
                          reference_stories) -> str:
        return f"""당신은 이야기의 DNA를 설계하는 스토리 아키텍트입니다.

## 사용자 요청
- 감정: {emotion}
- 갈등 유형: {conflict}
- 배경: {location}

## 참고 설화 요약
{chr(10).join(reference_stories[:3])}

## Story DNA 4요소를 설계하세요:

### 1. The Question (핵심 질문)
이 이야기가 독자에게 던지는 질문은 무엇인가?
- 좋은 예: "사랑은 떠나보내는 것인가?"
- 나쁜 예: "주인공이 행복해질까?" (너무 단순)

### 2. The Lack (캐릭터 결핍)
주인공에게 부족한 것은 무엇인가? (외적이 아닌 내적 결핍)
- 좋은 예: "타인을 믿는 능력", "자신을 용서하는 법"
- 나쁜 예: "돈", "힘" (외적 결핍)

### 3. The Cost (대가)
원하는 것을 얻으려면 무엇을 포기해야 하는가?
- 좋은 예: "진실을 알려면 평화로운 무지를 버려야 한다"
- 나쁜 예: "노력하면 된다" (대가 없음)

### 4. The Irony (아이러니)
이 이야기에서 표면과 이면의 괴리는 무엇인가?
- 좋은 예: "마을을 지키려는 수호신이 사실은 마을에 갇힌 존재"
- 나쁜 예: 없음 (아이러니 없는 이야기는 평면적)

## 출력 형식 (JSON):
```json
{{
    "the_question": "...",
    "the_lack": "...",
    "the_cost": "...",
    "the_irony": "..."
}}
```"""
```

### 5.3. Stage 3: Beat-Module Assembly

```python
class Stage3_BeatModuleAssembler:
    """
    목적: 각 Beat에 사용할 Module 조합

    ★ Cross-Story 조합의 핵심 - 여러 설화 요소 혼합

    Input:
        - beat_sequence: List[str]
        - story_dna: Dict
        - location: str
        - emotion: str

    Output:
        - beat_modules: {
            "Ki": {"place": {...}, "mood": {...}, "character": {...}},
            "Trial": {"event_ref": {...}, "character": {...}},
            ...
          }
    """

    # Beat별 필요 Module 매핑
    BEAT_MODULE_MAP = {
        "Ki": {
            "required": ["place", "mood"],
            "optional": ["character"],
            "story_dna_focus": "the_lack"  # Lack이 드러나야 함
        },
        "Shō": {
            "required": ["character"],
            "optional": ["mood"],
            "story_dna_focus": "the_lack"
        },
        "Trial": {
            "required": ["event_ref", "character"],
            "optional": [],
            "story_dna_focus": "the_cost"  # Cost 직면
        },
        "Crisis": {
            "required": ["event_ref"],
            "optional": ["mood"],
            "story_dna_focus": "the_cost"
        },
        "Ten": {
            "required": ["event_ref"],
            "optional": ["wisdom"],
            "story_dna_focus": "the_irony"  # Irony 드러남
        },
        "Climax": {
            "required": ["event_ref", "character"],
            "optional": [],
            "story_dna_focus": "the_cost"
        },
        "Ketsu": {
            "required": ["mood", "wisdom"],
            "optional": [],
            "story_dna_focus": "the_question"  # Question에 대한 (열린) 답
        }
    }

    def assemble_modules(self, beat_sequence: List[str],
                         story_dna: Dict,
                         location: str,
                         emotion: str) -> Dict:

        beat_modules = {}

        for beat in beat_sequence:
            beat_config = self.BEAT_MODULE_MAP.get(beat, {})
            modules = {}

            # 1. STORY_BEATS에서 참고 사건 검색
            if "event_ref" in beat_config.get("required", []):
                modules["event_ref"] = self._search_beat_reference(
                    beat=beat,
                    emotion=emotion,
                    story_dna_element=story_dna.get(
                        beat_config["story_dna_focus"], ""
                    )
                )

            # 2. STORY_MODULES에서 각 Module 검색
            for module_type in beat_config.get("required", []):
                if module_type == "event_ref":
                    continue  # 이미 처리함

                modules[module_type] = self._search_module(
                    module_type=module_type,
                    beat=beat,
                    location=location,
                    emotion=emotion,
                    story_dna=story_dna,
                    story_dna_focus=beat_config.get("story_dna_focus")
                )

            beat_modules[beat] = modules

        return beat_modules

    def _search_beat_reference(self, beat: str, emotion: str,
                                story_dna_element: str) -> Dict:
        """STORY_BEATS에서 참고할 사건 검색"""

        # Story DNA 요소를 검색 쿼리에 반영
        query = f"{beat} 단계에서 {story_dna_element}이(가) 드러나는 사건"

        results = self.story_beats.query(
            query_texts=[query],
            where={
                "beat": beat,
                "emotion": emotion
            },
            n_results=3
        )

        return {
            "event_text": results["documents"][0][0] if results["documents"][0] else "",
            "function": results["metadatas"][0][0].get("function", "") if results["metadatas"][0] else "",
            "source_story_id": results["metadatas"][0][0].get("source_story_id", "") if results["metadatas"][0] else ""
        }

    def _search_module(self, module_type: str, beat: str,
                       location: str, emotion: str,
                       story_dna: Dict, story_dna_focus: str) -> Dict:
        """STORY_MODULES에서 적합한 Module 검색"""

        MODULE_TYPE_MAP = {
            "place": ("Place", f"{location} 근처"),
            "mood": ("Mood", f"{emotion} 분위기"),
            "character": ("Character", story_dna.get("the_lack", "")),
            "wisdom": ("Wisdom", story_dna.get("the_question", ""))
        }

        db_type, query_hint = MODULE_TYPE_MAP.get(module_type, (module_type.capitalize(), ""))

        # Story DNA 요소를 검색에 반영
        dna_element = story_dna.get(story_dna_focus, "")
        query = f"{query_hint} - {dna_element}"

        results = self.story_modules.query(
            query_texts=[query],
            where={
                "module_type": db_type,
                "usable_in_beats": {"$contains": beat}
            },
            n_results=3
        )

        if not results["documents"][0]:
            return {}

        return {
            "text": results["documents"][0][0],
            "metadata": results["metadatas"][0][0],
            "source_story_id": results["metadatas"][0][0].get("source_story_id", "")
        }
```

### 5.4. Stage 4: Story Generation

```python
class Stage4_StoryGenerator:
    """
    목적: 최종 이야기 생성

    ★ 핵심: 규칙이 아닌 "질문"으로 LLM이 생각하게 함

    Input:
        - story_dna: Dict
        - beat_modules: Dict
        - beat_sequence: List[str]
        - emotion: str

    Output:
        - final_story: str (500-800자)
        - metadata: {used_stories: [], beat_breakdown: {...}}
    """

    def generate_story(self, story_dna: Dict, beat_modules: Dict,
                       beat_sequence: List[str], emotion: str) -> Dict:

        # 1. 프롬프트 구성
        prompt = self._build_generation_prompt(
            story_dna=story_dna,
            beat_modules=beat_modules,
            beat_sequence=beat_sequence,
            emotion=emotion
        )

        # 2. LLM 생성
        response = self.llm.generate(
            prompt,
            max_tokens=2000,
            temperature=0.8  # 창의성을 위해 약간 높게
        )

        # 3. 후처리 및 메타데이터 추출
        final_story = self._postprocess(response)
        metadata = self._extract_metadata(beat_modules)

        return {
            "story": final_story,
            "metadata": metadata
        }

    def _build_generation_prompt(self, story_dna, beat_modules,
                                  beat_sequence, emotion) -> str:

        # Emotion별 가이드 가져오기
        emotion_guide = EMOTION_GUIDES.get(emotion, "")

        # Beat별 소재 정리
        beat_materials = self._format_beat_materials(beat_modules, beat_sequence)

        return f"""당신은 제주 설화를 현대적으로 재해석하는 이야기꾼입니다.

## ⭐ Story DNA (이야기의 핵심 - 반드시 녹여내세요)
- **핵심 질문**: {story_dna["the_question"]}
- **캐릭터 결핍**: {story_dna["the_lack"]}
- **대가**: {story_dna["the_cost"]}
- **아이러니**: {story_dna["the_irony"]}

## Beat 구조
{' → '.join(beat_sequence)}

## Beat별 소재
{beat_materials}

## 6대 원칙 (각 장면에서 반드시 자문하세요)

1. **의미 있는 사건인가?**
   → 이 사건을 빼면 캐릭터의 내면이 달라지는가?

2. **대가 있는 선택인가?**
   → 이 선택에서 캐릭터가 뭔가를 잃는가?

3. **의미 있는 디테일인가?**
   → 이 디테일이 나중에 다시 연결되는가?

4. **말하지 않아도 되는 것은?**
   → 독자가 "아..." 하고 스스로 깨닫는 부분이 있는가?

5. **표면과 이면이 다른가?**
   → 캐릭터가 보여주는 모습과 실제가 다른가?

6. **내적 변화가 있는가?**
   → 처음 캐릭터가 끝의 캐릭터를 보면 놀랄 것인가?

{emotion_guide}

## 생성 지침
- 전체 길이: 500-800자
- 감정을 "설명"하지 말고 "보여"줘라
- Story DNA가 자연스럽게 녹아들어야 한다
- 제주 방언 일부 포함 (자연스럽게)
- **모든 것을 설명하지 마라. 빈 공간을 남겨라.**

## 지금 이야기를 생성하세요:"""
```

---

## 6. 6대 원칙과 Emotion별 가이드

### 6.1. 6대 원칙 상세

| # | 원칙 | 핵심 질문 | 나쁜 예 → 좋은 예 |
|---|------|----------|-----------------|
| 1 | **의미 있는 사건** | "이 사건 전과 후에 캐릭터가 어떻게 달라지는가?" | "괴물이 나타나서 싸웠다" → "3년간 병간호에 지친 청년에게 괴물은 차라리 반가운 적" |
| 2 | **대가 있는 선택** | "이 선택에서 캐릭터가 포기해야 하는 것은?" | "위험→도망" → "도망가면 평생 후회할 것 같다" |
| 3 | **의미 있는 디테일** | "이 디테일이 다른 부분과 어떻게 연결되는가?" | "빨간 지붕 집" → "할아버지가 바다에서 찾을 수 있게 칠함. 10년 전 돌아오지 못함" |
| 4 | **말하지 않는 것** | "독자가 스스로 깨달아야 할 부분은?" | "청년은 슬펐다" → "아버지 장화를 신고 바다로 갔다. 장화는 너무 컸다" |
| 5 | **표면과 이면** | "보이는 것과 실제가 어떻게 다른가?" | "용감한 영웅" → "마을 사람들은 영웅이라 불렀다. 그는 매일 밤 도망치는 꿈을 꿨다" |
| 6 | **내적 변화** | "처음 캐릭터가 끝의 캐릭터를 보면 놀랄 것인가?" | "가난→부자" → "'난 혼자가 편해' → '같이 가도 될까?'" |

### 6.2. Emotion별 강조점 매트릭스

| Emotion | 핵심 강조 원칙 | 이유 | 피해야 할 것 |
|---------|---------------|------|-------------|
| **Thriller** | 말하지 않는 것 + 대가있는 선택 | 불확실성이 긴장을 만듦 | 모든 것을 설명하면 무섭지 않음 |
| **Healing** | 의미있는 디테일 + 내적 변화 | 작은 것들이 위로가 됨 | 큰 사건으로 해결하면 억지 |
| **Sweet_Potato** | 표면과 이면 + 말하지 않는 것 | 알면서 못하는 답답함 | 시원하게 해결하면 장르 위반 |
| **Cider** | 대가있는 선택 + 내적 변화 | 정당한 승리는 희생 후에 | 공짜 승리는 카타르시스 없음 |
| **Bizarre** | 의미있는 사건 + 표면과 이면 | 신비는 "왜?"에서 옴 | 다 설명하면 신비 사라짐 |
| **Romantic** | 내적 변화 + 대가있는 선택 | 사랑은 변화와 희생 | 장애물만 있고 변화 없으면 멜로 X |

### 6.3. Emotion별 프롬프트 가이드

```python
EMOTION_GUIDES = {
    "Thriller": """
## Thriller 특별 지침
- **말하지 마라**: 위협의 정체를 최대한 늦게 보여줘라
- **선택에 시간제한**: "해가 지기 전에 결정해야 한다"
- **탈출구를 막아라**: 도망가면 더 나쁜 일이 생긴다
- **감각을 써라**: "뭔가 잘못됐다"를 설명하지 말고 느끼게 해라
- **평범함 속 균열**: 일상이 갑자기 낯설어지는 순간

예시 Beat 흐름:
Ki: 평화로운 일상 (독자를 안심시켜라)
Trial: 작은 이상 징후 (설명하지 마라)
Ten: 진실의 일부 공개 (전부는 아직)
Ketsu: 공포가 끝나지 않았음을 암시
""",

    "Healing": """
## Healing 특별 지침
- **큰 사건 금지**: 드라마틱한 화해 장면 NO
- **일상의 디테일**: 밥 짓는 소리, 빨래 걷는 손
- **천천히**: 치유는 한 순간에 오지 않는다
- **완전한 해결 금지**: 상처는 남되, 함께 살아가는 법을 배운다
- **침묵의 의미**: 말 없는 순간이 더 많은 것을 전달

예시 Beat 흐름:
Ki: 상처 받은 상태 (직접 설명 X, 행동으로)
Shō: 작은 일상의 반복
Ten: 미세한 변화의 순간
Ketsu: 완전하지 않지만 괜찮아진 상태
""",

    "Sweet_Potato": """
## Sweet_Potato 특별 지침
- **해결하지 마라**: 독자가 답답해야 한다
- **거의 될 뻔**: 희망을 주고 빼앗아라
- **좋은 사람의 실패**: 착한 사람이 손해보는 현실
- **여운**: 끝나고도 계속 생각나게
- **정의의 부재**: 세상이 공정하지 않음을 보여줘라

예시 Beat 흐름:
Ki: 희망적 상황 설정
Trial: 불공정한 상황 발생
Ten: 해결될 것 같은 희망 (그러나...)
Ketsu: 해결되지 않은 채 끝. 여운.
""",

    "Cider": """
## Cider 특별 지침
- **정당한 분노 축적**: 독자가 "때려!"라고 외치게
- **대가 먼저**: 승리 전에 반드시 희생/노력
- **악인의 몰락을 자세히**: 카타르시스는 디테일에서
- **주인공도 변해야**: 복수만 하고 똑같으면 공허
- **승리의 쓴맛**: 이겨도 뭔가 잃는다

예시 Beat 흐름:
Ki: 부당한 상황 (분노 축적)
Trial: 주인공의 노력/희생
Crisis: 거의 질 뻔한 위기
Climax: 정당한 승리 (디테일하게)
Ketsu: 승리했지만 달라진 주인공
""",

    "Bizarre": """
## Bizarre 특별 지침
- **설명하지 마라**: "왜?"에 답하지 않는다
- **일상 속 균열**: 평범한 것이 갑자기 낯설게
- **규칙이 있는 이상함**: 완전 랜덤은 신비가 아님
- **목격자 시점**: 이해 못하는 화자가 전달
- **여백**: 독자의 상상에 맡겨라

예시 Beat 흐름:
Ki: 평범한 일상 (디테일하게)
Trial: 설명 불가능한 일 발생
Ten: 패턴은 보이지만 이유는 모름
Ketsu: 질문만 남기고 끝
""",

    "Romantic": """
## Romantic 특별 지침
- **장애물만으론 부족**: 외부 방해가 아닌 내면 갈등
- **서로를 통해 변화**: 만나서 둘 다 달라져야
- **말 못하는 마음**: 직접 고백보다 행동으로
- **함께라서 가능한 것**: 혼자선 못했을 일을 같이
- **불완전한 사랑**: 완벽한 해피엔딩보다 현실적 관계

예시 Beat 흐름:
Ki: 각자의 결핍 (서로 다른 Lack)
Shō: 우연한 만남, 첫 연결
Trial: 내면 갈등으로 인한 위기
Ten: 서로를 통해 변화
Ketsu: 불완전하지만 함께
"""
}
```

---

## 7. RAG 전략 및 검색 로직

### 7.1. 4-Collection 연동 전략

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    RAG 검색 전략 Overview                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PLOT_PATTERNS (Stage 1)                                               │
│  ├─ 검색 방식: Semantic + Filter                                        │
│  ├─ Query: "{emotion} 감정의 {conflict} 갈등"                           │
│  ├─ Filter: beat_count, emotion, conflict                              │
│  └─ 목적: Beat 시퀀스 결정                                              │
│                                                                         │
│  STORY_CATALOG (Stage 2)                                               │
│  ├─ 검색 방식: Semantic + Filter                                        │
│  ├─ Query: "{location} 배경 {emotion} 감정"                             │
│  ├─ Filter: emotion, admin_region                                      │
│  └─ 목적: Story DNA 생성용 참고 설화                                    │
│                                                                         │
│  STORY_BEATS (Stage 3)                                                 │
│  ├─ 검색 방식: Semantic (Story DNA 요소 반영)                           │
│  ├─ Query: "{beat}에서 {story_dna_element}이 드러나는 사건"             │
│  ├─ Filter: beat, emotion                                              │
│  └─ 목적: Beat별 참고 사건                                              │
│                                                                         │
│  STORY_MODULES (Stage 3)                                               │
│  ├─ 검색 방식: Semantic + Filter                                        │
│  ├─ Query: Story DNA 요소 기반 (예: "{the_lack}" for Character)        │
│  ├─ Filter: module_type, usable_in_beats                               │
│  └─ 목적: Cross-Story 소재 조합                                         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 7.2. 검색 쿼리 최적화

```python
class RAGQueryBuilder:
    """검색 쿼리 최적화"""

    @staticmethod
    def build_plot_query(emotion: str, conflict: str) -> str:
        """PLOT_PATTERNS용 쿼리"""
        return f"{emotion} 감정의 {conflict} 갈등을 다루는 이야기 구조"

    @staticmethod
    def build_catalog_query(emotion: str, location: str) -> str:
        """STORY_CATALOG용 쿼리"""
        return f"{location} 배경의 {emotion} 감정 이야기"

    @staticmethod
    def build_beat_query(beat: str, story_dna_element: str,
                         emotion: str) -> str:
        """STORY_BEATS용 쿼리 - Story DNA 연결"""

        # Beat별 DNA 연결 패턴
        beat_dna_patterns = {
            "Ki": f"이야기 시작에서 '{story_dna_element}'이(가) 드러나는 상황",
            "Trial": f"'{story_dna_element}'로 인한 시련/갈등",
            "Shō": f"'{story_dna_element}'이(가) 심화되는 전개",
            "Crisis": f"'{story_dna_element}' 때문에 위기에 처하는 상황",
            "Ten": f"'{story_dna_element}'에 대한 반전/깨달음",
            "Climax": f"'{story_dna_element}'을(를) 극복하는 절정",
            "Ketsu": f"'{story_dna_element}'에 대한 열린 결말"
        }

        base_query = beat_dna_patterns.get(beat, f"{beat} 단계 사건")
        return f"{emotion} 감정 - {base_query}"

    @staticmethod
    def build_module_query(module_type: str, beat: str,
                           story_dna: Dict, location: str = None) -> str:
        """STORY_MODULES용 쿼리 - Module 타입별 최적화"""

        if module_type == "place":
            return f"{location or '제주'} 근처 장소"

        elif module_type == "character":
            # Character는 The Lack과 연결
            lack = story_dna.get("the_lack", "")
            return f"'{lack}'을(를) 가진 인물"

        elif module_type == "mood":
            # Mood는 감정과 연결
            return f"{story_dna.get('emotion', '')} 분위기"

        elif module_type == "wisdom":
            # Wisdom은 The Question과 연결
            question = story_dna.get("the_question", "")
            return f"'{question}'에 대한 교훈"

        return f"{module_type} {beat}"
```

### 7.3. Cross-Story 조합 전략

```python
class CrossStoryMixer:
    """여러 설화 요소를 창의적으로 혼합"""

    def mix_modules(self, beat_modules: Dict, story_dna: Dict) -> Dict:
        """
        목적: 서로 다른 설화의 요소를 자연스럽게 조합

        원칙:
        1. Story DNA와 연결되는 요소 우선
        2. 같은 설화에서만 가져오지 않음 (최소 2-3개 설화 혼합)
        3. 모순되는 요소 필터링
        """

        mixed = {}
        used_stories = set()

        for beat, modules in beat_modules.items():
            mixed[beat] = {}

            for module_type, module_data in modules.items():
                if not module_data:
                    continue

                # DNA 연관성 점수 계산
                dna_score = self._calculate_dna_relevance(
                    module_data, story_dna
                )

                # 다양성 점수 (이미 사용한 설화면 감점)
                diversity_score = self._calculate_diversity(
                    module_data, used_stories
                )

                # 최종 점수 기반 선택
                final_score = dna_score * 0.7 + diversity_score * 0.3

                mixed[beat][module_type] = {
                    **module_data,
                    "relevance_score": final_score
                }

                # 사용 설화 기록
                source = module_data.get("source_story_id")
                if source:
                    used_stories.add(source)

        return mixed

    def _calculate_dna_relevance(self, module_data: Dict,
                                  story_dna: Dict) -> float:
        """Story DNA와의 연관성 계산"""

        module_text = module_data.get("text", "")

        # DNA 요소 키워드 매칭
        score = 0.0
        for key, value in story_dna.items():
            if isinstance(value, str) and value.lower() in module_text.lower():
                score += 0.25

        return min(score, 1.0)

    def _calculate_diversity(self, module_data: Dict,
                              used_stories: set) -> float:
        """다양성 점수 (다른 설화에서 왔으면 높은 점수)"""

        source = module_data.get("source_story_id", "")

        if source in used_stories:
            return 0.3  # 이미 사용한 설화
        return 1.0  # 새로운 설화
```

---

## 8. 핵심 프롬프트/컨텍스트 엔지니어링

### 8.1. 프롬프트 구조 원칙

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    프롬프트 레이어 구조                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Layer 1: System Context (고정)                                         │
│  ├─ 역할 정의: "제주 설화를 재해석하는 이야기꾼"                         │
│  └─ 기본 제약: 길이, 언어, 방언 사용                                     │
│                                                                         │
│  Layer 2: Story DNA (최우선)                                            │
│  ├─ ⭐ 가장 중요 - 프롬프트 상단 배치                                    │
│  └─ the_question, the_lack, the_cost, the_irony                        │
│                                                                         │
│  Layer 3: 구조 정보                                                      │
│  ├─ Beat 시퀀스                                                         │
│  └─ Beat별 Module 소재                                                  │
│                                                                         │
│  Layer 4: 원칙 (질문 형태)                                              │
│  ├─ 6대 원칙을 "질문"으로                                               │
│  └─ 규칙❌ → 자문✅                                                     │
│                                                                         │
│  Layer 5: Emotion 가이드 (타입별)                                        │
│  ├─ 해당 Emotion 특별 지침                                              │
│  └─ 예시 Beat 흐름                                                      │
│                                                                         │
│  Layer 6: 생성 지시                                                      │
│  └─ "지금 이야기를 생성하세요"                                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 8.2. Story DNA 생성 프롬프트

```python
STORY_DNA_GENERATION_PROMPT = """당신은 이야기의 DNA를 설계하는 스토리 아키텍트입니다.

## 사용자 요청
- 감정: {emotion}
- 갈등 유형: {conflict}
- 배경: {location}

## 참고 설화 요약
{reference_stories}

## Story DNA 4요소를 설계하세요:

### 1. The Question (핵심 질문)
이 이야기가 독자에게 던지는 질문은 무엇인가?
- 이야기가 끝난 후 독자가 생각하게 될 것
- 정답이 없는 열린 질문이어야 함
- 예: "사랑은 떠나보내는 것인가?", "진정한 용기란 무엇인가?"

### 2. The Lack (캐릭터 결핍)
주인공에게 부족한 것은 무엇인가?
- 반드시 내적 결핍 (돈, 힘 같은 외적 결핍 ❌)
- 이야기를 통해 채워지거나 인정하게 되는 것
- 예: "타인을 믿는 능력", "자신을 용서하는 법", "소속감"

### 3. The Cost (대가)
원하는 것을 얻으려면 무엇을 포기해야 하는가?
- 공짜 점심은 없다
- 선택에는 반드시 포기가 따른다
- 예: "진실을 알려면 평화로운 무지를 버려야 한다"

### 4. The Irony (아이러니)
이 이야기에서 표면과 이면의 괴리는 무엇인가?
- 보이는 것과 실제가 다른 지점
- 이야기에 깊이를 더하는 반전
- 예: "마을을 지키려는 수호신이 사실은 마을에 갇힌 존재"

## 출력 형식:
```json
{{
    "the_question": "...",
    "the_lack": "...",
    "the_cost": "...",
    "the_irony": "..."
}}
```

{emotion}의 감정과 {conflict} 갈등에 맞는 Story DNA를 설계하세요:"""
```

### 8.3. 최종 이야기 생성 프롬프트

```python
FINAL_STORY_GENERATION_PROMPT = """당신은 제주 설화를 현대적으로 재해석하는 이야기꾼입니다.

## ⭐⭐⭐ Story DNA (이야기의 핵심) ⭐⭐⭐
이 4가지가 이야기 전체에 자연스럽게 녹아있어야 합니다:

- **핵심 질문**: {the_question}
  → 이야기 끝에 독자가 이 질문을 생각하게 해야 합니다

- **캐릭터 결핍**: {the_lack}
  → Ki에서 드러나고, 이야기 전체에서 주인공을 움직이는 동력

- **대가**: {the_cost}
  → Trial/Crisis에서 주인공이 직면해야 하는 것

- **아이러니**: {the_irony}
  → Ten에서 드러나며, 이야기에 깊이를 더합니다

---

## Beat 구조: {beat_sequence}

## Beat별 소재

{beat_materials}

---

## 📋 6대 원칙 체크리스트

각 Beat를 쓰기 전에 반드시 자문하세요:

☐ **의미 있는 사건인가?**
  "이 사건을 빼면 캐릭터의 내면이 달라지는가?"

☐ **대가 있는 선택인가?**
  "이 선택에서 캐릭터가 뭔가를 잃는가?"

☐ **의미 있는 디테일인가?**
  "이 디테일이 나중에 다시 연결되는가?"

☐ **말하지 않아도 되는 것은?**
  "독자가 '아...' 하고 스스로 깨닫는 부분이 있는가?"

☐ **표면과 이면이 다른가?**
  "캐릭터가 보여주는 모습과 실제가 다른가?"

☐ **내적 변화가 있는가?**
  "처음 캐릭터가 끝의 캐릭터를 보면 놀랄 것인가?"

---

{emotion_guide}

---

## 🚫 피해야 할 것들

1. **감정 설명 금지**: "슬펐다" ❌ → 행동으로 보여주기 ✅
2. **모든 것 설명 금지**: 독자가 채울 빈 공간을 남겨라
3. **당연한 선택 금지**: 위험→도망 같은 뻔한 선택 ❌
4. **장식적 디테일 금지**: 스토리와 연결되지 않는 묘사 ❌
5. **완벽한 해결 금지**: 열린 결말, 남는 여운

## ✅ 생성 지침

- 전체 길이: 500-800자
- 제주 방언 일부 포함 (자연스럽게)
- Story DNA가 매 Beat에 녹아있어야 함
- 마지막 문장은 여운을 남겨라

---

## 지금 이야기를 생성하세요:"""
```

### 8.4. 컨텍스트 최적화 전략

```python
class ContextOptimizer:
    """프롬프트 컨텍스트 최적화"""

    MAX_CONTEXT_LENGTH = 4000  # 토큰 기준

    def optimize_context(self, story_dna: Dict, beat_modules: Dict,
                          emotion_guide: str) -> str:
        """컨텍스트 크기 최적화"""

        # 1. 필수 요소 (항상 포함)
        essential = {
            "story_dna": story_dna,  # ~200 tokens
            "principles": self._get_principles(),  # ~300 tokens
        }

        # 2. 중요 요소 (가능하면 포함)
        important = {
            "beat_modules": self._summarize_modules(beat_modules),  # ~400 tokens
            "emotion_guide": self._truncate_guide(emotion_guide),  # ~300 tokens
        }

        # 3. 보조 요소 (공간 여유 시 포함)
        optional = {
            "examples": self._get_examples(story_dna["emotion"]),  # ~200 tokens
        }

        # 토큰 계산 및 조정
        context = self._build_context(essential, important, optional)

        return context

    def _summarize_modules(self, beat_modules: Dict) -> str:
        """Module 정보 요약"""

        summary = []
        for beat, modules in beat_modules.items():
            beat_summary = f"### {beat}\n"
            for module_type, data in modules.items():
                if data:
                    # 핵심 정보만 추출 (200자 제한)
                    text = data.get("text", "")[:200]
                    source = data.get("source_story_id", "")
                    beat_summary += f"- {module_type}: {text}... (출처: {source})\n"
            summary.append(beat_summary)

        return "\n".join(summary)

    def _truncate_guide(self, guide: str, max_length: int = 500) -> str:
        """Emotion 가이드 길이 조절"""

        if len(guide) <= max_length:
            return guide

        # 핵심 지침만 추출
        lines = guide.split("\n")
        important_lines = [l for l in lines if l.startswith("-") or l.startswith("##")]

        return "\n".join(important_lines)[:max_length]
```

---

## 9. 코드베이스 설계

### 9.1. 디렉토리 구조

```
jeju-stories/
├── scripts/
│   ├── story_generator.py          # 메인 엔진 (리팩토링 대상)
│   ├── init_vector_db.py           # DB 초기화 (완료)
│   └── test_vector_db.py           # DB 테스트
│
├── src/
│   └── narrative_engine/           # 신규 패키지
│       ├── __init__.py
│       ├── pipeline.py             # 4-Stage 파이프라인 오케스트레이터
│       ├── stages/
│       │   ├── __init__.py
│       │   ├── stage1_plot.py      # Plot Pattern Selection
│       │   ├── stage2_dna.py       # Story DNA Generation
│       │   ├── stage3_assembly.py  # Beat-Module Assembly
│       │   └── stage4_generation.py # Story Generation
│       ├── rag/
│       │   ├── __init__.py
│       │   ├── query_builder.py    # RAG 쿼리 빌더
│       │   ├── retriever.py        # 검색 실행기
│       │   └── mixer.py            # Cross-Story 조합기
│       ├── prompts/
│       │   ├── __init__.py
│       │   ├── dna_prompt.py       # Story DNA 프롬프트
│       │   ├── generation_prompt.py # 생성 프롬프트
│       │   └── emotion_guides.py   # Emotion별 가이드
│       └── utils/
│           ├── __init__.py
│           └── validators.py       # 품질 검증
│
├── chroma_db/                      # Vector DB (4-Collection)
├── enriched/                       # 246개 enriched JSON
└── docs/
    ├── Vector_DB_Schema.md         # DB 스키마 (완료)
    └── Narrative_Engine_Architecture.md  # 본 문서
```

### 9.2. 핵심 클래스 설계

```python
# pipeline.py
class NarrativeEnginePipeline:
    """4-Stage 파이프라인 오케스트레이터"""

    def __init__(self, db_path: str, llm_wrapper):
        self.db_client = chromadb.PersistentClient(path=db_path)
        self.llm = llm_wrapper

        # Stage 초기화
        self.stage1 = Stage1_PlotSelector(self.db_client)
        self.stage2 = Stage2_StoryDNAGenerator(self.db_client, self.llm)
        self.stage3 = Stage3_BeatModuleAssembler(self.db_client)
        self.stage4 = Stage4_StoryGenerator(self.llm)

    def generate(self, user_input: Dict) -> Dict:
        """전체 파이프라인 실행"""

        # Stage 1: Plot Pattern Selection
        plot_result = self.stage1.select_plot(
            emotion=user_input["emotion"],
            conflict=user_input["conflict"],
            beat_count_pref=user_input.get("beat_count", 5)
        )

        # Stage 2: Story DNA Generation
        dna_result = self.stage2.generate_dna(
            emotion=user_input["emotion"],
            conflict=user_input["conflict"],
            location=user_input["location"]
        )

        # Stage 3: Beat-Module Assembly
        modules_result = self.stage3.assemble_modules(
            beat_sequence=plot_result["beat_sequence"],
            story_dna=dna_result,
            location=user_input["location"],
            emotion=user_input["emotion"]
        )

        # Stage 4: Story Generation
        story_result = self.stage4.generate_story(
            story_dna=dna_result,
            beat_modules=modules_result,
            beat_sequence=plot_result["beat_sequence"],
            emotion=user_input["emotion"]
        )

        return {
            "story": story_result["story"],
            "metadata": {
                "plot_pattern": plot_result,
                "story_dna": dna_result,
                "used_modules": modules_result,
                "generation_metadata": story_result["metadata"]
            }
        }
```

### 9.3. 인터페이스 명세

```python
# 사용자 입력 스키마
UserInput = {
    "emotion": str,           # Required: Thriller, Healing, Sweet_Potato, Cider, Bizarre, Romantic
    "conflict": str,          # Required: 갈등 유형
    "location": str,          # Required: 위치 (예: "성산읍")
    "travel_context": str,    # Optional: walking, driving, resting
    "beat_count": int,        # Optional: 원하는 Beat 수 (default: 5)
    "preferences": Dict       # Optional: 추가 선호도
}

# 출력 스키마
GenerationOutput = {
    "story": str,             # 생성된 이야기 (500-800자)
    "metadata": {
        "plot_pattern": {
            "beat_sequence": List[str],
            "reference_story_id": str,
            "beat_count": int
        },
        "story_dna": {
            "the_question": str,
            "the_lack": str,
            "the_cost": str,
            "the_irony": str
        },
        "used_modules": Dict[str, Dict],  # Beat별 사용 모듈
        "generation_metadata": {
            "used_stories": List[str],    # Cross-Story 출처
            "generation_time": float
        }
    }
}
```

---

## 10. 품질 검증 체계

### 10.1. 자동 검증 체크리스트

```python
class StoryValidator:
    """생성된 이야기 품질 검증"""

    def validate(self, story: str, story_dna: Dict,
                 beat_sequence: List[str]) -> Dict:
        """
        품질 검증 실행

        Returns:
            {
                "is_valid": bool,
                "score": float (0-1),
                "checks": {
                    "length": bool,
                    "dna_presence": Dict[str, bool],
                    "beat_presence": Dict[str, bool],
                    "no_direct_emotion": bool,
                    "has_dialogue_or_action": bool
                },
                "warnings": List[str],
                "suggestions": List[str]
            }
        """

        checks = {}
        warnings = []
        suggestions = []

        # 1. 길이 검증 (500-800자)
        checks["length"] = 500 <= len(story) <= 800
        if not checks["length"]:
            if len(story) < 500:
                suggestions.append("이야기가 너무 짧습니다. 디테일을 추가하세요.")
            else:
                suggestions.append("이야기가 너무 깁니다. 불필요한 부분을 줄이세요.")

        # 2. Story DNA 반영 검증
        checks["dna_presence"] = {}
        for key, value in story_dna.items():
            # DNA 요소의 키워드가 이야기에 반영되었는지 (직접/간접)
            keywords = value.split()[:3]  # 핵심 키워드 추출
            presence = any(kw in story for kw in keywords)
            checks["dna_presence"][key] = presence

            if not presence:
                warnings.append(f"'{key}'가 이야기에 충분히 반영되지 않았습니다.")

        # 3. Beat 존재 검증 (각 Beat의 흔적)
        checks["beat_presence"] = {}
        for beat in beat_sequence:
            # Beat 전환 표시 또는 해당 기능의 존재
            checks["beat_presence"][beat] = self._check_beat_presence(story, beat)

        # 4. 직접적 감정 서술 검증 ("슬펐다", "기뻤다" 등 금지)
        emotion_words = ["슬펐다", "기뻤다", "화났다", "무서웠다", "행복했다"]
        checks["no_direct_emotion"] = not any(word in story for word in emotion_words)
        if not checks["no_direct_emotion"]:
            warnings.append("감정을 직접 서술하지 말고 행동으로 보여주세요.")

        # 5. 대화 또는 행동 존재 검증
        has_dialogue = '"' in story or "'" in story
        has_action = any(verb in story for verb in ["했다", "갔다", "봤다", "말했다"])
        checks["has_dialogue_or_action"] = has_dialogue or has_action

        # 점수 계산
        total_checks = (
            [checks["length"], checks["no_direct_emotion"],
             checks["has_dialogue_or_action"]] +
            list(checks["dna_presence"].values()) +
            list(checks["beat_presence"].values())
        )
        score = sum(total_checks) / len(total_checks)

        return {
            "is_valid": score >= 0.7,
            "score": score,
            "checks": checks,
            "warnings": warnings,
            "suggestions": suggestions
        }

    def _check_beat_presence(self, story: str, beat: str) -> bool:
        """Beat의 기능이 이야기에 존재하는지 확인"""

        beat_indicators = {
            "Ki": ["처음", "시작", "옛날", "어느 날"],
            "Shō": ["그러던", "점점", "계속"],
            "Trial": ["하지만", "그런데", "문제", "어려움"],
            "Crisis": ["결국", "위기", "급기야"],
            "Ten": ["그때", "알게", "깨달", "사실은"],
            "Climax": ["마침내", "드디어"],
            "Ketsu": ["그 후", "지금도", "아직도"]
        }

        indicators = beat_indicators.get(beat, [])
        return any(ind in story for ind in indicators)
```

### 10.2. 수동 검증 기준

| 검증 항목 | 기준 | 점수 |
|----------|------|------|
| **의미 있는 사건** | 사건을 빼면 캐릭터 내면이 달라지는가? | 0-2점 |
| **대가 있는 선택** | 선택에서 캐릭터가 뭔가를 잃는가? | 0-2점 |
| **의미 있는 디테일** | 디테일이 나중에 연결되는가? | 0-2점 |
| **말하지 않는 것** | 독자가 스스로 깨닫는 부분이 있는가? | 0-2점 |
| **표면과 이면** | 보이는 것과 실제가 다른가? | 0-2점 |
| **내적 변화** | 처음 캐릭터가 끝의 캐릭터를 보면 놀랄까? | 0-2점 |
| **총점** | 12점 만점, 8점 이상 통과 | |

---

## 11. 구현 로드맵

### 11.1. Phase 1: 기반 구축 (Week 1)

| Task | 설명 | 우선순위 |
|------|------|----------|
| 4-Collection DB 검증 | init_vector_db.py 실행 및 데이터 확인 | P0 |
| RAG 쿼리 테스트 | 각 Collection별 검색 품질 테스트 | P0 |
| 프롬프트 템플릿 작성 | Story DNA, 생성 프롬프트 완성 | P0 |

### 11.2. Phase 2: 파이프라인 구현 (Week 2)

| Task | 설명 | 우선순위 |
|------|------|----------|
| Stage 1 구현 | Plot Pattern Selection | P0 |
| Stage 2 구현 | Story DNA Generation | P0 |
| Stage 3 구현 | Beat-Module Assembly | P0 |
| Stage 4 구현 | Story Generation | P0 |

### 11.3. Phase 3: 통합 및 테스트 (Week 3)

| Task | 설명 | 우선순위 |
|------|------|----------|
| 파이프라인 통합 | 4-Stage 연결 | P0 |
| 품질 검증 구현 | StoryValidator | P1 |
| E2E 테스트 | 전체 플로우 테스트 | P0 |
| 성능 최적화 | 응답 시간 개선 | P1 |

### 11.4. Phase 4: 고도화 (Week 4+)

| Task | 설명 | 우선순위 |
|------|------|----------|
| Cross-Story 조합 개선 | 더 창의적인 혼합 | P1 |
| Emotion 가이드 확장 | 추가 감정 유형 | P2 |
| 사용자 피드백 반영 | 품질 개선 | P1 |
| A/B 테스트 | 프롬프트 최적화 | P2 |

---

---

## 12. Personalization Layer

> **Status**: ✅ Implemented (2025-12-12)
> **Location**: `/scripts/personalization/`

### 12.1. 개요

기존 4-Stage Engine을 감싸는 개인화 레이어. 사용자의 심리적 상태(User DNA)를 기반으로 스토리를 선택/생성하고, 맥락에 맞는 프레이밍(Prologue/Epilogue)을 추가합니다.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PERSONALIZATION PIPELINE                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  STAGE 0: Context & DNA Inference                                       │
│  ─────────────────────────────────────────────────────────────────────  │
│  Input:  mood_selection, GPS, timestamp, weather                        │
│  Process: 컨텍스트 수집 → User DNA 추론                                  │
│  Output: UserDNA, ContextData                                           │
│                                                                         │
│                         ↓                                               │
│            ┌─────────────┴─────────────┐                                │
│            ↓                           ↓                                │
│   [Selection Mode]              [Generation Mode]                       │
│   기존 스토리 선택               4-Stage Engine                          │
│   (story_catalog)               (새 스토리 생성)                         │
│            │                           │                                │
│            └─────────────┬─────────────┘                                │
│                          ↓                                              │
│                                                                         │
│  STAGE 5: Framing Generation                                            │
│  ─────────────────────────────────────────────────────────────────────  │
│  Input:  main_story, UserDNA, Context                                   │
│  Process: Prologue + Epilogue 생성                                      │
│  Output: FramedStory { prologue, main_story, epilogue }                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 12.1.1. Generation Mode에서 User DNA 흐름

Generation Mode에서 User DNA는 `preferences` dict를 통해 4-Stage Engine에 전달되어, **Stage 2**와 **Stage 4**의 LLM 프롬프트에 직접 주입됩니다.

```
User DNA (wound, desire, keywords)
       ↓
   preferences dict로 변환
   {
     "user_dna_wound": wound.value,
     "user_dna_desire": desire.value,
     "resonance_keywords": keywords[:5]
   }
       ↓
┌──────────────────────────────────────────────────┐
│  Stage 2: Story DNA Generation                   │
│  ─────────────────────────────────────────────   │
│  프롬프트에 "사용자 심리 상태" 섹션 삽입:          │
│                                                  │
│  ## 🧬 사용자 심리 상태 (User DNA) - 반드시 반영  │
│  - **상처 (Wound)**: {wound} → The Lack에 반영   │
│  - **갈망 (Desire)**: {desire} → The Question에  │
│  - **공명 키워드**: 배경/아이러니에 활용          │
│                                                  │
│  결과: User DNA를 반영한 Generated Story DNA     │
│  (the_question, the_lack, the_cost, the_irony)  │
└──────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────┐
│  Stage 3: Beat-Module Assembly                   │
│  ─────────────────────────────────────────────   │
│  (User DNA 직접 개입 없음)                       │
│  Generated Story DNA 기반으로 모듈 검색          │
└──────────────────────────────────────────────────┘
       ↓
┌──────────────────────────────────────────────────┐
│  Stage 4: Story Generation                       │
│  ─────────────────────────────────────────────   │
│  프롬프트에 "개인화 지침" 섹션 삽입:              │
│                                                  │
│  ## 🎯 개인화 지침 (User DNA 기반)               │
│  1. **주인공**: {wound}의 고통을 겪는 인물        │
│     → 독자가 "이건 내 이야기"로 느끼도록         │
│  2. **여정**: {desire}를 향한 과정을 반영         │
│     → 행동과 선택에 갈망 투영                    │
│  3. **분위기**: 공명 키워드로 배경 묘사           │
│                                                  │
│  결과: User DNA가 녹아든 최종 이야기             │
└──────────────────────────────────────────────────┘
```

**코드 참조:**
- `engine_integration.py` (line 291-302): User DNA → preferences 변환
- `story_generator.py` `_build_dna_prompt()` (line 467-488): Stage 2 프롬프트 주입
- `story_generator.py` `_build_generation_prompt()` (line 888-907): Stage 4 프롬프트 주입

### 12.2. User DNA 구조

```python
@dataclass
class UserDNA:
    the_wound: WoundType     # 사용자의 상처/결핍
    the_desire: DesireType   # 사용자의 갈망
    resonance_keywords: List[str]  # 공명 키워드 (5-10개)
    intensity: float         # 감정 강도 (0.0-1.0)
    confidence: float        # 추론 신뢰도 (0.0-1.0)

class WoundType(Enum):
    EXHAUSTION = "exhaustion"       # 소진, 지침
    LOSS = "loss"                   # 상실, 그리움
    STAGNATION = "stagnation"       # 정체, 막힘
    DISCONNECTION = "disconnection" # 단절, 고립
    INSIGNIFICANCE = "insignificance"  # 무의미, 존재감 부재
    ARROGANCE = "arrogance"         # 교만, 자만
    FEAR = "fear"                   # 두려움, 불안
    GRIEF = "grief"                 # 슬픔, 애도
    RESTLESSNESS = "restlessness"   # 불안정, 초조

class DesireType(Enum):
    REST = "rest"                   # 휴식, 쉼
    MEANING = "meaning"             # 의미, 목적
    TRANSFORMATION = "transformation"  # 변화, 성장
    RECONNECTION = "reconnection"   # 재연결, 관계회복
    DISCOVERY = "discovery"         # 발견, 깨달음
    HEALING = "healing"             # 치유, 회복
    COURAGE = "courage"             # 용기, 도전
    PEACE = "peace"                 # 평화, 안정
    LEGACY = "legacy"               # 유산, 흔적
    MINDFULNESS = "mindfulness"     # 현재, 순간
```

### 12.3. 3-Question UI → DNA 추론

사용자에게 직접 물어보지 않고, 은유적 선택지로 DNA 추론:

| Mood Selection | the_wound | the_desire | 설명 |
|----------------|-----------|------------|------|
| **release** 🌊 "비우고 싶다" | exhaustion | rest | 지침, 쉼 필요 |
| **presence** 🌿 "지금 여기" | disconnection | mindfulness | 단절, 현재 집중 |
| **courage** ⛰️ "도전하고 싶다" | stagnation | transformation | 정체, 변화 갈망 |
| **memory** 🕯️ "그리움" | loss | reconnection | 상실, 재연결 |
| **curiosity** 🔮 "신비로움" | insignificance | discovery | 무의미, 발견 |

### 12.4. Resonance Scoring

User DNA ↔ Story DNA 매칭 점수:

```python
def calculate_score(user_dna, story_metadata):
    score = 0.0

    # Wound 매칭 (40%)
    if user_dna.the_wound.value in story_metadata.get("wounds_addressed", []):
        score += 0.4

    # Desire 매칭 (40%)
    if user_dna.the_desire.value in story_metadata.get("desires_fulfilled", []):
        score += 0.4

    # Keyword 오버랩 (20%)
    triggers = story_metadata.get("resonance_triggers", [])
    overlap = len(set(user_dna.resonance_keywords) & set(triggers))
    score += 0.2 * min(overlap / 3, 1.0)

    # 위치 보너스 (+10%)
    if user_dna.context_location == story_metadata.get("location"):
        score += 0.1

    return min(score, 1.0)
```

### 12.5. 모듈 구조

```
scripts/personalization/
├── __init__.py              # 모듈 export
├── models.py                # UserDNA, StoryDNA, ContextData 등
├── dna_inference.py         # MoodSelection → UserDNA 변환
├── resonance_scorer.py      # DNA 매칭 스코어링
├── context_collector.py     # GPS/시간/날씨 수집 (25+ 제주 장소)
├── framing_generator.py     # Prologue/Epilogue 생성
├── story_selector.py        # Hybrid Search 스토리 선택
├── pipeline.py              # 독립 파이프라인
└── engine_integration.py    # 4-Stage Engine 통합
```

### 12.6. 사용 예시

```python
from personalization import create_personalized_engine

# Selection Mode (기존 스토리 선택)
engine = create_personalized_engine(
    chroma_path="/path/to/chroma_db",
    mode="selection"
)

# Generation Mode (4-Stage 생성)
engine = create_personalized_engine(
    chroma_path="/path/to/chroma_db",
    mode="generation"
)

# 실행
response = engine.generate(
    mood_selection_id="release",  # 비우고 싶다
    location="천지연폭포",
    weather="clear"
)

# 결과
print(response.framed_story.prologue)   # 개인화된 도입부
print(response.framed_story.main_story) # 매칭된 스토리
print(response.framed_story.epilogue)   # 개인화된 마무리
print(f"공명 점수: {response.resonance_score}")
```

### 12.7. Pending: Story DNA 메타데이터 추출

현재 story_catalog에는 기본 메타데이터만 존재. 더 정밀한 매칭을 위해 추가 추출 필요:

- `wounds_addressed`: 스토리가 다루는 상처 유형
- `desires_fulfilled`: 스토리가 충족시키는 갈망
- `resonance_triggers`: 공명 키워드

> 상세: [PENDING_STORY_DNA_EXTRACTION.md](./PENDING_STORY_DNA_EXTRACTION.md)

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2025-12-08 | v1.0 | 초안 작성 |
| 2025-12-10 | v2.0 | 3-Layer 구조 설계 |
| 2025-12-11 | v3.0 | Story DNA + 6대 원칙 프레임워크 도입 |
| 2025-12-11 | v4.0 | PRD 수준 전면 개편: 4-Stage 파이프라인 I/O 명세, RAG 전략, 프롬프트 엔지니어링, 코드베이스 설계, 품질 검증 체계, 구현 로드맵 추가 |
| 2025-12-12 | **v5.0** | **Personalization Layer 추가**: User DNA 기반 개인화, Stage 0 (Context/DNA) + Stage 5 (Framing), Selection/Generation 듀얼 모드, 25+ 제주 장소 DB |
| 2025-12-17 | **v5.1** | **용어 명확화**: "저장용 Story DNA" vs "생성용 Story DNA" 구분 추가, 관련 문서(DATA_STRUCTURE_ENRICHED.md, Vector_DB_Schema.md) 동기화, PENDING_STORY_DNA_EXTRACTION.md 아카이브 이동 |
| 2025-12-19 | **v5.2** | **Generation Mode User DNA 흐름 명세 추가**: Section 12.1.1에 User DNA가 preferences dict를 통해 Stage 2, 4에 주입되는 과정 상세 다이어그램 및 코드 참조 추가 |
