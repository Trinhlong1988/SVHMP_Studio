# ONBOARDING — Dự án SVHMP / Hắc Dạ Ký

> **Mục đích tài liệu**: Một CMD Claude MỚI đọc file này + `CLAUDE.md` + `bible/00_constitution.yaml` là hiểu hoàn toàn dự án, mọi thông số cài đặt, mọi quy tắc, và có thể tiếp tục làm việc mà không cần Mr.Long giải thích lại.

Cập nhật: 2026-07-01 03:50 (round 20.1, session 1/7 spec rebuild v2 + AB tests)

---

## 1. TỔNG QUAN DỰ ÁN

### 1.1 Danh tính

- **Channel YouTube**: **Hắc Dạ Ký** (`@hacdaky`) — LOCK 25/6, revert 29/6 sau ngắn test "Hắc Vỹ Dạ"
- **Tagline**: "chuyện kể từ cõi vô hình"
- **OUTTRO closing**: "Hắc Dạ Ký xin hẹn gặp lại quý vị trong những câu chuyện của cõi vô hình."
- **Series 1**: "Chuyến xe cuối cùng về đâu" — tagline riêng "Ai cũng có một chuyến xe chưa nói lời tạm biệt"
- **Kế hoạch**: 90 EPs, TTS Vietnamese narrative horror, style Nguyễn Ngọc Ngạn

### 1.2 Narrator — KHÔNG có tên "Khánh An"

- Narrator = **anonymous storyteller Hắc Dạ Ký**
- "Khánh An" là LEGACY anchor const trong `tools/svhmp_v13_render.py` từ phase v13a → v13b đã set `USE_ANCHOR=False` → anchor **DISABLED** runtime
- 1/7 (session này) xoá dead ANCHOR const → docstring + comment về "Khánh An" cleanup
- Voice sample file `NNG_narration_sample_19062026.wav` — chỉ là **asset filename**, KHÔNG phải narrator name

### 1.3 Path project

```
D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\
```

### 1.4 Trạng thái hiện tại

- Tier 1 QA Engine: FROZEN v1.0.0-rc1 (30/6)
- Tier 2.1 Audio/Mix Gate: ENGINEERING PASS 30/6, chưa PRODUCTION VALIDATED
- EP01 v200c: last Mr.Long-approved audio với 6 sections rebuilt spec v1 (buggy)
- EP01 v201: spec v2 rebuilt (session 1/7) — 193 chunks, 100% text-match episode.md, chưa render
- 5 A/B tests done 1/7: T4 defend rp=10.0 (rp=2/1.2 gây LOOP 3×)

---

## 2. R_SUPREME GOVERNANCE — 10 RULES TỐI THƯỢNG TUYỆT ĐỐI

**Mr.Long = ONLY AUTHORITY. Claude = Engineering Executor (KHÔNG autonomous).**

### R1 — NO AUTONOMOUS ACTION
CẤM: tạo script production, modify production data, overwrite spec, batch-sync, auto-fix content, extend/create rules, declare READY, declare PASS beyond QA coverage. Nếu uncertain → STOP.

### R2 — PERMISSION FIRST (4 câu hỏi)
Trước MỌI action:
- Q1: Explicit approval? NO → STOP
- Q2: Modifying production data? YES → Approval REQUIRED
- Q3: Changing architecture? YES → Approval REQUIRED
- Q4: Introducing/extending rule? YES → Production evidence REQUIRED first

### R3 — PRODUCTION VALIDATION MODE
Allowed: render / run QA / generate reports / diff / catalog bugs / wait for review
Forbidden: redesign / extend QA / calibrate thresholds / optimize pipeline / speculative

### R4 — BUG CLASS EXTENSION PRINCIPLE
- Ưu tiên EXTEND rule cùng group (Language/TTS/Voice/Mix/Story) hơn CREATE mới
- Goal: Fewer Rules + Broader Coverage
- Phase boundary lock: KHÔNG implement extension trước Production Validation complete

### R5 — PROCESS FAILURE PRINCIPLE
User-found bug = **thất bại quy trình kiểm thử**, không chỉ module.
Phải answer 5 câu hỏi TRƯỚC khi propose fix:
1. Tại sao Engineering QA miss?
2. QA layer nào failed?
3. Bug Class nào?
4. Existing rule có thể extend?
5. Process change nào chống recurrence?

### R6 — PASS DECLARATION QUALIFIER
NEVER unqualified PASS/READY/COMPLETE/PRODUCTION READY.
Correct: "PASS within current QA coverage" / "Engineering PASS" / "Manual review REQUIRED" / "Production NOT VERIFIED"

