"""SVHMP — Style stats全书级固化 audit (kentjuno pattern import).

Detects cross-EP pattern drift via deterministic statistics:
- patterns章均 (sentence-type per-chapter average)
- top_phrases (recent high-frequency 3-grams)
- repeated_sentences (cross-chapter verbatim repeats)
- ending.short_ratio (chapter-end short sentence percentage)
- opening_time_rate (opening time-word usage rate)
- title_formats (mixed title format detection)

Flag patterns whose章均 count abnormally high — disease across full series.
"""
import re
import sys
import json
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

def strip_meta(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    return text

def get_sentences(text):
    body = strip_meta(text)
    body = re.sub(r'#[^\n]*\n', '', body)
    body = re.sub(r'\[pause:[^\]]+\]', '', body)
    sentences = re.split(r'(?<=[.!?])\s+', body)
    return [s.strip() for s in sentences if s.strip() and len(s.split()) > 1]

def main():
    print("=" * 70)
    print("STYLE STATS — Cross-EP pattern drift detection")
    print("=" * 70)

    all_3grams = Counter()
    all_sentences = Counter()
    per_ep_short_ratio = {}
    per_ep_opening_time = {}
    title_formats = Counter()

    TIME_OPENERS = {'Đêm', 'Hôm', 'Ngày', 'Năm', 'Sáng', 'Chiều', 'Tối',
                    'Vào', 'Tháng', 'Mùa', 'Buổi'}

    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')

        # Title format
        m = re.match(r'^#\s*(.+)', text)
        if m:
            title = m.group(1).strip()
            # Detect format: "TẬP X — TITLE" or "TẬP X. TITLE" or "TẬP X TITLE"
            if ' — ' in title:
                title_formats['EM-DASH'] += 1
            elif '. ' in title.split(' ', 2)[1] if len(title.split(' ', 2)) > 1 else '':
                title_formats['PERIOD'] += 1
            else:
                title_formats['OTHER'] += 1

        sentences = get_sentences(text)
        if not sentences:
            continue

        # 3-grams across sentences
        for s in sentences:
            words = s.split()
            for i in range(len(words) - 2):
                trigram = ' '.join(words[i:i+3])
                if all(c not in trigram for c in '"—'):  # skip quotes/dashes
                    all_3grams[trigram] += 1

        # Full sentences for repeats
        for s in sentences:
            if 5 <= len(s.split()) <= 30:
                all_sentences[s] += 1

        # Short-end ratio (last sentence per "section")
        short_end = sum(1 for s in sentences if len(s.split()) <= 5)
        per_ep_short_ratio[n] = short_end / len(sentences)

        # Opening time-word rate
        first_words = [s.split()[0] for s in sentences[:10] if s]
        opening_time = sum(1 for w in first_words if w in TIME_OPENERS)
        per_ep_opening_time[n] = opening_time

    # Findings
    print("\n=== TITLE FORMATS ===")
    for fmt, c in title_formats.items():
        print(f"  {fmt}: {c}")
    if len(title_formats) > 1:
        print("  ⚠️ MIXED title formats — should standardize")

    print(f"\n=== TOP 3-GRAMS (high frequency = AI-tell) ===")
    for trigram, count in all_3grams.most_common(15):
        if count >= 10:
            print(f"  '{trigram}': {count}x (avg {count/50:.1f}/EP)")

    print(f"\n=== REPEATED FULL SENTENCES cross-EP (verbatim) ===")
    repeated = [(s, c) for s, c in all_sentences.most_common(30) if c >= 3]
    print(f"Total sentences repeating ≥3 EPs: {len(repeated)}")
    for s, c in repeated[:10]:
        print(f"  {c}x: {s[:80]}")

    print(f"\n=== SHORT-END RATIO per EP (target < 0.40) ===")
    high_short = [(n, r) for n, r in per_ep_short_ratio.items() if r > 0.40]
    if high_short:
        print(f"  {len(high_short)} EPs với short_ratio > 0.40:")
        for n, r in sorted(high_short, key=lambda x: -x[1])[:10]:
            print(f"    EP{n:02d}: {r:.2f}")
    else:
        print("  ✓ All EPs OK")

    print(f"\n=== OPENING TIME-WORD rate (target ≤ 3/first10) ===")
    high_time = [(n, c) for n, c in per_ep_opening_time.items() if c > 3]
    if high_time:
        for n, c in sorted(high_time, key=lambda x: -x[1])[:5]:
            print(f"  EP{n:02d}: {c} time-openers trong 10 câu đầu")
    else:
        print("  ✓ All EPs OK")

    out = SVHMP / 'runtime' / 'audit_style_stats.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        'title_formats': dict(title_formats),
        'top_3grams': dict(all_3grams.most_common(30)),
        'repeated_sentences': [(s, c) for s, c in all_sentences.most_common(50) if c >= 3],
        'short_ratio': per_ep_short_ratio,
        'opening_time': per_ep_opening_time,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
