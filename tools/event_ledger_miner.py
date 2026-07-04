"""SVHMP — G4 D2: EVENT LEDGER MINER (TASK_G4_WORLD, kiểm chứng 4/7).

NGUYÊN LÝ "ĐÀO DỮ LIỆU THẬT, KHÔNG BỊA" (mirror G2 roster_backfill_miner đã thắng):
máy trích xuất từ episode ĐÃ CÓ -> ghi ĐỀ XUẤT status=draft vào
runtime/event_ledger_draft.yaml. KHÔNG tự ghi sổ cái chính (chưa tồn tại — D3 mới
đề xuất schema). Người (Mr.Long/executor) duyệt.

Trích per-episode:
- primary_event: từ header (regret_sub/signature_object/passenger_main/death info)
  — đây LÀ sự kiện lõi của tập theo cấu trúc SVHMP.
- temporal_mentions: mọi cụm "X năm trước"/"X tuổi"/"sống X năm" trong thân bài
  (dùng tools/vn_number_words.py — episode.md viết số bằng CHỮ, không phải digit).
- object_mentions: signature_object (header) + mọi OBJ_ nào khác được nhắc literal
  trong thân bài (hiếm, nhưng bible/24 meta-arc có easter-egg xuyên tập).

Bonus bắt buộc: reports/G4_EVENT_FINDINGS.md — mâu thuẫn tự phát hiện:
- F1: 2 tập cùng nhắc đến 1 NHÂN VẬT one-shot (không phải Khải Phong/Hạ Vy) qua
  tên riêng trùng — evidence cho continuity xuyên tập. GIỚI HẠN ĐÃ BIẾT (ghi rõ
  trong report): case ví dụ TASK ("Phong" ep_15 tái xuất ep_25, tuổi/mốc NHẤT
  QUÁN 21+10=31 cả 2 tập) KHÔNG lọt được vào F1 — "Phong" trùng tên tắt Khải
  Phong (nhân vật chính mọi tập) nên bị loại khỏi candidate để tránh nhiễu; đây
  là hạn chế của phương pháp tần suất âm tiết (không giải quyết coreference).
- F2: cùng 1 episode có 2 temporal_mention về "X năm trước" cho CÙNG 1 mốc suy ra
  (từ tuổi hiện tại - tuổi lúc đó) mà số năm KHÔNG khớp phép trừ tuổi (mâu thuẫn
  nội tại 1 tập — vd tự nhận 31 tuổi + "mười năm trước 21 tuổi" nhưng lại nói
  "mười lăm năm trước" ở dòng khác cho cùng sự kiện).

Exit 0 = chạy trọn (findings nhiều/ít KHÔNG fail — miner là máy đào, gate là
g4_world_check qua timeline_check). Exit 1 = lỗi I/O/parse nghiêm trọng.
"""
import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from vn_number_words import extract_years_ago, extract_ages, extract_lived_years  # noqa: E402
from roster_backfill_miner import parse_passenger_main  # noqa: E402 (tai su dung G2, khong viet lai)

SVHMP = Path(__file__).parent.parent
ROSTER = SVHMP / 'runtime' / 'passenger_roster_100.yaml'
BIBLE12 = SVHMP / 'bible' / '12_object_library.yaml'
OUT_DRAFT = SVHMP / 'runtime' / 'event_ledger_draft.yaml'
OUT_FINDINGS = SVHMP / 'reports' / 'G4_EVENT_FINDINGS.md'


def _load_object_catalog_ids(bible12_path=None):
    doc = yaml.safe_load(Path(bible12_path or BIBLE12).read_text(encoding='utf-8'))
    return set((doc.get('object_library') or {}).keys())

RE_HEADER_KV = re.compile(r'^(\w+)\s*:\s*(.+)$')
RECURRING_NAMES = {'Khải Phong', 'Hạ Vy'}
# Nhan vat recurring (bible/03) DUOC GOI TAT 1 tu xuyen 50 tap (vd "Phong" =
# Khải Phong ke chuyen, "Vy" = Hạ Vy) — day KHONG phai tin hieu continuity
# one-shot, phai loai truoc khi dem F1 (khac han component-word cua ten one-shot
# khac, vd "Phong" trong "Lộc Phong" PAS_0057 van tinh binh thuong o cho khac).
RECURRING_NAME_COMPONENTS = {w for name in RECURRING_NAMES for w in name.split()}
# Tu hang chuc/xung ho pho bien — KHONG duoc coi la nickname nhan vat du 1 minh
# no trung 1 tu trong char_name nao do (chong false-positive kieu G2 tung gap)
_COMMON_WORDS_EXCLUDE = {'Văn', 'Thị', 'Hữu', 'Đức', 'Ngọc', 'Thanh', 'Minh'}


