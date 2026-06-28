"""SVHMP — Audit 9 rules CHƯA có script direct (N3 - Mr.Long 28/6).

Rules covered:
- R43 tier2_filler_cap_per_ep — filler words ≤30/EP
- R45 context_block — forbidden context patterns
- R49 template_variation_hardlock — recurring templates >30/50 EPs
- R57 reveal_vignette_structure — REVEAL có 3-5 vignettes
- R63 logic_math_physics — number consistency, math errors
- R64 dao_duc_vn — culture violations (xưng hô / tang chế)
- R65 total_consistency_no_invention — bịa địa danh / số liệu
- R66 short_sentence_chain — ≥3 câu 4-6 từ liền tiếp
- R67 verb_semantic — nhớ + recent action wrong

Usage: python tools/audit_r43_to_r67_missing.py [--summary]
"""
import re
import sys
import argparse
import json
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# R43 filler words pool
FILLER_WORDS = ['thì', 'mà', 'rồi', 'nhé', 'thôi', 'à', 'ạ', 'cơ', 'vậy', 'đấy']
FILLER_MAX_PER_EP = 30

# R45 context block
FORBIDDEN_CONTEXT = [
    r'\b(tự sát|sát nhân|giết người)\b.*(?:cách|kỹ thuật|hướng dẫn)',
    r'\bmáu\s+(?:phun|trào|nhỏ giọt|chảy thành dòng)\b',  # graphic gore
    r'\bxác chết\s+(?:đang phân hủy|thối rữa|biến dạng)\b',
]

# R49 templates to check overuse
RECURRING_TEMPLATES = [
    r'Chuông xe ngân\. Một tiếng\. Tan\.',
    r'bước lên xe\. Đi qua hàng ghế',
    r'Khải-?Phong quan sát từ ghế ba',
    r'vuốt vai.*Mỉm cười',
]
TEMPLATE_MAX = 15  # max occurrences per 50 EPs

# R63 timeline math
def check_timeline_math(text, ep_num):
    issues = []
    # Pattern: "X tuổi năm YYYY" / "sinh năm YYYY"
    age_year = re.findall(r'(\d{2})\s*tuổi.*?(\d{4})', text)
    for age, year in age_year:
        age = int(age); year = int(year)
        birth = year - age
        if birth < 1900 or birth > 2026:
            issues.append(f"timeline impossible: {age} tuổi năm {year} → sinh {birth}")
    return issues

# R64 culture violations
CULTURE_FORBIDDEN = [
    r'\b(đám cưới)\s+(?:trong vòng tang|trong tang)\b',
    r'\b(đốt vàng mã)\s+(?:trong nhà thờ|trước Chúa)\b',
    r'\b(cha)\s+(?:đọc kinh|cúng)\b.*\b(chùa)\b',
]

# R65 invention detection (suspect numbers)
def check_invention(text):
    issues = []
    # Suspect: lương cô giáo > 30 triệu (unrealistic Vietnam pay)
    m = re.findall(r'lương.*?(\d+)\s*triệu', text)
    for amt in m:
        if int(amt) > 30:
            issues.append(f"suspicious salary: {amt} triệu (may be invention)")
    return issues

# R66 short sentence chain
def check_short_chain(text):
    issues = []
    body = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    body = re.sub(r'#[^\n]*\n', '', body)
    sentences = re.split(r'(?<=[.!?])\s+', body)
    chain = 0
    for s in sentences:
        wc = len(s.split())
        if 4 <= wc <= 6:
            chain += 1
            if chain == 3:
                issues.append(f"short chain ≥3: ...{s[:60]}...")
        else:
            chain = 0
    return issues

# R67 verb semantic
def check_verb_semantic(text):
    issues = []
    # Pattern: "không nhớ + tại sao/sao" (should be "không hiểu")
    m = re.findall(r'không nhớ\s+(?:tại sao|vì sao|sao)\b[^.]*', text)
    issues.extend([f"R67: '{x[:50]}' should use 'không hiểu'" for x in m])
    return issues

