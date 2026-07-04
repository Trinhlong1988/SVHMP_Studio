"""G2 B3 — validate runtime/passenger_roster_backfill_ep11_50.yaml (extension
roster cho nhan vat one-shot ep_11-50, KHONG dung trong passenger_roster_100.yaml
vi file do khoa DUNG 100 — xem docstring dau file extension).

Batch 1 (5 passenger): PAS_0101/0102/0103/0105/0106. Con 34 cho batch sau.

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


def test_batch1_zero_violation_c1_to_c5():
    v, w = validate(_passengers(), FORBIDDEN, BIBLE23, BIBLE37)
    assert v == [], f"batch1 phai 0 violation C1-C5, got: {v[:5]}"
    assert w == [], f"batch1 phai 0 warn, got: {w[:5]}"


def test_batch1_exactly_5_passengers_ids_sequential():
    p = _passengers()
    ids = [x['id'] for x in p]
    assert ids == ['PAS_0113', 'PAS_0114', 'PAS_0115', 'PAS_0117', 'PAS_0118'], ids


def test_batch1_no_overlap_with_locked_roster_100():
    """39 nhan vat backfill KHONG duoc trung id/ten voi 100-roster da khoa."""
    roster100 = yaml.safe_load((SVHMP / 'runtime' / 'passenger_roster_100.yaml')
                               .read_text(encoding='utf-8'))
    ids100 = {p['id'] for p in roster100['passengers']}
    names100 = {p['char_name'] for p in roster100['passengers']}
    for p in _passengers():
        assert p['id'] not in ids100, f"id trung 100-roster: {p['id']}"
        assert p['char_name'] not in names100, f"ten trung 100-roster: {p['char_name']}"


def test_batch1_gap_objects_use_non_canonical_prefix():
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


def test_batch1_gap_count_matches_object_note_split():
    """2/5 batch nay la GAP that (hoa cuc), 3/5 la object that (pairing-mismatch
    thoi) — khoa dung phan chia da xac dinh, chong lan lon 2 loai note."""
    p = _passengers()
    n_gap = sum(1 for x in p if 'object_gap_note' in x)
    n_pairing = sum(1 for x in p if 'object_pairing_note' in x)
    assert n_gap == 2, f'ky vong 2 GAP that (hoa cuc), thay {n_gap}'
    assert n_pairing == 3, f'ky vong 3 object that (pairing-mismatch), thay {n_pairing}'


def test_batch1_death_type_khong_ro_when_self_death_unstated():
    """Tat ca 5 nhan vat batch 1: evidence chi ke ve NGUOI KHAC mat, khong neu
    ro chinh hanh khach chet the nao -> death.type phai 'khong_ro' (khong bia)."""
    for p in _passengers():
        assert p['death']['type'] == 'khong_ro', (
            f"{p['id']}: death.type phai khong_ro (evidence khong neu ro tu-vong "
            f"cua chinh hanh khach), dang la {p['death']['type']!r}")


def test_batch1_all_have_evidence_ref():
    for p in _passengers():
        assert p.get('evidence_ref'), f"{p['id']}: thieu evidence_ref (chong bia)"
        assert p.get('source_ep'), f"{p['id']}: thieu source_ep"
