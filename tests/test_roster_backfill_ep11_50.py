"""G2 B3 — validate runtime/passenger_roster_backfill_ep11_50.yaml (extension
roster cho nhan vat one-shot ep_11-50, KHONG dung trong passenger_roster_100.yaml
vi file do khoa DUNG 100 — xem docstring dau file extension).

Batch 1 (5 passenger, full-speech-evidence depth): PAS_0113/0114/0115/0117/0118.
Batch 2 (32 passenger, context-level evidence depth): PAS_0116/0119-0130/0132-0150.
2 waiver (ep_30 PAS_0131 / ep_50 PAS_0151) GAC LAI — dung cham Khai Phong/Ha Vy
da khoa bible/31, cho Mr.Long xem truoc — CHUA xuat hien trong file nay.

pytest-func -> tu dong collect trong `pytest tests/` va ci_gate.
"""
import sys
from pathlib import Path

import yaml

SVHMP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SVHMP / 'tools'))
from roster_validator import validate, load_forbidden, load_bible23, load_bible37  # noqa: E402

EXT_ROSTER = SVHMP / 'runtime' / 'passenger_roster_backfill_ep11_50.yaml'
FORBIDDEN = load_forbidden()
BIBLE23 = load_bible23()
BIBLE37 = load_bible37()


def _passengers():
    data = yaml.safe_load(EXT_ROSTER.read_text(encoding='utf-8'))
    return data['passengers']


def test_zero_violation_c1_to_c5():
    v, w = validate(_passengers(), FORBIDDEN, BIBLE23, BIBLE37)
    assert v == [], f"phai 0 violation C1-C5, got: {v[:5]}"
    assert w == [], f"phai 0 warn, got: {w[:5]}"


def test_exactly_37_passengers():
    """5 batch1 + 32 batch2 = 37 (2 waiver ep_30/ep_50 GAC LAI, chua trong file)."""
    p = _passengers()
    assert len(p) == 37, len(p)
    ids = [x['id'] for x in p]
    assert len(ids) == len(set(ids)), 'trung id noi bo file'
    assert 'PAS_0131' not in ids, 'ep_30 waiver KHONG duoc co trong file (gac lai cho Mr.Long)'
    assert 'PAS_0151' not in ids, 'ep_50 waiver KHONG duoc co trong file (gac lai cho Mr.Long)'


def test_no_overlap_with_locked_roster_100():
    """39 nhan vat backfill KHONG duoc trung id/ten voi 100-roster da khoa."""
    roster100 = yaml.safe_load((SVHMP / 'runtime' / 'passenger_roster_100.yaml')
                               .read_text(encoding='utf-8'))
    ids100 = {p['id'] for p in roster100['passengers']}
    names100 = {p['char_name'] for p in roster100['passengers']}
    for p in _passengers():
        assert p['id'] not in ids100, f"id trung 100-roster: {p['id']}"
        assert p['char_name'] not in names100, f"ten trung 100-roster: {p['char_name']}"


def test_gap_objects_use_non_canonical_prefix():
    """Object GAP THAT (khong co trong bible/12) phai dung prefix GAP_ o
    haunting_symbol — phan biet voi object_pairing_note (object THAT ton tai
    trong catalog, chi lech pillar-tag, khong phai gap)."""
    for p in _passengers():
        hs = p.get('haunting_symbol', '')
        if 'object_gap_note' in p:
            assert hs.startswith('GAP_'), (
                f"{p['id']}: co object_gap_note (claim GAP that) nhung "
                f"haunting_symbol {hs!r} khong phai GAP_ placeholder")
        if 'object_pairing_note' in p:
            assert not hs.startswith('GAP_'), (
                f"{p['id']}: object_pairing_note claim object THAT ton tai "
                f"nhung haunting_symbol {hs!r} lai la GAP_ placeholder")


def test_death_type_khong_ro_when_self_death_unstated():
    """Tat ca 37 nhan vat: evidence chi ke ve NGUOI KHAC mat hoac su kien qua khu,
    khong neu ro chinh hanh khach chet the nao -> death.type phai 'khong_ro'
    (khong bia)."""
    for p in _passengers():
        assert p['death']['type'] == 'khong_ro', (
            f"{p['id']}: death.type phai khong_ro (evidence khong neu ro tu-vong "
            f"cua chinh hanh khach), dang la {p['death']['type']!r}")