# R57 reveal vignette structure (count [pause] blocks in REVEAL)
def check_reveal_vignettes(text):
    m = re.search(r'#+\s*REVEAL.*?(?=#+\s*(?:PAYOFF|CLIFFHANGER)|$)', text, re.DOTALL | re.IGNORECASE)
    if not m: return []
    reveal = m.group()
    pauses = re.findall(r'\[pause:\d+ms\]', reveal)
    if not (3 <= len(pauses) <= 5):
        return [f"R57: REVEAL has {len(pauses)} pause blocks (target 3-5)"]
    return []

def audit_ep(text, ep_num):
    issues_by_rule = {
        'R43_filler': [],
        'R45_context': [],
        'R49_template': [],
        'R57_vignette': [],
        'R63_timeline': [],
        'R64_culture': [],
        'R65_invention': [],
        'R66_short_chain': [],
        'R67_verb_semantic': [],
    }

    # R43
    filler_count = sum(text.lower().count(f' {w} ') for w in FILLER_WORDS)
    if filler_count > FILLER_MAX_PER_EP:
        issues_by_rule['R43_filler'].append(f"{filler_count} fillers (max {FILLER_MAX_PER_EP})")

    # R45
    for pat in FORBIDDEN_CONTEXT:
        if re.search(pat, text, re.IGNORECASE):
            issues_by_rule['R45_context'].append(f"forbidden pattern: {pat}")

    # R57
    issues_by_rule['R57_vignette'] = check_reveal_vignettes(text)

    # R63
    issues_by_rule['R63_timeline'] = check_timeline_math(text, ep_num)

    # R64
    for pat in CULTURE_FORBIDDEN:
        if re.search(pat, text, re.IGNORECASE):
            issues_by_rule['R64_culture'].append(f"culture violation: {pat}")

    # R65
    issues_by_rule['R65_invention'] = check_invention(text)

    # R66
    issues_by_rule['R66_short_chain'] = check_short_chain(text)

    # R67
    issues_by_rule['R67_verb_semantic'] = check_verb_semantic(text)

    return issues_by_rule

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    print("=" * 70)
    print("AUDIT 9 RULES MISSING (R43/R45/R49/R57/R63/R64/R65/R66/R67)")
    print("=" * 70)

    eps = [(n, SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md')
           for n in (range(1, 91) if not args.ep else [args.ep])]

    rule_totals = Counter()
    all_eps_issues = {}
    for n, p in eps:
        if not p.exists(): continue
        text = p.read_text(encoding='utf-8')
        rule_issues = audit_ep(text, n)
        ep_total = sum(len(v) for v in rule_issues.values())
        if ep_total > 0:
            all_eps_issues[n] = rule_issues
            for rule, lst in rule_issues.items():
                rule_totals[rule] += len(lst)

    # R49 cross-EP template count
    print("\n[R49 template overuse 50 EPs]:")
    for pat in RECURRING_TEMPLATES:
        cnt = 0
        for n in range(1, 51):
            p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
            if p.exists():
                cnt += len(re.findall(pat, p.read_text(encoding='utf-8')))
        status = '⚠️' if cnt > TEMPLATE_MAX else '✓'
        print(f"  {status} {pat[:50]}: {cnt}/50 (max {TEMPLATE_MAX})")
        if cnt > TEMPLATE_MAX:
            rule_totals['R49_template'] += 1

    print(f"\n=== SUMMARY ===")
    print(f"EPs với issues: {len(all_eps_issues)}/50")
    for rule, count in rule_totals.most_common():
        if count > 0:
            print(f"  {rule}: {count}")
    total = sum(rule_totals.values())
    print(f"\nTOTAL: {total} issues across 9 rules")

    if not args.summary:
        # Top 5 EPs
        ep_totals = sorted([(n, sum(len(v) for v in iss.values())) for n, iss in all_eps_issues.items()], key=lambda x: -x[1])[:5]
        print(f"\nTop 5 EPs:")
        for n, c in ep_totals:
            print(f"  EP{n:02d}: {c}")

    out = SVHMP / 'runtime' / 'audit_r43_to_r67_report.json'
    out.write_text(json.dumps({
        'rule_totals': dict(rule_totals),
        'eps_with_issues': {str(k): v for k, v in all_eps_issues.items()},
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
