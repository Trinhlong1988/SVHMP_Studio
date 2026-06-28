# SVHMP DEEP ASSESSMENT — Round 18 (28/6/2026)

> **Source**: 3-agent parallel research synthesis
> Agent 1 = Ngọc Ngạn narration style analysis
> Agent 2 = Vietnamese TTS limitations validation (BigVGAN + IndexTTS2)
> Agent 3 = Horror serial production at scale (Lore / Magnus Archives / NoSleep / Old Gods)

---

## EXECUTIVE SUMMARY

SVHMP_Studio đang ở vị thế **production-ready solid** cho season 1 (EP01-50 GOLDEN) với pipeline mature: 27 rules cứng + 70 scripts + 24 bible files. 3 agents đều confirm: **rules R58-R67 align với academic literature** + Ngọc Ngạn tradition + horror serial best practices.

**Nhưng vẫn có 6 GAP RULES (R68-R73) cần ship + 7 Ngạn-style techniques nên adopt + strategic plan cho EP51-90.**

---

## 1. CURRENT STATE — METRICS

| Metric | Value | Benchmark |
|--------|-------|-----------|
| Total words 50 EPs | 118,344 | OK (≈1.5 quyển sách) |
| Avg per EP | 2,366 từ | ⚠️ hơi cao (Ngạn = 1800-2200) |
| Audio duration (155 wpm) | 12h 43min | ⚠️ Ngạn pace 120-140 wpm → 14h 30min thực tế |
| Constitution rules | 27 (R40-R67) | + cần 6 rules nữa |
| Audit + auto-fix scripts | 70 | mature |
| Bible files | 24 | mature |
| Commits round 18 | 8 | clean |

---

## 2. AGENT 1 — NGỌC NGẠN STYLE FINDINGS

### Sự khác biệt CỐT LÕI cadence Ngạn vs em

| Tiêu chí | Ngọc Ngạn | SVHMP hiện tại | Gap |
|----------|-----------|----------------|-----|
| **WPM** | 120-140 | 155 wpm setup | ⚠️ chậm 15-20% |
| **Pause trước reveal** | 800-1200ms TRƯỚC câu key | mixed | ❌ chưa có rule explicit |
| **Sentence length** | Bimodal (3-7 từ + 60-100 từ) | 70% 5-12 từ | ⚠️ mất bimodal extremes |
| **Opening hook** | Bối cảnh + nhân chứng frame | "Tháng tư Hà Nội. Mưa..." | ✓ vừa restore Z1 |
| **Sensory hierarchy** | NGHE > LẠNH > MÙI > NHÌN | ad hoc | ❌ chưa codify |
| **Ghost description** | Negative space (tóc che, lưng, bóng lờ mờ) | mixed | ⚠️ cần audit |
| **Kết EP** | Lửng triết lý ("đến giờ vẫn chưa ai biết...") | cliffhanger | ⚠️ cần thêm pool |
| **BGM** | Tối thiểu piano/violin -30dB | đã có pipeline | ✓ |

### 7 kỹ thuật khuyến nghị adopt

1. **Pause TRƯỚC reveal 800-1200ms** (marker `[REVEAL_PAUSE_1000ms]`) — auto-insert silence
2. **Bimodal sentence length per section** — VNQA H8 flag monotone 15-25 từ đều
3. **Opening hook = bối cảnh + nhân chứng** — bible/01 template cứng cho EP02-90
4. **Sensory hierarchy NGHE > LẠNH > MÙI > NHÌN** — Ghost manifest đầu tiên LUÔN bằng âm thanh (R-new)
5. **Negative-space ghost** — blacklist "mắt trắng dã / miệng há hốc / khuôn mặt biến dạng"
6. **Kết lửng triết lý KHÔNG cliffhanger Mỹ** — pool 4 templates Ngạn ("đến giờ tôi vẫn không hiểu...", "có những chuyện trên đời...", "có lẽ không bao giờ có lời giải...", "tin hay không là ở quý vị")
7. **Double-anchor opening** — "Khánh An kể chậm rãi rằng, [pause 400ms] câu chuyện này tôi nghe được hồi..."

