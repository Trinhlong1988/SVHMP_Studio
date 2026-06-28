# 🚨 NOTICE — ACTIVE SESSION ROUND 19.2 (28/6/2026)

> **CMD KHÁC ĐỌC NGAY** trước khi modify project.

## Session active: Claude Opus 4.7 (1M context)

**Round**: 19.2 ✅ COMPLETE (last commit 28/6)
**State**: production-ready
**Memory updated**: `project_svhmp_round_18_19_complete.md`

---

## 🏆 CURRENT MILESTONE

**EP01-50 = 50/50 GOLDEN** — ZERO violations cross R58-R73 + 50/50 PASS post_render_gate

## 📦 RECENT COMMITS (13 commits round 18+19 hôm nay)

```
[19.2] FULL 13 items + WPM 142 + bible/24-25-26 + TTS adapter
[19.1] 50-vòng comprehensive verification
204693c Round 19 P0 ship R68-R73 + bibles + data + audit
9df9ce9 Round 18.7 DEEP_ASSESSMENT 4-agent synthesis
4001b62 Round 18.6 R67 verb semantic precision
b80c391 Round 18.5 Z1 horror punch restore
[18.4] Round 18.4 EP26-50 + R66 (100% milestone)
19a8912 Round 18.3 V EP21-25 (50% milestone)
3ee5ad4 Round 18.2 S EP16-20
38a4de3 Round 18.1 L+P EP06-15
e6a7a3b Round 18 Rules R58-R65 + EP01-05
```

---

## ⚠️ DO NOT modify these files without checking memory first

### NEW round 18-19 (chưa stable):
- `bible/01_narrative_structure.yaml` (Ngạn opening template)
- `bible/21b_ep51_90_spec.yaml` (Season 2 spec)
- `bible/22b_anti_ai_tone_kentjuno.yaml` (Anti-AI tone 5 cat)
- `bible/24_meta_arc_easter_eggs.yaml` (Magnus Easter eggs)
- `bible/25_suspense_arc_templates.yaml` (6 kentjuno arc templates)
- `bible/26_pipeline_discipline_kentjuno.yaml` (Phase+Flow + 3 Iron Laws)
- `data/place_names.yaml` (R71 whitelist)
- `output/ep_*/episode_tts_ready.md` (preprocessed for TTS render)
- `DEEP_ASSESSMENT_ROUND18.md` (4-agent synthesis)

### Modified 50 EPs (all GOLDEN):
- `output/ep_01/episode.md` đến `output/ep_50/episode.md` (~500 manual rewrites)

---

## 🛠️ NEW SCRIPTS round 18-19 (15 NEW)

### TTS adapter (CRITICAL pre-render):
```bash
python tools/tts_adapter_pre_render.py --apply
```
Generates `output/ep_*/episode_tts_ready.md` với:
- [pause:1000ms] inserted TRƯỚC reveal
- Em-dash → [pause:250ms]
- Dialogue quote marked [DIALOGUE_SEG_START/END]

### Verification (run all):
```bash
python tools/verify_50_rounds.py
```
9 audits × 50 EPs + post_render_gate × 50 = ~1000 checks

### Individual audits NEW:
- `audit_tilde_eol.py` R58
- `audit_short_eol.py` R60
- `audit_short_start.py` R61
- `audit_anaphora_consecutive.py` R62
- `audit_r68_to_r73.py` combined R68-R72
- `audit_style_stats.py` cross-EP pattern drift
- `audit_bimodal_sentence.py` Ngạn rhythm H8
- `audit_ngan_opening_template.py` bible/01
- `audit_continuity_cross_ep.py` VNQA H9
- `audit_aesthetic_5_subdim.py` kentjuno editor
- `audit_voice_cosine_similarity.py` post-render drift (needs `pip install resemblyzer`)

---

## 📋 35 RULES CỨNG hiện tại (R40-R73 + R-NEW bible/01)

Đọc đầy đủ `bible/00_constitution.yaml` trước work.

NEW round 18-19: **R58-R73** (16 rules new TTS+logic+pipeline).

---

## 🎬 EP51-90 PRODUCTION-READY PLAN

- **Vol 3 EP51-72**: Discovery — Khải Phong recover M9-M13
- **EP73 PIVOT**: M14-M15 limbo reveal (22min extended, no passenger)
- **Vol 4 EP74-90**: Atonement — M16-M17
- **EP90 FINALE**: Hạ Vy = passenger Khải Phong định collect (25min, ambiguous)

Use `bible/21b_ep51_90_spec.yaml` chapter_contract schema cho mỗi EP.

---

## ⏳ PENDING (post-render only — không gấp)

- TTS render full 50 EPs với `episode_tts_ready.md`
- `pip install resemblyzer` + voice cosine audit sau render
- EP51 generation start (sau marketing pause 4-6 tuần)

---

## 🔗 KEY REFERENCES

- `DEEP_ASSESSMENT_ROUND18.md` — 4-agent synthesis (Ngạn / TTS / horror serial / kentjuno)
- `HIENPHAP_SUMMARY.md` — constitution summary
- `BUGS_FIXED.md` — B51-B59 round 18 bugs logged
- `VERSION.md` — current_round: 19
- `C:/tmp/ainovel-cli/` — kentjuno repo cloned for reference

---

**Session 28/6 — Mr.Long approved A+B+C ship full. 13 items complete.**
