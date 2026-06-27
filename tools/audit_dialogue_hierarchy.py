"""SVHMP — Audit dialogue hierarchy R48 (Mr.Long 28/6).

Deep research script for Vietnamese pronoun hierarchy in passenger dialogue.

Vietnamese pronoun rules:
- Speaker tự xưng: "em" (younger) / "tôi" (older/same) / "anh/chị" (relatable to listener)
- Refer to listener: theo age hierarchy
- Refer to người đã mất: theo age relationship
- 2+ "em" in same sentence with multiple referents = AMBIGUOUS

Detection logic:
1. Parse quoted dialogue blocks (passenger speech)
2. Identify speaker self-reference pronoun (tôi/em consistency)
3. Count "em" occurrences referencing DIFFERENT people in same quote
4. Detect inconsistency:
   - Speaker tự xưng "tôi" rồi đột nhiên "em" → pronoun shift bug
   - "em ... em ... em" referring to 2+ people without name disambiguation
   - Speaker gọi người already-named bằng "em" cùng lúc tự xưng "em"

Usage: python tools/audit_dialogue_hierarchy.py [--ep N] [--detail]
"""
import re
import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# Verbs that follow "em" to indicate distinct referent
VERBS_SELF = ['cố', 'nhớ', 'thấy', 'biết', 'sẽ', 'đã', 'không', 'có', 'sống', 'làm', 'đi', 'về',
              'mua', 'bán', 'gọi', 'nhắn', 'đem', 'cất', 'giữ', 'mở', 'đóng', 'đến', 'rời',
              'ngồi', 'đứng', 'quỳ', 'cúi', 'nhìn', 'hỏi', 'đáp', 'kể', 'nghe',
              'yêu', 'thương', 'ghét', 'sợ', 'mong', 'hứa', 'tin', 'nghĩ', 'cảm',
              'đeo', 'tháo', 'cầm', 'đặt', 'gửi', 'lấy', 'tặng', 'chạy', 'bay',
              'ăn', 'uống', 'ngủ', 'tỉnh', 'tắm', 'rửa']

# Verbs/words that follow "em" to indicate REFER to OTHER person
VERBS_OTHER_HINT = ['ơi', 'à', 'nhé', 'với', 'cho', 'theo']

def extract_quotes(text):
    """Extract list of (quote_text, paragraph_context)."""
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    quotes = []
    for m in re.finditer(r'"([^"]+)"', text):
        # Find surrounding paragraph (300 chars context)
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 100)
        context = text[start:end]
        quotes.append((m.group(1), context))
    return quotes

def detect_pronoun_issues_in_quote(quote, passenger_name=None):
    """For one quote, detect potential pronoun issues."""
    issues = []

    # Count em vs tôi self-reference
    em_total = len(re.findall(r'\bem\b', quote, re.IGNORECASE))
    toi_total = len(re.findall(r'\btôi\b', quote, re.IGNORECASE))
    anh_total = len(re.findall(r'\banh\b', quote))
    chi_total = len(re.findall(r'\bchị\b', quote))

    # Issue 1: pronoun shift — tự xưng "tôi" rồi đột nhiên "em" (or vice versa)
    if toi_total >= 2 and em_total >= 2:
        # Likely mixed self-reference + referent
        # Check if "em" appears as self vs as referent
        issues.append({
            'type': 'pronoun_shift_self',
            'detail': f'tôi={toi_total} + em={em_total} mixed self-ref',
            'severity': 'HIGH',
        })

    # Issue 2: "em" overload — 5+ em in 1 quote with potential multiple referents
    if em_total >= 5:
        # Check if there are at least 2 named persons in quote
        named_persons = re.findall(r'[A-ZĐ][a-zàáâãèéêíìóòôõùúýỳỵỷỹăằắẳẵặâầấẩẫậđèéẹẻẽêềếểễệìíỉĩịòóọỏõôồốổỗộơờớởỡợùúụủũưừứửữựỳýỷỹỵ]+\b', quote)
        named_filter = [n for n in named_persons if n not in ['Em', 'Tôi', 'Anh', 'Chị', 'Bác', 'Bố', 'Mẹ', 'Bà', 'Ông', 'Vâng', 'OK', 'Cảm']]
        if len(set(named_filter)) >= 1:
            # Has named person + multiple em
            sample = quote[:120]
            issues.append({
                'type': 'em_overload_multiple_referents',
                'detail': f'{em_total} em + named: {set(named_filter)} — likely ambiguous',
                'severity': 'HIGH' if em_total >= 7 else 'MEDIUM',
                'sample': sample,
            })

    # Issue 3: "em chị" or "em anh" — ambiguous self vs other
    if re.search(r'\bem (chị|anh)\b', quote):
        issues.append({
            'type': 'em_followed_by_kinship',
            'detail': 'em + chị/anh — ambiguous (self ref vs addressing)',
            'severity': 'MEDIUM',
        })

    # Issue 4: "em <verb>" repeated 4+ times consecutively — may be intentional Ngọc Ngạn monologue
    # Skip flag — accept R46

    return issues