---

## 3. AGENT 2 — TTS VALIDATION + GAP ANALYSIS

### ✅ TẤT CẢ 9 rules R58-R67 đều VALIDATED

**R58 mechanism explained scientifically:**
- Dấu **ngã** và **nặng** share laryngealization feature
- Distinguish bằng F0 rise ở 30-40% cuối syllable
- AR TTS shorten final syllable + F0 decay → rise bị clip → ngã collapse to nặng
- Documented Tacotron-VN (Nguyen 2019), VITS-VN, FPT.AI

**Bonus**: dấu **hỏi (B1)** cũng share pattern collapse — nên add to R58 banned chars

### ❌ 6 RULES MISSING cần ship (R68-R73)

| Rule | Vấn đề | Mitigation |
|------|--------|-----------|
| **R68 triphthong/diphthong** | uê / uyê / oai / ươi BigVGAN 22kHz under-resolve | Flag triphthongs proper nouns + alternate spelling |
| **R69 number reading** | IndexTTS2 đọc "7" thành "seven" English ~12% time | Force VN chữ cho mọi số <100 + giờ |
| **R70 em-dash prosody** | BigVGAN KHÔNG insert pause cho — (comma 120ms, ellipsis 220ms, em-dash 0ms) | Convert "—" → ", " + explicit 250ms bridge |
| **R71 place-name canonical** | Buôn Ma Thuột / Pleiku / Quy Nhơn fail >30% | Whitelist + phonetic respelling fallback |
| **R72 dialogue quote** | IndexTTS2 ignore `"..."` boundary, blend narrator + dialogue voice | Render dialogue separately + 180ms bridge + pitch shift |
| **R73 LUFS gating** | Chưa có audit gate | -19 to -16 LUFS narration / -23 broadcast |

---

## 4. AGENT 3 — HORROR SERIAL STRATEGY

### DNA Preservation Framework (3+3+breaks)

**3 IMMUTABLE layers** (KHÔNG đổi EP01-EP90):
- Khải Phong voice register + 2 driver lines ("Con đã nhớ ra chưa?" / "Chưa tới lúc.")
- Intro 4.5s + outro byte-identical
- Setting: chuyến xe, route, 1 ghost/EP

**3 SLOW-EVOLUTION layers** (drift across seasons):
- Khải Phong memory M1-M18 (~1 fragment / 5 EPs)
- Driver tone (cold S1 → reluctant warmth S2)
- Hạ Vy presence (whisper EP01-30 → letters/object EP31-60 → near-manifestation EP61-89 → resolution EP90)

**Anti-formula breaks** (milestone EPs ONLY): EP25, EP50 ✅, EP60, EP73, EP85, EP90

### EP51-90 STRATEGY

#### Stay single-Khải Phong (KHÔNG co-protagonist)
- Lore + Night Vale + Old Gods proven: single-voice anthology > multi-POV
- Deepen DRIVER thành quasi-co-lead (3-4 new lines S2, NOT 2)

#### Memory M1-M18 — 3-act payoff
- **EP51-72 Act 1**: Recover M9-M13 — triggered by passenger story (parallel grief)
- **EP73 PIVOT** (22 min extended): M14-M15 reveal Khải Phong = LIMBO STATUS. NO new passenger, Khải Phong rides alone confront driver
- **EP74-89**: Khải Phong knows truth, atones. M16-M17 = bridges to Hạ Vy
- **EP90 FINALE** (25 min): M18 = **Hạ Vy IS một trong passengers Khải Phong định collect**. Resolution: stay (xe chạy forever) hoặc release (xe end, Khải Phong fade) — leave ambiguous

#### 4 Western techniques import
1. **Magnus's "statement Easter eggs"** — plant 1 detail/EP retroactively matters EP73/90
2. **Old Gods's environmental cold open** — 30s pre-intro ambient (engine + rain + radio static + 1 haunting line)
3. **Magnus's season split** — S2A (EP51-72 discovery) + EP73 hinge + S2B (EP74-90 atonement) = 3 season finales total
4. **Night Vale's NPC accrual** — 3-4 passengers S1 referenced (KHÔNG re-appear) in S2

