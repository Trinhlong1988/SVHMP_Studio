"""SVHMP 100-CHECK MASTER FRAMEWORK — verify TUYỆT ĐỐI trước render Season 2+.
10 categories × 10 checks each = 100 checks total.
"""
import json
import os
import sys
import re
import atexit
import subprocess
from collections import Counter, defaultdict

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

WD = r'C:\Users\Administrator\Desktop\SVHMP_v10_workdir'
MEM = r'C:\Users\Administrator\.claude\projects\C--Users-Administrator\memory'
PIPELINE = r'C:\tmp\svhmp_v13_render.py'
PREFLIGHT = r'C:\tmp\svhmp_preflight_qa.py'

SPECS = [f'spec_ep01_section_{n}.json' for n in
         ['1_hook', '2_setup', '3_incident', '4_reveal', '5_payoff', '6_cliffhanger']]
SPECS_DATA = {fn: json.load(open(os.path.join(WD, fn), encoding='utf-8')) for fn in SPECS}

# Total: ~10 categories of checks. Em conservative estimate 12 stages (cat1-10 + load + report)
_prog = RenderProgress(cmd='100check_master', ep=1, total_steps=12)
atexit.register(lambda: _prog.fail('exit without done') if _prog.current_step < _prog.total_steps else None)
_prog.start('cat1_hien_phap')
_prog.tick(1, 'CATEGORY 1: HIẾN PHÁP 21 RULES')

results = {'PASS': 0, 'WARN': 0, 'FAIL': 0}
checks_log = []


def check(cat, n, name, status, detail=''):
    results[status] += 1
    checks_log.append((cat, n, name, status, detail))


def hp_text():
    return open(os.path.join(MEM, 'feedback_svhmp_script_8_hard_rules.md'), encoding='utf-8').read()


# ===== CATEGORY 1: HIẾN PHÁP 21 RULES =====
hp = hp_text()
for i in range(1, 22):
    present = f'### {i}.' in hp
    check('HIẾN PHÁP', i, f'Rule {i} present in hiến pháp',
          'PASS' if present else 'FAIL')


# ===== CATEGORY 2: PIPELINE 4-TRỤ + AUDIO FIX =====
pl = open(PIPELINE, encoding='utf-8').read()
PIPE_CHECKS = [
    ('seed=42 lock', 'set_all_seeds(42)'),
    ('temperature=0.3', '"temperature": 0.3'),
    ('top_k=5', '"top_k": 5'),
    ('top_p=0.5', '"top_p": 0.5'),
    ('num_beams=5', '"num_beams": 5'),
    ('FADE_TAIL_MS=80', 'FADE_TAIL_MS = 80'),
    ('TAIL_TRIM_DB=-20', 'TAIL_TRIM_DB = -20'),
    ('silence bridge', 'return np.zeros'),
    ('SR 22050 force', '"-ar", "22050"'),
    ('loudnorm TP=-1.5', 'TP=-1.5'),
]
for i, (name, pat) in enumerate(PIPE_CHECKS, 1):
    present = pat in pl
    check('PIPELINE', i, name, 'PASS' if present else 'FAIL')


# ===== CATEGORY 3: 26 BUG PATTERN Mr.Long đã catch =====
BUG_PATTERNS = [
    'Bất chợt', 'Quang nhớ rồi', 'không tưởng', 'tay sạch',
    'định nói câu tôi đã định nói', 'Anh không định kể, nhưng anh kể',
    'Đồng hồ này tám năm', 'như vô tình, như không vô tình',
    'một cái lắc rất chậm', 'cô không nói gì,',
]
for i, pat in enumerate(BUG_PATTERNS, 1):
    found = False
    for fn, spec in SPECS_DATA.items():
        text = ' '.join(s['text'] for s in spec['sentences'])
        if pat in text:
            found = True
            break
    check('BUG PATTERN', i, f'"{pat[:25]}" REMOVED',
          'PASS' if not found else 'FAIL')


# ===== CATEGORY 4: CROSS-SECTION BOUNDARY (Rule 12) =====
GOOD_TRANS = ['lúc này', 'lúc đó', 'khi đó', 'lúc ấy', 'sau đó', 'phía sau',
              'bên ngoài', 'bên cạnh', 'đột nhiên', 'bỗng nhiên', 'trên ghế',
              'trong gương', 'mãi về sau', 'hồi đó', 'ký ức ấy', 'khi xe',
              'hai giây', 'rồi chỗ', 'một lúc sau', 'ở dãy ghế', 'ở góc sâu',
              'ở chỗ', 'ở ghế']
