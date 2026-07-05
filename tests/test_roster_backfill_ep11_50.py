"""G2 B3 — validate subset backfill (ep_11-50 one-shot) trong passenger_roster_100.yaml.

CAP NHAT 2026-07-05 (per Mr.Long authorization): Boss dao nguoc quyet dinh kien truc
"file rieng" truoc do -> 39 nhan vat backfill (37 batch1+2 + 2 waiver ep_30/ep_50)
DA MERGE vao chinh passenger_roster_100.yaml (139 passenger tong). File rieng
passenger_roster_backfill_ep11_50.yaml DA XOA sau khi xac nhan merge dung. Subset
backfill nhan dien qua field 'evidence_ref' (chi backfill entry co, 100-roster goc
khong co field nay).

Batch 1 (5 passenger, full-speech-evidence depth): PAS_0113/0114/0115/0117/0118.
Batch 2 (32 passenger, context-level evidence depth): PAS_0116/0119-0130/0132-0150.
2 waiver (ep_30 PAS_0131 / ep_50 PAS_0151): Mr.Long DA DOC TRUC TIEP 2 episode.md
va xac nhan draft Tier1 (2026-07-05) -> DA FILL, KHONG con gac lai.

pytest-func -> tu dong collect trong `pytest tests/` va ci_gate.
"""
import sys
from pathlib import Path

import yaml

SVHMP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SVHMP / 'tools'))
from roster_validator import validate, load_forbidden, load_bible23, load_bible37  # noqa: E402

ROSTER = SVHMP / 'runtime' / 'passenger_roster_100.yaml'
FORBIDDEN = load_forbidden()
BIBLE23 = load_bible23()
BIBLE37 = load_bible37()


def _all_passengers():
    data = yaml.safe_load(ROSTER.read_text(encoding='utf-8'))
    return data['passengers']


def _passengers():
    """Subset backfill ep11-50 — nhan dien qua field 'evidence_ref' (chi backfill co)."""
    return [p for p in _all_passengers() if 'evidence_ref' in p]


def test_zero_violation_c1_to_c5_full_roster():
    """G2 B4 fix (5/7): roster_validator gio check DU 6 field bible/37
    tier_1_mandatory.voice (truoc chi 3, thieu speaking_speed/catchphrase/
    forbidden_words/dialogue_sample - named!=enforced). 4 field moi la WARN-class
    (0/139 passenger da fill du lieu that, do luong thuc te) - KHONG phai
    regression, la con so THAT vua duoc phoi bay dung, cho Boss quyet dinh
    nguong truoc khi bat --strict (xem PROMPT_HANDOFF_CMD_BUILD_g2b4.md)."""
    all_p = _all_passengers()
    v, w = validate(all_p, FORBIDDEN, BIBLE23, BIBLE37)
    assert v == [], f"phai 0 violation C1-C5 tren toan bo 139, got: {v[:5]}"
    assert len(w) == len(all_p) * 4, (
        f"ky vong dung {len(all_p)}*4={len(all_p)*4} warn (4 field bible/37 voice "
        f"chua fill x {len(all_p)} passenger), got {len(w)}: {w[:5]}")


def test_exactly_39_backfill_passengers():
    """5 batch1 + 32 batch2 + 2 waiver (ep_30/ep_50, DA fill 2026-07-05) = 39."""
    p = _passengers()
    assert len(p) == 39, len(p)
    ids = [x['id'] for x in p]
    assert len(ids) == len(set(ids)), 'trung id noi bo subset'
    assert 'PAS_0131' in ids, 'ep_30 waiver PHAI co trong roster (da fill 2026-07-05)'
    assert 'PAS_0151' in ids, 'ep_50 waiver PHAI co trong roster (da fill 2026-07-05)'


def test_total_roster_is_139_after_merge():
    """100 goc + 39 backfill = 139 (per Mr.Long authorization merge 2026-07-05)."""
    p = _all_passengers()
    assert len(p) == 139, len(p)
    ids = [x['id'] for x in p]
    assert len(ids) == len(set(ids)), 'trung id toan bo roster sau merge'


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
    """Tat ca 39 nhan vat: evidence chi ke ve NGUOI KHAC mat/su kien qua khu, hoac
    (2 waiver) nhan vat con song -> death.type phai 'khong_ro' (khong bia gia tri
    moi, dung enum co san)."""
    for p in _passengers():
        assert p['death']['type'] == 'khong_ro', (
            f"{p['id']}: death.type phai khong_ro, dang la {p['death']['type']!r}")


def test_all_have_evidence_ref():
    for p in _passengers():
        assert p.get('evidence_ref'), f"{p['id']}: thieu evidence_ref (chong bia)"
        assert p.get('source_ep'), f"{p['id']}: thieu source_ep"


