# AUDIO QA Spec v1.0 — SVHMP EP01-90 ❄️ LOCKED 2026-06-26 round 17

**Mục tiêu:** detect 100% TẤT CẢ pattern bug listener catch được + block ship nếu HIGH issue.
**Pipeline:** spec.json → text validator (R3/R67/R72/R73/R74/R75/R76/R77/R78) → render section.wav → **AUDIO QA strict** → concat → ship.
**Strict mode:** block concat nếu bất kỳ HIGH issue.

---

## 20 CHECK MANDATORY (R80.1 → R80.20)

### LAYER 1 — TRANSIENT / DYNAMIC ANOMALY (Mr.Long catch "bụp nặng")

**R80.1 — BỤP TRANSIENT (silence→loud burst)**
- Pattern: 50ms window peak rises ≥40 dB from prev 50ms with prev < -50 dB AND cur > -3 dBFS
- Implementation: `scan_bup_transients()` with prev_peak < -50 dB, cur_peak > -3 dB, delta > 40 dB
- Severity: HIGH → block
- Root cause: BigVGAN vocoder reconstruct after internal silence + stop consonant onset (`/d/ /t/ /b/ /p/ /k/`)
- Auto-fix: scale chunk peak to -6 dB OR re-render with shorter sentence split

**R80.2 — PEAK CLIPPING > -3 dBFS**
- Max sample amplitude trên section > -3 dBFS (loudnorm push near clip)
- Severity: HIGH → block
- Auto-fix: apply soft limit -6 dBFS post-loudnorm

**R80.3 — DC OFFSET**
- Mean amplitude > 0.01 → BigVGAN artifact tạo DC bias
- Severity: HIGH → block
- Auto-fix: highpass 30Hz remove DC

**R80.4 — RMS UNEVEN (volume jump cross-chunk)**
- RMS per 1s window: max - min > 12 dB trong section → volume "đột nhiên to" "đột nhiên nhỏ"
- Severity: MED → warn
- Auto-fix: gain compensation per chunk

### LAYER 2 — TAIL VOWEL RESONANCE (R76 listener catch "phù" "ngân quá lâu")

**R80.5 — TAIL OPEN VOWEL SUSTAIN**
- Last 200ms peak > -15 dB → vowel `/aːj/ /ɨə/ /ə/` still ringing → phù/ngân tail
- Severity: MED → warn (HIGH cho section cuối)
- Cross-check text: last word match OPEN_VOWEL_TAIL dictionary
- Auto-fix: exponential fade 200ms aggressive

**R80.6 — TAIL CONSONANT POP**
- Last 50ms peak > -6 dB AND prev 100ms quiet → "BỤP" cuối section
- Severity: HIGH → block
- Auto-fix: trim more aggressive + fade 200ms

### LAYER 3 — INTERNAL SILENCE (R77 listener catch "ngắt 4s", "dính câu")

**R80.7 — INTERNAL SILENCE TOO LONG**
- Silence run > 1500ms within chunk (excluding first/last 300ms) → comma split internal pause excessive
- Severity: MED → warn
- Cross-check: spec sentence có em-dash `—` hoặc multi-comma split

**R80.8 — INTERNAL SILENCE TOO SHORT**
- Silence run < 80ms between 2 voiced segments → "dính câu" listener perceive run-on
- Severity: MED → warn
- Auto-fix: detect comma boundary + add 200ms pause

**R80.9 — UNINTENDED LONG GAP (R66 boundary check)**
- Gap silence between supposed-continuous voice > 2500ms → unintended dead air
- Cross-check: spec pause_after_ms expected
- Severity: HIGH → block

### LAYER 4 — VOICE CONSISTENCY (R78 the thé + drift)

**R80.10 — VOICE PITCH DRIFT**
- F0 (fundamental frequency) mean per 5s window: shift > 30Hz vs section mean → giọng thay đổi cao thấp
- Implementation: librosa pyin or praat-parselmouth pitch tracking
- Severity: MED → warn

