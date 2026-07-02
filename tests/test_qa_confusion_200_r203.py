"""R203 — 200-case confusion-matrix audit cho TOAN BO QA detector (Boss 1/7).

Muc tieu (khong suy luan — chay that, dem ket qua):
  120 case DUNG (sach, QA phai DE YEN)  + 120 case SAI (co loi, QA phai BAT).
  6 co che QA x (20 good + 20 bad):
    - bup       scan_bup_transients   (R80 bup = im->burst to >-3dB)
    - peak      scan_overall_peak     (R80.peak > -3dB)
    - tail      scan_tail_residue     (R76 duoi 200ms > -15dB)
    - silence   scan_internal_silence (R77 im >200ms giua chunk)
    - qct       qa_clean_tail         (cut chu / tap am cuoi)
    - click     scan_click_transients (R80.click = pop muc vua no tren nen im, mid-chunk)
  Bao cao TP/FN/TN/FP moi co che. FN=bo sot loi, FP=bao nham -> bug an -> fix.
Exit 0 = 0 FN + 0 FP (QA chinh xac tuyet doi).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from collections import defaultdict
from svhmp_audio_qa import (scan_bup_transients, scan_overall_peak,
                            scan_tail_residue, scan_internal_silence,
                            scan_click_transients)
from svhmp_v13_render import qa_clean_tail

SR = 22050
rng = np.random.RandomState(203)


def tone(dur, f=300, amp=0.3):
    return (amp * np.sin(2 * np.pi * f * np.arange(int(dur * SR)) / SR)).astype(np.float32)
def noise(dur, amp): return (amp * rng.randn(int(dur * SR))).astype(np.float32)
def sil(dur, lvl=1e-5): return (lvl * np.ones(int(dur * SR))).astype(np.float32)


CM = defaultdict(lambda: {'TP': 0, 'FN': 0, 'TN': 0, 'FP': 0})
DETAIL = []


def judge(mech, is_bad, caught, tag):
    d = CM[mech]
    if is_bad:
        if caught: d['TP'] += 1
        else: d['FN'] += 1; DETAIL.append((mech, 'FN=BO SOT LOI', tag))
    else:
        if caught: d['FP'] += 1; DETAIL.append((mech, 'FP=BAO NHAM', tag))
        else: d['TN'] += 1


# ===== 1. BUP TRANSIENT =====
for k in range(20):  # GOOD: tone lien tuc, khong im->burst
    g = tone(0.5, 180 + 12 * k, 0.3 + 0.015 * k)
    judge('bup', False, len(scan_bup_transients(g, SR)) > 0, f'cont f{180+12*k}')
for k in range(20):  # BAD: im 0.15s + burst to (>-3dB)
    amp = 0.75 + 0.012 * k
    b = np.concatenate([sil(0.15), tone(0.15, 300, amp), tone(0.3, 300, 0.4)])
    judge('bup', True, len(scan_bup_transients(b, SR)) > 0, f'burst {amp:.2f}')

# ===== 2. PEAK (> -3dB) =====
for k in range(20):  # GOOD: peak <= -3.5dB (amp<=0.67)
    amp = 0.10 + 0.03 * k
    judge('peak', False, len(scan_overall_peak(tone(0.4, 250, amp), SR)) > 0, f'amp{amp:.2f}')
for k in range(20):  # BAD: peak > -3dB (amp>=0.72)
    amp = 0.72 + 0.014 * k
    judge('peak', True, len(scan_overall_peak(tone(0.4, 250, amp), SR)) > 0, f'amp{amp:.2f}')

# ===== 3. TAIL RESIDUE (last 200ms > -15dB) =====
for k in range(20):  # GOOD: duoi im (amp<=0.15 = -16.5dB)
    ta = 0.02 + 0.006 * k
    g = np.concatenate([tone(0.6, 300, 0.3), tone(0.25, 300, ta)])
    judge('tail', False, len(scan_tail_residue(g, SR)) > 0, f'tail{ta:.3f}')
for k in range(20):  # BAD: duoi con to (amp>=0.25)
    ta = 0.25 + 0.025 * k
    judge('tail', True, len(scan_tail_residue(tone(0.8, 300, ta), SR)) > 0, f'tail{ta:.2f}')

# ===== 4. INTERNAL SILENCE (>200ms giua) =====
for k in range(20):  # GOOD: lien tuc, hoac gap <200ms
    if k % 2 == 0:
        g = tone(1.2, 200 + 8 * k, 0.3)
    else:
        gap = 0.10 + 0.004 * k  # 100..176ms < 200 (luon duoi nguong)
        g = np.concatenate([tone(0.5, 300, 0.3), sil(gap), tone(0.5, 300, 0.3)])
    judge('silence', False, len(scan_internal_silence(g, SR)) > 0, f'good{k}')
for k in range(20):  # BAD: gap >200ms giua
    gap = 0.25 + 0.028 * k  # 250..780ms
    b = np.concatenate([tone(0.5, 300, 0.3), sil(gap), tone(0.5, 300, 0.3)])
    judge('silence', True, len(scan_internal_silence(b, SR)) > 0, f'gap{gap:.2f}')

# ===== 5. QA_CLEAN_TAIL (cut / tap am cuoi) =====
for k in range(20):  # GOOD: tu sach -> phai GIU (khong cut)
    wd = 0.3 + 0.11 * k
    out, info = qa_clean_tail(tone(wd, 300, 0.3), SR)
    over_trim = len(out) / SR < wd * 0.9 - 0.03
    judge('qct', False, over_trim, f'word{wd:.2f}')
for k in range(20):  # BAD: tu + crackle duoi -> phai GATE
    wd = 0.5 + 0.06 * k
    out, info = qa_clean_tail(np.concatenate([tone(wd, 260, 0.3), noise(0.5, 0.03 + 0.003 * k)]), SR)
    gated = info['gated_ms'] > 1 and len(out) / SR <= wd + 0.4
    judge('qct', True, gated, f'word{wd:.2f}')

# ===== 6. CLICK TRANSIENT (bup/pop muc vua no tren nen im, mid-chunk) =====
def voiced(d, f0=140, a=0.4):
    t = np.arange(int(d * SR)) / SR
    ph = 2 * np.pi * np.cumsum(f0 * (1 + 0.01 * np.sin(2 * np.pi * 5 * t))) / SR
    y = sum((a / k) * np.sin(k * ph) for k in range(1, 6))
    return (y * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t))).astype(np.float32)

def click_gap(amp):
    z = np.concatenate([tone(0.4, 300, 0.3), sil(0.3), tone(0.4, 300, 0.3)])
    p = int(0.55 * SR); z[p:p + 60] = amp; return z

for k in range(20):  # GOOD: giong/plosive/onset/tone muot -> KHONG duoc bat
    typ = k % 4
    if typ == 0:
        g = voiced(1.2, 90 + 15 * k, 0.4)
    elif typ == 1:
        g = np.concatenate([sil(0.1), tone(0.02, 300, 0.6), tone(0.5, 300, 0.5)])  # plosive->vowel
    elif typ == 2:
        g = np.concatenate([sil(0.15), tone(0.5, 300, 0.4 + 0.01 * k)])  # onset sau nghi
    else:
        g = tone(0.6, 200 + 20 * k, 0.5)  # tone muot
    judge('click', False, len(scan_click_transients(g, SR)) > 0, f'good{k}')
for k in range(20):  # BAD: click no trong gap im, muc vua->to (-18..-2dB)
    amp = 0.12 + 0.03 * k
    judge('click', True, len(scan_click_transients(click_gap(amp), SR)) > 0, f'click{amp:.2f}')

# ===== REPORT =====
N = sum(sum(CM[m].values()) for m in CM)
print(f"=== R203 CONFUSION MATRIX ({N} case: {N//2} dung / {N//2} sai) ===")
tot = {'TP': 0, 'FN': 0, 'TN': 0, 'FP': 0}
print(f"{'co che':10} {'TP':>4} {'FN':>4} {'TN':>4} {'FP':>4}  verdict")
for m in ['bup', 'peak', 'tail', 'silence', 'qct', 'click']:
    d = CM[m]
    for k in tot: tot[k] += d[k]
    v = 'OK' if d['FN'] == 0 and d['FP'] == 0 else 'LOI QA!'
    print(f"{m:10} {d['TP']:>4} {d['FN']:>4} {d['TN']:>4} {d['FP']:>4}  {v}")
print(f"{'TONG':10} {tot['TP']:>4} {tot['FN']:>4} {tot['TN']:>4} {tot['FP']:>4}")
caught = tot['TP'] + tot['TN']
print(f"\nDo chinh xac: {caught}/{N} = {caught/N*100:.1f}%  (bat dung {tot['TP']}/{N//2} loi, de yen {tot['TN']}/{N//2} sach)")
if DETAIL:
    print("\n!!! BUG AN (misclassify):")
    for m, kind, tag in DETAIL:
        print(f"  [{m}] {kind}: {tag}")
sys.exit(1 if (tot['FN'] or tot['FP']) else 0)
