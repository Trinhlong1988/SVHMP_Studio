"""Log mass-replace decision tới RENAME_LOG.md.

Mr.Long lệnh 29/6: chặn vector "mass-replace decision không log".

Precedent đau: "Hắc Vỹ Dạ" → "Hắc Dạ Ký" revert mid-session, em CMD LEAD không
biết khi nào decision, ship LESSONS file outdated 16 phút.

Usage:
    python tools/log_rename.py <old> <new> "reason text"

Output: append entry vào RENAME_LOG.md root.
Pre-commit hook SECTION C detect mass-replace → require log entry.
"""
import sys
from datetime import datetime
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
LOG = SVHMP / "RENAME_LOG.md"


HEADER = """# RENAME LOG — mass-replace decisions

**Rule:** Mọi mass-replace (≥10 instances cùng word→word) trong repo PHẢI log đây
trước commit. Pre-commit hook SECTION C verify.

**Format:** `[YYYY-MM-DD HH:MM] OLD → NEW (N instances) | author | reason`

---

"""


def append(old, new, reason):
    if not LOG.exists():
        LOG.write_text(HEADER, encoding="utf-8")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    line = f"- `{ts}` **{old}** → **{new}** | author: CMD LEAD | reason: {reason}\n"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line)
    print(f"[LOGGED] {old} → {new}")
    print(f"  File: {LOG}")
    print(f"  Reason: {reason}")


def main():
    if len(sys.argv) < 4:
        print("Usage: python tools/log_rename.py <old> <new> \"reason text\"")
        return 2
    old = sys.argv[1]
    new = sys.argv[2]
    reason = " ".join(sys.argv[3:])
    append(old, new, reason)
    return 0


if __name__ == "__main__":
    sys.exit(main())
