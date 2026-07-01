"""R201 regression — qa_clean_tail (voicing-based tail cleaner + continuity).

Chong tai phat cac bug phien 1/7 (Boss):
- "tap am cuoi" = trailing crackle/buzz sau tu cuoi bi giu lai -> phai GATE.
- "cut chu" = over-trim tu that -> CAM cat vao giong.
- Continuity (voiced >=60ms lien tuc) loai crackle roi rac.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from svhmp_v13_render import qa_clean_tail

SR = 22050
PASS, FAIL = [], []


def check(name, cond, detail=""):
    if cond:
        PASS.append(name); print(f"  ✓ {name}")
    else:
        FAIL.append((name, detail)); print(f"  ✗ {name}  {detail}")


voice = (0.3 * np.sin(2 * np.pi * 300 * np.arange(int(1.0 * SR)) / SR)).astype(np.float32)
rng = np.random.RandomState(1)
crackle = (0.03 * rng.randn(int(0.5 * SR))).astype(np.float32)  # noise -> unvoiced buzz

print("=== R201 qa_clean_tail regression ===")

# A: voiced 1s + trailing crackle -> crackle GATED (khong keo dai last_voiced)
out, info = qa_clean_tail(np.concatenate([voice, crackle]), SR)
check("crackle tail gated (dur ~1.0-1.35s)", 0.95 < len(out) / SR < 1.35,
      f"got {len(out)/SR:.2f}s gated={info['gated_ms']:.0f}ms")

# B: voiced 1s + pure silence 0.8s -> silence trimmed
out, _ = qa_clean_tail(np.concatenate([voice, np.zeros(int(0.8 * SR), np.float32)]), SR)
check("silence tail trimmed (~1.0-1.35s)", 0.95 < len(out) / SR < 1.35, f"got {len(out)/SR:.2f}s")

# C: voiced only -> KEEP (khong over-trim)
out, _ = qa_clean_tail(voice, SR)
check("voiced only kept (no over-trim)", len(out) / SR >= 0.95, f"got {len(out)/SR:.2f}s")

# D: short input -> no crash
out, _ = qa_clean_tail(np.zeros(50, np.float32), SR)
check("short input no crash", len(out) == 50)

# E: no-voice (pure noise) -> fallback unchanged (khong cat het ve 0)
out, _ = qa_clean_tail((0.03 * rng.randn(int(0.5 * SR))).astype(np.float32), SR)
check("no-voice fallback unchanged", abs(len(out) - int(0.5 * SR)) < 5)

# F: ket thuc bang ~0 (chong click vao bridge zero)
out, _ = qa_clean_tail(np.concatenate([voice, crackle]), SR)
check("ends near zero (declick)", abs(float(out[-1])) < 0.02, f"last={float(out[-1]):.3f}")

print(f"\n=== SUMMARY: {len(PASS)} PASS / {len(FAIL)} FAIL ===")
for n, d in FAIL:
    print(f"  FAIL: {n} — {d}")
sys.exit(1 if FAIL else 0)