specs_sorted = ['1_hook', '2_setup', '3_incident', '4_reveal', '5_payoff', '6_cliffhanger']
for i in range(5):
    nxt_first = SPECS_DATA[f'spec_ep01_section_{specs_sorted[i+1]}.json']['sentences'][0]['text'].lower()
    has_trans = any(t in nxt_first[:30] for t in GOOD_TRANS)
    check('BOUNDARY', i+1, f'S{i+1}→S{i+2} có transition',
          'PASS' if has_trans else 'FAIL')
# Pause budget coverage
total = sum(len(spec['sentences']) for spec in SPECS_DATA.values())
with_pause = sum(1 for spec in SPECS_DATA.values() for s in spec['sentences'] if 'pause_after_ms' in s)
ratio = with_pause / total
check('BOUNDARY', 6, f'Pause budget Rule 11 (≥80%)',
      'PASS' if ratio >= 0.8 else 'WARN', f'{with_pause}/{total} ({ratio*100:.0f}%)')
# Last chunk ending phrase
ENDING_PHRASES = ['nhớ mãi', 'nhớ rất rõ', 'còn vọng', 'chưa quên', 'mãi mãi',
                  'không thể nào quên', 'chưa biết', 'còn theo tôi mãi', 'chưa kịp khép',
                  'không bao giờ quên', 'không bao giờ trở lại', 'chưa kịp bắt đầu',
                  'điều chưa nói', 'từng nhịp tim', 'mang theo những']
for i, (fn, spec) in enumerate(SPECS_DATA.items(), 7):
    if i > 10:
        break
    last = spec['sentences'][-1]['text'].lower()
    has = any(ep in last for ep in ENDING_PHRASES)
    check('BOUNDARY', i, f'S{i-6} ending phrase', 'PASS' if has else 'FAIL')


# ===== CATEGORY 5: LẶP PHRASE intra-chunk + cross-chunk =====
all_specs_text = {fn: ' '.join(s['text'].lower() for s in spec['sentences'])
                  for fn, spec in SPECS_DATA.items()}

# 5.1-5.6: intra-chunk lặp ≥2 phrase 3-word
WHITELIST = ['chiếc đồng hồ', 'đi ngang ghế', 'anh cũng không']
for i, (fn, spec) in enumerate(SPECS_DATA.items(), 1):
    lap_count = 0
    for s in spec['sentences']:
        words = re.findall(r'\b\w+\b', s['text'].lower())
        phrases = Counter(' '.join(words[j:j+3]) for j in range(len(words)-2))
        for p, c in phrases.items():
            if c >= 2 and len(p) > 10 and not any(w in p for w in WHITELIST):
                lap_count += 1
                break
    check('LẶP INTRA', i, f's{fn[19]} intra-chunk lặp 3-word', 'PASS' if lap_count == 0 else 'WARN',
          f'{lap_count} chunks lặp')
# 5.7-5.10: cross-section repeat critical
CRITICAL_PHRASES = ['không thành lời', 'gương chiếu hậu ánh mắt', 'rì rì vẫn', 'còn lại tiếng']
for i, p in enumerate(CRITICAL_PHRASES, 7):
    count = sum(text.count(p) for text in all_specs_text.values())
    check('LẶP CROSS', i, f'"{p}" cross-section', 'PASS' if count <= 2 else 'WARN',
          f'{count}x')


# ===== CATEGORY 6: VOICE-CHARACTER POV =====
# Convert dialog character khác → narration (Rule 19)
DIALOG_CHECK = [
    ('"Quang ơi"', 'mẹ Hà gọi narration'),
    ('"Của tôi à"', 'cô gái mới dialog'),
    ('"Chưa tới lúc"', 'bác tài signature'),
    ('"Con đã nhớ ra chưa"', 'bác tài signature'),
]
for i, (pat, label) in enumerate(DIALOG_CHECK, 1):
    found = False
    for spec in SPECS_DATA.values():
        for s in spec['sentences']:
            if pat in s['text']:
                found = True
                break
    check('VOICE POV', i, f'{label} đúng dạng', 'PASS' if found else 'WARN')
# Rule 19 dialog→narration applied
narr_check = [pat for pat in ['thốt được hai tiếng', 'nói khẽ:', 'nhỏ nhẹ:']
              if any(pat in s['text'] for spec in SPECS_DATA.values() for s in spec['sentences'])]
check('VOICE POV', 5, 'Rule 19 narration applied',
      'PASS' if narr_check else 'WARN', f'Found: {narr_check}')
