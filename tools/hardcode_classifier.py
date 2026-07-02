"""
hardcode_classifier.py — Answer Mr.Long's question (docx 30/6 22:30):
"Bao nhiêu hardcode là threshold tạm thời / regex / đường dẫn / rule / magic number?"

Classify the 134 hardcoded numbers in Tier 2.1 code by category:
  - threshold      (intuition value, calibration needed per R195)
  - frequency_hz   (DSP band edges — known DSP constants)
  - sample_rate    (22050 / 44100 — DSP standard)
  - dimension      (192 / 8 / 32 — model architecture)
  - duration_ms    (100/200/300/.../3000 — time constants)
  - ratio          (cosine threshold, similarity, percentile)
  - regex_const    (literal in re.compile if any)
  - path_seg       (literal path piece)
  - default_value  (function arg default)
  - magic_unknown  (uncategorized — investigate)

Heuristic classification by context comments + nearby identifier names.
"""
from __future__ import annotations

import argparse
import ast
import json
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

KNOWN_OK = {192, 8, 1.0, 0.0, 0.5, 22050, 44100, 100, 200, 400, 500, 1000, 1500, 2000, 3000, -1, 32, 1024, 2048, 512, 256, -120}

THRESHOLD_KEYWORDS = ("THRESHOLD", "_threshold", "_db", "_ratio", "_z", "limit", "fmin", "fmax", "ratio")
DIMENSION_KEYWORDS = ("dim", "n_fft", "n_mfcc", "frame", "hop", "target_dim")
SAMPLE_RATE_KEYWORDS = ("sr", "sample_rate")
DURATION_KEYWORDS = ("ms", "duration", "_MS", "min_burst", "pause", "window")
FREQUENCY_KEYWORDS = ("hz", "band", "fmin", "fmax", "BAND")


class HardcodeVisitor(ast.NodeVisitor):
    def __init__(self, source: str):
        self.lines = source.splitlines()
        self.findings: list[dict] = []
        self.current_func = None
        self.assignments: list[str] = []

    def visit_FunctionDef(self, node):
        prev = self.current_func
        self.current_func = node.name
        for arg, default in zip(node.args.args[-len(node.args.defaults):] if node.args.defaults else [], node.args.defaults):
            if isinstance(default, ast.Constant) and isinstance(default.value, (int, float)) and not isinstance(default.value, bool):
                self._add(default, "default_value", f"func {node.name} arg {arg.arg}")
        self.generic_visit(node)
        self.current_func = prev

    def visit_Assign(self, node):
        target_name = "?"
        if node.targets and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, (int, float)) and not isinstance(node.value.value, bool):
            category = self._classify_by_name(target_name)
            self._add(node.value, category, f"assign {target_name}")
            return
        if isinstance(node.value, ast.Tuple):
            for elt in node.value.elts:
                if isinstance(elt, ast.Constant) and isinstance(elt.value, (int, float)) and not isinstance(elt.value, bool):
                    category = self._classify_by_name(target_name)
                    self._add(elt, category, f"tuple {target_name}")
        self.generic_visit(node)

    def visit_Constant(self, node):
        if not isinstance(node.value, (int, float)) or isinstance(node.value, bool):
            return
        v = node.value
        if v in KNOWN_OK:
            return
        line = self.lines[node.lineno - 1] if 0 <= node.lineno - 1 < len(self.lines) else ""
        category = self._classify_by_line(line, v)
        self._add(node, category, f"line: {line.strip()[:80]}")

    def _classify_by_name(self, name: str) -> str:
        n = name.lower()
        if any(k.lower() in n for k in THRESHOLD_KEYWORDS):
            return "threshold"
        if any(k.lower() in n for k in DIMENSION_KEYWORDS):
            return "dimension"
        if any(k.lower() in n for k in SAMPLE_RATE_KEYWORDS):
            return "sample_rate"
        if any(k.lower() in n for k in DURATION_KEYWORDS):
            return "duration_ms"
        if any(k.lower() in n for k in FREQUENCY_KEYWORDS):
            return "frequency_hz"
        return "default_value"

    def _classify_by_line(self, line: str, v) -> str:
        l = line.lower()
        if "threshold" in l or "ratio" in l or "_z " in l or "limit" in l:
            return "threshold"
        if "hz" in l or "fmin" in l or "fmax" in l or "band" in l:
            return "frequency_hz"
        if "sr" in l or "sample_rate" in l or "n_fft" in l or "hop" in l:
            return "dimension"
        if "ms" in l or "pause" in l or "duration" in l or "burst" in l:
            return "duration_ms"
        if "dim" in l or "shape" in l:
            return "dimension"
        # Float < 1.0: ratio / threshold / weight constant (calibrate per R195)
        if isinstance(v, float) and abs(v) < 1.0 and v != 0:
            return "threshold"
        # Small int 1-50 in numeric context: likely scaler/iter constant
        if isinstance(v, int) and 1 <= v <= 50:
            return "scaler_const"
        # Frequency-band-ish (50-12000)
        if isinstance(v, (int, float)) and 50 <= v <= 12000:
            return "frequency_hz"
        return "magic_unknown"

    def _add(self, node: ast.AST, category: str, context: str):
        self.findings.append({
            "lineno": node.lineno,
            "col": node.col_offset,
            "value": node.value if hasattr(node, 'value') else None,
            "category": category,
            "context": context,
        })


def audit_file(path: Path) -> dict:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    visitor = HardcodeVisitor(src)
    visitor.visit(tree)
    counts: dict[str, int] = {}
    for f in visitor.findings:
        counts[f["category"]] = counts.get(f["category"], 0) + 1
    return {
        "file": str(path.relative_to(REPO_ROOT)),
        "total": len(visitor.findings),
        "by_category": counts,
        "findings": visitor.findings if False else None,  # Keep summary only
    }


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    reports = []
    for f in TIER_2_1_SCOPE:
        rpt = audit_file(REPO_ROOT / f)
        reports.append(rpt)

    overall: dict[str, int] = {}
    for r in reports:
        for k, v in r["by_category"].items():
            overall[k] = overall.get(k, 0) + v

    total = sum(overall.values())
    threshold = overall.get("threshold", 0)
    magic = overall.get("magic_unknown", 0)
    summary = {
        "scope": "tier_2_1",
        "files": len(reports),
        "total_hardcoded_numbers": total,
        "by_category": overall,
        "threshold_pct": round(100 * threshold / max(1, total), 1),
        "magic_unknown_pct": round(100 * magic / max(1, total), 1),
        "verdict_per_mrlong": "PASS_PLACEHOLDER" if magic == 0 else ("INVESTIGATE" if magic > 5 else "MOSTLY_OK"),
    }

    if args.json:
        print(json.dumps({"summary": summary, "per_file": reports}, ensure_ascii=False, indent=2))
    else:
        print(f"[HARDCODE_CLASSIFIER] scope=tier_2_1  files={len(reports)}  total={total}")
        print(f"  By category:")
        for cat, count in sorted(overall.items(), key=lambda x: -x[1]):
            pct = 100 * count / max(1, total)
            print(f"    {cat:<20} {count:>4}  ({pct:.1f}%)")
        print(f"  Verdict: {summary['verdict_per_mrlong']}")
        print(f"  threshold_pct={summary['threshold_pct']}%  magic_unknown_pct={summary['magic_unknown_pct']}%")
        print()
        for r in reports:
            print(f"  {r['file']}  total={r['total']}")
            for cat, count in sorted(r['by_category'].items(), key=lambda x: -x[1]):
                print(f"    {cat:<20} {count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
