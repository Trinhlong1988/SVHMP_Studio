"""G2 B3 — roster_validator adversarial: valid -> 0, mutation lệch quê/tuổi/tên -> FAIL.

PHÂN VAI TASK_G2: "Kiểm duyệt: mutation (roster giả lệch quê/tuổi -> FAIL)".
Bài học 3/7: negative test PHẢI tự chứng minh nó cắn — mỗi mutation assert
violation CỤ THỂ xuất hiện (không assert rỗng-pass).

C4/C5 test thêm sau G2-B1-FLIP ceremony (Mr.Long ký bible/37 v2.1 + bible/23
v1.1, 2026-07-03): version-signed check + section/rule-present check + mutation
(thiếu rule/section, vùng không khai style, secret fact thiếu reveal_permission).

pytest-func -> tự động collect trong `pytest tests/` và ci_gate.
"""
import copy
import sys
from pathlib import Path

import yaml

SVHMP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SVHMP / 'tools'))
from roster_validator import (  # noqa: E402
    validate, load_forbidden, load_bible23, load_bible37,
    check_c4_naming_framework, check_c4b_vietnamese_purity, check_c5_knowledge_consistency)
import ci_gate  # noqa: E402

FORBIDDEN = load_forbidden()
BIBLE23 = load_bible23()
BIBLE37 = load_bible37()


# ---------- UNWIRE-GUARD (audit G2 vòng 1: gỡ stage 29 test vẫn xanh -> lỗ) ----------

def test_g2_roster_stage_wired_in_ci_gate():
    """Chống unwire (mirror test_blueprint_stage_wired_in_ci_gate BP5):
    gỡ ('G2_roster', tools/roster_validator.py) khỏi ci_gate CHECKS -> test này đỏ."""
    assert ('G2_roster', 'tools/roster_validator.py') in ci_gate.CHECKS, \
        'stage G2_roster bị gỡ khỏi ci_gate CHECKS (unwire!)'


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


def test_real_locked_roster_zero_violations_c1_to_c5():
    """Sau flip planned->exists (Mr.Long ký 2026-07-03): C4/C5 chạy thật, vẫn 0 violation."""
    v, w = validate(_real_passengers(), FORBIDDEN, BIBLE23, BIBLE37)
    assert v == [], f"roster LOCK phải 0 violation C1-C5, got: {v[:5]}"
    assert w == []


def test_synthetic_valid_passenger_clean():
    v, w = validate(_base(), FORBIDDEN)
    assert v == [] and w == []


# ---------- C4/C5 (bật sau Mr.Long ký bible/37 v2.1 + bible/23 v1.1) ----------

def test_c4_bible23_version_signed():
    assert str(BIBLE23.get('version', '')).startswith('1.1'), \
        'bible/23 phải v1.1 (naming framework đã ký) để C4 hoạt động'


def test_c4_all_4_naming_rules_present():
    rules = BIBLE23['RULES']
    for rid in ['rule_06_region_match', 'rule_07_generation_match',
                'rule_08_culture_belief', 'rule_09_vietnamese_purity']:
        assert rid in rules, f'thiếu {rid} trong bible/23 v1.1'


def test_c4_mutation_missing_rule_bites():
    b23 = copy.deepcopy(BIBLE23)
    del b23['RULES']['rule_06_region_match']
    errs = check_c4_naming_framework(b23, [])
    assert any('rule_06_region_match' in e for e in errs), errs


def test_c4_mutation_region_without_style_bites():
    """Roster dùng vùng KHÔNG có style_by_region khai -> C4 FAIL."""
    errs = check_c4_naming_framework(BIBLE23, [{'id': 'PAS_X', 'voice': {'region_dialect': 'tay_bac_fake'}}])
    assert any('tay_bac_fake' in e for e in errs), errs


def test_c4_mutation_unsigned_version_bites():
    b23 = copy.deepcopy(BIBLE23)
    b23['version'] = 1.0
    errs = check_c4_naming_framework(b23, [])
    assert any("chưa v1.1" in e for e in errs), errs


def test_c5_bible37_version_signed():
    assert str(BIBLE37['meta'].get('version', '')).startswith('2.1'), \
        'bible/37 phải v2.1 (g2_extension đã ký) để C5 hoạt động'


def test_c5_g2_extension_sections_present():
    g2 = BIBLE37['g2_extension']
    for key in ('knowledge', 'reveal_permission', 'continuity_risk'):
        assert key in g2, f'thiếu g2_extension.{key} trong bible/37 v2.1'


