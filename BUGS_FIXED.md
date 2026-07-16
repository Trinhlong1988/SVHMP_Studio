# BUGS_FIXED — SVHMP_Studio

**Rule cứng:** memory `feedback_fix_registry_rule.md` (Mr.Long 26/6)
**Audit script:** TBD — cần tạo `svhmp_bugs_regression.py`
**Session start protocol:** đọc file này + CLAUDE.md project + memory feedback_svhmp_* trước touch code

---

## Round 18 bugs (2026-06-28 — TTS+LOGIC R58-R65 session)

### B51 — EP01 plot hole logic toán: đồng hồ duplicate [FIXED]
- Mr.Long phát hiện: Khải Phong xuống xe "tay ôm đồng hồ" (line 572) → ghế bảy "có vật nhỏ... chiếc đồng hồ nữ vỏ xà cừ" (line 604-614) → 2 đồng hồ duplicate
- Fix: rewrite trance natural — "Bàn tay anh buông lỏng tự khi nào. Chiếc đồng hồ trượt khỏi lòng tay — rơi êm xuống ghế số bảy. Anh không quay đầu nhặt."
- Regression: R65 logic toán/lý/hóa/sinh consistency hardlock + tools/audit_logic_total.py (build phase 2)

### B52 — TTS pronunciation "Mỹ" → "Mỵ" (dấu ngã EOL bug) [FIXED]
- Mr.Long phát hiện: "đoạn đi Mỹ, nghe như đi Mỵ" — TTS BigVGAN bug dấu ngã ở EOL đọc thành dấu nặng
- Cross-EP affected: EP01 / EP06 / EP27 (3x) / EP36 — fix "đi Mỹ" → "đi du học Hoa Kỳ" / "ở Mỹ" → "ở Hoa Kỳ" / "sang Mỹ" → "sang Hoa Kỳ"
- Regression: R58 hardlock + tools/audit_tilde_eol.py (495→43 violations)

### B53 — TTS "Đêm" mở đầu câu hụt hơi [FIXED]
- Mr.Long: "đoạn mở đầu Đêm hôm ấy, chữ Đêm nghe như bị cụt/hụt hơi"
- EP01 line 70: "Đêm đó mưa từ bảy giờ." → "Hôm đó, từ bảy giờ tối, mưa đã rơi không ngớt."
- Regression: R61 hardlock + tools/audit_short_start.py

### B54 — EP11 rename mistake "chị Hà" → "chị Hạ Vy" (2 nhân vật khác) [FIXED]
- Em rename "Hà" → "Hạ Vy" cross-EP trước đã làm SAI EP11 line 131 + 215
- EP11 "chị Hà" = Phạm Thị Thu Hà (chị bác sĩ Đức) ≠ Hạ Vy (người yêu Khải Phong)
- Fix: revert "chị Hạ Vy" → "chị Thu Hà" EP11 only
- Regression: R65 character consistency cross-EP

### B55 — Grammar "chợt" + câu hỏi SAI [FIXED]
- Mr.Long: "dùng từ chợt cho câu hỏi có đúng không?" — "chợt" adverb modifies past-tense statement, KHÔNG hợp câu hỏi
- Fix: bible/22 anti_slop grammar_note — "Anh chợt hiểu chưa?" SAI → "Anh đã hiểu chưa?"
- Regression: R44 dictionary block extend grammar dimension

### B56 — TTS "im./đi./tan." short EOL cụt âm [FIXED]
- Mr.Long: "các từ 2 chữ ở kết thúc câu như im hoặc các từ khác nghe bị cụt âm"
- 1259 violations across 50 EPs → 50 sau auto-fix
- Fix: tools/auto_fix_short_eol.py pad bằng từ ≥2 syllables
- Regression: R60 hardlock

### B57 — Anaphora "người người người" liền >2 nhàm chán [PENDING manual]
- Mr.Long: "người lặp đi lặp lại liên nhau quá 2 lần nghe nhàm chán như lỗi"
- 189 violations across 45 EPs — auto-fix risky meaning change → manual per-context
- Regression: R62 hardlock + tools/audit_anaphora_consecutive.py

### B58 — EP01 "Mặt số La Mã" ending Mã (tilde EOL) [FIXED]
- 2 instances line 41 + 101 → fix "Mặt số La Mã." → "Mặt số La Mã in chìm trên nền cừ."
- Regression: R58

### B59 — EP01 "ngoài cửa kính... ngoài kia" lặp phrase [FIXED]
- Mr.Long: "ngoài cửa kính... xong lại ngoài kia có hợp lý không?"
- Line 248-250: rewrite — "Khải Phong nhìn ra ngoài. Mặt kính đọng giọt mưa nhỏ. Sương đặc thêm sau lớp kính mờ."

---

## Round 17 bugs (2026-06-28 — AUDIO_MIX_RULES codify session)

### B50 — R42 PRO MIX có 1300 sample-level click/pop từ giây 18.85 [RESOLVED detection, PENDING re-mix R43]
- **Ngày catch:** 2026-06-28 (audit_audio_mix_qa.py C13 first run)
- **Phát hiện qua:** `python tools/audit_audio_mix_qa.py --ep 1 --wav output/ep_01/EP01_R42_PRO_MIX.wav` → C13 FAIL HIGH: `1300 click/pop. First @ 18.85s`
- **Triệu chứng:** Khán giả nghe ra "tạp âm loẹt xoẹt" liên tục từ giây 19 trở đi (Mr.Long judge "tạp âm khác"). 1300 chỗ sample-level discontinuity > 0.3 amplitude trong 2 samples liền.
- **Root cause:**
  - `C:/tmp/mix_ep01_v5_pro.py` line 76 `fade_in_out()` chỉ áp fade cho piano section boundaries (3s)
  - SFX accents (line 332-336) chỉ áp fade 0.5s in + 1s out
  - Cross-fade giữa moments (khi music switch category mid-section) KHÔNG có fade → hard cut → click
  - DC offset 4031 windows > 0.001 cũng góp phần (line 346 chỉ DC remove ONCE post-mix, không per-clip)
- **Fix shipped 28/6 (detection):**
  - `tools/audit_audio_mix_qa.py` C13 sample-level click/pop scan implemented + verified work
  - `bible/05 v1.1 R_AUDIO_09_no_audio_artifacts_hardlock` codify zero tolerance + min_fade_ms 80
  - `bible/00 R59` block ship nếu C13 FAIL
- **Fix pending (R43 mixer):**
  - Apply min 80ms fade tất cả clip boundaries (piano + SFX + ambient)
  - Use scipy.signal.resample_poly với anti-alias filter cho SR conversion (currently lib has 22050 + 48000 mix)
  - DC offset removal per-clip + per-section, not just final
  - Re-render R43 + re-audit C13 → must report 0 click
- **Regression test:** `tools/audit_audio_mix_qa.py --ep N` C13 auto-run pre-commit
- **Meta-lesson:** Em ship R42 PRO MIX với "sidechain ducking + 3-tier + climax detect" — sophisticated mixing tech, BUT bỏ qua basic mix hygiene (fade boundaries). Sophistication != quality. Always audit BASICS (click/pop/DC) trước features.