### R7 — WRITE PROTECTION WORKFLOW
**Read → Diff → Proposal → Mr.Long Approval → Backup → Patch → Regression → Production**
Skip step = violation.

### R8 — BASELINE PROTECTION
Trước production modify: verify clean → lock → backup → checksum → diff → apply patch AFTER approval only.

### R9 — EVIDENCE FIRST
KHÔNG implement dựa trên giả định. Order: Evidence → Analysis → Proposal → Approval → Implementation → Regression → Production.

### R10 — FINAL SAFETY RULE
**Uncertainty → STOP not ACT. No exception.**

---

## 3. HIẾN PHÁP RULES R60-R198 (highlights)

Tất cả rules chi tiết ở `bible/00_constitution.yaml`. Highlight rules critical:

| ID | Tên | Ý nghĩa |
|---|---|---|
| R86 | EOL diacritic broad | KHÔNG chunk kết thúc bằng NGA/HOI/NANG tone (BigVGAN cụt) |
| R94b | Silence bridge | Bridge 1500ms mặc định giữa sections |
| R96 | BigVGAN onset mitigation | Slow onset ramp INHERENT → pre-roll + crossfade + conservative trim |
| R108 | Channel name lock | "Hắc Dạ Ký" — CẤM "Hắc Vỹ Dạ" |
| R170-R173 | Zero-hallucination + Audit + Role separation | 3 roles: WRITER / TESTER / AUDITOR |
| R175b | emo_vector sum ≤ 1.0 | Constraint IndexTTS2 |
| R178b | Time marker pause opening | Pause 800ms sau "Đêm hôm ấy…" / "Rồi một hôm" |
| R180b | Verb-noun collocation | Chống awkward VN grammar |
| R181b | Voice Identity LOCKED + Emotion DYNAMIC | 2 field types |
| R181c | Speaker embedding QA | ECAPA-TDNN Phase 3 FROZEN |
| R188 | Boundary artifact | TOP priority "ù/xì/ẹ" detection |
| R189 | Breath artifact | sibilance/aspiration burst |
| R190 | Prosody collapse | F0 contour drop/rung lẹm — DETECT_ONLY per R195 |
| R190b | Onset artifact | Chunk start F0 jump |
| R191 | Dialogue identity | Speaker embedding cosine sim |
| R192 | Spec-Episode sync | `sync_specs_from_episode.py` (đã replaced by rebuild v2) |
| R195 | Golden Audio threshold | CẤM calibrate threshold từ data chưa đạt chuẩn |
| R196 | Production Reality | Engineering PASS ≠ Production PASS |
| R197 | FULL_TEXT_GATE MUST | Mọi text modification → FULL_TEXT_GATE trước render |
| R198 | cap_peak post-render | Peak ≤ -1.0 dB idempotent post-loudnorm |

---

## 4. TTS PIPELINE — CÀI ĐẶT THÔNG SỐ CHI TIẾT

### 4.1 Environment

```bash
# Python venv (index-tts .venv)
PYTHON: C:\Users\Administrator\index-tts\.venv\Scripts\python.exe

# ENV variables (REQUIRED)
PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Working directory (REQUIRED cho IndexTTS2 load config)
CWD: C:\Users\Administrator\index-tts
```

### 4.2 Model + weights

| Component | Source | Path |
|---|---|---|
| Code engine | IndexTTS GỐC (github.com/index-tts/index-tts) | `C:\Users\Administrator\index-tts\` |
| Weights VN | **dinhthuan/index-tts-2-vietnamese** HuggingFace | `C:\Users\Administrator\index-tts\checkpoints-vi\` |
| Vocoder | BigVGAN-vi (finetune Vietnamese) | inside checkpoints-vi |
| Emotion encoder | Qwen 0.6B emo4-merge | `checkpoints-vi\qwen0.6bemo4-merge\` |

Class: `IndexTTS2(model_dir=..., use_fp16=True)`

### 4.3 Fixed TTS params (ALL chunks)

```python
GEN_KWARGS = {
    'top_p': 0.5,
    'top_k': 5,
    'temperature': 0.3,
    'num_beams': 5,
    'repetition_penalty': 10.0,   # DEFEND 1/7 A/B test T4 — rp<10 gây silent overgenerate 20s trail
}

