# 제주 설화 데이터 구조: Enriched 버전

## 1. 분석 데이터 개요

### 총 데이터 규모
- **전체 설화**: 246개
- **데이터 출처**: 제주특별자치도 및 한국학중앙연구원 설화 채록본

### Category (설화 분류) 분포
| Category | 개수 | 비율 |
|----------|------|------|
| 전설 | 171 | 69.5% |
| 신화 | 62 | 25.2% |
| 민담 | 13 | 5.3% |

---

## 2. 데이터 전처리의 목적

### 핵심 목표: Modular Story Synthesis (모듈 기반 이야기 합성)

**정의**: 원본 설화를 재사용 가능한 모듈(Module) 단위로 분해(Decomposition)하고, 사용자 맥락에 맞게 재조합(Recombination)하여 새로운 이야기를 생성하는 시스템

**전문 용어**:
- **Data Decomposition**: 전체 설화를 독립적 구성 요소로 분해
- **Modularization**: 재사용 가능한 단위(Character, Place, Event, Mood, Wisdom)로 모듈화
- **Contextualized Synthesis**: 사용자 맥락(MBTI, 위치, 감정)에 맞춘 맞춤형 합성

### 이론적 근거

#### 1. Propp's Morphology of the Folktale (Vladimir Propp, 1928)

**학자**: Vladimir Propp (러시아 민속학자)
**이론 명칭**: 민담의 형태론 (Morphology of the Folktale)
**핵심 내용**:
> "민담은 31개의 기능(Function)과 7개의 역할(Role)로 분해 가능하며, 이들의 조합으로 무한한 이야기를 생성할 수 있다"

#### 2. Component-Based Software Engineering (Clemens Szyperski, 1997)

**학자**: Clemens Szyperski (소프트웨어 공학자)
**이론 명칭**: 컴포넌트 기반 소프트웨어 공학
**핵심 내용**:
> "복잡한 시스템을 독립적이고 재사용 가능한 컴포넌트로 분해하면 유연성과 확장성이 향상된다"

---

## 3. 구조화 정의

### attributes (메타데이터)

**정의**: 설화의 서사적, 감정적, 구조적 특성을 나타내는 메타데이터 집합

**목적**:
1. **검색 최적화**: 사용자 프로필(MBTI, 위치, 감정)에 맞는 설화 필터링
2. **모듈 추출**: Character, Place, Event 등 재사용 가능한 요소 식별
3. **서사 구조 파악**: Plot Point와 Beat 구조를 통한 이야기 전개 패턴 분석

### attributes 구성 항목

| 항목 | 타입 | 설명 | 세부 카테고리 | 선정 이유 |
|------|------|------|--------------|---------|
| **summary** | String | 현대적 요약 | - | 서사 스키마를 압축 표현하여 빠른 이해 지원 |
| **emotion** | String | 핵심 감정 | Sweet_Potato, Healing, Bizarre, Thriller, Cider, Mysterious, Hopeful, Calm, Tense | 사용자 감정 상태에 맞는 콘텐츠 추천 |
| **conflict** | String | 갈등 유형 | Rivalry, Lack, Obstacle, Mystery, Taboo, Inner_Conflict, Nature_Challenge, Social_Tension, Moral_Dilemma | 서사의 핵심 동력으로 이야기 전개 방향 결정 |
| **keywords** | Array[String] | 핵심 키워드 | 자유 형식 (예: ["개", "닭", "원한", "속담"]) | 의미적 검색을 위한 텍스트 벡터화 |
| **entities** | Array[Object] | 등장 존재 | name, description, type (Human, Animal, Spirit, Monster, Object, Abstract) | 인물 스키마 표현으로 재사용 가능한 캐릭터 모듈 추출 |
| **roles** | Array[Object] | 서사적 역할 | entity_name, type (Protagonist, Antagonist, Helper, Trickster, Victim, Neutral) | 서사적 기능에 따른 인물 분류로 플롯 구성 지원 |
| **terrains** | Array[Object] | 배경 지형 | type (Village, Mountain, Sea, Cave, Forest, Road, River, Waterfall, Other), description | 공간 스키마 표현으로 재사용 가능한 배경 모듈 추출 |
| **location_context** | Object | 지리 정보 | primary_place (예: "제주", "성산일출봉"), admin_region (예: "서귀포시") | 지역 기반 맞춤형 이야기 생성 |
| **plot_points** | Array[Object] | 플롯 포인트 | beat, event, function (다음 섹션 참조) | 서사 전개 패턴 분석 및 Beat별 사건 재조합 |
| **story_dna** | Object | 저장용 Story DNA | wounds_addressed, desires_fulfilled, resonance_triggers 등 | User DNA ↔ Story 매칭 및 검색 |

