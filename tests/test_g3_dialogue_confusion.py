"""tests/test_g3_dialogue_confusion.py — D5 (TASK_G3_DIALOGUE.md).

Mirror cau truc R206 (bang confusion TP/FN/TN/FP) nhung do HANH VI GENERATOR (dialogue_
generator.py qua DialogueManager) tren >=30 passenger THAT (>=3 vung giong), case sach vs
case co y pha (mutation: xoa field Tier1 / ep region_dialect lech hometown / chen
forbidden_words) - doi chieu voi runtime/dialogue_golden_set.yaml (Nguon A + Nguon B) lam
baseline. Khac R206/R208 (test THANG validator noi bo) - day la test HANH VI GENERATOR
(dialogue_generator.py) o lop tren, xem D6 cross-reference.

PASS = 0 FN + 0 FP. Neu ra 0 FN/0 FP ngay lan dau -> khong tin ngay, phai co >=1 case
pronoun-ambiguity THAT (khong chi dialect/age) - xem test_pronoun_ambiguity_real_case_from_source_b.
"""
import copy
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))

from dialogue_generator import (  # noqa: E402
    generate_line, Tier1IncompleteError, _build_profile_dict, detect_pronoun_issues_in_quote)
from dialogue_manager import DialogueManager  # noqa: E402
import dialog_voice_validator as dvv  # noqa: E402

GOLDEN_PATH = REPO / 'runtime' / 'dialogue_golden_set.yaml'

CM = {'TP': 0, 'FN': 0, 'TN': 0, 'FP': 0}
DETAIL = []


def judge(is_bad, caught, tag):
    if is_bad:
        if caught:
            CM['TP'] += 1
        else:
            CM['FN'] += 1
            DETAIL.append(('FN', tag))
    else:
        if caught:
            CM['FP'] += 1
            DETAIL.append(('FP', tag))
        else:
            CM['TN'] += 1


@pytest.fixture(scope='module')
def dm():
    return DialogueManager()


@pytest.fixture(scope='module')
def golden():
    assert GOLDEN_PATH.exists(), 'D5: runtime/dialogue_golden_set.yaml phai duoc tao truoc'
    return yaml.safe_load(GOLDEN_PATH.read_text(encoding='utf-8'))


@pytest.fixture(scope='module')
def sample_passengers(dm):
    pas = [c for c in dm.registry.all('passenger') if c.assigned_ep]
    by_region = {}
    for c in pas:
        by_region.setdefault(c.voice.region_dialect, []).append(c)
    picked = []
    for r, lst in by_region.items():
        picked.extend(lst[:15])
    assert len(picked) >= 30, f'can >=30 passenger, co {len(picked)}'
    assert len({c.voice.region_dialect for c in picked}) >= 3
    return picked


# ---------- Golden set structure sanity (tach bach nguon, khong tron nhan) ----------

def test_golden_set_sources_separated_not_mixed(golden):
    a = golden['source_a_synthetic_r206']
    b = golden['source_b_real_mined']
    assert a['count'] == 500 == len(a['entries'])
    assert all(e['source'] == 'synthetic_r206' for e in a['entries'])
    assert len(b['correct_cases']) == 2
    assert len(b['incorrect_cases']) > 0, ('D5: neu 1 nhanh Nguon B ra 0 case phai ghi ro trong '
                                           'report, khong duoc xay ra am tham - hien tai phai >0')
    for e in b['incorrect_cases']:
        assert 'source' in e and 'ep=' in e['source'], 'M10: entry Nguon B phai co ep:line evidence'


def test_golden_set_source_b_never_touches_bible31(golden):
    """D1B Phan B: VI PHAM KIEN TRUC THAT (dialogue/narrative khong duoc depend audio/
    presentation) - CAC ENTRY DU LIEU (khong phai chu thich meta) KHONG duoc lay tu bible/31
    duoi bat ky hinh thuc nao."""
    def _flat_values(node):
        if isinstance(node, dict):
            for v in node.values():
                yield from _flat_values(v)
        elif isinstance(node, list):
            for v in node:
                yield from _flat_values(v)
        elif isinstance(node, str):
            yield node

    for key in ('source_a_synthetic_r206', 'source_b_real_mined'):
        for v in _flat_values(golden[key]):
            assert 'bible/31' not in v and '31_golden_samples' not in v, (
                f"D1B Phan B vi pham: entry du lieu {key} nhac bible/31: {v!r}")


# ---------- Nguon A lam baseline (doi chieu, khong lap lai het R206 - chi sanity) ----------

def test_source_a_lines_stay_clean_against_real_validator(golden):
    for e in golden['source_a_synthetic_r206']['entries'][:50]:
        profile = {'region_dialect': e['region'], 'hometown': e['hometown'], 'pronoun_system': 'con'}
        issues = dvv.validate_line(profile, e['line'])
        judge(is_bad=False, caught=bool(issues), tag=f"sourceA_clean_{e['index']}")
    assert CM['FP'] == 0


# ---------- >=30 passenger that x case sach ----------

def test_clean_generation_30plus_passengers_3_regions(dm, sample_passengers):
    for c in sample_passengers:
        r = generate_line(c.id, {'emotion_beat': 'nhớ nhà', 'listener_call': 'Mẹ ơi'}, dm)
        judge(is_bad=False, caught=(r['status'] != 'OK'), tag=f"clean_{c.id}")
    assert CM['FP'] == 0, f"case sach bi bat nham: {[d for d in DETAIL if d[0]=='FP']}"


# ---------- Mutation 1: xoa field Tier1 (region_dialect) ----------

