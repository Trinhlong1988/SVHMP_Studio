"""Render single section EP01 — per-section QA workflow.

Usage:
  python tools/render_section.py --section HOOK
  python tools/render_section.py --section SETUP --start 22 --end 33

Per-section sentence index ranges (verify trước render):
  HOOK         0-21    (~22 sentences)
  SETUP       22-90    (~68 sentences)
  INCIDENT    91-160   (~70 sentences)
  REVEAL     161-220   (~60 sentences)
  PAYOFF     221-270   (~50 sentences)
  CLIFFHANGER 271-292  (~22 sentences)
  (boundaries TBD per current spec)
"""
import json, sys, argparse, subprocess
from pathlib import Path

BASE = Path(r'D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio')
SPEC = BASE / 'output' / 'ep_01' / 'spec.json'
SECTIONS_DIR = BASE / 'output' / 'ep_01' / 'sections'
SECTIONS_DIR.mkdir(exist_ok=True)

# Section boundaries — verify with current spec
SECTION_RANGES = {
    'HOOK':        (0, 20),     # intro 7 + hook 13 (chunks 20-21 thuộc SETUP, đã fix 29/6)
    'SETUP':       (20, 90),
    'INCIDENT':    (90, 160),
    'REVEAL':      (160, 220),
    'PAYOFF':      (220, 270),
    'CLIFFHANGER': (270, 999),
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--section', required=True, choices=list(SECTION_RANGES.keys()))
    ap.add_argument('--start', type=int, help='Override start sentence index')
    ap.add_argument('--end', type=int, help='Override end sentence index')
    args = ap.parse_args()

    spec_full = json.loads(SPEC.read_text(encoding='utf-8'))
    total = len(spec_full['sentences'])

    start, end = SECTION_RANGES[args.section]
    if args.start is not None: start = args.start
    if args.end is not None: end = args.end
    end = min(end, total)

    sentences_subset = spec_full['sentences'][start:end]
    section_spec = {
        'sentences': sentences_subset,
        'sample_prompt': spec_full['sample_prompt'],
    }

    spec_section = SECTIONS_DIR / f'spec_{args.section.lower()}.json'
    output_wav = SECTIONS_DIR / f'{args.section.lower()}.wav'

    spec_section.write_text(json.dumps(section_spec, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f'Section: {args.section}')
    print(f'  Sentences: {len(sentences_subset)} (index {start}-{end-1})')
    print(f'  Spec: {spec_section}')
    print(f'  Output: {output_wav}')
    print()
    print('Preview first 3 sentences:')
    for i, s in enumerate(sentences_subset[:3]):
        print(f'  [{start+i}] "{s["text"][:80]}"')
    print('Preview last 3:')
    for i, s in enumerate(sentences_subset[-3:]):
        print(f'  [{end-3+i}] "{s["text"][:80]}"')
    print()
    print(f'TO RENDER (run manually via UV venv):')
    print(f'  cd C:/Users/Administrator/index-tts')
    print(f'  uv run --no-sync python "{BASE}/tools/svhmp_v13_render.py" --spec "{spec_section}" --output "{output_wav}"')

if __name__ == '__main__':
    main()
