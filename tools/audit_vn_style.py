"""
audit_vn_style.py — R193 enforcement
Scan episode.md against bible/36_vn_style_db.yaml for:
  - Forbidden collocations
  - AI-slop overuse
  - Time markers missing pause (R178b)
  - Grammar rules violations
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = REPO_ROOT / "bible" / "36_vn_style_db.yaml"


def load_db(path: Path = DEFAULT_DB) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML required")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def scan_collocations(text: str, db: dict) -> list[dict]:
    findings = []
    for entry_id, entry in (db.get("collocations") or {}).items():
        base = entry.get("base", "")
        forbidden = entry.get("forbidden_modifiers", []) or entry.get("forbidden_patterns", [])
        for fm in forbidden:
            pat = re.compile(re.escape(base) + r"\s+(rất\s+)?" + re.escape(fm.replace("rất ", "")))
            for m in pat.finditer(text):
                findings.append({
                    "type": "collocation_forbidden",
                    "severity": "HIGH",
                    "entry": entry_id,
                    "match": m.group(0),
                    "note": entry.get("grammar_note", ""),
                })
            if fm in text:
                full = base + " " + fm.replace("rất ", "")
                if full in text:
                    pass
    return findings


def scan_ai_slop(text: str, db: dict) -> list[dict]:
    findings = []
    for entry in db.get("ai_slop_extended", []) or []:
        phrase = entry.get("phrase", "")
        max_per_ep = entry.get("max_per_episode", 5)
        count = text.count(phrase)
        if count > max_per_ep:
            findings.append({
                "type": "ai_slop_overuse",
                "severity": "MEDIUM",
                "phrase": phrase,
                "count": count,
                "max_allowed": max_per_ep,
                "note": entry.get("note", ""),
            })
    return findings


def scan_time_markers(text: str, db: dict) -> list[dict]:
    findings = []
    tm = db.get("time_markers_flashback") or {}
    triggers = tm.get("triggers", []) or []
    pause_ms_min = tm.get("must_have_pause_after_ms", 400)
    lines = text.splitlines()
    for ln_idx, line in enumerate(lines, 1):
        for trig in triggers:
            if trig in line.lower():
                pos = line.lower().find(trig)
                tail = line[pos + len(trig):pos + len(trig) + 50]
                has_pause_marker = bool(re.search(r"\[pause:\d{3,4}ms\]", tail))
                ends_clause = bool(re.match(r"^\s*[,.]\s", tail))
                if not has_pause_marker and not tail.endswith((".", "?", "!", "…")):
                    if pos + len(trig) < len(line) - 5 and not has_pause_marker:
                        findings.append({
                            "type": "time_marker_no_pause",
                            "severity": "MEDIUM",
                            "line": ln_idx,
                            "trigger": trig,
                            "tail": tail.strip(),
                            "rule": "R178b",
                        })
    return findings


def scan_emdash_style(text: str) -> list[dict]:
    findings = []
    pattern = re.compile(r",\s{2,}")
    for m in pattern.finditer(text):
        findings.append({
            "type": "double_space_comma_avoid",
            "severity": "LOW",
            "match": text[max(0, m.start() - 20):m.end() + 20].strip(),
            "note": "Consider em-dash ' — ' for dramatic pause per G06",
        })
    return findings


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", type=int)
    ap.add_argument("--file", type=str)
    ap.add_argument("--db", type=str, default=str(DEFAULT_DB))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.file:
        target = Path(args.file)
    elif args.episode:
        target = REPO_ROOT / "output" / f"ep_{args.episode:02d}" / "episode.md"
    else:
        ap.error("--file PATH or --episode N")

    if not target.exists():
        print(f"[R193] FAIL — missing {target}")
        return 2

    db = load_db(Path(args.db))
    text = target.read_text(encoding="utf-8")

    findings = []
    findings.extend(scan_collocations(text, db))
    findings.extend(scan_ai_slop(text, db))
    findings.extend(scan_time_markers(text, db))
    findings.extend(scan_emdash_style(text))

    n_high = sum(1 for f in findings if f["severity"] == "HIGH")
    n_med = sum(1 for f in findings if f["severity"] == "MEDIUM")
    n_low = sum(1 for f in findings if f["severity"] == "LOW")
    verdict = "PASS" if n_high == 0 else "FAIL"

    report = {
        "rule": "R193 vn_style_db_audit",
        "target": str(target),
        "db_version": db.get("version"),
        "n_high": n_high,
        "n_medium": n_med,
        "n_low": n_low,
        "verdict": verdict,
        "findings": findings,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[R193] {target.name}  HIGH={n_high}  MED={n_med}  LOW={n_low}  verdict={verdict}")
        for f in findings[:30]:
            print(f"  {f['severity']} {f['type']}  {f.get('match') or f.get('phrase') or f.get('trigger')}")
    return 0 if n_high == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
