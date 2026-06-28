"""SVHMP R62 — Audit anaphora liên tiếp "người/cô/anh/ông/bà..." > 2.

Mr.Long 28/6: "người lặp đi lặp lại liên nhau quá 2 lần nghe nhàm chán như lỗi"

Rule: CẤM từ chỉ định danh (người/cô/anh/chị/ông/bà/em/cụ) lặp liền tiếp > 2
trong 3 câu liền.

Detection:
- scan câu liên tiếp (split . ! ?)
- check first word
- if same trigger word repeated >2 trong 3 câu liền → HIGH

Usage: python tools/audit_anaphora_consecutive.py [--ep N]
"""
import re
import sys
import argparse
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

TRIGGER_WORDS = {'người', 'cô', 'anh', 'chị', 'ông', 'bà', 'em', 'cụ', 'tôi', 'Khải', 'bác'}
MAX_CONSECUTIVE = 2

def strip_meta(text):
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'^---\n.*?\n---\n', '', text, count=1, flags=re.DOTALL)
    return text

def get_first_meaningful_word(s):
    """Get first content word, skip punctuation/quote."""
    m = re.match(r'^["\'—\s\(\)]*([A-ZĐÂÊÔƠƯÁÀẢÃẠăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵa-zA-Z]+)', s)
    return m.group(1) if m else None

def audit_episode(text):
    issues = []
    body = strip_meta(text)
    # Split into paragraphs
    paragraphs = re.split(r'\n\s*\n', body)
    for pidx, para in enumerate(paragraphs):
        if not para.strip() or para.startswith('#') or para.startswith('[pause') or para.startswith('---'):
            continue
        if para.startswith('|') or para.startswith('-'):
            continue
        sentences = re.split(r'(?<=[.!?])\s+', para)
        # Look for SAME trigger word at start of consecutive sentences
        chain = []
        chain_word = None
        for sidx, s in enumerate(sentences):
            first = get_first_meaningful_word(s)
            first_l = first.lower() if first else None
            if first_l and first_l in {w.lower() for w in TRIGGER_WORDS}:
                if first_l == chain_word:
                    chain.append((sidx, first_l, s[:80]))
                else:
                    # Word changed — flush old chain if violated
                    if len(chain) > MAX_CONSECUTIVE:
                        issues.append({
                            'para_index': pidx,
                            'chain_length': len(chain),
                            'first_word': chain[0][1],
                            'sentences': [c[2] for c in chain],
                            'severity': 'HIGH',
                        })
                    chain = [(sidx, first_l, s[:80])]
                    chain_word = first_l
            else:
                if len(chain) > MAX_CONSECUTIVE:
                    issues.append({
                        'para_index': pidx,
                        'chain_length': len(chain),
                        'first_word': chain[0][1],
                        'sentences': [c[2] for c in chain],
                        'severity': 'HIGH',
                    })
                chain = []
                chain_word = None
        if len(chain) > MAX_CONSECUTIVE:
            issues.append({
                'para_index': pidx,
                'chain_length': len(chain),
                'first_word': chain[0][1],
                'sentences': [c[2] for c in chain],
                'severity': 'HIGH',
            })
    return issues

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int)
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()

    print("=" * 70)
    print("R62 AUDIT — Anaphora consecutive >2 (nhàm chán)")
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
                print(f"\nEP{n:02d}: {len(issues)} anaphora chains")
                for v in issues[:3]:
                    print(f"  Para#{v['para_index']} chain x{v['chain_length']} of '{v['first_word']}':")
                    for s in v['sentences'][:4]:
                        print(f"    - {s}...")

    print(f"\nSUMMARY: {total} HIGH in {len(eps_with)} EPs")
    for n, c in sorted(eps_with, key=lambda x: -x[1])[:10]:
        print(f"  EP{n:02d}: {c}")

    out = SVHMP / 'runtime' / 'audit_anaphora_consecutive_report.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        'total': total, 'eps': eps_with, 'violations': all_v,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Report: {out}")
    return 0 if total == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