### B49 — assignment_planner.py v1.0 chọn SFX phi lý với setting (fire/chandelier/desert trên xe buýt Hà Nội) [RESOLVED v2.0]
- **Ngày catch:** 2026-06-28 (Mr.Long judge R42 PRO MIX "lồng hiệu ứng không phù hợp")
- **Phát hiện qua:** Em đọc `output/ep_audio_plan.yaml` EP01.sfx → 4/6 picks phi lý setting:
  - SETUP: "13_Fire in fireplace" — xe buýt KHÔNG có lò sưởi
  - INCIDENT: "Shattering Chandelier" — xe buýt KHÔNG có đèn chùm
  - PAYOFF: "Heavy breathing" — không match emotional swell + vi phạm NEVER.jump_scare
  - CLIFFHANGER: "Desert wind" — SVHMP Hà Nội KHÔNG phải sa mạc
- **Triệu chứng:** SFX random từ pool 822 pixabay không cross-check với setting EP. EP01 setting `setting_dem_thang_tu_HN` + `setting_mua_nho` (xe buýt đêm mưa phùn) — SFX picks phải match (rain/wet_road/wiper/lamp), KHÔNG fire/chandelier/desert.
- **Root cause:**
  - `tools/assignment_planner.py` v1.0 line 49 `SFX_BY_SECTION['SETUP']` có `'fire'` → category fire match → picks "Fire in fireplace"
  - Line 49 `'glass'` → picks "Shattering Chandelier"
  - Line 52 `'wind'` → picks "Desert wind"
  - Line 120 `pick_sfx()` chỉ `random.choice(avail)` từ pool, NO semantic context check vs `bible/13 setting_library` hoặc `bible/00 NEVER.gore + NEVER.jump_scare`
  - KHÔNG ưu tiên 25 HDK_* specialized tracks đã categorized sẵn (HDK_MYSTERY/SAD/REVEAL/TENSION/ENDING x5 seeds)
- **Fix shipped 28/6:**
  - `bible/05 v1.1 R_AUDIO_04_setting_sfx_validation` define `forbidden_by_vehicle_context.xe_buyt_dem` list (fire/chandelier/desert/etc)
  - `bible/05 v1.1 R_AUDIO_05` define moment_to_music_category mapping HDK_SAD/REVEAL/MYSTERY
  - `tools/assignment_planner.py` v1.0 → **v2.0** refactor:
    - Layer 1: HDK specialized pick first (`get_hdk_tracks_for_category`)
    - Layer 2: pixabay fallback
    - `pick_sfx()` filter `FORBIDDEN_SFX_KEYWORDS` PRE-pick
    - `SFX_BY_SECTION_V2` removed 'fire'/'glass'/'wolf' from defaults
    - Emit `moment_map_template.yaml` per EP (R_AUDIO_02)
  - `tools/audit_audio_mix_qa.py` C4 setting validation post-pick gate
- **Regression test:** `tools/audit_audio_mix_qa.py --ep N` C4 scan SFX picks vs FORBIDDEN_KW. Verified on R42 PRO MIX → caught 4 violations.
- **Counter:** rule_break N/A (new feature, không repeat violation)
- **Meta-lesson:** Random pick từ metadata-categorized pool KHÔNG đủ — phải có semantic validation layer. Áp global: mọi pick từ asset library cần cross-check với physical setting + bible NEVER rules.

### B51-B55 — bible/00_constitution.yaml 5 pre-existing YAML parse bugs (quoted scalar trailing text) [RESOLVED]
- **Ngày catch:** 2026-06-28 (em add R59 → yaml.safe_load FAIL line 107)
- **Phát hiện qua:** Cascade YAML parse errors fix iteratively (line 107 → 127 → 217 → 263 → 302)
- **Triệu chứng:** `yaml.safe_load(bible/00)` raises `expected <block end>, but found '<scalar>'`. Bibles không load được → mọi tool dependent (audit_60_dimensions, post_render_gate, audit_audio_mix_qa) crash.
- **Root cause (pattern B7 family):** YAML inline syntax với quoted string + trailing text trên cùng line:
  - B51 line 107-110 R56 `must_be: - "Hồi tưởng" — fragments...` (R14 add round 14)
  - B52 line 127-129 R56 `detection_patterns: - "Năm tôi/em [age] tuổi" lặp 5+ lần...`
  - B53 line 215 R58 `boundary_definition: "EOL = ngay trước [.!?—""] hoặc..."` (double quote inside double quote)
  - B54 line 263-266 R53 `banned_overuse: - "Chuông xe ngân. Một tiếng. Tan." identical 32/50...`
  - B55 line 302-304 + 309-311 R51 `acceptable_patterns: - First-person passenger monologue: "Em là X..."`
- **Fix:** Wrap entire string trong single quote outer (`- '"..." trailing'`). Fix 5 bugs total. Verified `yaml.safe_load` returns 48 top keys.
- **Regression test:** `python -c "import yaml; yaml.safe_load(open('bible/00_constitution.yaml', encoding='utf-8'))"` exit 0
- **Cross-ref:** B7 same pattern bible/20 line 240 (round 12 fix). General lesson: NEVER mix quoted string với trailing text trong YAML inline list — luôn wrap single quote outer.
- **Meta-lesson:** Bug pattern này lặp 6 lần (B7 + B51-B55) — em phải audit toàn bộ bibles bằng `yaml.safe_load` round 18 + add pre-commit lint check.

### B49 NAMING CONFLICT — R58 duplicate name in bible/00
- **Ngày catch:** 2026-06-28 (em add R58 audio mới → đã có R58_no_tilde_ending_sentence_hardlock)
- **Triệu chứng:** YAML mapping key conflict (silent — last definition wins)
- **Fix:** Rename em ship `R58 → R59_audio_mix_qa_mandatory_pre_publish`. Update VERSION.md + bible/00 cross-refs.
- **Meta-lesson:** Pre-add rule check `grep "R{N}_" bible/00` để verify name không trùng.

---

## Bugs (seed từ memory entries existing)

### B1 — Arc schema thiếu payoff_owner
- **Ngày catch:** 2026 round 8 (timestamp chính xác trong git history)
- **Phát hiện qua:** Cross-ref bible/11_regret_catalog vs runtime/state.yaml
- **Triệu chứng:** ARC payoff không xác định passenger nào chịu trách nhiệm → 90 ep risk drift
- **Root cause:** Schema state.yaml round 7 thiếu `payoff_owner` field per arc
- **Fix:** `runtime/state.yaml:128-141` add field `payoff_owner: PAS_XXXX` — schema round 8 commented "B5 fix"
- **Regression test:** YAML schema check arcs[].payoff_owner exists for status=OPEN | PAYOFF
- **Cross-ref:** `state.yaml` line 128 comment `# ARCS — schema round 8 (status + importance + payoff_owner — B5 fix)`

### B2 — Bibles 07-10 frozen consumption mismatch
- **Ngày catch:** Round 12
- **Phát hiện qua:** Note round 12 fix B5.1 trong bible/10_brand_audio.yaml
- **Triệu chứng:** Generator FROZEN + QA Lock FROZEN nhưng vẫn load bibles 07-10 → consumption không cần thiết
- **Root cause:** Round 11 add bibles 07-10 không identify consumer correctly. Generator (FROZEN round 11) + QA Lock (FROZEN) KHÔNG cần load 07-10.
- **Fix:** `bible/10_brand_audio.yaml:157-163` note — chỉ TTS Director v1.1 M8 + Publisher v1.0 P1 load bible/10. Bibles 07-09 cũng documented similarly.
- **Regression test:** Audit script check bible consumer mapping per prompt file
- **Cross-ref:** Round 12 fix B5.1, bible/10 line 157

