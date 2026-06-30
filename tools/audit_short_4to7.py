"""
audit_short_4to7.py — detect sentences 4-7 từ TTS dễ cụt hơi
Mr.Long lock 30/6 17:30: 'kiểm tra sâu full những đoạn ngắt 4 5 6 7 từ'.

R-supplement to R60 (≤3 EOL) and R61 (≤3 START):
sentences 4-7 từ chưa fail hardlock nhưng TTS BigVGAN onset/offset
+ pause flow dễ tạo cảm nhận cụt hơi cho người nghe.

Usage:
    python tools/audit_short_4to7.py --file output/ep_01/episode.md
    python tools/audit_short_4to7.py --episode 1 --json
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

WHITELIST_DIALOGUE_HEAD = ["—", "-"]


def is_skip(line: str) -> bool:
    s = line.strip()
    if not s:
        return True
    if s.startswith("#"):
        return True
    if s.startswith("[pause:"):
        return True
    if s.startswith(">"):
        return True
    if s.startswith("---"):
        return True
    if s.startswith("```"):
        return True
    return False


def count_words(s: str) -> int:
    text = re.sub(r"^[—\-—]\s*", "", s.strip())
    text = re.sub(r"[\.\?!…,;:\"“”‘’]", " ", text)
    parts = [p for p in text.split() if p.strip()]
    return len(parts)


def split_into_sentences(line: str) -> list[str]:
    parts = re.split(r"(?<=[\.\?!…])\s+", line.strip())
    return [p.strip() for p in parts if p.strip()]


def audit_file(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    findings = []
    n_total = 0
    consecutive_short = 0
    chain_starts: list[int] = []
    chains: list[tuple[int, int]] = []

    line_idx = 0
    for raw in text.splitlines():
        line_idx += 1
        if is_skip(raw):
            consecutive_short = 0
            continue
        for sent in split_into_sentences(raw):
            n_total += 1
            wc = count_words(sent)
            if 4 <= wc <= 7:
                findings.append(
                    {
                        "line": line_idx,
                        "word_count": wc,
                        "text": sent,
                        "verdict": "SHORT_4to7",
                        "severity": "MEDIUM",
                        "reason": (
                            "4-7 từ — TTS dễ cụt hơi do BigVGAN onset/offset ramp + "
                            "pause flow. Khuyến nghị merge câu kế hoặc thêm complement."
                        ),
                    }
                )
                if consecutive_short == 0:
                    chain_starts.append(line_idx)
                consecutive_short += 1
            else:
                if consecutive_short >= 2:
                    chains.append((chain_starts[-1], consecutive_short))
                consecutive_short = 0

    if consecutive_short >= 2:
        chains.append((chain_starts[-1], consecutive_short))

    chain_warnings = []
    for start, length in chains:
        chain_warnings.append(
            {
                "start_line": start,
                "count": length,
                "verdict": "SHORT_CHAIN",
                "severity": "HIGH",
                "reason": f"{length} câu 4-7 từ liên tiếp từ line {start} = 'máy đọc' (R1 cấm).",
            }
        )

    n_short = len(findings)
    n_chain = len(chain_warnings)
    return {
        "source": str(path),
        "rule": "R60+R61 supplement: 4-7 word TTS cụt hơi check",
        "total_sentences": n_total,
        "n_short_4to7": n_short,
        "n_chains": n_chain,
        "verdict": "PASS" if n_chain == 0 and n_short < n_total * 0.15 else "WARN",
        "findings": findings,
        "chain_warnings": chain_warnings,
    }


def _resolve_targets(args: argparse.Namespace) -> list[Path]:
    if args.file:
        return [Path(args.file)]
    if args.episode:
        return [REPO_ROOT / "output" / f"ep_{int(args.episode):02d}" / "episode.md"]
    if args.all:
        return sorted((REPO_ROOT / "output").glob("ep_*/episode.md"))
    return []


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", type=int)
    ap.add_argument("--file", type=str)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--max-show", type=int, default=20)
    args = ap.parse_args()

    targets = _resolve_targets(args)
    if not targets:
        ap.error("--episode N or --file PATH or --all")

    overall_warn = 0
    reports = []
    for t in targets:
        if not t.exists():
            print(f"[R60+R61+] MISSING {t}")
            overall_warn += 1
            continue
        rpt = audit_file(t)
        reports.append(rpt)
        if rpt["verdict"] != "PASS":
            overall_warn += 1
        if args.json:
            continue
        print(
            f"[R60+R61+] {t} | verdict={rpt['verdict']} | "
            f"4-7 từ count={rpt['n_short_4to7']} chains={rpt['n_chains']} "
            f"total_sents={rpt['total_sentences']}"
        )
        for w in rpt["chain_warnings"]:
            print(
                f"  CHAIN line {w['start_line']} × {w['count']} câu liên tiếp "
                f"4-7 từ → {w['reason']}"
            )
        for i, f in enumerate(rpt["findings"][: args.max_show]):
            print(f"  L{f['line']:>4} wc={f['word_count']} : {f['text']}")
        if len(rpt["findings"]) > args.max_show:
            print(f"  ... ({len(rpt['findings']) - args.max_show} more)")

    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))

    return 0 if overall_warn == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
