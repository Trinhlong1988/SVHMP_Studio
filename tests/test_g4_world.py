"""G4 — mutation battery cho World/Timeline/Event (TASK_G4_WORLD, kiểm chứng 4/7).

Mutation TASK sẽ bắn: M1 2 tập nhắc cùng sự kiện lệch mốc thời gian → FAIL ·
M2 đồ vật đổi trạng thái vô lý giữa 2 dòng liền kề → FAIL · M3 fact không nguồn
(thiếu ep:line) → FAIL khi merge vào sổ chính · M4 sự kiện rơi đúng rằm tháng 7
nhưng hành vi/không khí không khớp mùa → WARN · M5 gỡ stage G4_world → unwire
test đỏ · M6 event chain dùng domain/facet không có trong BP2/BP4 đã khai → FAIL.

pytest-func FLAT -> collect trong `pytest tests/` và ci_gate.
"""
import re
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
import ci_gate  # noqa: E402
from vn_number_words import extract_years_ago, extract_ages  # noqa: E402
from event_ledger_miner import (  # noqa: E402
    mine, validate_fact_entry_has_source, find_internal_age_arithmetic_conflicts)
from timeline_check import (  # noqa: E402
    check_arithmetic_consistency_across_episodes, check_cross_episode_M1,
    check_lunar_season_from_files, run as timeline_run)
from story_consistency_validator import (  # noqa: E402
    validate_event_consistency, validate_object_state_transition)

BIBLE12 = yaml.safe_load((REPO / 'bible' / '12_object_library.yaml').read_text(encoding='utf-8'))
OBJECT_CATALOG_IDS = set((BIBLE12.get('object_library') or {}).keys())


# ---------- UNWIRE-GUARD (M5 — mirror BP5/G2_roster pattern) ----------

def test_g4_world_stage_wired_in_ci_gate():
    """M5: gỡ ('G4_world', tools/g4_world_check.py) khỏi ci_gate CHECKS -> đỏ."""
    assert ('G4_world', 'tools/g4_world_check.py') in ci_gate.CHECKS, \
        'stage G4_world bị gỡ khỏi ci_gate CHECKS (unwire!)'


# ---------- POSITIVE (reality anchor: data thật 50 tập) ----------

def test_real_50_episodes_mined():
    result = mine()
    assert len(result['episodes_scanned']) == 50


def test_timeline_check_pass_on_real_data():
    result = timeline_run()
    assert result['M1_cross_episode_violations'] == [], \
        'M1 tren du lieu that phai 0 (chua co lien ket xac nhan tu D3) — khac 0 la loi thiet ke'


def test_vn_number_words_extract_real_case():
    """Case that ep_25 line 133: 'Ba mươi tám tuổi' — extract_ages doi hoi tu
    'tuổi' theo sau (NHIEU cau trong corpus khai bao tuoi KHONG kem 'tuổi' —
    vd 'ba mươi mốt' dung 1 minh — day la GIOI HAN da biet, extract_ages CHi
    bat duoc dang co 'tuổi' tuong minh, khong doan tu ngu canh)."""
    text = 'Tôi là Văn Quân. Ba mươi tám tuổi. Tôi ở Thái Nguyên — quê.'
    ages = [v for v, _, _ in extract_ages(text)]
    assert 38 in ages


# ---------- M1: mâu thuẫn thời gian xuyên tập (dùng synthetic — case CONFIRMED cùng người) ----------

def test_m1_consistent_cross_episode_ages_pass():
    """Case Phong-like: 21 tuổi + 10 năm = 31, nhất quán cả 2 tập -> True (không FAIL)."""
    ok = check_arithmetic_consistency_across_episodes({15: {31}, 25: {31}}, {15: {10}, 25: {10}})
    assert ok is True


def test_m1_conflicting_cross_episode_ages_bites():
    """Đòn TASK M1: 2 tập nhắc cùng sự kiện lệch mốc thời gian -> phải phát hiện False."""
    ok = check_arithmetic_consistency_across_episodes({15: {31}, 25: {50}}, {15: {10}, 25: {10}})
    assert ok is False


# ---------- M1 WIRING FIX (bug 2 lớp đã audit: check_cross_episode_M1(mined)
# bỏ qua tham số `mined`, return [] vô điều kiện — R84 KHÔNG BAO GIỜ bắt được
# mâu thuẫn xuyên tập dù rõ đến đâu. Fix: lớp MỚI, HẸP HƠN F1 — exact literal
# full-name match (case-sensitive, KHÔNG fuzzy/nickname) + xác nhận qua
# check_arithmetic_consistency_across_episodes() trên dữ liệu THẬT-mined.
# Xem reports/G4_FIX_TIMELINE_CROSSEP.md cho before/after evidence đầy đủ.) ----------

