"""SVHMP — G2 B2: ROSTER BACKFILL MINER (TASK_G2_CHARACTER, Mr.Long duyệt 3/7).

NGUYÊN LÝ "ĐÀO DỮ LIỆU THẬT, KHÔNG BỊA": máy trích xuất từ episode ĐÃ CÓ ->
ghi ĐỀ XUẤT status=draft vào runtime/roster_backfill_draft.yaml — KHÔNG tự ghi
roster chính. Người (executor/Mr.Long) duyệt rồi mới merge (B3).

Trích per-character:
- xuất hiện tập nào (header passenger_main + whole-word match char_name trong text)
- speech evidence (dòng thoại "..." trong tập của nhân vật — speaker CHƯA gán, người duyệt)
- knowledge candidates (dòng chứa marker bí mật/giấu/chưa từng kể)
- continuity_risk flags kèm evidence (ep:line)

Bonus bắt buộc: reports/G2_CONTINUITY_FINDINGS.md — mâu thuẫn sẵn có:
- F1 roster drift: tập dùng passenger free-form KHÔNG có PAS_ id
- F2 PAS_ id lệch assigned_ep roster
- F3 char_name roster xuất hiện ngoài tập được gán (one-shot bible/03)
- F4 tên free-form vi phạm bible/23 (forbidden 15 / trùng âm tiết / 1 âm tiết)

Exit 0 = chạy trọn (findings nhiều hay ít KHÔNG fail — miner là máy đào, gate là
roster_validator). Exit 1 = lỗi I/O/parse nghiêm trọng.
"""
import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml

SVHMP = Path(__file__).parent.parent
ROSTER = SVHMP / 'runtime' / 'passenger_roster_100.yaml'
NAMES_DB = SVHMP / 'data' / 'vietnamese_names_extended.yaml'
OUT_DRAFT = SVHMP / 'runtime' / 'roster_backfill_draft.yaml'
OUT_FINDINGS = SVHMP / 'reports' / 'G2_CONTINUITY_FINDINGS.md'

# Recurring hợp lệ xuyên tập (bible/03: CHỈ CHAR_DRIVER + CHAR_NAM; rename toàn
# dự án 148a80c: POV='Khải Phong', vai ký ức='Hạ Vy'; 'bác tài'=CHAR_DRIVER).
RECURRING_NAMES = {'Khải Phong', 'Hạ Vy'}
KNOWLEDGE_MARKERS = ['bí mật', 'không ai biết', 'giấu', 'chưa từng kể', 'chưa kể ai', 'giấu kín']

RE_HEADER_KV = re.compile(r'^(\w+)\s*:\s*(.+)$')
RE_PAS = re.compile(r'PAS_\d{4}')
# free-form: "nu 36 Vy An Long Biên (chia tay ...)" | "nam 30 anh Nguyễn (...)"
RE_FREEFORM = re.compile(r'(nu|nam)[ _]?(\d+)?\s+(.+?)\s*(?:\((.*)\))?\s*$')
RE_QUOTE = re.compile(r'^"(.+)"\s*$')


def load_forbidden_words():
    db = yaml.safe_load(NAMES_DB.read_text(encoding='utf-8'))
    return {item['syl'] for item in db.get('forbidden_words', [])}


def episode_files(root=None):
    root = root or (SVHMP / 'output')
    eps = []
    for d in sorted(root.glob('ep_*')):
        # chỉ ep_NN trực tiếp — archive_draft_* KHÔNG match glob này
        m = re.fullmatch(r'ep_(\d+)', d.name)
        f = d / 'episode.md'
        if m and f.exists():
            eps.append((int(m.group(1)), f))
    return eps


def parse_header(lines):
    """Đọc block ``` đầu tiên (metadata) -> dict key->value."""
    meta, inside = {}, False
    for ln in lines:
        s = ln.strip()
        if s.startswith('```'):
            if inside:
                break
            inside = True
            continue
        if inside:
            m = RE_HEADER_KV.match(s)
            if m:
                meta[m.group(1)] = m.group(2).strip()
    return meta


def parse_passenger_main(raw):
    """PAS_ id hoặc free-form. Trả (pas_id|None, info dict)."""
    if not raw:
        return None, {}
    pas = RE_PAS.search(raw)
    if pas:
        return pas.group(0), {'raw': raw}
    m = RE_FREEFORM.match(raw)
    info = {'raw': raw, 'parse_confidence': 'low'}
    if m:
        info['gender_guess'] = m.group(1)
        info['age_guess'] = m.group(2)
        rest = m.group(3).strip()
        words = rest.split()
        # tên VN 2 âm tiết (rule_01) -> 2 từ đầu = name_guess, còn lại = quê/ghi chú
        guess = ' '.join(words[:2]) if len(words) >= 2 else rest
        # header dị dạng (vd 'nu_45 → nam 26 ...') sinh guess rác — máy KHÔNG đoán bừa
        if re.fullmatch(r'[A-Za-zÀ-ỹ]+(?: [A-Za-zÀ-ỹ]+)*', guess):
            info['name_guess'] = guess
        else:
            info['name_guess'] = None
            info['needs_human'] = 'header dị dạng — không trích được tên'
        info['hometown_guess'] = ' '.join(words[2:]) if len(words) > 2 else ''
        info['context'] = m.group(4) or ''
    return None, info


