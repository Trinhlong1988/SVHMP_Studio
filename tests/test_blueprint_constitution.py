"""SYSTEM_BLUEPRINT_CONSTITUTION v1.0 — certify (positive + 9 negative bat buoc).

Negative test = chung minh checker KHONG phai weak-verifier: moi lop vi pham
theo AUDIT.md phai lam tools/blueprint_constitution_check.py FAIL that su.
Mutate deep-copy cua contract THAT roi assert check() tra vi pham dung lop
(khong subprocess de nhanh + khong phu thuoc cwd; CLI exit-code co test rieng).

pytest-func -> tu dong collect trong `pytest tests/` va ci_gate.
"""
import copy
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from blueprint_constitution_check import check, REQUIRED_DOMAINS, REQUIRED_MEMORY  # noqa: E402

BP = REPO / 'governance' / 'blueprint'
CONTRACT = BP / 'blueprint_domains.yaml'
DOCS = ['00_system_blueprint_constitution.md', '01_required_documents.md',
        '02_domain_contract.md', '03_dependency_rules.md', '04_blueprint_audit_gate.md']


def load():
    return yaml.safe_load(CONTRACT.read_text(encoding='utf-8'))


# ---------- POSITIVE ----------

def test_real_contract_passes():
    assert check(load()) == [], 'contract that phai 0 vi pham'


def test_cli_exit_codes():
    """Gate that: CLI exit 0 tren contract that (chay bang sys.executable)."""
    r = subprocess.run([sys.executable, str(REPO / 'tools' / 'blueprint_constitution_check.py')],
                       capture_output=True, text=True, encoding='utf-8')
    assert r.returncode == 0, f'CLI phai exit 0: {r.stdout}\n{r.stderr}'


def test_all_14_domains_declared():
    data = load()
    assert set(REQUIRED_DOMAINS) <= set(data['domains']), 'contract thieu domain bat buoc'
    assert len(REQUIRED_DOMAINS) == 14


def test_blueprint_docs_exist_nonempty():
    for name in DOCS:
        p = BP / name
        assert p.exists(), f'blueprint doc missing: {name}'
        assert p.stat().st_size > 0, f'blueprint doc empty: {name}'


def test_promotion_is_candidate_not_locked_by_builder():
    """Builder giu candidate — yaml khong duoc mang locked khi registry chua ky."""
    assert load()['meta']['promotion_status'] == 'candidate'


# ---------- 9 NEGATIVE BAT BUOC (AUDIT.md) ----------

def _assert_fails(data, needle):
    errs = check(data)
    assert errs, f'checker phai FAIL (mong bat: {needle})'
    assert any(needle in e for e in errs), f'khong thay vi pham {needle!r} trong: {errs}'


def test_neg1_missing_required_domain_fails():
    data = load()
    del data['domains']['timeline']
    _assert_fails(data, 'THIEU domain bat buoc: timeline')


def test_neg2_missing_manager_fails():
    data = load()
    del data['domains']['character']['manager']
    _assert_fails(data, 'character: THIEU field manager')


def test_neg3_missing_schema_fails():
    data = load()
    data['domains']['audio']['schema'] = None
    _assert_fails(data, 'audio: field schema RONG')


def test_neg4_missing_validator_fails():
    data = load()
    del data['domains']['qa_runtime']['validator']
    _assert_fails(data, 'qa_runtime: THIEU field validator')


def test_neg5_wrong_dependency_direction_fails():
    data = load()
    data['domains']['character']['dependencies'] = ['generator']  # L2 dep L5
    _assert_fails(data, 'SAI HUONG')


def test_neg6_supernatural_merged_into_world_fails():
    data = load()
    # ca 2 kieu gop: world nuot supernatural / supernatural khai sub_of world
    d1 = copy.deepcopy(data)
    d1['domains']['world']['contains'] = ['supernatural']
    _assert_fails(d1, 'contains supernatural')
    d2 = copy.deepcopy(data)
    d2['domains']['supernatural']['sub_of'] = 'world'
    _assert_fails(d2, 'DOC LAP')


def test_neg7_memory_without_owner_fails():
    data = load()
    del data['memory']['event_memory']['owner']
    _assert_fails(data, 'KHONG co owner')


def test_neg8_candidate_self_locked_fails():
    """Builder tu doi yaml sang locked ma registry chua ky -> FAIL."""
    data = load()
    data['meta']['promotion_status'] = 'locked'
    _assert_fails(data, 'SELF-LOCK')


def test_neg9_missing_audit_gate_fails():
    data = load()
    data['domains']['production']['audit_rule'] = ''
    _assert_fails(data, 'production: field audit_rule RONG')