### 5 PRODUCTION RISKS lớn nhất

| Risk | Bằng chứng | Mitigation |
|------|-----------|-----------|
| Narrator voice drift | NoSleep + VN YT channels swap MC → lose 40-60% views | Lock IndexTTS2 anchor + seed + render whole batch 1 session, cosine sim ≥0.85 |
| Archetype repetition no variation | Burnout S8 NoSleep | 90-passenger spreadsheet tag 3 axes (archetype/era/region), no 2 adjacent EPs share 2+ tags |
| Mythology reveal quá sớm | Magnus S4 mistake | M14-M15 KHÔNG before EP73 |
| Episode length creep | Lore 20→45min lost casual listeners | Hard cap 15min standard, chỉ 6 milestone EPs allow 20-25min |
| Skip "dư âm" coda | Kills literary feel | NEVER cut 60-90s closing reflection, Ngạn never did |

**Bonus**: Plan EP50→EP51 marketing pause **4-6 tuần** với teaser trailer dùng EP73 pivot audio (no spoilers). Magnus + Old Gods cùng pause inter-season.

---

## 5. UNIFIED GAP MATRIX — PRIORITIZED ACTIONS

### 🔴 P0 — CRITICAL gap (ship trước EP51)

| # | Action | Source | Effort |
|---|--------|--------|--------|
| 1 | **R68-R73** codify vào constitution (6 rules new) | Agent 2 | 1h |
| 2 | **Bible/21 EP51-90 arc design** (90-passenger archetype matrix + memory M9-M18 progression + EP73/90 spec) | Agent 3 | 3-4h |
| 3 | **R-NEW Ngạn opening hook template** "Bối cảnh + nhân chứng frame" bible/01 + EP02-50 retrofit | Agent 1 | 2h |
| 4 | **R-NEW sensory hierarchy NGHE>LẠNH>MÙI>NHÌN** + 50 EPs ghost manifest audit | Agent 1 | 2h |

### 🟡 P1 — IMPORTANT (ship trong tháng 7)

| # | Action | Source | Effort |
|---|--------|--------|--------|
| 5 | **R-NEW kết lửng pool 4 templates Ngạn** bible/07 | Agent 1 | 30min |
| 6 | **R-NEW bimodal sentence length** VNQA H8 check + audit 50 EPs | Agent 1 | 1.5h |
| 7 | **R-NEW negative-space ghost blacklist** + audit | Agent 1 | 1h |
| 8 | **Generator prompt PHASE 13** import 4 Western techniques (Magnus + Old Gods + Night Vale) | Agent 3 | 2h |

### 🟢 P2 — STRATEGIC (chuẩn bị production scaling)

| # | Action | Source | Effort |
|---|--------|--------|--------|
| 9 | **Voice cosine similarity audit cross-EP** ≥0.85 | Agent 3 | 1.5h |
| 10 | **90-passenger archetype spreadsheet** 3-axis tagging | Agent 3 | 2h |
| 11 | **EP50→EP51 marketing pause** 4-6 tuần với teaser trailer | Agent 3 | external |
| 12 | **Calibrate WPM 155 → 140** sát Ngạn pace + measure 3-5 audio gốc Ngạn (librosa pause histogram) | Agent 1 | 2h test |

---

## 6. RISK REGISTER UPDATED

| Risk | Severity | Probability | Mitigation Status |
|------|----------|-------------|-------------------|
| TTS pronunciation R58-R67 | HIGH | 100% | ✅ ALL VALIDATED + applied 50 EPs |
| 6 missing TTS rules (R68-R73) | MEDIUM | ~30% per rule per EP | ❌ PENDING |
| Voice drift cross-EP | HIGH | medium | ⚠️ Pipeline có, audit chưa wire |
| EP73 + EP90 finale chưa design | HIGH | 100% | ❌ PENDING bible/21 expand |
| Cliffhanger Mỹ-style mất chất Ngạn | MEDIUM | mixed | ⚠️ Cần pool 4 templates |
| Sensory hierarchy ad hoc | MEDIUM | mixed | ⚠️ Cần codify R-NEW |

