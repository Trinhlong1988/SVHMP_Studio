"""VNSL Validator v1.0 — scan spec JSON, flag violations vs hiến pháp R65/R67/R72/R73."""
import json, re, sys, os, glob
from collections import Counter
from pathlib import Path

LEX_PATH = Path(__file__).parent.parent / 'data' / 'vnsl_lexicon.json'
LEX = json.load(open(LEX_PATH, encoding='utf-8'))

PRESENT_T = LEX['temporal']['PRESENT_specific']
PAST_VAG = LEX['temporal']['PAST_vague'] + LEX['temporal']['PAST_specific']
RECUR = LEX['temporal']['RECURRING']
TEMP_BASES = ['đêm', 'tối', 'khuya', 'sáng', 'chiều', 'sớm', 'hôm']

VERB_GUIDE = LEX['_verb_usage_guide']
FORBIDDEN = LEX['_forbidden_patterns']

class Issue:
    __slots__ = ('rule', 'severity', 'sec', 'ch', 'msg', 'fix')
    def __init__(self, rule, severity, sec, ch, msg, fix=''):
        self.rule = rule; self.severity = severity
        self.sec = sec; self.ch = ch; self.msg = msg; self.fix = fix
    def __repr__(self):
        return f"[{self.severity}][{self.rule}] s{self.sec} ch{self.ch}: {self.msg}{(' → '+self.fix) if self.fix else ''}"

def validate_chunk(sec, idx, text, prev_text='', next_text=''):
    issues = []
    tl = text.lower()

    # R72.1 — same-base temporal in 1 chunk (present+past with same word)
    for base in ['đêm', 'tối', 'lúc', 'khi', 'hôm']:
        if tl.count(base) >= 2:
            has_present = any(p in tl for p in PRESENT_T if base in p)
            has_past = any(p in tl for p in PAST_VAG if base in p)
            if has_present and has_past:
                issues.append(Issue('R72.1', 'HIGH', sec, idx,
                    f'"{base}" used for both present+past in 1 chunk',
                    f'rotate past → khuya/quãng xa xôi/thuở ấy'))

    # R72.2 — temporal density ≥3 in 1 chunk
    tot = sum(len(re.findall(rf'\b{t}\b', tl)) for t in TEMP_BASES)
    if tot >= 3:
        issues.append(Issue('R72.2', 'MED', sec, idx,
            f'{tot} temporal terms in 1 chunk',
            'reduce → use signature time once + vary'))

    # R72.3 — cross-chunk temporal overlap (same base in prev or next)
    for base in ['đêm', 'tối', 'khuya', 'hôm']:
        if re.search(rf'\b{base}\b', tl):
            for neighbor, label in [(prev_text, 'prev'), (next_text, 'next')]:
                if neighbor and re.search(rf'\b{base}\b', neighbor.lower()):
                    issues.append(Issue('R72.3', 'MED', sec, idx,
                        f'"{base}" overlaps with {label} chunk',
                        f'reword 1 of the 2 to non-{base} synonym'))
                    break

    # R67 — STOP-CONSONANT TAIL
    sents = [s.strip() for s in re.split(r'[.!?…]', text) if s.strip()]
    if sents:
        last_sent = sents[-1].strip().strip('"').strip("'").strip(',').strip()
        words = last_sent.split()
        if words:
            last_word = words[-1].lower().strip('.,!?…"\'')
            for entry in FORBIDDEN['stop_consonant_tail']:
                if last_word == entry['word']:
                    issues.append(Issue('R67', 'HIGH', sec, idx,
                        f'tail stop-consonant "{last_word}"',
                        entry['fix_examples'][0] if entry['fix_examples'] else 'reword tail to open-vowel or soft consonant'))

    # R73 — VERB MISUSE (thốt + others)
    for verb, guide in VERB_GUIDE.items():
        for bad in guide.get('INVALID_collocations', []) + guide.get('INVALID', []):
            # extract just the bad pattern (before " (")
            pat = bad.split(' (')[0].strip()
            if pat.lower() in tl:
                issues.append(Issue('R73', 'HIGH', sec, idx,
                    f'verb misuse "{pat}" ({verb})',
                    f'use {list(guide.get("alternative_when_wrong", {}).values())[0] if guide.get("alternative_when_wrong") else "valid_collocation"}'))

    # R3 — repetition ≥3 same content word in 1 chunk
    words = re.findall(r'\b\w{4,}\b', tl)
    cnt = Counter(words)
    for w, n in cnt.items():
        if n >= 3 and w not in {'không', 'những', 'chiếc', 'người', 'trong', 'cũng', 'nhưng', 'đang', 'phải', 'quang', 'chuyến'}:
            issues.append(Issue('R3', 'MED', sec, idx,
                f'word "{w}" ×{n} in 1 chunk',
                'vary with synonym'))

    return issues

def validate_spec(path):
    d = json.load(open(path, encoding='utf-8'))
    chunks = d.get('sentences') or d.get('chunks') or []
    texts = [(c.get('text', '') if isinstance(c, dict) else c) for c in chunks]
    sec = re.search(r'section_(\d+)', path).group(1) if re.search(r'section_(\d+)', path) else '?'
    all_issues = []
    for i, t in enumerate(texts):
        if not t: continue
        prev = texts[i-1] if i > 0 else ''
        nxt = texts[i+1] if i < len(texts)-1 else ''
        all_issues.extend(validate_chunk(sec, i, t, prev, nxt))
    return all_issues

def main(spec_paths):
    total = []
    for p in spec_paths:
        issues = validate_spec(p)
        total.extend(issues)
        print(f"\n=== {os.path.basename(p)} : {len(issues)} issue(s) ===")
        for iss in issues:
            print(f"  {iss}")
    print(f"\n{'='*60}\nTOTAL: {len(total)} issues across {len(spec_paths)} specs")
    by_rule = Counter(i.rule for i in total)
    by_sev = Counter(i.severity for i in total)
    print(f"By rule: {dict(by_rule)}")
    print(f"By severity: {dict(by_sev)}")
    return total

if __name__ == '__main__':
    if len(sys.argv) > 1:
        paths = sys.argv[1:]
    else:
        os.chdir(r'C:\Users\Administrator\Desktop\SVHMP_v10_workdir')
        paths = sorted(p for p in glob.glob('spec_ep01_section_*.json')
                       if '_v' not in p and 'backup' not in p and 'old' not in p)
    main(paths)