def test_mirror_shard_cluster_consistent_object():
    """CUM VAT bible/24 (ep_15/25/35/45 — 'manh guong/kinh cuu nguoi dinh tu tu',
    driver callback truc tiep xuyen 4 tap): ep_15/35/45 (manh VO) phai dung CUNG
    GAP_MANH_GUONG_VO; ep_25 (kinh NGUYEN, khac chi tiet) dung GAP_KINH_NHO
    rieng — khong duoc lan sang nhau."""
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
    canh bao placeholder DA GO, thay bang regret_label/death.pain THAT."""
    by_id = {p['id']: p for p in _passengers()}
    for pid in ('PAS_0137', 'PAS_0141'):
        p = by_id[pid]
        assert 'CANH BAO CONTINUITY' not in p['regret_label'], (
            f"{pid}: van con placeholder 'CANH BAO CONTINUITY' cu — chua duoc go dung")
        assert p['haunting_symbol'] != 'GAP_CHUA_XAC_DINH', (
            f"{pid}: van con object placeholder tam GAP_CHUA_XAC_DINH — chua dien that")
        assert p.get('signature_object') and p.get('haunting_symbol'), pid


def test_pas_0137_diem_boyfriend_named_tuan_not_khai_phong():
    """Doc sau speech_evidence ep_36 xac nhan: nguoi yeu cua Diem la 'Tuan' (SV
    Bach khoa) — header episode.md ghi nham 'Khai Phong' la loi miner/header."""
    by_id = {p['id']: p for p in _passengers()}
    p = by_id['PAS_0137']
    assert 'Tuấn' in p['death']['pain']
    assert 'Khải Phong' not in p['death']['pain'], (
        "death.pain khong duoc lap lai ten sai 'Khai Phong' tu header — than bai "
        "xac nhan ten that la Tuan")


def test_zero_placeholder_object_remaining():
    """39/39 nhan vat phai co signature_object/haunting_symbol THAT (OBJ_ that hoac
    GAP_<TEN> co y nghia) — KHONG con GAP_CHUA_XAC_DINH tam."""
    for p in _passengers():
        assert p['signature_object'] != 'GAP_CHUA_XAC_DINH', (
            f"{p['id']}: van con placeholder tam GAP_CHUA_XAC_DINH")
        assert p['haunting_symbol'] != 'GAP_CHUA_XAC_DINH', (
            f"{p['id']}: van con placeholder tam GAP_CHUA_XAC_DINH")
        assert p['signature_object'] == p['haunting_symbol'], (
            f"{p['id']}: signature_object != haunting_symbol (quy uoc dung 1 gia tri)")


def test_gap_object_reuse_across_characters_allowed():
    """Nhieu nhan vat khac nhau co the dung CHUNG 1 ma object khi vat that trong
    evidence CUNG loai — KHONG phai loi trung lap can sua."""
    from collections import Counter
    codes = Counter(p['signature_object'] for p in _passengers())
    reused = {c: n for c, n in codes.items() if n > 1}
    assert reused, 'ky vong co it nhat 1 object-code dung lai giua >=2 nhan vat khac nhau'


def test_object_code_cross_referenced_against_episode_declaration():
    """PROCESS-FIX (Boss spot-check PAS_0126 5/7): moi episode.md TU KHAI rieng
    mot dong `signature_object: OBJ_XXX` — bat buoc doi chieu voi ma dang dung,
    chong trung lap an nhu vu PAS_0126/ep_25 (GAP_KINH_PHAN_CHIEU vs OBJ_KINH_NHO)."""
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


def test_waivers_ep30_ep50_filled_per_mr_long_confirmation():
    """2 waiver (ep_30 anh Nguyen PAS_0131 / ep_50 Ha Nhi PAS_0151) DA duoc kiem
    duyet doc truc tiep episode.md va Mr.Long xac nhan draft (2026-07-05, khong
    con GAC LAI). Ca 2 la nhan vat CON SONG (entity_class=nguoi, life_status=song)
    — KHAC voi da so hanh khach khac (linh_hon/da_mat)."""
    by_id = {p['id']: p for p in _passengers()}
    for pid, ep in (('PAS_0131', 30), ('PAS_0151', 50)):
        p = by_id[pid]
        assert p['source_ep'] == ep
        assert p.get('entity_class') == 'nguoi', f"{pid}: phai entity_class=nguoi (con song)"
        assert p.get('life_status') == 'song', f"{pid}: phai life_status=song"
        assert p.get('regret_sub_archetype'), f"{pid}: thieu regret_sub_archetype"


def test_ha_nhi_regret_archetype_pending_rfc_not_fabricated():
    """PAS_0151 (Ha Nhi) KHONG khop bat ky archetype nao trong 27 muc bible/11 hien
    co (da doc toan bo catalog xac nhan) — dung placeholder RFC_PENDING_* tuong
    minh, KHONG duoc bia mot ma REG_* gia de "cho du field"."""
    by_id = {p['id']: p for p in _passengers()}
    p = by_id['PAS_0151']
    assert p['regret_sub_archetype'].startswith('RFC_PENDING'), (
        f"PAS_0151: regret_sub_archetype phai la RFC_PENDING_* tuong minh (khong "
        f"co archetype khop that trong bible/11), dang la {p['regret_sub_archetype']!r}")