def _load_nickname_candidates(roster_path=None):
    """Tu roster char_name (VD 'Phong Hoài Đức') -> tap tu-don co the la nickname
    ('Phong') anh xa ve (pas_id, assigned_ep). Chi lay tu KHONG nam trong danh
    sach hang-chuc/xung-ho pho bien (tranh khop nham vo nghia)."""
    roster = yaml.safe_load(Path(roster_path or ROSTER).read_text(encoding='utf-8'))
    out = {}   # word -> list[(pas_id, char_name, assigned_ep)]
    for p in roster['passengers']:
        for w in p['char_name'].split():
            if w in _COMMON_WORDS_EXCLUDE or w in RECURRING_NAME_COMPONENTS or len(w) < 2:
                continue
            out.setdefault(w, []).append((p['id'], p['char_name'], p.get('assigned_ep')))
    return out


def episode_files(root=None):
    root = root or (SVHMP / 'output')
    eps = []
    for d in sorted(root.glob('ep_*')):
        m = re.fullmatch(r'ep_(\d+)', d.name)
        f = d / 'episode.md'
        if m and f.exists():
            eps.append((int(m.group(1)), f))
    return eps


def parse_header(lines):
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


def _extract_obj_id(raw):
    """Header ghi 'OBJ_XXX (mo ta tieng Viet)' — chi lay token OBJ_ id de resolve
    duoc bible/12 (giu nguyen raw neu khong khop dinh dang, khong bia)."""
    if not raw:
        return raw
    m = re.match(r'OBJ_[A-Z_]+', raw)
    return m.group(0) if m else raw


def mine_episode(ep_no, path, nickname_candidates):
    """Tra ve dict 1 episode: primary_event, temporal_mentions, object_mentions, nickname_hits."""
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines()
    header = parse_header(lines)

    primary_event = {
        'regret_sub': header.get('regret_sub'),
        # header ghi 'OBJ_XXX (mo ta tieng Viet)' — chi lay TOKEN id, bo mo ta
        # (bug that: mine truoc day giu ca chuoi, khong resolve duoc bible/12)
        'signature_object': _extract_obj_id(header.get('signature_object')),
        'signature_setting': header.get('signature_setting'),
        'passenger_main': header.get('passenger_main'),
        'stop_location': header.get('stop_location'),
    }

    temporal_mentions = []
    object_mentions = set()
    nickname_hits = {}   # nickname -> [line_no] (chi tu roster, KHONG doan tu)
    for i, ln in enumerate(lines, 1):
        for v, matched, span in extract_years_ago(ln):
            temporal_mentions.append({'ep': ep_no, 'line': i, 'kind': 'years_ago',
                                      'value': v, 'text': matched})
        for v, matched, span in extract_ages(ln):
            temporal_mentions.append({'ep': ep_no, 'line': i, 'kind': 'age',
                                      'value': v, 'text': matched})
        for v, matched, span in extract_lived_years(ln):
            temporal_mentions.append({'ep': ep_no, 'line': i, 'kind': 'lived_years',
                                      'value': v, 'text': matched})
        for m in re.finditer(r'OBJ_[A-Z_]+', ln):
            object_mentions.add(m.group(0))
        for nick in nickname_candidates:
            if nick in RECURRING_NAMES:
                continue
            if re.search(r'(?<![\wÀ-ỹ])' + re.escape(nick) + r'(?![\wÀ-ỹ])', ln):
                nickname_hits.setdefault(nick, []).append(i)

    sig_obj = header.get('signature_object')
    if sig_obj:
        object_mentions.add(sig_obj)

    return {
        'primary_event': primary_event,
        'temporal_mentions': temporal_mentions,
        'object_mentions': sorted(object_mentions),
        'nickname_hits': nickname_hits,
    }


MAX_EXTRA_EPISODES_SIGNAL = 3   # > nguong nay = am tiet qua pho bien (nhieu tu-
# thuong/dia-danh trung 1 tu char_name — vd "Anh"/"Hà"/"Hải" xuat hien hang chuc
# tap), KHONG phai tin hieu continuity nhan vat that. Nguong thap giu dung case
# that ("Phong" ep_15->ep_25 = 1 tap thua) va loai am tiet-thuong (>10 tap thua).


