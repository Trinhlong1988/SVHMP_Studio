"""R208 — 1000-case Dialogue Consistency theo TUOI (phan bien.txt module 4).
500 DUNG (nguoi gia noi chuan) + 500 SAI (nguoi gia noi tieng long hien dai "Ok bro").
Exit 0 = 0 FN + 0 FP.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
sys.stdout.reconfigure(encoding='utf-8')
from dialog_voice_validator import validate, MODERN_SLANG

CM = {'TP': 0, 'FN': 0, 'TN': 0, 'FP': 0}
def judge(bad, caught):
    k = ('TP' if caught else 'FN') if bad else ('FP' if caught else 'TN')
    CM[k] += 1

elder = {'region_dialect': 'nam', 'hometown': 'Sài Gòn', 'pronoun_system': 'con',
         'particles': ['nghen'], 'age_group': '66+', 'forbidden_words': []}
CLEAN = ["Con dìa nghen.", "Má đợi con nghen.", "Vô nhà nghen con.", "Con thương má nghen."]
SLANG = list(MODERN_SLANG)

# 500 DUNG: nguoi gia noi sach (khong slang, dung vung)
for i in range(500):
    judge(False, len(validate(elder, CLEAN[i % len(CLEAN)])) > 0)
# 500 SAI: nguoi gia chen tieng long hien dai
for i in range(500):
    s = SLANG[i % len(SLANG)]
    judge(True, any(x['code'] == 'AGE_INAPPROPRIATE_SLANG' for x in validate(elder, f"{s} con dìa nghen.")))

N = sum(CM.values()); acc = CM['TP'] + CM['TN']
print("=== R208 CONFUSION Dialogue-Consistency tuoi (1000 case) ===")
print(f"  TP={CM['TP']} FN={CM['FN']} TN={CM['TN']} FP={CM['FP']}")
print(f"  Do chinh xac: {acc}/{N} = {acc/N*100:.1f}%  (bat {CM['TP']}/500 sai tuoi, de yen {CM['TN']}/500 dung)")
sys.exit(1 if (CM['FN'] or CM['FP']) else 0)
