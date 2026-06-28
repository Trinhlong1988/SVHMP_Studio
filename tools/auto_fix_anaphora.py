"""SVHMP R62 — Auto-fix anaphora "người người người" liên tiếp >2.

Strategy: Vary anaphora bằng synonyms ("Người X. Người Y. Người Z." → "Người X. Cô Y. Bên kia, người Z.")

Conservative: chỉ replace 3rd+ instance trong chain với varied phrasing.
"""
import re
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# When word X repeats 3+ times in chain, replace 3rd with these connectors
VARY_PREFIX = {
    'người': ['Bên kia, người', 'Phía sau, người', 'Bên cạnh, người'],
    'cô': ['Cô gái', 'Người phụ nữ', 'Bóng cô'],
    'anh': ['Người đàn ông', 'Bóng anh', 'Anh chàng'],
    'chị': ['Người chị', 'Bóng chị', 'Chị gái'],
    'ông': ['Ông cụ', 'Bóng ông', 'Người ông'],
    'bà': ['Bà cụ', 'Bóng bà', 'Người bà'],
    'em': ['Em ấy', 'Đứa em', 'Em đó'],
    'cụ': ['Cụ già', 'Bóng cụ', 'Người cụ'],
}

def fix_episode(text):
    changes = []
    paragraphs = re.split(r'(\n\s*\n)', text)  # keep separators
    new_paras = []
    for para in paragraphs:
        if not para.strip() or para.startswith('#') or para.startswith('[') or para.startswith('---') or para.startswith('|'):
            new_paras.append(para)
            continue
        sentences = re.split(r'(?<=[.!?])\s+', para)
        new_sents = []
        chain_word = None
        chain_count = 0
        for s in sentences:
            s_strip = s.strip()
            if not s_strip:
                new_sents.append(s)
                continue
            m = re.match(r'^[""\'—\s\(\)]*(\w+)\b', s_strip)
            first = m.group(1).lower() if m else None
            if first and first in {w.lower() for w in VARY_PREFIX}:
                if first == chain_word:
                    chain_count += 1
                    if chain_count >= 2:  # 3rd+ in chain
                        # Replace first word with variation
                        varieties = VARY_PREFIX[first]
                        new_first = varieties[chain_count % len(varieties)]
                        rest = s_strip[m.end():]
                        new_s = new_first + rest
                        changes.append({
                            'from': first,
                            'to': new_first,
                            'context': s_strip[:60],
                        })
                        new_sents.append(new_s)
                        continue
                else:
                    chain_word = first
                    chain_count = 0
            else:
                chain_word = None
                chain_count = 0
            new_sents.append(s)
        new_paras.append(' '.join(new_sents))
    return ''.join(new_paras), changes

def main():
    apply = '--apply' in sys.argv
    print("=" * 70)
    print(f"R62 AUTO-FIX — Anaphora vary | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    print("=" * 70)

    total = 0
    for n in range(1, 91):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        new_text, changes = fix_episode(text)
        if changes:
            total += len(changes)
            print(f"EP{n:02d}: {len(changes)} vary")
            for c in changes[:3]:
                print(f"  '{c['from']}' → '{c['to']}' | {c['context']}")
            if apply:
                shutil.copy2(p, p.with_suffix('.md.bak.R62'))
                p.write_text(new_text, encoding='utf-8')
    print(f"\nTotal: {total} vary")
    if apply:
        print("APPLIED (backups: *.bak.R62)")

if __name__ == '__main__':
    main()
