---
project: SVHMP_Studio
current_round: 13
last_update_ts: 2026-06-26
last_update_by: Claude session 26/6 (EP01 PRODUCTION FIRST SHIP + 32 hiến pháp + Pipeline LOCKED)
schema_version: 1
---

# VERSION — SVHMP_Studio

**Rule cứng (memory):** `feedback_fix_registry_rule.md` — Session start protocol bắt buộc đọc file này trước work.

---

## Session start protocol (mọi AI/CMD bắt buộc theo)

```
1. Read CLAUDE.md workspace (C:\Users\Administrator\CLAUDE.md)
2. Read VERSION.md project (THIS FILE) — compare với last_known_version
3. If mismatch → re-read changed artifacts (see "Current versions" table)
4. Read BUGS_FIXED.md project (D:\...\SVHMP_Studio\BUGS_FIXED.md)
5. Read memory feedback_* relevant (cam_suy_luan, fix_registry, validated_params, ...)
6. **EP02+ render:** Read `feedback_svhmp_script_8_hard_rules.md` (32 rules) + `project_svhmp_master_production_v1.md`
7. THEN start work
```

---

## Current versions per artifact

| Artifact | Version | Lock date | Notes |
|---|---|---|---|
| **prompts/generator.md** | RC3.4 round 11 | 2026-06-19 | FROZEN |
| **prompts/qa.md** | v1.2 | 2026-06-26 | round 12 add PHASE 12.14 Arc Consistency |
| **prompts/director.md** | round 11 | 2026-06-19 | step_1.5 ref tools/related_eps.py (optional aid, not enforced) |
| **prompts/tts.md** | **v1.2** | 2026-06-26 | **round 13** — Pipeline LOCKED s3 baseline + 32 hiến pháp script lints |
| **prompts/tts_adapter.md** | round 11 | 2026-06-19 | |
| **prompts/video.md** | v1.0 | 2026-06-19 | round 10 + 11 ship |
| **prompts/video_intro.md** | v1.0 | 2026-06-26 | round 12 — HDK channel intro V7-V9 |
| **prompts/publisher.md** | v1.0 | 2026-06-19 | |
| **bible/00_constitution.yaml** | v1.0 | 2026-06-23 | cross_bible_refs updated 26/6 (add bible/20) |
| **bible/01-18** | v1.0 | 2026-06-23 | round 11 ship + round 12 04 extension |
| **bible/04_asset_bible.yaml** | v1.1 | 2026-06-26 | round 12 add channel_brand_assets (HDK) |
| **bible/19_motion_bible.yaml** | v1.0 | 2026-06-26 | round 12 — HDK channel motion rules |
| **bible/20_arc_rolling_expansion.yaml** | v1.0 | 2026-06-26 | round 12 — codify state.arcs[] schema |
| **runtime/state.yaml** | round 8 schema | dynamic | B5 fix payoff_owner added |
| **runtime/lifecycle.yaml** | round 11 | dynamic | per_ep_status authoritative |
| **runtime/analytics.yaml** | round 3 schema | dynamic | feedback_loop_enabled |
| **runtime/canon_registry.yaml** | round 8 | dynamic | immutable post-first-seen |
| **tools/related_eps.py** | v1.0 | 2026-06-26 | round 12 — Pattern 7 (ainovel-cli adapted) |
| **tools/svhmp_v13_render.py** | **v1.3** | 2026-06-26 | **round 13** NEW — Pipeline LOCKED EP02-90: fade 80ms, trim -20dB, silence bridge, SR 22050, NO compressor, loudnorm TP=-1.5 |
| **tools/svhmp_preflight_qa.py** | **v3** | 2026-06-26 | **round 13** NEW — 11 rules + dialog whitelist + R10 word-boundary + R17 phrase repeat |
| **tools/svhmp_dupe_audit.py** | **v1** | 2026-06-26 | **round 13** NEW — pattern bug + 3+ from + cross-chunk repeat |
| **tools/svhmp_audit_chi_tiet.py** | **v1** | 2026-06-26 | **round 13** NEW — cross-section phrase repeat |
| **tools/svhmp_100check_master.py** | **v1** | 2026-06-26 | **round 13** NEW — 100-check framework, ≥95 PASS gate |
| **tools/svhmp_final_verify.py** | **v1** | 2026-06-26 | **round 13** NEW — 26 bug pattern Mr.Long catched verify |
| **assets/hdk_channel/** | round 12 ship | 2026-06-26 | HDK refactor hợp nhất (17 file) |
| **EP01_FINAL.wav** | **v1.0 PILOT** | 2026-06-26 | **round 13** SHIP — 15:29 min, 6 sections, SR 22050Hz, Workspace `Desktop\SVHMP_v10_workdir\` |

---

## Memory rules NEW round 13

| File | Mục đích |
|---|---|
| `feedback_svhmp_script_8_hard_rules.md` | **32 hiến pháp HARDLOCK** (R1-R32) EP02-EP90 |
| `project_svhmp_master_production_v1.md` | Master production doc — 100-check 101 PASS / 10 WARN / 0 FAIL |
| `project_svhmp_8phase_roadmap.md` | Roadmap chiến lược 8-phase Mr.Long docx 25/6 |
| `feedback_svhmp_v13_session_lessons.md` | 13 practical lessons từ session iterate v13d→v13m |
| `feedback_svhmp_tts_production_principles.md` | TTS production 5-trụ docx Mr.Long 25/6 |

---

## Recent changes (newest first)

### 2026-06-26 round 13 (Claude session) — EP01 PRODUCTION FIRST SHIP
- **EP01_FINAL.wav** ship Desktop — 15:29 min, 6 sections (Hook 1:05, Setup 3:26, Incident 2:58, Reveal 3:49, Payoff 2:57, Cliffhanger 1:14)
- **32 hiến pháp HARDLOCK** R1-R32 (memory `feedback_svhmp_script_8_hard_rules.md`)
- **Pipeline LOCKED** `tools/svhmp_v13_render.py` — fade 80ms / trim -20dB / silence bridge / SR 22050 / NO compressor / loudnorm TP=-1.5
- **7 scripts vận hành** ship `C:\tmp\svhmp_*.py` — preflight + dupe_audit + audit_chi_tiet + 100check + final_verify
- **100-check master framework**: 101 PASS / 10 WARN / 0 FAIL gate ≥95 PASS trước render
- **Bugs caught + fixed:** B8-B22 (15 production bugs trong session)
  - B8 protobuf C-ext conflict → `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python`
  - B9 cwd index-tts required → `cd C:/Users/Administrator/index-tts`
  - B10 192kHz upsample click → SR fix `-ar 22050`
  - B11 compressor → khàn giọng → Rule 18 NO transform
  - B12 fade 80ms vẫn còn impulse natural Vietnamese consonant
  - B13 Whisper transcribe digit "bảy"→"7" / "tám"→"8" — QA pattern dual form
  - B14 BigVGAN tail "phù" /aːj/ open vowel → Rule 22 closed consonant ending
  - B15 dialog character ≠ narrator → Rule 19 dialog→narration
  - B16 section ending logic disrupt s+1 → Rule 21 cross-section logic
  - B17 lặp phrase cross-chunk "giọng bà nghẹn lại" → Rule 17 ABSOLUTE NO REPEAT
  - B18 2+ câu 4-7 từ liên tiếp narrative → "máy đọc" → Rule 1 updated
  - B19 "X không Y, X chỉ Z" pronoun lặp → Rule 1 pattern cấm
  - B20 lyrics/poetry isolated 2 từ → Rule 32 context dẫn dắt + quote + đủ vần
  - B21 plosive cluster Vietnamese natural perception → reword text avoid
  - B22 pipeline pause_after_ms IGNORE bug 200ms cố định → variable bridge

### 2026-06-26 round 12 (earlier Claude session)
- Phase D2: tools/related_eps.py NEW
- Phase D1: bible/20 NEW + qa.md v1.2
- HDK refactor: assets/hdk_channel/ hợp nhất

### 2026-06-23 round 3
- Bibles 00-18 ship
- EP01 v7_final_round3_lock golden reference

### 2026-06-19 round 11
- 7 prompts FROZEN
- 19 bibles ship (00-18)

---

## Compatibility matrix

| Combo | Status |
|---|---|
| Generator RC3.4 ↔ QA Lock v1.2 | ✅ |
| TTS v1.2 (Pipeline LOCKED) ↔ 32 hiến pháp | ✅ |
| 100-check framework ↔ all 6 specs EP01 | ✅ 101/111 PASS |
| svhmp_v13_render.py ↔ IndexTTS2-vi checkpoints-vi | ✅ |

---

## Breaking changes round 13
**NONE.** Round 13 additive only:
- EP01_FINAL.wav PILOT ship (no prior EP01 production)
- New scripts (svhmp_v13_render.py, preflight, dupe_audit, etc.) — KHÔNG modify existing artifacts
- tts.md v1.1 → v1.2 (add Pipeline LOCKED section + 32 rules reference, không break v1.1)
- Memory entries new (32 rules, master production doc) — KHÔNG modify existing memory

---

## Pending changes (chưa ship)
- **Phase 2 Content Constitution**: 100 Passenger + 100 Secret + Emotional Archetypes + Season Bible 1-30
- **director.md** bump version document Pipeline LOCKED reference
- **Pattern 1** Checkpoint Resume ainovel — SKIP (SVHMP RICHER)

---

## How to check version mismatch

```bash
# CMD/AI session start:
cat "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\VERSION.md" | grep -E "^current_round|^last_update_ts"

# Output expected: current_round: 13, last_update_ts: 2026-06-26
# Nếu khác với last known → re-read changed artifacts per "Current versions" table
```

---

## Audit verification round 13

- `python C:\tmp\svhmp_100check_master.py` → 101/111 PASS (10 WARN false positive accept, 0 FAIL)
- `python C:\tmp\svhmp_preflight_qa.py <spec>` → must PASS or WARN narrative R10
- `python C:\tmp\svhmp_audit_chi_tiet.py` → cross-section phrase repeat report

Round 12 audits still valid:
- `python C:\tmp\svhmp_arc_audit.py` → 10/10 PASS
- `python C:\tmp\svhmp_related_eps_audit.py` → 10/10 PASS
- `python C:\tmp\hdk_audit_20rounds.py` → 22/22 PASS

Total: 143/153 PASS at last verify (2026-06-26 round 13).