def get_passenger_info(text):
    """Extract passenger name + age from EP."""
    body = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    # Reveal intro: "Em/Tôi là [Name]. [Age] tuổi."
    m = re.search(r'"(?:Em|Tôi) (?:là|tên) (\w+(?:\s\w+)*)\. ([^.]{2,30}) tuổi', body)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None, None

def audit_ep(ep_num, text, detail=False):
    """Audit one EP — return list of dialogue issues."""
    quotes = extract_quotes(text)
    passenger_name, age = get_passenger_info(text)

    all_issues = []
    for q_idx, (q, ctx) in enumerate(quotes):
        # Skip very short quotes (< 20 chars)
        if len(q) < 20: continue
        issues = detect_pronoun_issues_in_quote(q, passenger_name)
        for iss in issues:
            iss['ep'] = ep_num
            iss['passenger'] = passenger_name
            iss['quote_idx'] = q_idx
            all_issues.append(iss)

    return all_issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--detail', action='store_true')
    args = parser.parse_args()

    print("=" * 70)
    print("DIALOGUE HIERARCHY R48 AUDIT")
    print("=" * 70)

    eps = {}
    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if p.exists():
            eps[n] = p.read_text(encoding='utf-8')

    if args.ep:
        eps = {args.ep: eps[args.ep]} if args.ep in eps else {}

    all_issues = []
    per_ep_severity = defaultdict(lambda: defaultdict(int))

    for n, text in eps.items():
        issues = audit_ep(n, text, args.detail)
        all_issues.extend(issues)
        for iss in issues:
            per_ep_severity[n][iss['severity']] += 1

    # Per-EP summary
    print(f"\n=== PER-EP SUMMARY ===")
    print(f"  EP   | HIGH | MEDIUM | passenger")
    for n in sorted(eps.keys()):
        sev = per_ep_severity[n]
        if sev['HIGH'] > 0 or sev['MEDIUM'] > 3:
            passenger_name, _ = get_passenger_info(eps[n])
            symbol = '🔴' if sev['HIGH'] > 3 else '🟡' if sev['HIGH'] > 0 else '○'
            print(f"  EP{n:02d} | {sev['HIGH']:4} | {sev['MEDIUM']:6} | {symbol} {passenger_name}")

    # Global summary
    high_total = sum(1 for i in all_issues if i['severity'] == 'HIGH')
    med_total = sum(1 for i in all_issues if i['severity'] == 'MEDIUM')
    print(f"\n=== GLOBAL ===")
    print(f"  Total HIGH dialogue issues: {high_total}")
    print(f"  Total MEDIUM: {med_total}")
    print(f"  EPs affected: {sum(1 for n in per_ep_severity if per_ep_severity[n]['HIGH'] > 0 or per_ep_severity[n]['MEDIUM'] > 0)}")

    # Top 10 worst quotes
    if args.detail or args.ep:
        print(f"\n=== TOP 10 WORST DIALOGUE QUOTES ===")
        sorted_issues = sorted(
            [i for i in all_issues if i.get('sample')],
            key=lambda x: -int(re.search(r'(\d+) em', x.get('detail', '0 em')).group(1)) if re.search(r'(\d+) em', x.get('detail', '0 em')) else 0
        )
        for iss in sorted_issues[:10]:
            print(f"  EP{iss['ep']:02d} [{iss['severity']}] {iss['type']}")
            print(f"      {iss['detail']}")
            print(f"      Sample: '{iss.get('sample', '')[:120]}...'")

    # Save report
    out = SVHMP / 'runtime' / 'audit_dialogue_hierarchy_report.json'
    out.write_text(json.dumps({
        'summary': {'high': high_total, 'medium': med_total},
        'per_ep_severity': {str(n): dict(sev) for n, sev in per_ep_severity.items()},
        'sample_issues': all_issues[:50],
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")
    return 0 if high_total == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
