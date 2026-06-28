"""SVHMP R61 — Audit short-syllable start-of-sentence (TTS hụt hơi).

Mr.Long 28/6: "đoạn mở đầu Đêm hôm ấy, chữ Đêm nghe như bị cụt / hụt hơi"

Rule: CẤM mở đầu câu/đoạn bằng từ 1 âm tiết đơn rồi space + content.
TTS prosody accelerate at sentence-start → short syllable bị nuốt.

Banned starts: Đêm / Hôm / Ngày / Năm / Sáng / Chiều / Tối / Mưa / Gió

Usage: python tools/audit_short_start.py [--ep N]
"""
import re
import sys
import argparse
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

BANNED_STARTS = {
    'Đêm', 'Hôm', 'Ngày', 'Năm', 'Sáng', 'Chiều', 'Tối',
    'Mưa', 'Gió', 'Sương', 'Lúc', 'Khi', 'Trên', 'Dưới',
    'Trong', 'Ngoài', 'Cô', 'Anh', 'Chị', 'Ông', 'Bà',
}

def strip_meta(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    return text

def audit_episode(text):
    issues = []
    body = strip_meta(text)
    lines = body.splitlines()

    # Pattern at start of line OR after . ! ? \n
    for i, line in enumerate(lines, 1):
        if not line.strip() or line.startswith('#') or line.startswith('[pause') or line.startswith('---'):
            continue
        if line.startswith('|') or line.startswith('-'):
            continue
        # Sentences in this line: split by . ! ?
        sentences = re.split(r'(?<=[.!?])\s+', line)
        for s in sentences:
            s = s.strip()
            if not s:
                continue
            # Get first word
            m = re.match(r'^["\'—\s]*(\w+)\b', s)
            if m:
                first = m.group(1)
                if first in BANNED_STARTS:
                    # Get next word — if 2nd word is short (1 syl), it's risky
                    # Pattern critical: "Đêm đó" / "Đêm nay" — Mr.Long flag
                    rest = s[m.end():].strip()
                    next_word = rest.split()[0] if rest else ''
                    word_count = len(s.split())
                    # Only flag short sentences (<5 words) starting with banned + short 2nd
                    if next_word and len(next_word) <= 4 and word_count <= 5:
                        issues.append({
                            'line': i,
                            'word': first,
                            'next_word': next_word,
                            'context': s[:60],
                            'word_count': word_count,
                            'severity': 'HIGH',
                        })
    return issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    print("=" * 70)
    print("R61 AUDIT — Short-syllable at start (TTS hụt hơi)")
    print("=" * 70)

    total = 0
    eps_with = []
    all_v = []
    eps = [(n, SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md')
           for n in (range(1, 91) if not args.ep else [args.ep])]

    for n, p in eps:
        if not p.exists():
            continue
        issues = audit_episode(p.read_text(encoding='utf-8'))
        if issues:
            eps_with.append((n, len(issues)))
            total += len(issues)
            for v in issues:
                v['ep'] = n
                all_v.append(v)
            if not args.summary:
                print(f"\nEP{n:02d}: {len(issues)}")
                for v in issues[:5]:
                    print(f"  L{v['line']}: '{v['word']} {v['next_word']}...' | {v['context']}")

    print(f"\nSUMMARY: {total} HIGH in {len(eps_with)} EPs")
    for n, c in sorted(eps_with, key=lambda x: -x[1])[:10]:
        print(f"  EP{n:02d}: {c}")

    out = SVHMP / 'runtime' / 'audit_short_start_report.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        'total': total, 'eps': eps_with, 'violations': all_v,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report: {out}")
    return 0 if total == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
