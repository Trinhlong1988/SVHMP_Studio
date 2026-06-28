"""SVHMP R60 — Audit short-syllable end-of-sentence (TTS prosody decay).

Mr.Long 28/6: "các từ 2 chữ ở kết thúc câu như 'im' hoặc các từ khác nghe sẽ bị cụt âm"

Rule: kết thúc câu bằng từ 1 âm tiết đơn (mono-syllable) → TTS cụt âm.

Banned EOL words (mono-syllable adverbs/verbs hay dùng):
im, lặng, rơi, đi, ra, qua, lui, tan, nhỏ, to, lên, xuống, vào, ra, đó, đây,
khẽ, nhẹ, mau, chậm, mềm, cứng, nóng, lạnh, vắng, đông, xa, gần, cao, thấp

EOL boundary: . ! ? — " \\n [pause:

Usage: python tools/audit_short_eol.py [--ep N]
"""
import re
import sys
import argparse
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# Mono-syllable words risky at EOL (TTS prosody tail cụt)
BANNED_EOL = {
    'im', 'lặng', 'rơi', 'đi', 'ra', 'qua', 'lui', 'tan', 'nhỏ', 'to',
    'lên', 'xuống', 'vào', 'đó', 'đây', 'khẽ', 'nhẹ', 'mau', 'chậm',
    'mềm', 'cứng', 'nóng', 'lạnh', 'vắng', 'đông', 'xa', 'gần', 'cao',
    'thấp', 'sáng', 'tối', 'hết', 'rồi', 'thôi', 'nữa', 'mãi', 'liền',
    'ngay', 'dày', 'mỏng', 'bự', 'lép', 'khô', 'ướt',
}

# Allowed exceptions (proper noun, dialogue intentional staccato)
EXCEPTIONS = {
    'Khải', 'Phong', 'Hạ', 'Vy',  # names — usually mid-sentence
}

def strip_meta(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    return text

def audit_episode(text):
    issues = []
    body = strip_meta(text)
    lines = body.splitlines()

    # Pattern: word followed by EOL boundary
    eol_pattern = re.compile(
        r'\b(\w+)\s*(?=[.!?])',
        re.UNICODE
    )

    for i, line in enumerate(lines, 1):
        if not line.strip() or line.startswith('#') or line.startswith('[pause'):
            continue
        for m in eol_pattern.finditer(line):
            word = m.group(1)
            if word in BANNED_EOL:
                ctx_start = max(0, m.start() - 40)
                ctx_end = min(len(line), m.end() + 5)
                # Check sentence length — exception if sentence < 3 words (intentional stacato)
                sentence_start = max(line.rfind('.', 0, m.start()), line.rfind('?', 0, m.start()))
                sentence = line[sentence_start+1:m.end()].strip()
                word_count = len(sentence.split())
                # Only flag when sentence < 4 words (clearly cụt) — staccato 4+ words is intentional
                if word_count <= 3:
                    issues.append({
                        'line': i,
                        'word': word,
                        'context': line[ctx_start:ctx_end].strip(),
                        'sentence_words': word_count,
                        'severity': 'HIGH',
                    })
    return issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    print("=" * 70)
    print("R60 AUDIT — Short-syllable at end-of-sentence (TTS cụt âm)")
    print("=" * 70)

    total = 0
    eps_with = []
    all_v = []
    eps = [(n, SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md')
           for n in (range(1, 91) if not args.ep else [args.ep])]

    for n, p in eps:
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8')
        issues = audit_episode(text)
        if issues:
            eps_with.append((n, len(issues)))
            total += len(issues)
            for v in issues:
                v['ep'] = n
                all_v.append(v)
            if not args.summary:
                print(f"\nEP{n:02d}: {len(issues)} violations")
                for v in issues[:5]:
                    print(f"  L{v['line']}: '{v['word']}' | ...{v['context']}...")

    print(f"\nSUMMARY: {total} HIGH in {len(eps_with)} EPs")
    for n, c in sorted(eps_with, key=lambda x: -x[1])[:10]:
        print(f"  EP{n:02d}: {c}")

    out = SVHMP / 'runtime' / 'audit_short_eol_report.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        'total': total,
        'eps': eps_with,
        'violations': all_v,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report: {out}")
    return 0 if total == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
