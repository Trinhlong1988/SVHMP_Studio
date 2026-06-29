"""Check counter canonical — detect 1 rule có 2+ scripts đếm khác nhau.

Mr.Long lệnh 29/6: chặn vector "counter mismatch cross-script".

Vấn đề thật:
- R66 short_sentence_chain:
  - audit_r43_to_r67_missing.py → 14 chains (stream toàn EP)
  - audit_short_chain.py → ? (em chưa run)
  - Mr.Long báo manual count: 42
- Cùng "R66" nhưng 3 con số. KHÔNG biết detector nào canonical.

Tool này:
1. Scan tools/ scripts → detect script nào reference rule R{N}
2. Map rule → [script1, script2, ...]
3. Cho --rule R{N} → run all scripts on cùng target → diff counter
4. Flag mismatch + recommend canonical (newest mtime + highest detail)

Usage:
    python tools/check_counter_canonical.py --rule R66
    python tools/check_counter_canonical.py --scan-all       # report all rules với 2+ scripts
    python tools/check_counter_canonical.py --target output/ep_01/episode.md --rule R86
"""
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
TOOLS = SVHMP / "tools"
DEFAULT_TARGET = SVHMP / "output" / "ep_01" / "episode.md"


def scan_scripts_for_rules():
    """Walk tools/*.py, find each script and which rules it references.
    Returns: dict rule_id (int) → list of (script_path, mtime, snippet)."""
    rule_map = defaultdict(list)
    for script in sorted(TOOLS.glob("*.py")):
        if script.name == "check_counter_canonical.py":
            continue
        try:
            text = script.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        # Find rule references: R{N} với N=40-200
        # Prefer references in docstring/top 30 lines (more likely the script's PURPOSE)
        head = "\n".join(text.split("\n")[:50])
        body = text
        refs = set()
        for pat in [
            r"\bR(\d{2,3})\b",
            r"\bR(\d{2,3})_",
        ]:
            for m in re.finditer(pat, head):
                n = int(m.group(1))
                if 40 <= n <= 200:
                    refs.add(n)
        # Filter only scripts whose name suggests audit/qa/fix purpose
        is_audit = any(kw in script.name for kw in ["audit_", "qa_", "verify_", "check_"])
        if not is_audit:
            continue
        for n in refs:
            rule_map[n].append((script, script.stat().st_mtime))
    return rule_map


def run_script_count(script, target):
    """Run script với target, extract a violation count number from stdout."""
    try:
        r = subprocess.run(
            ["python", str(script), str(target)],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", cwd=SVHMP, timeout=60,
        )
        out = r.stdout
    except Exception as e:
        return None, f"[ERR {e}]"
    # Try multiple count patterns
    for pat in [
        r"R(?:\d{2,3})\s+(?:EOL\s+)?violations?:\s*(\d+)",
        r"Total\s+(?:violations|chains|issues|repeats|R86|EOL):?\s*(\d+)",
        r"violations?:\s*(\d+)",
        r"chains?\s*≥3.*?:\s*(\d+)",
        r"R\d+\s+(?:chain[s]?|repeat[s]?|issue[s]?)\s+\d+\s+EPs?:\s*(\d+)",
        r"(\d+)\s+(?:violations|chains|issues|repeats)",
    ]:
        m = re.search(pat, out, re.IGNORECASE)
        if m:
            return int(m.group(1)), out[:200]
    return None, out[:200]


def check_rule(rule_n, target):
    rule_map = scan_scripts_for_rules()
    scripts = rule_map.get(rule_n, [])
    print(f"=== R{rule_n} counter check on {target.name} ===\n")
    if len(scripts) == 0:
        print(f"[OK] R{rule_n}: 0 scripts reference — no canonical concern")
        return 0
    if len(scripts) == 1:
        s, _ = scripts[0]
        count, snippet = run_script_count(s, target)
        print(f"[OK] R{rule_n}: 1 script (canonical) — {s.name}")
        print(f"  Count: {count}")
        return 0
    print(f"[CANDIDATES] R{rule_n}: {len(scripts)} scripts reference\n")
    results = []
    for s, mtime in sorted(scripts, key=lambda x: -x[1]):
        count, snippet = run_script_count(s, target)
        results.append((s, mtime, count, snippet))
        print(f"  {s.name:45s} count={count}  mtime={int(mtime)}")
    # Mismatch check
    counts = [r[2] for r in results if r[2] is not None]
    if len(set(counts)) <= 1:
        print(f"\n[OK] All scripts agree (count={counts[0] if counts else 'N/A'})")
        return 0
    print(f"\n[MISMATCH] {len(set(counts))} different counts: {sorted(set(counts))}")
    canonical = max(results, key=lambda r: r[1])  # newest mtime
    print(f"[CANONICAL recommend] {canonical[0].name} (newest mtime)")
    print(f"  → Deprecate others hoặc reconcile spec")
    return 1


def scan_all():
    rule_map = scan_scripts_for_rules()
    multi = {n: scripts for n, scripts in rule_map.items() if len(scripts) >= 2}
    if not multi:
        print("[OK] No rules với 2+ scripts — no counter mismatch risk")
        return 0
    print(f"=== Rules với 2+ scripts (counter mismatch risk) ===\n")
    for n in sorted(multi):
        scripts = multi[n]
        print(f"R{n}: {len(scripts)} scripts")
        for s, mtime in sorted(scripts, key=lambda x: -x[1]):
            print(f"  {s.name}  mtime={int(mtime)}")
        print()
    print(f"\nRun `python tools/check_counter_canonical.py --rule R{sorted(multi)[0]}` để diff count")
    return 1 if multi else 0


def main():
    rule = None
    target = DEFAULT_TARGET
    scan = False
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--rule" and i + 1 < len(args):
            m = re.match(r"R?(\d+)", args[i+1])
            rule = int(m.group(1)) if m else None
            i += 2
        elif args[i] == "--target" and i + 1 < len(args):
            target = Path(args[i+1])
            i += 2
        elif args[i] == "--scan-all":
            scan = True
            i += 1
        else:
            i += 1
    if scan:
        return scan_all()
    if rule is None:
        print(__doc__)
        return 2
    return check_rule(rule, target)


if __name__ == "__main__":
    sys.exit(main())
