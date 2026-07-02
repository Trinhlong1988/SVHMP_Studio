"""Verify PING claim — auto-cross-check claim từ PING với FACT từ repo.

Mr.Long lệnh 29/6: chặn vector "trust PING không verify" — em catch 5 lần
CMD #2 report không khớp factual trong session 29/6.

Usage:
    python tools/verify_ping_claim.py "R109 codified"
    python tools/verify_ping_claim.py "STAGE 3 6/6 PASS"
    python tools/verify_ping_claim.py "Pipeline v77"
    python tools/verify_ping_claim.py --recent 20    # verify 20 events latest PING

Exit codes:
    0 — VERIFIED (claim khớp FACT)
    1 — FAILED (claim sai)
    2 — UNKNOWN (chưa parse được claim type)

Claim patterns detected:
    - "R{N} codified" → grep 4-format bible/00 + bible/05
    - "X rules R{a}-R{b}" → count actual range
    - "STAGE 3 {n}/6 PASS" → run qa_post_render per section
    - "EP{N} R86 PASS" → run qa_eol_diacritic
    - "Pipeline v{N}" → grep version in svhmp_v13_render.py
    - "Section X rendered" → check wav exists
    - "Commit {hash}" → git show
"""
import re
import subprocess
import sys
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent

# Result colors / markers
VERIFIED = "[VERIFIED]"
FAILED = "[FAILED]"
UNKNOWN = "[UNKNOWN]"


def run(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          cwd=SVHMP, timeout=timeout)
        return r.stdout, r.returncode
    except Exception as e:
        return f"[ERR] {e}", -1


# ---- VERIFIERS per claim type ----

def verify_rule_codified(n):
    """Verify R{n} codified bible/00 OR bible/05 (4-format)."""
    files = ["bible/00_constitution.yaml", "bible/05_audio_bible.yaml"]
    hits = []
    for f in files:
        p = SVHMP / f
        if not p.exists(): continue
        text = p.read_text(encoding="utf-8")
        for fmt, pat in [
            ("top_level", rf"^R{n}_[a-zA-Z]"),
            ("list_id", rf"^\s*-\s*id:\s*R{n}\b"),
            # deep-audit F9 (2/7): thieu format `rule_R{n}_` (session 30/6+) ma
            # bible/00 dang dung + check_rule_mention_codified.py da co -> tool
            # verify BAO NHAM missing (vd R77-R80 codified that -> flag FAILED).
            ("rule_prefix", rf"^rule_R{n}_[a-zA-Z]"),
            ("rule_subletter", rf"^rule_R{n}[a-z]?_[a-zA-Z]"),
        ]:
            for m in re.finditer(pat, text, re.MULTILINE):
                line_num = text[:m.start()].count("\n") + 1
                hits.append((f, line_num, fmt))
    if hits:
        msg = ", ".join(f"{f.split('/')[-1]}:{ln} ({fmt})" for f, ln, fmt in hits)
        return True, f"R{n} codified — {msg}"
    return False, f"R{n} NOT codified (0 hits 4-format)"


def verify_rules_range(a, b):
    """Verify 'X rules R{a}-R{b}' — count actual codified."""
    codified = []
    for n in range(a, b + 1):
        ok, _ = verify_rule_codified(n)
        if ok: codified.append(n)
    expected = b - a + 1
    actual = len(codified)
    if actual == expected:
        return True, f"All {expected} rules R{a}-R{b} codified"
    missing = [n for n in range(a, b + 1) if n not in codified]
    return False, f"Only {actual}/{expected} codified — missing: R{missing}"


def verify_stage3_sections(passes_expected):
    """Verify 'STAGE 3 X/6 PASS' — run qa_post_render per section."""
    sections = ["hook", "setup", "incident", "reveal", "payoff", "cliffhanger"]
    passes = []
    for sec in sections:
        wav = SVHMP / "output" / "ep_01" / "sections" / f"{sec}.wav"
        if not wav.exists():
            continue
        out, _ = run(["python", "tools/qa_post_render.py", str(wav)], timeout=60)
        if "GATE: PASS" in out:
            passes.append(sec)
    actual = len(passes)
    if actual == passes_expected:
        return True, f"STAGE 3 {actual}/6 PASS: {passes}"
    return False, f"STAGE 3 actual {actual}/6 PASS (expected {passes_expected}): passes={passes}"


def verify_ep_r86(ep_num):
    """Verify 'EP{N} R86 PASS' — qa_eol_diacritic exit code."""
    p = SVHMP / "output" / f"ep_{ep_num:02d}" / "episode.md"
    if not p.exists():
        return False, f"EP{ep_num:02d} episode.md missing"
    out, code = run(["python", "tools/qa_eol_diacritic.py", str(p)], timeout=30)
    m = re.search(r"R86 EOL violations:\s*(\d+)", out)
    v = int(m.group(1)) if m else None
    if v == 0:
        return True, f"EP{ep_num:02d} R86: 0 violations"
    return False, f"EP{ep_num:02d} R86: {v} violations"


def verify_pipeline_version(version):
    """Verify 'Pipeline v{N}' — grep version trong svhmp_v13_render.py."""
    f = SVHMP / "tools" / "svhmp_v13_render.py"
    if not f.exists():
        return False, "svhmp_v13_render.py missing"
    text = f.read_text(encoding="utf-8")
    # Look for v{N} or version{N}
    pat = re.compile(rf"\bv{version}\b", re.IGNORECASE)
    hits = pat.findall(text)
    if hits:
        return True, f"v{version} found {len(hits)} mentions in svhmp_v13_render.py"
    return False, f"v{version} NOT found in svhmp_v13_render.py"


