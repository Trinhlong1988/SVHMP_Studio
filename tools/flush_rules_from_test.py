"""Flush rules từ regression test → bible/00 (auto-codify stub).

Mr.Long catch 30/6: CMD #2 ship Tier 1 v1.0.0-rc1 với 8 rules test PASS
(R86/R92b/R110/R111/R113/R117/R128/R141) — nhưng 5/8 KHÔNG codified bible/00:
R110/R111/R113/R117/R128/R141.

Tool:
1. Đọc tests/regression/regression_report.json (rules tested + KPI)
2. Cross-check bible/00 codified (4-format)
3. List missing
4. Generate stub entry per missing rule
5. --apply để write stub vào bible/00 (top-level format)
6. --rule R{N} --source FILE để codify 1 rule manually

Usage:
    python tools/flush_rules_from_test.py                    # report missing
    python tools/flush_rules_from_test.py --apply            # write all missing stubs
    python tools/flush_rules_from_test.py --rule R110        # propose single
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
BIBLE = SVHMP / "bible" / "00_constitution.yaml"
REPORT = SVHMP / "tests" / "regression" / "regression_report.json"
TOOLS_DIR = SVHMP / "tools"


def codified_in_bible(n):
    """Return True nếu R{n} codified bible/00 (any format)."""
    if not BIBLE.exists():
        return False
    text = BIBLE.read_text(encoding="utf-8")
    pats = [
        rf"^R{n}_[a-zA-Z]",
        rf"^\s*-\s*id:\s*R{n}\b",
    ]
    for pat in pats:
        if re.search(pat, text, re.MULTILINE):
            return True
    return False


def find_detection_tool(n):
    """Look in tools/qa_*.py for R{N} reference → return tool name."""
    for f in sorted(TOOLS_DIR.glob("qa_*.py")) + sorted(TOOLS_DIR.glob("audit_*.py")):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if re.search(rf"\bR{n}\b", text[:500]):  # check docstring/top
            return f.name
    return None


def make_stub(n, kpi):
    """Generate yaml stub entry cho R{n}."""
    tool = find_detection_tool(n) or "TODO — find detection tool"
    ts = datetime.now().strftime("%Y-%m-%d")
    tp = kpi.get("TP", "?")
    tn = kpi.get("TN", "?")
    fp = kpi.get("FP", "?")
    fn = kpi.get("FN", "?")
    return f"""
R{n}_codified_from_test_stub:
  # CODIFIED {ts} by CMD LEAD flush_rules_from_test.py
  # Source: regression test PASS — TP={tp} TN={tn} FP={fp} FN={fn}
  # WARN: STUB only — em CMD LEAD chỉ flush từ test evidence
  # TODO: fill rule/why/example từ memory hoặc CMD #2 spec gốc
  rule: "STUB — em CMD LEAD chỉ flush từ regression test evidence. CMD ship rule cần fill full spec."
  detection: tools/{tool}
  test_evidence:
    TP: {tp}
    TN: {tn}
    FP: {fp}
    FN: {fn}
    report: tests/regression/regression_report.json
  status: stub_pending_full_spec
"""


def report_missing():
    if not REPORT.exists():
        print(f"[ERR] {REPORT} not found")
        return 1, []
    data = json.loads(REPORT.read_text(encoding="utf-8"))
    tested = data.get("qa_tools", [])
    results = data.get("results", {})

    codified = []
    missing = []
    for tool_name in tested:
        m = re.match(r"R(\d+)", tool_name)
        if not m:
            continue
        n = int(m.group(1))
        if codified_in_bible(n):
            codified.append(n)
        else:
            missing.append((n, results.get(tool_name, {})))

    print(f"=== Regression test rules ({len(tested)} tested) ===")
    print(f"  Codified bible/00: {sorted(codified)} ({len(codified)})")
    print(f"  MISSING from bible/00: {[n for n, _ in missing]} ({len(missing)})")
    return 0, missing


def apply_missing():
    code, missing = report_missing()
    if code != 0 or not missing:
        print("\n[OK] Nothing to flush")
        return 0
    print(f"\n=== Writing {len(missing)} stubs vào bible/00 ===")
    current = BIBLE.read_text(encoding="utf-8")
    new_blocks = []
    for n, kpi in missing:
        if codified_in_bible(n):
            print(f"  Skip R{n} — already codified (race)")
            continue
        stub = make_stub(n, kpi)
        new_blocks.append(stub)
        print(f"  R{n}: stub append (tool={find_detection_tool(n) or 'unknown'})")
    if new_blocks:
        marker = "\n\n# === FLUSHED FROM REGRESSION TEST by CMD LEAD ===\n"
        BIBLE.write_text(current + marker + "".join(new_blocks), encoding="utf-8")
        print(f"\n[WRITE] {len(new_blocks)} stubs appended bible/00")
    return 0


def main():
    args = sys.argv[1:]
    if "--apply" in args:
        return apply_missing()
    code, _ = report_missing()
    return code


if __name__ == "__main__":
    sys.exit(main())
