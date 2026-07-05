"""BP6 — mutation battery cho bp6_decision_check (đòn audit báo trước TASK_BP6).

Mutation TASK sẽ bắn: hardcode dialogue_ratio=0.45 → FAIL · knob 13 lạ → FAIL ·
generator writable knob → FAIL · knob thiếu → FAIL · packet field ma → FAIL ·
dup-key → FAIL. Mỗi negative assert MARKER cụ thể (bài học: test phải cắn,
không pass-rỗng). Positive: checker CLI exit 0 trên data bp6 THẬT (reality anchor).

pytest-func FLAT -> collect trong `pytest tests/` và ci_gate.
"""
import copy
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402
from bp6_decision_check import (  # noqa: E402
    check_contract, check_io, EXPECTED_KNOBS, D_CONTRACT, D_IO, D_BP0)

CONTRACT = load_yaml_no_dup(D_CONTRACT.read_text(encoding='utf-8'))
IO = load_yaml_no_dup(D_IO.read_text(encoding='utf-8'))
BP0 = load_yaml_no_dup(D_BP0.read_text(encoding='utf-8'))
CLI = REPO / 'tools' / 'bp6_decision_check.py'


# ---------- POSITIVE (reality anchor: data thật) ----------

def test_cli_exit_zero_on_real_data():
    r = subprocess.run([sys.executable, str(CLI)], capture_output=True,
                       text=True, encoding='utf-8')
    assert r.returncode == 0, f'checker phai PASS tren data bp6 that:\n{r.stdout}'


def test_real_contract_has_exactly_12_knobs_machine_counted():
    ids = [k['knob_id'] for k in CONTRACT['knobs']]
    assert len(ids) == 12 and set(ids) == set(EXPECTED_KNOBS)


def test_real_contract_zero_violations():
    assert check_contract(CONTRACT) == []


def test_real_io_zero_violations():
    assert check_io(IO, CONTRACT, BP0) == []


# ---------- MUTATIONS (mỗi đòn phải CẮN với marker cụ thể) ----------

def _mut_contract():
    return copy.deepcopy(CONTRACT)


def test_mut_hardcode_dialogue_ratio_045_bites():
    """Đòn TASK: hardcode dialogue_ratio=0.45 → FAIL R195."""
    c = _mut_contract()
    knob = next(k for k in c['knobs'] if k['knob_id'] == 'dialogue_ratio')
    knob['default'] = 0.45
    errs = check_contract(c)
    assert any('R195-HARDCODE' in e and 'dialogue_ratio' in e for e in errs), errs


def test_mut_numeric_leak_outside_valid_range_bites():
    """Số lạc ngoài valid_range (không qua key cấm) vẫn phải bị bắt."""
    c = _mut_contract()
    knob = next(k for k in c['knobs'] if k['knob_id'] == 'scene_budget')
    knob['calibration_source']['recommended'] = 7   # số chui vào chỗ khác
    errs = check_contract(c)
    assert any('R195-HARDCODE so nam ngoai valid_range' in e for e in errs), errs


def test_mut_13th_knob_bites():
    """Đòn TASK: knob thứ 13 lạ → FAIL."""
    c = _mut_contract()
    c['knobs'].append({'knob_id': 'music_volume', 'type': 'scalar',
                       'units': 'x', 'valid_range': [0, 1],
                       'consumer': {'domain': 'generator', 'access': 'read_only'},
                       'calibration_source': {'calibrate_from': 'golden'},
                       'lifecycle': 'draft', 'status': 'planned'})
    errs = check_contract(c)
    assert any('KNOB-LA' in e and 'music_volume' in e for e in errs), errs


def test_mut_missing_knob_bites():
    """Đòn TASK: knob thiếu → FAIL."""
    c = _mut_contract()
    c['knobs'] = [k for k in c['knobs'] if k['knob_id'] != 'pov']
    errs = check_contract(c)
    assert any('KNOB-THIEU' in e and 'pov' in e for e in errs), errs


def test_mut_generator_writable_bites():
    """Đòn TASK: consumer ghi-được (vi phạm read-only BP3) → FAIL."""
    c = _mut_contract()
    next(k for k in c['knobs'] if k['knob_id'] == 'pacing')['consumer']['access'] = 'write'
    errs = check_contract(c)
    assert any('LEO-THANG' in e and 'pacing' in e for e in errs), errs


def test_mut_enum_numeric_values_bites():
    c = _mut_contract()
    next(k for k in c['knobs'] if k['knob_id'] == 'pacing')['values'] = [1, 2, 3]
    errs = check_contract(c)
    assert any('enum value so' in e for e in errs), errs


def test_mut_calibration_not_golden_bites():
    c = _mut_contract()
    next(k for k in c['knobs'] if k['knob_id'] == 'fear_curve')['calibration_source'] = \
        {'calibrate_from': 'kinh nghiem chuyen gia'}
    errs = check_contract(c)
    assert any('khong tro golden' in e and 'fear_curve' in e for e in errs), errs