def find_cross_episode_name_recurrence(scans, nickname_candidates):
    """F1: nickname (tu roster char_name, KHONG phai capitalization doan) xuat
    hien o tap KHAC voi (moi) tap assigned_ep cua CHINH chu nhan nickname do —
    proxy cho continuity xuyen tap (case that: 'Phong' ep_15 -> tai xuat ep_25).
    Loc nguong MAX_EXTRA_EPISODES_SIGNAL de bot am tiet-thuong (chong weak-verifier
    nhieu nhieu — bai hoc du an: negative/positive test phai la tin hieu that)."""
    out = {}
    for nick, owners in nickname_candidates.items():
        owner_eps = {o[2] for o in owners if o[2] is not None}
        appear_eps = {ep for ep, scan in scans.items() if nick in scan['nickname_hits']}
        extra = sorted(appear_eps - owner_eps)
        if extra and owner_eps and len(extra) <= MAX_EXTRA_EPISODES_SIGNAL:
            out[nick] = {'owner_pas_ids': [o[0] for o in owners],
                        'assigned_eps': sorted(owner_eps), 'also_appears_in': extra}
    return out


MAX_LINE_WINDOW_FOR_SAME_REFERENT = 3   # +/- so dong de coi 2 mocc thoi gian la
# CUNG 1 nguoi/su kien (case that ep_25 line 63: age+years_ago+age_now CUNG 1
# dong). Rong hon toan tap (bai hoc: gop tuoi NHIEU nguoi khac nhau trong tap ->
# false-positive — case that ep_05: tuoi chu (60s/21 luc tre) lan tuoi hon me (40)
# bi gop nham). Window hep giu tin hieu that, giam nhieu da-nguoi.


def find_internal_age_arithmetic_conflicts(scans):
    """F2: 2 cum 'age' + 'years_ago' NAM GAN NHAU (cung dong hoac +/-3 dong) ma
    phep tru tuoi KHONG dong nhat — nghi mau thuan CUNG 1 nguoi/su kien. Window
    hep de tranh gop tuoi nhieu nguoi khac nhau trong 1 tap (da xac minh: window
    rong = 70% tap bi flag sai, da so la conflate nhan vat khac nhau)."""
    conflicts = {}
    for ep, scan in scans.items():
        ages = [t for t in scan['temporal_mentions'] if t['kind'] == 'age']
        years_ago = [t for t in scan['temporal_mentions'] if t['kind'] == 'years_ago']
        ep_issues = []
        for ya in years_ago:
            nearby_ages = [a for a in ages
                          if abs(a['line'] - ya['line']) <= MAX_LINE_WINDOW_FOR_SAME_REFERENT]
            if len(nearby_ages) < 2:
                continue
            derived_candidates = set()
            for a in nearby_ages:
                derived_candidates.add(a['value'] - ya['value'])
                derived_candidates.add(a['value'] + ya['value'])
            # neu >1 "tuoi hien tai" khac nhau ma KHONG co cach nao cung khop 1
            # moc goc chung qua phep +/- years_ago -> mau thuan that
            distinct_ages = {a['value'] for a in nearby_ages}
            if len(distinct_ages) >= 2:
                consistent = any(
                    all(abs((a['value'] - ya['value']) - base) == 0 or
                        abs((a['value'] + ya['value']) - base) == 0
                        for a in nearby_ages)
                    for base in derived_candidates)
                if not consistent:
                    ep_issues.append({
                        'years_ago_line': ya['line'], 'years_ago_value': ya['value'],
                        'nearby_ages': sorted(distinct_ages),
                        'evidence': f"ep_{ep:02d}:{ya['line']} '{ya['text']}'",
                    })
        if ep_issues:
            conflicts[ep] = ep_issues
    return conflicts


def _add_freeform_nickname_candidates(nickname_candidates, eps):
    """Bo sung nickname tu passenger_main FREE-FORM (ep_11-50, KHONG co PAS_id —
    da biet tu G2 F1 finding). Tai su dung parse_passenger_main (G2), KHONG viet
    lai logic doan ten. Case that can bat: ep_15 header 'nam 31 Phong Hoài Đức
    (...)' -> name_guess='Phong Hoài' -> dang ky CA 2 tu ('Phong', 'Hoài') tru tu
    nao trung RECURRING_NAME_COMPONENTS (vd 'Phong' bi loai vi la ten tat cua
    Khai Phong — qua nhieu, con 'Hoài' van la tin hieu sach)."""
    for ep, path in eps:
        lines = path.read_text(encoding='utf-8').splitlines()
        header = parse_header(lines)
        pas_id, info = parse_passenger_main(header.get('passenger_main', ''))
        if pas_id is None:
            guess = info.get('name_guess')
            if guess:
                for w in guess.split():
                    if (w not in _COMMON_WORDS_EXCLUDE and w not in RECURRING_NAME_COMPONENTS
                            and len(w) >= 2):
                        nickname_candidates.setdefault(w, []).append(
                            (f'freeform_ep{ep:02d}', guess, ep))


