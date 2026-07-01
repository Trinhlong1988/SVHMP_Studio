"""A/B test: aggressive_trim_tail v1 (current, search 600ms) vs v2 (full-scan + gap qualifier).

Regression per R199 mandate:
- ≥5 THƯỜNG chunks: v2 output diff ≤100ms vs v1 → PASS
- ≥1 runaway chunk (rp=2.0 test wav): v2 must cắt 30s→~10s, v1 giữ 30s
- ≥1 case #1 chunk (legacy tail burst): v2 xoá burst, v1 preserve

Usage:
    python tools/ab_test_tail_trim_v1_vs_v2.py --seg-dir <tmpdir_of_seg_files>
    python tools/ab_test_tail_trim_v1_vs_v2.py --files <wav1> <wav2> ...
"""
import argparse, sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
import soundfile as sf


def aggressive_trim_tail_v1(data, sr, search_ms=600, silence_thr_db=-30):
    """CURRENT logic (svhmp_v13_render.py:118)."""
    n = len(data)
    search_n = int(search_ms * sr / 1000)
    if n <= search_n:
        return data.copy()
    thr = 10 ** (silence_thr_db / 20)
    win_n = max(1, int(0.001 * sr))  # 1ms window

    last_voice_end = n
    for i in range(n - win_n, max(0, n - search_n), -win_n):
        win_rms = np.sqrt(np.mean(data[i:i+win_n] ** 2))
        if win_rms > thr:
            last_voice_end = i + win_n
            break

    grace_n = int(0.050 * sr)  # 50ms grace
    keep_end = min(len(data), last_voice_end + grace_n)
    out = data[:keep_end].copy()
    fade_n = int(0.010 * sr)  # 10ms fade
    if 0 < fade_n < len(out):
        ramp = np.linspace(1.0, 0.0, fade_n).astype(np.float32)
        out[-fade_n:] *= ramp
    return out


def aggressive_trim_tail_v2(data, sr, silence_thr_db=-40, gap_ms=300, main_run_ms=100,
                             grace_ms=80, fade_ms=10, win_ms=10):
    """NEW logic — R199 mandate.

    - Full scan backwards (no search_ms cap)
    - Find last main voice region (≥100ms contiguous voice above threshold)
    - Cut at end of main voice + grace_ms
    - Drops isolated tail bursts + long silent runaway
    - Fallback: no main voice → return unchanged
    """
    thr = 10 ** (silence_thr_db / 20)
    win_n = int(win_ms * sr / 1000)
    n_win = len(data) // win_n
    if n_win < main_run_ms // win_ms + 5:
        return data.copy()

    win_rms = np.array([
        np.sqrt(np.mean(data[i*win_n:(i+1)*win_n]**2))
        for i in range(n_win)
    ])
    voice_mask = win_rms > thr
    main_run = main_run_ms // win_ms  # e.g. 100/10 = 10

    last_main_end_win = None
    run = 0
    for i in range(n_win):
        if voice_mask[i]:
            run += 1
            if run >= main_run:
                last_main_end_win = i + 1
        else:
            run = 0

    if last_main_end_win is None:
        return data.copy()

    grace_n = int(grace_ms * sr / 1000)
    cut = min(len(data), last_main_end_win * win_n + grace_n)
    out = data[:cut].copy()
    fade_n = int(fade_ms * sr / 1000)
    if 0 < fade_n < len(out):
        ramp = np.linspace(1.0, 0.0, fade_n).astype(np.float32)
        out[-fade_n:] *= ramp
    return out


def compare(path):
    data, sr = sf.read(path)
    if data.ndim > 1: data = data[:, 0]
    data = data.astype(np.float32)
    orig_s = len(data) / sr

    v1_out = aggressive_trim_tail_v1(data, sr)
    v2_out = aggressive_trim_tail_v2(data, sr)

    v1_s = len(v1_out) / sr
    v2_s = len(v2_out) / sr
    diff_ms = (v1_s - v2_s) * 1000

    # Classify
    if orig_s > 20 and v1_s > 20 and v2_s < 15:
        verdict = 'RUNAWAY_FIXED_BY_V2'
    elif abs(diff_ms) < 100:
        verdict = 'v1≈v2 (regular chunk)'
    elif diff_ms > 100:
        verdict = 'V2_CUT_MORE (potential tail burst/runaway removed)'
    else:
        verdict = 'V2_CUT_LESS (⚠️ over-preserve — check)'

    return {
        'file': path.name,
        'orig_s': round(orig_s, 3),
        'v1_out_s': round(v1_s, 3),
        'v2_out_s': round(v2_s, 3),
        'diff_ms': round(diff_ms, 1),
        'verdict': verdict,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seg-dir', help='Directory containing seg_*.wav')
    ap.add_argument('--files', nargs='*', help='Explicit list of wav files')
    ap.add_argument('--json', help='Optional JSON output path')
    args = ap.parse_args()

    files = []
    if args.seg_dir:
        files.extend(sorted(Path(args.seg_dir).glob('seg_*.wav')))
    if args.files:
        files.extend([Path(f) for f in args.files])
    if not files:
        print('No input. Use --seg-dir or --files.')
        return 2

    print(f'{"File":<50} {"Orig":<8} {"v1":<8} {"v2":<8} {"Δms":<10} Verdict')
    print('-' * 130)
    results = []
    for f in files:
        r = compare(f)
        results.append(r)
        print(f'{r["file"]:<50} {r["orig_s"]:<8} {r["v1_out_s"]:<8} {r["v2_out_s"]:<8} {r["diff_ms"]:<10} {r["verdict"]}')

    # Verdict summary
    regular = [r for r in results if r['verdict'].startswith('v1≈v2')]
    runaway_fixed = [r for r in results if r['verdict'] == 'RUNAWAY_FIXED_BY_V2']
    v2_more = [r for r in results if r['verdict'].startswith('V2_CUT_MORE')]
    warn = [r for r in results if r['verdict'].startswith('V2_CUT_LESS')]

    print()
    print(f'=== REGRESSION SUMMARY ({len(files)} chunks) ===')
    print(f'  Regular (v1≈v2 within 100ms):  {len(regular)}')
    print(f'  Runaway fixed by v2:           {len(runaway_fixed)}')
    print(f'  v2 cut MORE (tail cleanup):    {len(v2_more)}')
    print(f'  ⚠️ v2 cut LESS (warn):          {len(warn)}')

    if args.json:
        Path(args.json).write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'\nJSON: {args.json}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
