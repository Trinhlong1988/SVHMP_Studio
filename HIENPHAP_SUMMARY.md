# SVHMP HIẾN PHÁP TỔNG HỢP — v1.2 + R58-R62 (round 15, 28/6)

> **Source**: `bible/00_constitution.yaml` + `bible/21_series_arc_design.yaml`
> **Total**: 62 rules cứng + Universal Hard Rule Enforcement
> **Mode**: HARD_UNIVERSAL — exception_policy: ZERO

---

## A. UNIVERSAL ENFORCEMENT (v1.2)
- **enforcement_level**: HARD_UNIVERSAL (mọi rule cứng, không soft)
- **pre_render_protocol**: MANDATORY (chạy `pre_render_checklist.py --ep N` PASS trước viết)
- **post_render_gate**: VNQA PASS + word count 2000-2700 + 13min+ + bell/ghost count + rename verified + intro injected

---

## B. NHÓM IDENTITY & STRUCTURE (R33-R44)

### Series Arc (bible/21_series_arc_design.yaml)
- **R33** pillar_interleave: family/promise/love/work/regret xoay vần 90 EPs
- **R34** intensity_phase: warming 0.4-0.6 / heightening 0.6-0.8 / climax 0.8-0.95
- **R35** memory_progression: M1→M18 Khải Phong nhớ Hạ Vy fragmented
- **R36** cross_ep_callback: schedule EP-EP link
- **R37** milestone_ep: 10/20/30/40/50/60/70/73/80/90 đặc biệt
- **R38** object_sub_arc: cluster temporal/geographic/personal
- **R39** word_count: 2200-2500 ideal, hard_floor 2000, hard_ceiling 2700

### Identity Lock (bible/00)
- **R40** intro_hac_da_ky_mandatory: 5 elements (logo voice + tagline + tác giả + series + tagline series + tập)
- **R41** no_commit_if_gate_fail_HARDLOCK: .githooks/pre-commit block
- **R42** driver_foreshadow_line_allowed_cliffhanger: bác tài quote 2 standard + 1 foreshadow CLIFFHANGER
- **R43** tier2_filler_cap_per_ep: filler word ≤ N/EP
- **R44** dictionary_block: forbidden words list

---

## C. NHÓM POV & DIALOGUE (R45-R52)
- **R45** context_block: forbidden context check
- **R46** passenger_first_person_anaphora_accept: passenger nói "em" referring self OK
- **R47** narrator_3rd_person_pov_hardlock: narrator = Khải Phong viewpoint 3rd
- **R48** passenger_dialogue_hierarchy_pronoun: pronoun consistency in dialogue
- **R49** template_variation_hardlock: rotate templates
- **R50** audit_toolkit_mandatory_pre_commit: 17 scripts run
- **R51** dialogue_audit_smart_v2: per-sentence smart detection
- **R52** acceptable_ngoc_ngan_first_person: convention "em" passenger acceptable

---

## D. NHÓM TEMPLATE & STORY MODE (R53-R57)
- **R53** template_pattern_variety_hardlock: chuông/entry/observation xoay 4-5 forms
- **R54** reveal_word_count_min: REVEAL ≥ 600 words
- **R55** driver_R42_strict_enforce: bác tài quote strict
- **R56** story_mode_hồi_tưởng_ám_ảnh: CẤM kể lể chronological resume
- **R57** reveal_vignette_structure: 3-5 vignettes (memory peak / sensory / death / regret / tonight)

---

## E. NHÓM TTS PRONUNCIATION (R58-R62) — NEW ROUND 15

### **R58 — TILDE END-OF-SENTENCE (HARDLOCK)** 🔴
- **Rule**: CẤM TUYỆT ĐỐI từ kết thúc câu bằng nguyên âm dấu NGÃ (~)
- **Why**: BigVGAN/IndexTTS2 prosody bug — dấu ngã ở EOL → đọc thành dấu nặng
- **Examples**:
  - "đi Mỹ." → "đi Mỵ." ❌
  - "khung cũ." → "khung cụ." ❌
- **Banned chars EOL**: ã ẵ ẫ ẽ ễ ĩ õ ỗ ỡ ũ ữ ỹ
- **Detection**: `tools/audit_tilde_eol.py`
- **Auto-fix**: `tools/auto_fix_tilde_eol.py --apply`
- **Status**: 495 → 45 violations (sau apply)

### **R59 — CONCAT SHORT SYLLABLE CỤT (HARDLOCK)** 🔴
- **Rule**: Chuỗi 3+ từ ngắn liền tiếp ở cuối câu → TTS đọc cụt + mix glitch
- **Why**: Concatenation pipeline + TTS prosody decay cuối câu
- **Example**:
  - "Mưa làm ướt một góc nhỏ." ❌
  - "Mưa rơi xuống làm ướt một góc nhỏ trên bàn." ✓

### **R60 — SHORT SYLLABLE EOL (HARDLOCK)** 🔴
- **Rule**: CẤM kết thúc câu bằng từ 1 âm tiết đơn (mono-syllable cụt)
- **Why**: TTS prosody tail decay — single-syllable mất âm cuối
- **Banned**: im / lặng / rơi / đi / ra / qua / lui / tan / nhỏ / to
- **Example**: "Anh đứng im." → "Anh đứng im lặng một hồi lâu." ✓

