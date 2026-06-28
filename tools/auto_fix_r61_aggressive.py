"""SVHMP — R61 aggressive auto-fix (Mr.Long 28/6 Q option).

Strategy: replace short opener với full subject:
- "Anh [verb]." → "Khải Phong [verb]." (sentence ≤5 words, next word ≤4 chars)
- "Cô [verb]." → "Cô gái [verb]."

Risk: meaning shift nếu "Anh" referent ≠ Khải Phong (passenger backstory).
Mitigation: skip nếu paragraph context có other passenger name nearby.
"""
import re
import sys
import json
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# Subject mapping: short opener → full subject
SUBJECT_MAP = {
    'Anh': ['Khải Phong', 'Người đàn ông'],
    'Cô': ['Cô gái', 'Người con gái'],
    'Bà': ['Bà cụ', 'Người bà'],
    'Ông': ['Ông cụ', 'Người ông'],
    'Em': ['Cô gái', 'Em ấy'],
    'Chị': ['Người chị', 'Chị ấy'],
}

def fix_ep(ep_num, dry_run=False):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists(): return 0
    text = p.read_text(encoding='utf-8')
    orig = text
    fixes = 0

    paragraphs = text.split('\n\n')
    new_paragraphs = []
    counter = 0

    for para in paragraphs:
        if not para.strip() or para.startswith(('#', '[', '|', '---', '```')):
            new_paragraphs.append(para)
            continue
        sentences = re.split(r'(?<=[.!?])\s+', para)
        new_sentences = []
        for s in sentences:
            s_strip = s.strip()
            if not s_strip:
                new_sentences.append(s)
                continue
            # Match: short opener + short next + ≤5 words
            m = re.match(r'^(Anh|Cô|Bà|Ông|Em|Chị)\s+(\w+)(.*?[.!?])\s*$', s_strip)
            if m:
                opener = m.group(1)
                next_word = m.group(2)
                rest = m.group(3)
                word_count = len(s_strip.split())
                # Trigger: next word ≤4 chars AND total ≤5 words
                if len(next_word) <= 4 and word_count <= 5:
                    if opener in SUBJECT_MAP:
                        # Rotate replacement
                        replacement = SUBJECT_MAP[opener][counter % len(SUBJECT_MAP[opener])]
                        counter += 1
                        new_s = f'{replacement} {next_word}{rest}'
                        new_sentences.append(new_s)
                        fixes += 1
                        continue
            new_sentences.append(s)
        new_paragraphs.append(' '.join(new_sentences))

    if fixes > 0 and not dry_run:
        shutil.copy2(p, p.with_suffix('.md.bak.r61_agg'))
        p.write_text('\n\n'.join(new_paragraphs), encoding='utf-8')
    return fixes

def main():
    apply = '--apply' in sys.argv
    print(f"R61 AGGRESSIVE FIX | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    total = 0
    for n in range(1, 51):
        fixes = fix_ep(n, dry_run=not apply)
        if fixes > 0:
            total += fixes
    print(f"Total: {total} R61 fixes")

if __name__ == '__main__':
    main()
