"""SVHMP — Character Balance Report (Boss 1/7, target tu Đúng.docx).

Kiem soat CAN BANG xuyen suot 100 tap:
- Phan bo tuoi (them TRE EM + NGUOI GIA — hien roster thieu).
- Da dang KIEU CHET (khong tap nao cung 'oan hon bi hai').
- So nhan vat/tap (5-8, khong qua 10 — nghe TTS de roi).
- Vung giong (dialogue khong don dieu).
Bao cao ACTUAL vs TARGET, flag lech. Khong suy luan — doc so lieu tu roster.
"""
from __future__ import annotations
import sys
from pathlib import Path
from collections import Counter
sys.path.insert(0, str(Path(__file__).parent))
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
from character_manager import CharacterRegistry

# ── TARGET (Đúng.docx) ──
AGE_STAGE_TARGET = {  # % tren tong
    'child':   (10, 15),
    'youth':   (25, 30),
    'middle':  (30, 35),
    'elderly': (15, 20),
    'unknown': (5, 10),
}
AGE_RANGE_TO_STAGE = {
    '0-12': 'child', '13-17': 'child', '<18': 'child',
    '18-25': 'youth', '26-35': 'youth',
    '36-50': 'middle', '51-65': 'middle',
    '66+': 'elderly',
}
DEATH_TYPES_REQUIRED = ['tai_nan', 'benh_tat', 'mat_tich', 'oan_khuat',
                        'tu_nhien', 'hieu_lam', 'hy_sinh', 'bi_phan_boi', 'khong_ro']
PER_EP_COUNT = (5, 8)   # nhan vat hieu qua / tap
PER_EP_MAX = 10


def _pct(n, tot): return round(100 * n / tot, 1) if tot else 0.0


def report(reg: CharacterRegistry) -> dict:
    pas = reg.all('passenger')
    tot = len(pas)
    out = {'total': tot, 'flags': []}

    # 1. Tuoi
    stage = Counter()
    for c in pas:
        stage[AGE_RANGE_TO_STAGE.get(c.age_range, 'unknown')] += 1
    out['age_stage'] = {k: {'n': stage[k], 'pct': _pct(stage[k], tot),
                            'target': AGE_STAGE_TARGET.get(k)} for k in AGE_STAGE_TARGET}
    for k, (lo, hi) in AGE_STAGE_TARGET.items():
        p = _pct(stage[k], tot)
        if p < lo:
            out['flags'].append(f"AGE '{k}' {p}% < target {lo}-{hi}% (THIEU)")
        elif p > hi:
            out['flags'].append(f"AGE '{k}' {p}% > target {lo}-{hi}% (THUA)")

    # 2. Da dang cai chet
    dt = Counter(c.death.get('type', '?') if isinstance(c.death, dict) else '?' for c in pas)
    have = {k for k in dt if k and k != '?'}
    out['death_types_present'] = dict(dt)
    missing_dt = [d for d in DEATH_TYPES_REQUIRED if d not in have]
    if missing_dt:
        out['flags'].append(f"DEATH thieu {len(missing_dt)}/{len(DEATH_TYPES_REQUIRED)} kieu: {missing_dt}")

    # 3. Vung giong set chua
    unset_voice = sum(1 for c in pas if not (c.voice.region_dialect or '').strip())
    out['voice_region_unset'] = unset_voice
    if unset_voice:
        out['flags'].append(f"VOICE region chua set: {unset_voice}/{tot} (dialogue don dieu)")

    # 4. So nhan vat/tap (chi dem focal trong roster — canh bao neu chua co secondary cast)
    ep_count = Counter(c.assigned_ep for c in pas if c.assigned_ep)
    over = {e: n for e, n in ep_count.items() if n > PER_EP_MAX}
    out['per_ep_focal_max'] = max(ep_count.values()) if ep_count else 0
    out['note_secondary_cast'] = "Roster chi track FOCAL/ep; secondary cast (5-8/tap) CHUA quan ly -> can bo sung"
    if over:
        out['flags'].append(f"PER-EP >{PER_EP_MAX} focal: {over}")

    return out


def diversity_report(reg: CharacterRegistry) -> dict:
    """Diversity (phan bien.txt): dam bao 100 tap KHONG lap tren nhieu truc."""
    pas = reg.all('passenger'); tot = len(pas) or 1
    dims = {
        'gender': [c.gender for c in pas],
        'age_range': [c.age_range for c in pas],
        'occupation': [(c.background or {}).get('occupation', '') for c in pas],
        'hometown': [c.voice.hometown for c in pas],
        'region_dialect': [c.voice.region_dialect for c in pas],
        'death_type': [(c.death or {}).get('type', '') for c in pas],
        'pain': [(c.death or {}).get('pain', '') for c in pas],
        'role': [c.narrative_hook for c in pas],
    }
    out = {}
    for k, vals in dims.items():
        ne = [v for v in vals if v]
        out[k] = {'distinct': len(set(ne)), 'filled': len(ne), 'ratio': round(len(set(ne)) / tot, 2)}
    return out


def main():
    reg = CharacterRegistry()
    r = report(reg)
    print(f"=== CHARACTER BALANCE REPORT (target Đúng.docx) — {r['total']} passenger ===\n")
    print("[TUOI] stage : actual% (n) vs target%")
    for k, v in r['age_stage'].items():
        tg = v['target']
        print(f"  {k:8}: {v['pct']:>5}% ({v['n']:>2})   target {tg[0]}-{tg[1]}%")
    print(f"\n[CAI CHET] present: {r['death_types_present']}")
    print(f"[GIONG] region chua set: {r['voice_region_unset']}/{r['total']}")
    print(f"[SO NV/TAP] focal max/ep: {r['per_ep_focal_max']}  — {r['note_secondary_cast']}")
    print(f"\n=== {len(r['flags'])} FLAG LECH CAN BANG ===")
    for f in r['flags']:
        print(f"  ⚠ {f}")

    dv = diversity_report(reg)
    print("\n=== DIVERSITY (chong lap 100 tap) — distinct/filled (ratio) ===")
    for k, v in dv.items():
        warn = "  ⚠ DON DIEU/CHUA SET" if v['distinct'] <= 1 else ""
        print(f"  {k:14}: {v['distinct']:>3} distinct / {v['filled']:>3} filled  (ratio {v['ratio']}){warn}")


if __name__ == '__main__':
    main()