### **R61 — SHORT SYLLABLE START SENTENCE (HARDLOCK)** 🔴
- **Rule**: CẤM mở đầu câu/đoạn bằng từ 1 âm tiết đơn
- **Why**: TTS accelerate start → "Đêm" / "Hôm" bị cụt / hụt hơi
- **Banned starts**: Đêm / Hôm / Ngày / Năm / Sáng / Chiều / Tối
- **Example**:
  - "Đêm đó mưa từ bảy giờ." ❌
  - "Hôm đó, từ bảy giờ tối, mưa đã rơi không ngớt." ✓

### **R62 — ANAPHORA "NGƯỜI" LIÊN TIẾP (HARDLOCK)** 🔴
- **Rule**: CẤM từ chỉ định danh (người/cô/anh/chị/ông/bà/em/cụ) lặp liền tiếp > 2 trong 3 câu
- **Why**: Repetitive "Một người gia. Người y tá. Người đàn ông trung niên" → TTS đọc đều như list → nhàm chán
- **Max consecutive**: 2
- **Fix pattern**:
  - "Một người gia. Người y tá. Người đàn ông trung niên" ❌
  - "Một cụ già. Cô y tá đứng cạnh. Bên kia, người đàn ông trung niên" ✓

---

## F. LOGIC CONSISTENCY (toán học) — NEW
- **EP01 bug đã fix 28/6**: Khải Phong xuống xe "tay ôm đồng hồ" → ghế số bảy "có vật nhỏ" → 2 đồng hồ? PLOT HOLE. Fix: Khải Phong đặt đồng hồ trở lại ghế trước khi xuống.
- **Rule chung**: Mọi vật mang đi phải tính toán continuity giữa scene (vật mang đi không thể đồng thời ở chỗ cũ).

---

## G. ENFORCEMENT PIPELINE

### Pre-write (BẮT BUỘC)
1. `pre_render_checklist.py --ep N` — verify bible + arc + pillar
2. Read CLAUDE.md → VERSION.md → BUGS_FIXED.md → MEMORY.md

### Post-write (BẮT BUỘC)
1. `audit_episode_gate.py --ep N` — 11/11 PASS
2. `audit_tilde_eol.py --ep N` — 0 HIGH
3. `audit_story_mode.py --ep N` — 0 HIGH
4. `audit_dialogue_hierarchy.py --ep N` — smart check
5. `audit_hidden_bugs.py --ep N` — 20-dim deep
6. `vnqa/orchestrator.py --ep N` — VNQA verdict != CRITICAL
7. `.githooks/pre-commit` 3-layer block

### Audit toolkit (`tools/`)
17+ scripts mandatory:
- `audit_episode_gate.py` — 11-check core
- `audit_tilde_eol.py` — R58 NEW
- `audit_short_eol.py` — R60 (BUILD)
- `audit_short_start.py` — R61 (BUILD)
- `audit_anaphora_consecutive.py` — R62 (BUILD)
- `audit_dialogue_hierarchy.py` — R48+R51
- `audit_story_mode.py` — R56+R57
- `audit_hidden_bugs.py` — 20-dim
- `audit_template_variety.py` — R49+R53
- `vary_bell_entry.py` — R53
- `trim_driver_extras.py` — R42+R55
- `auto_fix_dialogue_hierarchy.py` — R48
- `auto_fix_tilde_eol.py` — R58 NEW
- `vnqa/orchestrator.py` — VNQA full
- `cleanup_vary_artifacts.py` — vary cleanup

---

## H. STATUS HÔM NAY (28/6)

### Fixed
- ✅ R58 tilde-EOL: 495 → 45 violations (auto-fix applied)
- ✅ EP01 plot hole đồng hồ (line 572): đặt lại ghế thay vì mang đi
- ✅ EP01 line 70 "Đêm đó" → "Hôm đó, từ bảy giờ tối" (R61)
- ✅ EP01 + EP11 + EP27 + EP06 + EP36: "Mỹ" → "Hoa Kỳ" (R58)
- ✅ EP11 revert "chị Hạ Vy" → "chị Thu Hà" (rename mistake)
- ✅ R58-R62 codified vào bible/00_constitution.yaml

### Pending (cần Mr.Long approve trước ship)
- ⏳ R60 audit_short_eol.py — chưa build
- ⏳ R61 audit_short_start.py — chưa build
- ⏳ R62 audit_anaphora_consecutive.py — chưa build
- ⏳ R58 remaining 45 violations (cần manual)
- ⏳ 16 EPs còn naked "Hà" — cần per-context rename
- ⏳ EP01 line 248-250 "ngoài cửa kính... ngoài kia" reword
- ⏳ Cross-EP "Đêm đó/hôm/nay" mở đầu pad (R61)
- ⏳ EP23 + EP30 R56 hồi tưởng rewrite
- ⏳ EP44/47/50 REVEAL < 600 expand (R54)
- ⏳ Ship EP51-60 với R58-R62 enforce

---

**End of summary.** Báo cáo chi tiết per-rule trong `bible/00_constitution.yaml`.
