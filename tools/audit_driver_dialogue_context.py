"""
audit_driver_dialogue_context.py — R174 enforcer
Mr.Long lock 30/6 16:30 (B60 fix).

Bác tài CHỈ 2 câu LOCK (bible/02_lore_db.yaml:18-20):
  Q1 "Con đã nhớ ra chưa?"  -- KHÔNG cần trigger câu hỏi trước; phù hợp passenger MỚI
  Q2 "Chưa tới lúc."        -- PHẢI có câu hỏi từ passenger trong 3 sentence preceding

Vi phạm = dialogue floating, người nghe không hiểu, cảm nhận cụt ngủn.

Usage:
    python tools/audit_driver_dialogue_context.py --episode 1
    python tools/audit_driver_dialogue_context.py --file output/ep_01/episode.md
    python tools/audit_driver_dialogue_context.py --all  # scan output/ep_*/episode.md
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent

Q1_VARIANTS = [
    "Con đã nhớ ra chưa",
    "con đã nhớ ra chưa",
]
Q2_VARIANTS = [
    "Chưa tới lúc",
    "chưa tới lúc",
]

QUESTION_FROM_PASSENGER_PATTERNS = [
    r"\?",
    r"Tới chưa",
    r"Khi nào",
    r"Bao giờ",
    r"Sao lại",
    r"Tại sao",
    r"Đâu rồi",
    r"Có phải",
    r"Là gì",
]


def split_sentences_md(text: str) -> list[str]:
    """Split markdown into rough sentences keeping order."""
    lines = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#"):
            continue
        if s.startswith("[pause:"):
            continue
        if s.startswith(">"):
            continue
        for sent in re.split(r"(?<=[\.\?!…])\s+", s):
            sent = sent.strip()
            if sent:
                lines.append(sent)
    return lines


def contains_any(s: str, variants: list[str]) -> bool:
    low = s.lower()
    for v in variants:
        if v.lower() in low:
            return True
    return False


def is_passenger_question(s: str) -> bool:
    if "—" in s and not s.strip().startswith("—"):
        return False
    for pat in QUESTION_FROM_PASSENGER_PATTERNS:
        if re.search(pat, s):
            return True
    return False


def audit_text(text: str, src: str = "<text>") -> dict:
    sentences = split_sentences_md(text)
    findings = []
    for idx, sent in enumerate(sentences):
        if contains_any(sent, Q1_VARIANTS):
            findings.append(
                {
                    "type": "Q1",
                    "idx": idx,
                    "text": sent,
                    "verdict": "OK",
                    "reason": "Q1 cho passenger mới — không cần trigger câu hỏi trước.",
                }
            )
            continue
        if contains_any(sent, Q2_VARIANTS):
            window = sentences[max(0, idx - 3) : idx]
            has_trigger = any(is_passenger_question(w) for w in window)
            if has_trigger:
                findings.append(
                    {
                        "type": "Q2",
                        "idx": idx,
                        "text": sent,
                        "verdict": "OK",
                        "reason": "Q2 có trigger câu hỏi passenger trong 3 câu trước.",
                        "trigger_window": window,
                    }
                )
            else:
                findings.append(
                    {
                        "type": "Q2",
                        "idx": idx,
                        "text": sent,
                        "verdict": "FAIL_HIGH",
                        "reason": (
                            "Q2 'Chưa tới lúc' KHÔNG có câu hỏi passenger trong 3 câu trước. "
                            "Vi phạm R174: dialogue floating + cụt ngủn. "
                            "Suggest swap → Q1 'Con đã nhớ ra chưa?' nếu passenger mới."
                        ),
                        "trigger_window": window,
                    }
                )

    n_fail = sum(1 for f in findings if f["verdict"] == "FAIL_HIGH")
    return {
        "source": src,
        "rule": "R174 driver_dialogue_context_match",
        "total_driver_lines": len(findings),
        "n_fail_high": n_fail,
        "verdict": "PASS" if n_fail == 0 else "FAIL",
        "findings": findings,
    }


def _resolve_target(args: argparse.Namespace) -> list[Path]:
    if args.file:
        return [Path(args.file)]
    if args.episode:
        ep_dir = REPO_ROOT / "output" / f"ep_{int(args.episode):02d}"
        return [ep_dir / "episode.md"]
    if args.all:
        return sorted((REPO_ROOT / "output").glob("ep_*/episode.md"))
    return []


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", type=int, help="EP number, e.g. 1")
    ap.add_argument("--file", type=str, help="explicit episode.md path")
    ap.add_argument("--all", action="store_true", help="scan all output/ep_*/episode.md")
    ap.add_argument("--json", action="store_true", help="dump JSON report")
    args = ap.parse_args()

    targets = _resolve_target(args)
    if not targets:
        ap.error("provide --episode N or --file PATH or --all")

    overall_fail = 0
    reports = []
    for t in targets:
        if not t.exists():
            print(f"[R174] MISSING {t}")
            overall_fail += 1
            continue
        text = t.read_text(encoding="utf-8")
        rpt = audit_text(text, src=str(t))
        reports.append(rpt)
        if rpt["verdict"] == "FAIL":
            overall_fail += 1
        if args.json:
            continue
        print(f"[R174] {t} | verdict={rpt['verdict']} | driver_lines={rpt['total_driver_lines']} fail={rpt['n_fail_high']}")
        for f in rpt["findings"]:
            mark = "OK " if f["verdict"] == "OK" else "FAIL"
            print(f"   {mark} {f['type']} idx={f['idx']}: {f['text']}")
            if f["verdict"] == "FAIL_HIGH":
                print(f"        reason: {f['reason']}")

    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))

    return 0 if overall_fail == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