### attributes 이론적 근거

#### 1. Information Retrieval Theory (Gerard Salton, 1960s)

**학자**: Gerard Salton (정보 검색 이론 창시자)
**이론 명칭**: Vector Space Model
**핵심 내용**:
> "문서를 메타데이터 벡터로 표현하면 의미적 유사도 기반 검색이 가능하다"

**본 연구 적용**:
- **keywords**: 의미적 검색을 위한 텍스트 벡터화
- attributes의 각 필드(emotion, conflict, entities, terrains)를 벡터 차원으로 활용하여 사용자 쿼리와 설화 메타데이터 간 코사인 유사도 계산

#### 2. Schema Theory (Frederic Bartlett, 1932)

**학자**: Frederic Bartlett (인지심리학자)
**이론 명칭**: Schema Theory (스키마 이론)
**핵심 내용**:
> "사람은 이야기를 '스키마'(구조화된 지식 틀)로 이해하고 기억한다"

**본 연구 적용**:
- **summary**: 서사 스키마의 압축 표현
- **entities**: 인물 스키마 (Character Schema) 표현
- **terrains**: 공간 스키마 (Spatial Schema) 표현
- **plot_points**: 서사 스키마 (Narrative Schema) 표현

#### 3. Affective Computing (Rosalind Picard, 1995)

**학자**: Rosalind Picard (MIT 미디어랩)
**이론 명칭**: Affective Computing (감성 컴퓨팅)
**핵심 내용**:
> "컴퓨터가 인간의 감정을 인식하고 반응하면 더 나은 사용자 경험을 제공할 수 있다"

**본 연구 적용**:
- **emotion**: 사용자 감정 상태에 맞는 콘텐츠 추천

#### 4. Propp's Functional Analysis (Vladimir Propp, 1928)

**학자**: Vladimir Propp (러시아 민속학자)
**이론 명칭**: 민담의 형태론 - 31개 기능 분석
**핵심 내용**:
> "모든 민담은 31개의 기본 기능으로 분해 가능하며, 갈등은 서사의 핵심 동력이다"

**본 연구 적용**:
- **conflict**: 서사의 핵심 동력으로 이야기 전개 방향 결정
- **roles**: 서사적 기능에 따른 인물 분류 (7개 역할)

#### 5. Location-Based Services Theory

**개념**: 위치 정보를 활용한 맞춤형 서비스 제공
**핵심 내용**:
> "사용자의 물리적 위치를 기반으로 관련성 높은 콘텐츠를 제공할 수 있다"

**본 연구 적용**:
- **location_context**: 지역 기반 맞춤형 이야기 생성

---

### story_dna (Stored Story DNA) 구조

**정의**: User DNA와 매칭하여 개인화된 스토리 검색/선택에 사용되는 메타데이터

**⚠️ 주의**: 이 필드는 **저장용 Story DNA**입니다. `the_question`, `the_lack`, `the_cost`, `the_irony`는 여기에 저장되지 않으며, Stage 2에서 LLM이 동적으로 생성합니다. (→ Narrative_Engine_Architecture.md 참조)

| 필드 | 타입 | 설명 | 허용값 |
|------|------|------|--------|
| **wounds_addressed** | Array[String] | 이 설화가 다루는 상처 유형 | exhaustion, loss, stagnation, disconnection, insignificance, arrogance, fear, grief |
| **desires_fulfilled** | Array[String] | 이 설화가 채워주는 갈망 | rest, meaning, transformation, reconnection, discovery, healing, courage, peace, legacy |
| **primary_wound** | String | 대표 상처 (wounds_addressed 중 1개) | 위와 동일 |
| **primary_desire** | String | 대표 갈망 (desires_fulfilled 중 1개) | 위와 동일 |
| **resonance_triggers** | Array[String] | 공명 키워드 (5-10개) | 자유 형식 (한글) |
| **emotional_arc** | String | 감정 전개 흐름 | 자유 형식 |
| **narrative_themes** | Array[String] | 서사 테마 | 자유 형식 |