### B3 — Path inconsistent giữa Desktop archive vs D:\ working
- **Ngày catch:** 2026-06-26
- **Phát hiện qua:** Cross-analysis HDK research session
- **Triệu chứng:** 2 SVHMP folder song song (`Desktop\SVHMP_Round3_Lock_20260623\` 35 files vs `D:\...\SVHMP_Studio\` 92 files), không rõ canon
- **Root cause:** Lock snapshot 23/6 (Desktop archive) vs working production round 11 onwards (D:\)
- **Fix:** Confirmed `D:\...\SVHMP_Studio\` = CANON. Desktop = historical lock reference, KHÔNG modify.
- **Regression test:** Manual check: mọi script + memory ref `D:\...\SVHMP_Studio\` path. Desktop folder = read-only archive.
- **Cross-ref:** session 26/6 verification turn

---

### B40 — EP12-19 + EP31-34 < 2000 từ (R39 hard_floor) VI PHẠM 2 LẦN [RESOLVED hiến pháp v1.3 R41 HARDLOCK]
- **Ngày catch:** 2026-06-27 (Mr.Long audit "fix toàn bộ lỗi xử lý nghiêm hiến pháp cấm tái diễn")
- **Phát hiện qua:** Em chạy `post_render_gate.py` cho EP01-35 → 35 EP audit → phát hiện EP12-19 FAIL R39 hard_floor (1596-1953 từ < 2000) + EP31-34 FAIL R39 (đã fix triệt để trước nhưng commit lỗi gate detection)
- **Triệu chứng:**
  - EP12-19: viết quá ngắn (1606-1953 từ) — vi phạm R39 hard_floor 2000 từ
  - EP31-34: vi phạm R39 lần thứ 2 (vừa fix trước đó)
  - Em commit DÙ đã có rule R39 — không tự verify trước commit
- **Root cause:**
  - **Root 1 (em):** không chạy `post_render_gate.py` trước khi commit — viết xong → commit ngay
  - **Root 2 (process):** không có physical block — em commit được dù gate FAIL
  - **Root 3 (gate):** post_render_gate có false positive cho EP01-10 (golden + initial 10) vì phrase variant bell/ghost
- **Fix shipped 27/6 (hiến pháp v1.3 + R41 HARDLOCK):**
  - Update `tools/post_render_gate.py` accept phrase variants (chuông xe/chuông giao thừa/chuông ngân/[chuông + hiện ra/hiện lên/bóng người/một thoáng) + metadata bell_count fallback
  - Expand EP12-19: append CLIFFHANGER block deeper Khải Phong internal monologue về Hạ Vy (bà ngoại Liên trồng cúc / ảnh hai đứa cài cúc tai / sổ tay nhật ký Hạ Vy) — all 8 EPs PASS hard_floor 2000+ từ
  - Add `bible/00 R41 no_commit_if_gate_fail_HARDLOCK`:
    - Cấm commit nếu gate FAIL
    - Vi phạm = LOG B40 + counter rule_break
    - Auto-block via git pre-commit hook
  - Add `.githooks/pre-commit` script auto-block commit nếu staged EP files FAIL gate
  - Activate hook qua `git config core.hooksPath .githooks`
- **Verify:** 35/35 EPs PASS gate 11/11 (sau fix)
- **Regression test:** git pre-commit hook block physical — em không thể commit FAIL EP nữa
- **Counter:** rule_break_count = 2 (R39 vi phạm 2 lần — EP21-25 + EP12-19/EP31-34 sequential)
- **Meta-lesson:**
  - Per-rule constitution KHÔNG đủ nếu KHÔNG có process enforcement physical
  - Hooks > documentation — hook block 100%, doc rely on em đọc
  - Em đã hứa "tránh làm đi làm lại" nhưng vẫn lặp — chỉ có hook physical mới đảm bảo
  - Cross-ref: `feedback_fix_registry_rule` + `feedback_svhmp_arc_lesson` + memory mới `feedback_svhmp_r41_hardlock`

### B37 — EP11-41 LỘN XỘN NO ARC TỔNG ("không thành bản nhạc") [RESOLVED hiến pháp v1.1]
- **Ngày catch:** 2026-06-27 (Mr.Long 26/6 reject sau ship EP36-41)
- **Phát hiện qua:** Mr.Long judgement nghe 31 EPs hand-craft EP11-41 — "rất lộn xộn không thành bản nhạc"
- **Triệu chứng:** 
  - L1: Linear pillar distribution — 6 EPs FAM_005 liên tiếp / 4 EPs LOV_001 liên tiếp → block flat
  - L2: Mỗi EP đứng riêng — không cross-EP arc → khán giả không có "case theo dõi"
  - L3: Intensity flat 0.55 từ EP11→EP41 → không cao trào tăng dần
  - L4: Quang memory unlock random + đơn lẻ → không thấy Quang đi đâu về đâu
  - L5: Item collection chỉ counter — 38 items thành 38 mảnh rời rạc
  - L6: Milestone EP10/20/30/40 không khác EP thường — không "ô nhịp"
- **Root cause:** Per-EP constitution PASS không đảm bảo series-level "bản nhạc". Hiến pháp v1.0 chỉ có per-EP rules (ALWAYS_5, NEVER_7, GHOST_RULES_3, SERIES_RULES_8) — THIẾU series-wide ARC rules.
- **Fix shipped 27/6 (hiến pháp v1.1):**
  - Add `bible/00 SERIES_ARC_RULES` 6 rules R33-R38:
    - R33: pillar_interleave (max 2 consecutive same pillar)
    - R34: escalation_curve_enforcement (per-phase intensity)
    - R35: quang_memory_unlock_progressive (M1-M18, 5 EPs/fragment)
    - R36: cross_ep_callback_required (≥1 callback per 10 EPs)
    - R37: milestone_ep_rule (EP10/20/30/40/50/60/70/80/90 turn points)
    - R38: object_collection_arc (sub-arc symbol/temporal/geographic)
  - Tạo `bible/21_series_arc_design.yaml` — EP-level arc map 90 EPs (M1-M18 memory progression + pillar interleave map + intensity per-EP + callback schedule + object sub-arc)
  - Doc proposal: `docs/svhmp_arc_50ep_design.md`
- **Regression test:** QA Lock add PHASE 12.16-12.18 check R33-R38 per-EP + cross-EP arc
- **Action pending:** Rework EP11-41 theo arc map mới (Option C user choose 27/6) — pending approve 5 câu hỏi trong design doc
- **Cross-ref:** memory `feedback_svhmp_arc_lesson.md` (new) — codify lesson learned
- **Meta-lesson:** Mỗi tập có thể PASS riêng nhưng series 90 EPs phải có flow. Per-EP rules ≠ series-wide rules. Tránh "fix bug riêng quên forest tổng".

### B36 — Pool naming NU 48 < 50 needed → 2 wrap → 4 word dup + 98/100 unique [RESOLVED]
- **Ngày catch:** 2026-06-27 audit 50 vòng constitution (Mr.Long lệnh)
- **Phát hiện qua:** R24, R25, R27 trong `C:/tmp/svhmp_constitution_50round_audit.py`
- **Triệu chứng:** 4 syllables (Hạ, Diệu, Diễm, Tường) lặp 2x. 98/100 unique full names.
- **Root cause:** FEM bank 121 syllables nhưng overlap với MAS bank (Tâm, Hân, ...). Sau exclude used_mas (100 syl từ NAM pool 50), FEM effective còn 96 → 48 pair. Cần 50 pair → thiếu 2.
- **Fix shipped 27/6:** Add 12 pure feminine syllables NEW vào `data/vietnamese_names_extended.yaml` feminine.b36_fix_2026 (Tô / Mỵ / Bạch / Khuyên / Hảo / Trầm / Mộng / Tuyên / Phấn / Vịnh / Trầu / Quách). Verified KHÔNG overlap với MAS bank.
- **Verify:** Pool NU 50 + NAM 50 = 100 names, 100/100 unique, 0 word duplicate. **50/50 audit PASS** (100%).
- **Meta-lesson:** Khi 2 bank cần distinct uniqueness cross-bank, add syl mới phải verify không overlap qua check `not in mas_syls`. Em đã thử lazy thêm syl trùng → fail.

### B35 — gen_100_passenger.py wrap-around khi pool < count
- **Ngày catch:** 2026-06-27 Phase build pool
- **Phát hiện qua:** Sample EP3 hiển thị "Minh Khang" — tên LEGACY hardcoded trong gen_100_passenger.py overwrite pool load
- **Triệu chứng:** Pool load 50 NU + 43 NAM nhưng kết quả gen có tên ngoài pool (legacy)
- **Root cause:** Em rename `NAMES_NU → _LEGACY_NAMES_NU` nhưng QUÊN rename `NAMES_NAM` legacy → legacy NAMES_NAM hardcoded overwrite pool load.
- **Fix:** `tools/gen_100_passenger.py` rename legacy NAMES_NAM → `_LEGACY_NAMES_NAM` (commit cùng bài).
- **Meta-lesson:** Khi pivot data source, RENAME ALL legacy variables. Search & replace half-way = bug.

### B34 — Ollama keep_alive=0 chỉ unload model LOGICALLY, CUDA context vẫn giữ ~5-7GB VRAM
- **Ngày catch:** 2026-06-26 Phase H series ollama check (Mr.Long bắt verify)
- **Phát hiện qua:** Sau invoke Gemma 2 9B với `keep_alive=0`, wait 60s+ → `/api/ps` returns `models loaded: []` BUT `nvidia-smi` shows VRAM 14.8GB still used. `llama-server.exe` worker process PID alive với 7.9 MB RSS NHƯNG giữ CUDA context.
- **Triệu chứng:** TTS IndexTTS2 cần 15GB VRAM peak → conflict với Gemma 7GB persistent → OOM khi orchestrator chain qua TTS render.
- **Root cause:** Ollama API `keep_alive=0` chỉ unload model weights khỏi worker memory, nhưng worker process (`llama-server.exe`) vẫn alive giữ CUDA initialization context. CUDA không reclaim VRAM cho tới khi process exit.
- **Fix:** `tools/llm_router.py` + `free_ollama_vram()` helper subprocess `taskkill /F /IM llama-server.exe` sau ollama invoke. Ollama daemon (ollama.exe) tự respawn worker khi có request mới (~20s reload tax, chấp nhận vì Skeptic invoke hiếm 1x/EP).
- **Verified:** VRAM 14.8GB → 10.3GB sau invoke + auto-kill (4.5GB CUDA freed). Helper standalone: 15.7GB → 10.5GB (5.2GB).
- **Meta-lesson:** Ollama API documentation không nói rõ "unload" chỉ logical-level. Production cần kill worker process để guarantee VRAM free. Áp dụng cho mọi local LLM Ollama-based future.

### B33 — Windows schtask + Vietnamese path = corrupt + fail (3 attempts)
- **Ngày catch:** 2026-06-26 Phase H5 ship install
- **Phát hiện qua:** `schtasks /Run /TN SVHMP_AutoWatch` Last Result: -2147024629 (0x8007010B ERROR_DIRECTORY) hoặc 2 (FILE_NOT_FOUND)
- **Triệu chứng:** Schtask `Start In` field + cmd.exe parser không decode UTF-8 Vietnamese chars trong `D:\DỰ ÁN AI\...`. Manual invoke OK nhưng qua schtask fail.
- **Root cause:** Windows scheduled task store + invoke với OEM codepage default (cp437/cp1252) — Vietnamese UTF-8 bytes mis-interpret.
- **3 attempts failed:**
  - V1: wscript + .vbs → wscript COM Run() Vietnamese path corrupt
  - V2: pythonw direct + WorkingDirectory Vietnamese → Start In field corrupt → rc=-2147024629
  - V3: .bat at ASCII path → cmd.exe parser breaks Vietnamese chars trong CD command line → bị cắt thành multiple invalid commands
- **Final fix:** ASCII-only Python starter `C:\Users\Administrator\svhmp_auto_watch_starter.py` (Python handle UTF-8 path natively). Schtask Execute=pythonw.exe + Argument=starter.py (cả 2 ASCII path).
- **Live verified:** Daemon PID 39488 alive, spawn EP02 fake → 10s catch + autofix CLEAR.
- **Meta-lesson:** Windows + Vietnamese path + (schtask | cmd | wscript) = LUÔN dùng ASCII proxy. Áp global cho mọi Windows automation task tương lai.

### B32 — orchestrator subprocess UnicodeDecodeError cp1252 Vietnamese characters
- **Ngày catch:** 2026-06-26 Phase H4 wire verify
- **Phát hiện qua:** Test `python tools/qa_skeptic_orchestrator.py --ep 2 ...` → `UnicodeDecodeError: 'charmap' codec can't decode byte 0x8d` trong subprocess._readerthread
- **Triệu chứng:** Subprocess stdout có Vietnamese characters (→, ✓, "bùn cầu") → Windows cp1252 default codec không decode được → `af_run.stdout = None` → orchestrator log không write đầy đủ. NHƯNG auto_fix.py vẫn chạy success (write file IO trước stdout decode).
- **Root cause:** `subprocess.run(text=True)` không specify encoding → fallback Windows cp1252 → crash với UTF-8 output Vietnamese.
- **Fix:** Add `encoding='utf-8', errors='replace'` vào 3 `subprocess.run` calls (autofix, vnqa, skeptic) trong `tools/qa_skeptic_orchestrator.py`.
- **Regression test:** TBD — add e2e test `orchestrator_subprocess_encoding.py` invoke với fake EP có Vietnamese characters, assert stdout_tail không empty.
- **Meta-lesson:** Windows + Python subprocess + Vietnamese = LUÔN cần `encoding='utf-8'` explicit. Áp dụng global cho mọi project SVHMP_Studio/HDK/tro-ly future.

### B31 — EP01 "bùn cầu" 2x mispronounce thành "bồn cầu" (toilet) — VNQA H8 catch [RESOLVED]
- **Ngày catch:** 2026-06-26 Phase H3 ship verify (VNQA H8 collocation lexicon wire 1st run)
- **Phát hiện qua:** `tools/vnqa/pipeline.py` H8 check `_forbidden_patterns.phonetic_risk` match pattern `"bùn cầu"` 2x trong `output/ep_01/episode.md` (line 532 + 675)
- **Triệu chứng:** TTS BigVGAN render đọc "bùn cầu" → phát âm gần như "bồn cầu" (toilet). Người nghe sẽ hiểu "mùi sông Hồng. mùi bồn cầu" = mùi toilet trên xe → break atmosphere horror nghiêm trọng.
- **Root cause:** Generator EP01 viết "bùn cầu" (bùn dưới chân cầu Long Biên) — văn viết OK nhưng văn nói/TTS không OK do phonetic ambiguity.
- **Fix:** Mr.Long approve 26/6 option 3 "phù sa sông Hồng". Replace line 532 + 675 ep_01/episode.md. Re-run VNQA verify "bùn cầu" KHÔNG còn flag.
- **Note:** Line 532 sau fix có lặp "sông Hồng" 2x (`Mùi sông Hồng. Mùi phù sa sông Hồng.`) — chấp nhận Mr.Long, tinh chỉnh sau nếu cần.
- **Catch lý do:** 25+ vòng QA trước miss vì check thủ công không cover phonetic ambiguity. VNQA H8 `_LEXICON._forbidden_patterns.phonetic_risk` có sẵn pattern này từ trước, chỉ chưa wire vào pipeline.
- **Regression test:** Tự nhiên có — `data/vnsl_lexicon.json` `_forbidden_patterns.phonetic_risk` chứa pattern.
- **Meta-lesson:** Có data tốt nhưng chưa wire = vô dụng. Phase H1 ship `data/vnsl_lexicon.json` đầu session nhưng pipeline chỉ wire ở Phase H3 → miss 25 vòng QA. Future: wire DATA ngay khi ship, không defer "Phase X sau".

### B30 — VNQA pipeline.py SVHMP path resolve thiếu 1 `.parent` → lexicon + resources không load
- **Ngày catch:** 2026-06-26 Phase H2 wire verify (Mr.Long bắt verify "không suy luận")
- **Phát hiện qua:** Test `_LEXICON.keys()` returns `[]` dù file exists (17454 bytes) + JSON parse OK manual
- **Triệu chứng:** `tools/vnqa/pipeline.py:46` `SVHMP = Path(__file__).parent.parent` resolve về `tools/` thay vì `SVHMP_Studio/`. Mọi load `SVHMP/'data'/'vnsl_lexicon.json'` fail silent (return `{}`).
- **Root cause:** Pipeline.py nằm sâu 3 level (`tools/vnqa/pipeline.py`), chỉ `.parent.parent` = `tools/`. Cần `.parent.parent.parent` = SVHMP_Studio.
- **Fix:** `tools/vnqa/pipeline.py:46` thêm 1 `.parent` → `Path(__file__).parent.parent.parent`. Verify: 8 top keys + 9 voice_speech entries load OK.
- **Regression test:** TBD — add `vnqa_path_resolve_test.py` assert `_LEXICON` non-empty + `_RES_AI` non-empty.
- **Cross-ref:** Verify log `_LEXICON keys: ['_meta', '_verb_usage_guide', '_forbidden_patterns', 'sensory', 'body_gesture', 'voice_speech', 'emotion', 'temporal']`
- **Meta-lesson:** Em ship `_load_lexicon()` với try/except silent return `{}` — che bug. Future: log warning khi load fail thay silent.

### B29 — VNQA H1 token_repeat over-flags proper nouns + central objects (false positive)
- **Ngày catch:** 2026-06-26 Phase H wire Step 1 (first real EP01 test)
- **Phát hiện qua:** `tools/vnqa/pipeline.py --episode output/ep_01/episode.md` returned 10 WARN, 4 are "anh"/"đồng hồ"/"ghế"/"tay" repeat 30-72x
- **Triệu chứng:** Token repeat check flags character names + central narrative objects as suspicious repetition. False positive for narrative content (Quang appears 72x = normal; đồng hồ xà cừ kim 7:10 ARC_0001 central prop appears 38x = expected).
- **Root cause:** H1 underthesea POS check không có whitelist cho proper nouns (NNP tag) hoặc canon objects từ `bible/12_object_library` + `runtime/canon_registry.yaml`.
- **Fix:** PHASE H2 tune planned — load proper noun whitelist + central object whitelist từ canon_registry, skip token_repeat check cho whitelisted terms. Mr.Long approve "ship + tune sau" pattern (memory `feedback_validated_params_no_drift.md`).
- **Workaround current:** Verdict WARN cho phép pipeline tiếp (chỉ FAIL escalate REGEN). Mr.Long manual review flag false positive.
- **Regression test:** TBD — add `svhmp_vnqa_tune_check.py` sau khi tune (Phase H2).
- **Cross-ref:** `prompts/qa.md` PHASE 12.20 known_limitations + `runtime/vnqa_ep_1.json` evidence

### B28 — F1+F2 audit R06 hardcoded v1.3 (same pattern B26)
- **Ngày catch:** 2026-06-26 (round 14 F3+F4 ship — F1+F2 regression test)
- **Phát hiện qua:** F3+F4 audit R11 cross-trigger F1+F2 → FAIL 14/15
- **Triệu chứng:** Bump qa.md v1.3→v1.4 → F1+F2 audit R06 fail (hardcoded "v1.3")
- **Root cause:** SAME pattern B26 — em quên apply monotonic check khi tạo F1+F2 audit. "Fix trước quên sau" precedent rule failed mặc dù em đã có rule cứng — lesson: cần audit cross-script linting nếu có hardcoded version
- **Fix:** F1+F2 audit R06 dùng regex parse + check ≥v1.3 monotonic
- **Regression test:** F3+F4 R11 auto-trigger F1+F2 cross-verify
- **Cross-ref:** B26 same pattern, B23 same lesson (regex monotonic, NOT hardcoded string)
- **Meta-lesson:** Em ship 3 audit scripts (HDK, arc, F1F2), 2/3 đầu vi phạm cùng pattern. Cần checklist "monotonic version" pre-commit cho mọi audit script tương lai.

### B27 — F3+F4 audit script self syntax error (quote escape)
- **Ngày catch:** 2026-06-26 (round 14 F3+F4 ship)
- **Phát hiện qua:** Run audit immediately fail SyntaxError line 57
- **Triệu chứng:** `has_ollama_branch = "..." in src or 'provider'] == "ollama"' in src` — unmatched `]`
- **Root cause:** Em viết double-condition với mixed quote escape sai
- **Fix:** Bỏ second condition, dùng single string check
- **Regression test:** F3+F4 audit run exit 0
- **Cross-ref:** Lesson Python script self-audit — `python -c "import ast; ast.parse(open(...).read())"` trước run

### B26 — Pattern 5 arc_audit regression khi qa.md bump v1.2→v1.3
- **Ngày catch:** 2026-06-26 (round 14 F1+F2 ship)
- **Phát hiện qua:** F1+F2 audit R15 regression test (must 10/10 Pattern 5)
- **Triệu chứng:** Pattern 5 arc_audit fail 9/10 sau khi bump qa.md v1.2→v1.3. R05 check "v1.2 in qa.md" hardcoded — không match khi version bumped.
- **Root cause:** `has_v12_id = "SVHMP_CMD_QA_MASTER_LOCK_v1.2" in qa` hardcoded version string. Khi version bump → string không match → FAIL false positive.
- **Fix:** `C:\tmp\svhmp_arc_audit.py` R05 — dùng regex parse version + check monotonic ≥v1.2 thay vì exact match
- **Regression test:** R15 trong F1+F2 audit auto-trigger arc_audit cross-verify
- **Cross-ref:** General lesson — audit scripts cần monotonic version check, KHÔNG hardcode (similar pattern với B23 e2e regex). Apply cho mọi audit script tương lai.

### B25 — Pipeline svhmp_v13_render.py IndentationError sau add try/except wrapper
- **Ngày catch:** 2026-06-26 (round 14 hook insertion)
- **Phát hiện qua:** `python -c "ast.parse(...)"` IndentationError line 150
- **Triệu chứng:** Em wrap toàn pipeline trong `try:` block + add hook calls, nhưng for-loop body (line 150-209) không re-indent +4 spaces → Python parse fail
- **Root cause:** Edit add `try:` ở level main(), expect body code indent +4 spaces. Em chỉ edit cụ thể vài line, KHÔNG indent recursive toàn for-body.
- **Fix:** Rewrite svhmp_v13_render.py — BỎ try/except wrapper, dùng `atexit.register` cho cleanup case crash. Hook calls minimal insertion KHÔNG nest level mới.
- **Regression test:** `python -c "ast.parse(open(svhmp_v13_render.py).read())"` exit 0 OK
- **Cross-ref:** Lesson chung: thêm wrapper try/except cần re-indent toàn body. Prefer atexit/decorator pattern để minimal change.

### B23 — e2e test T6 regex false positive Video V1-V6 vs Video_intro V7-V9 overlap
- **Ngày catch:** 2026-06-26 (round 14 F3.1 ship)
- **Phát hiện qua:** `C:/tmp/e2e_pipeline_test.py` T6 FAIL "overlap {'6', '1'}"
- **Triệu chứng:** Audit báo Video V1 + V6 trong cả video.md + video_intro.md (overlap)
- **Root cause:** Regex `r'V(\d+)'` match cả module headers (V1 SCENE GRAPH) lẫn text refs ("parent: video.md V1-V6"). False positive.
- **Fix:** `tools/e2e_pipeline_test.py` T6 — regex `r'(?:^|\n|═\s+)V(\d+)\s+[A-Z]'` chỉ match module headers (V<n> + space + uppercase title)
- **Regression test:** T6 PASS sau fix — video={'1'..'6'}, intro={'7','8','9'}, disjoint
- **Cross-ref:** General lesson: regex parse markdown phải distinguish heading vs text ref. Apply cho audit scripts tương lai.

### B2-DETAIL — Bible consumer mapping audit results (15 mismatch + 6 missing header + 1 unused)
- **Ngày catch:** 2026-06-26 (round 14 F3.2 ship)
- **Phát hiện qua:** `tools/bible_consumer_audit.py` first run
- **Triệu chứng:** 15 bible declared consumer X nhưng X.md không reference; 6 bible thiếu "# Loaded by:" header; 1 bible (17_sfx_acquisition_pipeline) không prompt nào reference
- **Status:** TENTATIVE — parser em chưa smart split "TTS Director M8" → "tts" có thể false positive. Need Mr.Long review từng case
- **Root cause candidates:**
  1. Bible declares consumer nhưng consumer load INLINE (không qua explicit `bible/NN_*.yaml` ref) — false positive script
  2. Bible declaration sai (typo "Generator" thực ra không load)
  3. Bible orphan (17_sfx_acquisition_pipeline) — verify intentional hay defunct
- **Fix:** Audit script ship + Mr.Long review từng mismatch. Mỗi mismatch confirmed bug → fix bible header hoặc add ref to prompt.
- **Regression test:** `python tools/bible_consumer_audit.py` re-run sau fix → expect 0 mismatch

### B7 — YAML parse fail bible/20 line 240 inline array với trailing text
- **Ngày catch:** 2026-06-26
- **Phát hiện qua:** Audit script `C:\tmp\svhmp_arc_audit.py` R01 sau ship Pattern 5
- **Triệu chứng:** `yaml.safe_load(bible/20)` raises "expected <block end>, but found '<scalar>'" line 240 col 65
- **Root cause:** YAML inline flow array `[...]` cho phép text trailing trên cùng line. Line 240: `- regen_scope_suggestion: ["story_only", "continuity_only"] (per existing allowed_regen_scope)` — text `(per existing...)` sau `]` phá flow.
- **Fix:** `bible/20_arc_rolling_expansion.yaml` line 240 — quote entire string thành 1 scalar: `- "regen_scope_suggestion: [story_only, continuity_only] (per existing allowed_regen_scope)"`. Tương tự lines 237-239 cũng quote.
- **Regression test:** `C:/tmp/svhmp_arc_audit.py` R01 — `yaml.safe_load(bible/20)` parse OK
- **Cross-ref:** Pattern giống B1 HDK (YAML colon parse) — general lesson: YAML inline syntax cẩn thận khi có text mixed. Apply rule: prefer block syntax + comment `#` thay vì inline flow + trailing text.

## Bugs cần verify từ git history (em chưa đọc full)

- Round 3 → 11 evolution có nhiều fix em chưa list. Mr.Long verify từ git log nếu cần seed thêm.

---

## Audit regression coverage

**Audit script:** `C:\tmp\svhmp_arc_audit.py` (Pattern 5 Rolling Arc regression — 10 rounds)

Coverage:
| Bug | Check method | Status |
|---|---|---|
| B1 arc payoff_owner field exists | R08 state.arcs[] schema match bible/20 (11 fields) | ✓ permanent |
| B2 Bible consumer mapping | Manual review needed (cần audit riêng) | TODO |
| B3 Desktop vs D:\ canon | Manual (no script ref Desktop archive) | TODO |
| B7 YAML parse bible/20 inline array trailing text | R01 yaml.safe_load(bible/20) | ✓ permanent |

Re-run command: `python C:/tmp/svhmp_arc_audit.py` — must PASS 10/10.

---

## Stats

- Total bugs caught: 6 (B1-B3 seed + B7 + B23 + B2-DETAIL during 7-gap ship round 14)
- Total regression tests: 22 (Pattern 5: 10r + Pattern 7: 10r + e2e_pipeline: 10r — B1 + B7 + B23 covered)
- Last audit run: 2026-06-26 round 14
  - `C:\tmp\svhmp_arc_audit.py` Pattern 5: 10/10 PASS
  - `C:\tmp\svhmp_related_eps_audit.py` Pattern 7: 10/10 PASS
  - `tools/e2e_pipeline_test.py` e2e: 9/10 PASS, 1 WARN (T5 tts.md optional ref), 0 FAIL
  - `tools/bible_consumer_audit.py` consumer mapping: 15 mismatch (TENTATIVE — Mr.Long review)
- Round 14 NEW tools ship:
  - `tools/analytics_populate.py` (F2 telemetry)
  - `tools/bible_consumer_audit.py` (F3.2 B2 fix)
  - `tools/e2e_pipeline_test.py` (F3.1)
  - `tools/llm_router.py` (F4.1 skeleton)
  - `tools/cost_tracker.py` (F4.2)
- Phase D2 Pattern 7 shipped clean (0 bug caught)
- 7-gap round 14 ship: 2 bugs caught (B23 e2e regex + B2-DETAIL data)
- Git init round 14 + tagged round_13_initial baseline

### B41-B47 — Round 18-24 lessons (28/6)

#### B41 — Audit script formulaic template detection [RESOLVED R49]
- Pattern 40/50 EPs same HOOK "Đêm tháng tư. Mưa nhẹ." formulaic AI
- Fix: tools/detect_template_repetition + tools/vary_templates + R49 hiến pháp
- Result: 40 → 0 EPs với pattern (varied 10 templates)

#### B42 — POV narrator 3rd person bug 49 EPs [RESOLVED R47 + rewrite]
- EP01 golden ref: "Khải Phong... anh..." 3rd person ✓
- EP02-50: "Khải Phong... em..." mix 1st/3rd POV (275 violations)
- Fix: R47 hiến pháp + tools/rewrite_pov 457 replacements em→anh
- Result: 275 → 0 violations

#### B43 — Dictionary + Context cấm + dialogue hierarchy [RESOLVED R44+R45+R48]
- Mr.Long lệnh: verify từ điển, ngữ cảnh, dùng từ đúng, KHÔNG SUY LUẬN
- Fix: R44 dictionary block + R45 context block + R48 dialogue hierarchy
- Audit: 70 → 100 deep dimensions

#### B44 — Anaphora threshold raise for Ngọc Ngạn first-person [RESOLVED R46]
- Passenger tự kể "Em là... Em sống... Em đi..." 8-14 consecutive = intentional Vietnamese narrative
- Audit script raise threshold 5 → 15 HIGH (Ngọc Ngạn accept)
- R46 hiến pháp codify

#### B45 — Dialogue R48 hierarchy 154 HIGH issues [PARTIAL FIX]
- Passenger gọi người đã mất lẫn "em" thay vì "chị/anh/con"
- EP40 manual fix complete + tools/auto_fix_dialogue_hierarchy 29 patterns
- Still 152 HIGH remaining — many are false positives (Ngọc Ngạn first-person monologue)

#### B46 — EP01 format inconsistency với EP02-50 [PENDING]
- EP01: `## 1. HOOK (≤120 từ — 0:00—0:20) [beat_1: TÒ MÒ]`
- EP02-50: `# HOOK [section 1]`
- Pending unify (low priority, not affecting TTS)

#### B47 — Bác tài liếc gương template overuse [PENDING]
- 100 occurrences across 50 EPs (2x/EP avg)
- Acceptable per R42 driver foreshadow but template feel
- Pending vary phrasings

ROUND 18-24 TOTAL ARTIFACTS:
- New rules: R41, R42, R43, R44, R45, R46, R47, R48, R49, R50 (10 rules)
- New tools: 9 audit/fix scripts
- Pre-commit hook R50 mandatory 3-layer (POV + 70-dim + formulaic)
- Counter rule_break_count: 2 (R39 vi phạm 2 lần — historical)

---

## Round 20 bugs (2026-06-30 — Tier 2.x driver dialogue context)

### B60 — EP01 cliffhanger: bác tài "Chưa tới lúc" với cô gái mới = vô lý + cụt ngủn [FIXED]
- **Mr.Long phát hiện 30/6:** "đoạn cuối với cô gái đa vô lý ko rõ ý gì, cụt ngun"
- **Bối cảnh:** EP01 line 526-528. Khải-Phong vừa "nhớ ra rồi — bảy giờ mười là lúc cô gái ấy mất" → rời xe. Cô gái mới xuất hiện ghế bảy giữ đủ 12 (`fact_004`). Bác tài thì thầm: "— Chưa tới lúc đâu cháu ạ."
- **Root cause (3 lớp):**
  1. **Sai trigger:** câu Q2 "Chưa tới lúc" theo `bible/02_lore_db.yaml:20` là TRẢ LỜI khi passenger HỎI bác tài. Scene cuối cô gái KHÔNG hỏi → dialogue floating, không trigger.
  2. **Cụt ngủn:** "Chưa tới lúc đâu cháu ạ" thiếu object/complement. Bible LOCK câu cộc gọn vì giả định trigger câu hỏi tạo object ngầm.
  3. **Logic break `fact_003`+`fact_004`:** cô gái VỪA xuất hiện (passenger mới) → đáng lẽ trigger Q1 "Con đã nhớ ra chưa?" để khởi vòng lặp horror. Q2 chỉ hợp với passenger có trigger câu hỏi.
- **Fix:** EP01 line 528 đổi "— Chưa tới lúc đâu cháu ạ." → "— Con đã nhớ ra chưa?"
- **Verify dialog count:** trước = Q1×2 + Q2×1 = 3 ✓ ; sau = Q1×3 + Q2×0 = 3 ✓ (`max_dialog_per_ep: 3` OK)
- **Effect:** cycle horror rõ hơn — cô gái = passenger tiếp theo phải nhớ ra (hook EP02). Match `fact_003` (mỗi điểm dừng 1 người nhớ ra + rời) + `fact_004` (1 rời → 1 mới giữ đủ 12).
- **Backup:** `output/ep_01/episode.md.bak.B_driver_dialog_30_06`
- **Regression rule (cần build):** R174 driver_dialogue_context_match — Q1 cho passenger mới xuất hiện / Q2 chỉ khi passenger HỎI bác tài trong 3 câu trước. Tool `tools/audit_driver_dialogue_context.py` (PENDING).
- **SHIPPED v108 17:15** Mr.Long approve. `output/ep_01/EP01_FULL_v108.mp3` 13MB / 20:15 min. Audio residual accepted same as v103 baseline (peak/click BETTER than v103).
- **R174 codified** bible/00 — driver_dialogue_context_match (Q1 cho passenger mới / Q2 chỉ khi passenger hỏi)
- **tools/audit_driver_dialogue_context.py** built — verify EP01 PASS 0 fail

---

## Round 23 (2026-06-30 22:30) — Process improvements catalog (R_SUPREME)

Per R_SUPREME.test_process_failure_principle: every user-found bug = process failure, propose process change.

### Process changes applied 30/6 (NOT just module fixes)

| Mr.Long catch | Module fix | **Process change applied** |
|---|---|---|
| L130+L132 'kính' lặp | episode.md vary | Add adjacent-line check coverage to phrase_repetition (TODO Round 24) |
| L480 'cái nhìn rất ngắn' | episode.md vary | R180b codify + bible/36 collocation entry + audit_vn_style.py |
| v108 voice 'ẹ ẹ' | (no module fix per Mr.Long lock) | R181b/c + R188-R191 entire Voice QA layer + bible/15 v2.0 |
| Outro 'Hãy nhớ rằng...' cụt | Option D edit | Outro completeness verification (TODO new test) |
| Nhạc nền thiếu 2:38 cuối | music_loop.py invocation | music duration check mandatory in audio_pre_ship_gate (TODO Round 24) |
| Spec out of sync episode | R192 sync tool | R192 codified + tools/sync_specs_from_episode.py + R194 SSOT roadmap (FROZEN_FOR_FUTURE Tier 2.5) |
| 134 hardcode breakdown question | hidden_audit refined | tools/hardcode_classifier.py NEW — answer broken-by-category (0 magic_unknown) |
| Tier 2.1 not yet validated | TIER_2_1_VALIDATION_REPORT.md | 4-gate lock workflow R_SUPREME enforced |

### B37 — Intro ep_01 tail/onset artifacts (Boss 1/7)

| Bug | Nguyên nhân | Fix | Test |
|---|---|---|---|
| Cụt chữ / hụt hơi cuối câu | threshold-trim cắt release mềm dưới ngưỡng | `qa_clean_tail` (voicing + continuity ≥60ms) thay aggressive_trim_tail; KHÔNG over-trim | R201, R202 |
| Tạp âm cuối ("Ký" buzz) | voicing giữ window tonal lẻ tẻ của crackle | continuity: chỉ tính voiced khi liên tục ≥60ms → gate crackle rời rạc | R202 |
| "Xẹt" onset đầu chunk | pop biên do fade ngắn sau bridge zero | `fade_head` cosine 80ms + QA onset-pop nhúng pipeline (maxDiff<0.13) | pipeline gate |
| "Tập một" rush | chunk 2-từ dày transient | merge + ellipsis "Tập một…" (nghỉ 700ms) | — |

Test process-fix (R_SUPREME): `tests/test_qa_clean_tail_r201.py` (6/6), `tests/test_intro_tail_50cases_r202.py` (50-case adversarial: hụt hơi / cụt chữ / tạp âm cuối, 50/50).
Ghi chú: R80.peak -1.0dB do master v65 alimiter 0.85 (Mr.Long lock) — R198 cap_peak PASS, R80 advisory.

### Workflow patterns codified

| Pattern | Rule | Tool |
|---|---|---|
| Build → Test → Validate → Freeze → Tag → (only then) Build next | R_SUPREME | (workflow) |
| Calibrate threshold ONLY from Golden Audio | R195 | (architecture) |
| Every user-found bug → process change required | R_SUPREME.test_process_failure_principle | (process) |
| Real-time progress log mandatory for long tasks | R176 | tools/cmd_progress_logger.py |
| Spec/episode sync mandatory before render | R192 | tools/sync_specs_from_episode.py |
| Voice Identity LOCKED + Emotion DYNAMIC | R181b | tools/voice_profile_manager.py |
| Speaker similarity QA per chunk | R181c | tools/extract_speaker_embedding.py |
| 5 voice artifact types tách riêng | R188-R191 + R190b | tools/qa_*.py 5 modules |
| Hidden code audit gate | (gate 3) | tools/hidden_audit.py + tools/hardcode_classifier.py |
| Historical bug replay gate | (gate 4) | tools/historical_bug_replay.py |

---

## B_publish_freshness (2026-07-09 09:42) — CMD TỔNG TRỢ LÝ, per Mr.Long authorization

- **Bug (process gap):** `tools/auditor.py::publish_auditor()` chỉ `.exists()` VERSION.md, KHÔNG kiểm nội dung freshness → version drift ~9 ngày LỌT Publish gate (VERSION.md header round 21 / last_update_ts 2026-06-30 trong khi pack release mới nhất 2026-07-05, git tới 09-07). Phát hiện qua vòng phản biện (firsthand + agent refute) khi đánh giá quy trình.
- **Root cause:** gate thiết kế existence-only; freshness/changelog nằm trong "ROADMAP — CHƯA gate" của `04_publish_auditor.md` (kỷ luật review, chưa cưỡng chế).
- **Fix:** thêm `version_freshness_advisory(version_path, claim_path)` — **ADVISORY non-gating** (không đụng `decide()` → R209/R213 nguyên vẹn). Metric bất biến `last_update_ts >= max(released_at)` (không ngưỡng tùy tiện). In dòng `Advisory: [OK/STALE]` trong report auditor.
- **Vì sao advisory chứ không hard-gate (R195):** VERSION.md đang stale (baseline chưa chuẩn) + `auditor.py` bị pytest R213 gọi transitively trong đường push → hard-fail sẽ chặn push CẢ live session. Advisory trước, LEAD promote hard-gate SAU khi owner reconcile VERSION.md content.
- **Regression:** `tests/test_version_freshness_advisory.py` 5-case tempfile (DEBT-005 lesson) — stale/fresh/equal/missing-skip/advisory-không-đổi-verdict. PASS. R209 5/5 PASS, R213 PASS, registry 0/0/0 PASS. Advisory chạy repo thật bắt đúng STALE.
- **Backup:** `tools/auditor.py.bak.freshness_advisory_09_07` (R8).
- **Process change (R_SUPREME test_process_failure):** gap này lọt vì gate chỉ kiểm tồn tại — đề xuất LEAD promote advisory→hard-gate publish_auditor sau khi VERSION.md content reconcile, để drift KHÔNG lọt lần nữa.
- **Còn lại (owner):** header `current_round`/`status` reconcile pack-era — KHÔNG bịa số, thuộc live session/LEAD.

---

## B_deep200_stale (2026-07-09 10:23) — CMD TỔNG TRỢ LÝ, per Mr.Long authorization

- **Vấn đề (misleading artifact, KHÔNG phải bug logic):** `runtime/deep_200_rounds_report.json` (28/6) hiển thị R61=93, R60=5, R58=2 "không đổi qua 5 vòng" → dễ đọc nhầm là "lỗi không hội tụ / khủng hoảng chất lượng" (chính CMD TỔNG TRỢ LÝ đã suýt kết luận sai như vậy).
- **Sự thật (firsthand):** (1) report là snapshot 28/6 trên 50 EP text CŨ đang REGEN qua G-pipeline → số liệu không phải hiện tại; audit R61 chạy fresh chỉ còn **6 HIGH**. (2) R61 khai `None` trong runner (chỉ đếm, không sửa) → delta=0 là **đúng thiết kế**, không phải vòng sửa hỏng. (3) 6 hit R61 hiện tại là câu mở bằng đại từ tự nhiên ("Anh thở phào...", "Cô ấy đợi anh") — cần tai người phán, không phải bug rõ ràng. (4) `auto_fix_short_start.py` nay tồn tại nhưng chỉ fix từ THỜI GIAN, không áp được đại từ.
- **Dọn:** mark `_STALE` vào report JSON + banner STALE/SUPERSEDED trong `tools/deep_200_rounds.py` + xóa `runtime/deep_200_rounds.log` (gitignored). JSON verify hợp lệ.
- **Backup:** `.bak.stale_mark_09_07` cho cả 2 file (R8).
- **Process change (R_SUPREME test_process_failure):** artifact QA cũ không mang nhãn stale → gây hiểu lầm phân tích. Đề xuất LEAD: (1) runtime QA report nên có field `generated_ts` + `corpus_ref` để tự lộ staleness; (2) tách audit R61 thành time-word (auto-fixable) vs pronoun-start (audio judgment) để số đếm không phồng giả. CHỜ duyệt.
- **Bài học CMD TỔNG TRỢ LÝ:** suýt kết luận "khủng hoảng chất lượng" từ số cũ mà chưa mở file — firsthand đọc mới thấy không có khủng hoảng. Lặp pattern jump-to-conclusion, phản biện/firsthand cứu.

## B_DEBT035_ep01_havy_death_canon (2026-07-16) — CMD_AUDIT (KIEM_DUYET), per Mr.Long "GO land + bless v8"

- **Bug:** `output/ep_01` (golden pilot) tả cái chết Hạ Vy = tai nạn TAXI ở New York (du học Hoa Kỳ) — MÂU THUẪN canon đã khóa bible/21 (Hạ Vy mất 12/4/2018, Hà Nội, tai nạn XE MÁY). Xác nhận bug thật (không misdirection): `output/archive_draft_v1_ep11_41/ep_35` cũng có version "đi Mỹ" đã bị bỏ khi lock arc; EP01 tự mâu thuẫn nội bộ (khung Hà Nội L98/L136 vs chết NY L336).
- **Fix:** reframe 3 file EP01 → "đêm mưa cuối tháng tư Hà Nội, cô ấy đi xe máy về, ngã tư xe tải đâm ngang, mất ngay tại chỗ"; giữ đồng hồ/7:10/"chưa kịp nói"/love_regret; GIỮ reveal budget EP73 (KP tách khỏi hiện trường, KHÔNG lộ KP lái). Golden bless v7→v8.
- **Khóa chặt lỗi (R215 / R_SUPREME test_process_failure):** enforcer mới `tools/canon_consistency_check.py` (proximity Hạ-Vy + chết + token nước-ngoài, chống false-positive hành khách khác) + 8 test mutation-proof `tests/test_canon_consistency_check.py`. **CMD_AUDIT tự tay verify:** EP01 gốc → FLAG 2 (New York+Kennedy); đã sửa → 0; 50 EP PASS 0; full suite 797 passed/0 fail; R86 broad 0; R41 2899/2899; dialogue_ratio Δ+0.0017.
- **Còn MỞ (không overclaim):** ghế 7-vs-3 EP01 + bible/21 M13 plan-vs-EP31-41 — xem `governance/TECH_DEBT.md` DEBT-035.