FIXED = {
    'emo_alpha': 0.65,             # blend ratio target_emo vs sample_emo
    'interval_silence': 200,       # ms silence giữa internal segments
    'max_text_tokens_per_segment': 400,   # VN ~1.4 token/char → 400 covers ~285 VN chars
    'verbose': False,
    'use_fp16': True,
}
```

### 4.4 Seed strategy (post-1/7 change)

```python
# OLD (pre-1/7): set_all_seeds(42) — 193 chunks same → robotic onset
# NEW (1/7): set_all_seeds(42 + i) where i = chunk_index
# Rationale: deterministic variation chống onset đồng đều
# Location: tools/svhmp_v13_render.py line 259
```

### 4.5 Per-chunk payload (variable)

Spec JSON structure:
```json
{
  "sentences": [
    {
      "text": "…",
      "emo_vector": [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm],
      "pause_after_ms": 1500,
      "is_dialogue": false,
      "tempo_factor": 0.97
    }
  ],
  "sample_prompt": "C:\\Users\\Administrator\\Desktop\\NNG_narration_sample_19062026.wav"
}
```

- **text**: Passed as `text=` to `tts.infer()` — NO anchor prepend (USE_ANCHOR=False permanent)
- **emo_vector**: 8-dim, sum ≤ 1.0 (R175b), passed as `emo_vector=`
- **pause_after_ms**: NOT passed to TTS — applied post concat (silence room tone bridge)
- **is_dialogue**: metadata only — dùng cho voice QA (R191)
- **tempo_factor**: post-TTS ffmpeg `atempo=X`. 1.0 = bypass. Default per section profile (below)
- **sample_prompt**: passed as `spk_audio_prompt=` — voice reference WAV (13.52s)

### 4.6 Section tempo profile (1/7 apply)

| Section | Narration | Dialogue |
|---|---|---|
| HOOK | 0.97 | 0.97 |
| SETUP | 1.00 | 1.00 |
| INCIDENT | 1.00 | 1.03 |
| REVEAL | 0.97 | 0.97 |
| PAYOFF | 0.95 | 0.95 |
| CLIFFHANGER | 0.92 | 0.92 |

### 4.7 Emo vector per section (default nếu chunk chưa lock)

| Section | Distinct pattern |
|---|---|
| HOOK (Tò Mò) | surprised 0.40 + calm 0.30 + melancholic 0.15 + afraid 0.10 + sad 0.05 = 1.00 |
| SETUP (Bất An) | afraid 0.30 + calm 0.30 + melancholic 0.20 + sad 0.10 + surprised 0.10 |
| INCIDENT (Đồng Cảm) | sad 0.25 + melancholic 0.30 + calm 0.25 + afraid 0.10 + surprised 0.10 |
| REVEAL (Nghẹn) | melancholic 0.40 + sad 0.25 + calm 0.20 + afraid 0.10 + surprised 0.05 |
| PAYOFF (Dư Âm) | melancholic 0.35 + calm 0.30 + sad 0.20 + afraid 0.10 + surprised 0.05 |
| CLIFFHANGER (Cycle Horror) | melancholic 0.30 + afraid 0.25 + calm 0.20 + sad 0.15 + surprised 0.10 |

### 4.8 Post-processing per chunk

```python
# svhmp_v13_render.py flow post tts.infer():
# 1. Trim leading silence -36 dB (aggressive_trim_head 200ms search @ -50dB back-off)
# 2. Trim trailing silence -20 dB baseline (aggressive_trim_tail 600ms search @ -30dB)
# 3. DC offset removal (data - mean)
# 4. RMS normalize -23 dBFS
# 5. Soft limit peak 0.89 (-1.0 dBFS)
# 6. fade_head 15ms (click prevention)
# 7. Read pause_after_ms from spec → variable room-tone bridge
```

### 4.9 Concat + master mix

```python
# 1. Concat 6 sections with R94b 1500ms silence bridge
# 2. music_loop covering voice duration
# 3. Mix chain: highpass 30Hz + voice 0.85 + music 0.225 + amix + loudnorm I=-16 TP=-1.5
# 4. R198 cap_peak (tools/cap_peak.py) — hardlock peak ≤ -1.0 dB
# 5. Output: EP01_FULL_v{N}.mp3
```

---

## 5. EP01 STRUCTURE (session 1/7 state)

### 5.1 Section breakdown

| Section | Name | Chunks | Pause range | Dialogue | Tempo |
|---|---|---|---|---|---|
| 1 | HOOK (Tò Mò) | 13 | 1500ms | 0 | 0.97 |
| 2 | SETUP (Bất An) | 36 | 1200–1500ms | 0 | 1.00 |
| 3 | INCIDENT (Đồng Cảm) | 44 | 300–1800ms | 20 | 1.00 / dlg 1.03 |
| 4 | REVEAL (Nghẹn) | 51 | 300–1500ms | 18 | 0.97 |
| 5 | PAYOFF (Dư Âm) | 30 | 1500–2000ms | 2 | 0.95 |
| 6 | CLIFFHANGER (Cycle Horror) | 19 | 500–2800ms | 1 | 0.92 |
| **TOTAL** | | **193** | | 41 | |

Post-merge 9 short narration chunks (1/7): 202 → 193 chunks.

### 5.2 SHA256 (post-fix 1/7)

```
episode.md              ebb4eeb8949655c9…
spec_hook.json          4c902d6efa135e2a…  (13 chunks) — hook tempo not applied yet if fresh
spec_setup.json         (post-merge + tempo applied)
spec_incident.json      (post-merge + tempo)
spec_reveal.json        (post-merge + tempo)
spec_payoff.json        (post-merge + tempo)
spec_cliffhanger.json   (tempo 0.92)
```

### 5.3 Voice sample reference

```
C:\Users\Administrator\Desktop\NNG_narration_sample_19062026.wav
Size: 1,081,644 bytes (~13.52s @ 22050 Hz mono)
```

---

## 6. FILES & TOOLS

### 6.1 Bible files (immutable — chỉ AUDITOR modify)

```
bible/00_constitution.yaml       — R_SUPREME + R60-R198 hiến pháp
bible/03                          — Recurring characters (CHAR_DRIVER + CHAR_KHAI_PHONG only;
                                     id đổi từ CHAR_NAM 12/7, xem bible/03 v1.1 changelog)