def find_object_catalog_gaps(scans, catalog_ids):
    """F3 (moi phat hien khi build G4 — REAL finding, khong phai loi tool):
    signature_object mined tu header KHONG co trong bible/12 object_library.
    Xac nhan: 36/50 tap (chu yeu ep_11-50 free-form) dung OBJ_ id CHUA duoc
    khai vao catalog chinh thuc — khop dung RFC da ghi nhan truoc do (thieu
    nhom guong/kinh, hoa cuc, van ban nghe nghiep — memory blueprint-phase-state)."""
    gaps = {}
    for ep, scan in scans.items():
        obj = scan['primary_event'].get('signature_object')
        if obj and obj.startswith('OBJ_') and obj not in catalog_ids:
            gaps[ep] = obj
    return gaps


def mine(output_root=None, roster_path=None, bible12_path=None):
    eps = episode_files(output_root)
    nickname_candidates = _load_nickname_candidates(roster_path)
    _add_freeform_nickname_candidates(nickname_candidates, eps)
    scans = {ep: mine_episode(ep, f, nickname_candidates) for ep, f in eps}
    catalog_ids = _load_object_catalog_ids(bible12_path)
    f1 = find_cross_episode_name_recurrence(scans, nickname_candidates)
    f2 = find_internal_age_arithmetic_conflicts(scans)
    f3 = find_object_catalog_gaps(scans, catalog_ids)
    return {'episodes_scanned': [e for e, _ in eps], 'scans': scans,
            'findings': {'F1_cross_episode_name_recurrence': f1,
                        'F2_internal_age_arithmetic_conflict': f2,
                        'F3_object_not_in_bible12_catalog': f3}}


