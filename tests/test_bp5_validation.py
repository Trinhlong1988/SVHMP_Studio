"""BP5 Validation — certify suite 1-cua (positive + mutation theo TASK_BP5).

Don audit bao truoc: 1 tang con FAIL -> suite exit 1 · go stage khoi ci_gate
-> test unwire do (mirror test_server_side_ci_wired) · dup-key bat ky file
blueprint -> suite do · loader dup-key phai 1 implementation (import, khong
copy-paste 5 ban).

pytest-func FLAT -> collect trong `pytest tests/` va ci_gate.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from blueprint_suite_check import SUITE, run_suite  # noqa: E402
import ci_gate  # noqa: E402

BP2_SPEC = REPO / 'governance' / 'blueprint' / 'bp2' / 'domain_specs.yaml'
BP4_BUS = REPO / 'governance' / 'blueprint' / 'bp4' / 'event_bus.yaml'
SUITE_CLI = REPO / 'tools' / 'blueprint_suite_check.py'


def _run_cli(*args):
    return subprocess.run([sys.executable, str(SUITE_CLI), *args],
                          capture_output=True, text=True, encoding='utf-8')


# ---------- POSITIVE ----------

def test_suite_covers_all_five_layers():
    """Suite phai goi DU 5 tang bp0-bp4, script ton tai that (chong tang ma)."""
    keys = [k for k, _l, _s in SUITE]
    assert keys == ['bp0', 'bp1', 'bp2', 'bp3', 'bp4'], keys
    for _k, _label, rel in SUITE:
        assert (REPO / rel).exists(), f'checker tang thieu tren disk: {rel}'


def _scan_loader_impls(dir_path):
    """Quet cac file *.py co IMPLEMENTATION loader dup-key (def/class top-level).
    Doc utf-8-sig: BOM dau file (van la Python hop le!) tung lam '^def' re.M
    truot match dong 1 -> copy-paste loader kem BOM lot guard (audit BP5 Minor)."""
    hits = []
    for py in sorted(Path(dir_path).glob('*.py')):
        src = py.read_text(encoding='utf-8-sig')
        if re.search(r'^def load_yaml_no_dup\b', src, re.M) or \
           re.search(r'^class _DupKeySafeLoader\b', src, re.M):
            hits.append(py.name)
    return hits


def test_dup_key_loader_single_impl():
    """DUP-KEY loader dung chung: DUNG 1 implementation (constitution_check),
    cac checker con IMPORT — khong copy-paste 5 ban (rang buoc TASK_BP5)."""
    defs = _scan_loader_impls(REPO / 'tools')
    assert defs == ['blueprint_constitution_check.py'], \
        f'loader phai 1 implementation duy nhat, thay: {defs}'
    for name in ['bp1_architecture_check.py', 'bp2_domain_check.py',
                 'bp3_ownership_check.py', 'bp4_runtime_check.py']:
        src = (REPO / 'tools' / name).read_text(encoding='utf-8')
        assert 'from blueprint_constitution_check import load_yaml_no_dup' in src, \
            f'{name} khong import loader dung chung'


def test_mut_loader_copy_with_bom_detected(tmp_path):
    """Neg-test BOM evasion (audit BP5): copy loader vao file MOI co UTF-8 BOM
    dau file — guard PHAI van bat (utf-8-sig strip BOM truoc khi match)."""
    bom_copy = tmp_path / 'sneaky_loader.py'
    bom_copy.write_bytes(b'\xef\xbb\xbf' +
                         'def load_yaml_no_dup(text):\n    return None\n'
                         .encode('utf-8'))
    # tu chung minh don danh dung cho: khong co BOM cung phai bat
    plain_copy = tmp_path / 'plain_loader.py'
    plain_copy.write_text('class _DupKeySafeLoader:\n    pass\n', encoding='utf-8')
    hits = _scan_loader_impls(tmp_path)
    assert 'sneaky_loader.py' in hits, \
        f'BOM evasion khong bi bat — guard thung: {hits}'
    assert 'plain_loader.py' in hits, hits


def test_real_suite_passes():
    """Blueprint that (committed data) phai 5/5 xanh — exit 0 tu 1 lenh."""
    r = _run_cli()
    assert r.returncode == 0, f'suite phai exit 0:\n{r.stdout}\n{r.stderr}'
    assert r.stdout.count('[PASS]') == 5, r.stdout


def test_blueprint_stage_wired_in_ci_gate():
    """Chong unwire (mirror test_server_side_ci_wired): go stage blueprint
    khoi ci_gate CHECKS -> test nay do."""
    assert ('blueprint', 'tools/blueprint_suite_check.py') in ci_gate.CHECKS, \
        'stage blueprint bi go khoi ci_gate CHECKS (unwire!)'


def test_doc_11_elements():
    text = (REPO / 'governance' / 'blueprint' / 'bp5' /
            '00_validation.md').read_text(encoding='utf-8').lower()
    for e in ['mission', 'purpose', 'scope', 'authority', 'responsibilit',
              'workflow', 'mandatory', 'pass', 'fail', 'promotion', 'example']:
        assert e in text, f'doc thieu {e}'


# ---------- MUTATION BATTERY ----------

def _dup_key_mutant(tmp_path, src_file, name):
    """Nhân bản file that + 1 khoa top-level trung (validator_version co san
    o top-level moi file blueprint pack) — dup DUNG cap, tu chung minh can."""
    bad = tmp_path / name
    bad.write_text(src_file.read_text(encoding='utf-8') +
                   '\nvalidator_version: 9.9.9\n', encoding='utf-8')
    return bad


def test_mut_one_layer_fail_suite_exit1(tmp_path):
    """1 tang con FAIL -> suite exit 1, matrix chi ro tang do, tang khac van
    duoc cham (khong short-circuit)."""
    bad = _dup_key_mutant(tmp_path, BP2_SPEC, 'spec_dup.yaml')
    r = _run_cli('--bp2', f'--spec {bad}')
    assert r.returncode == 1, f'suite phai exit 1 khi bp2 do:\n{r.stdout}'
    assert '[FAIL] bp2' in r.stdout, r.stdout
    assert 'DUP-KEY' in r.stdout, f'phai bat dung loi DUP-KEY:\n{r.stdout}'
    assert '[PASS] bp0' in r.stdout and '[PASS] bp1' in r.stdout, \
        f'tang khac phai van chay du matrix:\n{r.stdout}'


def test_mut_dup_key_any_blueprint_file_suite_red(tmp_path):
    """Dup-key o file blueprint tang KHAC (bp4 event_bus) -> suite van do
    (loader dung chung phu moi tang)."""
    bad = _dup_key_mutant(tmp_path, BP4_BUS, 'bus_dup.yaml')
    rows = {row['key']: row for row in run_suite(overrides={'bp4': ['--bus', str(bad)]})}
    assert rows['bp4']['rc'] != 0, 'bp4 phai do voi dup-key'
    assert 'DUP-KEY' in rows['bp4']['tail'], rows['bp4']['tail']
    assert rows['bp0']['rc'] == 0, 'tang khong dinh mutation phai van xanh'
    assert any(row['rc'] != 0 for row in rows.values()), 'suite tong phai FAIL'
