"""SVHMP — Auto-fix anaphora chains by VARYING subject mid-chain.

Strategy: tìm chain ≥3, vary subject của câu thứ 2 hoặc 3 bằng synonym.

Synonyms:
  Anh → "Người đàn ông" / "Người khách"
  Cô → "Người con gái" / "Cô gái ấy"
  Khải-Phong → "Anh ấy" / "Người khách ngồi ghế bảy"
  Bà → "Bà cụ ấy" / "Người bà"
  Ông → "Ông cụ ấy" / "Người ông"
  Em → "Cô bé ấy" / "Cậu trai" (context-dependent)
  Tôi → "Người kể chuyện" (rare narrative)
  Bác → "Bác ấy"

Mr.Long 28/6: "bất kể từ gì không được lặp liền nhau quá 2 lần"
"""
import re
import sys
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

TRIGGER_WORDS = {'Khải-Phong', 'Khải', 'Cô', 'Anh', 'Bà', 'Ông', 'Em', 'Tôi', 'Bác'}

SYNONYMS = {
    'Anh': ['Người đàn ông', 'Người khách'],
    'Cô': ['Người con gái', 'Cô ấy'],
    'Khải-Phong': ['Anh ấy', 'Người khách ngồi ghế bảy'],
    'Khải': ['Anh ấy'],
    'Bà': ['Bà cụ ấy', 'Người bà'],
    'Ông': ['Ông cụ ấy', 'Người ông'],
    'Em': ['Cô ấy', 'Em ấy'],
    'Tôi': ['Người kể chuyện'],
    'Bác': ['Bác ấy'],
}

def process_ep(ep_num, dry_run=True):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists(): return 0
    text = p.read_text(encoding='utf-8')

    # Process paragraph by paragraph
    paragraphs = text.split('\n\n')
    new_paragraphs = []
    fixes = 0
    for para in paragraphs:
        if not para.strip() or para.startswith(('#', '[', '|', '---', '```')):
            new_paragraphs.append(para)
            continue
        sentences = re.split(r'(?<=[.!?])\s+', para)
        chain = []
        # Find chains + vary middle
        new_sentences = []
        for i, s in enumerate(sentences):
            s_strip = s.strip()
            first = s_strip.split()[0] if s_strip else ''
            if first in TRIGGER_WORDS:
                chain.append((i, first, s_strip))
            else:
                # Process chain
                if len(chain) >= 3:
                    # Vary every 3rd sentence in chain
                    for idx_in_chain, (orig_i, w, txt) in enumerate(chain):
                        if idx_in_chain >= 2 and idx_in_chain % 2 == 0:  # vary index 2, 4, 6...
                            if w in SYNONYMS and SYNONYMS[w]:
                                syn = SYNONYMS[w][idx_in_chain % len(SYNONYMS[w])]
                                new_txt = re.sub(rf'^{re.escape(w)}\b', syn, txt, count=1)
                                # Mark for replacement later
                                sentences[orig_i] = new_txt
                                fixes += 1
                chain = []
        # Trailing chain
        if len(chain) >= 3:
            for idx_in_chain, (orig_i, w, txt) in enumerate(chain):
                if idx_in_chain >= 2 and idx_in_chain % 2 == 0:
                    if w in SYNONYMS and SYNONYMS[w]:
                        syn = SYNONYMS[w][idx_in_chain % len(SYNONYMS[w])]
                        new_txt = re.sub(rf'^{re.escape(w)}\b', syn, txt, count=1)
                        sentences[orig_i] = new_txt
                        fixes += 1
        new_paragraphs.append(' '.join(sentences))

    if fixes > 0 and not dry_run:
        shutil.copy2(p, p.with_suffix('.md.bak.anaphora_vary'))
        p.write_text('\n\n'.join(new_paragraphs), encoding='utf-8')
    return fixes

def main():
    apply = '--apply' in sys.argv
    print(f"ANAPHORA VARY — EP02-50 | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    total = 0
    for n in range(2, 51):
        fixes = process_ep(n, dry_run=not apply)
        if fixes > 0:
            print(f"EP{n:02d}: {fixes}")
            total += fixes
    print(f"\nTotal: {total} subject vary")

if __name__ == '__main__':
    main()
