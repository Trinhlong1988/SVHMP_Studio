"""
hidden_audit.py — R_SUPREME gate 3 (Mr.Long lock 30/6 22:00 docx)

Answer Mr.Long's questions about every shipped tool:
  - Lines of code?
  - Number of TODO / FIXME / XXX / HACK markers?
  - Number of 'placeholder' mentions?
  - Number of bare `pass` statements (suspect stub)?
  - Number of NotImplemented?
  - Number of hardcoded magic numbers (suspect intuition tuning)?

Output: STRICT PROTOCOL JSON + per-file table.

Usage:
    python tools/hidden_audit.py
    python tools/hidden_audit.py --scope tier_2_1   (Voice Profile + 5 voice QA + extract_embedding)
    python tools/hidden_audit.py --json
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

TIER_2_1_SCOPE = [
    "tools/voice_profile_manager.py",
    "tools/qa_boundary_artifact.py",
    "tools/qa_breath_artifact.py",
    "tools/qa_prosody_collapse.py",
    "tools/qa_onset_artifact.py",
    "tools/qa_dialogue_identity.py",
    "tools/extract_speaker_embedding.py",
]

ALL_SCOPE = TIER_2_1_SCOPE + [
    "tools/cmd_progress_logger.py",
    "tools/audit_driver_dialogue_context.py",
    "tools/sync_specs_from_episode.py",
    "tools/audit_vn_style.py",
    "tools/build_specs_from_episode.py",
    "tests/test_voice_profile_manager.py",
    "tests/test_voice_qa_tools.py",
]

TODO_RE = re.compile(r"\b(TODO|FIXME|XXX|HACK)\b", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\bplaceholder\b", re.IGNORECASE)
NOT_IMPL_RE = re.compile(r"\bNotImplemented(Error)?\b")

KNOWN_OK_HARDCODES = {
    192,  # ECAPA embedding dim
    8,    # IndexTTS2 emotion vector dim
    1.0, 0.0, 0.5,
    22050, 44100,  # standard sample rates
    100, 200, 400, 500, 1000, 1500, 2000, 3000,  # ms increments
    -1,
}


def count_bare_pass(tree: ast.AST) -> int:
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Pass):
            count += 1
    return count


def count_hardcoded_numbers(tree: ast.AST) -> tuple[int, list[float]]:
    suspect: list[float] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            v = node.value
            if v in KNOWN_OK_HARDCODES:
                continue
            if abs(v) < 1.0 and v != 0:
                suspect.append(float(v))
            elif isinstance(v, int) and 1 < v <= 100000:
                suspect.append(int(v))
    return len(suspect), suspect[:20]


def audit_file(path: Path) -> dict:
    if not path.exists():
        return {"file": str(path), "missing": True}
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
    total_lines = len(lines)
    todos = TODO_RE.findall(src)
    placeholders = PLACEHOLDER_RE.findall(src)
    not_impl = NOT_IMPL_RE.findall(src)
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return {"file": str(path), "parse_error": str(e)}
    bare_pass = count_bare_pass(tree)
    n_hardcode, hardcode_samples = count_hardcoded_numbers(tree)
    return {
        "file": str(path.relative_to(REPO_ROOT)),
        "total_lines": total_lines,
        "loc_excluding_comments_blank": loc,
        "todo_fixme_xxx_hack": len(todos),
        "todo_matches": list(set(todos)),
        "placeholder_mentions": len(placeholders),
        "bare_pass_statements": bare_pass,
        "not_implemented": len(not_impl),
        "hardcoded_numbers": n_hardcode,
        "hardcoded_samples": hardcode_samples,
    }


def severity_for_file(rpt: dict) -> str:
    if rpt.get("missing") or rpt.get("parse_error"):
        return "FAIL"
    high = (
        rpt["todo_fixme_xxx_hack"] > 0
        or rpt["not_implemented"] > 0
        or rpt["bare_pass_statements"] > 2
    )
    medium = rpt["placeholder_mentions"] > 0 or rpt["hardcoded_numbers"] > 30
    if high:
        return "HIGH"
    if medium:
        return "MEDIUM"
    return "OK"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=("tier_2_1", "all"), default="tier_2_1")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    files = TIER_2_1_SCOPE if args.scope == "tier_2_1" else ALL_SCOPE
    reports = []
    for f in files:
        rpt = audit_file(REPO_ROOT / f)
        rpt["severity"] = severity_for_file(rpt)
        reports.append(rpt)

    summary = {
        "rule": "R_SUPREME gate 3 hidden_audit",
        "scope": args.scope,
        "files_audited": len(reports),
        "total_loc": sum(r.get("loc_excluding_comments_blank", 0) for r in reports),
        "total_todo": sum(r.get("todo_fixme_xxx_hack", 0) for r in reports),
        "total_placeholder": sum(r.get("placeholder_mentions", 0) for r in reports),
        "total_bare_pass": sum(r.get("bare_pass_statements", 0) for r in reports),
        "total_not_impl": sum(r.get("not_implemented", 0) for r in reports),
        "total_hardcode": sum(r.get("hardcoded_numbers", 0) for r in reports),
        "files_high": sum(1 for r in reports if r["severity"] == "HIGH"),
        "files_medium": sum(1 for r in reports if r["severity"] == "MEDIUM"),
        "files_ok": sum(1 for r in reports if r["severity"] == "OK"),
        "verdict": "PASS" if all(r["severity"] in ("OK", "MEDIUM") for r in reports) else "FAIL",
    }

    if args.json:
        print(json.dumps({"summary": summary, "per_file": reports}, ensure_ascii=False, indent=2))
    else:
        print(f"[HIDDEN_AUDIT] scope={args.scope}  files={len(reports)}")
        print(f"  TOTAL: loc={summary['total_loc']}  todo={summary['total_todo']}  "
              f"placeholder={summary['total_placeholder']}  bare_pass={summary['total_bare_pass']}  "
              f"not_impl={summary['total_not_impl']}  hardcode={summary['total_hardcode']}")
        print(f"  Verdict: {summary['verdict']}  HIGH={summary['files_high']}  "
              f"MED={summary['files_medium']}  OK={summary['files_ok']}")
        print()
        for r in reports:
            if r.get("missing"):
                print(f"  [{r['severity']}] {r['file']}  MISSING")
                continue
            if r.get("parse_error"):
                print(f"  [{r['severity']}] {r['file']}  PARSE_ERROR: {r['parse_error']}")
                continue
            print(f"  [{r['severity']}] {r['file']}  loc={r['loc_excluding_comments_blank']}  "
                  f"todo={r['todo_fixme_xxx_hack']}  ph={r['placeholder_mentions']}  "
                  f"pass={r['bare_pass_statements']}  ni={r['not_implemented']}  hc={r['hardcoded_numbers']}")

    return 0 if summary["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
