"""SVHMP — 200 vòng FULL ALL RULES (Mr.Long 28/6).

20+ audit scripts cover R40-R74 + extended dims.

Each round:
- Run ALL audits → count violations
- Trigger fix scripts available
- Log delta

Early-stop nếu 5 vòng KHÔNG có thay đổi.
"""
import subprocess
import sys
import json
import re
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# All audit + fix mapping
AUDITS = [
    # (label, audit_script, fix_script_or_None)
    ('R58_tilde_eol',         'audit_tilde_eol.py',              'auto_fix_tilde_eol.py'),
    ('R60_short_eol',         'audit_short_eol.py',              'auto_fix_short_eol.py'),
    ('R61_short_start',       'audit_short_start.py',            None),
    ('R62_anaphora',          'audit_anaphora_consecutive.py',   'fix_chains_zero_tolerance.py'),
    ('R68_R73_combined',      'audit_r68_to_r73.py',             None),
    ('R74_phrase_repeat',     'audit_phrase_repetition.py',      'auto_fix_phrase_repetition.py'),
    ('aesthetic_5_subdim',    'audit_aesthetic_5_subdim.py',     None),
    ('bimodal_sentence',      'audit_bimodal_sentence.py',       None),
    ('continuity_cross_ep',   'audit_continuity_cross_ep.py',    None),
    ('dialogue_hierarchy',    'audit_dialogue_hierarchy.py',     None),
    ('hidden_bugs',           'audit_hidden_bugs.py',            None),
    ('ngan_opening',          'audit_ngan_opening_template.py',  None),
    ('pronoun_pov',           'audit_pronoun_pov.py',            None),
    ('story_mode',            'audit_story_mode.py',             None),
    ('style_stats',           'audit_style_stats.py',            None),
]

def audit_count(audit_script):
    """Run audit, parse violation count."""
    r = subprocess.run([sys.executable, f'tools/{audit_script}', '--summary'],
                      capture_output=True, text=True, encoding='utf-8', errors='replace',
                      cwd=SVHMP, timeout=180)
    # Try multiple patterns
    for pat in [r'SUMMARY:?\s*(\d+)\s*HIGH', r'Total:\s*(\d+)', r'Total\s+violations?:\s*(\d+)',
                r'(\d+)\s*HIGH\s*violations']:
        m = re.search(pat, r.stdout)
        if m: return int(m.group(1))
    return 0

def apply_fix(fix_script):
    if not fix_script: return 0
    r = subprocess.run([sys.executable, f'tools/{fix_script}', '--apply'],
                      capture_output=True, text=True, encoding='utf-8', errors='replace',
                      cwd=SVHMP, timeout=180)
    for pat in [r'Total:\s*(\d+)', r'fixes=(\d+)', r'(\d+)\s*changes?\s*in', r'(\d+)\s*phrase\s*fixes']:
        m = re.search(pat, r.stdout)
        if m: return int(m.group(1))
    return 0

def main():
    MAX_ROUNDS = 200
    EARLY_STOP = 5
    log_file = SVHMP / 'runtime' / 'deep_200_all_rules.log'
    rounds_data = []
    no_change = 0

    print("=" * 100)
    print(f"DEEP 200 ROUNDS — ALL {len(AUDITS)} AUDITS (Mr.Long 28/6 'tất cả rule')")
    print("=" * 100)

    for round_n in range(1, MAX_ROUNDS + 1):
        before = {label: audit_count(audit) for label, audit, _ in AUDITS}
        before_total = sum(before.values())

        # Apply available fixes
        changes = sum(apply_fix(fix) for _, _, fix in AUDITS if fix)

        after = {label: audit_count(audit) for label, audit, _ in AUDITS}
        after_total = sum(after.values())
        delta = before_total - after_total

        rounds_data.append({
            'round': round_n,
            'before_total': before_total,
            'after_total': after_total,
            'delta': delta,
            'fixes_applied': changes,
            'before': before,
            'after': after,
        })

        ts = datetime.now().strftime('%H:%M:%S')
        line = f"[{ts}] Round {round_n:3d} | before={before_total:5d} after={after_total:5d} delta={delta:+4d} fixes={changes:3d}"
        print(line)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{line}\n")
            # Per-rule line
            f.write(f"          " + " | ".join(f"{k.split('_')[0]}={v}" for k,v in after.items()) + "\n")

        if delta == 0 and changes == 0:
            no_change += 1
        else:
            no_change = 0

        if no_change >= EARLY_STOP:
            print(f"\n⏸️ Early stop — {EARLY_STOP} rounds no change")
            break

    # Final
    print(f"\n{'='*100}")
    print(f"DONE — {len(rounds_data)} rounds")
    print(f"{'='*100}")
    initial = rounds_data[0]['before']
    final = rounds_data[-1]['after']
    print(f"{'Rule':<25} {'Initial':>10} {'Final':>10} {'Δ':>8}")
    for label in [a[0] for a in AUDITS]:
        ini = initial[label]
        fin = final[label]
        d = ini - fin
        marker = '✓' if fin == 0 else ('↓' if d > 0 else '·')
        print(f"{label:<25} {ini:>10} {fin:>10} {d:>+7}  {marker}")
    print(f"{'TOTAL':<25} {sum(initial.values()):>10} {sum(final.values()):>10} {sum(initial.values()) - sum(final.values()):>+7}")

    out = SVHMP / 'runtime' / 'deep_200_all_rules.json'
    out.write_text(json.dumps({
        'rounds_run': len(rounds_data),
        'initial': initial,
        'final': final,
        'rounds': rounds_data,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
