# Jeju Dialect Integration Implementation Plan

## 🎯 Project Overview
Integrate rare, defunct Jeju dialect elements from Hunminjeongeum (Yi Dynasty) into our folklore generation system.

## 📊 Current Data Assets Analysis

### ✅ What We Have
- **1500+ folklore stories** from Jeju Provincial Government
- **60+ structured JSON files** with mythology data
- **Geographic grid system** (5km × 5km mapping)
- **Web crawling infrastructure** for content collection

### 🚀 What We Need to Build

## Phase 1: Linguistic Data Preparation (12월 3주)

### 1.1 Dialect Lexicon Creation
```json
{
  "dialect_lexicon": {
    "modern_korean": "할머니",
    "jeju_historical": "하르방네",
    "hunminjeongeum_ref": "HMJ-1446-P23",
    "phonetic_ipa": "[haɾɯbaŋne]",
    "cultural_context": "elderly_female_respect",
    "usage_examples": ["하르방네가 말씀하시길...", "옛날 하르방네 시절에..."]
  }
}
```

### 1.2 Enhanced Tokenization System
Extend current schema to include dialect markers:

```json
{
  "id": "myth_seolmundae_dialect",
  "title": "설문대할망",
  "dialect_version": {
    "standard_korean": "설문대할망",
    "jeju_historical": "선문데하르방네",
    "phonetic_guide": "[sʌnmunde haɾɯbaŋne]"
  },
  "content": {
    "summary": "...",
    "episodes": [
      {
        "title": "제주도 지형 창조",
        "standard_text": "설문대할망은 치마에 흙을 담아...",
        "dialect_text": "[DIALECT:Historical] 선문데하르방네는 젓고리예 ᄒᆞᆯ크 담앙...",
        "dialect_tokens": ["[STYLE:Elder:Jeju_Phonetics]", "[DIALECT:Jeju_Historical]"]
      }
    ]
  }
}
```

## Phase 2: AWS Infrastructure Setup (1월 1주)

### 2.1 Data Pipeline Architecture
```
Raw Stories → Dialect Enhancement → Tokenization → AWS S3
     ↓              ↓                   ↓
Lambda Functions → SageMaker Processing → Model Training
     ↓              ↓                   ↓
Dialect Injection → Dataset Augmentation → Fine-tuned LLM
```

### 2.2 Required AWS Services Configuration

#### Amazon S3 Buckets:
- `jeju-folklore-corpus` - Original 1500+ stories
- `jeju-dialect-lexicon` - Historical language mappings
- `enhanced-training-data` - Dialect-augmented dataset

#### AWS Lambda Functions:
- `dialect-injection-processor` - Automated dialect enhancement
- `tokenization-pipeline` - Add dialect tokens to existing content
- `phonetic-validator` - Verify historical pronunciation accuracy

#### SageMaker Components:
- **Processing Jobs**: Dataset preparation and augmentation
- **Training Jobs**: Fine-tune Korean LLM on dialectal corpus
- **Endpoints**: Deploy model for real-time folklore generation

## Phase 3: Implementation Steps (1월 1주 - 1월 2주)

### 3.1 Immediate Actions (이번 주)

**김지현 (Historical Research)**:
1. Research Hunminjeongeum texts for Jeju dialect references
2. Create initial dialect mapping spreadsheet (100 key terms)
3. Validate cultural context for historical language use

**박소영 (Geographic Mapping)**:
1. Map dialect variations to specific Jeju regions in grid system
2. Identify location-specific terminology differences
3. Integrate dialect data with existing GPS grid structure

**이병남 (Technical Infrastructure)**:
1. Set up AWS account and service access
2. Create S3 bucket structure for data storage
3. Develop initial Lambda function for dialect injection

### 3.2 Data Processing Workflow

```python
# Example dialect enhancement pipeline
def enhance_story_with_dialect(story_json):
    """
    Process existing story JSON to add dialect variants
    """
    enhanced_story = story_json.copy()
    
    # Add dialect tokens
    for episode in enhanced_story['episodes']:
        episode['dialect_tokens'] = detect_dialect_opportunities(episode['content'])
        episode['dialect_text'] = apply_dialect_transformation(
            episode['content'], 
            dialect_lexicon
        )
    
    # Add phonetic markup for TTS
    enhanced_story['polly_ssml'] = generate_ssml_markup(
        enhanced_story['dialect_text']
    )
    
    return enhanced_story
```

### 3.3 Quality Assurance Framework

**Cultural Accuracy Validation**:
- Cross-reference with academic linguistic sources
- Community review by Jeju cultural experts
- Historical context verification

**Technical Validation**:
- Automated dialect consistency checks
- Phonetic accuracy testing with AWS Polly
- Model output quality assessment

## 🎯 Success Metrics

### Technical Milestones:
- [ ] 500+ words dialect lexicon completed
- [ ] AWS pipeline fully operational
- [ ] Model generates contextually accurate dialect stories
- [ ] TTS pronounces historical terms correctly

### Cultural Milestones:
- [ ] Community validation of dialect accuracy
- [ ] Academic review of linguistic authenticity
- [ ] Preservation of cultural nuances in generated content

## 🔄 Integration with Existing Project

This dialect integration enhances our current project phases:

**Team Kickoff & Research** → Add linguistic research component
**Technical Architecture** → Include AWS ML services
**Core Development** → Integrate dialect-enhanced content generation
**Content Creation** → Focus on authentic historical voice
**Field Testing** → Validate with Jeju community speakers

## 📅 Timeline Integration

- **12월 3주**: Dialect research and lexicon creation
- **1월 1주**: AWS infrastructure setup and initial processing
- **1월 2주**: Model training and TTS integration
- **1월 3주**: Community validation and deployment testing

## 🚨 Critical Dependencies

1. **Historical Source Access**: Hunminjeongeum texts and linguistic research
2. **Cultural Validation**: Connection with Jeju cultural institutions
3. **Technical Resources**: AWS credits and computational resources
4. **Linguistic Expertise**: Collaboration with historical language specialists

---

**Next Actions**: 
1. Schedule team meeting to assign specific dialect research tasks
2. Apply for AWS credits for machine learning workloads
3. Contact Jeju cultural institutions for linguistic consultation
4. Begin collecting Hunminjeongeum reference materials