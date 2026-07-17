"""Pre-render audit — MANDATORY trước render section.

Check R154 mandatory: (renamed from R81-R85 addon range, xem prompts/generator_vnsl_addon.md v1.3)
1. Text validator (R3/R67/R72-R78) PASS 0
2. High-freq word audit
3. Cross-chunk 3-gram repeat (R74.2)
4. Open-vowel tail check (R76)
5. Em-dash check (R70 — bible/00 R70_em_dash_prosody_explicit_pause_hardlock; "R75" renamed away to proper_noun_anaphora, no longer em-dash)
6. Pause > 1500ms check
7. Tempo factor consistency (R71/R152)
8. Emo_vector consistency (R152)

Exit 1 if any HIGH issue. Block render.
"""
import json, re, sys, os
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
LEX_PATH = Path(__file__).parent.parent / 'data' / 'vnsl_lexicon.json'

EXCL = {'và','là','của','có','không','một','những','cái','này','đó','ấy','cô','anh','em','tôi','mình','nó','họ','người','chiếc','cho','với','như','mà','thì','để','từ','trong','ra','vào','lên','xuống','đi','đến','về','qua','ở','cũng','lại','còn','đã','sẽ','đang','rồi','mới','chưa','phải','rất','quá','hơn','thật','chỉ','nhưng','vì','nếu','khi','lúc','sau','trước','giữa','bên','trên','dưới','hà','quang','đồng','hồ','xe','ghế','bác','tài'}

STOP_GRAMS = {'của hôm ấy','trong lòng anh','trong tay anh','ở phía sau','một chiếc đồng','chiếc đồng hồ','bảy giờ mười','ghế số bảy','cổng b sân','b sân bay','cô gái ghế','quang nhìn xuống','quang quay lại','quang thở ra','một hơi dài','như có ai','bên cạnh anh','phía trước anh','bác tài liếc','liếc gương chiếu','gương chiếu hậu','ở ghế số','con đã nhớ','trong gương chiếu','chiếu hậu ánh'}

OPEN_VOWEL_TAIL = {'nữa','mãi','ngày','tay','dài','ai','mai','đời','ơi','trời','vời','khơi','đâu','sau','lâu','đau','xa','ra','qua','thưa','mưa','vừa','rồi','chơi','trôi','tựa','lúa','đầy','cô','cảm','khảm','lìm','tâm','nay'}

def grams(s, n=3):
    ws = re.findall(r'\w+', s.lower())
    return [' '.join(ws[i:i+n]) for i in range(len(ws)-n+1)]

def audit(spec_path):
    d = json.load(open(spec_path, encoding='utf-8'))
    chunks = d.get('sentences', d.get('chunks', []))
    issues = {'HIGH': [], 'MED': [], 'WARN': []}

    # 1. Text validator (run external)
    # (handled separately by vnsl_validator.py)

    # 2. High-freq words
    text = ' '.join(c.get('text','') if isinstance(c,dict) else c for c in chunks).lower()
    words = re.findall(r'\b\w+\b', text)
    cnt = Counter(words)
    high = [(w,n) for w,n in cnt.most_common() if w not in EXCL and len(w)>=2 and n>=5]
    for w,n in high[:5]:
        issues['MED'].append(f'R3 high-freq "{w}" x{n}')

    # 3. Cross-chunk 3-gram
    for i in range(len(chunks)-1):
        t1 = chunks[i].get('text','') if isinstance(chunks[i],dict) else chunks[i]
        t2 = chunks[i+1].get('text','') if isinstance(chunks[i+1],dict) else chunks[i+1]
        common = (set(grams(t1)) & set(grams(t2))) - STOP_GRAMS
        for g in common:
            if len(g) >= 8:
                issues['HIGH'].append(f'R74.2 ch{i}-{i+1} repeat "{g}"')

    # 4. Open-vowel tail
    for i,c in enumerate(chunks):
        t = c.get('text','') if isinstance(c,dict) else c
        sents = [s.strip() for s in re.split(r'[.!?…]', t) if s.strip()]
        if sents:
            last = sents[-1].strip().strip('"').strip(',')
            ws = last.split()
            if ws:
                lw = ws[-1].lower().strip('.,!?…"\'')
                if lw in OPEN_VOWEL_TAIL:
                    issues['HIGH'].append(f'R76 ch{i} tail "{lw}"')

    # 5. Em-dash
    for i,c in enumerate(chunks):
        t = c.get('text','') if isinstance(c,dict) else c
        if '—' in t:
            issues['MED'].append(f'R70 ch{i} em-dash')

    # 6. Pause > 1500ms
    for i,c in enumerate(chunks):
        if isinstance(c, dict):
            p = c.get('pause_after_ms', 600)
            if p > 1500:
                issues['HIGH'].append(f'R66 ch{i} pause={p}ms > 1500')

    # 7. Tempo factor consistency
    tempos = [c.get('tempo_factor', 1.0) for c in chunks if isinstance(c, dict)]
    for i in range(1, len(tempos)):
        dt = abs(tempos[i] - tempos[i-1])
        if dt > 0.15:
            issues['MED'].append(f'R152 ch{i-1}-{i} tempo jump {tempos[i-1]}→{tempos[i]}')

    # 8. Emo_vector consistency
    emos = [c.get('emo_vector', None) for c in chunks if isinstance(c, dict)]
    for i in range(1, len(emos)):
        if emos[i] is None or emos[i-1] is None: continue
        for axis in range(min(len(emos[i]), len(emos[i-1]))):
            d_axis = abs(emos[i][axis] - emos[i-1][axis])
            if d_axis > 0.15:
                issues['HIGH'].append(f'R152 ch{i-1}-{i} emo axis{axis} delta={d_axis:.2f} >0.15')
                break

    return issues

def main():
    if len(sys.argv) < 2:
        print("Usage: python pre_render_audit.py <spec.json>")
        sys.exit(1)
    spec_path = sys.argv[1]
    issues = audit(spec_path)
    print(f"\n=== Pre-render audit {spec_path} ===")
    for sev in ['HIGH','MED','WARN']:
        if issues[sev]:
            print(f"\n[{sev}] ({len(issues[sev])})")
            for i in issues[sev][:20]:
                print(f"  - {i}")
    total_high = len(issues['HIGH'])

    # === Integrate post_rotate_verify (R88) ===
    print(f"\n=== R88 Post-rotate verify (double-prep + Hoàng Phê + tail) ===")
    import subprocess

    CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
    prv_path = Path(__file__).parent / 'post_rotate_verify.py'
    result = subprocess.run([sys.executable, str(prv_path), spec_path], capture_output=True, text=True, encoding='utf-8', errors='replace', env={**os.environ, 'PYTHONIOENCODING':'utf-8'})
    print(result.stdout)
    if result.returncode != 0:
        print("R88 BLOCK render")
        sys.exit(1)

    print(f"\n{'='*50}\nTOTAL HIGH: {total_high}")
    if total_high > 0:
        print("BLOCK render. Fix HIGH issues first.")
        sys.exit(1)
    print("PASS — safe to render")

if __name__ == '__main__':
    main()
