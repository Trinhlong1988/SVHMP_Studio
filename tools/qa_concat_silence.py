"""R94b — Verify silence bridges at section boundaries.

Detect silence ≥1500ms between expected timestamps (per cumulative section duration).

Usage:
  python tools/qa_concat_silence.py --wav <path> --expected_count 5
  python tools/qa_concat_silence.py --wav output/ep_01/EP01_VOICE_v102.wav
"""
import argparse
import sys
import json
import soundfile as sf
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
SECTIONS_DIR = BASE / "output/ep_01/sections"


def detect_silence_blocks(audio, sr, threshold_dbfs=-50, min_silence_ms=1000):
    """Return list of (start_sec, end_sec, duration_sec) for silence blocks ≥ min_silence_ms."""
    thr = 10 ** (threshold_dbfs / 20)
    is_silent = np.abs(audio) < thr

    blocks = []
    cur_start = None
    for i, s in enumerate(is_silent):
        if s and cur_start is None:
            cur_start = i
        elif not s and cur_start is not None:
            dur_samples = i - cur_start
            if dur_samples >= int(sr * min_silence_ms / 1000):
                blocks.append((cur_start / sr, i / sr, dur_samples / sr))
            cur_start = None
    if cur_start is not None:
        dur_samples = len(is_silent) - cur_start
        if dur_samples >= int(sr * min_silence_ms / 1000):
            blocks.append((cur_start / sr, len(is_silent) / sr, dur_samples / sr))
    return blocks


def expected_boundary_timestamps(sections_dir, silence_padding_sec=1.5):
    """Compute expected silence MIDPOINT timestamps from per-section WAV durations + silence padding.

    Concat with silence: section[i] starts at sum(durations[0:i]) + i * silence_padding.
    Silence i starts AFTER section i ends = cum_i (after i+1 sections) + i * silence_padding.
    Silence i midpoint = silence_start + silence_padding/2
    """
    midpoints = []
    cum = 0.0
    section_order = ["hook", "setup", "incident", "reveal", "payoff"]  # 5 boundaries
    silence_count = 0
    for s in section_order:
        wav = sections_dir / f"{s}.wav"
        if not wav.exists():
            return None
        info = sf.info(str(wav))
        cum += info.duration
        # Silence i starts here (after section i ends)
        # Offset by previous silences
        silence_start = cum + silence_count * silence_padding_sec
        silence_mid = silence_start + silence_padding_sec / 2
        midpoints.append(silence_mid)
        silence_count += 1
    return midpoints


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--expected_count", type=int, default=5, help="Expected section boundaries (default 5 = 6 sections)")
    ap.add_argument("--min_silence_ms", type=int, default=1300, help="Min silence to count as boundary (default 1300ms tolerance)")
    ap.add_argument("--threshold_dbfs", type=int, default=-45)
    ap.add_argument("--sections_dir", default=str(SECTIONS_DIR), help="Sections WAV dir for expected timestamps")
    ap.add_argument("--tolerance_sec", type=float, default=3.0, help="Tolerance ± for boundary match")
    args = ap.parse_args()

    wav_path = Path(args.wav)
    if not wav_path.exists():
        print(f"ERROR: WAV not found: {wav_path}")
        sys.exit(1)

    audio, sr = sf.read(str(wav_path))
    if audio.ndim > 1:
        audio = audio[:, 0]

    blocks = detect_silence_blocks(audio, sr, args.threshold_dbfs, args.min_silence_ms)

    # Compute expected timestamps
    expected = expected_boundary_timestamps(Path(args.sections_dir))
    if expected is None:
        print("⚠️ Cannot compute expected timestamps (sections WAV missing) — fallback to count mode")
        # Old behavior
        qualifying = [b for b in blocks if b[2] >= 1.4]
        enough = len(qualifying) >= args.expected_count
        verdict = "PASS" if enough else "FAIL"
        print(f"== R94b GATE (count mode): {verdict} ==")
        sys.exit(0 if enough else 1)

    print(f"=== R94b CONCAT SILENCE QA (timestamp mode) — {wav_path.name} ===")
    print(f"  Duration: {len(audio)/sr:.2f}s, SR: {sr}")
    print(f"  Silence threshold: {args.threshold_dbfs} dBFS")
    print(f"  Expected boundaries at (cumulative sec): {[f'{t:.2f}' for t in expected]}")
    print(f"  Tolerance: ±{args.tolerance_sec}s")
    print()

    # For each expected boundary, find silence block whose midpoint is within tolerance
    matched_count = 0
    boundary_results = []
    for i, exp_t in enumerate(expected):
        match = None
        for b_start, b_end, b_dur in blocks:
            mid = (b_start + b_end) / 2
            if abs(mid - exp_t) <= args.tolerance_sec and b_dur >= 1.4:
                match = (b_start, b_end, b_dur)
                break
        if match:
            matched_count += 1
            boundary_results.append((exp_t, match, "✅"))
            print(f"  ✅ Boundary {i+1} @ {exp_t:.2f}s: silence {match[0]:.2f}s → {match[1]:.2f}s ({match[2]*1000:.0f}ms)")
        else:
            boundary_results.append((exp_t, None, "❌"))
            print(f"  ❌ Boundary {i+1} @ {exp_t:.2f}s: NO silence block within ±{args.tolerance_sec}s tolerance")

    print()
    print(f"  Matched: {matched_count} / {len(expected)}")

    enough = matched_count >= args.expected_count
    verdict = "PASS" if enough else "FAIL"
    print(f"\n== R94b GATE: {verdict} ==")
    if not enough:
        print(f"  Need {args.expected_count} boundary silence ≥1400ms at expected timestamps, found {matched_count}")

    # JSON output (timestamp mode)
    report = {
        "wav": str(wav_path),
        "duration_sec": round(len(audio)/sr, 2),
        "sample_rate": sr,
        "expected_boundaries_count": len(expected),
        "matched_count": matched_count,
        "expected_count_required": args.expected_count,
        "verdict": verdict,
        "boundaries": [{"expected_sec": round(e, 2), "matched": m is not None,
                        "actual_duration_ms": int(m[2]*1000) if m else 0}
                       for e, m, _ in boundary_results],
    }
    json_path = wav_path.with_suffix(".concat_silence.json")
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\n  Report: {json_path}")
    sys.exit(0 if enough else 1)


if __name__ == "__main__":
    main()
