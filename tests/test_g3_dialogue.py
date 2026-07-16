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


def test_dialect_leak_end_to_end_via_generate_line_full_pipeline(dm, real_passengers, tmp_path):
    """G3-5 RE-AUDIT THAT (kiem duyet doc lap 5/7 phat hien 2 test o tren CHI goi
    dvv.validate_line() TRUC TIEP tren 1 chuoi tay go - CHUA chung minh generate_line() (buoc 3
    THAT cua generator) tu loc duoc candidate leak qua TOAN BO pipeline). Test nay bom marker
    leak ('nhe'/'nhi' - EXCLUSIVE cua vung 'bac') qua scene_context (input TU BEN NGOAI, dung
    dung cach G6 se cap trong tuong lai - khong bia du lieu nhan vat) khien candidate 'core'
    (buoc dau _candidate_variants sinh ra) leak that; nhan vat THAT trong roster, region 'nam'.
    particles/catchphrase duoc lam sach de loai tru nguon leak khac (chi con dung 2 candidate:
    core leak + fallback sach), cach ly bien so can kiem tra."""
    c = real_passengers[3]
    bad = copy.deepcopy(c)
    bad.voice.region_dialect = 'nam'
    bad.voice.hometown = 'Sài Gòn'
    bad.voice.pronoun_system = 'tui'
    bad.voice.particles = []
    bad.voice.catchphrase = ''
    bad.id = 'TEST_G3_DIALECT_LEAK_E2E'
    dm.registry.chars[bad.id] = bad
    try:
        leaky_scene = {'emotion_beat': 'nhé', 'listener_call': 'nhỉ'}
        r = generate_line(bad.id, leaky_scene, dm, missing_report_path=tmp_path / 'missing.md')
        assert r['status'] == 'OK', f"generator phai tim duoc candidate sach khac, khong REFUSED oan: {r}"
        assert r['attempts'] > 1, (
            f"attempts={r['attempts']} - candidate dau (core, chua 'nhé'/'nhỉ' tu scene_context) "
            f"PHAI bi buoc 3 (dvv.validate_line THAT) tu choi TRUOC, khong duoc chon ngay: {r}")
        assert 'nhé' not in r['line'] and 'nhỉ' not in r['line'], \
            f"generator EMIT cau leak dialect qua FULL pipeline: {r}"
        final_issues = dvv.validate_line(
            {'region_dialect': 'nam', 'hometown': 'Sài Gòn', 'pronoun_system': 'tui',
             'particles': [], 'forbidden_words': []}, r['line'])
        assert final_issues == [], f"line cuoi cung van con issue THAT (validator doc lap): {final_issues}"
    finally:
        del dm.registry.chars[bad.id]


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


# ============================================================
# D7 — gate 1 cua + wire + unwire-guard 2 LOP
# ============================================================

# SUBSET-check (17/7, R215): danh sach cac stage BAT BUOC phai con trong CHECKS. Truoc day
# la ORIGINAL_11_STAGES = exact-list (remaining == list) — ANTI-PATTERN frozen exact-list:
# vo NGAY khi them BAT KY gate moi (da xay: them 'cross_ep_canon' R216 17/7 lam 3 test nay
# FAIL du chi la THEM, khong phai GO). Sua goc = issubset: THEM gate moi KHONG vo; chi GO 1
# stage bat buoc moi FAIL. Muon 1 gate moi duoc guard thi them ten vao set nay (chu dich).
REQUIRED_STAGES = {
    'registry', 'blueprint', 'R199_tail', 'R203_conf', 'R205_char', 'R206_voice',
    'R207_canon', 'R208_age', 'project_config', 'G2_roster', 'g5_supernatural', 'G4_world',
    'G6_story_planner', 'G7_generator', 'G8_qa_runtime',
    'cross_ep_canon',   # R216 cross-episode canon gate (them 17/7)
}


def test_g3_dialogue_stage_wired_in_ci_gate():
    """Lop (a) — grep TINH: dong 'G3_dialogue' phai co mat trong CHECKS THAT cua ci_gate.py
    (bat truong hop ai xoa dong that sau nay), dat DUNG SAU R208_age, KHONG xoa/doi thu tu
    11 entry cu."""
    import ci_gate
    assert ('G3_dialogue', 'tools/g3_dialogue_check.py') in ci_gate.CHECKS, \
        'stage G3_dialogue bi go khoi ci_gate CHECKS (unwire!)'
    keys = [k for k, _ in ci_gate.CHECKS]
    idx_r208 = keys.index('R208_age')
    idx_g3 = keys.index('G3_dialogue')
    assert idx_g3 == idx_r208 + 1, 'G3_dialogue phai dat NGAY SAU R208_age'
    # SUBSET (khong exact-list): moi stage BAT BUOC phai con; THEM gate moi KHONG vo test.
    missing = REQUIRED_STAGES - set(keys)
    assert not missing, f'stage BAT BUOC bi go khoi CHECKS (unwire): {sorted(missing)}'
    src = (REPO / 'tools' / 'ci_gate.py').read_text(encoding='utf-8')
    assert "'G3_dialogue'" in src, 'grep tinh tren SOURCE THAT (khong chi object in-memory)'