bible/11                          — Regret catalog (27 sub-archetypes)
bible/12                          — Object library (71+ OBJ_)
bible/13                          — Setting library (21+ setting_)
bible/15_voice_bible.yaml v2.0    — Voice Identity LOCKED + Emotion DYNAMIC
bible/18                          — Driver reveal budget (EP73 + EP90 reserved)
bible/22                          — Anti-slop VN (32 rules)
bible/23                          — Passenger naming (5 rules)
bible/30_error_handbook.yaml
bible/35_text_fix_registry.yaml
bible/36_vn_style_db.yaml v0.1    — FROZEN Tier 2.2
```

### 6.2 Tools key

```
tools/svhmp_v13_render.py         — TTS pipeline LOCKED v1.3 (1/7 anchor removed, seed=42+i)
tools/cap_peak.py                 — R198 hardlock peak ≤ -1.0 dB
tools/qa_eol_diacritic.py         — R86 broad NGA+NANG+HOI EOL check
tools/svhmp_preflight_qa.py       — R197 FULL_TEXT_GATE chain
tools/voice_profile_manager.py    — R181b LOCKED + DYNAMIC field enforcement
tools/qa_boundary_artifact.py     — R188 TOP priority
tools/qa_breath_artifact.py       — R189
tools/qa_prosody_collapse.py      — R190 DETECT_ONLY
tools/qa_onset_artifact.py        — R190b
tools/qa_dialogue_identity.py     — R191
tools/extract_speaker_embedding.py — R181c (ECAPA Phase 3 FROZEN)
tools/hidden_audit.py             — Anti-orphan rule counter
tools/hardcode_classifier.py      — 144 magic numbers classified
tools/cmd_progress_logger.py      — R176 realtime CMD log
tools/audit_driver_dialogue_context.py — R174
tools/auto_watch.py               — daemon poll episode.md
tools/vnqa/pipeline.py            — H1-H9 checks
```

### 6.3 Tests

```
tests/test_voice_profile_manager.py       — 15 tests / 10-round = 150/150 PASS
tests/test_voice_qa_tools.py              — 23 tests / 10-round = 230/230 PASS
tests/test_full_text_gate_r86_broad.py    — 5/5 PASS
tests/regression/                          — 800 runs 8/8 PASS KPI (Tier 1 frozen)
```

### 6.4 Runtime state

```
runtime/passenger_roster_100.yaml  — 100 passenger LOCK
runtime/realtime_logs/              — CMD parallel logs
runtime/audit_*.json                — Historical audit reports
data/vnsl_lexicon.json              — Vietnamese Standard Lexicon
data/vnqa_approved_replacements.yaml — R001-R00N auto-fix
```

### 6.5 Output

```
output/ep_01/
├── episode.md                       — SSOT authoritative text (628 lines, 21898 chars)
├── episode_golden_text.md           — Golden reference
├── episode_tts_ready.md             — After TTS adapter (em-dash + pauses inserted)
└── sections/
    ├── spec_hook.json               — 13 chunks
    ├── spec_setup.json              — 36 chunks
    ├── spec_incident.json           — 44 chunks
    ├── spec_reveal.json             — 51 chunks
    ├── spec_payoff.json             — 30 chunks
    ├── spec_cliffhanger.json        — 19 chunks
    └── *.wav                        — rendered audio (excluded from git)
