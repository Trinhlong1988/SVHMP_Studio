"""SVHMP — Auto-fix dialogue hierarchy (R48) using context-aware replacement.

Per EP:
1. Extract passenger info (name, gender, age) from metadata
2. Identify deceased relationship from reveal (con/vợ/chồng/bạn/bà/mẹ/cháu/bố/cô)
3. Smart replace ambiguous "em" patterns in dialogue with relationship word

Approach: identify specific 'em' patterns referring to OTHER person (not speaker):
- "em đem em" → "em đem [relationship_word]"
- "em yêu thầm em" → "em yêu thầm [rel]"
- "em nuôi em" → "em nuôi [rel]"
- etc.

Usage: python tools/auto_fix_dialogue_hierarchy.py [--ep N] [--dry-run]
"""
import re
import sys
import argparse
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).resolve().parents[1]

# Verbs that often precede "em" as object reference (not self-ref)
OBJECT_VERBS = [
    'đem', 'gửi', 'cho', 'tặng', 'đưa', 'mời', 'dìu', 'đỡ',
    'nuôi', 'chăm', 'bồng', 'ôm', 'vuốt',
    'yêu', 'thầm', 'thương', 'quý', 'coi',
    'biết', 'thấy', 'gặp', 'nhớ', 'nhìn', 'tin',
    'để', 'cất', 'giữ', 'mất', 'không thấy',
    'đợi', 'theo', 'tìm', 'gọi', 'báo',
]

def detect_relationship(reveal_text, passenger_age=None):
    """Detect deceased relationship word from reveal section.
    Returns the appropriate replacement word (chị/em/con/bố/mẹ/bà/anh/...)."""
    # Common patterns
    if re.search(r'(?:con (?:trai|gái)|cháu (?:trai|gái))\s+(?:em|tôi)\s*[—-]', reveal_text):
        return 'con'
    if re.search(r'(?:vợ|chồng)\s+(?:em|tôi)\s*[—-]', reveal_text):
        # Speaker is husband/wife — deceased is opposite
        if 'vợ' in reveal_text[:300]:
            return 'em'  # wife (younger) — actually keep complex
        else:
            return 'anh'
    if re.search(r'bà (?:nội|ngoại)\s+(?:em|tôi)', reveal_text):
        return 'bà'
    if re.search(r'mẹ\s+(?:em|tôi)\s*[—-]', reveal_text):
        return 'mẹ'
    if re.search(r'bố\s+(?:em|tôi)\s*[—-]', reveal_text):
        return 'bố'
    if re.search(r'em (?:gái|trai)\s+(?:em|tôi)', reveal_text):
        return 'em'  # younger sibling
    if re.search(r'(?:chị|anh)\s+(?:em|tôi)\s*[—-]', reveal_text):
        # Speaker has older sibling, deceased is sibling
        if 'chị' in reveal_text[:300]:
            return 'chị'
        else:
            return 'anh'
    if re.search(r'bạn (?:cấp ba|cấp hai|đại học|cùng phòng|cùng lớp|thân)', reveal_text):
        return 'bạn'  # friend — same age
    if re.search(r'hàng xóm', reveal_text):
        return 'bác'  # neighbor older
    if re.search(r'(?:người yêu|chồng|vợ) (?:cũ|trước)', reveal_text):
        # Ex-lover/spouse
        if re.search(r'cô(?: ấy)?\s*[—.]', reveal_text):
            return 'em'  # she
        return 'anh'
    if re.search(r'cô\s+\w+\s+mất', reveal_text):
        return 'cô'
    # Default: peer
    return 'bạn'

def extract_passenger_metadata(text):
    """Extract passenger name, gender, age from metadata block."""
    m = re.search(r'passenger_main:\s*([^\n]+)', text)
    if not m:
        return None, None, None
    info = m.group(1)
    # Try patterns: "nam 35 [Name]" or "nu 42 [Name]"
    age_m = re.search(r'(\d{2})', info)
    name_m = re.search(r'(?:nam|nu|nữ)\s*\d*\s*([\wÀ-ỹ]+(?:\s+[\wÀ-ỹ]+)?)', info)
    age = int(age_m.group(1)) if age_m else None
    name = name_m.group(1).strip() if name_m else None
    gender = 'nam' if 'nam' in info[:10].lower() else 'nu'
    return name, gender, age

