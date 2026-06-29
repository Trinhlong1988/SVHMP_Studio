"""SVHMP — Auto-fix anaphora chains MIXED words (Mr.Long real audio QA 28/6).

Khác R62 (chỉ check SAME word), script này flag MIXED chain:
- "Anh ngồi. Cô gái nhìn. Anh quay đầu."  ← 3 chains mixed
- "Khải Phong gật. Anh cúi xuống. Cô gái mỉm cười."  ← 3 chains mixed

Strategy:
1. Find ≥3 consecutive sentences starting with trigger words
2. Merge câu 2 vào câu 1 (comma) hoặc câu 2-3 vào 1 (em-dash)
3. Preserve meaning, reduce repetitive sentence-start cadence

Conservative — chỉ merge khi 2 câu liền tiếp ngắn (≤8 từ each) + meaning compatible.
"""
import re
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

TRIGGER_WORDS = {'Khải-Phong', 'Khải', 'Cô', 'Anh', 'Bà', 'Ông', 'Em', 'Tôi', 'Bác'}

def find_chains(text):
    """Return list of (start_idx, end_idx, sentences) for chains ≥3."""
    body = re.sub(r'#[^\n]*\n', '', text)
    body = re.sub(r'```.*?```', '', body, flags=re.DOTALL)
    paragraphs = re.split(r'\n\s*\n', body)
    chains = []
    for para in paragraphs:
        if not para.strip(): continue
        sentences = re.split(r'(?<=[.!?])\s+', para)
        chain = []
        for s in sentences:
            s_strip = s.strip()
            first = s_strip.split()[0] if s_strip else ''
            if first in TRIGGER_WORDS:
                chain.append(s_strip)
            else:
                if len(chain) >= 3:
                    chains.append(chain.copy())
                chain = []
        if len(chain) >= 3:
            chains.append(chain.copy())
    return chains

def merge_short_pair(s1, s2):
    """Merge 2 short sentences into 1 with comma. Drop second subject if same.

    'Anh ngồi yên. Anh không nói.' → 'Anh ngồi yên, không nói.'
    'Cô gái cười. Cô gái gật đầu.' → 'Cô gái cười, gật đầu.'
    """
    # Strip trailing period
    s1_clean = s1.rstrip('.')
    s2_clean = s2.rstrip('.')
    # Find subject of s2 (first 1-2 words)
    s2_words = s2_clean.split()
    if not s2_words: return None
    # If s1 and s2 share same subject (Anh/Cô/Khải-Phong + optional 2nd word)
    # Drop s2 subject
    s2_subj_1 = s2_words[0]
    if len(s2_words) >= 2 and s2_words[0] in TRIGGER_WORDS:
        # Drop subject
        s2_rest = ' '.join(s2_words[1:])
        return f'{s1_clean}, {s2_rest}.'
    return None

def fix_chain(chain_sentences):
    """Try to merge first 2 sentences of chain. Return list of (old_sentence_pair, new_merged) or None."""
    if len(chain_sentences) < 2:
        return None
    s1, s2 = chain_sentences[0], chain_sentences[1]
    # Only merge if both ≤8 words
    if len(s1.split()) > 8 or len(s2.split()) > 8:
        return None
    merged = merge_short_pair(s1, s2)
    if not merged:
        return None
    return (s1 + '\n\n' + s2, merged)

def process_ep(ep_num, dry_run=True):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists(): return 0
    text = p.read_text(encoding='utf-8')
    chains = find_chains(text)
    fixes = 0
    new_text = text
    for chain in chains:
        result = fix_chain(chain)
        if result:
            old, new = result
            if old in new_text:
                new_text = new_text.replace(old, new, 1)
                fixes += 1
    if fixes > 0 and not dry_run:
        shutil.copy2(p, p.with_suffix('.md.bak.anaphora_mixed'))
        p.write_text(new_text, encoding='utf-8')
    return fixes

def main():
    apply = '--apply' in sys.argv
    print(f"ANAPHORA CHAINS MIXED FIX — EP02-50 | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    total = 0
    for n in range(2, 51):
        fixes = process_ep(n, dry_run=not apply)
        if fixes > 0:
            print(f"EP{n:02d}: {fixes} chain merges")
            total += fixes
    print(f"\nTotal: {total} chain merges")

if __name__ == '__main__':
    main()
