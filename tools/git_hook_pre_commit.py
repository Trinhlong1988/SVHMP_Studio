"""Pre-commit orchestrator (Python) — portable replacement for the bash hook.

deep-audit F1c (2/7): this machine runs MinGit (no bash.exe, no coreutils:
grep/sed/awk/date 'command not found'), so the old `#!/bin/bash` pre-commit
could not spawn -> enforcement INERT. This Python version runs on MinGit AND
full Git-for-Windows. .githooks/pre-commit is now a thin sh wrapper -> this.

Replicates the 4 sections of the original bash hook faithfully:
  A  R-ID conflict guard   (staged bible/00|05) -> check_rule_id_free.py --staged
  D  rule-mention codified guard               -> check_rule_mention_codified.py --staged
  C  mass-replace log guard (>=10 same removed) -> WARN if RENAME_LOG missing today
  B  R41 post_render_gate  (staged EP episode)  -> post_render_gate.py --ep N
Exit 1 = BLOCK commit (A/D/B fail). C is WARN-only. Never use --no-verify.
"""
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
PY = sys.executable


def _run(args):
    return subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=str(SVHMP))


def _tool(rel, *extra):
    return _run([PY, str(SVHMP / rel), *extra])


def staged_names():
    r = _run(["git", "diff", "--cached", "--name-only"])
    return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]


def main():
    names = staged_names()
    block = 0

    # SECTION A — R-ID conflict guard (only if staged bible/00 or 05 yaml)
    if any(re.match(r"^bible/0[05]_.*\.yaml$", n) for n in names):
        print("=== SVHMP R-ID CONFLICT GUARD ===")
        r = _tool("tools/check_rule_id_free.py", "--staged")
        sys.stdout.write(r.stdout)
        if r.returncode != 0:
            print("xxx R-ID CONFLICT — COMMIT BLOCKED (pick different R{N})")
            block = 1

    # SECTION D — rule-mention codified guard (always)
    print("=== SVHMP RULE MENTION GUARD ===")
    r = _tool("tools/check_rule_mention_codified.py", "--staged")
    sys.stdout.write(r.stdout + ("\n" if not r.stdout.endswith("\n") else ""))
    if r.returncode != 0:
        print("xxx RULE MENTION ORPHAN — COMMIT BLOCKED "
              "(claim 'R{N} codified' but bible/00 has no entry)")
        block = 1

    # SECTION C — mass-replace log guard (WARN only)
    r = _run(["git", "diff", "--cached", "--unified=0"])
    removed = [ln for ln in r.stdout.splitlines()
               if ln.startswith("-") and not ln.startswith("---")]
    dup = [(ln, c) for ln, c in Counter(removed).items() if c >= 10]
    if dup:
        print("=== SVHMP MASS-REPLACE GUARD ===")
        rename_log = SVHMP / "RENAME_LOG.md"
        today = date.today().isoformat()
        logged = rename_log.exists() and today in rename_log.read_text(
            encoding="utf-8", errors="replace")
        if not logged:
            print(f"  WARN: mass-replace (>=10 same lines removed) without "
                  f"RENAME_LOG.md entry for {today} — document via "
                  f"tools/log_rename.py (commit allowed).")

    # SECTION B — R41 post_render_gate (staged EP episode.md)
    eps = [n for n in names if re.match(r"^output/ep_[0-9]+/episode\.md$", n)]
    if eps:
        print("=== SVHMP R41 PRE-COMMIT GATE ===")
        for ep_file in eps:
            m = re.search(r"ep_0*([0-9]+)", ep_file)
            ep = m.group(1)
            g = _tool("tools/post_render_gate.py", "--ep", ep)
            total = ""
            for ln in g.stdout.splitlines():
                if "Total:" in ln:
                    total = ln.split("Total:")[-1].strip()
            if "0 FAIL" in total.replace(" ", " "):
                print(f"  OK EP{int(ep):02d}: {total}")
            else:
                print(f"  FAIL EP{int(ep):02d}: {total or '(no Total line)'}")
                for ln in g.stdout.splitlines():
                    if ln.strip().startswith("x") or "FAIL" in ln:
                        print("      " + ln.strip())
                block = 1

    if block:
        print("\nxxx COMMIT BLOCKED — fix above + git add + re-commit. "
              "Do NOT use --no-verify.")
        return 1
    print("OK pre-commit gate PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
