# Jeju Folklore Model Training - Token Definitions

## Character Tokens
| Token | Korean Name | English Description | Usage Context |
|-------|-------------|-------------------|---------------|
| `[CHR:Seolmundae:Goddess]` | 설문대할망 | Creation goddess, giant woman | Origin stories, landscape creation |
| `[CHR:Elder:Male]` | 할아버지 | Elderly grandfather figure | Traditional storytelling, wisdom |
| `[CHR:Elder:Female]` | 할머니 | Elderly grandmother figure | Nurturing stories, cultural transmission |
| `[CHR:Child:Curious]` | 호기심 많은 아이 | Curious child character | Educational stories, discovery |
| `[CHR:Spirit:Dragon]` | 용신 | Dragon spirit/deity | Water stories, supernatural elements |
| `[CHR:Spirit:Divine]` | 신령 | General divine being | Sacred stories, mystical events |

## Location Tokens (Mapped to Grid System)
| Token | Korean Location | Grid Reference | Geographic Context |
|-------|----------------|----------------|-------------------|
| `[LOC:Hallasan:Sacred]` | 한라산 | Center | Sacred mountain, creation site |
| `[LOC:SS-A1:Seongsan]` | 성산일출봉 | SS-A1 | Sunrise peak, dramatic coastline |
| `[LOC:Coast:Ocean]` | 해안/바다 | Various coastal grids | Ocean stories, fishing tales |
| `[LOC:Village:Traditional]` | 전통 마을 | Village grid cells | Community stories, daily life |
| `[LOC:Forest:Mysterious]` | 신비로운 숲 | Forested areas | Mystery stories, supernatural |
| `[LOC:Oreum:Volcanic]` | 오름 | Volcanic cone locations | Local legends, geographic features |

## Plot Structure Tokens
| Token | Korean Concept | Story Function | Example Usage |
|-------|----------------|----------------|---------------|
| `[PLOT:Origin]` | 창조/기원 | Creation/origin stories | How landscapes/customs began |
| `[PLOT:Transformation]` | 변신/변화 | Transformation events | Character or object changes |
| `[PLOT:Quest]` | 탐험/여행 | Journey/quest narrative | Adventure, discovery stories |
| `[PLOT:Moral]` | 교훈/도덕 | Moral lesson conclusion | Teaching stories, wisdom |
| `[PLOT:Conflict]` | 갈등/문제 | Conflict/problem setup | Dramatic tension, challenges |

## Style/Audience Tokens
| Token | Target Audience | Language Characteristics | Sentence Structure |
|-------|----------------|-------------------------|-------------------|
| `[STYLE:Child:3-5]` | Preschoolers | Simple words, repetition | Short sentences, excitement |
| `[STYLE:Child:6-10]` | Elementary age | Educational, clear | Medium sentences, questions |
| `[STYLE:Elder:Traditional]` | General audience | Formal storytelling | Traditional narrative rhythm |
| `[STYLE:Academic:Formal]` | Scholars/adults | Complex vocabulary | Detailed, analytical |
| `[STYLE:Modern:Casual]` | Contemporary audience | Conversational tone | Natural, accessible |

## Cultural/Dialect Tokens
| Token | Language Variety | Historical Context | Usage Notes |
|-------|-----------------|-------------------|-------------|
| `[DIALECT:Standard]` | 표준 한국어 | Modern standard Korean | Default, accessible |
| `[DIALECT:Jeju:Historical]` | 역사적 제주 방언 | Yi Dynasty era | Hunminjeongeum references |
| `[DIALECT:Jeju:Modern]` | 현대 제주 방언 | Contemporary Jeju | Local authenticity |
| `[VOICE:Granny:Rhythmic]` | 할머니 구술체 | Traditional oral style | Storytelling rhythm |
| `[VOICE:Formal:Ceremonial]` | 의식용 격식체 | Ritual/ceremonial tone | Sacred contexts |

## Example Training Prompts

### Simple Child Version
```
INPUT: [STYLE:Child:3-5] [CHR:Seolmundae:Goddess] [PLOT:Origin] [LOC:Hallasan:Sacred] [GENERATE_STORY]

EXPECTED OUTPUT: 
"옛날에 아주 큰 할머니가 살았어요! 이 할머니는 우리 제주도를 만든 특별한 분이에요. 할머니가 치마에 흙을 담아서 높은 산을 만들었답니다. 그 산이 바로 한라산이에요! 정말 멋진 할머니죠?"
```

### Traditional Elder Version
```
INPUT: [STYLE:Elder:Traditional] [CHR:Seolmundae:Goddess] [PLOT:Origin] [LOC:Hallasan:Sacred] [GENERATE_STORY]

EXPECTED OUTPUT:
"옛적 이 섬에 설문대할망이라 하는 여신이 계셨습니다. 그 몸집이 어찌나 크던지, 아무리 깊은 바다라도 무릎 높이밖에 차지 않았습니다. 할망은 치마 자락에 흙을 담아 이곳저곳에 쏟으며 한라산과 크고 작은 오름들을 빚어내셨습니다."
```

### Academic Formal Version
```
INPUT: [STYLE:Academic:Formal] [CHR:Seolmundae:Goddess] [PLOT:Origin] [LOC:Hallasan:Sacred] [GENERATE_STORY]

EXPECTED OUTPUT:
"제주도의 창조신화에서 설문대할망은 거인 여신으로 묘사되며, 한라산과 360여 개의 오름을 창조한 존재로 전승됩니다. 이 신화는 제주도의 화산 지형 형성에 대한 민간의 설명 체계이자, 모계 중심의 제주 전통 사회를 반영하는 문화적 상징으로 해석됩니다."
```

## Token Combination Rules

### Valid Combinations
- `[STYLE:*] + [CHR:*] + [PLOT:*] + [LOC:*]` - Complete story generation
- `[CHR:*] + [PLOT:*]` - Character-focused narrative
- `[LOC:*] + [PLOT:Origin]` - Location origin story
- `[STYLE:*] + [DIALECT:*]` - Language style specification

### Invalid Combinations
- Multiple `[STYLE:*]` tokens (conflicting styles)
- Anachronistic combinations (e.g., `[CHR:Modern] + [DIALECT:Historical]`)
- Geographically impossible combinations (e.g., coastal stories with mountain-only locations)

## Training Data Structure

Each training sample should follow this format:
```json
{
  "id": "unique_identifier",
  "prompt": "tokenized input prompt",
  "response": "expected story output",
  "metadata": {
    "source_story": "original folklore reference",
    "target_style": "style category",
    "complexity_score": 1-3,
    "cultural_elements": ["list of cultural markers"],
    "training_weight": 0.5-1.0
  }
}
```

## Quality Metrics

### Cultural Authenticity
- Historical accuracy of cultural references
- Appropriate use of traditional narrative elements
- Respect for sacred/ceremonial contexts

### Linguistic Consistency  
- Age-appropriate vocabulary for target style
- Grammatical correctness across variations
- Dialect authenticity for historical versions

### Narrative Coherence
- Logical story structure maintenance
- Character consistency across variations
- Plot coherence despite style changes

---

*This token system enables controlled generation while preserving the cultural authenticity and educational value of Jeju folklore traditions.*