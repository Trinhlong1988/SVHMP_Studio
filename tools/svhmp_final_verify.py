"""Final verify trước render full EP01 — scan tất cả patterns đã fix."""
import json
import os
import re
import subprocess
from collections import Counter

WD = r'C:\Users\Administrator\Desktop\SVHMP_v10_workdir'
SPECS_NAMES = ['1_hook', '2_setup', '3_incident', '4_reveal', '5_payoff', '6_cliffhanger']

# Tất cả pattern bug Mr.Long đã catch
BUG_PATTERNS = {
    'Bất chợt': 'mispronounce → Bỗng nhiên/Đột nhiên',
    'Quang nhớ rồi': 'mispronounce → Anh nhớ rồi',
    'không tưởng': 'idiom sai → không nghĩ đến',
    'tay sạch': 'detail rời nghĩa',
    'định nói câu tôi đã định nói': 'lặp pattern',
    'Anh không định kể, nhưng anh kể': 'lặp pattern cộc',
    'Đồng hồ này tám năm': 'lặp ch10+ch12 s2',
    'như vô tình, như không vô tình': 'paradox awkward',
    'một cái lắc rất chậm': 'lặp "lắc"',
    'cô không nói gì,': 'vô hồn',
    'anh không nói gì.': 'vô hồn (s5 ch19)',
    'Trưa ngày thứ Bảy không có tin': 'lặp pattern',
    'Sáng ngày thứ Bảy không có tin': 'lặp pattern',
    'Bác tài liếc gương chiếu hậu, bác không nói': 'lặp vô hồn',
    'Tiếng anh khẽ': 'mơ hồ → Anh nói rất khẽ',
    'Quang không biết là mưa hay là gì khác': 'vô hồn',
    'Quang cứng người': 'cứng → uyển chuyển',
    'Cô tóc cột thấp': 'khó nghe',
    'Cô ấy đi rồi.': 'khô → "Cô ấy... đi xa rồi"',
    'Mẹ Hà nói, máy bay tới nơi an toàn': 'khô không cảm xúc',
    'Cô tóc xõa,': 's6 ch2 cụt mirror Hà',
    'kim chỉ bảy giờ mười.': 's6 ch5 cụt',
    'Anh đi ngang ghế ba.': 'lặp pattern 3 chunks',
    'Cô nhíu mày, cô cúi xuống, cô nhặt lên': 'lặp "cô"',
    'Ông cụ ôm radio như cũ.': 'lặp "như cũ"',
    'Bác tài chậm rãi đặt tay lên vô-lăng. Xe lại lăn bánh chậm rãi': 'lặp "chậm rãi"',
}

print('=' * 70)
print('FINAL VERIFY — scan tất cả 26 pattern bug đã fix')
print('=' * 70)

total_remaining = 0
for fn in SPECS_NAMES:
    p = os.path.join(WD, f'spec_ep01_section_{fn}.json')
    spec = json.load(open(p, encoding='utf-8'))
    text_all = ' '.join(s['text'] for s in spec['sentences'])
    print(f'\n--- s{fn[0]} ({len(spec["sentences"])} chunks) ---')
    found = 0
    for pat, reason in BUG_PATTERNS.items():
        if pat in text_all:
            print(f'  🚨 STILL "{pat}" → {reason}')
            found += 1
            total_remaining += 1
    if found == 0:
        print(f'  ✓ clean — 0/26 bug pattern remaining')

print()
print(f'TOTAL remaining: {total_remaining}/26 bug pattern × 6 specs')
print()

# Preflight all
print('=== PREFLIGHT 11 rules ===')
for fn in SPECS_NAMES:
    p = os.path.join(WD, f'spec_ep01_section_{fn}.json')
    r = subprocess.run(['python', r'C:\tmp\svhmp_preflight_qa.py', p],
                       capture_output=True, text=True, encoding='utf-8')
    print(f'  s{fn[0]}: {r.stdout.splitlines()[0]}')
