"""R179 pre-verify — check word ending diacritic BEFORE propose.

Em vi phạm self-verify R86 6 lần hôm nay. Tool này:
1. Take a NEW substitute text
2. Extract last word of each sentence (sentence = split by .!?…)
3. Check diacritic of last word
4. If ngã/nặng/hỏi → FAIL with suggestion

Usage:
  python tools/pre_verify_word_ending.py "Đèn vàng lụi đi, tắt hẳn."
  python tools/pre_verify_word_ending.py --file output/ep_01/episode.md
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path


def get_diacritic(word):
    nfd = unicodedata.normalize("NFD", word)
    if "̃" in nfd: return "NGA"
    if "̉" in nfd: return "HOI"
    if "̣" in nfd: return "NANG"
    if "́" in nfd: return "SAC"
    if "̀" in nfd: return "HUYEN"
    return "NGANG"


def get_last_word(sentence):
    sentence = sentence.strip().rstrip(".,!?…—–-:;")
    if not sentence: return ""
    words = sentence.split()
    return words[-1] if words else ""


def split_sentences(text):
    # Split by period/?/!/…
    parts = re.split(r"([.!?…])", text)
    sentences = []
    current = ""
    for p in parts:
        if p in ".!?…":
            current += p
            sentences.append(current)
            current = ""
        else:
            current += p
    if current.strip():
        sentences.append(current)
    return sentences


def verify_text(text):
    sentences = split_sentences(text)
    violations = []
    for s in sentences:
        last = get_last_word(s)
        if not last: continue
        # Strip leading punctuation like — / em-dash
        last_clean = last.lstrip("—–-").rstrip(".,!?…")
        if not last_clean: continue
        diac = get_diacritic(last_clean)
        if diac in ("NGA", "HOI", "NANG"):
            violations.append((last_clean, diac, s.strip()[:80]))
    return violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text", nargs="?", help="Text to verify")
    ap.add_argument("--file", help="File to scan all sentences")
    args = ap.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    elif args.text:
        text = args.text
    else:
        text = sys.stdin.read()

    print(f"=== R179 Word Ending Pre-Verify ===")
    violations = verify_text(text)
    if not violations:
        print("  ✓ All sentence endings OK (no NGA/HOI/NANG EOL)")
        sys.exit(0)
    print(f"  ✗ {len(violations)} violations:")
    for word, diac, ctx in violations:
        print(f"    {diac} '{word}' in: \"{ctx}\"")
    print()
    print("  → R86 will FAIL. Substitute tail before commit.")
    sys.exit(1)


if __name__ == "__main__":
    main()
