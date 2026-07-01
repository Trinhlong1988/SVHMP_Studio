"""R202 — 50-case adversarial audit cho tail handling intro (Boss 1/7).

Phan bien 3 lop bug phien 1/7:
  - HUT HOI / runaway: duoi im lang/runaway dai -> phai trim, KHONG giu le the.
  - CUT CHU: over-trim cat vao tu (nhat la tu ngan, phu am cuoi, release mem) -> CAM.
  - TAP AM CUOI: crackle/buzz sau tu cuoi -> phai GATE (continuity loai window le).
  + declick: ket thuc ~0 chong pop vao bridge zero.

Test qa_clean_tail() = ham xu ly tail cua svhmp_v13_render (voicing + continuity).
Exit 0 = 50/50 PASS.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from svhmp_v13_render import qa_clean_tail

SR = 22050
rng = np.random.RandomState(202)
PASS, FAIL = [], []

PAD = 0.14  # release_pad_ms default
MARGIN = 0.25  # dung sai pad+fade+bien


def tone(dur, f=300, amp=0.3, fo=0.0):
    n = int(dur * SR)
    y = amp * np.sin(2 * np.pi * f * np.arange(n) / SR)
    if fo > 0:
        fn = min(int(fo * SR), n)
        y[-fn:] *= np.linspace(1, 0, fn)
    return y.astype(np.float32)


def noise(dur, amp): return (amp * rng.randn(int(dur * SR))).astype(np.float32)
def sil(dur): return np.zeros(int(dur * SR), np.float32)


def case(cid, desc, data, word_dur, expect_gate=True, fallback=False):
    out, info = qa_clean_tail(data, SR)
    kept = len(out) / SR if len(out) else 0
    if fallback:  # no-voice: giu nguyen, khong cat ve 0
        ok = abs(kept - len(data) / SR) < 0.02
        (PASS if ok else FAIL).append((cid, desc, kept))
        return
    ok_word = kept >= word_dur * 0.9 - 0.03           # KHONG cut/hut hoi
    ok_trim = (kept <= word_dur + PAD + MARGIN) if expect_gate else True  # trailing gated
    ok_end = abs(float(out[-1])) < 0.03 if len(out) else False            # declick
    ok = ok_word and ok_trim and ok_end
    (PASS if ok else FAIL).append((cid, desc, kept))
    if not ok:
        print(f"  x C{cid:02d} {desc}: kept={kept:.2f} word={word_dur:.2f} "
              f"[cut={not ok_word} notgate={not ok_trim} end={not ok_end} {float(out[-1]):.3f}]")


print("=== R202 50-case adversarial tail audit ===")
cid = 0

# --- Cat A: CUT CHU — tu ngan/dai + im lang, phai giu tron (12) ---
for wd in [0.08, 0.12, 0.18, 0.25, 0.35, 0.5, 0.7, 1.0, 1.5, 2.0, 2.5, 0.15]:
    cid += 1
    case(cid, f"A word {wd}s +sil", np.concatenate([tone(wd, 300), sil(0.7)]), wd, True)

# --- Cat B: TAP AM CUOI — tu + crackle/buzz duoi, phai gate (12) ---
for i, (wd, camp, cdur) in enumerate([
    (1.0, 0.03, 0.5), (0.8, 0.05, 0.6), (1.2, 0.08, 0.4), (0.5, 0.04, 0.5),
    (1.0, 0.02, 0.8), (0.6, 0.06, 0.3), (1.5, 0.03, 0.6), (0.4, 0.05, 0.5),
    (2.0, 0.04, 0.5), (0.9, 0.07, 0.4), (1.1, 0.03, 0.7), (0.7, 0.05, 0.5)]):
    cid += 1
    case(cid, f"B word {wd}s +crackle{camp}", np.concatenate([tone(wd, 260), noise(cdur, camp)]), wd, True)

# --- Cat C: HUT HOI / runaway — tu + im lang KHONG lo (8) ---
for wd, sd in [(1.0, 5), (2.0, 10), (1.5, 15), (0.8, 20), (3.0, 25), (1.0, 8), (0.5, 12), (2.0, 6)]:
    cid += 1
    case(cid, f"C runaway {wd}s +{sd}s sil", np.concatenate([tone(wd, 300), sil(sd)]), wd, True)

# --- Cat D: tu ket GAT (do-like) / phu am cuoi vo thanh + crackle (10) ---
for i, (wd, fo) in enumerate([(0.5, 0.0), (0.8, 0.0), (1.0, 0.02), (0.6, 0.0),
                               (1.2, 0.03), (0.4, 0.0), (0.9, 0.01), (0.7, 0.0),
                               (1.5, 0.02), (0.3, 0.0)]):
    cid += 1
    # vowel + short unvoiced fricative (50-90ms) + crackle -> giu vowel+fricative, gate crackle
    fric = noise(0.06 + 0.03 * (i % 2), 0.12)
    d = np.concatenate([tone(wd, 300, fo=fo), fric, noise(0.4, 0.03)])
    case(cid, f"D checked-end {wd}s", d, wd, True)

# --- Cat E: edge (8) ---
cid += 1; case(cid, "E silence only", sil(0.5), 0, fallback=True)
cid += 1; case(cid, "E noise only", noise(0.5, 0.03), 0, fallback=True)
cid += 1; case(cid, "E tiny 40 samp", np.zeros(40, np.float32), 0, fallback=True)
cid += 1; case(cid, "E full voiced no trail", tone(1.0, 300), 1.0, expect_gate=False)
cid += 1; case(cid, "E long voiced 3s no trail", tone(3.0, 220), 3.0, expect_gate=False)
cid += 1  # word + short gap + word (2 cau) -> giu ca hai + gate cuoi
case(cid, "E two-words+crackle",
     np.concatenate([tone(0.6, 300), sil(0.15), tone(0.6, 300), noise(0.4, 0.04)]), 1.35, True)
cid += 1  # tap am NHE (noise ~-26dB) sau tu -> phai gate (tap am that = noise, KHONG phai tone)
case(cid, "E quiet noise tail",
     np.concatenate([tone(1.0, 300), noise(0.5, 0.015)]), 1.0, True)
cid += 1  # crackle CAO (-20dB) sau tu -> van phai gate (continuity)
case(cid, "E loud crackle tail",
     np.concatenate([tone(1.0, 300), (0.1 * rng.randn(int(0.5 * SR))).astype(np.float32)]), 1.0, True)

print(f"\n=== SUMMARY: {len(PASS)}/{cid} PASS, {len(FAIL)} FAIL ===")
if FAIL:
    print("FAILS:", [(c, d) for c, d, _ in FAIL])
sys.exit(1 if FAIL else 0)