def test_all_have_evidence_ref():
    for p in _passengers():
        assert p.get('evidence_ref'), f"{p['id']}: thieu evidence_ref (chong bia)"
        assert p.get('source_ep'), f"{p['id']}: thieu source_ep"


def test_mirror_shard_cluster_consistent_object():
    """CUM VAT bible/24 (ep_15/25/35/45 — 'manh guong/kinh cuu nguoi dinh tu tu',
    driver callback truc tiep xuyen 4 tap): ep_15/35/45 (manh VO) phai dung CUNG
    GAP_MANH_GUONG_VO; ep_25 (kinh NGUYEN, khac chi tiet) dung GAP_KINH_NHO
    rieng — khong duoc lan sang nhau. (Ten GAP_KINH_NHO thay cho GAP_KINH_PHAN_CHIEU
    ngay 2026-07-05 de khop dung tu khai signature_object cua ep_25:39 — Boss
    spot-check phat hien ten cu khong doi chieu voi episode.md.)"""
    by_ep = {p['source_ep']: p for p in _passengers()}
    for ep in (15, 35, 45):
        assert by_ep[ep]['haunting_symbol'] == 'GAP_MANH_GUONG_VO', (
            f"ep_{ep}: phai dung GAP_MANH_GUONG_VO (cum vat manh vo), "
            f"dang la {by_ep[ep]['haunting_symbol']!r}")
    assert by_ep[25]['haunting_symbol'] == 'GAP_KINH_NHO', (
        f"ep_25: phai dung GAP_KINH_NHO (kinh nguyen, khac ep_15/35/45), "
        f"dang la {by_ep[25]['haunting_symbol']!r}")


def test_continuity_resolved_entries_have_real_regret_no_placeholder_warning():
    """PAS_0137 (ep_36) va PAS_0141 (ep_40) tung bi gac 'CANH BAO CONTINUITY' cho
    Mr.Long xac nhan. Mr.Long DA XAC NHAN khong dung canon (2026-07-04) — 2 co
    canh bao placeholder DA GO, thay bang regret_label/death.pain THAT (khong
    con text 'CANH BAO CONTINUITY' cu, khong con object GAP_CHUA_XAC_DINH tam)."""
    by_id = {p['id']: p for p in _passengers()}
    for pid in ('PAS_0137', 'PAS_0141'):
        p = by_id[pid]
        assert 'CANH BAO CONTINUITY' not in p['regret_label'], (
            f"{pid}: van con placeholder 'CANH BAO CONTINUITY' cu — chua duoc go dung")
        assert p['haunting_symbol'] != 'GAP_CHUA_XAC_DINH', (
            f"{pid}: van con object placeholder tam GAP_CHUA_XAC_DINH — chua dien that")
        assert p.get('signature_object') and p.get('haunting_symbol'), pid


def test_pas_0137_diem_boyfriend_named_tuan_not_khai_phong():
    """Doc sau speech_evidence ep_36 xac nhan: nguoi yeu cua Diem (em gai nhan
    vat) la 'Tuan' (SV Bach khoa) — header episode.md ghi nham 'Khai Phong' la
    loi miner/header (KHONG phai lien ket canon that). regret_label/death.pain
    PHAI dung ten THAT tu than bai (Tuan), khong lap lai ten sai cua header."""
    by_id = {p['id']: p for p in _passengers()}
    p = by_id['PAS_0137']
    assert 'Tuấn' in p['death']['pain']
    assert 'Khải Phong' not in p['death']['pain'], (
        "death.pain khong duoc lap lai ten sai 'Khai Phong' tu header — than bai "
        "xac nhan ten that la Tuan")