---

## 7. WHAT SVHMP ALREADY DOES RIGHT (validated externally)

- ✅ Voice anchor strip pattern (Khánh An) = INDUSTRY STANDARD per Agent 2
- ✅ Silence bridge + cross-fade (R59) = production VN TTS workaround chính thức
- ✅ R58 tilde EOL = ALIGN với Tacotron-VN papers Nguyen 2019
- ✅ R86-R89 audit lessons 27/6 = match Brunelle & Jannedy 2007 syllable-timed VN
- ✅ Bible 24-file modular = match Magnus Archives + Lore production discipline
- ✅ Pre-render checklist + post-render gate = match Magnus 2-week sprint discipline
- ✅ 2 driver lines locked = correct DNA preservation per Agent 3
- ✅ Memory M1-M18 fragmentation design = match Magnus statement Easter eggs pattern

---

## 8. SO-WHAT — Top 3 priorities tuần tới

### Priority 1: SHIP 6 RULES MISSING (R68-R73) + retrofit 50 EPs
- Critical cho TTS production quality
- Effort: 1h codify + 2-3h audit 50 EPs
- Output: Bulletproof TTS rendering cho 50 EPs hiện tại

### Priority 2: DESIGN EP51-90 STRATEGIC ARC
- Critical cho season 2 production
- Effort: 3-4h spec bible/21 expansion
- Output: 90-passenger matrix + M9-M18 progression + EP73 pivot + EP90 finale spec

### Priority 3: ADOPT NGỌC NGẠN 7 TECHNIQUES
- Critical cho "kể chuyện đêm khuya" authentic feel
- Effort: 4-5h codify rules + retrofit
- Output: Style fidelity match Ngạn cadence — moat khó copy

---

## 9. STRATEGIC OUTLOOK

**Strength**: SVHMP đang xây kiên cố — rule system + tools + bible modular. 50 EPs GOLDEN + pipeline mature.

**Opportunity**: EP51-90 với EP73 pivot + EP90 finale Hạ Vy reveal sẽ là **moat literary** so với Khánh An / MC Hồng YT channels (chỉ binge-format không có meta-arc).

**Threat**: Nếu skip 6 rules R68-R73 → TTS production EP51-90 sẽ tích lũy artifacts (em-dash flat, dialogue blend, place name wrong). Risk audience churn.

**Recommendation**: Hoàn thành P0 actions (6 rules + bible/21 expand + Ngạn opening template) TRƯỚC khi viết EP51.

---

---

## 10. AGENT 4 — kentjuno/ainovel-cli RESEARCH

### Repo identification
- **kentjuno/ainovel-cli**: Description "CLI sáng tác tiểu thuyết AI đa agent — **Bản tiếng Việt của voocel/ainovel-cli**"
- Created **2026-06-25** (rất mới, 3 ngày trước)
- 43⭐ + 28 forks (vs voocel 1118⭐ + 230 forks)
- Language: **Go** (same as voocel)
- Parent: null (NOT GitHub fork — independent Vietnamese adaptation)
- README 32KB Chinese (paradox — owner VN nhưng content TQ)

### Architecture (kentjuno extends voocel với nuance hơn)

**1. Phase + Flow 2-layer state machine** ✨ NEW
- **Phase** (chỉ tiến không lùi): `init → premise → outline → writing → complete`
- **Flow** (có thể switch): `writing ↔ reviewing ↔ rewriting ↔ polishing ↔ steering`
- Validation cứng — không cho retreat Phase, không cho jump bất hợp lý Flow

**2. 3 IRON LAWS (三铁律)** ✨ NEW
- **Law 1**: Tools chỉ return FACTS, KHÔNG return cross-scheduling instructions
- **Law 2**: Flow Router = pure function (no side effects), code routing chứ không LLM routing
- **Law 3**: Coordinator KHÔNG được physical `end_turn` trừ khi Phase=Complete (StopGuard 5 lần intercept → terminate)