# ---------- CHONG PHANTOM + CHONG PASS-RONG ----------

def test_phantom_exists_path_fails():
    """Khai exists cho path khong ton tai = khai lao/phantom -> FAIL (lesson built!=wired)."""
    data = load()
    data['domains']['world']['manager'] = {'path': 'tools/khong_ton_tai_dau.py',
                                           'status': 'exists'}
    _assert_fails(data, 'phantom')


def test_planned_with_full_metadata_does_not_fail():
    """Rule 1: KHONG FAIL vi planned (du 5 metadata) — trung thuc, cam ep stub."""
    data = load()
    data['domains']['video']['manager'] = {
        'status': 'planned', 'planned_path': 'tools/chua_he_ton_tai.py',
        'owner': 'video', 'reason_not_exists_yet': 'chua khoi cong',
        'target_milestone': 'M4_video_publisher', 'blocking_dependency': 'R196'}
    assert check(data) == [], 'planned du metadata khong duoc lam checker FAIL'


def test_neg10_planned_missing_metadata_fails():
    """PLANNED HONESTY RULE: planned thieu bat ky metadata nao -> FAIL."""
    for missing in ('planned_path', 'owner', 'reason_not_exists_yet',
                    'target_milestone', 'blocking_dependency'):
        data = load()
        ref = {'status': 'planned', 'planned_path': 'tools/x.py', 'owner': 'video',
               'reason_not_exists_yet': 'r', 'target_milestone': 'M4_video_publisher',
               'blocking_dependency': 'b'}
        del ref[missing]
        data['domains']['video']['manager'] = ref
        _assert_fails(data, f'thieu metadata {missing}')


def test_neg11_planned_bogus_milestone_fails():
    """target_milestone phai nam trong milestones map — chong milestone bia."""
    data = load()
    data['domains']['video']['manager']['target_milestone'] = 'M99_khong_ton_tai'
    _assert_fails(data, 'khong co trong milestones')


def test_all_exists_refs_truly_on_disk():
    """Khong pass rong: contract that phai co >=15 ref exists va TAT CA ton tai."""
    data = load()
    n = 0
    for d in data['domains'].values():
        refs = list(d.get('source_of_truth') or [])
        refs += [d[f] for f in ('manager', 'schema', 'validator') if isinstance(d.get(f), dict)]
        for ref in refs:
            if ref.get('status') == 'exists':
                n += 1
                assert (REPO / ref['path']).exists(), f"exists ref mat tich: {ref['path']}"
    assert n >= 15, f'contract chi co {n} exists ref — qua it, nghi khai planned bua'


def test_memory_six_scopes_owned():
    data = load()
    assert set(REQUIRED_MEMORY) == set(data['memory'].keys())
    for m, entry in data['memory'].items():
        assert entry['owner'] in data['domains'], f'{m} owner khong hop le'


# ---------- DOC BAR (Rule 2 — khuon test_pack5_docs) ----------

REQUIRED_ELEMENTS = ['mission', 'purpose', 'scope', 'authority', 'responsibilit',
                     'workflow', 'mandatory', 'pass', 'fail', 'promotion', 'example']


def test_blueprint_docs_have_11_elements():
    missing = {}
    for name in DOCS:
        text = (BP / name).read_text(encoding='utf-8').lower()
        gaps = [e for e in REQUIRED_ELEMENTS if e not in text]
        if gaps:
            missing[name] = gaps
    assert not missing, f'blueprint docs thieu element: {missing}'


def test_blueprint_docs_no_placeholder():
    import re
    bad = re.compile(r'TODO|FIXME|PLACEHOLDER|TBD|\bDRAFT\b')
    for name in DOCS:
        text = (BP / name).read_text(encoding='utf-8')
        assert not bad.search(text), f'{name} chua placeholder/draft marker'


def test_blueprint_docs_reference_real_enforcers():
    enforcers = {
        '00_system_blueprint_constitution.md': 'tools/blueprint_constitution_check.py',
        '01_required_documents.md': 'tests/test_blueprint_constitution.py',
        '02_domain_contract.md': 'governance/blueprint/blueprint_domains.yaml',
        '03_dependency_rules.md': 'tools/blueprint_constitution_check.py',
        '04_blueprint_audit_gate.md': 'tools/cmd_pipeline_gate.py',
    }
    for name, rel in enforcers.items():
        assert (REPO / rel).exists(), f'{name} enforcer thieu tren disk: {rel}'
        doc_text = (BP / name).read_text(encoding='utf-8')
        basename = rel.split('/')[-1]
        assert basename in doc_text, f'{name} khong reference enforcer {rel}'
