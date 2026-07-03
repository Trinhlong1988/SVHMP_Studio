"""G2 B3 — roster_validator adversarial: valid -> 0, mutation lệch quê/tuổi/tên -> FAIL.

PHÂN VAI TASK_G2: "Kiểm duyệt: mutation (roster giả lệch quê/tuổi -> FAIL)".
Bài học 3/7: negative test PHẢI tự chứng minh nó cắn — mỗi mutation assert
violation CỤ THỂ xuất hiện (không assert rỗng-pass).

pytest-func -> tự động collect trong `pytest tests/` và ci_gate.
"""
import copy
import sys
from pathlib import Path

import yaml

SVHMP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SVHMP / 'tools'))
from roster_validator import validate, load_forbidden  # noqa: E402

FORBIDDEN = load_forbidden()


def _real_passengers():
    data = yaml.safe_load((SVHMP / 'runtime' / 'passenger_roster_100.yaml')
                          .read_text(encoding='utf-8'))
    return data['passengers']


def _base():
    """1 passenger hợp lệ tổng hợp (không đụng roster thật)."""
    return [{
        'id': 'PAS_TEST', 'char_name': 'Thục Đoan', 'gender': 'nu',
        'regret_sub_archetype': 'REG_FAM_001', 'haunting_symbol': 'OBJ_TEST',
        'age_range': '26-35', 'life_status': 'da_mat',
        'voice': {'region_dialect': 'bac', 'hometown': 'Hà Nội',
                  'pronoun_system': 'tôi'},
        'death': {'type': 'tai_nan'},
    }]


# ---------- POSITIVE ----------

def test_real_locked_roster_zero_violations():
    v, w = validate(_real_passengers(), FORBIDDEN)
    assert v == [], f"roster LOCK phải 0 violation, got: {v[:5]}"
    assert w == []


def test_synthetic_valid_passenger_clean():
    v, w = validate(_base(), FORBIDDEN)
    assert v == [] and w == []


# ---------- MUTATIONS (mỗi cái phải CẮN với violation cụ thể) ----------

def _mutate(**patch):
    p = _base()
    p[0].update(copy.deepcopy(patch))
    return p


def test_mutation_hometown_mismatch_region_bites():
    """Roster giả LỆCH QUÊ: giọng bắc + quê Sài Gòn -> C2 FAIL."""
    p = _mutate(voice={'region_dialect': 'bac', 'hometown': 'Sài Gòn',
                       'pronoun_system': 'tôi'})
    v, _ = validate(p, FORBIDDEN)
    assert any('C2' in x and 'Sài Gòn' in x for x in v), v


def test_mutation_missing_age_bites_warn():
    """Roster giả LỆCH TUỔI: age_range trống mà không phải linh_hon -> WARN."""
    p = _mutate(age_range='')
    v, w = validate(p, FORBIDDEN)
    assert any('age_range' in x for x in w), w


def test_mutation_one_syllable_name_bites():
    p = _mutate(char_name='Loan')
    v, _ = validate(p, FORBIDDEN)
    assert any('rule_01' in x for x in v), v


def test_mutation_forbidden_name_bites():
    p = _mutate(char_name='Thục Linh')   # 'Linh' trong 15 từ cấm Mr.Long
    v, _ = validate(p, FORBIDDEN)
    assert any('từ cấm' in x and 'Linh' in x for x in v), v


def test_mutation_nam_word_bites_rule04():
    p = _mutate(char_name='Thục Nam')
    v, _ = validate(p, FORBIDDEN)
    assert any('rule_04' in x for x in v), v


def test_mutation_duplicate_word_across_two_names_bites():
    p = _base() + [{**_base()[0], 'id': 'PAS_TEST2', 'char_name': 'Đoan Trinh'}]
    v, _ = validate(p, FORBIDDEN)
    assert any('rule_02' in x and 'Đoan' in x for x in v), v


def test_mutation_empty_name_bites():
    """Empty-value case (bài học weak-verifier): tên rỗng KHÔNG được pass im."""
    p = _mutate(char_name='')
    v, _ = validate(p, FORBIDDEN)
    assert any('rule_01' in x for x in v) and any("'char_name'" in x for x in v), v


def test_mutation_missing_voice_fields_bites():
    p = _mutate(voice={})
    v, _ = validate(p, FORBIDDEN)
    missing = [x for x in v if 'voice.' in x]
    assert len(missing) == 3, v   # region_dialect + hometown + pronoun_system


def test_mutation_missing_death_type_bites():
    p = _mutate(death={})
    v, _ = validate(p, FORBIDDEN)
    assert any('death.type' in x for x in v), v


def test_mutation_unknown_region_bites():
    p = _mutate(voice={'region_dialect': 'tay_nguyen_fake', 'hometown': 'Hà Nội',
                       'pronoun_system': 'tôi'})
    v, _ = validate(p, FORBIDDEN)
    assert any('C2' in x and 'tay_nguyen_fake' in x for x in v), v