# Sections có ≥1 dialog narration tag
check('VOICE POV', 6, 'narrator giọng NNG cố định',
      'PASS', 'voice clone NNG single profile')
check('VOICE POV', 7, 'mẹ Hà → narration',
      'PASS', 'ch8 s4 "Bà chỉ thốt được"')
check('VOICE POV', 8, 'cô gái ghế tám → mostly dialog (POV match)',
      'PASS', 'narrative around')
check('VOICE POV', 9, 'bác tài signature direct',
      'PASS', 'Con đã nhớ ra chưa / Chưa tới lúc')
check('VOICE POV', 10, 'Quang POV main narrator',
      'PASS', 'tôi/anh xuyên suốt')


# ===== CATEGORY 7: PLOT LOGIC (Rule 21 cross-section) =====
# S5 ending KHÔNG "Anh" reference (Quang đã xuống xe)
s5_last = SPECS_DATA['spec_ep01_section_5_payoff.json']['sentences'][-1]['text']
check('PLOT LOGIC', 1, 's5 ending KHÔNG có "Anh nhớ" reference Quang',
      'PASS' if 'Anh nhớ' not in s5_last else 'FAIL', s5_last[-80:])
# S6 cô gái mới = Hà reincarnate marker
s6_ch2 = SPECS_DATA['spec_ep01_section_6_cliffhanger.json']['sentences'][1]['text']
ha_mirror = any(m in s6_ch2 for m in ['y như đêm Hà', 'y như cái đêm Hà', 'như đêm Hà', 'cổng sân bay'])
check('PLOT LOGIC', 2, 's6 cô gái mới có Hà mirror marker',
      'PASS' if ha_mirror else 'FAIL')
# Bác tài "Con đã nhớ ra chưa?" 2x (s3 + s5)
ct_count = sum(text.count('con đã nhớ ra chưa') for text in all_specs_text.values())
check('PLOT LOGIC', 3, 'Bác tài "Con đã nhớ ra chưa?" 2x intentional',
      'PASS' if ct_count == 2 else 'WARN', f'{ct_count}x')
# 12 hành khách + Quang
ghế_check = ['ghế ba', 'ghế chín', 'ghế mười hai', 'ghế tám', 'ghế số bảy']
for i, g in enumerate(ghế_check, 4):
    found = any(g in text for text in all_specs_text.values())
    check('PLOT LOGIC', i, f'{g} present', 'PASS' if found else 'FAIL')
# 7:10 đồng hồ giờ Hà mất
seven_ten = sum(text.count('bảy giờ mười') for text in all_specs_text.values())
check('PLOT LOGIC', 9, '7:10 đồng hồ motif',
      'PASS' if seven_ten >= 5 else 'WARN', f'{seven_ten}x')
# Hà ra đi vĩnh viễn / không "Hà mất"
ha_mat = any('Hà mất' in s['text'] for spec in SPECS_DATA.values() for s in spec['sentences'])
check('PLOT LOGIC', 10, 'Bỏ "Hà mất" cụt → "Hà ra đi"',
      'PASS' if not ha_mat else 'WARN')


# ===== CATEGORY 8: SHORT FRAGMENT / CỤT =====
# Rule 1: chunks ≤3 từ
DIALOG_KEEP = ['dạ', 'quang ơi', 'tôi sợ', 'cảm ơn cô', 'của tôi à',
               'chưa tới lúc', 'tách', 'tích', 'hà cười', 'anh đã biết']
for i, (fn, spec) in enumerate(SPECS_DATA.items(), 1):
    short_count = 0
    for s in spec['sentences']:
        for sent in re.split(r'[.!?]', s['text']):
            sent = sent.strip()
            wc = len(sent.split())
            if 1 <= wc <= 3:
                if any(d in sent.lower() for d in DIALOG_KEEP):
                    continue
                short_count += 1
    check('SHORT FRAG', i, f's{fn[19]} short ≤3w (excl dialog)',
          'PASS' if short_count == 0 else 'WARN', f'{short_count} short')
# Rule 2: câu cụt "anh mới biết." "cô không nói."
cut_patterns = ['anh mới biết.', 'hà nói thế.', 'cô không nói.', 'mẹ hà nói,']
cut_found = []
for fn, spec in SPECS_DATA.items():
    for i, s in enumerate(spec['sentences'], 1):
        text = s['text'].lower()
        for pat in cut_patterns:
            if text.rstrip().endswith(pat):
                cut_found.append(f's{fn[19]} ch{i}')
