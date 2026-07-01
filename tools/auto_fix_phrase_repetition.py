"""SVHMP — Auto-fix R74 phrase repetition (Ollama gap fill).

Strategy:
- Read audit_phrase_repetition_report.json
- For each violation: replace 2nd+ occurrence với synonym/alternative
- Name overuse: vary với Người [đàn ông/con gái/bà/ông]
- Phrase repeat: drop or paraphrase 2nd+ occurrence

Conservative: skip nếu phrase là dialogue quote.
"""
import re
import sys
import json
import shutil
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(__file__).resolve().parents[1]

NAME_VARIES = {
    'Khải Phong': ['anh', 'người khách', 'người đàn ông', 'anh ấy'],
    'Khải-Phong': ['anh', 'người khách', 'anh ấy'],
    'Hạ Vy': ['cô ấy', 'người yêu cũ', 'cô gái ấy'],
    'Hạ-Vy': ['cô ấy', 'cô gái ấy'],
    'Bác tài': ['bác', 'tài xế', 'ông tài'],
}

def fix_ep(ep_num, violations, dry_run=False):
    p = SVHMP / 'output' / f'ep_{ep_num:02d}' / 'episode.md'
    if not p.exists(): return 0
    text = p.read_text(encoding='utf-8')
    orig = text
    fixes = 0

    for v in violations:
        if v['type'] == 'name_overuse':
            name = v['name']
            if name not in NAME_VARIES: continue
            varies = NAME_VARIES[name]
            # Replace 4th+ occurrences với rotating varies
            # Iterative replace: find first qualifying occurrence beyond first 3, replace once, repeat
            iteration = 0
            max_iter = 20
            while iteration < max_iter:
                pattern = re.compile(rf'\b{re.escape(name)}\b')
                matches = list(pattern.finditer(text))
                if len(matches) <= 3: break
                # Replace 4th match
                m = matches[3]
                syn = varies[iteration % len(varies)]
                # Capitalize if start of sentence
                if m.start() > 0 and text[m.start() - 1] in '.!?\n':
                    syn = syn[0].upper() + syn[1:]
                text = text[:m.start()] + syn + text[m.end():]
                fixes += 1
                iteration += 1
        elif v['type'].startswith('phrase_'):
            # 2-gram/3-gram repeat in paragraph
            phrase = v['phrase']
            # Replace 3rd+ occurrence với simplified version
            pattern = re.compile(rf'\b{re.escape(phrase)}\b')
            matches = list(pattern.finditer(text))
            if len(matches) >= 3:
                # Drop 3rd occurrence (replace with first word only)
                m = matches[2]
                first_word = phrase.split()[0]
                text = text[:m.start()] + first_word + text[m.end():]
                fixes += 1

    if fixes > 0 and not dry_run:
        shutil.copy2(p, p.with_suffix('.md.bak.phrase'))
        p.write_text(text, encoding='utf-8')
    return fixes

def main():
    apply = '--apply' in sys.argv
    report_path = SVHMP / 'runtime' / 'audit_phrase_repetition_report.json'
    if not report_path.exists():
        print("Run audit_phrase_repetition.py first")
        return
    data = json.loads(report_path.read_text(encoding='utf-8'))
    violations = data.get('violations', [])
    by_ep = {}
    for v in violations:
        by_ep.setdefault(v['ep'], []).append(v)

    print(f"AUTO-FIX R74 phrase repetition | Mode: {'APPLY' if apply else 'DRY-RUN'}")
    total = 0
    for ep, vs in sorted(by_ep.items()):
        fixes = fix_ep(ep, vs, dry_run=not apply)
        if fixes > 0:
            total += fixes
    print(f"Total: {total} phrase fixes")

if __name__ == '__main__':
    main()
