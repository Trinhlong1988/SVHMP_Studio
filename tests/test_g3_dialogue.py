"""tests/test_g3_dialogue.py — D3/D4/D7 (TASK_G3_DIALOGUE.md).

D3: dialogue_generator.py chay sinh THAT tren roster that (>=10 passenger da vung),
Tier1-completeness gate, dialect-leak/hometown-mismatch reject qua validator that (khong
viet lai logic - import + goi 3 tool cu), recurring driver refuse/pass-through dung R174.
D4: validate_generated_batch() moi trong dialog_voice_validator.py (KHONG phai file moi).
D7: unwire-guard 2 lop cho stage G3_dialogue trong ci_gate.CHECKS (them o cuoi file khi
D7 wire xong).
"""
import copy
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))

from dialogue_generator import (  # noqa: E402
    generate_line, write_episode_line, Tier1IncompleteError, OPTIONAL_VOICE_FIELDS)
from dialogue_manager import DialogueManager  # noqa: E402
import dialog_voice_validator as dvv  # noqa: E402
from audit_dialogue_hierarchy import extract_quotes  # noqa: E402


@pytest.fixture(scope='module')
def dm():
    return DialogueManager()


@pytest.fixture(scope='module')
def real_passengers(dm):
    return [c for c in dm.registry.all('passenger') if c.assigned_ep]


# ---------- D3 REALITY ANCHOR: sinh that tren >=10 passenger da vung ----------

def test_generate_line_real_10plus_passengers_multi_region(dm, real_passengers):
    sample = real_passengers[:30]
    assert len(sample) >= 10
    regions_seen = set()
    ok_count = 0
    for c in sample:
        r = generate_line(c.id, {'emotion_beat': 'nhớ nhà đã lâu', 'listener_call': 'Mẹ ơi'}, dm)
        regions_seen.add(c.voice.region_dialect)
        if r['status'] == 'OK':
            ok_count += 1
            assert r['line']
            # buoc 3 that: cau sinh ra khong duoc co issue con lai
            assert dvv.validate_line(
                {'region_dialect': c.voice.region_dialect, 'hometown': c.voice.hometown,
                 'pronoun_system': c.voice.pronoun_system, 'particles': c.voice.particles,
                 'forbidden_words': []}, r['line']) == []
    assert len(regions_seen) >= 3, f"chi thay {regions_seen} vung — can da vung that"
    assert ok_count >= 10


def test_generate_line_logs_missing_optional_fields_no_placeholder(dm, real_passengers):
    """PHAN BIEN #7: field roster con thieu (catchphrase/forbidden_words/dialogue_sample/
    speaking_speed) phai duoc SKIP + log, KHONG bia placeholder vao line/output."""
    c = real_passengers[0]
    r = generate_line(c.id, {}, dm)
    assert set(r['missing_optional_fields']) <= set(OPTIONAL_VOICE_FIELDS)
    report = REPO / 'reports' / 'G3_MISSING_VOICE_FIELDS.md'
    assert report.exists(), 'D3 buoc 2 phai ghi log field thieu'
    text = report.read_text(encoding='utf-8')
    assert c.id in text


# ---------- D3 buoc 1: Tier1-completeness gate (dung MANDATORY_VOICE THAT cua dvv) ----------

def test_tier1_incomplete_raises(dm, real_passengers, tmp_path):
    c = real_passengers[0]
    bad = copy.deepcopy(c)
    bad.voice.region_dialect = ''
    bad.id = 'TEST_G3_TIER1_MISSING'
    dm.registry.chars[bad.id] = bad
    try:
        with pytest.raises(Tier1IncompleteError):
            generate_line(bad.id, {}, dm, missing_report_path=tmp_path / 'missing.md')
    finally:
        del dm.registry.chars[bad.id]


# ---------- D3 buoc 3: validator that chan profile sai (region<->hometown lech) ----------

def test_hometown_region_mismatch_blocks_via_real_validator(dm, real_passengers, tmp_path):
    c = real_passengers[1]
    bad = copy.deepcopy(c)
    bad.voice.hometown = 'Hà Nội'
    bad.voice.region_dialect = 'nam'
    bad.id = 'TEST_G3_HOMETOWN_MISMATCH'
    dm.registry.chars[bad.id] = bad
    try:
        r = generate_line(bad.id, {}, dm, missing_report_path=tmp_path / 'missing.md')
        assert r['status'] == 'REFUSED'
        assert r['reason'] == 'PROFILE_INVALID'
        assert any(i['code'] == 'HOMETOWN_REGION_MISMATCH' for i in r['issues'])
    finally:
        del dm.registry.chars[bad.id]


def test_forbidden_word_direct_call_confirms_step3_uses_live_function():
    """PHAN BIEN #7: CharacterProfile.voice (dataclass) KHONG co field forbidden_words nen
    pipeline sinh qua roster that hien tai KHONG the truyen forbidden_words that (no du lieu
    G2, generator KHONG tu bia). Kiem truc tiep dvv.validate_line() — ham THAT ma buoc 3 cua
    dialogue_generator goi — van bat dung FORBIDDEN_WORD khi co du lieu, chung minh buoc 3
    goi ham song, khong phai stub chet."""
    issues = dvv.validate_line({'region_dialect': 'nam', 'forbidden_words': ['vãi']},
                                'Thôi vãi cả người.')
    assert any(i['code'] == 'FORBIDDEN_WORD' for i in issues)