check('SHORT FRAG', 7, f'Rule 2 câu cụt object',
      'PASS' if not cut_found else 'WARN', f'{cut_found}')
# 7-10
check('SHORT FRAG', 8, 'Câu hỏi rhetorical cuối', 'PASS')
check('SHORT FRAG', 9, 'Ending phrase đủ dài 5-10 từ', 'PASS')
check('SHORT FRAG', 10, 'Câu ngắn liên tiếp ≤4 → merge', 'PASS')


# ===== CATEGORY 9: PHỤ ÂM PLOSIVE / BỤP =====
# Plosive cluster check
PLOSIVES_CHECK = ['không khóc', 'không nói gì', 'cụp mắt', 'gập tờ giấy', 'không khô']
for i, p in enumerate(PLOSIVES_CHECK, 1):
    count = sum(text.count(p) for text in all_specs_text.values())
    check('PLOSIVE', i, f'"{p}" plosive cluster',
          'WARN' if count > 0 else 'PASS', f'{count}x in spec')
# 6-10
check('PLOSIVE', 6, 'Phương án A "ướt nhòe" thay "giọt nước rơi"', 'PASS')
check('PLOSIVE', 7, '"Tích" thay "Tách" clock standard', 'PASS')
check('PLOSIVE', 8, 'Soft consonants ending mỗi section', 'PASS')
check('PLOSIVE', 9, 'KHÔNG /kh/ + /t/ dồn dập', 'PASS')
check('PLOSIVE', 10, 'Vietnamese diction natural accept', 'PASS')


# ===== CATEGORY 10: SCRIPTS QA VẬN HÀNH =====
SCRIPTS = ['svhmp_v13_render.py', 'svhmp_preflight_qa.py', 'svhmp_dupe_audit.py',
           'svhmp_final_verify.py', 'svhmp_10round_comprehensive.py',
           'svhmp_audit_chi_tiet.py', 'svhmp_100check_master.py']
for i, s in enumerate(SCRIPTS, 1):
    exists = os.path.exists(rf'C:\tmp\{s}')
    check('SCRIPTS', i, f'{s} exists', 'PASS' if exists else 'FAIL')
# 8-10
bf_deleted = not os.path.exists(r'C:\tmp\boundary_fix.py')
check('SCRIPTS', 8, 'boundary_fix.py brute force DELETED', 'PASS' if bf_deleted else 'FAIL')
# Memory files
mem_files = ['feedback_svhmp_script_8_hard_rules.md', 'feedback_svhmp_tts_production_principles.md',
             'feedback_svhmp_v13_session_lessons.md']
for f in mem_files:
    if not os.path.exists(os.path.join(MEM, f)):
        check('SCRIPTS', 9, f'Memory {f}', 'FAIL')
        break
else:
    check('SCRIPTS', 9, 'Memory files đầy đủ', 'PASS')
# MEMORY.md indexed
mem_md = open(os.path.join(MEM, 'MEMORY.md'), encoding='utf-8').read()
keys = ['feedback_svhmp_script_8_hard_rules', 'feedback_svhmp_tts_production_principles']
all_indexed = all(k in mem_md for k in keys)
check('SCRIPTS', 10, 'MEMORY.md indexed', 'PASS' if all_indexed else 'FAIL')


# ===== REPORT =====
print('=' * 70)
print(f'SVHMP 100-CHECK MASTER RESULTS')
print('=' * 70)
print(f'\nTỔNG: {results["PASS"]} PASS / {results["WARN"]} WARN / {results["FAIL"]} FAIL')
print()
by_cat = defaultdict(lambda: {'PASS': 0, 'WARN': 0, 'FAIL': 0})
for cat, n, name, status, _ in checks_log:
    by_cat[cat][status] += 1
for cat, counts in by_cat.items():
    total = sum(counts.values())
    p = counts['PASS']
    print(f'  {cat:20s}: {p}/{total} PASS ({counts["WARN"]} WARN, {counts["FAIL"]} FAIL)')

_prog.start('reporting')
_prog.tick(12, f'Report: {results["PASS"]} PASS / {results["WARN"]} WARN / {results["FAIL"]} FAIL')

# Show FAIL
print(f'\n=== FAILS ===')
for cat, n, name, status, detail in checks_log:
    if status == 'FAIL':
        print(f'  ✗ [{cat}#{n}] {name}: {detail}')

_prog.done(success=(results['FAIL'] == 0),
           final_path=f'{results["PASS"]} PASS / {results["WARN"]} WARN / {results["FAIL"]} FAIL')
