# Data Transformation Pipeline for Model Training

## 🎯 Objective: Convert Raw Jeju Folklore Data → Structured Training Corpus

### Current Data State Analysis
- ✅ **Raw Stories**: 1500+ folklore stories downloaded from Jeju Provincial Government
- ✅ **Structured JSON**: 60+ mythology files with episodes and cultural context
- ✅ **Geographic Mapping**: Grid system with location-story relationships
- 🔄 **Need**: Tokenized, controllable story elements for model training

---

## Phase 1: Story Element Tokenization (This Week)

### 1.1 Token System Design

Based on your existing story structure, implement these token categories:

#### **Character Tokens**
```json
{
  "character_tokens": {
    "[CHR:Seolmundae:Goddess]": "설문대할망 - Creation goddess",
    "[CHR:Elder:Male]": "할아버지 - Elderly male narrator",
    "[CHR:Elder:Female]": "할머니 - Elderly female narrator", 
    "[CHR:Spirit:Dragon]": "용신 - Dragon spirit",
    "[CHR:Child:Curious]": "호기심 많은 아이"
  }
}
```

#### **Plot Structure Tokens**
```json
{
  "plot_tokens": {
    "[PLOT:Origin]": "창조/기원 이야기",
    "[PLOT:Transformation]": "변신/변화 사건",
    "[PLOT:Quest]": "탐험/여행 서사",
    "[PLOT:Moral]": "교훈/도덕적 결말",
    "[PLOT:Conflict]": "갈등/문제 상황"
  }
}
```

#### **Location Tokens (Using Your Grid System)**
```json
{
  "location_tokens": {
    "[LOC:SS-A1:Seongsan]": "성산일출봉 지역",
    "[LOC:Hallasan:Sacred]": "한라산 신성한 공간",
    "[LOC:Coast:Dramatic]": "해안 절벽",
    "[LOC:Village:Traditional]": "전통 마을",
    "[LOC:Forest:Mysterious]": "신비로운 숲"
  }
}
```

#### **Style/Audience Tokens**
```json
{
  "style_tokens": {
    "[STYLE:Child:3-5]": "유아용 단순한 문체",
    "[STYLE:Child:6-10]": "초등생용 교육적 문체", 
    "[STYLE:Elder:Traditional]": "전통적인 구술 문체",
    "[STYLE:Modern:Casual]": "현대적이고 친근한 문체",
    "[STYLE:Academic:Formal]": "학술적이고 정중한 문체"
  }
}
```

#### **Cultural/Dialect Tokens**
```json
{
  "cultural_tokens": {
    "[DIALECT:Standard]": "표준 한국어",
    "[DIALECT:Jeju:Historical]": "역사적 제주 방언",
    "[DIALECT:Jeju:Modern]": "현대 제주 방언",
    "[VOICE:Granny:Rhythmic]": "할머니의 리듬감 있는 구술",
    "[VOICE:Formal:Ceremonial]": "의식용 격식 있는 목소리"
  }
}
```

### 1.2 Manual Tagging Process (Priority Stories)

Start with your key mythology files and manually tag them:

#### **Example: 설문대할망 Story Transformation**

**Original Content:**
```
"설문대할망은 치마에 흙을 담아 여러 번 쏟아 한라산을 형성했다."
```

**Tokenized Version:**
```
"[CHR:Seolmundae:Goddess] [ACTION:Creation] [LOC:Hallasan:Sacred] [PLOT:Origin] [STYLE:Traditional:Formal]"
```

**Generated Training Data:**
```json
{
  "prompt": "[CHR:Seolmundae:Goddess] [PLOT:Origin] [LOC:Hallasan:Sacred] [STYLE:Child:3-5]",
  "response": "옛날에 아주 큰 할머니가 계셨어요. 이 할머니는 치마에 흙을 담아서 높은 산을 만들었답니다.",
  "metadata": {
    "source_story": "seolmundae-halmang",
    "complexity_level": 1,
    "target_audience": "preschool"
  }
}
```

---

## Phase 2: Data Augmentation Pipeline (Next Week)

### 2.1 Systematic Story Variations

For each of your 60+ core stories, create variations:

#### **Style Variations**
```python
# Pseudo-code for data augmentation
def generate_style_variations(original_story):
    variations = []
    
    styles = [
        "[STYLE:Child:3-5]",
        "[STYLE:Child:6-10]", 
        "[STYLE:Elder:Traditional]",
        "[STYLE:Academic:Formal]"
    ]
    
    for style in styles:
        variation = {
            "prompt": f"{style} {original_story['tokens']}",
            "response": rewrite_for_style(original_story['content'], style),
            "metadata": {
                "original_id": original_story['id'],
                "variation_type": "style",
                "target_style": style
            }
        }
        variations.append(variation)
    
    return variations
```

