"""Audit chi tiết TỪNG CÂU ý lặp cross-section + intra-section."""
import json
import os
import re
from collections import Counter, defaultdict

WD = r'C:\Users\Administrator\Desktop\SVHMP_v10_workdir'
SPECS = ['1_hook', '2_setup', '3_incident', '4_reveal', '5_payoff', '6_cliffhanger']

# Load all specs
all_specs = {}
for fn in SPECS:
    p = os.path.join(WD, f'spec_ep01_section_{fn}.json')
    all_specs[fn] = json.load(open(p, encoding='utf-8'))

# Build phrase index: phrase → list of (section, chunk_id)
phrase_idx = defaultdict(list)
for fn, spec in all_specs.items():
    for i, s in enumerate(spec['sentences'], 1):
        text = s['text'].lower()
        words = re.findall(r'\b\w+\b', text)
        # 4-word + 5-word phrases
        for n in [4, 5]:
            for j in range(len(words) - n + 1):
                phrase = ' '.join(words[j:j+n])
                if len(phrase) > 15:
                    phrase_idx[phrase].append((fn, i))

# Find duplicates ≥2 (cross-section or intra)
WHITELIST = {
    'chiếc đồng hồ', 'kim đồng hồ', 'cô gái ghế tám', 'trên ghế ba',
    'trên ghế chín', 'trên ghế mười', 'lòng bàn tay', 'kim chỉ bảy giờ mười',
    'bảy giờ mười', 'bác tài', 'một câu chưa', 'câu chưa kịp nói',
}

dupes = []
for phrase, locs in phrase_idx.items():
    if len(locs) < 2:
        continue
    if any(w in phrase for w in WHITELIST):
        continue
    if phrase.startswith(('anh ', 'cô ', 'tôi ', 'có ', 'mỗi ', 'một ')):
        continue
    dupes.append((phrase, locs))

dupes.sort(key=lambda x: (-len(x[1]), -len(x[0])))

print(f'=== REPEAT PHRASES cross-section ({len(dupes)} found) ===')
for phrase, locs in dupes[:30]:
    sections = set(l[0] for l in locs)
    if len(sections) >= 2:  # ACTUAL cross-section
        print(f'\n  📌 "{phrase}" ({len(locs)}x)')
        for s, ch in locs:
            text = all_specs[s]['sentences'][ch-1]['text']
            print(f'     s{s[0]} ch{ch}: ...{text[max(0,text.lower().find(phrase)-15):text.lower().find(phrase)+len(phrase)+25]}...')
