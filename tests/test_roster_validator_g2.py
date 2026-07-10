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
                  'pronoun_system': 'tôi', 'speaking_speed': 'binh_thuong',
                  'catchphrase': 'thoi thi', 'forbidden_words': ['vai'],
                  'dialogue_sample': 'toi khong con gi de noi'},
        'death': {'type': 'tai_nan'},
    }]


# ---------- POSITIVE ----------

def test_real_locked_roster_zero_violations():
    v, w = validate(_real_passengers(), FORBIDDEN)
    assert v == [], f"roster LOCK phải 0 violation, got: {v[:5]}"
    # G2 B4 fix (5/7): 4 field bible/37 tier_1_mandatory.voice moi duoc them vao
    # check (speaking_speed/catchphrase/forbidden_words/dialogue_sample) la
    # WARN-class. B4 voice-fill (batch nho, dang tien hanh 5/7) DAN GIAM so
    # warn nay theo tung dot - KHONG hardcode con so co dinh (se doi moi
    # batch), tinh DONG bang cach dem thuc te bao nhieu (passenger, field)
    # con thieu, roi doi chieu dung voi validate() tra ve. Test van cham
    # regression that: neu validate() dem sai (vd bo sot 1 field) se lech voi
    # phep dem doc lap nay.
    real = _real_passengers()
    voice_warn_fields = ('speaking_speed', 'catchphrase', 'forbidden_words', 'dialogue_sample')
    expected_missing = sum(1 for p in real for f in voice_warn_fields
                           if not (p.get('voice') or {}).get(f))
    assert len(w) == expected_missing, (
        f"ky vong {expected_missing} warn (dem thuc te tren du lieu), got {len(w)}")
    if expected_missing:
        for field in voice_warn_fields:
            if any(not (p.get('voice') or {}).get(field) for p in real):
                assert any(field in x for x in w), f"thieu warn cho field '{field}'"


def test_real_locked_roster_zero_violations_c1_to_c5():
    """Sau flip planned->exists (Mr.Long ký 2026-07-03): C4/C5 chạy thật, vẫn 0 violation.
    Warn (B4 4-field bible/37 voice chưa fill, dem dong) — xem test_real_locked_roster_zero_violations."""
    real = _real_passengers()
    v, w = validate(real, FORBIDDEN, BIBLE23, BIBLE37)
    assert v == [], f"roster LOCK phải 0 violation C1-C5, got: {v[:5]}"
    voice_warn_fields = ('speaking_speed', 'catchphrase', 'forbidden_words', 'dialogue_sample')
    expected_missing = sum(1 for p in real for f in voice_warn_fields
                           if not (p.get('voice') or {}).get(f))
    assert len(w) == expected_missing, (
        f"ky vong {expected_missing} warn (dem thuc te tren du lieu), got {len(w)}")


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
    v = str(BIBLE37['meta'].get('version', ''))
    v_tuple = tuple(int(x) for x in v.split('.')[:2])
    assert v_tuple >= (2, 1), \
        f"bible/37 phải >=v2.1 (g2_extension đã ký) để C5 hoạt động, hiện '{v}'"


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


# ---------- PROCESS-FIX (audit G2-1, 2026-07): chong cong-thuc-1-bien-0-ngoai-le ----------

def test_speaking_speed_not_perfectly_determined_by_age_alone():
    """G2-1 audit (CMD_AUDIT_G2.md): truoc fix, speaking_speed = ham THUAN TUY
    cua age_range (3 vung/6 moc = 18 khuon giong, 0 ngoai le tren 139 nguoi) -
    dung thu R195 cam ('bia hang loat bang cong thuc may moc'). Test nay khoa
    cung: voi MOI age_range co >=2 passenger, PHAI co it nhat 2 gia tri
    speaking_speed khac nhau xuat hien - neu ai fill lai bang cong thuc tra-
    thang-age, test nay do ngay."""
    from collections import defaultdict
    real = _real_passengers()
    by_age = defaultdict(set)
    count_by_age = defaultdict(int)
    for p in real:
        age = p.get('age_range', '')
        by_age[age].add((p.get('voice') or {}).get('speaking_speed'))
        count_by_age[age] += 1
    mono = [age for age, speeds in by_age.items() if count_by_age[age] >= 2 and len(speeds) == 1]
    assert not mono, (
        f"age_range sau day co >=2 passenger nhung CHI 1 gia tri speaking_speed "
        f"(nghi cong thuc thuan-age, khong ca tinh hoa that): {mono}")