def test_mutation_missing_tier1_field_caught(dm, sample_passengers, tmp_path):
    for c in sample_passengers[:10]:
        bad = copy.deepcopy(c)
        bad.voice.region_dialect = ''
        bad.id = f'TESTM1_{c.id}'
        dm.registry.chars[bad.id] = bad
        try:
            caught = False
            try:
                generate_line(bad.id, {}, dm, missing_report_path=tmp_path / 'm.md')
            except Tier1IncompleteError:
                caught = True
            judge(is_bad=True, caught=caught, tag=f"m1_missing_tier1_{c.id}")
        finally:
            del dm.registry.chars[bad.id]
    assert CM['FN'] == 0


# ---------- Mutation 2: ep region_dialect lech hometown ----------

def test_mutation_region_hometown_mismatch_caught(dm, sample_passengers, tmp_path):
    other_region = {'bac': 'nam', 'trung': 'bac', 'nam': 'trung'}
    for c in sample_passengers[:10]:
        bad = copy.deepcopy(c)
        bad.voice.region_dialect = other_region.get(c.voice.region_dialect, 'bac')
        bad.id = f'TESTM2_{c.id}'
        dm.registry.chars[bad.id] = bad
        try:
            r = generate_line(bad.id, {}, dm, missing_report_path=tmp_path / 'm.md')
            caught = r['status'] == 'REFUSED' and any(
                i['code'] == 'HOMETOWN_REGION_MISMATCH' for i in r.get('issues', []))
            judge(is_bad=True, caught=caught, tag=f"m2_region_mismatch_{c.id}")
        finally:
            del dm.registry.chars[bad.id]
    assert CM['FN'] == 0


# ---------- Mutation 3: chen forbidden_words (o lop profile-dict/buoc3 that - PHAN BIEN
# #7: CharacterProfile dataclass chua giu field nay tu roster, nen mutation nay kiem truc
# tiep _build_profile_dict + dvv.validate_line THAT, khong qua duoc full CharacterRegistry) ----------

def test_mutation_forbidden_word_inserted_caught():
    for region, ban_word, bad_line in (
            ('bac', 'vãi', 'Thôi vãi cả người.'),
            ('trung', 'đm', 'Răng mà đm rứa.'),
            ('nam', 'chửi', 'Con chửi rồi đó.')):
        voice_profile = {'region_dialect': region, 'hometown': '', 'pronoun_system': 'con',
                          'particles': [], 'forbidden_words': [ban_word]}
        profile, _missing = _build_profile_dict(voice_profile)
        issues = dvv.validate_line(profile, bad_line)
        caught = any(i['code'] == 'FORBIDDEN_WORD' for i in issues)
        judge(is_bad=True, caught=caught, tag=f"m3_forbidden_{region}")
    assert CM['FN'] == 0


# ---------- REALITY ANCHOR D5: >=1 case pronoun-ambiguity THAT (khong chi dialect/age) ----------

def test_pronoun_ambiguity_real_case_from_source_b(golden):
    """Neu 0 case dang nay bat duoc gi -> nghi adapter D3 buoc 4 chua noi dung (TASK D5
    'Cach bat loi'). Dung THAT sample_issues severity HIGH tu audit_dialogue_hierarchy_
    report.json (R48) - khong tu bia cau mau."""
    incorrect = golden['source_b_real_mined']['incorrect_cases']
    assert incorrect, 'Nguon B incorrect_cases rong - khong the kiem pronoun-ambiguity that'
    n_caught = 0
    for case in incorrect:
        issues = detect_pronoun_issues_in_quote(case['sample'])
        high = [i for i in issues if i.get('severity') == 'HIGH']
        caught = bool(high)
        judge(is_bad=True, caught=caught, tag=f"sourceB_pronoun_ep{case['ep']}")
        if caught:
            n_caught += 1
    assert n_caught >= 1, ('0 case pronoun-ambiguity that duoc bat lai — nghi adapter D3 '
                           'buoc 4 chua noi dung that (TASK D5 REALITY ANCHOR)')


def test_source_b_correct_lock_lines_passthrough_not_flagged(dm):
    from audit_driver_dialogue_context import Q1_VARIANTS, Q2_VARIANTS
    r1 = generate_line('CHAR_DRIVER', {'driver_target': 'Q1'}, dm)
    judge(is_bad=False, caught=(r1['status'] != 'RECURRING_PASSTHROUGH' or r1['line'] != Q1_VARIANTS[0]),
          tag='sourceB_q1_correct')
    r2 = generate_line('CHAR_DRIVER',
                        {'driver_target': 'Q2', 'driver_trigger_window': ['Bao giờ con mới nhớ ra?']}, dm)
    judge(is_bad=False, caught=(r2['status'] != 'RECURRING_PASSTHROUGH' or r2['line'] != Q2_VARIANTS[0]),
          tag='sourceB_q2_correct')
    assert CM['FP'] == 0


# ---------- Tong ket cuoi cung (chay sau, dung order alphabet trong file -> dat cuoi bang ten) ----------

def test_zz_confusion_matrix_0fn_0fp_final():
    print(f"\n=== D5 CONFUSION MATRIX (dialogue_generator.py) ===")
    print(f"  TP={CM['TP']} FN={CM['FN']} TN={CM['TN']} FP={CM['FP']}")
    if DETAIL:
        for k, t in DETAIL[:20]:
            print(f"  !!! {k}: {t}")
    assert CM['FN'] == 0, f"False Negative: {[d for d in DETAIL if d[0]=='FN']}"
    assert CM['FP'] == 0, f"False Positive: {[d for d in DETAIL if d[0]=='FP']}"