**예시**:
```json
"story_dna": {
  "wounds_addressed": ["loss", "insignificance"],
  "desires_fulfilled": ["reconnection", "meaning"],
  "primary_wound": "loss",
  "primary_desire": "reconnection",
  "resonance_triggers": ["개", "닭", "원한", "속담", "복수"],
  "emotional_arc": "반지 분실 → 수색 → 속임수 → 원한",
  "narrative_themes": ["동물", "원한", "속임수", "속담"]
}
```

### story_dna 이론적 근거

#### 1. Jungian Archetypes (Carl Jung, 1934)

**학자**: Carl Jung (분석심리학 창시자)
**이론 명칭**: 원형 이론 (Archetype Theory)
**핵심 내용**:
> "모든 인간은 '그림자(Shadow)'와 '상처(Wound)'를 가지고 있으며, 이를 통합하는 과정에서 진정한 자아를 실현한다."

**본 연구 적용**:
- **wounds_addressed**: Jung의 "그림자" 개념 → 이야기가 다루는 보편적 상처 유형
- **desires_fulfilled**: "자기(Self)" 실현을 향한 갈망 → 이야기가 채워주는 갈망

#### 2. Narrative Therapy (White & Epston, 1990)

**학자**: Michael White, David Epston (서사치료 창시자)
**이론 명칭**: 서사치료 (Narrative Therapy)
**핵심 내용**:
> "사람은 자신의 상처와 '공명(Resonance)'하는 이야기를 통해 치유된다."

**본 연구 적용**:
- **resonance_triggers**: 사용자의 상처/갈망과 공명할 수 있는 키워드 추출
- **User DNA ↔ Story DNA 매칭**: 서사치료의 "재저작(Re-authoring)" 원리 적용

---

### Emotion & Conflict 분포

#### Emotion (핵심 감정) 분포
| Emotion | 개수 | 비율 |
|---------|------|------|
| Sweet_Potato | 97 | 39.4% |
| Healing | 40 | 16.3% |
| Bizarre | 36 | 14.6% |
| Thriller | 35 | 14.2% |
| Cider | 34 | 13.8% |
| 기타 | 4 | 1.6% |

#### Conflict (갈등 유형) 분포
| Conflict | 개수 | 비율 |
|----------|------|------|
| Rivalry | 52 | 21.1% |
| Lack | 51 | 20.7% |
| Obstacle | 40 | 16.3% |
| Mystery | 39 | 15.9% |
| Taboo | 36 | 14.6% |
| 기타 | 28 | 11.4% |

---

## 4. 플롯 포인트 (Plot Points) 구조

### 플롯 포인트 정의

**정의**: 설화의 서사 전개를 구성하는 핵심 사건(Event) 단위. 각 사건은 특정 Beat에 속하며 서사적 기능(Function)을 수행한다.

**구성 요소**:
```json
{
  "beat": "Ki",
  "event": "부잣집에서 오래 기른 닭과 개가 사람처럼 변할 수 있게 되었다",
  "function": "배경/초자연적 설정"
}
```

**이야기 생성에서의 중요성**:
1. **재조합 단위**: Beat별로 서로 다른 설화에서 사건을 추출하여 새로운 이야기 생성
2. **서사 일관성**: 각 Beat의 서사적 기능을 통해 논리적 전개 보장
3. **유연한 구조**: 필수 Beat(Ki, Shō, Ketsu)와 선택 Beat(Ten, Trial, Crisis, Climax, Ally) 조합으로 다양한 길이와 복잡도 구현

### 플롯 포인트 구성: 기본 4 Beat + 확장 4 Beat

#### 기본 4 Beat (Ki-Shō-Ten-Ketsu)

**이론적 근거**: 기승전결 (起承轉結) - 중국 고전 시가 이론 (당나라 시대)
- 중국 고전 시가(절구, 율시)에서 발전한 4단 구성 원리
- 동아시아 전통 서사 구조의 보편적 패턴

