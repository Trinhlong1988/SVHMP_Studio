# R199 Tail Pathology — Comprehensive Audit + A/B Test Report

**Date**: 2026-07-01 09:00
**Source**: Mr.Long docx analysis + Claude comprehensive audit

## 1. Root Cause Analysis (Mr.Long)

3 case gây tiếng **"ù ù xèo xẹo lục bục khi kết câu"**:

| Case | Symptom | Root cause |
|---|---|---|
| #1 | Đuôi rác burst peak -21 dB @ tail | Model burst nhỏ sau silence gap ≥300ms — không phải giọng thật |
| #2 | Runaway generation → đuôi 26s | Model sinh lố tới max_mel_tokens |
| #3 | Auto-trim lỗ hổng | `search_ms=600` quá hẹp + logic bỏ qua khi cục cuối < 0.25s |

## 2. Evidence — Comprehensive audit

### 2.1 6861 raw chunks scanned (281 tmpdirs)

| Metric | Value |
|---|---|
| Total raw chunks | 6861 |
| Total tmpdirs | 281 |
| Case #1 hits (current pipeline rp=10) | **0** |
| Case #2 hits (current pipeline rp=10) | **0** |

→ Current pipeline (rp=10.0) **CLEAN**.

### 2.2 Legacy hits (case #1 confirmed pre-rp=10 era)

| File | Position | Peak dB | Gap ms |
|---|---|---|---|
| `SVHMP_v10_workdir/ep01_full_v6.wav` | 795.53s | -15.1 | 320 |
| `SVHMP_v10_workdir/ep01_s6_v6.wav` | 50.88s | -15.1 | 320 |
| `SVHMP_v10_workdir/intro_v13_test.wav` | 69.59s | -19.0 | 1150 |
| `SVHMP_v10_workdir/mini_R25_fixes.wav` | 40.1s | -17.0 | 1070 |
| `SVHMP_v10_workdir/mini_R25_fixes.wav.raw.wav` | 40.1s | -16.2 | 1060 |
| `SVHMP_v10_workdir/new_s6_ch13.wav` | 12.07s | -17.0 | 1070 |

### 2.3 Case #2 confirmed via forced rp<10 (AB Test T4)

| File | Total | Voice end | Trail silence |
|---|---|---|---|
| `Test4/A_rp10.0.wav` | 11.0s | 10.0s | 1.0s ✓ |
| `Test4/B_rp2.0.wav` | 30.0s | 9.9s | **20.0s** 🚨 |
| `Test4/C_rp1.2.wav` | 30.0s | 9.8s | **20.1s** 🚨 |
| `SVHMP_v10_workdir/intro_v11_test.wav` | 122.7s | 92.5s | **30.2s** 🚨 |

### 2.4 Case #3 confirmed via code review

`tools/svhmp_v13_render.py:118` current logic:
```python
def aggressive_trim_tail(data, sr, search_ms=600, silence_thr_db=-30):
    ...
    last_voice_end = n              # ← starts at END
    for i in range(n - win_n, max(0, n - search_n), -win_n):
        if win_rms > thr:
            last_voice_end = i + win_n
            break
    # If no voice found in 600ms → last_voice_end = n → KEEP ENTIRE DATA
```

**Structural hole**: nếu tail >600ms silence, scan không tìm thấy voice → giữ nguyên → runaway PRESERVED.

## 3. Fix Tầng 1 — R199 mandate

### 3.1 New tool `tools/ab_test_tail_trim_v1_vs_v2.py`

Signature:
```python
def aggressive_trim_tail_v2(
    data, sr,
    silence_thr_db=-40,   # was -30 in v1 (broader detection)
    gap_ms=300,           # silence ≥300ms → tail boundary
    main_run_ms=100,      # 100ms contiguous voice = main region
    grace_ms=80,          # keep +80ms after last main voice (was 50 in v1)
    fade_ms=10,           # linear fade inside voice content
    win_ms=10,            # 10ms window precision
)
```

### 3.2 Regression A/B v1 vs v2 (8 chunks)

| Chunk | Orig | v1 out | v2 out | Δms | Verdict |
|---|---|---|---|---|---|
| A_rp10.0.wav | 11.0s | 11.0s | 10.0s | +957 | V2 cắt tail residue |
| **B_rp2.0.wav** | 30.0s | 30.0s | 10.0s | **+19986** | **RUNAWAY FIXED** ✓ |
| **C_rp1.2.wav** | 30.0s | 30.0s | 9.9s | **+20076** | **RUNAWAY FIXED** ✓ |
| A_full_single.wav | 11.0s | 11.0s | 10.0s | +957 | V2 cắt tail residue |
| A_seed42_fixed.wav | 11.0s | 11.0s | 10.0s | +957 | V2 cắt tail residue |
| B_seed42_plus_index.wav | 11.0s | 11.0s | 10.0s | +957 | V2 cắt tail residue |
| A_current_surprised40.wav | 11.0s | 11.0s | 10.0s | +957 | V2 cắt tail residue |
| B_calm_higher60.wav | 9.9s | 9.8s | 9.8s | -55 | v1≈v2 regular ✓ |

**Summary**: 2/2 runaway fixed, 6/8 tail residue removed, 0 over-trim warnings.

## 4. Codified

- ✓ `bible/00_constitution.yaml` `rule_R199_tail_pathology_hardlock`
- ✓ `tools/ab_test_tail_trim_v1_vs_v2.py`
- ✓ `runtime/audits/tail_pathology_audit_1_7.json` (6861 chunks scan)
- ✓ `runtime/audits/ab_test_tail_trim_v1_vs_v2_1_7.json` (8 chunk A/B)
- ⏸️ **PENDING** Mr.Long approve → replace `aggressive_trim_tail` in `svhmp_v13_render.py` với v2 logic

## 5. Cách khác CMD phối hợp

Sau `git pull` từ repo `Trinhlong1988/SVHMP_Studio`:

```bash
# Chạy audit trên chunks của mình
python tools/ab_test_tail_trim_v1_vs_v2.py --seg-dir <local_tmpdir> --json my_audit.json

# So sánh với audit của Mr.Long
diff runtime/audits/ab_test_tail_trim_v1_vs_v2_1_7.json my_audit.json
```

Realtime sync workflow:
- Bên nào commit → push origin main
- Bên kia `git pull --rebase origin main` trước khi work
- Conflict → resolve theo baseline lock R8
