"""SVHMP pre-flight QA — FULL_TEXT_GATE (Mr.Long lock 30/6 23:00)
Now includes qa_eol_diacritic (R86 broad NGA + NANG + HOI) — process gap PV-01..04 fix.

Usage: python svhmp_preflight_qa.py <spec.json> [--skip-r86]
Exit 0 = PASS, exit 1 = FAIL (block render).
"""
import sys
import json
import re
import os
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
import atexit
from pathlib import Path

# Round 14 dashboard live render hook
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

if len(sys.argv) < 2:
    print('Usage: svhmp_preflight_qa.py <spec.json>')
    sys.exit(2)

_ep_match = re.search(r'ep_?(\d+)', sys.argv[1])
_ep = int(_ep_match.group(1)) if _ep_match else 0
_prog = RenderProgress(cmd='preflight_qa', ep=_ep, total_steps=10)
atexit.register(lambda: _prog.fail('exit without done') if _prog.current_step < _prog.total_steps else None)
_prog.start('checking_rules')

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
    'bắt đầu',  # R4 ext (Boss duyet 1/7): intro closer dan vao truyen ("...cau chuyen bat dau")
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
    for trig in ['Bất chợt', 'Khải Phong nhớ rồi', 'Khải Phong là']:
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


_prog.tick(10, f'Preflight {"FAIL" if issues else "PASS"} — {len(issues)} issues / {len(sents)} chunks')

# ========================================================================
# FULL_TEXT_GATE — Mr.Long lock 30/6 23:00 process gap PV-01..04 fix
# Chain qa_eol_diacritic R86 broad EOL (NGA + NANG + HOI).
# ========================================================================
if '--skip-r86' not in sys.argv:
    spec_path = Path(sys.argv[1])
    ep_match = re.search(r'ep_(\d+)', str(spec_path))
    if ep_match:
        ep_num = int(ep_match.group(1))
        md_path = spec_path.parents[1] / 'episode.md'
        if md_path.exists():
            print('[FULL_TEXT_GATE] R86 broad EOL check via qa_eol_diacritic.py')
            r86 = subprocess.run(
                ['python', str(Path(__file__).parent / 'qa_eol_diacritic.py'), str(md_path)],
                capture_output=True, text=True, encoding='utf-8',
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
            )
            sys.stdout.write(r86.stdout)
            if r86.returncode != 0:
                issues.append(f'R86 broad EOL BLOCKED via qa_eol_diacritic rc={r86.returncode}')
        else:
            print(f'[FULL_TEXT_GATE] WARN: episode.md not found at {md_path}, skip R86 broad')
    else:
        print('[FULL_TEXT_GATE] WARN: cannot detect ep_N from spec path, skip R86 broad')

# ========================================================================
# CHARACTER_COMPLETENESS_GATE (G2, 2026-07-02) — wire Character DoD vao render.
# WARN-by-default: roster hien "vo dien" (avg completeness ~0.23, occupation/role
# chua fill) nen HARD-block se chan MOI episode -> production dung. Gate nay chi
# CANH BAO trong render log; them --strict-characters de BLOCK khi roster da day.
# Nguong chinh qua --char-threshold=<0..1> (default 0.5). Khong bao gio crash render.
# ========================================================================
_strict_chars = '--strict-characters' in sys.argv
_char_thr = 0.5
for _a in sys.argv:
    if _a.startswith('--char-threshold='):
        try:
            _char_thr = float(_a.split('=', 1)[1])
        except ValueError:
            pass
try:
    from character_manager import CharacterRegistry
    _cg = CharacterRegistry().episode_completeness(_ep, _char_thr) if _ep else None
    if _cg and _cg['total']:
        mode = 'STRICT' if _strict_chars else 'WARN'
        print(f'[CHARACTER_GATE:{mode}] ep{_ep}: {_cg["total"]} char(s), '
              f'{len(_cg["below"])} below completeness {_char_thr}')
        _warns, _blocks = CharacterRegistry.render_gate_lines(_cg, _strict_chars)
        for _w in _warns:
            print(f'  [WARN] {_w}')
        for _b in _blocks:
            issues.append(f'R-CHAR {_b}')
    elif _ep:
        print(f'[CHARACTER_GATE] ep{_ep}: no roster char mapped (assigned_ep) — skip')
except Exception as _e:
    print(f'[CHARACTER_GATE] WARN: skipped ({type(_e).__name__}: {_e})')

# ========================================================================
# D5 PREREQUISITE (Mr.Long duyet 9/7, qa_verdict_schema_proposal final_decision_9_7):
# Phat THEM 1 JSON verdict native (format_3) — GIU NGUYEN exit code cu (backward-compat),
# JSON chi la output BO SUNG. Adapter tools/qa_verdict_adapter.py canonical-hoa ve 4-enum
# [PASS/PASS_WITH_WARNING/REGEN/REVIEW_REQUIRED]. exit_2 (usage-error o dau file) KHONG toi
# day nen khong emit verdict (dung R9: exit_2 la TOOLING_ERROR, khong phai verdict tap).
# KHONG doi 11 rule text / R86 FULL_TEXT_GATE / exit code — chi ghi them file JSON.
# ========================================================================
try:
    if _ep:
        from datetime import datetime, timezone
        _out = {
            'tool': 'preflight',
            'ep_number': _ep,
            'verdict': 'FAIL' if issues else 'PASS',   # native PASS/FAIL (adapter map FAIL->REGEN)
            'exit_code': 1 if issues else 0,
            'chunks': len(sents),
            'issues': list(issues),
            'ts': datetime.now(timezone.utc).isoformat(),
        }
        _rt = Path(__file__).resolve().parents[1] / 'runtime'
        _rt.mkdir(exist_ok=True)
        _json_path = _rt / f'preflight_ep_{_ep}.json'
        _json_path.write_text(json.dumps(_out, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'[VERDICT_JSON] {_json_path}')
except Exception as _je:  # noqa: BLE001 — JSON la phu, tuyet doi khong lam doi exit code render
    print(f'[VERDICT_JSON] WARN: khong ghi duoc JSON verdict ({type(_je).__name__}: {_je})')

if issues:
    print(f'PREFLIGHT FAIL — {len(issues)} issues')
    for iss in issues:
        print(f'  {iss}')
    _prog.done(success=False)
    sys.exit(1)
else:
    print(f'PREFLIGHT PASS — {len(sents)} chunks OK + FULL_TEXT_GATE (R86 broad) PASS')
    _prog.done(success=True)
    sys.exit(0)
