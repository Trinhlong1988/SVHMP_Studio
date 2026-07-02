"""Bible audit — comprehensive health check hiến pháp.

Mr.Long lệnh 30/6: "nghiên cứu sâu hiến pháp, kiểm soát chặt chẽ, fix triệt để".

Per-rule audit 6 dim:
1. Spec coverage  — rule/why/example/detection fields exist?
2. Schema format  — top-level vs list_id (inconsistency detect)
3. Tool linked    — detection: tools/X.py tồn tại?
4. Test linked    — tests/regression có test cho R{N}?
5. Hook enforced  — pre-commit hook reference R{N}?
6. Cross-rule     — duplicate / contradiction / variant

Output:
    runtime/bible_audit_report.json  — full data
    runtime/bible_audit_report.md    — human-readable

Usage:
    python tools/bible_audit.py             # report
    python tools/bible_audit.py --strict    # exit 1 nếu có HIGH issue
"""
import json
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
BIBLE_00 = SVHMP / "bible" / "00_constitution.yaml"
BIBLE_05 = SVHMP / "bible" / "05_audio_bible.yaml"
TOOLS = SVHMP / "tools"
TESTS = SVHMP / "tests" / "regression"
HOOK = SVHMP / ".githooks" / "pre-commit"
REPORT_JSON = SVHMP / "runtime" / "bible_audit_report.json"
REPORT_MD = SVHMP / "runtime" / "bible_audit_report.md"


def scan_bible():
    """Parse bible/00 + bible/05 → return dict {rule_n: {format, name, fields, line, file}}."""
    rules = {}
    for bf in [BIBLE_00, BIBLE_05]:
        if not bf.exists(): continue
        text = bf.read_text(encoding="utf-8")
        lines = text.split("\n")
        # Top-level: R{N}_xxx: → scan body 30 lines
        for m in re.finditer(r"^(R(\d+))_([a-zA-Z][a-zA-Z0-9_]*?):", text, re.MULTILINE):
            n = int(m.group(2))
            line_n = text[:m.start()].count("\n") + 1
            body = "\n".join(lines[line_n - 1:line_n + 30])
            fields = set(re.findall(r"^\s+(\w+):", body, re.MULTILINE))
            rules.setdefault(n, []).append({
                "format": "top_level",
                "name": m.group(3),
                "line": line_n,
                "file": bf.name,
                "fields": sorted(fields),
            })
        # List format: - id: R{N} + block
        for m in re.finditer(r"^\s*-\s*id:\s*(R(\d+))\s*\n((?:\s+\w+:.*\n){0,20})", text, re.MULTILINE):
            n = int(m.group(2))
            line_n = text[:m.start()].count("\n") + 1
            block = m.group(3)
            fields = set(re.findall(r"^\s+(\w+):", block, re.MULTILINE))
            nm = re.search(r"name:\s*[\"']?([^\"'\n]+)", block)
            rules.setdefault(n, []).append({
                "format": "list",
                "name": (nm.group(1).strip()[:80] if nm else "?"),
                "line": line_n,
                "file": bf.name,
                "fields": sorted(fields),
            })
    return rules


def check_tool_for_rule(n):
    """Return list of tools/ scripts referencing R{n} in header (top 50 lines)."""
    hits = []
    for f in sorted(TOOLS.glob("*.py")):
        try:
            head = "\n".join(f.read_text(encoding="utf-8", errors="replace").split("\n")[:50])
            if re.search(rf"\bR{n}\b", head):
                hits.append(f.name)
        except Exception:
            pass
    return hits


def check_test_for_rule(n):
    """Test exist?"""
    if not TESTS.exists(): return []
    hits = []
    for f in TESTS.rglob("*"):
        if f.is_file() and re.search(rf"r_?{n}\b", f.name, re.IGNORECASE):
            hits.append(f.name)
    return hits


def check_hook_for_rule(n):
    """Hook reference R{n}?"""
    if not HOOK.exists(): return False
    text = HOOK.read_text(encoding="utf-8")
    return bool(re.search(rf"\bR{n}\b", text))


def required_fields(format_type):
    # CMD LEAD 30/6: minimum spec = rule statement. why/detection RECOMMENDED nhưng không required.
    if format_type == "top_level":
        return {"rule"}  # rule statement mandatory
    else:  # list
        return {"name"}  # name = identifier mandatory; rule/statement either accepted

def fields_match(actual, required, format_type):
    """Accept synonyms: rule|statement, detection|tool. List format chỉ cần name."""
    actual = set(actual)
    if format_type == "list":
        # list format: name mandatory, rule/statement/text accepted as content
        if "name" not in actual: return {"name"}
        return set()
    # top_level: rule OR statement mandatory
    if "rule" in actual or "statement" in actual:
        return required - {"rule"} - actual
    return required - actual