def test_catchphrase_distinct_within_same_regret_label_group():
    """G2-1 audit: cac hanh khach CUNG 1 regret_label (ban sao procedural cung
    cau chuyen) truoc day co catchphrase CUNG 1 khuon cu phap, chi doi tu vung
    mien. Sau fix: moi nguoi phai co catchphrase RIENG (khong trung y het nhau
    trong cung nhom) - dung death.type/hoan canh rieng lam khung tu su."""
    from collections import defaultdict
    real = _real_passengers()
    by_label = defaultdict(list)
    for p in real:
        by_label[p.get('regret_label')].append(p.get('voice', {}).get('catchphrase'))
    dup_groups = {label: catches for label, catches in by_label.items()
                  if len(catches) >= 2 and len(set(catches)) < len(catches)}
    assert not dup_groups, (
        f"Cac nhom regret_label sau day co >=2 passenger TRUNG catchphrase y het "
        f"nhau (nghi copy-paste khong ca tinh hoa): {list(dup_groups.keys())}")


def test_pronoun_system_not_perfectly_determined_by_region_alone():
    """G2-7 (10/7, per Mr.Long authorization, TASK_AUDIT_HIGH_G2_G8.md — mirror ky
    thuat e079d10/G2-1): truoc fix, pronoun_system = PRON[region] (ham THUAN TUY
    cua region_dialect, dung 3 gia tri co dinh cho ca 139 nguoi, 0 ngoai le). Sau
    fix: ket hop THEM age_range (bien THAT co san) - moi region co >=2 passenger
    o >=2 age bucket khac nhau PHAI co >=2 gia tri pronoun_system khac nhau xuat
    hien - neu ai quay lai cong thuc thuan-region, test nay do ngay."""
    from collections import defaultdict
    real = _real_passengers()
    by_region = defaultdict(set)
    count_by_region = defaultdict(int)
    for p in real:
        region = (p.get('voice') or {}).get('region_dialect')
        by_region[region].add((p.get('voice') or {}).get('pronoun_system'))
        count_by_region[region] += 1
    mono = [r for r, vals in by_region.items() if count_by_region[r] >= 2 and len(vals) == 1]
    assert not mono, (
        f"vung sau day co >=2 passenger nhung CHI 1 gia tri pronoun_system "
        f"(nghi cong thuc thuan-region, khong ca tinh hoa that): {mono}")


def test_particles_not_perfectly_determined_by_region_alone():
    """Doi xung voi test tren, cho particles."""
    from collections import defaultdict
    real = _real_passengers()
    by_region = defaultdict(set)
    count_by_region = defaultdict(int)
    for p in real:
        region = (p.get('voice') or {}).get('region_dialect')
        parts = tuple((p.get('voice') or {}).get('particles') or [])
        by_region[region].add(parts)
        count_by_region[region] += 1
    mono = [r for r, vals in by_region.items() if count_by_region[r] >= 2 and len(vals) == 1]
    assert not mono, (
        f"vung sau day co >=2 passenger nhung CHI 1 gia tri particles "
        f"(nghi cong thuc thuan-region): {mono}")


