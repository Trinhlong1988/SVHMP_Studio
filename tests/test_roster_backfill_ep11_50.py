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
    GAP_MANH_GUONG_VO; ep_25 (kinh NGUYEN, khac chi tiet) dung GAP_KINH_PHAN_CHIEU
    rieng — khong duoc lan sang nhau."""
    by_ep = {p['source_ep']: p for p in _passengers()}
    for ep in (15, 35, 45):
        assert by_ep[ep]['haunting_symbol'] == 'GAP_MANH_GUONG_VO', (
            f"ep_{ep}: phai dung GAP_MANH_GUONG_VO (cum vat manh vo), "
            f"dang la {by_ep[ep]['haunting_symbol']!r}")
    assert by_ep[25]['haunting_symbol'] == 'GAP_KINH_PHAN_CHIEU', (
        f"ep_25: phai dung GAP_KINH_PHAN_CHIEU (kinh nguyen, khac ep_15/35/45), "
        f"dang la {by_ep[25]['haunting_symbol']!r}")


def test_continuity_warning_flagged_for_canon_touching_entries():
    """PAS_0137 (ep_36, nhac Khai Phong) va PAS_0141 (ep_40, nhac Ha Vy/anh Hai)
    dung cham nhan vat chinh da khoa bible/31 — PHAI co canh bao ro trong
    archetype_fit_note hoac death.pain, KHONG duoc am tham chot nhu binh thuong."""
    by_id = {p['id']: p for p in _passengers()}
    for pid in ('PAS_0137', 'PAS_0141'):
        p = by_id[pid]
        text = (p.get('archetype_fit_note', '') + p['death']['pain'])
        assert 'CANH BAO' in text or 'canh bao' in text.lower(), (
            f"{pid}: dung cham canon chinh (Khai Phong/Ha Vy) nhung KHONG co canh bao ro")


def test_waivers_ep30_ep50_absent_pending_mr_long():
    """2 waiver (ep_30 anh Nguyen / ep_50 Ha Nhi) GAC LAI HOAN TOAN — dung cham
    Khai Phong/Ha Vy da khoa, KHONG duoc tu y gan regret/object khi chua co
    Mr.Long xem truc tiep. Test nay khoa quyet dinh 'gac lai', chong tu-fill am
    tham sau nay ma khong qua duyet."""
    eps = {p['source_ep'] for p in _passengers()}
    assert 30 not in eps, 'ep_30 (waiver, dung Khai Phong) khong duoc tu fill'
    assert 50 not in eps, 'ep_50 (waiver, dung Ha Vy) khong duoc tu fill'
