"""BP7 — mutation battery cho bp7_narrative_check (đòn audit báo trước TASK_BP7).

Mutation TASK sẽ bắn: xoá REVEAL khỏi components → FAIL · cultural item facet ma
→ FAIL · nhét fear_curve=0.8 (số hardcode) → FAIL. Thêm: structure mâu thuẫn
bible/01 (thứ tự sai) → FAIL · curve_ref má → FAIL · DUP-KEY → FAIL.

LƯU Ý (4/7): bible/00_constitution.yaml đang có 2 DUP-KEY thật (rule_R142/R143,
kiểm duyệt xác nhận, chờ Mr.Long quyết nội dung + fix "per Mr.Long authorization").
Test end-to-end `main()`/full check_story_structure(ENDING) tạm KHÔNG assert full
PASS ở đây — chỉ test các phần độc lập với bible/00 bằng synthetic data. Sau khi
bible/00 được fix (thông báo qua PING), rerun `tools/bp7_narrative_check.py`
trực tiếp để xác nhận ENDING_RULES resolve sạch (không cần sửa test này).

pytest-func -> tự động collect trong `pytest tests/` và ci_gate.
"""
import copy
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402
from bp7_narrative_check import (  # noqa: E402
    check_story_structure, check_cultural_spec, check_pacing_format,
    D_STRUCTURE, D_CULTURAL, D_PACING, D_BP2, D_BP6, D_BIBLE01,
    EPISODE_COMPONENTS_EXPECTED)

STRUCTURE = load_yaml_no_dup(D_STRUCTURE.read_text(encoding='utf-8'))
CULTURAL = load_yaml_no_dup(D_CULTURAL.read_text(encoding='utf-8'))
PACING = load_yaml_no_dup(D_PACING.read_text(encoding='utf-8'))
BP2 = load_yaml_no_dup(D_BP2.read_text(encoding='utf-8'))
BP6 = load_yaml_no_dup(D_BP6.read_text(encoding='utf-8'))
BIBLE01 = load_yaml_no_dup(D_BIBLE01.read_text(encoding='utf-8'))


# ---------- POSITIVE (reality anchor — phần KHÔNG phụ thuộc bible/00) ----------

def test_real_cultural_spec_zero_violations():
    assert check_cultural_spec(CULTURAL, BP2) == []


def test_real_pacing_format_zero_violations():
    assert check_pacing_format(PACING, BP6) == []


def test_real_7_cultural_items_machine_counted():
    assert len(CULTURAL['items']) == 7


def test_real_5_curve_applications_machine_counted():
    assert len(PACING['curve_application']) == 5


def test_real_episode_components_match_bible01_order():
    """Phần story_structure KHÔNG phụ thuộc bible/00 (chỉ bible/01) — verify độc lập."""
    ep = next(lv for lv in STRUCTURE['levels'] if lv['level_id'] == 'episode')
    assert ep['components_required'] == EPISODE_COMPONENTS_EXPECTED
    real_keys = list(BIBLE01['bimodal_sentence_length_per_section']['pattern_per_section'].keys())
    assert real_keys == EPISODE_COMPONENTS_EXPECTED


# ---------- MUTATIONS (đòn TASK báo trước — mỗi cái phải CẮN) ----------

def _mut_structure():
    return copy.deepcopy(STRUCTURE)


def _mut_cultural():
    return copy.deepcopy(CULTURAL)


def _mut_pacing():
    return copy.deepcopy(PACING)


def test_mut_missing_reveal_component_bites():
    """Đòn TASK: xoá REVEAL khỏi components → FAIL."""
    s = _mut_structure()
    ep = next(lv for lv in s['levels'] if lv['level_id'] == 'episode')
    ep['components_required'] = [c for c in ep['components_required'] if c != 'REVEAL']
    errs = check_story_structure(s, BIBLE01)
    assert any('COMPONENT-LECH-BIBLE01' in e for e in errs), errs


