"""SVHMP — AGGRESSIVE anaphora chain breaker (Mr.Long 28/6 zero tolerance).

KHÔNG check word count limit, KHÔNG skip.
EVERY chain ≥3 → vary middle sentences EVERY pass.

Synonym pool expanded để rotate qua nhiều iterations:
"""
import re
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(__file__).resolve().parents[1]

TRIGGER_WORDS = {'Khải-Phong', 'Khải', 'Cô', 'Anh', 'Bà', 'Ông', 'Em', 'Tôi', 'Bác'}

# Diverse synonym pool — cycle through them
SYNONYMS = {
    'Anh': ['Người đàn ông', 'Người khách', 'Người ngồi đó', 'Bóng anh', 'Anh ấy', 'Người kia'],
    'Cô': ['Người con gái', 'Cô ấy', 'Cô gái ấy', 'Bóng cô', 'Người nữ', 'Cô gái đó'],
    'Khải-Phong': ['Anh ấy', 'Người khách ghế bảy', 'Người ngồi ghế bảy', 'Anh khách'],
    'Khải': ['Anh ấy', 'Người ngồi ghế bảy'],
    'Bà': ['Bà cụ ấy', 'Người bà', 'Người phụ nữ già', 'Bà già'],
    'Ông': ['Ông cụ ấy', 'Người ông', 'Người đàn ông già', 'Cụ ông'],
    'Em': ['Cô ấy', 'Người trẻ', 'Cô em', 'Cậu em'],
    'Tôi': ['Người kể', 'Tôi đây', 'Người này'],
    'Bác': ['Bác ấy', 'Người bác', 'Bác kia'],
}

# Round-robin counter across all replacements
counter = [0]

def get_synonym(word):
    pool = SYNONYMS.get(word, [])
    if not pool: return None
    syn = pool[counter[0] % len(pool)]
    counter[0] += 1
    return syn

def process_ep(ep_num, dry_run=True):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists(): return 0
    text = p.read_text(encoding='utf-8')

    paragraphs = text.split('\n\n')
    new_paragraphs = []
    fixes = 0
    for para in paragraphs:
        if not para.strip() or para.startswith(('#', '[', '|', '---', '```')):
            new_paragraphs.append(para)
            continue
        sentences = re.split(r'(?<=[.!?])\s+', para)
        chain = []
        chain_indices = []
        for i, s in enumerate(sentences):
            s_strip = s.strip()
            first = s_strip.split()[0] if s_strip else ''
            if first in TRIGGER_WORDS:
                chain.append(first)
                chain_indices.append(i)
            else:
                if len(chain) >= 3:
                    # Vary EVERY sentence in chain at position 2+ (index 1, 2, 3...)
                    for pos, idx in enumerate(chain_indices):
                        if pos >= 1:  # vary from 2nd sentence onwards (chain ≥3 means at least 2 vary)
                            w = chain[pos]
                            syn = get_synonym(w)
                            if syn:
                                sentences[idx] = re.sub(rf'^{re.escape(w)}\b', syn, sentences[idx], count=1)
                                fixes += 1
                chain = []
                chain_indices = []
        # Trailing chain
        if len(chain) >= 3:
            for pos, idx in enumerate(chain_indices):
                if pos >= 1:
                    w = chain[pos]
                    syn = get_synonym(w)
                    if syn:
                        sentences[idx] = re.sub(rf'^{re.escape(w)}\b', syn, sentences[idx], count=1)
                        fixes += 1

        new_paragraphs.append(' '.join(sentences))

    if fixes > 0 and not dry_run:
        shutil.copy2(p, p.with_suffix('.md.bak.aggressive'))
        p.write_text('\n\n'.join(new_paragraphs), encoding='utf-8')
    return fixes

def main():
    apply = '--apply' in sys.argv
    print(f"AGGRESSIVE ANAPHORA BREAKER — EP02-50 | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    total = 0
    for n in range(2, 51):
        fixes = process_ep(n, dry_run=not apply)
        if fixes > 0:
            total += fixes
    print(f"Total: {total} subject vary")

if __name__ == '__main__':
    main()