def scan_episode(ep_no, path, roster_names):
    """Trả dict: header, quotes, knowledge_lines, name_hits {char_name: [line_no]}."""
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    header = parse_header(lines)
    quotes, knowledge_lines = [], []
    for i, ln in enumerate(lines, 1):
        s = ln.strip()
        q = RE_QUOTE.match(s)
        if q:
            quotes.append({'ep': ep_no, 'line': i, 'text': q.group(1)})
        low = s.lower()
        if any(k in low for k in KNOWLEDGE_MARKERS):
            knowledge_lines.append({'ep': ep_no, 'line': i, 'text': s[:200]})
    name_hits = {}
    for name in roster_names:
        hits = [i for i, ln in enumerate(lines, 1)
                if re.search(r'(?<![\wÀ-ỹ])' + re.escape(name) + r'(?![\wÀ-ỹ])', ln)]
        if hits:
            name_hits[name] = hits
    return {'header': header, 'quotes': quotes,
            'knowledge_lines': knowledge_lines, 'name_hits': name_hits}


def check_name_bible23(name, used_words, forbidden):
    """Vi phạm bible/23 của 1 tên: trả list str."""
    v = []
    words = name.split()
    if len(words) < 2:
        v.append(f"rule_01: '{name}' chỉ 1 âm tiết")
    for w in words:
        if w in forbidden:
            v.append(f"forbidden: '{name}' chứa từ cấm '{w}' (Mr.Long 27/6)")
        if w in used_words and name != used_words[w]:
            v.append(f"rule_02: '{name}' trùng âm tiết '{w}' với '{used_words[w]}'")
    return v


def mine(output_root=None, roster_path=None):
    roster = yaml.safe_load((roster_path or ROSTER).read_text(encoding='utf-8'))
    passengers = {p['id']: p for p in roster['passengers']}
    by_name = {p['char_name']: p for p in roster['passengers']}
    forbidden = load_forbidden_words()

    eps = episode_files(output_root)
    scans = {ep: scan_episode(ep, f, set(by_name)) for ep, f in eps}

    characters = {}   # PAS_id -> draft entry
    unmatched = []    # free-form không PAS_ id
    findings = {'F1_roster_drift': [], 'F2_assigned_ep_mismatch': [],
                'F3_cross_episode_appearance': [], 'F4_naming_violations': []}

    # từ điển âm tiết đã dùng (roster = nguồn hợp lệ gốc)
    used_words = {}
    for nm in by_name:
        for w in nm.split():
            used_words.setdefault(w, nm)

    for ep, scan in sorted(scans.items()):
        pas_id, info = parse_passenger_main(scan['header'].get('passenger_main', ''))
        if pas_id:
            p = passengers.get(pas_id)
            if p is None:
                findings['F2_assigned_ep_mismatch'].append(
                    f"ep_{ep:02d}: {pas_id} KHÔNG có trong roster")
                continue
            entry = characters.setdefault(pas_id, {
                'char_name': p['char_name'], 'assigned_ep': p.get('assigned_ep'),
                'appearances': [], 'speech_evidence': [], 'knowledge_candidates': [],
                'continuity_risk': {'flags': [], 'level': 'low', 'evidence': []},
                'status': 'draft'})
            entry['appearances'].append({'ep': ep, 'source': 'header_passenger_main'})
            entry['speech_evidence'] += [dict(q, speaker='UNATTRIBUTED_can_nguoi_duyet')
                                         for q in scan['quotes']]
            entry['knowledge_candidates'] += scan['knowledge_lines']
            if p.get('assigned_ep') != ep:
                findings['F2_assigned_ep_mismatch'].append(
                    f"ep_{ep:02d}: {pas_id} ({p['char_name']}) roster gán ep {p.get('assigned_ep')}")
        else:
            raw = scan['header'].get('passenger_main', '')
            if raw:
                findings['F1_roster_drift'].append(f"ep_{ep:02d}: passenger_main='{raw[:90]}' (KHÔNG PAS_ id)")
                ent = {'ep': ep, **info,
                       'roster_link': None,
                       'continuity_risk': {'flags': ['roster_drift_no_pas_id'], 'level': 'high',
                                           'evidence': [f'ep_{ep:02d}:header']},
                       'speech_evidence': [dict(q, speaker='UNATTRIBUTED_can_nguoi_duyet')
                                           for q in scan['quotes']],
                       'knowledge_candidates': scan['knowledge_lines'],
                       'status': 'draft'}
                unmatched.append(ent)
                ng = info.get('name_guess', '')
                if ng:
                    for viol in check_name_bible23(ng, used_words, forbidden):
                        findings['F4_naming_violations'].append(
                            f"ep_{ep:02d}: {viol} [name_guess parse_confidence=low — người duyệt]")
                    for w in ng.split():
                        used_words.setdefault(w, ng)
            else:
                findings['F1_roster_drift'].append(f"ep_{ep:02d}: header KHÔNG có passenger_main")

    # F3: char_name roster xuất hiện ngoài tập gán (one-shot bible/03)
    for ep, scan in sorted(scans.items()):
        for name, hit_lines in scan['name_hits'].items():
            if name in RECURRING_NAMES:
                continue
            p = by_name[name]
            if p.get('assigned_ep') != ep:
                findings['F3_cross_episode_appearance'].append(
                    f"ep_{ep:02d}:{hit_lines[:3]}: '{name}' ({p['id']}, gán ep {p.get('assigned_ep')})")
                entry = characters.setdefault(p['id'], {
                    'char_name': name, 'assigned_ep': p.get('assigned_ep'),
                    'appearances': [], 'speech_evidence': [], 'knowledge_candidates': [],
                    'continuity_risk': {'flags': [], 'level': 'low', 'evidence': []},
                    'status': 'draft'})
                cr = entry['continuity_risk']
                if 'recurring_cross_ep' not in cr['flags']:
                    cr['flags'].append('recurring_cross_ep')
                    cr['level'] = 'high'
                cr['evidence'].append(f"ep_{ep:02d}:{hit_lines[0]}")
                entry['appearances'].append({'ep': ep, 'source': 'text_mention',
                                             'lines': hit_lines[:5]})

    # knowledge candidate -> flag biet_bi_mat (đề xuất, người duyệt)
    for cid, entry in characters.items():
        if entry['knowledge_candidates'] and 'biet_bi_mat' not in entry['continuity_risk']['flags']:
            entry['continuity_risk']['flags'].append('biet_bi_mat')
            entry['continuity_risk']['evidence'] += [
                f"ep_{k['ep']:02d}:{k['line']}" for k in entry['knowledge_candidates'][:3]]

    return {'episodes_scanned': [e for e, _ in eps], 'characters': characters,
            'unmatched_episode_characters': unmatched, 'findings': findings}