**3. Compass + Vision rolling planning** ✨ NEW
- Khác voocel's standard rolling — kentjuno có **指南针 (Compass)**:
  - Initial: chỉ plan 2 vol skeleton + 1st vol detailed chapters
  - Mỗi vol boundary, Architect update Compass (terminal direction + active long lines + scale estimate)
  - Skeleton arcs = chỉ có goal + ước chapter count
  - Progressive refinement với prior summary + character snapshot

**4. 4-layer memory system** ✨ NEW
- `working_memory` — current chapter context
- `episodic_memory` — long-term continuity check
- `reference_pack` — style rules + anti-ai-tone references
- `memory_policy` — tells AI which to prioritize

**5. chapter_contract per-chapter verification** ✨ NEW
- `required_beats` — must-hit beats per chapter
- `forbidden_moves` — banned actions
- `continuity_checks` — cross-chapter checks
- `emotion_target` — target emotion arc
- `payoff_points` — must-resolve hooks
- `hook_goal` — chapter-end追读驱动力

**6. Aesthetic 5 sub-dimensions với MUST cite source text** ✨ NEW
- Subdivisions: 描写质感 / 叙事手法 / 对话区分度 / 用词质量 / 情感打动力
- Each issue MUST quote原文 — no empty conclusions allowed
- Combined với `style_stats全书级固化` (deterministic statistics)

**7. Anti-AI tone reference** (5 categories, ~50 patterns) ✨ NEW
- 结构: tam-cấu / parallel sentence triples / list-style numbered breaks
- 用词: 4-char idiom堆砌 / 明喻套句 / 量词癖 / abstract big words / contrast definition syntax
- 描写: abstract代具象 / emotion-labeling
- 对话: character homogenization / over-explained motivation / written-style speech
- 节奏: 事事交代完整 / forced ascension chapter-end

**8. style_stats全书级固化** ✨ NEW
- Deterministic patterns cross all chapters
- `patterns章均` — sentence type per-chapter avg
- `top_phrases` — recent high-frequency phrases
- `repeated_sentences` — cross-chapter verbatim repeats
- `ending.short_ratio` — short-end chapter percentage
- `opening_time_rate` — opening time-word rate
- `title_formats` — mixed title format detection

**9. Suspense genre arc templates** ✨ RELEVANT cho horror
- Case investigation arc (10-15 ch)
- Truth-approach arc (8-12 ch)
- Chase/infiltrate arc (12-18 ch)
- Trial/reveal arc (8-12 ch)
- Connected cases arc (15-20 ch)
- Daily/transition arc (4-6 ch)

**10. Observability discipline** ✨ CRITICAL pattern
- `internal/diag` = observer ONLY
- KHÔNG auto-fix, KHÔNG auto-resume, KHÔNG modify flow
- Anti-pattern: idleResume + StallDetector deleted (lesson learned)

### Comparison voocel vs kentjuno

| Aspect | voocel (original) | kentjuno (VN adapt) |
|--------|------|------|
| Stars | 1118⭐ | 43⭐ (mới) |
| Created | older | 2026-06-25 |
| Architecture | Multi-agent + checkpoint | + Phase/Flow + 3 Iron Laws |
| Memory | character snapshots | + 4-layer memory_policy |
| QA | Editor 7-dim | + 5 aesthetic sub-dimensions + cite source |
| Anti-slop | basic | + 50-pattern reference library |
| Rolling arc | linear vol | + Compass + Vision per vol-boundary |
| Genre support | generic | + suspense/fantasy/romance arc templates |
| Verification | post-write | + chapter_contract pre-write |

### 12 SVHMP-applicable techniques từ kentjuno

#### 🔴 P0 — Apply NGAY (tuần 1)

1. **chapter_contract per-EP** — codify `bible/21` mỗi EP có schema:
   ```yaml
   ep_51:
     required_beats: [passenger_intro, ghost_manifest, reveal, kết_lửng]
     forbidden_moves: [resolution_too_early, 2_ghosts]
     emotion_target: melancholic_0.55_peak_at_section_4
     payoff_points: [M9_memory_trigger]
     hook_goal: ep52_passenger_teaser
   ```

