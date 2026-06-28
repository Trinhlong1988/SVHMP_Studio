"""SVHMP — Combined audit cho R68-R73 (TTS gap fill round 18.8).

R68: triphthong proper nouns
R69: number reading (số Ả Rập trong narrative)
R70: em-dash prosody (em-dash in narrative position, not dialogue)
R71: place name canonical (lesser cities)
R72: dialogue quote rendering (count quote dialogue segments)
R73: LUFS gating (run on render audit_audio_mix_qa.py separately)

Usage: python tools/audit_r68_to_r73.py [--ep N]
"""
import re
import sys
import argparse
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# R68: triphthong proper nouns risky
TRIPHTHONG_PROPER_NOUNS = {
    'Huế', 'Thuận', 'Tuyên', 'Tuyến', 'Khải', 'Quỳnh', 'Quân', 'Tuấn',
    'Khang', 'Nhuần', 'Khoái', 'Đoàn', 'Khoảng',
}

# R69: số Ả Rập trong context narrative (không phải năm 4 chữ số)
NUMBER_PATTERN = re.compile(r'\b([1-9]\d?)\s*(giờ|tuổi|năm|tháng|ngày|phút|giây|lần|đêm)\b')

# R70: em-dash trong narrative (KHÔNG phải dialogue dash đầu câu)
EM_DASH_NARRATIVE = re.compile(r'[^\n]+\s—\s[^\n"]+')  # em-dash giữa câu narrative

# R71: place names ngoài whitelist HN/SG/HP
COMMON_OK_PLACES = {'Hà Nội', 'Sài Gòn', 'Hải Phòng', 'Hà Đông', 'Bạch Mai', 'Long Biên'}
RISKY_PLACES = {
    'Buôn Ma Thuột', 'Pleiku', 'Quy Nhơn', 'Đắk Lắk', 'Phước Long',
    'Vũng Tàu', 'Cần Thơ', 'Nha Trang', 'Đà Nẵng', 'Huế',
    'Phú Thọ', 'Vĩnh Lộc', 'Lào Cai', 'Sa Pa',
}

# R72: dialogue quotes
DIALOGUE_QUOTE_PATTERN = re.compile(r'"[^"]{5,300}"')

def strip_meta(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    return text

def audit_episode(text):
    body = strip_meta(text)
    issues = {'R68': [], 'R69': [], 'R70': [], 'R71': [], 'R72': []}

    # R68 triphthong
    for word in TRIPHTHONG_PROPER_NOUNS:
        for m in re.finditer(rf'\b{re.escape(word)}\b', body):
            ctx = body[max(0, m.start() - 30):m.end() + 20]
            issues['R68'].append({'word': word, 'context': ctx.strip()[:80]})

    # R69 số Ả Rập
    for m in NUMBER_PATTERN.finditer(body):
        ctx = body[max(0, m.start() - 30):m.end() + 20]
        issues['R69'].append({'match': m.group(), 'context': ctx.strip()[:80]})

    # R70 em-dash narrative
    for m in EM_DASH_NARRATIVE.finditer(body):
        # Skip if line starts with em-dash (dialogue speaker)
        line_start = body.rfind('\n', 0, m.start()) + 1
        line_prefix = body[line_start:m.start()].strip()
        if line_prefix.startswith('—'):
            continue  # dialogue dash
        ctx = m.group()[:80]
        issues['R70'].append({'context': ctx.strip()})

    # R71 risky place names
    for place in RISKY_PLACES:
        if place in body and place not in COMMON_OK_PLACES:
            cnt = body.count(place)
            issues['R71'].append({'place': place, 'count': cnt})

    # R72 dialogue quotes count (informational)
    quotes = DIALOGUE_QUOTE_PATTERN.findall(body)
    if len(quotes) > 0:
        issues['R72'].append({'quote_segments': len(quotes), 'note': 'separate render needed per R72'})

    return issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    print("=" * 70)
    print("R68-R72 COMBINED AUDIT")
    print("=" * 70)

    totals = {'R68': 0, 'R69': 0, 'R70': 0, 'R71': 0, 'R72': 0}
    eps_data = {}

    eps = [(n, SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md')
           for n in (range(1, 91) if not args.ep else [args.ep])]

    for n, p in eps:
        if not p.exists(): continue
        text = p.read_text(encoding='utf-8')
        issues = audit_episode(text)
        ep_total = sum(len(v) for v in issues.values())
        if ep_total > 0:
            eps_data[n] = issues
            for rule, lst in issues.items():
                totals[rule] += len(lst)

    print(f"\nRule totals (all 50 EPs):")
    for rule, count in totals.items():
        print(f"  {rule}: {count}")

    if not args.summary:
        for ep in sorted(eps_data.keys())[:10]:
            print(f"\nEP{ep:02d}:")
            for rule, lst in eps_data[ep].items():
                if lst:
                    print(f"  {rule} ({len(lst)}):")
                    for item in lst[:3]:
                        print(f"    {item}")

    out = SVHMP / 'runtime' / 'audit_r68_r73_report.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        'totals': totals,
        'eps_data': {str(k): v for k, v in eps_data.items()},
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