**R80.11 — VOICE SPECTRAL CARRYOVER (the thé "/vowel-tail/+/stop-onset/")**
- Cross-chunk boundary detect: end-of-prev = vowel-resonance (-15dB sustained), start-of-next = stop consonant initial → BigVGAN harmonic carryover distortion
- Auto-detect: spectral centroid shift > 1000Hz across boundary
- Severity: HIGH → block
- Auto-fix: extend pause +200ms OR reword opener không stop consonant

**R80.12 — VOICE TIMBRE INCONSISTENCY**
- MFCC similarity between consecutive chunks < 0.75 → voice profile drift
- Implementation: librosa MFCC + cosine similarity
- Severity: MED → warn

### LAYER 5 — PRONUNCIATION ARTIFACTS (Mr.Long catch "lúc này muddled")

**R80.13 — PRONUNCIATION MUDDLED (low intelligibility window)**
- Detect: low energy + high entropy in spectral 1-4kHz band → listener perceive "không tròn tiếng"
- Cross-check: Whisper transcribe + diff with spec → mismatch ≥3 chars per chunk = FAIL
- Severity: HIGH → block

**R80.14 — SIBILANCE DISTORTION**
- 5-8kHz energy spike > -10 dB sustained > 100ms → "/s/ /ʃ/" hiss harsh
- Severity: MED → warn
- Auto-fix: de-esser

### LAYER 6 — TECHNICAL FORMAT INTEGRITY

**R80.15 — SAMPLE RATE CONSISTENCY**
- All sections MUST sr = 22050 Hz (pipeline LOCKED R20)
- Severity: HIGH → block

**R80.16 — BIT DEPTH CONSISTENCY**
- All sections MUST pcm_s16le
- Severity: HIGH → block

**R80.17 — CHANNEL CONSISTENCY**
- All sections MUST mono (channels=1)
- Severity: HIGH → block

**R80.18 — LOUDNESS LUFS COMPLIANCE**
- Per-section LUFS integrated = -18 ±1.0 LUFS (pipeline LOCKED loudnorm I=-18)
- Severity: HIGH if > 1.5 LUFS deviation → block
- Auto-fix: re-apply loudnorm

### LAYER 7 — BOUNDARY INTEGRITY (R66 adaptive 1600-1900ms)

**R80.19 — CROSS-SECTION BOUNDARY GAP**
- Compute actual silence at boundary between concat sections
- TARGET adaptive theo emotion arc (R66):
  - HOOK→SETUP: 1600ms ±100ms
  - SETUP→INCIDENT: 1700ms ±100ms
  - INCIDENT→REVEAL: 1800ms ±100ms
  - REVEAL→PAYOFF: 1800ms ±100ms
  - PAYOFF→CLIFF: 1900ms ±100ms
- Deviation > 200ms → MED warn
- Deviation > 400ms → HIGH block

**R80.20 — END-OF-EP TEMPO RELAX (R71)**
- Section CLIFFHANGER cuối: detect speech rate last 3 chunks vs avg section
- Speech rate (chars/sec or syllables/sec) PHẢI 0.85-0.92x avg (chậm 10-15% theo R71)
- Severity: MED → warn nếu không relax

---

## DETECTOR IMPLEMENTATION CHECKLIST

| Check | numpy | librosa | praat | whisper | Status |
|-------|-------|---------|-------|---------|--------|
| R80.1 bụp | ✅ | | | | DONE v1.0 |
| R80.2 peak | ✅ | | | | DONE v1.0 |
| R80.3 DC | ✅ | | | | TODO v1.1 |
| R80.4 RMS jump | ✅ | | | | TODO v1.1 |
| R80.5 tail vowel | ✅ | | | | DONE v1.0 |
| R80.6 tail pop | ✅ | | | | TODO v1.1 |
| R80.7 internal long | ✅ | | | | DONE v1.0 |
| R80.8 internal short | ✅ | | | | TODO v1.1 |
| R80.9 unintended gap | ✅ | | | | TODO v1.1 |
| R80.10 F0 drift | | ✅ | ✅ | | TODO v1.2 |
| R80.11 spectral carryover | | ✅ | | | TODO v1.2 |
| R80.12 MFCC timbre | | ✅ | | | TODO v1.2 |
| R80.13 muddled Whisper diff | | | | ✅ | TODO v1.2 |
| R80.14 sibilance | | ✅ | | | TODO v1.2 |
| R80.15-17 format | ✅ | | | | TODO v1.1 |
| R80.18 LUFS | | | | | TODO v1.1 (pyloudnorm) |
| R80.19 boundary | ✅ | | | | TODO v1.1 |
| R80.20 EP tempo | | ✅ | | | TODO v1.2 |

