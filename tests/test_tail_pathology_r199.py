"""R199 regression test — tail pathology hardlock.

Tests trên 8 AB test wavs + synthetic edge cases.
- Runaway (rp<10): trim 30s → ~10s
- Regular chunk: v1≈v2 (diff <100ms)
- Synthetic tail burst: burst removed
- Synthetic long silence trail: silence dropped
- Fallback: no voice → return unchanged
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
import soundfile as sf

from svhmp_v13_render import aggressive_trim_tail

SR = 22050
PASS_CASES = []
FAIL_CASES = []


def check(name, cond, detail=""):
    if cond:
        PASS_CASES.append(name)
        print(f"  ✓ {name}")
    else:
        FAIL_CASES.append((name, detail))
        print(f"  ✗ {name}  {detail}")


def synth_voice_then_silence(voice_s, silence_s):
    """Voice = 400Hz sine, silence = zeros."""
    voice = 0.3 * np.sin(2 * np.pi * 400 * np.arange(int(voice_s * SR)) / SR)
    silence = np.zeros(int(silence_s * SR), dtype=np.float32)
    return np.concatenate([voice.astype(np.float32), silence])


def synth_voice_gap_burst(voice_s, gap_s, burst_s, burst_amp=0.1):
    """Voice then silence gap then small burst then silence."""
    voice = 0.3 * np.sin(2 * np.pi * 400 * np.arange(int(voice_s * SR)) / SR)
    gap = np.zeros(int(gap_s * SR), dtype=np.float32)
    burst = burst_amp * np.sin(2 * np.pi * 200 * np.arange(int(burst_s * SR)) / SR)
    tail_silence = np.zeros(int(0.5 * SR), dtype=np.float32)
    return np.concatenate([voice.astype(np.float32), gap, burst.astype(np.float32), tail_silence])


print("=== R199 REGRESSION — synthetic ===")

# Case A: runaway (voice 5s + silence 25s)
data = synth_voice_then_silence(5.0, 25.0)
out = aggressive_trim_tail(data, SR)
dur = len(out) / SR
check("runaway_5s+25s → trim to ~5s", 4.5 < dur < 6.0, f"got {dur:.2f}s")

# Case B: regular chunk (voice 3s + silence 0.5s)
data = synth_voice_then_silence(3.0, 0.5)
out = aggressive_trim_tail(data, SR)
dur = len(out) / SR
check("regular 3s+0.5s → keep ~3s", 2.9 < dur < 3.2, f"got {dur:.2f}s")

# Case C: tail burst after gap
data = synth_voice_gap_burst(voice_s=3.0, gap_s=0.5, burst_s=0.25, burst_amp=0.1)
out = aggressive_trim_tail(data, SR)
dur = len(out) / SR
check("tail_burst after 0.5s gap → drop burst", 2.9 < dur < 3.3, f"got {dur:.2f}s (should ≈3s, not 3.75s)")

# Case D: no voice fallback
data = np.zeros(int(2.0 * SR), dtype=np.float32)
out = aggressive_trim_tail(data, SR)
dur = len(out) / SR
check("no_voice → return unchanged", abs(dur - 2.0) < 0.01, f"got {dur:.3f}s (should be 2.0)")

# Case E: short input
data = np.zeros(100, dtype=np.float32)
out = aggressive_trim_tail(data, SR)
check("short input → no crash", len(out) == 100)

# Case F: voice only (no silence)
voice = 0.3 * np.sin(2 * np.pi * 400 * np.arange(int(3.0 * SR)) / SR).astype(np.float32)
out = aggressive_trim_tail(voice, SR)
dur = len(out) / SR
check("voice only 3s → keep ~3s", 2.9 < dur < 3.1, f"got {dur:.2f}s")

# Case G: voice + burst (no gap → burst treated as continuation)
data = synth_voice_gap_burst(voice_s=3.0, gap_s=0.05, burst_s=0.25, burst_amp=0.1)
out = aggressive_trim_tail(data, SR)
dur = len(out) / SR
check("voice+burst_no_gap → keep both (no gap qualifier)", 3.2 < dur < 3.5, f"got {dur:.2f}s")

# Case H: real AB test files if available
AB_ROOT = Path(r'C:/Users/Administrator/Desktop/EP01_AB_TESTS')
if AB_ROOT.exists():
    print()
    print("=== R199 REGRESSION — real AB tests ===")
    for name, expected in [
        ('Test4_repetition_penalty/A_rp10.0.wav', ('regular', 9.5, 11.0)),
        ('Test4_repetition_penalty/B_rp2.0.wav', ('runaway_fix', 8.0, 11.0)),
        ('Test4_repetition_penalty/C_rp1.2.wav', ('runaway_fix', 8.0, 11.0)),
    ]:
        p = AB_ROOT / name
        if not p.exists(): continue
        data, sr = sf.read(p)
        if data.ndim > 1: data = data[:, 0]
        out = aggressive_trim_tail(data.astype(np.float32), sr)
        dur = len(out) / sr
        _, lo, hi = expected
        check(f"AB {p.name} → duration {lo}-{hi}s", lo <= dur <= hi, f"got {dur:.2f}s")

print()
print(f"=== SUMMARY: {len(PASS_CASES)} PASS / {len(FAIL_CASES)} FAIL ===")
for name, detail in FAIL_CASES:
    print(f"  FAIL: {name} — {detail}")

sys.exit(1 if FAIL_CASES else 0)
