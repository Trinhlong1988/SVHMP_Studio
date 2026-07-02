"""R207 — 1000-case confusion cho story_consistency_validator (Boss 1/7).
500 NHAT QUAN (khong doi field khoa -> phai DE YEN) + 500 MAU THUAN (doi 1 field khoa -> phai BAT).
Exit 0 = 0 FN + 0 FP.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
sys.stdout.reconfigure(encoding='utf-8')
from story_consistency_validator import validate_consistency, LOCKED_FIELDS

CM = {'TP': 0, 'FN': 0, 'TN': 0, 'FP': 0}
DETAIL = []
def judge(is_bad, caught, tag):
    if is_bad:
        (CM.__setitem__('TP', CM['TP'] + 1) if caught else (CM.__setitem__('FN', CM['FN'] + 1), DETAIL.append(('FN', tag))))
    else:
        (CM.__setitem__('FP', CM['FP'] + 1), DETAIL.append(('FP', tag))) if caught else CM.__setitem__('TN', CM['TN'] + 1)

def base(i):
    return {'character_id': f'PAS_{i:04d}', 'full_name': f'Nhan {i}', 'gender': 'nu' if i % 2 else 'nam',
            'date_of_birth': f'19{60 + i % 40}-01-01', 'age_group': ['18-25', '26-35', '36-50', '66+'][i % 4],
            'hometown': ['Hà Nội', 'Huế', 'Sài Gòn'][i % 3], 'occupation': ['giáo viên', 'bác sĩ', 'nông dân'][i % 3],
            'region_dialect': ['bac', 'trung', 'nam'][i % 3], 'parents': f'Bố {i}/Mẹ {i}',
            'death_date': f'20{10 + i % 15}-05-05', 'death_type': ['tai_nan', 'benh_tat', 'oan_khuat'][i % 3],
            'pain_core': f'noi dau {i}', 'catchphrase': f'cau cua mieng {i}'}

MUT = [f for f in LOCKED_FIELDS if f != 'character_id' and base(0).get(f)]  # chi doi field co gia tri

# 500 NHAT QUAN
for i in range(500):
    b = base(i)
    judge(False, len(validate_consistency(b, dict(b))) > 0, f'same {i}')
# 500 MAU THUAN (doi 1 field khoa)
for i in range(500):
    b = base(i); f = MUT[i % len(MUT)]
    cur = dict(b); cur[f] = (b[f] or 'x') + '_DOI'
    judge(True, len(validate_consistency(b, cur)) > 0, f'change {f} {i}')

N = sum(CM.values()); acc = CM['TP'] + CM['TN']
print("=== R207 CONFUSION story_consistency (1000 case) ===")
print(f"  TP={CM['TP']} FN={CM['FN']} TN={CM['TN']} FP={CM['FP']}")
print(f"  Do chinh xac: {acc}/{N} = {acc/N*100:.1f}%  (bat {CM['TP']}/500 mau thuan, de yen {CM['TN']}/500 nhat quan)")
for k, t in DETAIL[:10]:
    print(f"    {k}: {t}")
sys.exit(1 if (CM['FN'] or CM['FP']) else 0)