| Beat | 한자 | 정의 | 서사적 기능 | 필수 여부 |
|------|------|------|------------|----------|
| **Ki** (기) | 起 | 시작 | 인물, 배경, 상황 제시 | ✅ 필수 (246/246) |
| **Shō** (승) | 承 | 전개 | 문제 발생, 갈등 시작 | ✅ 필수 (246/246) |
| **Ten** (전) | 轉 | 전환 | 반전, 예상 밖 사건 | ⚠️ 선택 (170/246, 69%) |
| **Ketsu** (결) | 結 | 결말 | 문제 해결, 교훈 도출 | ✅ 필수 (246/246) |

**선정 이유**:
- 129개 설화(52%)가 기본 4 Beat만으로 구성 → 최소 완결 구조로 적합
- 동아시아 문화권 보편 구조로 한국 설화에 자연스럽게 적용

#### 확장 4 Beat (세부 전개)

**이론적 근거**: Hero's Journey (Joseph Campbell, 1949) + Three-Act Structure (Syd Field, 1979)
- Campbell의 영웅 여정 12단계 중 핵심 단계 추출
- Syd Field의 3막 구조를 더 세분화

| Beat | 정의 | 서사적 기능 | 출현 빈도 |
|------|------|------------|----------|
| **Trial** (시련) | 주인공이 난관에 직면 | 갈등 심화, 긴장 고조 | 110/246 (45%) |
| **Crisis** (위기) | 최악의 상황 도래 | 절정 직전의 긴장감 | 91/246 (37%) |
| **Climax** (절정) | 갈등의 정점 | 문제 해결의 핵심 사건 | 108/246 (44%) |
| **Ally** (조력) | 조력자 등장 | 주인공 지원, 문제 해결 실마리 | 47/246 (19%) |

**선정 이유**:
- 복잡한 설화(117개, 48%)의 정밀한 전개 표현
- 이야기 생성 시 긴장감과 극적 전개를 위한 선택적 요소

### Beat 상세 설명

| Beat | 정의 | 서사적 기능 | 필수 여부 |
|------|------|------------|----------|
| **Ki** (기) | 이야기의 초기 상황, 인물, 배경 제시 | 인물 소개 (Who), 배경 설정 (Where, When), 초기 상황 제시 (What) | ✅ 필수 |
| **Shō** (승) | 문제가 발생하고 갈등이 시작되는 전개부 | 문제 제기 (Problem), 갈등 도입 (Conflict), 목표 설정 (Goal) | ✅ 필수 |
| **Trial** (시련) | 주인공이 목표 달성 과정에서 난관에 직면 | 장애물 등장 (Obstacle), 주인공의 능력 시험 (Test), 긴장감 고조 (Tension) | ⚠️ 선택 |
| **Ten** (전) | 예상 밖의 사건이 발생하거나 상황이 반전 | 반전 (Twist), 예상 밖의 사건 (Surprise), 서사의 방향 전환 (Direction Change) | ⚠️ 선택 |
| **Crisis** (위기) | 주인공이 최악의 상황에 처하는 위기 국면 | 최악의 상황 (Worst Situation), 절정 직전의 긴장감 (Pre-Climax Tension), 선택의 순간 (Decision Point) | ⚠️ 선택 |
| **Climax** (절정) | 갈등이 최고조에 달하고 문제 해결의 핵심 사건 발생 | 갈등의 정점 (Peak Conflict), 결정적 사건 (Decisive Event), 문제 해결의 계기 (Solution Trigger) | ⚠️ 선택 |
| **Ally** (조력) | 조력자가 등장하여 주인공을 돕는 국면 | 조력자 등장 (Helper Arrival), 도움 제공 (Assistance), 문제 해결 실마리 (Clue to Solution) | ⚠️ 선택 |
| **Ketsu** (결) | 문제가 해결되고 이야기가 마무리되며 교훈 도출 | 문제 해결 (Resolution), 결과 제시 (Outcome), 교훈 도출 (Moral) | ✅ 필수 |

### 플롯 포인트 조합 패턴 (예시)

**기본형** (52%): `Ki → Shō → Ten → Ketsu`
**확장형** (25%): `Ki → Shō → Trial → Ten → Climax → Ketsu`
**복합형** (22%): `Ki → Ally → Shō → Trial → Ten → Crisis → Climax → Ketsu`