#### **Character Substitution**
```python
def generate_character_variations(original_story):
    # Replace [CHR:Seolmundae:Goddess] with [CHR:Elder:Wise]
    # Adjust story content accordingly
    # Maintain plot structure but change character roles
```

#### **Location Adaptation**
```python
def generate_location_variations(original_story):
    # Map [LOC:Hallasan:Sacred] to [LOC:SS-A1:Seongsan]
    # Adapt story elements to match new geographic context
    # Use your existing grid system for location accuracy
```

### 2.2 Training Data Format

Structure your final training data for model consumption:

```json
{
  "training_samples": [
    {
      "id": "seolmundae_child_variant_001",
      "input": "[STYLE:Child:3-5] [CHR:Goddess:Kind] [PLOT:Origin] [LOC:Mountain:Big] Generate story",
      "output": "옛날에 아주 착한 여신님이 살았어요. 여신님은 큰 산을 만들고 싶었어요. 그래서 치마에 흙을 많이 담았답니다. 그리고 그 흙으로 우리가 사는 제주도에 아름다운 한라산을 만들어 주었어요. 정말 멋진 여신님이죠?",
      "metadata": {
        "source_mythology": "seolmundae-halmang",
        "target_age": "3-5",
        "complexity_score": 1,
        "cultural_elements": ["creation_myth", "jeju_geography"],
        "training_weight": 1.0
      }
    }
  ]
}
```

---

## Phase 3: Technical Implementation (Next 2 Weeks)

### 3.1 Preprocessing Scripts

Create automated tools for your data transformation:

#### **Token Extraction Script**
```python
# Extract existing story elements and suggest tokens
def analyze_story_structure(story_json):
    """
    Analyze existing JSON files and suggest appropriate tokens
    """
    suggestions = {
        "characters": extract_character_mentions(story_json),
        "locations": extract_location_references(story_json),
        "plot_points": identify_narrative_beats(story_json),
        "cultural_elements": detect_cultural_markers(story_json)
    }
    return suggestions
```

#### **Augmentation Pipeline**
```python
# Automated story variation generation
def create_training_corpus(base_stories_dir, output_dir):
    """
    Process all 60+ mythology files and create training variations
    """
    for story_file in base_stories_dir:
        story = load_json(story_file)
        
        # Extract tokens
        tokens = extract_tokens(story)
        
        # Generate variations
        variations = []
        variations.extend(generate_style_variations(story))
        variations.extend(generate_character_variations(story))
        variations.extend(generate_location_variations(story))
        
        # Save training data
        save_training_data(variations, output_dir)
```

### 3.2 Quality Control Framework

#### **Cultural Accuracy Validation**
- Cross-reference generated content with original cultural context
- Implement automated checks for cultural consistency
- Flag content that may misrepresent traditional elements

#### **Linguistic Consistency**
- Ensure dialect tokens produce appropriate language variations
- Validate age-appropriate vocabulary for different style tokens
- Check grammatical accuracy across style transformations

---

## Phase 4: Model Training Setup (Week 3-4)

### 4.1 Training Data Organization

```
training_data/
├── base_stories/           # Your original 60+ JSON files
├── tokenized_stories/      # Manual token assignments
├── augmented_corpus/       # Generated variations
├── validation_set/         # Hold-out data for testing
└── metadata/
    ├── token_definitions.json
    ├── cultural_guidelines.json
    └── quality_metrics.json
```

### 4.2 Model Training Configuration

```json
{
  "training_config": {
    "base_model": "korean-llm-base",
    "training_data_path": "./augmented_corpus/",
    "validation_split": 0.2,
    "batch_size": 16,
    "learning_rate": 2e-5,
    "num_epochs": 3,
    "special_tokens": {
      "prompt_start": "[GENERATE]",
      "style_tokens": ["[STYLE:", "]"],
      "character_tokens": ["[CHR:", "]"],
      "location_tokens": ["[LOC:", "]"]
    }
  }
}
```

---

## Immediate Next Steps (This Week)

### Day 1-2: Token System Setup
1. **Define token categories** using your existing story structure
2. **Create token definition files** (JSON format)
3. **Manually tag 5-10 key stories** as training examples

### Day 3-4: Data Processing
1. **Write tokenization scripts** for automated processing
2. **Process first batch** of 20 mythology files
3. **Generate initial variations** for testing

### Day 5-7: Quality Validation
1. **Review generated variations** for cultural accuracy
2. **Refine token definitions** based on testing
3. **Prepare training dataset** structure

### Week 2: Automated Pipeline
1. **Scale tokenization** to all 60+ stories
2. **Generate comprehensive variations** (300-500 training samples)
3. **Set up validation framework** for quality control

This structured approach transforms your rich folklore collection into a controllable, culturally-accurate story generation system that preserves the authenticity of Jeju cultural heritage while enabling dynamic content creation.