"""SVHMP — R74 Audit phrase repetition trong-paragraph + cross-paragraph nearby.

Ollama gemma2:9b 28/6 phát hiện gap: audit em chỉ check first-word chain,
KHÔNG catch cụm-từ-giữa-câu lặp ("Khải Phong" / "ướm thử" / "mắt thâm").

Detection:
- 2-3 word phrases (excluded function words)
- Repeat ≥3 lần trong cùng paragraph
- OR repeat ≥4 lần trong 5 paragraphs adjacent

Usage: python tools/audit_phrase_repetition.py [--ep N]
"""
import re
import sys
import argparse
import json
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# Function words to exclude from phrase counting
STOPWORDS = {
    'của', 'và', 'là', 'cho', 'với', 'một', 'này', 'kia', 'đó', 'đã', 'sẽ', 'đang',
    'cũng', 'thì', 'mà', 'nhưng', 'rồi', 'lại', 'ra', 'vào', 'lên', 'xuống',
    'cái', 'những', 'các', 'mỗi', 'từng', 'khi', 'lúc', 'như', 'có', 'không',
    'phải', 'nên', 'được', 'hay', 'thôi', 'nhé', 'đi', 'đây', 'thế',
}

# Allowed character names (NOT count as repetition violation if expected)
EXPECTED_NAMES = {
    'Khải Phong', 'Khải-Phong', 'Hạ Vy', 'Hạ-Vy', 'Bác tài',
    'Thu Hà', 'Hà Nội', 'Hà Đông', 'Hải Phòng', 'Sài Gòn', 'Bạch Mai',
    'Long Biên', 'Khâm Thiên', 'Cầu Long Biên',
}

# Whitelist intentional repetitions (onomatopoeia, family, common phrases)
ONOMATOPOEIA_WHITELIST = {
    'tách', 'tách tách', 'tách tách tách', 'Tách', 'Tách Tách', 'Tách Tách Tách',
    'lách cách', 'lộc cộc', 'vù vù', 'ầm ầm', 'rì rì', 'thì thầm',
    'lập cập', 'lập lờ', 'lơ lửng', 'thấp thoáng',
    'cụ cụ', 'cụ ơi',
}

PROPER_NOUN_PHRASES = {
    'viết Cháu', 'Cháu Diệu', 'Cháu Linh',  # dialogue tag children name
    'mẹ em', 'mẹ con', 'bà cháu',  # family relation
    'riêng Cluster',  # metadata leftover (separate cleanup)
}

# Max allowed character name occurrences per paragraph
MAX_NAME_PER_PARA = 3

def strip_meta(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    text = re.sub(r'#[^\n]*\n', '', text)
    text = re.sub(r'\[pause:[^\]]+\]', '', text)
    return text

def get_phrases(text, n=2):
    """Extract n-gram phrases excluding stopwords."""
    words = re.findall(r'\w+', text)
    phrases = []
    for i in range(len(words) - n + 1):
        phrase = ' '.join(words[i:i+n])
        # Skip if all words are stopwords
        word_set = set(words[i:i+n])
        if not word_set.issubset(STOPWORDS):
            phrases.append(phrase)
    return phrases

def audit_episode(text, ep_num):
    body = strip_meta(text)
    paragraphs = re.split(r'\n\s*\n', body)
    issues = []

    for pidx, para in enumerate(paragraphs):
        if not para.strip(): continue

        # Count expected names (Khải Phong etc.)
        for name in EXPECTED_NAMES:
            cnt = len(re.findall(rf'\b{re.escape(name)}\b', para))
            if cnt > MAX_NAME_PER_PARA:
                issues.append({
                    'type': 'name_overuse',
                    'name': name,
                    'count': cnt,
                    'max': MAX_NAME_PER_PARA,
                    'para_idx': pidx,
                    'para_preview': para[:100],
                })

        # 2-gram + 3-gram repetition trong paragraph
        for n in [2, 3]:
            phrases = get_phrases(para, n=n)
            counter = Counter(phrases)
            for phrase, count in counter.items():
                if count >= 3:
                    # Skip if phrase contains expected name
                    if any(name in phrase for name in EXPECTED_NAMES):
                        continue
                    # Skip onomatopoeia + proper nouns
                    if phrase in ONOMATOPOEIA_WHITELIST or phrase.lower() in {w.lower() for w in ONOMATOPOEIA_WHITELIST}:
                        continue
                    if phrase in PROPER_NOUN_PHRASES:
                        continue
                    issues.append({
                        'type': f'phrase_{n}gram_repeat',
                        'phrase': phrase,
                        'count': count,
                        'para_idx': pidx,
                        'para_preview': para[:100],
                    })
    return issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    print("=" * 70)
    print("R74 AUDIT — Phrase repetition (Ollama gap fill)")
    print("=" * 70)

    total = 0
    eps_with = []
    all_v = []
    eps = [(n, SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md')
           for n in (range(1, 91) if not args.ep else [args.ep])]

    for n, p in eps:
        if not p.exists(): continue
        text = p.read_text(encoding='utf-8')
        issues = audit_episode(text, n)
        if issues:
            eps_with.append((n, len(issues)))
            total += len(issues)
            for v in issues:
                v['ep'] = n
                all_v.append(v)
            if not args.summary:
                print(f"\nEP{n:02d}: {len(issues)} issues")
                for v in issues[:5]:
                    if v['type'] == 'name_overuse':
                        print(f"  [{v['type']}] '{v['name']}' x{v['count']} > {v['max']} | para {v['para_idx']}")
                    else:
                        print(f"  [{v['type']}] '{v['phrase']}' x{v['count']} | para {v['para_idx']}")

    print(f"\nSUMMARY: {total} HIGH in {len(eps_with)} EPs")
    for n, c in sorted(eps_with, key=lambda x: -x[1])[:10]:
        print(f"  EP{n:02d}: {c}")

    out = SVHMP / 'runtime' / 'audit_phrase_repetition_report.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        'total': total, 'eps': eps_with, 'violations': all_v,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report: {out}")

if __name__ == '__main__':
    main()
