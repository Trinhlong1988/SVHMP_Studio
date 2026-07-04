"""G4 WORLD CHECK v1.0.0 — GATE 1 CUA cho G4 World/Timeline/Event (TASK_G4_WORLD D5).

Mirror pattern tools/blueprint_suite_check.py (BP5): GOI tuan tu cac checker con
qua subprocess, in matrix PASS/FAIL, KHONG short-circuit (chay het roi moi ket
luan), exit 0 CHI KHI tat ca xanh.

  D1  tools/timeline_check.py         (timeline engine + M1 arithmetic + M4 lunar WARN)
  D2  tools/event_ledger_miner.py     (mine that — da duoc D1 goi ben trong, chay
                                       doc lap o day de dam bao CHINH mine cung PASS
                                       khong phu thuoc D1 wrap)
  D4  tools/story_consistency_validator.py  (self-test — sanity check module import
                                       + ham thuan chay duoc, KHONG crash)
  D3  governance/proposals/fact_ledger_schema.yaml (ton tai — de xuat cho Mr.Long ky)

Exit 0 = tat ca tang PASS, exit 1 = >=1 tang FAIL.
"""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable

__version__ = '1.0.0'

SUITE = [
    ('D1_timeline', 'tools/timeline_check.py'),
    ('D2_event_ledger', 'tools/event_ledger_miner.py'),
    ('D4_story_consistency', 'tools/story_consistency_validator.py'),
]
D3_PROPOSAL = REPO / 'governance' / 'proposals' / 'fact_ledger_schema.yaml'


def run_suite():
    """Chay tuan tu cac stage script; KHONG short-circuit (chay het roi moi ket luan)."""
    rows = []
    for key, rel in SUITE:
        r = subprocess.run([PY, str(REPO / rel)], capture_output=True, text=True, encoding='utf-8')
        rows.append({'key': key, 'script': rel, 'rc': r.returncode,
                    'tail': ((r.stdout or '') + (r.stderr or ''))[-500:]})
    d3_ok = D3_PROPOSAL.exists()
    rows.append({'key': 'D3_fact_ledger_proposal', 'script': str(D3_PROPOSAL.relative_to(REPO)),
                'rc': 0 if d3_ok else 1,
                'tail': '' if d3_ok else 'FILE KHONG TON TAI'})
    return rows


def main():
    print(f'=== G4 WORLD CHECK v{__version__} (D5 — 1 cua) ===')
    rows = run_suite()
    fails = [row for row in rows if row['rc'] != 0]
    for row in rows:
        mark = 'PASS' if row['rc'] == 0 else 'FAIL'
        print(f"  [{mark}] {row['key']:<24} {row['script']} (exit {row['rc']})")
        if row['rc'] != 0:
            print(row['tail'])
    if fails:
        print(f"=== FAIL — {len(fails)}/{len(rows)} tầng đỏ: "
              f"{', '.join(row['key'] for row in fails)} ===")
        return 1
    print(f'=== PASS — {len(rows)}/{len(rows)} tầng G4 xanh ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