def write_outputs(result, out_draft=OUT_DRAFT, out_findings=OUT_FINDINGS):
    eps = result['episodes_scanned']
    draft = {
        'meta': {
            'tool': 'tools/roster_backfill_miner.py',
            'generated': str(date.today()),
            'status': 'draft',
            'principle': 'Máy trích xuất — người DUYỆT. KHÔNG tự merge vào passenger_roster_100.yaml.',
            'episodes_scanned': len(eps),
            'episodes_range': f"ep_{min(eps):02d}..ep_{max(eps):02d}" if eps else 'none',
        },
        'characters': result['characters'],
        'unmatched_episode_characters': result['unmatched_episode_characters'],
    }
    out_draft.write_text(yaml.safe_dump(draft, allow_unicode=True, sort_keys=False, width=120),
                         encoding='utf-8')

    f = result['findings']
    lines = [
        '# G2 CONTINUITY FINDINGS — máy đào ngược episode ĐÃ CÓ (TASK_G2_CHARACTER B2)',
        '',
        f"- Sinh bởi: `tools/roster_backfill_miner.py` — {date.today()}",
        f"- Tập quét: {len(eps)} (ep_{min(eps):02d}..ep_{max(eps):02d})" if eps else '- Tập quét: 0',
        '- **LỆCH SO VỚI TASK:** task ghi "90 tập đã có" — thực tế trên disk chỉ '
        f'{len(eps)} tập có `episode.md` (ep_51..90 mới có moment_map_template). KHÔNG overclaim.',
        '- Route: **executor xử lý** (TASK G2 DoD). Mọi finding kèm evidence ep:line — không suy luận.',
        '',
    ]
    titles = {
        'F1_roster_drift': 'F1 — Roster drift: tập KHÔNG dùng PAS_ id (đứt liên kết roster↔episode)',
        'F2_assigned_ep_mismatch': 'F2 — PAS_ id lệch assigned_ep trong roster',
        'F3_cross_episode_appearance': 'F3 — char_name roster xuất hiện ngoài tập được gán (one-shot bible/03)',
        'F4_naming_violations': 'F4 — Tên free-form nghi vi phạm bible/23 (forbidden/trùng âm/1 âm tiết)',
    }
    for key, title in titles.items():
        items = f[key]
        lines.append(f"## {title} — {len(items)} finding")
        lines += [f"- {x}" for x in items] or ['- (không có)']
        lines.append('')
    out_findings.write_text('\n'.join(lines), encoding='utf-8')
    return draft


def main():
    result = mine()
    write_outputs(result)
    f = result['findings']
    n_char = len(result['characters'])
    n_un = len(result['unmatched_episode_characters'])
    print("=== ROSTER BACKFILL MINER (G2 B2) ===")
    print(f"  episodes scanned : {len(result['episodes_scanned'])}")
    print(f"  roster chars mined: {n_char}   unmatched (free-form): {n_un}")
    for k, v in f.items():
        print(f"  {k}: {len(v)}")
    print(f"  -> {OUT_DRAFT.relative_to(SVHMP)}")
    print(f"  -> {OUT_FINDINGS.relative_to(SVHMP)}")
    print("  status: DRAFT — người duyệt trước khi merge (KHÔNG tự ghi roster chính)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