def test_pronoun_particles_still_valid_per_region_dialect_no_leak():
    """Xac nhan da dang hoa (2 test tren) KHONG gay dialect-leak - moi gia tri
    pronoun_system/particles moi PHAI van nam trong tap HOP LE cua chinh region
    (dialog_voice_validator.py::REGIONS), khong bia tu moi ngoai tap da xac nhan."""
    sys.path.insert(0, str(SVHMP / 'tools'))
    import dialog_voice_validator as dvv
    real = _real_passengers()
    leaks = []
    for p in real:
        voice = p.get('voice') or {}
        region = voice.get('region_dialect')
        if region not in dvv.REGIONS:
            continue
        pronoun = voice.get('pronoun_system')
        if pronoun and pronoun not in dvv.REGIONS[region]['pronouns']:
            leaks.append((p['id'], 'pronoun_system', pronoun, region))
        for part in (voice.get('particles') or []):
            if part not in dvv.REGIONS[region]['particles']:
                leaks.append((p['id'], 'particle', part, region))
    assert not leaks, f"gia tri KHONG nam trong tap hop le cua region (dialect-leak): {leaks}"


def test_mutation_missing_voice_fields_bites():
    p = _mutate(voice={})
    v, w = validate(p, FORBIDDEN)
    missing = [x for x in v if 'voice.' in x]
    assert len(missing) == 3, v   # region_dialect + pronoun_system (VOICE_REQ) + hometown (BACKGROUND_REQ)
    missing_warn = [x for x in w if 'voice.' in x]
    assert len(missing_warn) == 4, w  # speaking_speed + catchphrase + forbidden_words + dialogue_sample


def test_mutation_missing_bible37_voice_warn_fields_bites():
    """G2 B4 fix (5/7): 4 field bible/37 tier_1_mandatory.voice truoc day KHONG
    bao gio duoc check (named != enforced). Thieu 1 minh 'catchphrase' -> PHAI
    bi WARN (truoc fix se KHONG bi flag gi ca vi VOICE_REQ cu chi co 3 field
    khac)."""
    p = _mutate(voice={'region_dialect': 'bac', 'hometown': 'Hà Nội',
                       'pronoun_system': 'tôi', 'speaking_speed': 'cham',
                       'forbidden_words': ['vai'], 'dialogue_sample': 'xin chao'})
    v, w = validate(p, FORBIDDEN)
    assert v == [], v
    assert any('catchphrase' in x for x in w), w
    assert not any(f in ' '.join(w) for f in
                  ('speaking_speed', 'forbidden_words', 'dialogue_sample')), w


def test_bible37_voice_pronoun_style_alias_matches_real_field_pronoun_system():
    """bible/37 khai ten 'pronoun_style' nhung code+data that dung 'pronoun_system'
    — VOICE_FIELD_ALIAS phai map dung, khong duoc lech am tham."""
    from roster_validator import VOICE_FIELD_ALIAS
    assert VOICE_FIELD_ALIAS.get('pronoun_style') == 'pronoun_system'
    bible_voice_fields = BIBLE37['tier_1_mandatory']['voice']
    assert 'pronoun_style' in bible_voice_fields
    assert 'pronoun_system' not in bible_voice_fields  # xac nhan bible dung ten khac data that


def test_bible37_voice_6_fields_all_checked_hard_or_warn():
    """Doi chieu: ca 6 field bible/37 tier_1_mandatory.voice phai duoc check o
    dau do (VOICE_REQ hard hoac VOICE_REQ_WARN), khong duoc bo sot field nao —
    chinh la bug G2 B4 (4/6 field roi khoi enforcement) da duoc fix."""
    from roster_validator import VOICE_REQ, VOICE_REQ_WARN, VOICE_FIELD_ALIAS
    bible_voice_fields = set(BIBLE37['tier_1_mandatory']['voice'])
    checked = set(VOICE_REQ) | set(VOICE_REQ_WARN)
    aliased_bible_fields = {VOICE_FIELD_ALIAS.get(f, f) for f in bible_voice_fields}
    assert aliased_bible_fields == checked, (aliased_bible_fields, checked)


def test_mutation_missing_death_type_bites():
    p = _mutate(death={})
    v, _ = validate(p, FORBIDDEN)
    assert any('death.type' in x for x in v), v


def test_mutation_unknown_region_bites():
    p = _mutate(voice={'region_dialect': 'tay_nguyen_fake', 'hometown': 'Hà Nội',
                       'pronoun_system': 'tôi'})
    v, _ = validate(p, FORBIDDEN)
    assert any('C2' in x and 'tay_nguyen_fake' in x for x in v), v
