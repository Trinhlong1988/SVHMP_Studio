"""SVHMP — Detect formulaic template repetition across EPs.

Mr.Long 28/6: reader judgement phát hiện HOOK + REVEAL intro lặp formula across 40 EPs.

Checks:
1. HOOK opener identical sentences cross-EP
2. REVEAL intro template cross-EP
3. Common phrase repetition

Usage: python tools/detect_template_repetition.py
"""
import re
import sys
import json
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

def strip_metadata(text):
    return re.sub(r'```.*?```', '', text, flags=re.DOTALL)

def extract_section(text, section):
    """Extract a section by name."""
    pattern = rf'#+\s+{section}.*?(?=#+\s+[A-Z]|$)'
    m = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    return m.group() if m else ''

def first_n_sentences(text, n=3):
    """Get first N narrative sentences (skip pause markers)."""
    # Remove pause markers + section headers
    text = re.sub(r'\[pause:[^\]]+\]', '', text)
    text = re.sub(r'#+\s+\w+\s*\[?[^\]]*\]?\s*', '', text)
    text = text.strip()
    # Split sentences
    sentences = re.split(r'[.!?]\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return sentences[:n]

def main():
    print("=" * 70)
    print("TEMPLATE REPETITION DETECTOR EP01-50")
    print("=" * 70)

    eps = {}
    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if p.exists():
            eps[n] = strip_metadata(p.read_text(encoding='utf-8'))

    # 1. HOOK opener first sentence frequency
    print("\n=== HOOK opener first sentence frequency ===")
    hook_openers = Counter()
    hook_first = {}
    for n, text in eps.items():
        hook = extract_section(text, 'HOOK')
        sents = first_n_sentences(hook, n=2)
        if sents:
            opener = sents[0]
            hook_openers[opener] += 1
            hook_first[n] = opener

    for opener, count in hook_openers.most_common(5):
        print(f"  [{count}x] {opener[:80]}")

    # 2. HOOK template "Đêm tháng tư. Mưa nhẹ" frequency
    template_dem_mua = sum(1 for t in eps.values() if 'Đêm tháng tư. Mưa nhẹ' in t)
    template_xe_chay = sum(1 for t in eps.values() if 'Chuyến xe đêm chạy qua đoạn đường' in t)
    template_den_pha = sum(1 for t in eps.values() if 'Đèn pha quét lên hàng' in t)
    print(f"\n=== Specific template phrases ===")
    print(f"  'Đêm tháng tư. Mưa nhẹ' in: {template_dem_mua}/{len(eps)} EPs")
    print(f"  'Chuyến xe đêm chạy qua đoạn đường' in: {template_xe_chay}/{len(eps)} EPs")
    print(f"  'Đèn pha quét lên hàng' in: {template_den_pha}/{len(eps)} EPs")

    # 3. REVEAL intro "Tôi/Em là [name]" frequency
    print(f"\n=== REVEAL intro pattern ===")
    intro_pattern = re.compile(r'"(Tôi|Em) (?:là|tên) (\w+[^.]{0,30})\. (\w+) tuổi')
    intro_matches = []
    for n, text in eps.items():
        reveal = extract_section(text, 'REVEAL')
        m = intro_pattern.search(reveal)
        if m:
            intro_matches.append((n, m.group()))
    print(f"  Cookie-cutter intro 'Tôi/Em là X. Y tuổi.' in: {len(intro_matches)}/{len(eps)} EPs")
    for n, sample in intro_matches[:5]:
        print(f"    EP{n:02d}: {sample[:80]}")

    # 4. CLIFFHANGER ending pattern
    print(f"\n=== CLIFFHANGER ending pattern ===")
    ending_template = sum(1 for t in eps.values() if 'Bác tài liếc gương. "Đêm' in t)
    print(f"  Bác tài foreshadow 'Đêm thứ X' in: {ending_template}/{len(eps)} EPs (R42 design intent)")

    # Verdict
    print(f"\n{'='*70}\nVERDICT\n{'='*70}")
    formulaic_score = (template_dem_mua + template_xe_chay + template_den_pha + len(intro_matches)) / (4 * len(eps))
    print(f"  Formulaic score: {formulaic_score*100:.1f}% (lower = better)")
    if formulaic_score > 0.7:
        print(f"  🔴 HIGH FORMULAIC — needs varied templates per R49")
    elif formulaic_score > 0.4:
        print(f"  🟡 MEDIUM FORMULAIC")
    else:
        print(f"  ✓ ACCEPTABLE")

    # Save
    out = SVHMP / 'runtime' / 'detect_template_repetition_report.json'
    out.write_text(json.dumps({
        'hook_openers_top5': hook_openers.most_common(5),
        'template_dem_mua': template_dem_mua,
        'template_xe_chay': template_xe_chay,
        'template_den_pha': template_den_pha,
        'cookie_cutter_intros': len(intro_matches),
        'cookie_cutter_eps': [n for n, _ in intro_matches],
        'cliffhanger_template': ending_template,
        'formulaic_score': formulaic_score,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
