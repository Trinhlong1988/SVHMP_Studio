"""
sync_specs_from_episode.py — R192 enforcement (Option A: spec/episode sync)
Mr.Long approve 30/6 19:50.

Propagate text changes from output/ep_N/episode.md to output/ep_N/sections/spec_*.json
preserving emo_vector / pause_after_ms / is_dialogue / volume_scale / etc.

Strategy:
  - Read each spec_<section>.json
  - For each chunk in spec, find matching text in episode.md by similarity
  - If matched (>= threshold) and old != new: replace spec chunk["text"]
  - If not matched: WARN + leave unchanged
  - Backup spec_*.json.bak.sync_<ts> before write

NOTE: Phase 2.5 will replace this with SSOT generate-from-episode (Option D).
This tool is the bridge until SSOT migration.

Usage:
    python tools/sync_specs_from_episode.py --episode 1 --dry-run
    python tools/sync_specs_from_episode.py --episode 1 --apply
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def normalize(s: str) -> str:
    s = re.sub(r"\[pause:\d+ms\]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def extract_episode_sentences(md_path: Path) -> list[str]:
    """Return list of candidates. Each line in md is one candidate.
    DO NOT split at '...' since Vietnamese ellipsis is continuation, not EOS.
    DO NOT split at '.' inside potential abbreviation. Treat each line as one chunk.
    Spec chunks typically map 1:1 to markdown lines.
    """
    text = md_path.read_text(encoding="utf-8")
    out = []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("#") or s.startswith(">") or s.startswith("```"):
            continue
        if s.startswith("---") or s.startswith("|"):
            continue
        if re.match(r"^\s*\[pause:\d+ms\]\s*$", s):
            continue
        out.append(s)
    return out


def find_best_match(old: str, candidates: list[str], threshold: float) -> tuple[str, float] | None:
    old_n = normalize(old)
    if not old_n:
        return None
    best = None
    best_score = 0.0
    for c in candidates:
        c_n = normalize(c)
        if not c_n:
            continue
        if c_n == old_n:
            return c, 1.0
        score = difflib.SequenceMatcher(None, old_n, c_n).ratio()
        if score > best_score:
            best_score = score
            best = c
    if best and best_score >= threshold:
        return best, best_score
    return None


def is_cosmetic_only(old: str, new: str) -> bool:
    """Difference is only whitespace + em-dash punctuation."""
    a = re.sub(r"[\s\-—,]+", "", old)
    b = re.sub(r"[\s\-—,]+", "", new)
    return a == b


def sync_spec(spec_path: Path, episode_sentences: list[str], threshold: float, apply: bool,
              max_len_ratio: float = 1.5, safe_mode: bool = True) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    chunks = spec.get("sentences", [])
    changes = []
    skipped_merge = 0
    unchanged = 0
    not_matched = 0
    for i, ch in enumerate(chunks):
        old = ch.get("text", "")
        if not old:
            continue
        match = find_best_match(old, episode_sentences, threshold)
        if match is None:
            not_matched += 1
            continue
        new, score = match
        if normalize(old) == normalize(new):
            unchanged += 1
            continue
        if old.strip() == new.strip():
            unchanged += 1
            continue
        if safe_mode:
            ratio = len(new) / max(1, len(old))
            if ratio > max_len_ratio:
                skipped_merge += 1
                continue
        changes.append(
            {
                "chunk_index": i,
                "score": round(score, 3),
                "old": old,
                "new": new,
            }
        )
        if apply:
            ch["text"] = new

    if apply and changes:
        ts = int(time.time())
        bak = spec_path.with_suffix(f".json.bak.sync_{ts}")
        bak.write_text(spec_path.read_text(encoding="utf-8"), encoding="utf-8")
        spec_path.write_text(
            json.dumps(spec, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    return {
        "spec": str(spec_path.relative_to(REPO_ROOT)),
        "total_chunks": len(chunks),
        "changes": len(changes),
        "unchanged": unchanged,
        "not_matched": not_matched,
        "skipped_merge": skipped_merge,
        "details": changes,
    }


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", type=int, required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--threshold", type=float, default=0.85)
    ap.add_argument("--cosmetic-only", action="store_true",
                    help="Skip changes where only whitespace/em-dash differs")
    args = ap.parse_args()

    if args.apply and args.dry_run:
        ap.error("--apply and --dry-run mutually exclusive")
    if not args.apply:
        args.dry_run = True

    ep_dir = REPO_ROOT / "output" / f"ep_{args.episode:02d}"
    md_path = ep_dir / "episode.md"
    sections_dir = ep_dir / "sections"
    if not md_path.exists():
        print(f"[R192] FAIL — missing {md_path}")
        return 2
    if not sections_dir.exists():
        print(f"[R192] FAIL — missing {sections_dir}")
        return 2

    episode_sentences = extract_episode_sentences(md_path)
    print(f"[R192] episode.md sentences extracted: {len(episode_sentences)}")
    print(f"[R192] mode: {'APPLY' if args.apply else 'DRY-RUN'}  threshold: {args.threshold}")

    spec_files = sorted(sections_dir.glob("spec_*.json"))
    spec_files = [s for s in spec_files if not s.name.endswith(".bak") and ".bak" not in s.name]

    total_changes = 0
    for spec_path in spec_files:
        rpt = sync_spec(spec_path, episode_sentences, args.threshold, args.apply)
        print(f"\n[R192] {rpt['spec']}")
        print(
            f"  chunks={rpt['total_chunks']}  changes={rpt['changes']}  "
            f"unchanged={rpt['unchanged']}  not_matched={rpt['not_matched']}"
        )
        for d in rpt["details"]:
            print(f"  ch[{d['chunk_index']}] sim={d['score']}")
            print(f"    OLD: {d['old']}")
            print(f"    NEW: {d['new']}")
        total_changes += rpt["changes"]

    print(f"\n[R192] TOTAL changes across {len(spec_files)} specs: {total_changes}")
    if args.dry_run:
        print("[R192] DRY-RUN only — no files written. Re-run with --apply to commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
