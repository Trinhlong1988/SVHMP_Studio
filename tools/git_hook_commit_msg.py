"""commit-msg orchestrator (Python) — portable replacement for the bash hook.

deep-audit F1c (2/7): MinGit has no bash/coreutils, so the #!/bin/bash
commit-msg (grep/cat/sort) could not spawn. Same guard, in Python.

Round 19.27 rule: block commit whose MESSAGE claims a rule codified/locked/
shipped/added (ghi/wrote) when bible/00 has no `rule_R{N}_...` entry.
Usage: git_hook_commit_msg.py <path-to-commit-msg-file>. Exit 1 = BLOCK.
"""
import re
import sys
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
BIBLE = SVHMP / "bible" / "00_constitution.yaml"

VERBS = r"(?:ghi|codify|codified|add|added|locked|shipped|wrote)"
PATS = [
    re.compile(rf"{VERBS}\s+R(\d+)[a-z]?", re.IGNORECASE),
    re.compile(rf"R(\d+)[a-z]?\s+{VERBS}", re.IGNORECASE),
]


def main():
    if len(sys.argv) < 2:
        return 0
    msg = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
    ids = set()
    for pat in PATS:
        for m in pat.finditer(msg):
            ids.add(int(m.group(1)))
    if not ids:
        return 0
    print("=== COMMIT-MSG GUARD (Round 19.27) ===")
    print(f"Mentioned in commit msg: R{sorted(ids)}")
    bible = BIBLE.read_text(encoding="utf-8", errors="replace") if BIBLE.exists() else ""
    missing = sorted(n for n in ids
                     if not re.search(rf"(?im)^rule_R{n}_", bible))
    if missing:
        print("xxx COMMIT BLOCKED (Round 19.27): message claims rule(s) "
              "codified but bible/00 has no rule_R{N}_ entry:")
        for n in missing:
            print(f"    x R{n}")
        print("Fix: (a) codify into bible/00, OR (b) remove the claim from "
              "the message. Do NOT use --no-verify.")
        return 1
    print("OK all mentioned R-IDs verified in bible/00")
    return 0


if __name__ == "__main__":
    sys.exit(main())