```

---

## 7. WORKFLOW END-TO-END

### 7.1 Render 1 section

```bash
cd C:\Users\Administrator\index-tts
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# Command production render (svhmp_v13_render.py takes spec + section arg)
.venv/Scripts/python.exe \
  "D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/tools/svhmp_v13_render.py" \
  --spec "D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/output/ep_01/sections/spec_hook.json" \
  --output "D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/output/ep_01/sections/hook.wav"
```

### 7.2 Preflight FULL_TEXT_GATE (R197)

```bash
python tools/svhmp_preflight_qa.py output/ep_01/episode.md
# Chains: qa_eol_diacritic + audit_tilde_eol + hardcode_classifier + hidden_audit
```

### 7.3 Post-render audit

```bash
python tools/qa_boundary_artifact.py  <section>.wav   # R188
python tools/qa_breath_artifact.py    <section>.wav   # R189
python tools/qa_prosody_collapse.py   <section>.wav   # R190 DETECT_ONLY
python tools/qa_onset_artifact.py     <section>.wav   # R190b
python tools/qa_dialogue_identity.py  <section>.wav <spec>.json  # R191
python tools/cap_peak.py --input <section>.wav        # R198
```

### 7.4 Mix master

```bash
# Concat 6 sections + music_loop + loudnorm + cap_peak
# TODO: expose as tools/build_master_mix.py (currently inline in v13_render)
```

### 7.5 Audio pre-ship gate

```bash
python tools/audio_pre_ship_gate.py EP01_FULL_v{N}.mp3
# Checks: peak/LUFS/clip/duration/R94b bridges/artifact catalog
```

---

## 8. SESSION START PROTOCOL (mọi CMD Claude mới)

1. Đọc workspace `C:\Users\Administrator\CLAUDE.md` — TỐI THƯỢNG lines
2. Đọc project `CLAUDE.md` này — TỐI THƯỢNG R196/R197/R_SUPREME
3. Đọc file `ONBOARDING.md` này
4. Đọc `VERSION.md` project — so last_known_version, mismatch → re-read artifacts
5. Đọc `BUGS_FIXED.md` (B1-B36+) trước touch code
6. Đọc memory `feedback_svhmp_*` + `project_svhmp_*` relevant
7. EP02+ render: Đọc `feedback_svhmp_script_8_hard_rules.md` (32 rules) + `project_svhmp_master_production_v1.md`
8. **KHÔNG render nếu chưa ≥95 PASS 100-check (Rule 31)**
9. **KHÔNG iterate reactive — workflow LOCKED proactive**

---

## 9. BACKUP CHAIN (session 1/7)

```
Spec files:
  L1 baseline:       .bak.sync_1782826082         (30/6 20:28)
  L2 pre-corrupt:    .bak.sync_1782847715         (1/7 02:28)
  L3 pre-rebuild-v1: .bak.before_rebuild_1782849460 (1/7 02:57)
  L4 pre-split-v2:   .bak.v1_before_split_pause_1782850500 (1/7 03:15)
  L5 pre-merge:      .bak.before_merge_short_1782852000    (1/7 03:20)
  L6 pre-tempo:      .bak.before_tempo_1782852500          (1/7 03:22)
  L7 current:        spec_*.json                           (1/7 latest)

Render script:
  svhmp_v13_render.py.bak.before_anchor_delete_1782851753  (1/7 anchor delete)