def _write_episode(root, ep_no, body_lines, header_kv=None):
    header_kv = header_kv or {'regret_sub': 'TEST'}
    ep_dir = root / f'ep_{ep_no:02d}'
    ep_dir.mkdir(parents=True, exist_ok=True)
    header = '\n'.join(f'{k}: {v}' for k, v in header_kv.items())
    text = f"```\n{header}\n```\n" + '\n'.join(body_lines) + '\n'
    (ep_dir / 'episode.md').write_text(text, encoding='utf-8')


def _write_roster(path, entries):
    path.write_text(yaml.safe_dump({'passengers': entries}, allow_unicode=True, sort_keys=False),
                    encoding='utf-8')


def test_m1_exact_name_match_arithmetic_conflict_bites(tmp_path):
    """Đòn TASK (case audit xác nhận là BUG THẬT): CÙNG 1 tên nhân vật ĐẦY ĐỦ
    ('Phong Hoài Đức', case-sensitive, full-name — KHÔNG phải fuzzy/nickname
    kiểu F1) xuất hiện literal ở ep_15 VÀ ep_25; ep_15 nói '...ba mươi mốt
    tuổi. Mười năm trước...', ep_25 nói '...năm mươi tuổi. Mười năm trước...'
    cho CÙNG mốc 'mười năm trước' — mâu thuẫn số học rõ ràng (31 vs 50, cùng
    -10 năm). TRƯỚC FIX: check_cross_episode_M1 bỏ qua `mined`, return []
    VÔ ĐIỀU KIỆN -> case này (dù rõ ràng đến đâu) vẫn PASS sai (xanh giả).
    SAU FIX: phải FAIL đúng (đỏ thật)."""
    roster = tmp_path / 'roster.yaml'
    _write_roster(roster, [{'id': 'PAS_TEST01', 'char_name': 'Phong Hoài Đức', 'assigned_ep': 15}])
    out_root = tmp_path / 'output'
    _write_episode(out_root, 15, [
        'Phong Hoài Đức năm nay ba mươi mốt tuổi. Mười năm trước, anh gặp tai nạn định mệnh.'])
    _write_episode(out_root, 25, [
        'Phong Hoài Đức năm nay năm mươi tuổi. Mười năm trước, anh gặp tai nạn định mệnh.'])

    mined = mine(output_root=out_root, roster_path=roster)
    violations = check_cross_episode_M1(mined, output_root=out_root, roster_path=roster)

    assert violations != [], (
        'FIX PHẢI bắt được mâu thuẫn xuyên tập rõ ràng (before fix: [] vô điều kiện, sai)')
    assert violations[0]['exact_name'] == 'Phong Hoài Đức'
    assert set(violations[0]['episodes']) == {15, 25}


def test_m1_exact_name_match_consistent_case_clean(tmp_path):
    """Case Phong-like NHẤT QUÁN (mirror ví dụ TASK gốc: 21 tuổi + 10 năm = 31
    khớp cả 2 tập) -> KHÔNG được FAIL (âm tính thật, không phải 0-vì-yếu)."""
    roster = tmp_path / 'roster.yaml'
    _write_roster(roster, [{'id': 'PAS_TEST02', 'char_name': 'Lộc Thiên Ân', 'assigned_ep': 15}])
    out_root = tmp_path / 'output'
    _write_episode(out_root, 15, [
        'Lộc Thiên Ân năm nay ba mươi mốt tuổi. Mười năm trước, cô rời quê.'])
    _write_episode(out_root, 25, [
        'Lộc Thiên Ân năm nay ba mươi mốt tuổi. Mười năm trước, cô rời quê.'])

    mined = mine(output_root=out_root, roster_path=roster)
    violations = check_cross_episode_M1(mined, output_root=out_root, roster_path=roster)
    assert violations == []


