"""SVHMP — SEQUENTIAL EP × RULE FULL AUTO (Mr.Long 28/6).

Order theo Mr.Long:
  EP01 → R58 → R60 → R61 → R62 → R74 (all rules)
  EP02 → R58 → R60 → R61 → R62 → R74
  ...
  EP50 → R58 → R60 → R61 → R62 → R74

Per cell (EP_N × R_i):
  audit → count violations
  if > 0: fix → re-audit
  log

Extendable: thêm rule mới vào RULES list.
"""
import subprocess
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

RULES = [
    ('R58', 'audit_tilde_eol.py', 'auto_fix_tilde_eol.py', 'audit_tilde_eol_report.json'),
    ('R60', 'audit_short_eol.py', 'auto_fix_short_eol.py', 'audit_short_eol_report.json'),
    ('R62', 'audit_anaphora_consecutive.py', 'fix_chains_zero_tolerance.py', 'audit_anaphora_consecutive_report.json'),
    ('R74', 'audit_phrase_repetition.py', 'auto_fix_phrase_repetition.py', 'audit_phrase_repetition_report.json'),
]

def count_violations_ep(rpt_name, ep):
    p = SVHMP / 'runtime' / rpt_name
    if not p.exists(): return 0
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        return len([v for v in data.get('violations', []) if v.get('ep') == ep])
    except: return 0

def audit_then_count(audit_s, rpt, ep):
    subprocess.run([sys.executable, f'tools/{audit_s}', '--summary'],
                   capture_output=True, cwd=SVHMP, timeout=60)
    return count_violations_ep(rpt, ep)

def main():
    print("=" * 75)
    print("SEQUENTIAL FULL AUTO — EP × RULE (Mr.Long 28/6)")
    print(f"Order: EP01 → {' → '.join(r[0] for r in RULES)} → EP02 → ...")
    print("=" * 75)

    results = {}
    grand_total_init = 0
    grand_total_final = 0

    for ep in range(1, 51):
        ep_results = {}
        ep_total_init = 0
        ep_total_final = 0
        for rule_name, audit_s, fix_s, rpt in RULES:
            initial = audit_then_count(audit_s, rpt, ep)
            if initial > 0:
                # Apply fix
                subprocess.run([sys.executable, f'tools/{fix_s}', '--apply'],
                              capture_output=True, cwd=SVHMP, timeout=120)
                final = audit_then_count(audit_s, rpt, ep)
            else:
                final = 0
            ep_results[rule_name] = (initial, final)
            ep_total_init += initial
            ep_total_final += final

        results[ep] = ep_results
        grand_total_init += ep_total_init
        grand_total_final += ep_total_final

        # Log per EP
        cells = ' '.join(f'{r}:{v[0]}→{v[1]}' for r, v in ep_results.items())
        status = '✓' if ep_total_final == 0 else f'⚠️ {ep_total_final}'
        print(f"EP{ep:02d} | {cells} | total {ep_total_init}→{ep_total_final} {status}")

    print("\n" + "=" * 75)
    print(f"GRAND TOTAL: {grand_total_init} → {grand_total_final}")
    clean = sum(1 for ep in results.values() if sum(v[1] for v in ep.values()) == 0)
    print(f"CLEAN EPs (all rules 0): {clean}/50")

    out = SVHMP / 'runtime' / 'sequential_full_auto.json'
    out.write_text(json.dumps({
        'order': 'EP × RULE',
        'rules': [r[0] for r in RULES],
        'grand_init': grand_total_init,
        'grand_final': grand_total_final,
        'clean_eps': clean,
        'results': {str(k): v for k, v in results.items()},
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
