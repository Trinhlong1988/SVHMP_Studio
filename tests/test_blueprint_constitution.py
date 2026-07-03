"""SYSTEM_BLUEPRINT_CONSTITUTION v2.0 — certify (positive + negative behavioral).

Amendment v2 (bang E 3/7 + 2 dieu kien kiem duyet). Negative test = chung minh
checker KHONG phai weak-verifier: moi lop vi pham phai lam
tools/blueprint_constitution_check.py FAIL that su. Mutate deep-copy cua contract
THAT roi assert check() tra vi pham dung lop.

pytest-func -> tu dong collect trong `pytest tests/` va ci_gate.
"""
import copy
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from blueprint_constitution_check import (check, REQUIRED_DOMAINS,  # noqa: E402
                                          REQUIRED_MEMORY, __version__)

BP = REPO / 'governance' / 'blueprint'
CONTRACT = BP / 'blueprint_domains.yaml'
DOCS = ['00_system_blueprint_constitution.md', '01_required_documents.md',
        '02_domain_contract.md', '03_dependency_rules.md', '04_blueprint_audit_gate.md']

FULL_PLANNED = {'status': 'planned', 'planned_path': 'tools/chua_he_ton_tai.py',
                'owner': 'video', 'reason_not_exists_yet': 'chua khoi cong',
                'target_milestone': 'M4_video_publisher', 'blocking_dependency': 'R196'}


def load():
    return yaml.safe_load(CONTRACT.read_text(encoding='utf-8'))


def _assert_fails(data, needle):
    errs = check(data)
    assert errs, f'checker phai FAIL (mong bat: {needle})'
    assert any(needle in e for e in errs), f'khong thay vi pham {needle!r} trong: {errs}'


# ---------- POSITIVE ----------

def test_real_contract_passes():
    assert check(load()) == [], 'contract that phai 0 vi pham'


def test_cli_exit_zero():
    r = subprocess.run([sys.executable, str(REPO / 'tools' / 'blueprint_constitution_check.py')],
                       capture_output=True, text=True, encoding='utf-8')
    assert r.returncode == 0, f'CLI phai exit 0: {r.stdout}\n{r.stderr}'


def test_all_22_required_domains_declared():
    data = load()
    assert set(REQUIRED_DOMAINS) <= set(data['domains']), 'contract thieu domain bat buoc'
    assert len(REQUIRED_DOMAINS) == 22
    assert 'quest' in data['domains'], 'quest RESERVED phai duoc khai cho (bang E)'


def test_versioning_meta_present_and_matches_checker():
    meta = load()['meta']
    for k in ('schema_version', 'contract_version', 'validator_version'):
        assert meta.get(k), f'meta.{k} thieu (A4)'
    assert str(meta['validator_version']) == __version__


def test_blueprint_docs_exist_nonempty():
    for name in DOCS:
        p = BP / name
        assert p.exists(), f'blueprint doc missing: {name}'
        assert p.stat().st_size > 0, f'blueprint doc empty: {name}'


def test_promotion_is_candidate_not_locked_by_builder():
    assert load()['meta']['promotion_status'] == 'candidate'


def test_planned_with_full_metadata_does_not_fail():
    """KHONG FAIL vi planned (du 5 metadata) — trung thuc, cam ep stub."""
    data = load()
    data['domains']['video']['manager'] = dict(FULL_PLANNED)
    assert check(data) == [], 'planned du metadata khong duoc lam checker FAIL'


def test_l1_canon_domains_have_empty_dependencies():
    """Cond 1: 8 domain canon L1 dependencies rong tuyet doi (reader-only)."""
    data = load()
    l1 = [n for n, layer in data['layers'].items() if layer == 1]
    assert len(l1) == 8
    for name in l1:
        assert (data['domains'][name].get('dependencies') or []) == [], (
            f'{name} la L1 nhung co dependencies — vi pham Cond 1')


# ---------- 9 NEGATIVE GOC (AUDIT.md) ----------

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
    data['domains']['character']['dependencies'] = ['generator']  # L2 dep L6
    _assert_fails(data, 'SAI HUONG')


def test_neg6_supernatural_merged_into_world_fails():
    d1 = load()
    d1['domains']['world']['contains'] = ['supernatural']
    _assert_fails(d1, 'contains supernatural')
    d2 = load()
    d2['domains']['supernatural']['sub_of'] = 'world'
    _assert_fails(d2, 'DOC LAP')