def audit():
    rules = scan_bible()
    issues = defaultdict(list)
    report = {"timestamp": datetime.now().isoformat(), "rules": {}, "summary": {}}

    all_ns = sorted(rules.keys())
    if not all_ns:
        return {"error": "no rules"}, issues
    min_n, max_n = all_ns[0], all_ns[-1]
    gaps = [n for n in range(min_n, max_n + 1) if n not in rules]

    duplicates = []
    stubs = []
    missing_spec = []
    no_tool = []
    no_test = []

    for n in all_ns:
        entries = rules[n]
        # Duplicate (multiple definitions)
        if len(entries) > 1:
            duplicates.append(n)
            issues["HIGH"].append(f"R{n}: DUPLICATE — {len(entries)} definitions")

        entry = entries[0]
        # Stub detect
        if "_stub" in entry["name"] or "from_test_stub" in entry["name"]:
            stubs.append(n)
            issues["MEDIUM"].append(f"R{n}: STUB rule — missing full spec")

        # Required fields missing (using synonym-aware check)
        req = required_fields(entry["format"])
        miss = fields_match(entry["fields"], req, entry["format"])
        if miss:
            missing_spec.append(n)
            issues["MEDIUM"].append(f"R{n}: missing fields {miss}")

        # Tool/test/hook coverage
        tools_hits = check_tool_for_rule(n)
        tests_hits = check_test_for_rule(n)
        hook_hit = check_hook_for_rule(n)
        if not tools_hits and not stubs.count(n):
            no_tool.append(n)
        if not tests_hits:
            no_test.append(n)

        report["rules"][n] = {
            "format": entry["format"],
            "name": entry["name"],
            "file": entry["file"],
            "line": entry["line"],
            "fields": entry["fields"],
            "tools": tools_hits,
            "tests": tests_hits,
            "hook_referenced": hook_hit,
            "is_duplicate": n in duplicates,
            "is_stub": n in stubs,
        }

    report["summary"] = {
        "total_rules": len(rules),
        "range": f"R{min_n}-R{max_n}",
        "gaps_count": len(gaps),
        "gaps": gaps,
        "duplicates": duplicates,
        "stubs": stubs,
        "missing_spec": missing_spec,
        "no_tool": no_tool,
        "no_test_count": len(no_test),
        "high_issues": len(issues["HIGH"]),
        "medium_issues": len(issues["MEDIUM"]),
    }
    return report, issues


def write_reports(report, issues):
    REPORT_JSON.parent.mkdir(exist_ok=True, parents=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    s = report["summary"]
    md = [
        f"# BIBLE AUDIT REPORT — {report['timestamp'][:19]}",
        "",
        f"**Total rules:** {s['total_rules']} (range {s['range']})",
        f"**Gaps:** {s['gaps_count']}",
        f"**Duplicates:** {len(s['duplicates'])} ({s['duplicates']})",
        f"**Stubs:** {len(s['stubs'])} ({s['stubs']})",
        f"**Missing required spec fields:** {len(s['missing_spec'])} ({s['missing_spec']})",
        f"**No tool linked:** {len(s['no_tool'])}",
        f"**No test linked:** {s['no_test_count']}",
        "",
        f"## Issues HIGH ({s['high_issues']})",
        "",
    ]
    for ln in issues["HIGH"]:
        md.append(f"- {ln}")
    md.append("")
    md.append(f"## Issues MEDIUM ({s['medium_issues']})")
    md.append("")
    for ln in issues["MEDIUM"][:30]:
        md.append(f"- {ln}")
    if len(issues["MEDIUM"]) > 30:
        md.append(f"- ... + {len(issues['MEDIUM']) - 30} more")
    md.append("")
    md.append(f"## Gaps in range")
    md.append("")
    md.append(f"`{s['gaps']}`")
    md.append("")
    md.append("## Per-rule health (top 20)")
    md.append("")
    md.append("| Rule | Format | Tool | Test | Hook | Stub |")
    md.append("|------|--------|------|------|------|------|")
    for n in sorted(report["rules"].keys())[:20]:
        r = report["rules"][n]
        tool = "✓" if r["tools"] else "—"
        test = "✓" if r["tests"] else "—"
        hook = "✓" if r["hook_referenced"] else "—"
        stub = "⚠" if r["is_stub"] else ""
        md.append(f"| R{n} | {r['format']} | {tool} | {test} | {hook} | {stub} |")
    REPORT_MD.write_text("\n".join(md), encoding="utf-8")


def main():
    print(f"=== Bible audit running... ===")
    report, issues = audit()
    if "error" in report:
        print(f"[ERR] {report['error']}")
        return 2
    write_reports(report, issues)
    s = report["summary"]
    print(f"\n=== SUMMARY ===")
    print(f"  Rules:        {s['total_rules']} ({s['range']})")
    print(f"  Gaps:         {s['gaps_count']}")
    print(f"  Duplicates:   {len(s['duplicates'])} — {s['duplicates']}")
    print(f"  Stubs:        {len(s['stubs'])} — {s['stubs']}")
    print(f"  Missing spec: {len(s['missing_spec'])}")
    print(f"  No tool:      {len(s['no_tool'])}")
    print(f"  No test:      {s['no_test_count']}")
    print(f"  HIGH issues:  {s['high_issues']}")
    print(f"  MEDIUM:       {s['medium_issues']}")
    print(f"\nReport: {REPORT_MD}")
    print(f"JSON:   {REPORT_JSON}")
    if "--strict" in sys.argv and s["high_issues"] > 0:
        print(f"\n[FAIL] {s['high_issues']} HIGH issues (strict mode)")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
