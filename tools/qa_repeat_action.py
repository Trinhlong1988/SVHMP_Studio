"""R113 — Action verb repeat audit.

Rule: 1 hành động phrase ≥3 từ KHÔNG được lặp >2 lần / episode cùng wording.
Nếu cần lặp >2 phải VARIED wording (chủ ý + uyển chuyển).

Scan phrases:
  - liếc gương chiếu hậu
  - cúi đầu / cúi xuống / cúi nhìn
  - ngẩng đầu / ngẩng lên
  - gật đầu / khẽ gật
  - nhìn xuống / nhìn ra / nhìn sang / nhìn lên
  - đưa mắt / quay đầu
  - mang theo / theo người
  - thở ra / hơi thở
  - cô không hỏi thêm / không nói thêm

Threshold: phrase repeat count > 2 = VIOLATION
"""
import re
import sys
from pathlib import Path

EPISODE = Path(r"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/output/ep_01/episode.md")

# Phrases to scan — exact phrase match
PHRASES = [
    # Action verbs
    "liếc gương chiếu hậu",
    "liếc nhìn gương chiếu hậu",
    "cúi đầu",
    "cúi xuống",
    "cúi nhìn",
    "ngẩng đầu",
    "ngẩng lên",
    "gật đầu",
    "nhìn xuống",
    "nhìn ra",
    "nhìn sang",
    "nhìn lên",
    "đưa mắt",
    "quay đầu",
    "ôm radio",
    # Repeat phrases
    "mang theo người",
    "theo người đêm nay",
    "thở ra một hơi",
    "hơi thở chậm",
    "không hỏi thêm câu nào",
    "không nói thêm",
    "không hỏi gì",
    "im lặng hồi lâu",
]

# Whitelist — onomatopoeia / intentional anchor phrases
WHITELIST = {
    "rì rì",  # engine
    "rả rích",  # rain
}

THRESHOLD = 2  # Max occurrences


def cut_metadata(text):
    """Strip codeblock + post-narration metadata."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    for marker in ("# SELF-CHECK", "# NOTES", "## SOUL", "## REVIEW", "## NARRATION", "## EMOTION"):
        idx = text.find(marker)
        if idx >= 0:
            text = text[:idx]
    return text


def scan_phrase_repeats(text):
    """Find phrases occurring > THRESHOLD times."""
    violations = []
    for phrase in PHRASES:
        if phrase in WHITELIST:
            continue
        # Case-insensitive count, word boundary aware
        pattern = re.escape(phrase)
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        n = len(matches)
        if n > THRESHOLD:
            # Find lines containing it
            lines = []
            for ln, line in enumerate(text.split("\n"), 1):
                if phrase.lower() in line.lower():
                    lines.append((ln, line[:80]))
            violations.append((phrase, n, lines))
    return violations


def scan_action_clusters(text):
    """Scan 4-word phrases starting with action verb that repeat ≥3 times."""
    action_starts = ["liếc", "cúi", "ngẩng", "nhìn", "đưa", "gật", "quay", "ôm", "mang", "thở", "buông"]
    lines = [l for l in text.split("\n") if l.strip() and not l.startswith(("#", "[", "```", "---", "|"))]
    full = " ".join(lines).lower()
    phrases_seen = {}
    # Generate 4-word windows starting with action verbs
    words = full.split()
    for i in range(len(words) - 3):
        if any(words[i].startswith(a) for a in action_starts):
            phrase = " ".join(words[i:i+4])
            # Strip punctuation
            phrase_clean = re.sub(r"[.,!?…—\-:;\"]", "", phrase).strip()
            if len(phrase_clean) > 10:
                phrases_seen[phrase_clean] = phrases_seen.get(phrase_clean, 0) + 1
    clusters = [(p, n) for p, n in phrases_seen.items() if n > 2]
    return sorted(clusters, key=lambda x: -x[1])


def main():
    text = EPISODE.read_text(encoding="utf-8")
    text_clean = cut_metadata(text)

    print("=== R113 REPEAT ACTION AUDIT ===\n")

    print("[1] Exact phrase repeat > 2:")
    violations = scan_phrase_repeats(text_clean)
    for phrase, n, lines in violations:
        print(f"\n  ⚠️ '{phrase}' x{n}:")
        for ln, ctx in lines:
            print(f"    L{ln}: {ctx}")

    print()
    print("[2] Action-verb 4-word cluster repeat > 2:")
    clusters = scan_action_clusters(text_clean)
    for phrase, n in clusters[:10]:
        print(f"  ⚠️ x{n} '{phrase[:70]}'")

    fail = len(violations) + len(clusters) > 0
    print()
    print(f"== R113 GATE: {'FAIL - FIX REQUIRED' if fail else 'PASS'} ==")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