2. **Anti-AI tone reference adopt** vào `bible/22_anti_slop_vi.yaml`:
   - 5 categories áp dụng nguyên: structural / vocabulary / description / dialogue / pacing
   - Bổ sung "force ascension chapter-end" — match Ngạn "kết lửng triết lý KHÔNG cliffhanger Mỹ"

3. **Aesthetic 5 sub-dimensions** với MUST cite原文 → Update audit_dialogue_hierarchy + add audit_aesthetic_cite_required.py

#### 🟡 P1 — Apply tháng 7 (sau khi xong P0 round 18)

4. **Phase + Flow 2-layer state machine** cho EP production pipeline:
   - Phase: `init → spec_locked → drafted → rendered → published`
   - Flow: `drafting ↔ qa ↔ rewriting ↔ render ↔ steering`

5. **3 Iron Laws apply cho tools/**:
   - Tools chỉ return facts JSON, không return next-step instructions
   - Routing logic isolate (pure function)
   - Pre-commit hook = StopGuard (R41 đã có nhưng có thể extend)

6. **4-layer memory system** cho generator pipeline:
   - working_memory = current EP scaffold
   - episodic_memory = cross-EP M1-M18 progression
   - reference_pack = bible/22 anti-slop + reference list
   - memory_policy = which to prioritize per task

7. **style_stats全书级固化** — build `tools/style_stats_audit.py`:
   - Cross-EP patterns章均
   - top_phrases recent across 50 EPs
   - repeated_sentences cross-chapter
   - ending.short_ratio per EP
   - opening_time_rate stats

#### 🟢 P2 — Strategic (S2 production)

8. **Compass + Vision rolling planning** — bible/21 expand cho EP51-90:
   - Compass = M1→M18 + Hạ Vy reveal trajectory + 90 EP scale
   - Vol 1 = EP01-30 (already detailed) ✓
   - Vol 2 = EP31-50 (detailed)
   - Vol 3 = EP51-72 skeleton + EP51-60 detailed (Compass updated at EP30/50 vol-boundary)
   - Vol 4 = EP73-90 skeleton + EP73 detailed (PIVOT)

9. **Suspense genre arc templates** import — passenger story arcs:
   - "Truth-approach arc" cho EP73 pivot (Khải Phong approach own death truth)
   - "Connected cases arc" cho EP01-50 thread (passenger revelations connect to Hạ Vy)

10. **Observability discipline** — em đã có 70 audit scripts:
    - Confirm tools ONLY report, NEVER auto-fix without explicit `--apply`
    - audit_episode_gate read-only ✓
    - auto_fix_* explicit `--apply` ✓
    - Sync với kentjuno principle: diag observer-only

11. **chapter_contract verification gate** — extend post_render_gate.py:
    - Add chapter_contract validation
    - Verify required_beats present
    - Flag forbidden_moves violations
    - Check emotion_target arc

12. **Continuity_check theo episodic_memory** — VNQA H9:
    - Cross-EP fact verification (Khải Phong's items count, M1-M18 state, Hạ Vy mentions)
    - Auto-detect inconsistency

### Direct adoption value cho SVHMP

| kentjuno feature | SVHMP applicable | Effort | Impact |
|-----------------|------------------|--------|--------|
| chapter_contract | ⭐⭐⭐ HIGH (Mr.Long stress logic toán/lý) | 4h | 🔥 KILL plot holes |
| Anti-AI tone 5 cat | ⭐⭐⭐ HIGH (Ngạn style fidelity) | 3h | 🔥 Style moat |
| Aesthetic 5 sub-dim cite | ⭐⭐ MED (audit deep) | 2h | Audit quality |
| Phase+Flow state machine | ⭐⭐ MED (pipeline structure) | 3h | Process safety |
| 3 Iron Laws | ⭐⭐ MED (architectural) | 2h docs | Long-term safety |
| 4-layer memory | ⭐⭐⭐ HIGH (generator EP51-90) | 4h | Memory consistency |
| style_stats全书 | ⭐⭐⭐ HIGH (cross-EP audit) | 3h | Catch patterns drift |
| Compass+Vision rolling | ⭐⭐⭐ HIGH (S2 planning) | 4h | Long arc coherence |
| Suspense arc templates | ⭐⭐ MED (EP variety) | 2h | Genre depth |
| Observability discipline | ⭐ LOW (em đã có) | 30min docs | Validate alignment |

---

## 11. CONSOLIDATED ACTION PLAN

### Week 1 (29/6 - 5/7) — P0 ship trước viết EP51

1. **R68-R73 codify** (6 missing rules từ Agent 2) — 1h
2. **chapter_contract schema** (kentjuno) → bible/21 — 4h
3. **Anti-AI tone 5 categories** → bible/22 expand — 3h
4. **R-NEW Ngạn opening hook template** "Bối cảnh + nhân chứng" (Agent 1) → bible/01 — 2h
5. **R-NEW sensory hierarchy NGHE>LẠNH>MÙI>NHÌN** (Agent 1) — 2h
6. **bible/21 expand EP51-90 Compass + Vision rolling plan** (Agent 3 + kentjuno) — 4h
7. **EP73 pivot + EP90 finale spec** (Agent 3 reveal: Khải Phong limbo + Hạ Vy = passenger) — 3h

**Total P0**: ~19h work

### Week 2-4 (6/7-26/7) — P1 ship

8. style_stats全书 cross-EP audit script
9. 4-layer memory system cho generator
10. Aesthetic 5 sub-dim cite required audit
11. Phase + Flow state machine for production pipeline
12. Voice cosine similarity cross-EP audit
13. 90-passenger archetype spreadsheet 3-axis tagging
14. WPM 155 → 140 calibrate sát Ngạn

### Tháng 7 — S2 production start
- EP51-60 batch 1 with new rules enforced
- Marketing pause 4-6 tuần EP50→EP51 với teaser EP73 audio
- Vol-boundary Compass update at EP30/50 review

---

## 12. FINAL VERDICT

**SVHMP_Studio sau round 18:**

✅ **PRODUCTION READY** cho EP01-50 — 50 GOLDEN + 27 rules + 70 scripts
✅ **ARCHITECTURALLY SOUND** — 3 sources externally validate (Ngạn / TTS / horror serial)
✅ **DIFFERENTIATED** — Ngạn-style cadence + tâm linh ám ảnh moat khó copy

⚠️ **GAPS to close trước EP51:**
- 6 missing TTS rules (R68-R73)
- chapter_contract per-EP not codified
- Anti-AI tone reference chưa adopt
- Ngạn opening template + sensory hierarchy chưa rule
- EP73 + EP90 spec chưa drafted

🔥 **OPPORTUNITY**:
EP73 pivot (Khải Phong = limbo) + EP90 finale (Hạ Vy = passenger Khải Phong định collect) = **literary moat** vs Khánh An/MC Hồng channels (chỉ binge-format không meta-arc).

🚀 **ROADMAP**:
P0 19h work → ship EP51 quality bulletproof → EP51-60 batch → EP73 pivot → EP90 finale → S3 sequel option

---

**End of assessment v2 (4-agent synthesis).**

Files referenced trong synthesis:
- bible/00_constitution.yaml (27 rules R40-R67)
- bible/21_series_arc_design.yaml (cần expand EP51-90)
- bible/22_anti_slop_vi.yaml (cần expand 5 categories)
- bible/01_narrative_structure.yaml (cần add Ngạn opening template)
- bible/07_cliffhanger_pool.yaml (cần thêm 4 Ngạn kết lửng)
- prompts/generator.md (cần add PHASE 13)
- tools/audit_*.py (70 scripts)
- HIENPHAP_SUMMARY.md (round 18)
- VERSION.md round 18
- C:/tmp/ainovel-cli/ (kentjuno repo cloned for reference)
- C:/tmp/ainovel_cli_analysis.md (prior voocel analysis)
