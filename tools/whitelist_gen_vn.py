"""Generate exhaustive Vietnamese reduplication whitelist.

Mr.Long lệnh 29/6: chặn vector "whitelist gap" — em ship Round 19.14 whitelist
18 từ, thiếu "dần" → QA WATCH 22 iter waste 22 phút detect "dần dần" false positive.

Vietnamese reduplication patterns (từ láy):
- Tượng thanh (onomatopoeia): rì rì, vù vù, lộc cộc, lách cách, ầm ầm...
- Tượng hình (form): lúp xúp, ngơ ngẩn, lập loè...
- Intensification (degree): chậm chậm, nhẹ nhẹ, từ từ, dần dần...
- Modulator (manner): rón rón, khe khẽ, le lói...

Usage:
    python tools/whitelist_gen_vn.py                  # write data/vn_reduplication_whitelist.json
    python tools/whitelist_gen_vn.py --count          # count + show categories
    python tools/whitelist_gen_vn.py --add <word>     # extend manually
    python tools/whitelist_gen_vn.py --update-qa      # patch qa_watch.py WHITELIST_REDUP từ JSON
"""
import json
import re
import sys
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
WHITELIST_JSON = SVHMP / "data" / "vn_reduplication_whitelist.json"


# Exhaustive list — base words có thể duplicate back-to-back trong Vietnamese natural
# Chỉ lưu SINGLE word (qa_watch logic: w1 == w2 same word)
REDUPLICATION = {
    # === ONOMATOPOEIA tượng thanh ===
    "tượng_thanh": [
        "rì", "rầm", "ầm", "ù", "vù", "phù", "xì", "lụp", "lụt", "lúp",
        "lách", "lộc", "tách", "cạch", "leng", "lanh", "róc", "ò", "vo", "ve",
        "kẽo", "lạch", "lép", "bép", "bùng", "đùng", "rì",
        "khò", "khẹt", "phù", "phì", "rít", "rin", "bẹp", "chát", "chát",
        "lốp", "tóp", "tép", "tạch", "tích", "tóc",
        "rít", "kẹt", "róc", "rách", "rộn", "rộp", "ráp",
    ],
    # === TƯỢNG HÌNH (form/state) ===
    "tượng_hình": [
        "lúp", "lúng", "loạng", "ngúng", "lóng", "lập", "lò",
        "ngúc", "ngơ", "ngẩn", "lập", "lờ", "đăm", "thoăn", "thoắt",
        "lụng", "lủng", "lập", "phập", "phồng",
        "lấp", "ló", "le", "lói", "lập", "loè", "nhấp", "nhô",
        "lẳng", "lặng", "lim", "dim", "đăm",
    ],
    # === INTENSIFICATION (cường độ tăng) ===
    "cường_độ": [
        "chậm", "nhẹ", "khẽ", "từ", "dần", "đần",
        "mãi", "hoài", "luôn", "mải",
        "thoáng", "thỉnh", "thi", "thoáng",
        "lai", "lác", "lai", "rai",
        "ngày", "đêm", "tháng", "năm",  # "ngày ngày" / "đêm đêm" idiom
    ],
    # === MODULATOR (manner) ===
    "modulator": [
        "rón", "lẳng", "lặng", "le", "lấp", "ló",
        "chầm", "chậm", "thoăn", "thoắt",
        "thì", "thầm", "lập", "lờ", "chập", "chờn",
        "thấp", "thoáng",
    ],
    # === FREQUENCY/RHYTHM ===
    "tần_số": [
        "đăm", "đắm", "ngơ", "ngẩn",
        "khắc", "khoải", "trĩu", "trĩu",
        "thui", "thủi",
    ],
    # === HORROR/EMOTIONAL (SVHMP genre) ===
    "horror_emotion": [
        "rợn", "rùng", "run", "rẩy",
        "ngấn", "ngấn", "lăn", "lăn",
        "rơi", "rớt",  # "rơi rơi" / "rớt rớt" tear motion
        "ấm", "ức",
    ],
}


def all_words():
    """Flatten all categories → set of unique words."""
    s = set()
    for cat in REDUPLICATION.values():
        s.update(cat)
    return s


def write_json():
    WHITELIST_JSON.parent.mkdir(exist_ok=True, parents=True)
    data = {
        "schema": "vn_reduplication_whitelist_v1",
        "description": "Vietnamese reduplication whitelist cho R98 duplicate word detect",
        "generated_by": "tools/whitelist_gen_vn.py",
        "categories": REDUPLICATION,
        "all_words": sorted(all_words()),
        "count": len(all_words()),
    }
    WHITELIST_JSON.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"[WRITE] {WHITELIST_JSON} ({len(all_words())} words, {len(REDUPLICATION)} categories)")


def show_count():
    print(f"=== Vietnamese reduplication whitelist ===")
    print(f"Categories: {len(REDUPLICATION)}")
    for cat, words in REDUPLICATION.items():
        unique = sorted(set(words))
        print(f"  {cat}: {len(unique)} words — {', '.join(unique[:8])}...")
    print(f"\nTotal unique words: {len(all_words())}")


def update_qa_watch():
    """Patch qa_watch.py WHITELIST_REDUP từ JSON."""
    if not WHITELIST_JSON.exists():
        write_json()
    data = json.loads(WHITELIST_JSON.read_text(encoding="utf-8"))
    words = sorted(data["all_words"])

    qa_watch = SVHMP / "tools" / "qa_watch.py"
    text = qa_watch.read_text(encoding="utf-8")

    # Build new WHITELIST_REDUP block
    new_block_lines = ["WHITELIST_REDUP = {"]
    line = "    "
    for w in words:
        addition = f'"{w}", '
        if len(line) + len(addition) > 100:
            new_block_lines.append(line.rstrip())
            line = "    "
        line += addition
    if line.strip():
        new_block_lines.append(line.rstrip())
    new_block_lines.append("}")
    new_block = "\n".join(new_block_lines)

    # Replace WHITELIST_REDUP block (multiline)
    pat = re.compile(r"WHITELIST_REDUP\s*=\s*\{[^}]*\}", re.DOTALL)
    if not pat.search(text):
        print("[ERR] WHITELIST_REDUP block not found in qa_watch.py")
        return 1

    new_text = pat.sub(new_block, text, count=1)
    qa_watch.write_text(new_text, encoding="utf-8")
    print(f"[PATCH] qa_watch.py WHITELIST_REDUP updated với {len(words)} words")
    return 0


def add_word(word):
    """Add word to default 'modulator' category + write JSON."""
    if word in all_words():
        print(f"[SKIP] '{word}' already in whitelist")
        return
    REDUPLICATION["modulator"].append(word)
    write_json()
    print(f"[ADD] '{word}' added to modulator category")


def main():
    if len(sys.argv) < 2:
        write_json()
        return 0
    arg = sys.argv[1]
    if arg == "--count":
        show_count()
        return 0
    if arg == "--update-qa":
        return update_qa_watch()
    if arg == "--add":
        if len(sys.argv) < 3:
            print("Usage: --add <word>")
            return 2
        add_word(sys.argv[2])
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