def extract_reveal_text(text):
    """Extract REVEAL section text."""
    m = re.search(r'#+\s*REVEAL.*?(?=#+\s*(?:PAYOFF|CLIFFHANGER)|$)', text, re.IGNORECASE | re.DOTALL)
    return m.group() if m else ''

def fix_dialogue_hierarchy(text):
    """Fix dialogue pronoun rối in EP text."""
    reveal = extract_reveal_text(text)
    if not reveal:
        return text, 0

    rel = detect_relationship(reveal)
    changes = 0

    def fix_quote(match):
        nonlocal changes
        quote = match.group(1)
        original = quote

        # Pattern 1: "em <object_verb> em" → "em <verb> <rel>"
        # The 2nd em is the object — replace with rel
        for verb in OBJECT_VERBS:
            # "em <verb> em" → "em <verb> <rel>"
            pattern = rf'\bem ({re.escape(verb)})\s+em\b'
            new_quote = re.sub(pattern, rf'em \1 {rel}', quote)
            if new_quote != quote:
                changes += quote.count(f'em {verb} em')
                quote = new_quote

        # Pattern 2: "em yêu thầm em" → "em yêu thầm <rel>"
        pattern = r'\bem yêu thầm em\b'
        new_quote = re.sub(pattern, f'em yêu thầm {rel}', quote)
        if new_quote != quote:
            changes += quote.count('em yêu thầm em')
            quote = new_quote

        # Pattern 3: "em đem em về" → "em đem <rel> về"
        pattern = r'\bem đem em (về|đến|ra|vào)\b'
        new_quote = re.sub(pattern, rf'em đem {rel} \1', quote)
        if new_quote != quote:
            changes += 1
            quote = new_quote

        # Pattern 4: "yêu em [time]" hoặc "thương em [time]"
        pattern = r'\b(yêu|thương|quý|coi) thầm em\b'
        new_quote = re.sub(pattern, rf'\1 thầm {rel}', quote)
        if new_quote != quote:
            changes += 1
            quote = new_quote

        # Pattern 5: "Em <verb> em mới"/"em <verb> em rất" (em chỉ em là)
        pattern = r'\bem coi em (là\s+)?(\w+)'
        new_quote = re.sub(pattern, rf'em coi {rel} \1\2', quote)
        if new_quote != quote:
            changes += 1
            quote = new_quote

        # Pattern 6: "biết em có" / "biết em mất" / "biết em đã"
        for after in ['có', 'không có', 'mất', 'chết', 'đã', 'sẽ', 'sắp']:
            pattern = rf'\bbiết em ({re.escape(after)})\b'
            new_quote = re.sub(pattern, rf'biết {rel} \1', quote)
            if new_quote != quote:
                changes += 1
                quote = new_quote

        # Pattern 7: "em nói thẳng em yêu em" — "em yêu em" (refer to other)
        pattern = r'\bem yêu em\b'
        new_quote = re.sub(pattern, f'em yêu {rel}', quote)
        if new_quote != quote:
            changes += 1
            quote = new_quote

        return '"' + quote + '"'

    new_text = re.sub(r'"([^"]+)"', fix_quote, text)
    return new_text, changes

def process_ep(ep_num, dry_run=False):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists():
        return 0
    text = p.read_text(encoding='utf-8')
    new_text, changes = fix_dialogue_hierarchy(text)
    if not dry_run and changes > 0:
        p.write_text(new_text, encoding='utf-8')
    if changes > 0:
        rel = detect_relationship(extract_reveal_text(text))
        print(f"  EP{ep_num:02d}: {changes} fixes (rel={rel})")
    return changes

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if args.ep:
        process_ep(args.ep, args.dry_run)
    else:
        total = 0
        for n in range(1, 51):
            c = process_ep(n, args.dry_run)
            total += c
        print(f"\nTOTAL: {total} fixes across {sum(1 for n in range(1,51) if (SVHMP/'output'/f'ep_{n:02d}'/'episode.md').exists())} EPs")

if __name__ == '__main__':
    main()
