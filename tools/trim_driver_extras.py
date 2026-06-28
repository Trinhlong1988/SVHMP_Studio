"""SVHMP — Trim bác tài extra quotes (R55 + R42 strict).

Rule: Bác tài quote chỉ allowed:
- 2 standard: "Con đã nhớ ra chưa?" / "Chưa tới lúc."
- 1 foreshadow in CLIFFHANGER (R42)
- Milestone EPs allow +1 extra

Script:
1. Identify CLIFFHANGER section
2. Outside CLIFFHANGER: remove extra bác tài quotes (keep only standard 2)
3. Inside CLIFFHANGER: allow max 1 foreshadow quote

CAUTION: Conservative — only delete if quote clearly identifiable as bác tài speaker.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

STANDARD = {'Con đã nhớ ra chưa?', 'Chưa tới lúc.'}
MILESTONES = {1, 10, 20, 30, 40, 50, 60, 70, 73, 80, 90}

def trim_ep(ep_num, dry_run=False):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists():
        return 0
    text = p.read_text(encoding='utf-8')

    # Skip golden EP01-10
    if ep_num <= 10:
        return 0

    # Split into sections
    cliffhanger_start = text.find('# CLIFFHANGER')
    if cliffhanger_start == -1:
        cliffhanger_start = text.find('## 6. CLIFFHANGER')
    if cliffhanger_start == -1:
        return 0

    before_cliff = text[:cliffhanger_start]
    cliff = text[cliffhanger_start:]

    # In BEFORE_CLIFFHANGER, find pattern: "Bác tài [verb]\n\n\"non-standard quote\"\n\n[content]"
    # Conservative: remove if quote is non-standard AND not crucial
    # Pattern to remove: paragraph with "Bác tài [foreshadow verb]" + immediate quote that's non-standard
    # SKIP this aggressive removal — risk content loss

    # Instead: just trim the foreshadow line that em added in many EPs as extra
    # Pattern: "Bác tài liếc gương\..*?\"[^\"]+\"\\s*\\n\\s*\\n[A-Z]" where quote is foreshadow type
    # → Remove the bác tài line entirely

    changes = 0
    # Only remove extras in EP11-50, non-milestone
    if ep_num not in MILESTONES:
        # Pattern: lone "Bác tài liếc gương\..*\"Đêm thứ.*?\"" outside CLIFFHANGER
        # Remove these foreshadow lines that em accidentally placed outside CLIFFHANGER
        pattern = re.compile(
            r'Bác tài liếc gương\.\s*"Đêm thứ[^"]+"\s*\n\s*\n(?=[A-ZĐ])',
            re.DOTALL
        )
        new_before, n = pattern.subn('', before_cliff)
        if n:
            changes += n
            before_cliff = new_before

    text = before_cliff + cliff

    if changes > 0 and not dry_run:
        p.write_text(text, encoding='utf-8')
        print(f"  EP{ep_num:02d}: {changes} trim")
    return changes

def main():
    total = 0
    for n in range(11, 51):
        c = trim_ep(n)
        total += c
    print(f"\nTotal trim: {total}")

if __name__ == '__main__':
    main()