def test_mut_wrong_order_components_bites():
    """structure mâu thuẫn bible/01 (đổi thứ tự) → FAIL."""
    s = _mut_structure()
    ep = next(lv for lv in s['levels'] if lv['level_id'] == 'episode')
    ep['components_required'] = ['SETUP', 'HOOK', 'INCIDENT', 'REVEAL', 'PAYOFF', 'CLIFFHANGER']
    errs = check_story_structure(s, BIBLE01)
    assert any('COMPONENT-LECH-BIBLE01' in e for e in errs), errs


def test_mut_missing_episode_level_bites():
    s = _mut_structure()
    s['levels'] = [lv for lv in s['levels'] if lv['level_id'] != 'episode']
    errs = check_story_structure(s, BIBLE01)
    assert any('THIEU level episode' in e for e in errs), errs


def test_mut_planned_missing_metadata_bites():
    s = _mut_structure()
    scene = next(lv for lv in s['levels'] if lv['level_id'] == 'scene')
    del scene['sot']['blocking_dependency']
    errs = check_story_structure(s, BIBLE01)
    assert any('scene' in e and 'blocking_dependency' in e for e in errs), errs


def test_mut_sot_phantom_path_bites():
    s = _mut_structure()
    season = next(lv for lv in s['levels'] if lv['level_id'] == 'season')
    season['sot'] = {'status': 'exists', 'path': 'bible/99_khong_ton_tai.yaml'}
    errs = check_story_structure(s, BIBLE01)
    assert any('phantom' in e for e in errs), errs


def test_mut_cultural_facet_ma_domain_bites():
    """Đòn TASK: cultural item trỏ facet má (domain lạ) → FAIL."""
    c = _mut_cultural()
    c['items'][0]['domain_facet'] = 'khong_ton_tai.xung_ho_convention'
    errs = check_cultural_spec(c, BP2)
    assert any('FACET-MA' in e and 'khong_ton_tai' in e for e in errs), errs


def test_mut_cultural_facet_ma_facet_id_bites():
    """cultural item trỏ facet má (facet_id lạ trong domain thật) → FAIL."""
    c = _mut_cultural()
    c['items'][0]['domain_facet'] = 'culture.facet_bia_dat'
    errs = check_cultural_spec(c, BP2)
    assert any('FACET-MA' in e and 'facet_bia_dat' in e for e in errs), errs


def test_mut_cultural_malformed_domain_facet_bites():
    c = _mut_cultural()
    c['items'][0]['domain_facet'] = 'khong_co_dau_cham'
    errs = check_cultural_spec(c, BP2)
    assert any('sai dinh dang' in e for e in errs), errs


def test_mut_pacing_hardcode_fear_curve_bites():
    """Đòn TASK: nhét fear_curve=0.8 (số hardcode) → FAIL."""
    p = _mut_pacing()
    entry = next(e for e in p['curve_application']
                if e['curve_ref'] == 'bp6.decision_contract.knobs.fear_curve')
    entry['default_value'] = 0.8
    errs = check_pacing_format(p, BP6)
    assert any('R195-HARDCODE' in e and 'default_value' in e for e in errs), errs


def test_mut_pacing_hardcode_nested_bites():
    p = _mut_pacing()
    p['series_level_aggregation']['sample_count'] = 90
    errs = check_pacing_format(p, BP6)
    assert any('R195-HARDCODE' in e and 'sample_count' in e for e in errs), errs


def test_mut_curve_ref_ma_bites():
    """curve_ref trỏ knob không tồn tại trong bp6 → FAIL."""
    p = _mut_pacing()
    p['curve_application'][0]['curve_ref'] = 'bp6.decision_contract.knobs.knob_bia_dat'
    errs = check_pacing_format(p, BP6)
    assert any('CURVE-MA' in e and 'knob_bia_dat' in e for e in errs), errs


def test_dup_key_in_bp7_file_bites():
    """DUP-KEY loader single-impl phải bắt (lớp bug H6 blueprint) — nguyên nhân
    chính CHÍNH LÀ lớp bug vừa phát hiện thật trong bible/00 (R142/R143)."""
    with pytest.raises(DupKeyError):
        load_yaml_no_dup('meta:\n  version: 1.0.0\nmeta:\n  version: 2.0.0\n')
