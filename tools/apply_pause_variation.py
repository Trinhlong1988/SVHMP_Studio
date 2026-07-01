"""Apply varied pauses per chunk based on context (R98 + R97 + Mr.Long master pattern).

Pause rules:
  short (≤5 words):       800ms  (dialogue exchange tempo)
  medium (6-15 words):    1200ms (narrative default)
  long (≥16 words):       1500ms (long breath after)
  last chunk of section:  2000ms (section transition)
  paragraph break:        1500ms (default)
"""
import json
import sys
from pathlib import Path

def apply_variation(spec_path):
    spec = json.loads(Path(spec_path).read_text(encoding='utf-8'))
    sents = spec['sentences']
    for i, s in enumerate(sents):
        word_count = len(s['text'].split())
        is_last = (i == len(sents) - 1)
        if is_last:
            s['pause_after_ms'] = 2000  # section transition
        elif word_count <= 5:
            s['pause_after_ms'] = 800  # short dialogue tempo
        elif word_count >= 16:
            s['pause_after_ms'] = 1500  # long sentence breath
        else:
            s['pause_after_ms'] = 1200  # medium default
    Path(spec_path).write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding='utf-8')
    return spec

if __name__ == '__main__':
    base = Path(__file__).resolve().parents[1] / r'output/ep_01/sections'
    for section in ['setup', 'incident', 'reveal', 'payoff', 'cliffhanger']:
        fp = base / f'spec_{section}.json'
        if fp.exists():
            spec = apply_variation(fp)
            from collections import Counter
            pauses = Counter(s['pause_after_ms'] for s in spec['sentences'])
            print(f'{section.upper()}: {len(spec["sentences"])} chunks, pauses: {dict(pauses)}')