---

## THRESHOLD TUNING ROADMAP

Round 17 v1.0 thresholds based on EP01 R16/R17 calibration:
- bụp prev_db < -50, cur_db > -3, delta > 40
- peak max -3 dBFS
- tail vowel last 200ms > -15 dB
- internal silence > 1500ms

Round 18 tune based on:
- False positive rate per check (target < 5%)
- False negative rate per Mr.Long QA pass (target < 1%)
- Per-emotion calibration (slow narrative vs urgent reveal)

---

## RUN COMMAND (mandatory pre-concat)

```bash
python tools/svhmp_audio_qa.py \
    ep01_s1_R17.wav ep01_s2_R17.wav ep01_s3_R17.wav \
    ep01_s4_R18.wav ep01_s5_R17.wav ep01_s6_R17.wav \
    --strict --json-out audio_qa_report.json
# Exit 1 if HIGH issues → block concat
```

---

## INTEGRATION VỚI PIPELINE

```
spec_ep0X.json
    ↓ [R66-R79 text validator]
    ↓ PASS 0/0
render section_n.wav  ← svhmp_v13_render.py
    ↓ [R80.1-R80.20 audio QA strict]
    ↓ PASS 0 HIGH
boundary measure + concat
    ↓ [R80.19 boundary integrity check]
    ↓ PASS
EP_FULL.wav ship → Mr.Long QA approve
```

**KHÔNG ship cho đến khi:**
- text validator PASS 0 issue
- audio QA strict PASS 0 HIGH issue
- boundary integrity PASS adaptive target ±100ms

---

## STRICT GATE WORKFLOW (R79 ENFORCE HARD)

**KHÔNG ship cho đến khi cả 3 layer PASS 0 HIGH/0 violation:**

```
LAYER 1: TEXT VALIDATOR (R3/R67/R72/R73/R74/R74.2/R75/R76/R77/R78)
  python tools/vnsl_validator.py spec_ep0X_section_*.json
  → expect: TOTAL: 0 issues
  → FAIL: reword spec, re-render, re-validate. NEVER bypass.

LAYER 2: AUDIO QA (R80.1-R80.20)
  python tools/svhmp_audio_qa.py ep01_s*_R*.wav --strict
  → expect: HIGH=0
  → FAIL: auto-fix peak cap / re-render chunk / re-render section. NEVER bypass.

LAYER 3: BOUNDARY INTEGRITY
  measure_edges.py + concat plan
  → expect: deviation ≤200ms per pair
  → FAIL: re-measure + re-compute concat silence per emotion arc.

CONCAT EP_FULL.wav → SHIP
```

**HARD RULE: nếu Mr.Long catch lỗi audio sau ship = QA workflow FAILED. Add detector to v1.1, never repeat.**

## RUT KINH NGHIEM session 26/6 round 17

Em ship EP01 R16 với 0 audio QA → Mr.Long catch 6 lỗi audio (bụp/phù/the thé/lúc này/đầy thấu hiểu/em-dash). 5/6 catch được nếu chạy tool v1.0 + 1/6 cần v1.2 Whisper diff.

**Bài học:** TEXT validator KHÔNG đủ. AUDIO LAYER mandatory. Em LLM text-only KHÔNG nghe được — phải tool replace ear.