def verify_section_rendered(section):
    """Verify 'Section X rendered' — wav exists + size > 100KB."""
    wav = SVHMP / "output" / "ep_01" / "sections" / f"{section}.wav"
    if not wav.exists():
        return False, f"{section}.wav missing"
    size = wav.stat().st_size
    if size < 100_000:
        return False, f"{section}.wav too small ({size} bytes — likely corrupt)"
    return True, f"{section}.wav exists ({size:,} bytes)"


def verify_commit(commit_hash):
    """Verify 'Commit {hash}' — git show."""
    out, code = run(["git", "show", "--no-patch", "--format=%H %s", commit_hash])
    if code == 0 and commit_hash[:7] in out:
        return True, f"Commit found: {out.strip()[:120]}"
    return False, f"Commit {commit_hash} NOT found"


# ---- PARSE claim string → dispatch verifier ----

def parse_and_verify(claim: str):
    """Auto-detect claim type, dispatch verifier."""
    claim = claim.strip()

    # Pattern: "R{N} codified" / "R{N} codify"
    m = re.search(r"\bR(\d+)\s+codif", claim, re.IGNORECASE)
    if m:
        ok, msg = verify_rule_codified(int(m.group(1)))
        return ok, msg, "rule_codified"

    # Pattern: "X rules R{a}-R{b}" / "X hard rules R{a}-R{b}"
    m = re.search(r"(\d+)\s+(?:hard\s+)?rules?\s+R(\d+)[-–]R(\d+)", claim, re.IGNORECASE)
    if m:
        expected_count, a, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        ok, msg = verify_rules_range(a, b)
        # Also check count match
        if ok and (b - a + 1) != expected_count:
            return False, f"{msg}, BUT claim said {expected_count} rules ≠ actual range R{a}-R{b} = {b-a+1}", "rules_range"
        return ok, msg, "rules_range"

    # Pattern: "STAGE 3 X/6 PASS"
    m = re.search(r"STAGE\s+3\s+(\d+)/6\s+PASS", claim, re.IGNORECASE)
    if m:
        ok, msg = verify_stage3_sections(int(m.group(1)))
        return ok, msg, "stage3_sections"

    # Pattern: "EP{N} R86 PASS"
    m = re.search(r"EP(\d+)\s+R86\s+PASS", claim, re.IGNORECASE)
    if m:
        ok, msg = verify_ep_r86(int(m.group(1)))
        return ok, msg, "ep_r86"

    # Pattern: "Pipeline v{N}" / "v{N} LOCK" / "v{N} ship"
    m = re.search(r"(?:Pipeline\s+|^|\s)v(\d+)\b", claim, re.IGNORECASE)
    if m:
        ok, msg = verify_pipeline_version(m.group(1))
        return ok, msg, "pipeline_version"

    # Pattern: "Section X rendered" / "X.wav shipped"
    m = re.search(r"(hook|setup|incident|reveal|payoff|cliffhanger)\.wav", claim, re.IGNORECASE)
    if m:
        ok, msg = verify_section_rendered(m.group(1).lower())
        return ok, msg, "section_rendered"

    # Pattern: 7+ char hash
    m = re.search(r"\b([0-9a-f]{7,40})\b", claim)
    if m:
        ok, msg = verify_commit(m.group(1))
        return ok, msg, "commit"

    return None, f"No claim pattern matched: '{claim[:80]}'", "unknown"


def verify_recent_ping(n: int):
    """Verify N latest PING AUTO LOG events."""
    ping = SVHMP / "PING_CMD_LEAD_29_06.md"
    if not ping.exists():
        print(f"[ERR] PING file not found: {ping}")
        return 2
    text = ping.read_text(encoding="utf-8")
    m = re.search(r"## AUTO LOG.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if not m:
        print("[ERR] No AUTO LOG section")
        return 2
    lines = [l for l in m.group(1).split("\n") if l.strip().startswith("- `")][:n]
    print(f"=== VERIFY LATEST {len(lines)} PING events ===\n")
    verified = failed = unknown = 0
    for line in lines:
        # Extract claim text (after **[CATEGORY]**)
        cm = re.search(r"\*\*\[(\w+)\]\*\*[^:]*:\s*(.*)", line)
        if not cm: continue
        cat, claim = cm.group(1), cm.group(2)
        ok, msg, ctype = parse_and_verify(claim)
        if ok is True:
            print(f"  [VERIFIED] ({ctype}) {msg[:90]}")
            verified += 1
        elif ok is False:
            print(f"  [FAILED]   ({ctype}) {msg[:90]}")
            failed += 1
        else:
            print(f"  [UNKNOWN]  {msg[:90]}")
            unknown += 1
    print(f"\nSUMMARY: VERIFIED={verified} FAILED={failed} UNKNOWN={unknown}")
    return 0 if failed == 0 else 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    if sys.argv[1] == "--recent":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        return verify_recent_ping(n)
    claim = " ".join(sys.argv[1:])
    ok, msg, ctype = parse_and_verify(claim)
    if ok is True:
        print(f"{VERIFIED} ({ctype}) {msg}")
        return 0
    elif ok is False:
        print(f"{FAILED} ({ctype}) {msg}")
        return 1
    else:
        print(f"{UNKNOWN} {msg}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
