"""R111 — TTS phonetic safe-word audit.

BigVGAN vocoder tạo "phù phù" artifact với:
  - Aspirated consonant "h" sau open vowel (thở ra, hơi thở)
  - Long open vowel ending + period (an toàn., cao vút.)
  - Short standalone fragment EOL (cao vút., to lớn.)
  - "Hơi" / "thở" combos

Phrase database — Mr.Long catch session 29-30/6:
  - "thở ra một hơi"
  - "Hơi thở chậm lại"
  - "tới nơi an toàn"
  - "đến nơi an toàn"
  - "cao vút"
  - "ghế trống số bảy đó" (period after "đó" aspirated)
  - "kể lại bao giờ"

Propose safe substitute.
"""
import re
import sys
from pathlib import Path

EPISODE = Path(r"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/output/ep_01/episode.md")

# Database: trigger phrase → safe substitute
PHONETIC_SAFE_DB = {
    "thở ra một hơi": "buông một hơi",
    "thở ra hơi": "buông hơi",
    "Hơi thở chậm lại": "Lồng ngực anh chậm lại",
    "tới nơi an toàn": "hạ cánh êm xuôi",
    "đến nơi an toàn": "hạ cánh êm xuôi",
    "đáp xuống bình an": "hạ cánh êm xuôi",
    "bình an.": "êm xuôi,",
    "an toàn.": "êm xuôi,",
    "cabin.": "cabin xe,",
    "phút...": "phút,",
    "Bác không nói.": "Bác không nói lời nào.",
    "cao vút.": "thật cao,",
    "ghế trống số bảy đó.": "chiếc ghế bỏ trống số bảy,",
    "kể lại bao giờ": "kể ra lần nào",
    "phù phù": "khe khẽ",
}

# Patterns regex
PHONETIC_PATTERNS = [
    (r"\bthở (?:ra|dài|hắt)\s+(?:một|hơi)", "Aspirated 'thở ra/thở dài/thở hắt' → use 'buông/trút'"),
    (r"hơi thở\s+(?:chậm|dài|nặng)", "'hơi thở X' → 'lồng ngực X' / 'nhịp thở X'"),
    (r"(?:an toàn|cao vút|chân thật|thân thiện)\.\s*$", "Open vowel + period EOL → soften/extend"),
]


def cut_metadata(text):
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    for marker in ("# SELF-CHECK", "# NOTES", "## SOUL", "## REVIEW", "## NARRATION", "## EMOTION"):
        idx = text.find(marker)
        if idx >= 0:
            text = text[:idx]
    return text


def scan_phonetic_unsafe(text):
    violations = []
    lines = text.split("\n")
    for ln, line in enumerate(lines, 1):
        if line.startswith(("#", "[", "```", "---", "|")):
            continue
        # Database exact match
        for trigger, substitute in PHONETIC_SAFE_DB.items():
            if trigger.lower() in line.lower():
                violations.append((ln, trigger, substitute, line[:100]))
        # Pattern match
        for pattern, hint in PHONETIC_PATTERNS:
            for m in re.finditer(pattern, line, flags=re.IGNORECASE | re.MULTILINE):
                if not any(v[1] in m.group(0).lower() for v in violations):
                    violations.append((ln, m.group(0), hint, line[:100]))
    return violations


def main():
    text = EPISODE.read_text(encoding="utf-8")
    text_clean = cut_metadata(text)

    print("=== R111 TTS PHONETIC SAFE-WORD AUDIT ===\n")
    violations = scan_phonetic_unsafe(text_clean)
    for ln, trigger, substitute, ctx in violations:
        print(f"  ⚠️ L{ln} '{trigger}' → '{substitute}'")
        print(f"     Context: {ctx}")

    fail = len(violations) > 0
    print(f"\n== R111 GATE: {'FAIL - FIX REQUIRED' if fail else 'PASS'} ==")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