def test_c5_mutation_missing_section_bites():
    b37 = copy.deepcopy(BIBLE37)
    del b37['g2_extension']['reveal_permission']
    errs = check_c5_knowledge_consistency(b37, [])
    assert any('reveal_permission' in e for e in errs), errs


def test_c5_mutation_secret_knowledge_without_permission_bites():
    """Passenger biết fact secrecy=secret nhưng KHÔNG có reveal_permission -> FAIL."""
    p = [{'id': 'PAS_SECRET', 'knowledge': [{'fact_id': 'FACT_001', 'secrecy': 'secret'}],
         'reveal_permission': []}]
    errs = check_c5_knowledge_consistency(BIBLE37, p)
    assert any('FACT_001' in e and 'PAS_SECRET' in e for e in errs), errs


def test_c5_secret_knowledge_with_matching_permission_clean():
    """Có reveal_permission khớp fact_id -> KHÔNG FAIL (đối chứng dương)."""
    p = [{'id': 'PAS_OK', 'knowledge': [{'fact_id': 'FACT_002', 'secrecy': 'secret'}],
         'reveal_permission': [{'fact_id': 'FACT_002', 'permission': 'never'}]}]
    errs = check_c5_knowledge_consistency(BIBLE37, p)
    assert errs == [], errs


def test_c5_mutation_unsigned_version_bites():
    b37 = copy.deepcopy(BIBLE37)
    b37['meta']['version'] = 2.0
    errs = check_c5_knowledge_consistency(b37, [])
    assert any("chưa v2.1" in e for e in errs), errs


# ---------- C4b rule_09 content-check (Mr.Long lệnh 4/7 — "Jenny Trần phải đỏ") ----------

def test_c4b_lai_western_name_jenny_bites():
    """Đòn Mr.Long chỉ định: 'Jenny Trần' PHẢI đỏ."""
    errs = check_c4b_vietnamese_purity([{'id': 'PAS_X', 'char_name': 'Jenny Trần'}])
    assert any('C4b' in e and 'rule_09' in e for e in errs), errs


def test_c4b_game_pattern_name_bites():
    errs = check_c4b_vietnamese_purity([{'id': 'PAS_X', 'char_name': 'Thục Dragon'}])
    assert any('C4b' in e and 'pattern' in e for e in errs), errs


def test_c4b_foreign_charset_name_bites():
    """Ky tu ngoai bang chu cai Viet (vd Cyrillic) -> FAIL charset."""
    errs = check_c4b_vietnamese_purity([{'id': 'PAS_X', 'char_name': 'Thục Ыа'}])
    assert any('C4b' in e and 'charset' in e for e in errs), errs


def test_c4b_valid_vietnamese_diacritics_clean():
    """Regression cho bug charset liệt-kê-tay từng thiếu ú/ý (false-positive
    Phú Quý / Ánh Thúy) — tên dấu đầy đủ PHẢI sạch."""
    for name in ('Phú Quý', 'Ánh Thúy', 'Thoa Lý'):
        errs = check_c4b_vietnamese_purity([{'id': 'PAS_X', 'char_name': name}])
        assert errs == [], (name, errs)


def test_c4b_real_roster_zero_violation_no_false_positive():
    """Roster LOCK 100 passenger phải 0 violation C4b (không quá-nhạy)."""
    data = yaml.safe_load((SVHMP / 'runtime' / 'passenger_roster_100.yaml')
                          .read_text(encoding='utf-8'))
    errs = check_c4b_vietnamese_purity(data['passengers'])
    assert errs == [], errs[:5]


def test_c4b_wired_into_validate():
    """C4b phai chay trong validate() ngay ca khi khong truyen bible23/bible37
    (content-check khong phu thuoc bible da ky)."""
    p = [{'id': 'PAS_X', 'char_name': 'Jenny Trần', 'gender': 'nu',
         'regret_sub_archetype': 'REG_FAM_001', 'haunting_symbol': 'OBJ_TEST',
         'age_range': '26-35', 'life_status': 'da_mat',
         'voice': {'region_dialect': 'bac', 'hometown': 'Hà Nội', 'pronoun_system': 'tôi'},
         'death': {'type': 'tai_nan'}}]
    v, _ = validate(p, FORBIDDEN)
    assert any('C4b' in x for x in v), v


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
