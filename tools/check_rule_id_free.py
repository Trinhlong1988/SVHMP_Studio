"""Check rule ID free across bible/*.yaml (4-format hardlock).

Usage:
    python tools/check_rule_id_free.py <N>        — check 1 ID
    python tools/check_rule_id_free.py --all      — scan ALL R-numbers, report duplicates
    python tools/check_rule_id_free.py --staged   — pre-commit mode: scan staged diff for new R{N} adds

Exit codes:
    0 — free / no collision
    1 — collision detected (BLOCK)
    2 — usage error

Why exists:
    CMD LEAD (Claude Opus 4.7) vi phạm 3 lần trong session 29/6 — grep `^R91` narrow
    miss list format `- id: R91` → duplicate rename. Memory feedback_no_grep_assumption.md
    save lesson nhưng KHÔNG tự apply → cần tool hardlock force 4-format check.

4 formats checked:
    1. ^R{N}_xxx:           (top-level key)
    2. R{N}_xxx anywhere    (any indent)
    3. id: R{N}             (list format under workflow_section)
    4. R{N}\\b              (any mention not prefix-attached)
"""
import re
import sys
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
BIBLE_FILES = [
    SVHMP / 'bible' / '00_constitution.yaml',
    SVHMP / 'bible' / '05_audio_bible.yaml',
]


def scan_id(n: int):
    """Return list of (file, line_num, line_text, format_name) for all matches."""
    hits = []
    patterns = [
        (f'top_level',  re.compile(rf'^R{n}_[a-zA-Z]')),
        (f'any_indent', re.compile(rf'(?<![\dR])R{n}_[a-zA-Z]')),
        (f'list_id',    re.compile(rf'^\s*-\s*id:\s*R{n}\b')),
        (f'mention',    re.compile(rf'(?<![\d])R{n}(?![\d_])')),
    ]
    for bf in BIBLE_FILES:
        if not bf.exists(): continue
        lines = bf.read_text(encoding='utf-8').split('\n')
        for lnum, line in enumerate(lines, 1):
            for fname, pat in patterns:
                if pat.search(line):
                    hits.append((bf.name, lnum, line.strip()[:100], fname))
                    break  # 1 line ≤ 1 hit
    return hits


def check_single(n: int) -> int:
    hits = scan_id(n)
    if not hits:
        print(f'[OK] R{n} FREE — no occurrence in 4 formats')
        return 0
    print(f'[COLLISION] R{n} occupied — {len(hits)} hit(s):')
    for fname, lnum, text, fmt in hits:
        print(f'  {fname}:{lnum} ({fmt}) {text}')
    return 1


def scan_all() -> int:
    """Scan R40-R200 for duplicates."""
    duplicates = []
    for n in range(40, 201):
        hits = scan_id(n)
        # filter to "definition" hits (top_level or list_id) — not just mentions
        defs = [h for h in hits if h[3] in ('top_level', 'list_id')]
        if len(defs) > 1:
            duplicates.append((n, defs))
    if not duplicates:
        print('[OK] No rule ID duplicates R40-R200')
        return 0
    print(f'[FAIL] {len(duplicates)} duplicate(s):')
    for n, defs in duplicates:
        print(f'  R{n}:')
        for fname, lnum, text, fmt in defs:
            print(f'    {fname}:{lnum} ({fmt}) {text}')
    return 1


def check_staged() -> int:
    """Pre-commit mode: parse staged diff for `+R{N}_` or `+ - id: R{N}` adds."""
    r = subprocess.run(['git', 'diff', '--cached', '--unified=0', '--',
                        'bible/00_constitution.yaml', 'bible/05_audio_bible.yaml'],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', cwd=SVHMP, creationflags=CREATE_NO_WINDOW)
    diff = r.stdout
    # Patterns for ADDED lines defining new rule
    add_top = re.compile(r'^\+R(\d+)_[a-zA-Z]', re.MULTILINE)
    add_list = re.compile(r'^\+\s*-\s*id:\s*R(\d+)\b', re.MULTILINE)
    added_ids = set()
    for m in add_top.finditer(diff): added_ids.add(int(m.group(1)))
    for m in add_list.finditer(diff): added_ids.add(int(m.group(1)))

    if not added_ids:
        print('[OK] No new rule ID adds in staged diff')
        return 0

    # For each added ID, check if it collides with existing definitions OUTSIDE the staged additions
    fail = 0
    for n in sorted(added_ids):
        hits = scan_id(n)
        defs = [h for h in hits if h[3] in ('top_level', 'list_id')]
        if len(defs) > 1:
            fail += 1
            print(f'[BLOCK] R{n} CONFLICT — {len(defs)} definitions:')
            for fname, lnum, text, fmt in defs:
                print(f'  {fname}:{lnum} ({fmt}) {text}')

    if fail:
        print(f'\n[PRE-COMMIT BLOCK] {fail} rule ID conflict(s) — pick different ID')
        print('  Run: python tools/check_rule_id_free.py <N>  to verify free slot')
        return 1
    print(f'[OK] {len(added_ids)} new rule ID(s) all unique: {sorted(added_ids)}')
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    arg = sys.argv[1]
    if arg == '--all':
        return scan_all()
    if arg == '--staged':
        return check_staged()
    try:
        n = int(arg)
    except ValueError:
        print(f'[ERR] Invalid argument: {arg}')
        return 2
    return check_single(n)


if __name__ == '__main__':
    sys.exit(main())