def test_zero_placeholder_object_remaining():
    """37/37 nhan vat (batch1+batch2, tru 2 waiver gac lai) phai co signature_object/
    haunting_symbol THAT (OBJ_ that hoac GAP_<TEN> co y nghia) — KHONG con
    GAP_CHUA_XAC_DINH tam (24 ca da fill xong per relay Boss 5/7)."""
    for p in _passengers():
        assert p['signature_object'] != 'GAP_CHUA_XAC_DINH', (
            f"{p['id']}: van con placeholder tam GAP_CHUA_XAC_DINH")
        assert p['haunting_symbol'] != 'GAP_CHUA_XAC_DINH', (
            f"{p['id']}: van con placeholder tam GAP_CHUA_XAC_DINH")
        assert p['signature_object'] == p['haunting_symbol'], (
            f"{p['id']}: signature_object != haunting_symbol (quy uoc file nay dung 1 gia tri)")


def test_gap_object_reuse_across_characters_allowed():
    """Nhieu nhan vat khac nhau co the dung CHUNG 1 ma object (OBJ_ that hoac GAP_)
    khi vat that trong evidence CUNG loai (vd 2 nguoi cung mat nhan cuoi) — KHONG
    phai loi trung lap can sua, mien moi entry co evidence_ref rieng."""
    from collections import Counter
    codes = Counter(p['signature_object'] for p in _passengers())
    reused = {c: n for c, n in codes.items() if n > 1}
    # it nhat 1 ma dung lai (OBJ_NHAN_CUOI: PAS ep_28+ep_42) — xac nhan hanh vi
    # dung y, khong phai bug. (OBJ_BAT_CANH_CHUA ep_39/ep_44 KHONG con dung lai
    # tu 2026-07-05 — phat hien la loi noi dung (com/che bi ep vao category
    # canh chua), da tach rieng GAP_TO_COM/GAP_KHUC_CHE.)
    assert reused, 'ky vong co it nhat 1 object-code dung lai giua >=2 nhan vat khac nhau'


def test_object_code_cross_referenced_against_episode_declaration():
    """PROCESS-FIX (Boss spot-check PAS_0126 5/7): moi episode.md TU KHAI rieng
    mot dong `signature_object: OBJ_XXX (mo ta)` — truoc day toi bia GAP_/OBJ_
    code rieng ma KHONG doi chieu dong nay, dan den PAS_0126/ep_25 dung
    GAP_KINH_PHAN_CHIEU trong khi episode.md da tu khai OBJ_KINH_NHO (cung 1
    vat, khac ten — trung lap an). Test nay bat buoc: voi MOI entry co
    source_ep, ma tu khai cua episode.md phai xuat hien nguyen van trong
    object_gap_note/object_pairing_note (hoac trung chinh xac signature_object
    khi dung lai ma that) — dam bao buoc doi chieu khong the bi bo qua am
    tham lan sau."""
    import re
    by_ep = {p['source_ep']: p for p in _passengers()}
    missing = []
    for ep, p in sorted(by_ep.items()):
        md_path = SVHMP / 'output' / f'ep_{ep}' / 'episode.md'
        if not md_path.exists():
            continue
        text = md_path.read_text(encoding='utf-8')
        m = re.search(r'^signature_object:\s*(\S+)', text, re.MULTILINE)
        if not m:
            continue
        declared_code = m.group(1)
        note = (p.get('object_gap_note') or p.get('object_pairing_note') or '') + \
            p.get('archetype_fit_note', '')
        matches = (declared_code == p['signature_object']) or (declared_code in note)
        if not matches:
            missing.append((p['id'], ep, declared_code, p['signature_object']))
    assert not missing, (
        "Cac entry sau CHUA doi chieu voi signature_object tu khai cua episode.md "
        "(id, ep, ma_tu_khai, ma_dang_dung): " + repr(missing))


def test_waivers_ep30_ep50_absent_pending_mr_long():
    """2 waiver (ep_30 anh Nguyen / ep_50 Ha Nhi) GAC LAI HOAN TOAN — dung cham
    Khai Phong/Ha Vy da khoa, KHONG duoc tu y gan regret/object khi chua co
    Mr.Long xem truc tiep. Test nay khoa quyet dinh 'gac lai', chong tu-fill am
    tham sau nay ma khong qua duyet."""
    eps = {p['source_ep'] for p in _passengers()}
    assert 30 not in eps, 'ep_30 (waiver, dung Khai Phong) khong duoc tu fill'
    assert 50 not in eps, 'ep_50 (waiver, dung Ha Vy) khong duoc tu fill'