def test_mut_packet_ghost_field_bites():
    """Đòn TASK: packet chứa field ma → FAIL."""
    io = copy.deepcopy(IO)
    io['output']['packet_schema']['magic_number'] = {'type': 'int'}
    errs = check_io(io, CONTRACT, BP0)
    assert any('FIELD-MA' in e and 'magic_number' in e for e in errs), errs


def test_mut_packet_missing_calibration_evidence_bites():
    io = copy.deepcopy(IO)
    del io['output']['packet_schema']['calibration_evidence']
    errs = check_io(io, CONTRACT, BP0)
    assert any('calibration_evidence' in e for e in errs), errs


def test_mut_writer_escalation_bites():
    io = copy.deepcopy(IO)
    io['output']['writer'].append('generator')
    errs = check_io(io, CONTRACT, BP0)
    assert any('vi pham BP3 1-writer' in e for e in errs), errs


def test_mut_reader_outside_bp0_grant_bites():
    io = copy.deepcopy(IO)
    io['output']['consumer_contract']['reader'].append('publisher')
    errs = check_io(io, CONTRACT, BP0)
    assert any('ngoai grant BP0' in e for e in errs), errs


def test_mut_planned_input_missing_metadata_bites():
    # G6b (5/7): input.source_schema THAT da flip planned->exists (story_plan_schema.yaml
    # field-hoa xong) - tu dung 1 dict 'planned' gia lap de test rieng kha nang checker bat
    # thieu metadata (khong con dua vao fixture IO that nua, vi no da la 'exists').
    io = copy.deepcopy(IO)
    io['input']['source_schema'] = {
        'status': 'planned', 'planned_path': 'governance/blueprint/schemas/story_plan_schema.yaml',
        'owner': 'story_planner', 'reason_not_exists_yet': 'gia lap test',
        'target_milestone': 'M2_planner_generator',
        # thieu 'blocking_dependency' co chu dich
    }
    errs = check_io(io, CONTRACT, BP0)
    assert any('thieu metadata: blocking_dependency' in e for e in errs), errs


def test_dup_key_in_bp6_file_bites():
    """DUP-KEY loader single-impl phải bắt (lớp bug H6 blueprint)."""
    with pytest.raises(DupKeyError):
        load_yaml_no_dup('meta:\n  version: 1.0.0\nmeta:\n  version: 2.0.0\n')


# ---------- R195 FULL-FILE SCAN (fix 4/7 — ban cu chi scan tung knob rieng le,
# so hardcode NGOAI knobs (meta/rules/io) lot 100%. Cac test duoi day CHUNG MINH
# lo hong that va da vam) ----------

def test_mut_numeric_leak_in_contract_meta_bites():
    """So hardcode trong contract['meta'] (NGOAI knobs) — ban cu (_numeric_leaks(k, kid)
    chi goi tren tung dict knob) se KHONG bao gio thay vi khong scan meta. Full-file
    scan tu document root phai bat."""
    c = _mut_contract()
    c['meta']['default_dialogue_ratio'] = 0.45
    errs = check_contract(c)
    assert any('R195-HARDCODE' in e and 'meta.default_dialogue_ratio' in e for e in errs), errs


def test_mut_numeric_leak_in_contract_rules_section_bites():
    """So hardcode trong contract['rules'] (top-level, ngoai knobs) phai bat."""
    c = _mut_contract()
    c['rules']['max_scene_hardcode'] = 8
    errs = check_contract(c)
    assert any('R195-HARDCODE' in e and 'rules.max_scene_hardcode' in e for e in errs), errs


def test_mut_numeric_leak_anywhere_in_io_bites():
    """decision_io.yaml TRUOC FIX khong scan R195 mot chut nao (check_io khong goi
    _numeric_leaks). So hardcode bat ky dau trong io (vd packet_schema field moi
    mang so) phai bi bat SAU fix."""
    io = copy.deepcopy(IO)
    io['output']['packet_schema']['default_scene_count'] = {'type': 'int', 'value': 6}
    errs = check_io(io, CONTRACT, BP0)
    assert any('R195-HARDCODE' in e and 'so hardcode trong decision_io' in e for e in errs), errs
    assert any('packet_schema.default_scene_count.value' in e for e in errs), errs


def test_mut_numeric_leak_in_io_meta_bites():
    """So hardcode trong io['meta'] (xa packet_schema, chung minh scan la FULL-FILE
    tu document root chu khong phai 1 nhanh cu the)."""
    io = copy.deepcopy(IO)
    io['meta']['retry_count'] = 3
    errs = check_io(io, CONTRACT, BP0)
    assert any('R195-HARDCODE' in e and 'io.meta.retry_count' in e for e in errs), errs


def test_real_bp6_files_zero_numeric_leak_no_false_positive():
    """Regression: data BP6 that (12 knob + valid_range hop le) KHONG duoc bao
    R195-HARDCODE gia — full-file scan phai chinh xac, khong qua-nhay."""
    errs_c = check_contract(CONTRACT)
    errs_io = check_io(IO, CONTRACT, BP0)
    assert not any('R195-HARDCODE' in e for e in errs_c), errs_c
    assert not any('R195-HARDCODE' in e for e in errs_io), errs_io
