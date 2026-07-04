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


def scan_id(n: int, files=None):
    """Return list of (file, line_num, line_text, format_name) for all matches.
    files=None -> quet BIBLE_FILES that; truyen list khac de test tren tmp copy."""
    hits = []
    patterns = [
        (f'top_level',  re.compile(rf'^R{n}_[a-zA-Z]')),
        (f'rule_prefix', re.compile(rf'^rule_R{n}_[a-zA-Z]')),   # bug 4/7: bible/00 dung
        # quy uoc "rule_R{N}_xxx:" cho 76/123 rule (vd rule_R142_kill_switch) — pattern
        # any_indent phia duoi VAN khop nhung scan_all()/check_staged() cu CHI dem
        # top_level+list_id la "definition" -> rule_prefix lot khoi dup-check hoan toan
        # (R142 dup that o bible/00 L2007+L2034 khong bi --all bat, chi --staged 1-ID bat).
        (f'any_indent', re.compile(rf'(?<![\dR])R{n}_[a-zA-Z]')),
        (f'list_id',    re.compile(rf'^\s*-\s*id:\s*R{n}\b')),
        (f'mention',    re.compile(rf'(?<![\d])R{n}(?![\d_])')),
    ]
    for bf in (files if files is not None else BIBLE_FILES):
        bf = Path(bf)
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


DEF_FORMATS = ('top_level', 'list_id', 'rule_prefix')


def scan_all(files=None) -> int:
    """Scan R40-R200 for duplicates."""
    duplicates = []
    for n in range(40, 201):
        hits = scan_id(n, files)
        # filter to "definition" hits (top_level/list_id/rule_prefix) — not just mentions
        defs = [h for h in hits if h[3] in DEF_FORMATS]
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
    # Patterns for ADDED lines defining new rule (bug 4/7: thieu rule_R{N}_ prefix ->
    # commit staged rule_R{N}_moi trung ID cu se lot qua pre-commit guard nay)
    add_top = re.compile(r'^\+R(\d+)_[a-zA-Z]', re.MULTILINE)
    add_rule_prefix = re.compile(r'^\+rule_R(\d+)_[a-zA-Z]', re.MULTILINE)
    add_list = re.compile(r'^\+\s*-\s*id:\s*R(\d+)\b', re.MULTILINE)
    added_ids = set()
    for m in add_top.finditer(diff): added_ids.add(int(m.group(1)))
    for m in add_rule_prefix.finditer(diff): added_ids.add(int(m.group(1)))
    for m in add_list.finditer(diff): added_ids.add(int(m.group(1)))

    if not added_ids:
        print('[OK] No new rule ID adds in staged diff')
        return 0

    # For each added ID, check if it collides with existing definitions OUTSIDE the staged additions
    fail = 0
    for n in sorted(added_ids):
        hits = scan_id(n)
        defs = [h for h in hits if h[3] in DEF_FORMATS]
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