def test_neg7_memory_without_owner_fails():
    data = load()
    del data['memory']['event_memory']['owner']
    _assert_fails(data, 'KHONG co owner')


def test_neg8_candidate_self_locked_fails():
    data = load()
    data['meta']['promotion_status'] = 'locked'
    _assert_fails(data, 'SELF-LOCK')


def test_neg9_missing_audit_gate_fails():
    data = load()
    data['domains']['production']['audit_rule'] = ''
    _assert_fails(data, 'production: field audit_rule RONG')


# ---------- NEGATIVE v1 (PLANNED HONESTY) ----------

def test_neg10_planned_missing_metadata_fails():
    for missing in ('planned_path', 'owner', 'reason_not_exists_yet',
                    'target_milestone', 'blocking_dependency'):
        data = load()
        ref = dict(FULL_PLANNED)
        del ref[missing]
        data['domains']['video']['manager'] = ref
        _assert_fails(data, f'thieu metadata {missing}')


def test_neg11_planned_bogus_milestone_fails():
    data = load()
    ref = dict(FULL_PLANNED)
    ref['target_milestone'] = 'M99_khong_ton_tai'
    data['domains']['video']['manager'] = ref
    _assert_fails(data, 'khong co trong milestones')


def test_phantom_exists_path_fails():
    data = load()
    data['domains']['world']['manager'] = {'path': 'tools/khong_ton_tai_dau.py',
                                           'status': 'exists'}
    _assert_fails(data, 'phantom')


# ---------- NEGATIVE v2 (amendment: Cond 1+2, A2-A7) ----------

def test_neg12_l1_cross_dep_fails():
    """Cond 1: canon L1 dep canon L1 -> L1-CROSS-DEP (chi duoc reader)."""
    data = load()
    data['domains']['location']['dependencies'] = ['world']
    _assert_fails(data, 'L1-CROSS-DEP')


def test_neg13_planned_path_on_disk_is_violation():
    """Cond 2 chong stub: planned nhung path DA ton tai -> VIOLATION (khong phai WARN)."""
    data = load()
    ref = dict(FULL_PLANNED)
    ref['planned_path'] = 'tools/character_manager.py'  # file THAT dang ton tai
    data['domains']['video']['manager'] = ref
    _assert_fails(data, 'DRIFT/STUB')


def test_neg14_archived_dependency_fails():
    """A2: dep vao domain lifecycle=archived = VIOLATION."""
    data = load()
    data['domains']['culture']['lifecycle'] = 'archived'
    # character dang dep culture trong contract that
    _assert_fails(data, 'archived')


def test_neg15_validator_version_mismatch_fails():
    """A4: contract khai validator_version lech checker -> FAIL."""
    data = load()
    data['meta']['validator_version'] = '1.0.0'
    _assert_fails(data, 'VERSIONING')


def test_neg16_old_lifecycle_enum_rejected():
    """A3: enum cu (active/locked_bible) khong con hop le."""
    data = load()
    data['domains']['world']['lifecycle'] = 'locked_bible'
    _assert_fails(data, "lifecycle 'locked_bible'")


def test_neg17_facet_two_writers_fails():
    """A7 FORMAT facet: 1 facet = DUNG 1 writer (chong 3 manager cung sua Emotion)."""
    data = load()
    data['domains']['character']['facets'] = {
        'emotion': {'writer': ['character', 'dialogue'], 'readers': ['story_planner']}}
    _assert_fails(data, '1 facet = DUNG 1 writer')


def test_neg18_domain_outside_layer_groups_fails():
    """A6: moi domain phai thuoc dung 1 nhom."""
    data = load()
    data['layer_groups']['narrative'].remove('quest')
    _assert_fails(data, "domain 'quest' khong thuoc nhom nao")


def test_neg19_event_chain_violates_reader_fails():
    """A7 FORMAT event: hop ke tiep phai nam trong reader cua hop truoc."""
    data = load()
    data['events'] = [{'name': 'ghost_appears', 'emitter': 'supernatural',
                       'chain': ['publisher']}]  # publisher KHONG trong supernatural.reader
    _assert_fails(data, 'chain pham quyen doc')


# ---------- CHONG PASS-RONG ----------

def test_all_exists_refs_truly_on_disk():
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


# ---------- DOC BAR (khuon test_pack5_docs) ----------

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