```

Rule: BẮT BUỘC backup + SHA256 fingerprint + diff BEFORE apply patch (R7 + R8).

---

## 10. BUGS + FIXES SESSION 1/7 (this session)

### Bug B37 — Spec rebuild v1 MẤT 17 inline pauses
- Root cause: `rebuild_specs_apply.py` line 83 `re.sub(r'\[pause:\d+ms\]', '', s)` STRIP thay vì SPLIT
- Fix: `rebuild_specs_v2_split_pause.py` — SPLIT chunk tại pause + preserve pause_after_ms
- Regression: text-match 202/202 = 100% (was 187/193 = 96.9%)
- Process fix per R5: em phải verify pre-report thay vì báo "100%" trước audit

### Bug B38 — 9 short narration chunks <25 chars (BigVGAN cụt onset risk)
- Detection: `audit_short_chunks.py` 1/7 05:00 sau khi Mr.Long chỉ ra "LỖI NẶNG NHẤT"
- Fix: `merge_short_chunks.py` — merge vào chunk liền kề (cùng is_dialogue)
- Result: 202 → 193 chunks, 0 violation remaining
- 10 exception giữ nguyên: dialogue cực ngắn + cliffhanger

### Bug B39 — Legacy ANCHOR "Khánh An" dead code confused narrator identity
- Detection: Mr.Long 1/7 correct "khánh an nào nữa? hắc dạ ký mà"
- Fix: delete `ANCHOR = "Khánh An kể chậm rãi rằng,"` const + replace usage
- svhmp_v13_render.py line 31 + 256 cleanup
- Memory: `feedback_no_khanh_an_narrator_hdk_1_7.md`

### Improvement Item 6 — seed=42 fixed → seed=42+chunk_index
- Rationale: 193 chunks same seed → robotic onset đồng đều
- Fix: `set_all_seeds(42 + i)` line 259
- A/B test T5 confirm: peak diff 0.86 dB, RMS diff 0.63 dB

### Improvement Item 7 — tempo profile per section
- Rationale: 193 chunks đều tempo=1.0 → mechanical pacing
- Fix: apply profile (HOOK 0.97 / SETUP 1.0 / INCIDENT 1.0-1.03 / REVEAL 0.97 / PAYOFF 0.95 / CLIFFHANGER 0.92)

### Defense Item 5 — repetition_penalty=10.0 (NOT change)
- A/B test T4 confirm rp=2.0 và rp=1.2 gây **20s silent overgenerate trailing** (KHÔNG phải LOOP nội dung)
- Voice content ~10s giống rp=10 nhưng model không trigger EOS đủ sớm
- Production pipeline có aggressive_trim_tail sẽ trim OK, nhưng giữ rp=10.0 tránh risk

---

## 11. NAMING CONVENTIONS

- Channel: **Hắc Dạ Ký** ✓ | ❌ Hắc Vỹ Dạ | ❌ HDK trong text/UI (viết tắt OK trong code)
- Narrator: **anonymous storyteller Hắc Dạ Ký** ✓ | ❌ Khánh An | ❌ NNG
- Voice sample: gọi "voice sample ref" | ❌ "Khánh An base"
- Series: "Chuyến xe cuối cùng về đâu" (Series 1)
- Chunks: chỉ số 1-N per section, format `ch{N:02d}` (ch01, ch12)
- Tone: "storyteller" | "narrator"

---

## 12. FORBIDDEN LIST (từ 20 projects workspace)

- 15 passenger names FORBIDDEN Mr.Long: Nam, Tài, Quang, Hưng, Long, Trang, Linh, Nhung, Lương, Khánh, An, Tùng, Tiến, Tú, Mai
- CẤM "Hắc Vỹ Dạ" trong text/asset/memory
- CẤM tự tạo character mới ngoài bible/03 (CHAR_DRIVER + CHAR_KHAI_PHONG — id đổi từ CHAR_NAM 12/7)
- CẤM skip QA gate STAGE 1 (R91 hardlock — svhmp_v13_render.py main() abort sys.exit 2 nếu R86 fail)
- CẤM reactive iterate — workflow LOCKED proactive
- CẤM Ollama keep_alive=0 assumption (memory feedback_ollama_keepalive_vram_truth)
- CẤM ffmpeg silenceremove aggressive >-35dB (memory feedback_svhmp_v24_silenceremove_disaster)

---

## 13. RESOURCES

- CLAUDE.md workspace: `C:\Users\Administrator\CLAUDE.md`
- Memory index: `C:\Users\Administrator\.claude\projects\C--Users-Administrator\memory\MEMORY.md`
- Bible constitution: `bible/00_constitution.yaml`
- Bug catalog: `BUGS_FIXED.md`
- Version tracker: `VERSION.md`
- Session 1/7 evidence: `C:\Users\Administrator\Desktop\EP01_v201_FIX_EVIDENCE.md`
- A/B tests: `C:\Users\Administrator\Desktop\EP01_AB_TESTS\`
- Chunk review: `C:\Users\Administrator\Desktop\EP01_v201_chunks_for_review.docx`
