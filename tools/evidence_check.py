"""SVHMP — EVIDENCE STANDARD GATE (PACK2 07, Boss 2/7).
Chan report THIEU bang chung: moi report BAT BUOC co
commit hash / branch / commands / PASS-FAIL matrix / verdict / exit code.
Thieu bat ky -> exit 1 (report VO HIEU). Dung: `python tools/auditor.py | python tools/evidence_check.py`.
"""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# field -> regex chung minh su ton tai trong report
REQUIRED = {
    'commit_hash': r'[0-9a-f]{7,40}',
    'branch': r'(?i)branch',
    'commands': r'(?i)command',
    'pass_fail_matrix': r'(?i)\b(PASS|FAIL)\b',
    'verdict': r'(?i)(SHIP|BLOCK_SHIP|verdict)',
    'exit_code': r'(?i)exit',
}


def missing_fields(text):
    """-> danh sach field thieu (rong = du bang chung). Tach ra de test R213."""
    text = text or ''
    return [k for k, pat in REQUIRED.items() if not re.search(pat, text)]


def main():
    if len(sys.argv) > 1:
        text = Path(sys.argv[1]).read_text(encoding='utf-8')
    else:
        text = sys.stdin.read()
    miss = missing_fields(text)
    if miss:
        print(f"[EVIDENCE FAIL] report THIEU {len(miss)} truong: {miss}")
        print("=== BLOCK (report vo hieu) ===")
        sys.exit(1)
    print("[EVIDENCE OK] du 6 truong bang chung.  === PASS ===")
    sys.exit(0)


if __name__ == '__main__':
    main()
