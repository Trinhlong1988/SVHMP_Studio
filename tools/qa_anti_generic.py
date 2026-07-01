"""R128 — Anti-Generic AI Detection.

Cấm/giới hạn dấu hiệu văn AI:
  - "Một cảm giác khó tả"
  - "Không ai biết rằng..."
  - "Trong khoảnh khắc ấy..."
  - "Có lẽ..."
  - "Từ đó về sau..."
  - "Bỗng nhiên", "đột nhiên" (overuse)
  - "im lặng", "lạnh sống lưng", "rợn người", "rùng mình", "nuốt nước bọt"

Threshold: mỗi cụm max 1 lần / EP (trừ chủ ý).
"""
import re
import sys
from pathlib import Path

EPISODE = Path(__file__).resolve().parents[1] / r'output/ep_01/episode.md'

# Anti-generic phrase DB (max occurrences per EP)
GENERIC_PHRASES = {
    "một cảm giác khó tả": 0,  # forbidden
    "không ai biết rằng": 0,
    "trong khoảnh khắc ấy": 0,
    "từ đó về sau": 0,
    "có lẽ": 2,  # max 2 per EP
    "bỗng nhiên": 2,
    "đột nhiên": 2,
    "im lặng": 3,
    "lạnh sống lưng": 1,
    "rợn người": 1,
    "rùng mình": 2,
    "nuốt nước bọt": 1,
    "không hiểu sao": 2,
    "khó tả": 1,
}

# AI-pattern detection (50 sentences same structure)
def cut_metadata(text):
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    for marker in ("# SELF-CHECK", "# NOTES", "## SOUL", "## REVIEW", "## NARRATION", "## EMOTION"):
        idx = text.find(marker)
        if idx >= 0:
            text = text[:idx]
    return text


def scan_generic(text):
    violations = []
    text_lc = text.lower()
    for phrase, max_count in GENERIC_PHRASES.items():
        count = text_lc.count(phrase)
        if count > max_count:
            violations.append((phrase, count, max_count))
    return violations


def scan_sentence_structure(text):
    """Detect repeated structure pattern (Subject + Verb same start >5 consecutive)."""
    sentences = re.split(r"(?<=[.!?…])\s+", text)
    starts = []
    for s in sentences:
        s = s.strip()
        if not s or s.startswith(("#", "[", "—")): continue
        words = s.split()[:2]
        if len(words) >= 2:
            starts.append(" ".join(words))
    # Find consecutive same start
    streaks = []
    cur_start = None
    cur_streak = 0
    for st in starts:
        if st == cur_start:
            cur_streak += 1
        else:
            if cur_streak >= 4:
                streaks.append((cur_start, cur_streak))
            cur_start = st
            cur_streak = 1
    return streaks


def main():
    text = EPISODE.read_text(encoding="utf-8")
    text_clean = cut_metadata(text)

    print("=== R128 ANTI-GENERIC AI DETECTION ===\n")
    print("[1] Generic phrase overuse:")
    violations = scan_generic(text_clean)
    for phrase, count, max_c in violations:
        print(f"  ⚠️ '{phrase}' x{count} (max {max_c})")
    if not violations:
        print("  ✓ All within limit")

    print("\n[2] Repeated sentence structure (≥4 consecutive same start):")
    streaks = scan_sentence_structure(text_clean)
    for start, n in streaks:
        print(f"  ⚠️ '{start}...' x{n} consecutive")
    if not streaks:
        print("  ✓ No structural repeat")

    fail = len(violations) + len(streaks) > 0
    print(f"\n== R128 GATE: {'FAIL - FIX REQUIRED' if fail else 'PASS'} ==")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
