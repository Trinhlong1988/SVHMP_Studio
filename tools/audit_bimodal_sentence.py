"""SVHMP — Bimodal sentence length audit (Agent 1 Ngạn pattern).

Mỗi section EP PHẢI có ít nhất 1 cụm 3 câu cụt (3-7 từ) xen kẽ 1 câu dài 60+ từ.
Flag EPs với monotone 15-25 từ đều (robotic feel).
"""
import re
import sys
import json
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

def main():
    print("=" * 70)
    print("BIMODAL SENTENCE LENGTH — Ngạn rhythm check")
    print("=" * 70)

    findings = []
    for n in range(1, 51):
        p = SVHMP / 'output' / f'ep_{n:02d}' / 'episode.md'
        if not p.exists(): continue
        text = p.read_text(encoding='utf-8')
        body = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        body = re.sub(r'^---\n.*?\n---\n', '', body, count=1, flags=re.DOTALL)
        body = re.sub(r'#[^\n]*\n', '', body)

        sentences = re.split(r'(?<=[.!?])\s+', body)
        lengths = [len(s.split()) for s in sentences if s.strip() and len(s.split()) > 1]

        if not lengths:
            continue

        # Bimodal check: count short (3-7), mid (8-25), long (26+, ideal 60+)
        short = sum(1 for l in lengths if 3 <= l <= 7)
        mid = sum(1 for l in lengths if 8 <= l <= 25)
        long = sum(1 for l in lengths if l >= 26)
        very_long = sum(1 for l in lengths if l >= 60)

        total = len(lengths)
        # Healthy: short ≥ 15% AND long ≥ 5% AND very_long ≥ 1
        # Unhealthy: short < 10% AND long < 3% (monotone mid)
        unhealthy = short / total < 0.10 and long / total < 0.05
        if unhealthy:
            findings.append((n, short, mid, long, very_long, total))

    print(f"\nMONOTONE 15-25 từ EPs (cần restore bimodal):")
    if findings:
        for n, s, m, l, vl, t in findings:
            print(f"  EP{n:02d}: short {s}({s*100//t}%) / mid {m}({m*100//t}%) / long {l} / very_long {vl} / total {t}")
    else:
        print("  ✓ ALL 50 EPs có bimodal distribution OK")

    out = SVHMP / 'runtime' / 'audit_bimodal.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({'monotone_eps': findings}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