→ Beat의 유연한 조합을 통해 다양한 전개 패턴 생성 가능

---

## 5. 최종 데이터 구조 (예시)

### 전체 Document 구조

```json
{
  "id": "F_001",
  "title": "개와 닭의 원한",
  "category": "민담",

  "content": {
    "clean": "개와 닭이 함께 살았다. 주인이 밭에서...",
    "raw": "옛날 어느 부잣집에 오래 기른 닭과 개가...",
    "commentary": null
  },

  "attributes": {
    "summary": "옛날 개와 닭이 함께 살았으나, 닭이 개의 공을 가로채자...",
    "emotion": "Sweet_Potato",
    "conflict": "Rivalry",
    "keywords": ["개", "닭", "원한", "속담"],

    "entities": [
      {
        "name": "개",
        "description": "뱀을 물리친 진짜 공로자",
        "type": "Animal"
      },
      {
        "name": "닭",
        "description": "공을 가로챈 동물",
        "type": "Animal"
      }
    ],

    "roles": [
      {"entity_name": "개", "type": "Victim"},
      {"entity_name": "닭", "type": "Trickster"}
    ],

    "terrains": [
      {
        "type": "Village",
        "description": "마을 - 개와 닭이 함께 사는 곳"
      },
      {
        "type": "Other",
        "description": "밭 - 뱀을 죽인 장소"
      }
    ],

    "location_context": {
      "primary_place": "제주",
      "admin_region": "제주 전역"
    },

    "plot_points": [
      {
        "beat": "Ki",
        "event": "부잣집에서 오래 기른 닭과 개가 사람처럼 변할 수 있게 되었다",
        "function": "배경/초자연적 설정"
      },
      {
        "beat": "Shō",
        "event": "닭이 개에게 주인의 횡포를 호소하며 원수를 갚자고 제안했다",
        "function": "문제 제기/음모 시작"
      },
      {
        "beat": "Trial",
        "event": "닭과 개가 뱀왕을 찾아가 복수를 청했고...",
        "function": "위험한 계획/조력자 확보"
      },
      {
        "beat": "Ten",
        "event": "장남이 닭장에서 이야기를 엿듣고 부친에게 보고했다",
        "function": "반전/음모 발각"
      },
      {
        "beat": "Crisis",
        "event": "주인이 삼해유를 뿌려 뱀을 퇴치할 준비를 했다",
        "function": "대응책 마련/반격 준비"
      },
      {
        "beat": "Climax",
        "event": "뱀들이 들어왔지만 삼해유를 맞아 죽었다",
        "function": "결정적 대결/승부 판가름"
      },
      {
        "beat": "Ketsu",
        "event": "'계불과삼년 구불과칠년'이라는 속담이 생겼다",
        "function": "교훈/속담 유래 설명"
      }
    ],

    "story_dna": {
      "wounds_addressed": ["loss", "insignificance"],
      "desires_fulfilled": ["reconnection", "meaning"],
      "primary_wound": "loss",
      "primary_desire": "reconnection",
      "resonance_triggers": ["개", "닭", "원한", "속담", "복수"],
      "emotional_arc": "반지 분실 → 수색 → 속임수 → 원한",
      "narrative_themes": ["동물", "원한", "속임수", "속담"]
    }
  }
}
```

---

## 6. 참고 문헌

### 서사 이론
- Propp, V. (1928). *Morphology of the Folktale*
- Campbell, J. (1949). *The Hero with a Thousand Faces*
- 기승전결 (起承轉結): 중국 고전 시가 이론 (당나라 시대)
- Field, S. (1979). *Screenplay: The Foundations of Screenwriting*

### 심리학 및 서사 치료
- Jung, C.G. (1934). *Archetypes and the Collective Unconscious*
- White, M. & Epston, D. (1990). *Narrative Means to Therapeutic Ends*

### 소프트웨어 공학 및 정보 검색
- Szyperski, C. (1997). *Component Software: Beyond Object-Oriented Programming*
- Salton, G. (1968). *Automatic Information Organization and Retrieval*

### 인지심리학 및 감성 컴퓨팅
- Bartlett, F. (1932). *Remembering: A Study in Experimental and Social Psychology*
- Picard, R. (1995). *Affective Computing*
