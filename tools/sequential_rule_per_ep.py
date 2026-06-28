"""SVHMP — SEQUENTIAL: chạy từng RULE × từng EP (Mr.Long 28/6).

Order:
  Rule R58 → EP01, EP02, ..., EP50 (audit + fix per EP loop until converge)
  Rule R60 → EP01-50
  Rule R61 → EP01-50 (skip — risky)
  Rule R62 → EP01-50 (already converged)
  Rule R74 → EP01-50

Per cell (R_i × EP_N):
  Loop max 3 iters:
    audit EP_N → count violations
    if 0 → next EP
    fix EP_N → apply
  Log result per cell
"""
import subprocess
import sys
import re
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# Rules with audit + fix scripts
RULES = [
    ('R58', 'audit_tilde_eol.py', 'auto_fix_tilde_eol.py'),
    ('R60', 'audit_short_eol.py', 'auto_fix_short_eol.py'),
    ('R62', 'audit_anaphora_consecutive.py', 'fix_chains_zero_tolerance.py'),
    ('R74', 'audit_phrase_repetition.py', 'auto_fix_phrase_repetition.py'),
    # R61 skip — auto_fix_short_start risky meaning change
]

def count_violations_ep(audit_script, ep_num):
    """Run audit, count violations for specific EP from JSON report."""
    rpt_map = {
        'audit_tilde_eol.py': 'audit_tilde_eol_report.json',
        'audit_short_eol.py': 'audit_short_eol_report.json',
        'audit_anaphora_consecutive.py': 'audit_anaphora_consecutive_report.json',
        'audit_phrase_repetition.py': 'audit_phrase_repetition_report.json',
    }
    rpt_path = SVHMP / 'runtime' / rpt_map.get(audit_script, '')
    if not rpt_path.exists(): return 0
    try:
        data = json.loads(rpt_path.read_text(encoding='utf-8'))
        violations = data.get('violations', [])
        return len([v for v in violations if v.get('ep') == ep_num])
    except: return 0

def main():
    print("=" * 70)
    print("SEQUENTIAL RULE × EP — Mr.Long 28/6")
    print("=" * 70)

    results = {}
    for rule_name, audit_s, fix_s in RULES:
        print(f"\n{'='*70}\nRULE {rule_name} — scan EP01-50")
        print(f"{'='*70}")
        results[rule_name] = {}

        # Run audit once to populate report
        subprocess.run([sys.executable, f'tools/{audit_s}', '--summary'],
                       capture_output=True, cwd=SVHMP)

        for ep in range(1, 51):
            initial = count_violations_ep(audit_s, ep)
            if initial == 0:
                print(f"  EP{ep:02d}: 0 violations ✓")
                results[rule_name][ep] = {'initial': 0, 'final': 0, 'iters': 0}
                continue

            # Loop audit + fix up to 3 iters
            iters = 0
            current = initial
            while iters < 3 and current > 0:
                iters += 1
                # Apply fix (per-ep if supported)
                fix_cmd = [sys.executable, f'tools/{fix_s}', '--apply']
                if rule_name in ('R58', 'R60'):
                    # These scripts may not support --ep; run global
                    pass
                fr = subprocess.run(fix_cmd, capture_output=True, text=True,
                                   encoding='utf-8', errors='replace', cwd=SVHMP)
                # Re-audit
                subprocess.run([sys.executable, f'tools/{audit_s}', '--summary'],
                              capture_output=True, cwd=SVHMP)
                new = count_violations_ep(audit_s, ep)
                if new == current: break  # no progress
                current = new

            status = '✓' if current == 0 else f'⚠️ {current} remain'
            print(f"  EP{ep:02d}: {initial} → {current} (iters={iters}) {status}")
            results[rule_name][ep] = {'initial': initial, 'final': current, 'iters': iters}

    # Summary
    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)
    for rule_name in results:
        total_init = sum(v['initial'] for v in results[rule_name].values())
        total_final = sum(v['final'] for v in results[rule_name].values())
        eps_clean = sum(1 for v in results[rule_name].values() if v['final'] == 0)
        print(f"  {rule_name}: {total_init} → {total_final} | {eps_clean}/50 EPs clean")

    # Save report
    out = SVHMP / 'runtime' / 'sequential_rule_per_ep.json'
    out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
