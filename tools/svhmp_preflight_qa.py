"""SVHMP pre-flight QA — check 10 hard rules trước render.
Usage: python svhmp_preflight_qa.py <spec.json>
Exit 0 = PASS, exit 1 = FAIL (block render).
"""
import sys
import json
import re

if len(sys.argv) < 2:
    print('Usage: svhmp_preflight_qa.py <spec.json>')
    sys.exit(2)

spec = json.load(open(sys.argv[1], encoding='utf-8'))
sents = spec['sentences']
issues = []

# Dialog markers — câu ngắn được phép nếu là dialog/signature
DIALOG_MARKERS = [
    'dạ', 'người ơi', 'quang ơi', 'tôi sợ', 'cảm ơn cô', 'của tôi à',
    'cô nhỏ nhẹ', 'tôi không nhớ', 'chưa tới lúc', 'tách', 'hà cười',
    'anh đã biết',  # internal monologue beat
    'cô ấy', 'đi xa rồi',  # nghẹn dialog 25/6
]

ENDING_PHRASES = [
    'nhớ mãi', 'nhớ rất rõ', 'còn vọng', 'chưa quên', 'mãi mãi',
    'không thể nào quên', 'chưa biết', 'còn theo tôi mãi',
]

GOOD_TRANSITIONS = [
    'đột nhiên', 'bỗng nhiên', 'bỗng dưng', 'lúc này', 'lúc đó',
    'trong gương', 'bên ngoài', 'phía sau', 'bên cạnh', 'cùng lúc',
    'mãi về sau', 'hồi đó', 'nhưng', 'sau đó', 'khi đó',
    'trên ghế',  # vị trí marker = transition cho hành khách
    'trong ký ức', 'lúc ấy', 'đến đây', 'quay lại', 'trong lúc đó',
]

PASSENGER_CHARS = ['ông cụ', 'cô y tá', 'anh trung niên', 'cô gái ghế tám']
MAIN_CHARS = ['quang', 'hà', 'bác tài']


for i, s in enumerate(sents, 1):
    text = s['text']
    text_lower = text.lower()

    # Rule 1: Short fragments ≤3 từ (skip dialog)
    for sent in re.split(r'[.!?]', text):
        sent = sent.strip()
        sent_lower = sent.lower()
        if 1 <= len(sent.split()) <= 3:
            # Check dialog/signature exception
            if any(m in sent_lower for m in DIALOG_MARKERS):
                continue
            issues.append(f'R1 ch{i}: SHORT ({len(sent.split())}w) "{sent}"')

    # Rule 2: Câu cụt mất object
    if re.search(r'(anh mới biết|hà nói thế|cô không nói|mãi về sau,? anh.{0,15})\.\s*$', text_lower):
        issues.append(f'R2 ch{i}: CỤT cuối "{text[-50:]}"')

    # Rule 3: Lặp từ
    for w in ['cầm', 'đều', 'tay']:
        n = len(re.findall(rf'\b{re.escape(w)}\b', text_lower))
        if n >= 3:
            issues.append(f'R3 ch{i}: LẶP "{w}" {n}x')

    # Rule 17: Lặp PHRASE 3-5 words trong cùng chunk (MỚI 26/6)
    from collections import Counter
    words = re.findall(r'\b\w+\b', text_lower)
    for n_gram in [3, 4, 5]:
        phrases = [' '.join(words[j:j+n_gram]) for j in range(len(words)-n_gram+1)]
        pc = Counter(phrases)
        for p, count in pc.items():
            if count >= 2 and len(p) >= 10:
                # Skip stopword phrases
                if any(p.startswith(x) for x in ['anh không', 'cô không', 'tôi không', 'có lẽ', 'một cái', 'anh cũng']):
                    continue
                # Skip subject "chiếc đồng hồ" - allowed motif
                if 'chiếc đồng hồ' in p:
                    continue
                # Skip "đi ngang ghế" - allowed walking sequence
                if 'đi ngang ghế' in p:
                    continue
                issues.append(f'R17 ch{i}: LẶP PHRASE "{p}" {count}x trong chunk')
                break

    # Rule 4: Trigger mispronounce
    for trig in ['Bất chợt', 'Quang nhớ rồi', 'Quang là']:
        if trig in text:
            issues.append(f'R4 ch{i}: TRIGGER "{trig}"')

    # Rule 7: Detail rời
    if 'tay sạch' in text_lower:
        issues.append(f'R7 ch{i}: DETAIL rời "tay sạch"')

# Rule 5: Chunk cuối
last = sents[-1]['text']
last_lower = last.lower()
if len(last) < 60:
    if not any(ep in last_lower for ep in ENDING_PHRASES):
        issues.append(f'R5 ch{len(sents)} LAST: SHORT {len(last)}c + thiếu ending phrase')
elif not any(ep in last_lower for ep in ENDING_PHRASES):
    issues.append(f'R5 ch{len(sents)} LAST: thiếu ending phrase')

# Rule 10: True scene switch boundary (topic switch + bad open + same passenger ghế)
for i in range(len(sents) - 1):
    cur = sents[i]['text']
    nxt_text = sents[i+1]['text']
    # Skip if cur ends with question (natural dialog flow)
    if cur.rstrip().endswith('?'):
        continue
    first_sent = [s.strip() for s in re.split(r'[.!?]', nxt_text) if s.strip()]
    if not first_sent:
        continue
    first_lower = first_sent[0].lower()
    cur_lower = cur.lower()

    # Scan ENTIRE chunk with word-boundary regex (KHÔNG substring match)
    all_chars = PASSENGER_CHARS + MAIN_CHARS
    cur_chars = set(c for c in all_chars if re.search(rf'\b{re.escape(c)}\b', cur_lower))
    nxt_chars = set(c for c in all_chars if re.search(rf'\b{re.escape(c)}\b', nxt_text.lower()))

    # TRUE scene switch: topic disjoint + opens flat
    if cur_chars and nxt_chars and cur_chars.isdisjoint(nxt_chars):
        if not any(t in first_lower[:30] for t in GOOD_TRANSITIONS):
            issues.append(f'R10 ch{i+1}→ch{i+2}: SCENE SWITCH {cur_chars}→{nxt_chars} no transition')


if issues:
    print(f'PREFLIGHT FAIL — {len(issues)} issues')
    for iss in issues:
        print(f'  {iss}')
    sys.exit(1)
else:
    print(f'PREFLIGHT PASS — {len(sents)} chunks OK')
    sys.exit(0)
