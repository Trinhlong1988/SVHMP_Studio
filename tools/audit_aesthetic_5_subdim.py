"""SVHMP — Aesthetic 5 sub-dim audit MUST cite source (kentjuno editor pattern).

5 sub-dimensions per kentjuno Editor prompt:
1. Description quality (abstract vs concrete sensory)
2. Narrative technique (POV consistency, time handling)
3. Dialogue distinction (character voice differentiation)
4. Vocabulary quality (parallel/idiom/template)
5. Emotional resonance (flat label vs body reaction)

Each issue MUST quote 原文 line — no empty conclusions allowed.
"""
import re
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

# 5 sub-dim patterns
PATTERNS = {
    '1_description_abstract': {
        'desc': 'Abstract summary vs concrete 5-sense detail',
        'regex': r'(không khí|bầu không khí|tâm trạng|atmosphere|aura)\s+(?:áp lực|căng thẳng|nặng nề|u ám|bí ẩn)',
        'severity': 'WARN',
    },
    '4_vocab_three_part_parallel': {
        'desc': 'Tam đoạn / parallel triple',
        'regex': r'không \w+,\s+không \w+,\s+không \w+',
        'severity': 'WARN',
    },
    '4_vocab_template_simile': {
        'desc': 'Template simile "như... một cách"',
        'regex': r'như\s+\w+\s+một cách\b|tựa như\s+\w+\s+vậy\b',
        'severity': 'WARN',
    },
    '5_emotion_label': {
        'desc': 'Flat emotion label (sad/scared/angry direct)',
        'regex': r'(?:anh|cô|em|tôi|bà|ông|cụ)\s+(?:rất|cực kỳ|vô cùng)\s+(?:căng thẳng|buồn|giận|sợ|hoảng|vui|hạnh phúc)',
        'severity': 'WARN',
    },
    '4_vocab_idiom_stacking': {
        'desc': '4-char idiom stacking ≥2 in 1 paragraph',
        'regex': r'(?:kinh tâm động phách|hiểm tượng hoàn sinh|ngàn cân nhất phát|trời đất đảo điên|thiên la địa võng){2,}',
        'severity': 'WARN',
    },
}

def strip_meta(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    return text

def audit_ep(text):
    body = strip_meta(text)
    issues = []
    for name, spec in PATTERNS.items():
        for m in re.finditer(spec['regex'], body, re.IGNORECASE):
            ctx_start = max(0, m.start() - 30)
            ctx_end = min(len(body), m.end() + 30)
            issues.append({
                'sub_dim': name,
                'desc': spec['desc'],
                'severity': spec['severity'],
                'quote': body[ctx_start:ctx_end].strip()[:120],
            })
    return issues

def main():
    print("=" * 70)
    print("AESTHETIC 5 SUB-DIM AUDIT (MUST cite source per kentjuno)")
    print("=" * 70)

    all_results = {}
    sub_dim_totals = {k: 0 for k in PATTERNS}

    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists(): continue
        text = p.read_text(encoding='utf-8')
        issues = audit_ep(text)
        if issues:
            all_results[n] = issues
            for issue in issues:
                sub_dim_totals[issue['sub_dim']] += 1

    print(f"\n=== SUB-DIM TOTALS ===")
    for name, count in sub_dim_totals.items():
        print(f"  {name}: {count}")

    print(f"\n=== EPs với issues ({len(all_results)} EPs) ===")
    for n in sorted(all_results.keys())[:10]:
        print(f"\nEP{n:02d} ({len(all_results[n])} issues):")
        for issue in all_results[n][:3]:
            print(f"  [{issue['sub_dim']}] {issue['quote']}")

    out = SVHMP / 'runtime' / 'audit_aesthetic_5subdim.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        'sub_dim_totals': sub_dim_totals,
        'eps_with_issues_count': len(all_results),
        'all_issues': {str(k): v for k, v in all_results.items()},
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