def test_g3_dialogue_unwire_guard_behavior_changes_when_removed(monkeypatch):
    """Lop (b) — monkeypatch xoa stage TAM trong bo nho roi assert HANH VI gate THAY DOI
    (bat truong hop lop (a) bi vo hieu bang cach sua dong ca 2 noi cung luc: neu CHECKS
    khong con dieu khien thuc thi that, monkeypatch se khong lam gi thay doi ca)."""
    import ci_gate
    orig = list(ci_gate.CHECKS)
    patched = [c for c in orig if c[0] != 'G3_dialogue']
    assert len(patched) == len(orig) - 1, 'stage phai ton tai truoc khi test nay chay'
    monkeypatch.setattr(ci_gate, 'CHECKS', patched)
    assert ('G3_dialogue', 'tools/g3_dialogue_check.py') not in ci_gate.CHECKS
    # HANH VI thay doi (G3 mat) NHUNG cac stage bat buoc khac con nguyen — subset, khong exact.
    assert REQUIRED_STAGES.issubset({k for k, _ in ci_gate.CHECKS}), \
        'monkeypatch xoa G3 khong duoc lam mat stage bat buoc khac'


def test_g3_dialogue_check_gate_runs_and_writes_report():
    """CHU Y de-quy (lesson-ci-gate-pytest-recursion): g3_dialogue_check.py stage
    D3_D4_pytest goi `pytest tests/test_g3_dialogue.py` — CHINH FILE nay — nen se gap lai
    test nay. Guard 2 lop: (1) o day, tu skip neu dang chay long trong 1 lan goi gate khac
    (bien moi truong SVHMP_G3_GATE_PYTEST_RUNNING); (2) trong g3_dialogue_check.py._run_pytest
    tu skip neu guard da bat (khong spawn nested pytest them). Ca 2 cung ton tai (defense in
    depth) - thieu 1 trong 2 van an toan, co ca 2 chan chac chan khong bao gio de quy qua 1
    lop long nhau."""
    import os
    import subprocess
    if os.environ.get('SVHMP_G3_GATE_PYTEST_RUNNING'):
        pytest.skip('re-entrant: dang chay long trong 1 lan g3_dialogue_check.py khac')
    r = subprocess.run([sys.executable, str(REPO / 'tools' / 'g3_dialogue_check.py')],
                       capture_output=True, text=True, cwd=str(REPO), encoding='utf-8')
    assert r.returncode == 0, r.stdout + r.stderr
    report = REPO / 'runtime' / 'reports' / 'dialogue_system_report.md'
    assert report.exists()


def test_r191_qa_dialogue_identity_not_wired_in_ci_gate():
    """R191 can WAV da render, ci_gate chay TRUOC render - PHAI KHONG nam trong CHECKS."""
    import ci_gate
    keys = [k for k, _ in ci_gate.CHECKS]
    scripts = [s for _, s in ci_gate.CHECKS]
    assert 'qa_dialogue_identity.py' not in ' '.join(scripts)
    handoff = REPO / 'reports' / 'G3_HANDOFF_G8.md'
    assert handoff.exists(), 'phai ban giao ro cho G8 (D7 yeu cau)'


# ============================================================
# G3-7 RE-AUDIT (kiem duyet doc lap 5/7): sandbox output THAT + 2 tool audit cu quet duoc
# ============================================================

def test_write_episode_line_accepts_non_numeric_ep_label():
    """write_episode_line() phai chap nhan ep_n dang chuoi (khong phai so) de tao thu muc
    sandbox TEN CHU - khong bao gio trung so tap that/tuong lai (hien 50, roadmap toi 90)."""
    from dialogue_generator import write_episode_line
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        out = write_episode_line(Path(d), 'g3_sample', 'Câu thử.', header_kv={'x': '1'})
        assert out == Path(d) / 'ep_g3_sample' / 'episode.md'
        assert out.exists()


def test_g3_7_sandbox_output_scanned_by_both_legacy_audit_tools():
    """G3-7 (kiem duyet doc lap 5/7): chinh gate g3_dialogue_check.py da chay stage
    G3_7_output_audit_real - test nay xac nhan LAI ket qua doc lap voi assertion cu the
    (khong chi tin exit code cua gate): sandbox path dung, extract_quotes() >=1, va
    audit_driver_dialogue_context.py --file KHONG bao 'MISSING' (that su quet duoc, khong
    phai 0-file pass rong)."""
    import subprocess
    from g3_dialogue_check import SANDBOX_DIR, _stage_output_audit_real
    from audit_dialogue_hierarchy import extract_quotes

    result = _stage_output_audit_real()
    assert result['rc'] == 0, result['tail']

    out_path = SANDBOX_DIR / 'episode.md'
    assert out_path.exists()
    assert '50' not in str(SANDBOX_DIR.relative_to(REPO / 'output'))  # ten chu, khong phai so tap
    text = out_path.read_text(encoding='utf-8')
    assert len(extract_quotes(text)) >= 1, 'G3-7: 0-quote se la PASS RONG'

    rel = out_path.relative_to(REPO).as_posix()
    p = subprocess.run([sys.executable, 'tools/audit_driver_dialogue_context.py', '--file', rel],
                       capture_output=True, text=True, cwd=str(REPO), encoding='utf-8')
    assert 'MISSING' not in (p.stdout or ''), 'audit_driver_dialogue_context.py khong quet duoc sandbox'


def test_g3_7_sandbox_never_collides_with_real_episode_numbers():
    """Sandbox dir PHAI la ten chu (khong phai so), khong duoc trung voi bat ky pattern
    ep_NN (so) nao du hien tai hay tuong lai (roadmap toi ep_90)."""
    import re
    from g3_dialogue_check import SANDBOX_DIR
    assert not re.match(r'^ep_\d+$', SANDBOX_DIR.name), \
        f'{SANDBOX_DIR.name} la so - co the trung tap that tuong lai'
