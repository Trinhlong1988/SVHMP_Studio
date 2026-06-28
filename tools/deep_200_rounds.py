"""SVHMP — 200 vòng sâu (Mr.Long 28/6).

Mỗi vòng = 1 sweep:
- Run 5 audits all 50 EPs
- Apply 5 auto-fixes
- Log delta

Early-stop nếu 5 vòng liên tiếp KHÔNG có thay đổi.
"""
import subprocess
import sys
import json
import re
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

RULES = [
    ('R58', 'audit_tilde_eol.py', 'auto_fix_tilde_eol.py'),
    ('R60', 'audit_short_eol.py', 'auto_fix_short_eol.py'),
    ('R61', 'audit_short_start.py', None),  # no auto-fix
    ('R62', 'audit_anaphora_consecutive.py', 'fix_chains_zero_tolerance.py'),
    ('R74', 'audit_phrase_repetition.py', 'auto_fix_phrase_repetition.py'),
]

def audit_count(audit_script):
    """Run audit, return total violation count."""
    r = subprocess.run([sys.executable, f'tools/{audit_script}', '--summary'],
                      capture_output=True, text=True, encoding='utf-8', errors='replace',
                      cwd=SVHMP, timeout=120)
    m = re.search(r'SUMMARY:?\s*(\d+)\s*HIGH', r.stdout)
    return int(m.group(1)) if m else 0

def apply_fix(fix_script):
    if not fix_script: return 0
    r = subprocess.run([sys.executable, f'tools/{fix_script}', '--apply'],
                      capture_output=True, text=True, encoding='utf-8', errors='replace',
                      cwd=SVHMP, timeout=120)
    # Extract change count
    for pat in [r'Total:\s*(\d+)', r'fixes=(\d+)', r'(\d+)\s*changes?\s*in']:
        m = re.search(pat, r.stdout)
        if m: return int(m.group(1))
    return 0

def main():
    MAX_ROUNDS = 200
    EARLY_STOP_NO_CHANGE = 5

    log_file = SVHMP / 'runtime' / 'deep_200_rounds.log'
    rounds_data = []
    no_change_streak = 0

    print("=" * 70)
    print("DEEP 200 ROUNDS — SVHMP_Studio (Mr.Long 28/6)")
    print(f"Rules: {[r[0] for r in RULES]} | Max: {MAX_ROUNDS} rounds | Early-stop: {EARLY_STOP_NO_CHANGE} no-change")
    print("=" * 70)

    for round_n in range(1, MAX_ROUNDS + 1):
        # Snapshot before round
        before = {rule: audit_count(audit) for rule, audit, _ in RULES}
        before_total = sum(before.values())

        # Apply all fixes
        changes_per_rule = {}
        for rule, _, fix in RULES:
            changes_per_rule[rule] = apply_fix(fix)
        total_changes = sum(changes_per_rule.values())

        # Snapshot after
        after = {rule: audit_count(audit) for rule, audit, _ in RULES}
        after_total = sum(after.values())

        delta = before_total - after_total
        rounds_data.append({
            'round': round_n,
            'before': before,
            'after': after,
            'changes': changes_per_rule,
            'delta': delta,
        })

        line = f"Round {round_n:3d} | before={before_total:4d} after={after_total:4d} delta={delta:+3d} | " + \
               ' '.join(f"{r}={after[r]}" for r in [x[0] for x in RULES])
        print(line)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {line}\n")

        if delta == 0 and total_changes == 0:
            no_change_streak += 1
        else:
            no_change_streak = 0

        if no_change_streak >= EARLY_STOP_NO_CHANGE:
            print(f"\n⏸️ Early stop — {EARLY_STOP_NO_CHANGE} rounds no change")
            break

    # Final summary
    print(f"\n{'='*70}")
    print(f"DEEP 200 ROUNDS COMPLETE — {len(rounds_data)} rounds run")
    print(f"{'='*70}")
    initial = rounds_data[0]['before']
    final = rounds_data[-1]['after']
    for rule in [r[0] for r in RULES]:
        print(f"  {rule}: {initial[rule]} → {final[rule]}")

    out = SVHMP / 'runtime' / 'deep_200_rounds_report.json'
    out.write_text(json.dumps({
        'total_rounds': len(rounds_data),
        'initial': initial,
        'final': final,
        'rounds': rounds_data,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")
    print(f"Log:    {log_file}")

if __name__ == '__main__':
    main()
