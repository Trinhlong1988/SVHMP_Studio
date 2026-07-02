"""Deep duplicate audit — không suy luận, chạy regex/counter thực tế.
- Lặp từ cùng câu (3+ lần exclude stopwords)
- Lặp phrase cross-chunk 3-5 word
- Pattern lặp dạng "X không Y, nhưng X Y" hoặc "X định Y X đã định Y"
"""
import json
import os
import sys
import re
import atexit
from collections import Counter

# Round 14 dashboard live hook
_TOOLS = os.path.dirname(os.path.abspath(__file__))
if _TOOLS not in sys.path: sys.path.insert(0, _TOOLS)
try:
    from render_progress_hook import RenderProgress
except ImportError:
    class RenderProgress:
        def __init__(self, **kw): self.current_step = 0; self.total_steps = 1
        def start(self, *a, **k): pass
        def tick(self, *a, **k): pass
        def done(self, *a, **k): pass
        def fail(self, *a, **k): pass

_prog = RenderProgress(cmd='dupe_audit', ep=1, total_steps=3)
atexit.register(lambda: _prog.fail('exit without done') if _prog.current_step < _prog.total_steps else None)
_prog.start('main')

WD = os.environ.get('SVHMP_WORKDIR', os.path.expanduser(r'~/Desktop/SVHMP_v10_workdir'))
if not os.path.isdir(WD):
    import sys
    sys.exit(f"[SKIP] Legacy workdir khong ton tai: {WD} — set env SVHMP_WORKDIR tro toi thu muc chua spec_ep01_section_*.json de chay tool nay.")

STOPWORDS = {'anh', 'cô', 'tôi', 'là', 'có', 'không', 'mà', 'và', 'của', 'một',
             'như', 'hai', 'những', 'này', 'ở', 'với', 'để', 'từ', 'cũng', 'đã',
             'thì', 'sẽ', 'cho', 'bị', 'trong', 'ra', 'lên', 'xuống', 'cô', 'em',
             'chú', 'sao', 'gì', 'thế', 'vậy', 'nào', 'đây', 'đó', 'đâu', 'rồi',
             'lại', 'nữa', 'nhưng', 'thôi', 'cứ', 'vẫn', 'còn', 'mới', 'mỗi',
             'bao', 'giờ', 'lúc', 'khi', 'năm', 'tay'}

PATTERN_LẶP = [
    # X định Y X đã định Y
    (r'(định \w+).{0,20}đã \1', 'X định Y, đã định Y'),
    # không X nhưng X
    (r'(không\s+\w+).{0,20}nhưng\s+\1', 'không X nhưng X'),
    # X rồi X
    (r'(\b\w{3,}\b)\s+rồi\s+\1', 'X rồi X'),
    # vừa X vừa X
    (r'(vừa\s+\w+).{0,15}vừa\s+\w+', 'vừa X vừa Y (verify)'),
]

print('=' * 70)
print('DEEP DUPE AUDIT — verify thực tế không suy luận')
print('=' * 70)

for fn in sorted(['1_hook', '2_setup', '3_incident', '4_reveal', '5_payoff', '6_cliffhanger']):
    p = os.path.join(WD, f'spec_ep01_section_{fn}.json')
    spec = json.load(open(p, encoding='utf-8'))
    sents = spec['sentences']
    print(f'\n--- s{fn[0]} ({len(sents)} chunks) ---')
    issues = 0

    # Build all text for cross-chunk audit
    all_text = ' '.join(s['text'] for s in sents).lower()

    # 1. Pattern lặp cùng câu
    for i, s in enumerate(sents, 1):
        text = s['text']
        for sent in re.split(r'[.!?]', text):
            sent = sent.strip()
            if not sent:
                continue
            for pat, name in PATTERN_LẶP:
                m = re.search(pat, sent.lower())
                if m:
                    print(f'  PATTERN ch{i} "{name}": ...{sent[max(0,m.start()-15):m.end()+15]}...')
                    issues += 1

    # 2. Lặp 3+ lần từ trong cùng câu (excl stopword)
    for i, s in enumerate(sents, 1):
        for sent in re.split(r'[.!?]', s['text']):
            sent = sent.strip()
            if not sent:
                continue
            words = sent.lower().split()
            wc = Counter(words)
            for w, n in wc.items():
                if n >= 3 and len(w) >= 2 and w not in STOPWORDS:
                    print(f'  LẶP 3x ch{i} "{w}" {n}x: "{sent[:90]}"')
                    issues += 1

    # 3. Cross-chunk: phrase 3-word repeat 3+ lần trong section
    words = re.findall(r'\b\w+\b', all_text)
    phrases_3 = [' '.join(words[i:i+3]) for i in range(len(words)-2)]
    phrase_count = Counter(phrases_3)
    for phrase, count in phrase_count.most_common(20):
        # Skip stopword phrases
        ws = phrase.split()
        if all(w in STOPWORDS for w in ws):
            continue
        if count >= 3 and len(phrase) > 12:
            # Skip subject "anh không" "cô gái" repetition (intentional in narrative)
            if phrase.startswith('anh ') or phrase.startswith('cô '):
                continue
            print(f'  CROSS-CHUNK 3-word "{phrase}" {count}x')
            issues += 1

    print(f'  → {issues} duplicate issues')

_prog.done(success=True, final_path='dupe_audit complete')
