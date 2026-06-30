"""Check rule mention codified — scan staged diff for `R{N} codified` claims,
verify bible/00 actually has rule R{N}. BLOCK commit if mismatch (test-orphan).

Mr.Long lệnh 30/6: chặn cứng pattern CMD #2 báo "codified" mà KHÔNG flush bible.
Precedent: R110-R172 (14 rules overnight) + R175-R180 (5 rules sáng) = 19 orphan.

Usage:
    python tools/check_rule_mention_codified.py --staged    # pre-commit mode
    python tools/check_rule_mention_codified.py --file PING_CMD_LEAD_29_06.md
"""
import re
import subprocess
import sys
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
BIBLE = SVHMP / "bible" / "00_constitution.yaml"


def codified_in_bible(n):
    if not BIBLE.exists():
        return False
    text = BIBLE.read_text(encoding="utf-8")
    pats = [rf"^R{n}_[a-zA-Z]", rf"^\s*-\s*id:\s*R{n}\b"]
    return any(re.search(p, text, re.MULTILINE) for p in pats)


def extract_claims(text):
    """Find all 'R{N} codified' / 'codified R{N}' / 'R{N}_codified' patterns."""
    claims = set()
    for pat in [
        r"R(\d+)\s+codif",
        r"codif\w*\s+R(\d+)",
        r"R(\d+)\s+ship",
        r"ship\s+R(\d+)",
        r"\bRule\s+new[^.]*R(\d+)",
        r"\b(\d+)\s+(?:rule|rules)\s+R(\d+)[-–]R(\d+)",
    ]:
        for m in re.finditer(pat, text, re.IGNORECASE):
            for g in m.groups():
                if g and g.isdigit():
                    n = int(g)
                    if 40 <= n <= 250:
                        claims.add(n)
    return claims


def check_staged():
    """Scan staged diff for added lines containing rule codified claims."""
    r = subprocess.run(
        ["git", "diff", "--cached", "--unified=0"],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=SVHMP,
    )
    diff = r.stdout
    # Only added lines (start with + but not +++)
    added = "\n".join(line[1:] for line in diff.split("\n")
                      if line.startswith("+") and not line.startswith("+++"))
    claims = extract_claims(added)
    if not claims:
        return 0, "No 'R{N} codified' claims in staged diff"
    missing = sorted(n for n in claims if not codified_in_bible(n))
    found = sorted(n for n in claims if codified_in_bible(n))
    if not missing:
        return 0, f"All {len(claims)} rule claims verified in bible/00: {found}"
    return 1, f"ORPHAN: {len(missing)}/{len(claims)} rule claim(s) NOT in bible/00: R{missing}\n  (Codified OK: R{found})"


def check_file(path):
    p = Path(path)
    if not p.exists():
        print(f"[ERR] {path} not found")
        return 2
    text = p.read_text(encoding="utf-8", errors="replace")
    claims = extract_claims(text)
    missing = sorted(n for n in claims if not codified_in_bible(n))
    print(f"Rule mentions in {path}: {len(claims)}")
    print(f"Codified bible/00: {len(claims) - len(missing)}")
    print(f"Missing (orphan): {len(missing)}")
    if missing:
        print(f"  → R{missing}")
        return 1
    return 0


def main():
    if "--staged" in sys.argv:
        code, msg = check_staged()
        print(msg)
        return code
    if "--file" in sys.argv:
        i = sys.argv.index("--file")
        return check_file(sys.argv[i + 1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
