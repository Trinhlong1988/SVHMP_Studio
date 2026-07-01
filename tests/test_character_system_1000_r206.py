"""R206 — 1000-case confusion (Boss 1/7): 500 DUNG + 500 SAI cho dialog_voice_validator.
Chung minh QA giong/vung BAT dung loi va DE YEN case hop le (khong suy luan — chay that).
5 loai loi x100: MISSING mandatory, HOMETOWN<->REGION mismatch, PARTICLE sai vung,
DIALECT_LEAK trong cau, FORBIDDEN word. Exit 0 = 0 FN + 0 FP.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
from dialog_voice_validator import validate

# 3 vung marker phan biet ro
REG = ['bac', 'trung', 'nam']
HOME = {'bac': 'Hà Nội', 'trung': 'Huế', 'nam': 'Sài Gòn'}
OWN_PARTICLE = {'bac': 'nhỉ', 'trung': 'rứa', 'nam': 'nghen'}
OTHER_PARTICLE = {'bac': 'rứa', 'trung': 'nghen', 'nam': 'nhé'}  # cua vung khac -> sai
VALID_LINE = {
    'bac': ["Con về nhé.", "Thế cơ à.", "Mẹ đợi con nhỉ.", "Con biết rồi nhé."],
    'trung': ["Con đi mô rứa.", "Mạ ơi con về tê.", "Răng hỉ.", "Con nhớ mô rứa."],
    'nam': ["Con dìa nghen.", "Cưng ơi con nè.", "Vô nhà nghen.", "Con thương má nghen."],
}
LEAK_MARKER = {'bac': 'rứa', 'trung': 'nghen', 'nam': 'nhé'}  # marker vung khac -> leak

CM = {'TP': 0, 'FN': 0, 'TN': 0, 'FP': 0}
DETAIL = []


def judge(is_bad, caught, tag):
    if is_bad:
        if caught: CM['TP'] += 1
        else: CM['FN'] += 1; DETAIL.append(('FN=BO SOT', tag))
    else:
        if caught: CM['FP'] += 1; DETAIL.append(('FP=BAO NHAM', tag))
        else: CM['TN'] += 1


def base(r):
    return {'region_dialect': r, 'hometown': HOME[r], 'pronoun_system': 'con',
            'particles': [OWN_PARTICLE[r]], 'forbidden_words': ['vãi', 'đm']}


# ── 500 DUNG (profile nhat quan + line dung vung + khong forbidden) ──
for i in range(500):
    r = REG[i % 3]
    line = VALID_LINE[r][i % len(VALID_LINE[r])]
    judge(False, len(validate(base(r), line)) > 0, f'valid {r} #{i}')

# ── 500 SAI (100 moi loai) ──
for i in range(100):  # 1. thieu mandatory
    r = REG[i % 3]; v = base(r); v['region_dialect'] = ''
    judge(True, len(validate(v, VALID_LINE[r][0])) > 0, f'missing {r}')
for i in range(100):  # 2. que <-> vung lech
    r = REG[i % 3]; other = REG[(i + 1) % 3]; v = base(r); v['hometown'] = HOME[other]
    judge(True, len(validate(v, VALID_LINE[r][0])) > 0, f'home_mismatch {r}')
for i in range(100):  # 3. tieu tu sai vung trong profile
    r = REG[i % 3]; v = base(r); v['particles'] = [OTHER_PARTICLE[r]]
    judge(True, len(validate(v, VALID_LINE[r][0])) > 0, f'particle_wrong {r}')
for i in range(100):  # 4. dialect leak trong cau
    r = REG[i % 3]; line = f"Con nói {LEAK_MARKER[r]} đó."
    judge(True, len(validate(base(r), line)) > 0, f'leak {r}')
for i in range(100):  # 5. dung tu cam
    r = REG[i % 3]; v = base(r); v['forbidden_words'] = ['chửi']
    judge(True, len(validate(v, "Con chửi rồi đó.")) > 0, f'forbidden {r}')

# ── REPORT ──
N = sum(CM.values())
print("=== R206 CONFUSION dialog_voice_validator (1000 case) ===")
print(f"  TP={CM['TP']}  FN={CM['FN']}  TN={CM['TN']}  FP={CM['FP']}   (N={N})")
acc = CM['TP'] + CM['TN']
print(f"  Do chinh xac: {acc}/{N} = {acc/N*100:.1f}%  (bat {CM['TP']}/500 loi, de yen {CM['TN']}/500 dung)")
if DETAIL:
    print("  !!! misclassify:")
    for k, t in DETAIL[:20]:
        print(f"    {k}: {t}")
sys.exit(1 if (CM['FN'] or CM['FP']) else 0)