def write_outputs(result, out_draft=OUT_DRAFT, out_findings=OUT_FINDINGS):
    eps = result['episodes_scanned']
    events = {}
    for ep, scan in sorted(result['scans'].items()):
        events[f'ep_{ep:02d}'] = {
            'status': 'draft',
            'primary_event': scan['primary_event'],
            'temporal_mentions': scan['temporal_mentions'],
            'object_mentions': scan['object_mentions'],
        }
    draft = {
        'meta': {
            'tool': 'tools/event_ledger_miner.py',
            'generated': str(date.today()),
            'status': 'draft',
            'principle': 'Máy trích xuất — người DUYỆT. Chưa có sổ cái chính (chờ D3 fact_ledger_schema ký).',
            'episodes_scanned': len(eps),
            'episodes_range': f"ep_{min(eps):02d}..ep_{max(eps):02d}" if eps else 'none',
        },
        'events': events,
    }
    out_draft.write_text(yaml.safe_dump(draft, allow_unicode=True, sort_keys=False, width=120),
                         encoding='utf-8')

    f = result['findings']
    lines = [
        '# G4 EVENT FINDINGS — máy đào ngược episode ĐÃ CÓ (TASK_G4_WORLD D2)',
        '',
        f"- Sinh bởi: `tools/event_ledger_miner.py` — {date.today()}",
        f"- Tập quét: {len(eps)} (ep_{min(eps):02d}..ep_{max(eps):02d})" if eps else '- Tập quét: 0',
        '- Route: **executor/Mr.Long xử lý**. Mọi finding kèm evidence ep:line — không suy luận.',
        '',
        f"## F1 — Nickname roster xuất hiện ngoài tập được gán ({len(f['F1_cross_episode_name_recurrence'])} nickname)",
        '(KHÔNG mặc định là lỗi — có thể là continuity xuyên tập CHỦ Ý. Cần người xác nhận chủ ý hay trùng âm tiết ngẫu nhiên.',
        'GIỚI HẠN ĐÃ BIẾT: case ví dụ trong TASK ("Phong" ep_15 tái xuất ep_25) KHÔNG lọt vào danh sách này — '
        '"Phong" bị loại khỏi candidate vì trùng tên tắt của Khải Phong (nhân vật chính, ~mọi tập), '
        'còn "Hoài" (từ khác trong "Phong Hoài Đức") không xuất hiện lại trong ep_25 (chỉ có "Phong" được nhắc). '
        'Miner dựa trên tần suất âm tiết — không giải quyết được đồng tham chiếu (coreference) nhân vật qua đại từ/tên tắt trùng nhân vật chính.)',
        '',
    ]
    for nick, info in sorted(f['F1_cross_episode_name_recurrence'].items()):
        also = ', '.join(f'ep_{e:02d}' for e in info['also_appears_in'])
        assigned = ', '.join(f'ep_{e:02d}' for e in info['assigned_eps'])
        lines.append(f"- '{nick}' ({'/'.join(info['owner_pas_ids'])}, gán {assigned}) — xuất hiện thêm: {also}")
    if not f['F1_cross_episode_name_recurrence']:
        lines.append('- (không có)')
    lines += ['', f"## F2 — Mâu thuẫn số học tuổi/mốc thời gian TRONG PHẠM VI GẦN NHAU "
              f"(±{MAX_LINE_WINDOW_FOR_SAME_REFERENT} dòng, {len(f['F2_internal_age_arithmetic_conflict'])} tập)",
              '(ỨNG VIÊN cần người xem lại — KHÔNG khẳng định là lỗi thật. Đã xác nhận có false-positive '
              'kiểu "mất X năm trước, Y tuổi... trước sinh nhật (Y+1) tuổi" — văn phong "gần tròn tuổi" '
              'không phải mâu thuẫn số học, máy chưa phân biệt được. Window hẹp quanh mốc "X năm trước" '
              'giảm nhiễu gộp-nhiều-nhân-vật so với bản đầu (35→4 tập), nhưng vẫn cần người xác nhận từng ca.)', '']
    for ep, issues in sorted(f['F2_internal_age_arithmetic_conflict'].items()):
        for c in issues:
            lines.append(f"- {c['evidence']}: tuổi gần đó = {c['nearby_ages']} "
                         f"(không cùng khớp 1 mốc qua ±{c['years_ago_value']})")
    if not f['F2_internal_age_arithmetic_conflict']:
        lines.append('- (không có)')
    lines += ['', f"## F3 — signature_object KHÔNG có trong bible/12 object_library "
              f"({len(f['F3_object_not_in_bible12_catalog'])} tập)",
              '(PHÁT HIỆN THẬT khi build G4, khớp RFC đã ghi nhận trước đó — bible/12 thiếu nhóm '
              'gương/kính + hoa cúc + văn bản/nghề nghiệp. Route: RFC bible/12 mở rộng, Mr.Long duyệt.)', '']
    for ep, obj in sorted(f['F3_object_not_in_bible12_catalog'].items()):
        lines.append(f"- ep_{ep:02d}: '{obj}'")
    if not f['F3_object_not_in_bible12_catalog']:
        lines.append('- (không có)')
    out_findings.write_text('\n'.join(lines), encoding='utf-8')
    return draft


def validate_fact_entry_has_source(entry):
    """M3 (TASK_G4 mutation): fact_id KHONG nguon (thieu ep:line) -> FAIL khi
    merge vao so chinh (mirror governance/proposals/fact_ledger_schema.yaml —
    'nguon' bat buoc, khong duoc trong). Tra ve list loi (rong = hop le)."""
    errs = []
    nguon = entry.get('nguon') or []
    if not nguon:
        errs.append(f"{entry.get('fact_id', '?')}: THIEU nguon (ep:line bat buoc)")
    for n in nguon:
        if not re.match(r'^ep_\d+:\d+$', str(n)):
            errs.append(f"{entry.get('fact_id', '?')}: nguon '{n}' sai dinh dang (can 'ep_NN:line')")
    return errs


def main():
    result = mine()
    write_outputs(result)
    f = result['findings']
    print("=== EVENT LEDGER MINER (G4 D2) ===")
    print(f"  episodes scanned : {len(result['episodes_scanned'])}")
    print(f"  F1_cross_episode_name_recurrence: {len(f['F1_cross_episode_name_recurrence'])}")
    print(f"  F2_internal_age_arithmetic_conflict: {len(f['F2_internal_age_arithmetic_conflict'])}")
    print(f"  F3_object_not_in_bible12_catalog: {len(f['F3_object_not_in_bible12_catalog'])}")
    print(f"  -> {OUT_DRAFT.relative_to(SVHMP)}")
    print(f"  -> {OUT_FINDINGS.relative_to(SVHMP)}")
    print("  status: DRAFT — chưa có sổ cái chính (chờ D3 ký)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