def test_m1_exact_name_match_requires_paired_temporal_anchor_not_bare_age_diff(tmp_path):
    """GIỚI HẠN CHỦ Ý (chống false-positive kiểu F2 cũ, case thật 'Hạ Nhi' bắt
    được khi build fix này — xem G4_FIX_TIMELINE_CROSSEP.md): 2 tập nhắc CÙNG
    tên đầy đủ với 2 TUỔI khác nhau NHƯNG KHÔNG có 'X năm trước' đi kèm ở tập
    nào để lập được phép tính đối chiếu -> KHÔNG đủ để hard-fail (không phải
    'temporal anchor' hợp lệ theo R84, có thể là 2 người/bối cảnh khác nhau
    trùng tên diễn giải, không phải mâu thuẫn số học xác nhận được)."""
    roster = tmp_path / 'roster.yaml'
    _write_roster(roster, [{'id': 'PAS_TEST03', 'char_name': 'Hạ Nhi Tường', 'assigned_ep': 15}])
    out_root = tmp_path / 'output'
    _write_episode(out_root, 15, ['Hạ Nhi Tường năm nay mười sáu tuổi, còn rất trẻ.'])
    _write_episode(out_root, 25, ['Hạ Nhi Tường năm nay hai mươi tư tuổi, đã trưởng thành.'])

    mined = mine(output_root=out_root, roster_path=roster)
    violations = check_cross_episode_M1(mined, output_root=out_root, roster_path=roster)
    assert violations == [], (
        'KHÔNG có mốc "X năm trước" đi kèm -> chưa đủ tin cậy để hard-fail (giới hạn THẬT, không phải né việc)')


def test_m1_single_word_nickname_not_promoted_to_exact_name_layer(tmp_path):
    """Đảm bảo lớp MỚI KHÔNG lặp lại lỗi F1 cũ: char_name 1 từ (họ/tên tắt,
    không phải 'full name' thật — mirror case thật PAS_0131 'Nguyễn' trong
    spare_pool) bị loại khỏi candidate ngay từ vòng load, dù trùng lặp nhiều
    tập và có vẻ mâu thuẫn tuổi."""
    roster = tmp_path / 'roster.yaml'
    _write_roster(roster, [{'id': 'PAS_TEST04', 'char_name': 'Nguyễn', 'assigned_ep': None}])
    out_root = tmp_path / 'output'
    _write_episode(out_root, 15, [
        'Nguyễn năm nay ba mươi mốt tuổi. Mười năm trước, anh rời làng.'])
    _write_episode(out_root, 25, [
        'Nguyễn năm nay năm mươi tuổi. Mười năm trước, anh rời làng.'])

    mined = mine(output_root=out_root, roster_path=roster)
    violations = check_cross_episode_M1(mined, output_root=out_root, roster_path=roster)
    assert violations == [], 'char_name 1 từ không phải full-name — không được vào lớp exact-match mới'


# ---------- M2: đồ vật đổi trạng thái vô lý ----------

def test_m2_object_jump_unexplained_bites():
    """Đòn TASK M2: đồ vật đổi trạng thái vô lý giữa 2 dòng liền kề -> FAIL."""
    issues = validate_object_state_transition('OBJ_AO_LEN_NAU', 'rách', 'lành',
                                              nearby_text='Cô mặc áo, đẹp như mới.')
    assert any(i['code'] == 'OBJECT_STATE_JUMP_UNEXPLAINED' for i in issues)


def test_m2_object_jump_explained_clean():
    issues = validate_object_state_transition('OBJ_AO_LEN_NAU', 'rách', 'lành',
                                              nearby_text='Cô đã vá lại áo cẩn thận tối qua.')
    assert issues == []


def test_event_consistency_locked_field_changed_bites():
    b = {'event_id': 'EVT_001', 'thoi_diem': 'tám năm trước', 'nguyen_nhan': 'tai nạn'}
    issues = validate_event_consistency(b, {**b, 'thoi_diem': 'mười năm trước'})
    assert any(i['code'] == 'EVENT_LOCKED_FIELD_CHANGED' for i in issues)


def test_event_consistency_same_clean():
    b = {'event_id': 'EVT_001', 'thoi_diem': 'tám năm trước', 'nguyen_nhan': 'tai nạn'}
    assert validate_event_consistency(b, dict(b)) == []


# ---------- M3: fact không nguồn ----------

def test_m3_fact_missing_source_bites():
    """Đòn TASK M3: fact không nguồn (thiếu ep:line) -> FAIL."""
    errs = validate_fact_entry_has_source({'fact_id': 'FACT_X', 'nguon': []})
    assert any('THIEU nguon' in e for e in errs)


def test_m3_fact_malformed_source_bites():
    errs = validate_fact_entry_has_source({'fact_id': 'FACT_Y', 'nguon': ['khong-dung-dinh-dang']})
    assert any('sai dinh dang' in e for e in errs)


