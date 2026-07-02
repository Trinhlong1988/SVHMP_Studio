"""R92b + R95 QA — Cách gọi, cách xưng hô, social hierarchy.

Detect violations:
  1. Khải-Phong (anh trung niên) dùng "thưa cô"/"thưa cô gái" (inverse hierarchy)
  2. Khải-Phong nói về Hạ-Vy mà dùng "cô gái ấy" (should be "cô ấy" or "Hạ-Vy")
  3. Character name count > 6/episode (R95)
  4. Repeat chủ thể consecutive ("Anh tự nhủ ... Anh tự nhủ ...")
"""
import re
import sys
from pathlib import Path

EPISODE = Path(__file__).resolve().parents[1] / r'output/ep_01/episode.md'


def cut_metadata(text):
    """Strip codeblock + post-narration metadata."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    for marker in ("# SELF-CHECK", "# NOTES", "## SOUL", "## REVIEW", "## NARRATION", "## EMOTION"):
        idx = text.find(marker)
        if idx >= 0:
            text = text[:idx]
    return text


def scan_honorific(text):
    violations = []
    lines = text.split("\n")
    for ln, line in enumerate(lines, 1):
        if line.startswith(("#", "[", "---", "```", "|", ">")):
            continue
        line_lc = line.lower()
        # 1. Khải-Phong dùng "thưa cô gái" / "thưa cô" / "thưa em" (anh > cô gái trẻ KHÔNG thưa)
        if re.search(r"thưa\s+(cô\s*gái|cô|em|chị|nàng)", line_lc):
            # Skip if cô gái asking chú (correct hierarchy)
            if "thưa chú" in line_lc or "thưa ông" in line_lc or "thưa bác" in line_lc:
                continue
            violations.append((ln, "HIERARCHY: 'thưa cô/cô gái' (anh không xưng thưa với cô gái trẻ)", line[:100]))
        # 2. "cô gái ấy" trong narration về Hạ-Vy (should be "cô ấy")
        if "cô gái ấy" in line_lc and "ghế tám" not in line_lc:
            violations.append((ln, "REFERENCE: 'cô gái ấy' về Hạ-Vy (dùng 'cô ấy')", line[:100]))
    return violations


def scan_name_count(text):
    """R95 character name max 6/episode."""
    names = ["Khải-Phong", "Hạ-Vy"]
    counts = {n: text.count(n) for n in names}
    violations = []
    for n, c in counts.items():
        if c > 6:
            violations.append(f"R95: {n} = {c} occurrences (max 6)")
    return violations, counts


def scan_consecutive_subject(text):
    """R92b layer 3: consecutive sentences with same subject."""
    violations = []
    pronouns = ("Anh", "Cô ấy", "Cô", "Hạ-Vy", "Khải-Phong", "Ông cụ", "Bác tài", "Tôi")
    paragraphs = re.split(r"\n\n+", text)
    for para in paragraphs:
        sents = re.split(r"(?<=[.!?…])\s+", para.strip())
        for i in range(len(sents) - 1):
            s1, s2 = sents[i].strip(), sents[i+1].strip()
            for p in pronouns:
                if s1.startswith(p) and s2.startswith(p):
                    # Skip if pronoun part of dialogue marker
                    if s1.startswith("—") or s2.startswith("—"):
                        continue
                    violations.append(f"Consecutive '{p}' subject: '{s1[:50]}...' + '{s2[:50]}...'")
                    break
    return violations


def main():
    text = EPISODE.read_text(encoding="utf-8")
    text_clean = cut_metadata(text)

    print("=== QA HONORIFIC + XƯNG HÔ + R95 + REPEAT ===\n")

    print("[1] HONORIFIC/REFERENCE violations:")
    h = scan_honorific(text_clean)
    for ln, kind, ctx in h:
        print(f"  L{ln} {kind}: {ctx}")
    print(f"  Total: {len(h)}\n")

    print("[2] R95 Character name count (max 6):")
    name_violations, counts = scan_name_count(text_clean)
    for n, c in counts.items():
        marker = " ✗ VƯỢT" if c > 6 else " ✓"
        print(f"  {n}: {c}{marker}")
    print()

    print("[3] R92b Consecutive subject repeat:")
    r = scan_consecutive_subject(text_clean)
    for v in r[:10]:
        print(f"  {v}")
    print(f"  Total: {len(r)}\n")

    fail = len(h) + len(name_violations) + len(r) > 0
    print(f"== GATE: {'FAIL - FIX REQUIRED' if fail else 'PASS'} ==")
    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