def test_dialect_leak_blocks_via_real_validator_direct_call():
    """Doi TASK M1/G3-5: cau leak marker doc quyen vung khac phai bi dvv.validate_line bat -
    xac nhan ham THAT dialogue_generator goi (khong phai stub)."""
    profile = {'region_dialect': 'nam', 'hometown': 'Sài Gòn', 'pronoun_system': 'tui'}
    issues = dvv.validate_line(profile, 'Con về nhé mẹ.')  # 'nhé' doc quyen 'bac'
    assert any(i['code'] == 'DIALECT_LEAK' for i in issues)


# ---------- D3 buoc 4: adapter pronoun-ambiguity (PHAN BIEN #2) ----------

def test_pronoun_adapter_calls_real_detector_directly():
    """Xac nhan dialogue_generator dung DUNG ham that (khong copy VN_NAMES/logic rieng)."""
    from dialogue_generator import detect_pronoun_issues_in_quote as adapter_fn
    from audit_dialogue_hierarchy import detect_pronoun_issues_in_quote as real_fn
    assert adapter_fn is real_fn, 'D3 phai IMPORT THAT ham nay, khong viet lai (R211/PHAN BIEN #2)'


# ---------- D3 buoc 5: recurring (Bac tai/Nam) refuse/passthrough dung R174 ----------

def test_recurring_default_refuses(dm):
    r = generate_line('CHAR_DRIVER', {}, dm)
    assert r['status'] == 'RECURRING_REFUSED'


def test_recurring_q1_passthrough_literal_no_paraphrase(dm):
    from audit_driver_dialogue_context import Q1_VARIANTS
    r = generate_line('CHAR_DRIVER', {'driver_target': 'Q1'}, dm)
    assert r['status'] == 'RECURRING_PASSTHROUGH'
    assert r['line'] == Q1_VARIANTS[0], 'PHAI nguyen van, cam paraphrase (M3)'


def test_recurring_q2_requires_trigger_window(dm):
    r_no_trigger = generate_line(
        'CHAR_DRIVER', {'driver_target': 'Q2', 'driver_trigger_window': ['Trời đẹp quá.']}, dm)
    assert r_no_trigger['status'] == 'RECURRING_REFUSED'
    r_trigger = generate_line(
        'CHAR_DRIVER',
        {'driver_target': 'Q2', 'driver_trigger_window': ['Bao giờ con mới nhớ ra?']}, dm)
    assert r_trigger['status'] == 'RECURRING_PASSTHROUGH'


# ---------- D3 buoc 6: write_episode_line dung format extract_quotes() quet duoc ----------

def test_write_episode_line_extractable(tmp_path):
    out = write_episode_line(tmp_path, 1, 'Con về nhé mẹ.')
    text = out.read_text(encoding='utf-8')
    quotes = extract_quotes(text)
    assert any(q == 'Con về nhé mẹ.' for q, _ in quotes)


# ---------- D3 buoc 7: khong import production/publisher ----------

def test_no_production_publisher_import():
    """Grep THAT dong import (khong bat nham docstring nhac ten mien - chi khop cu phap
    'import X'/'from X import' o dau dong)."""
    import re
    pat = re.compile(r'^\s*(import|from)\s+(production|publisher)\b', re.MULTILINE)
    for f in ('dialogue_generator.py', 'dialogue_manager.py'):
        src = (REPO / 'tools' / f).read_text(encoding='utf-8')
        assert not pat.search(src), f'{f} vi pham PHAN BIEN #9/forbidden_dependencies'


# ============================================================
# D4 — wiring evidence + validate_generated_batch (them VAO dialog_voice_validator.py,
# KHONG phai file moi trung pham vi)
# ============================================================

def test_d4_generator_imports_and_calls_real_validators_grep_evidence():
    """D4 bang chung bat buoc: grep -n 'dialog_voice_validator\\|audit_dialogue_hierarchy'
    tools/dialogue_generator.py phai thay IMPORT + CALL that (khong phai comment)."""
    import re
    src = (REPO / 'tools' / 'dialogue_generator.py').read_text(encoding='utf-8')
    assert re.search(r'^\s*import dialog_voice_validator', src, re.MULTILINE)
    assert re.search(r'\bdvv\.(validate_profile|validate_line)\(', src)
    assert re.search(r'^\s*from audit_dialogue_hierarchy import detect_pronoun_issues_in_quote',
                      src, re.MULTILINE)
    assert re.search(r'\bdetect_pronoun_issues_in_quote\(', src)


def test_d4_validate_generated_batch_added_to_existing_validator_not_new_file():
    """D4: validate_generated_batch() phai nam TRONG dialog_voice_validator.py (khong phai
    file dialect_validator/dialogue_validator moi nao khac)."""
    assert hasattr(dvv, 'validate_generated_batch')
    assert dvv.validate_generated_batch.__module__ == 'dialog_voice_validator'


def test_d4_validate_generated_batch_catches_leak_and_passes_clean():
    profile = {'region_dialect': 'nam', 'hometown': 'Sài Gòn', 'pronoun_system': 'tui'}
    lines = ['Con dìa nghen.', 'Con về nhé mẹ.']  # dong 2 leak marker 'bac'
    result = dvv.validate_generated_batch(profile, lines)
    assert result['total'] == 2
    assert result['ok'] == 1
    assert result['failed'] == 1
    assert any(i['code'] == 'DIALECT_LEAK' for i in result['results'][1]['issues'])


def test_d4_no_new_file_duplicating_validator_scope():
    """Review-bang-may: khong co file ten chua 'dialect_validator'/'dialogue_validator'
    (khac dialog_voice_validator.py that) trong tools/."""
    tools_dir = REPO / 'tools'
    offenders = [p.name for p in tools_dir.glob('*.py')
                 if ('dialect_validator' in p.name or 'dialogue_validator' in p.name)]
    assert offenders == [], f'R211: file trung pham vi validator: {offenders}'
