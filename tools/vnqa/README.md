# VNQA — Vietnamese Narrative QA Framework

**Lock date:** 2026-06-26 (Mr.Long approve full Phase H expand → reusable framework)
**Status:** v1.0 SKELETON — production for SVHMP horror, extensible cho news/podcast/novel

## Mục tiêu

**1 framework chuẩn hóa data — dùng được cho TẤT CẢ project narrative Vietnamese:**
- SVHMP horror narration (current)
- Tin tức / thời sự broadcast
- Podcast casual
- Novel văn học
- Future: bất kỳ project Vietnamese audio narrative

Replace manual `bible/22_anti_slop_vi.yaml` style → **library + corpus-based QA**.

## Architecture 4-layer

```
┌──────────────────────────────────────────┐
│  Layer 4: Pipeline Orchestrator          │
│  pipeline.py — load genre + run checks   │
└──────────────────────────────────────────┘
                    ↓ uses
┌──────────────────────────────────────────┐
│  Layer 3: Genre Profiles (per use case)  │
│  horror_narrative / news_broadcast /     │
│  podcast_casual / novel_literary         │
└──────────────────────────────────────────┘
                    ↓ overrides
┌──────────────────────────────────────────┐
│  Layer 2: Standardized Resources         │
│  ai_tell_words / idioms / filler /       │
│  formality_markers / ngram_baseline      │
└──────────────────────────────────────────┘
                    ↓ feeds
┌──────────────────────────────────────────┐
│  Layer 1: Core NLP Wrappers (H1-H7)      │
│  Underthesea (tokenize+POS) / PhoBERT    │
│  (collocation) / PhoNLP (dep parse) /    │
│  PhoMT (n-gram) / Wiktionary (dict)      │
└──────────────────────────────────────────┘
```

## Data standardization schema

### `resources/ai_tell_words.yaml` (cross-genre baseline)
```yaml
schema_version: 1
description: Vietnamese AI-tell words — overuse patterns
tier_1_max_per_ep: 3      # genre có thể override
tiers:
  tier_1_kill_on_sight:
    - word: "đột nhiên"
      reason: "transition mặc định AI"
      alternatives: [bỗng, chợt, vụt nhiên]
      genre_overrides:
        news_broadcast: { max_per_ep: 1 }  # news còn strict hơn
        podcast_casual: { max_per_ep: 5 }  # casual OK lỏng hơn
```

### `genres/horror_narrative.yaml` (SVHMP)
```yaml
inherits: _base
genre_id: horror_narrative
purpose: "Vietnamese ghost story TTS narration (SVHMP-like)"

thresholds:
  adverb_ratio_max: 0.15       # 15% — horror cần nhiều mood adverb
  idiom_max_per_ep: 2          # idiom 1x OK, 2+ = cliché
  sentence_len_max: 40

required_tone:
  - melancholy
  - subtle_haunting
forbidden_tone:
  - jump_scare_explicit
  - comedic_relief

cross_ref:
  - bible/00_constitution.yaml (ALWAYS_5 / NEVER_7)
  - bible/22_anti_slop_vi.yaml (existing manual list)
```

### `genres/news_broadcast.yaml`
```yaml
inherits: _base
genre_id: news_broadcast
purpose: "Vietnamese news/current affairs broadcast script"

thresholds:
  adverb_ratio_max: 0.08       # news strict — minimal adverb
  passive_voice_max: 0.20      # passive OK trong news
  formality_min: 0.7           # FORMAL required
  sentence_len_max: 35

required_tone:
  - formal
  - objective
forbidden_tone:
  - subjective_emotion
  - colloquial_slang
```

### `genres/podcast_casual.yaml`
```yaml
inherits: _base
genre_id: podcast_casual
purpose: "Vietnamese casual podcast (chat-style narration)"

thresholds:
  adverb_ratio_max: 0.20        # casual OK lỏng
  filler_max_per_ep: 10         # "ờm", "ý là", "thì" tự nhiên trong nói
  formality_min: 0.2            # informal OK

required_tone:
  - conversational
  - approachable
forbidden_tone:
  - academic_dense
```

## Usage cho project khác (SVHMP / news / podcast / future)

```python
from tools.vnqa.pipeline import VietnameseQAPipeline

# SVHMP horror
qa = VietnameseQAPipeline(genre='horror_narrative')
report = qa.check_episode(text=ep_text, ep_number=2)

# News broadcast
qa = VietnameseQAPipeline(genre='news_broadcast')
report = qa.check_segment(text=news_text)

# Podcast
qa = VietnameseQAPipeline(genre='podcast_casual')
report = qa.check_episode(text=podcast_text)
```

## Reuse pattern (project khác)

**Option 1: Copy folder** (simple)
- Copy `tools/vnqa/` → new project's `tools/`
- Customize genre yaml

**Option 2: Git submodule** (future when stable)
- Extract `tools/vnqa/` thành standalone repo
- `git submodule add` vào new project

**Option 3: pip package** (production-grade)
- Publish to PyPI: `pip install vnqa`
- Future Phase I if framework mature

## Phase H roadmap (within VNQA)

| Step | Status | Effort |
|---|---|---|
| H1 Underthesea POS rhythm | ✓ shipped (pipeline.py wrapper) | 2-3d |
| H2 Dictionary existence | 🟡 skeleton (Wiktionary defer download) | 2-3d |
| H3 PhoBERT collocation | 🟡 skeleton (model download defer) | 4-5d |
| H4 Idiom detection seed | ✓ shipped (10 idiom seed) | 1d |
| H5 Formality heuristic | ✓ shipped (journalistic markers) | 1d |
| H6 PhoNLP dependency | 🟡 skeleton (PhoNLP install defer) | 2-3d |
| H7 N-gram anomaly | ✓ shipped (per-sentence bi-gram) | 1d |
| H8 Orchestrator + qa.md integration | ✓ shipped (pipeline.py main) | 1d |

**Total now:** 5/8 production-ready, 3/8 skeleton (model defer install on-demand).
**Total full:** 4-6 weeks dev khi cần fine-tune PhoBERT cho specific genre.

## License safe stack

All MIT/Apache/CC0/BSD-3 — production safe for commercial Vietnamese audio channel.

## Memory ref

- `reference_vietnamese_nlp_libraries.md` — research detail 20+ repos
- `feedback_cam_suy_luan.md` — rule cứng marking TENTATIVE chỗ skeleton
- `feedback_fix_registry_rule.md` — BUGS_FIXED protocol

## Apply protocol

1. Mỗi project mới: copy folder `tools/vnqa/` → customize `genres/<project_genre>.yaml`
2. Run `python tools/vnqa/pipeline.py --episode <ep.md> --genre <genre_id> --output report.json`
3. Add report verdict vào project's QA pipeline (gate ship)
4. Tune thresholds in genre yaml based on real data feedback