def test_m3_fact_valid_source_clean():
    errs = validate_fact_entry_has_source({'fact_id': 'FACT_Z', 'nguon': ['ep_02:78']})
    assert errs == []


def test_proposed_fact_ledger_examples_have_source():
    """Reality anchor: ví dụ trong proposal tự nó phải qua được check M3."""
    doc = yaml.safe_load((REPO / 'governance' / 'proposals' / 'fact_ledger_schema.yaml')
                         .read_text(encoding='utf-8'))
    for entry in doc.get('example_entries') or []:
        assert validate_fact_entry_has_source(entry) == []


# ---------- M4: lịch âm lệch mùa (WARN) ----------

def test_m4_lunar_season_contradiction_bites(tmp_path):
    """Đòn TASK M4: sự kiện rơi đúng rằm tháng 7 nhưng mô tả mùa không khớp -> WARN."""
    ep_dir = tmp_path / 'ep_99'
    ep_dir.mkdir()
    text = ('x' * 10 + '\nĐêm rằm tháng 7 âm lịch. Trời nắng gắt, oi bức suốt buổi tối.\n' + 'y' * 10)
    (ep_dir / 'episode.md').write_text(text, encoding='utf-8')
    warns = check_lunar_season_from_files(tmp_path)
    assert any('rằm tháng 7' in w for w in warns)


def test_m4_lunar_season_consistent_clean(tmp_path):
    ep_dir = tmp_path / 'ep_99'
    ep_dir.mkdir()
    text = 'Đêm rằm tháng 7 âm lịch. Mưa lất phất, se lạnh cuối thu.'
    (ep_dir / 'episode.md').write_text(text, encoding='utf-8')
    warns = check_lunar_season_from_files(tmp_path)
    assert warns == []


# ---------- M6: object_mentions phải trỏ facet/catalog đã khai (BP2/bible/12) ----------

def test_m6_real_data_object_gaps_found_as_F3_finding():
    """REALITY ANCHOR: mining 50 tập thật PHÁT HIỆN THẬT 36 tập dùng OBJ_ id
    chưa khai trong bible/12 (chủ yếu ep_11-50 free-form — khớp RFC đã ghi nhận
    trước đó: bible/12 thiếu nhóm gương/kính/hoa cúc/văn bản). Đây là FINDING
    (F3, route RFC Mr.Long), KHÔNG PHẢI lỗi tool hay hard-fail của gate — mirror
    cách F1/F2 đã framework 'ứng viên cần người xem lại'."""
    result = mine()
    f3 = result['findings']['F3_object_not_in_bible12_catalog']
    assert len(f3) > 0, "REALITY ANCHOR: phải phát hiện được gap thật đã biết (nếu 0 = nghi tool yếu)"
    assert all(v.startswith('OBJ_') for v in f3.values())


def test_m6_object_id_ma_bites():
    """Đòn TASK M6: event/object dùng id không có trong catalog đã khai -> FAIL
    (mutation thật trên hàm check_object_catalog_gaps)."""
    from event_ledger_miner import find_object_catalog_gaps
    scans = {1: {'primary_event': {'signature_object': 'OBJ_BIA_DAT_KHONG_TON_TAI'}}}
    gaps = find_object_catalog_gaps(scans, OBJECT_CATALOG_IDS)
    assert gaps == {1: 'OBJ_BIA_DAT_KHONG_TON_TAI'}


def test_m6_object_id_real_clean():
    from event_ledger_miner import find_object_catalog_gaps
    real_id = next(iter(OBJECT_CATALOG_IDS))
    scans = {1: {'primary_event': {'signature_object': real_id}}}
    assert find_object_catalog_gaps(scans, OBJECT_CATALOG_IDS) == {}


# ---------- DUP-KEY guard (single-impl loader, mirror BP pattern) ----------

def test_dup_key_loader_used_for_proposal():
    """fact_ledger_schema.yaml proposal phai la YAML hop le, khong dup-key —
    dung yaml.safe_load truc tiep (file governance/proposals KHONG thuoc pham
    vi loader nghiem blueprint_constitution_check, do la rieng cho bpN)."""
    doc = yaml.safe_load((REPO / 'governance' / 'proposals' / 'fact_ledger_schema.yaml')
                         .read_text(encoding='utf-8'))
    assert doc['meta']['status'] == 'PROPOSAL_AWAITING_MR_LONG_SIGNATURE'
