"""BP1 Core Architecture — certify (positive + mutation battery M1-M10, TASK_BP1_CORE ban va).

Mutation = behavioral: bien dang ban sao artifact THAT (tmp_path) roi assert
tools/bp1_architecture_check.py FAIL dung lop — chung minh checker khong phai
weak-verifier. Subprocess scrub GIT_* (lesson hook-env).

pytest-func FLAT trong tests/ -> collect trong `pytest tests/` va ci_gate.
"""
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from bp1_architecture_check import run_checks, __version__  # noqa: E402

BP1 = REPO / 'governance' / 'blueprint' / 'bp1'
GRAPH = BP1 / 'dependency_graph.yaml'
IFACE = BP1 / 'interface_contracts.yaml'
LAYERS = BP1 / 'layer_contracts.yaml'
BP0 = REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml'
REPORT = REPO / 'reports' / 'BP1_CORE_ARCHITECTURE_REPORT.md'


def _dump(tmp_path, name, data):
    p = tmp_path / name
    p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')
    return p


def _errs(**kw):
    errs, _ = run_checks(**kw)
    return errs


def _assert_fails(needle, **kw):
    errs = _errs(**kw)
    assert errs, f'checker phai FAIL (mong bat: {needle})'
    assert any(needle in e for e in errs), f'khong thay {needle!r} trong: {errs}'


# ---------- POSITIVE ----------

def test_real_bp1_passes():
    assert _errs() == [], 'BP1 that phai 0 vi pham'


def test_cli_exit_zero():
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    r = subprocess.run([sys.executable, str(REPO / 'tools' / 'bp1_architecture_check.py')],
                       capture_output=True, text=True, encoding='utf-8', env=env)
    assert r.returncode == 0, f'CLI phai exit 0: {r.stdout}\n{r.stderr}'


def test_layer_model_is_locked_numeric_plus_groups():
    """Hard rule 6: layer model = so 1-12 + 4 nhan COPY nguyen ven BP0."""
    g = yaml.safe_load(GRAPH.read_text(encoding='utf-8'))
    b = yaml.safe_load(BP0.read_text(encoding='utf-8'))
    assert g['layers'] == b['layers']
    assert {k: sorted(v) for k, v in g['layer_groups'].items()} == \
           {k: sorted(v) for k, v in b['layer_groups'].items()}


def test_interface_planned_honesty_counts():
    """Hau het interface planned (trung thuc); exists chi khi co bang chung wire."""
    doc = yaml.safe_load(IFACE.read_text(encoding='utf-8'))
    sts = [c['status'] for c in doc['contracts']]
    assert sts.count('exists') == 4, f'exists phai dung 4 (2 read wire that + 2 write store that): {sts.count("exists")}'
    assert all(s in ('exists', 'planned') for s in sts)


def test_versions_match_checker():
    for f in (GRAPH, IFACE, LAYERS):
        doc = yaml.safe_load(f.read_text(encoding='utf-8'))
        assert str(doc['validator_version']) == __version__, f.name


# ---------- MUTATION BATTERY M1-M10 ----------

def test_m1_alien_domain_fails(tmp_path):
    g = yaml.safe_load(GRAPH.read_text(encoding='utf-8'))
    g['domains'].append({'domain_id': 'music', 'layer': 9, 'depends_on': [],
                         'reads_from': [], 'writes_to': [], 'lifecycle': 'draft',
                         'owner_artifact': 'x'})
    _assert_fails('DOMAIN-LA', graph_p=_dump(tmp_path, 'g.yaml', g))


def test_m2_missing_real_domain_fails(tmp_path):
    g = yaml.safe_load(GRAPH.read_text(encoding='utf-8'))
    g['domains'] = [d for d in g['domains'] if d['domain_id'] != 'timeline']
    _assert_fails('THIEU domain trong graph: timeline', graph_p=_dump(tmp_path, 'g.yaml', g))


def test_m3_l1_dep_l1_fails(tmp_path):
    g = yaml.safe_load(GRAPH.read_text(encoding='utf-8'))
    for d in g['domains']:
        if d['domain_id'] == 'location':
            d['depends_on'] = ['world']
    _assert_fails('L1-CROSS-DEP', graph_p=_dump(tmp_path, 'g.yaml', g))


def test_m4_provider_archived_fails(tmp_path):
    b = yaml.safe_load(BP0.read_text(encoding='utf-8'))
    b['domains']['culture']['lifecycle'] = 'archived'
    _assert_fails('archived', bp0_p=_dump(tmp_path, 'bp0.yaml', b))


def test_m5_dup_key_yaml_fails(tmp_path):
    text = GRAPH.read_text(encoding='utf-8')
    bad = tmp_path / 'dup.yaml'
    bad.write_text(text + '\nvalidator_version: 9.9.9\n', encoding='utf-8')  # key trung top-level
    _assert_fails('DUP-KEY', graph_p=bad)


def test_m6_interface_missing_version_fails(tmp_path):
    doc = yaml.safe_load(IFACE.read_text(encoding='utf-8'))
    del doc['contracts'][0]['version']
    _assert_fails('thieu version', iface_p=_dump(tmp_path, 'i.yaml', doc))


def test_m7_circular_dependency_fails(tmp_path):
    g = yaml.safe_load(GRAPH.read_text(encoding='utf-8'))
    for d in g['domains']:
        if d['domain_id'] == 'character':
            d['depends_on'] = list(d['depends_on']) + ['dialogue']
        if d['domain_id'] == 'dialogue':
            d['depends_on'] = list(d['depends_on']) + ['character']
    _assert_fails('CIRCULAR', graph_p=_dump(tmp_path, 'g.yaml', g))


def test_m8_depends_on_drift_vs_bp0_fails(tmp_path):
    """Don tu kiem duyet: sua tay graph lech blueprint_domains -> LECH-BP0."""
    g = yaml.safe_load(GRAPH.read_text(encoding='utf-8'))
    for d in g['domains']:
        if d['domain_id'] == 'generator':
            d['depends_on'] = [x for x in d['depends_on'] if x != 'decision_engine']
    _assert_fails('LECH-BP0 depends_on', graph_p=_dump(tmp_path, 'g.yaml', g))


def test_m9_report_claims_missing_file_fails(tmp_path):
    fake = tmp_path / 'r.md'
    fake.write_text(REPORT.read_text(encoding='utf-8') +
                    '\n| `tools/khong_he_ton_tai_bp1.py` | fake |\n', encoding='utf-8')
    _assert_fails('REPORT-CLAIM', report_p=fake)


def test_m10_status_exists_fake_path_fails(tmp_path):
    doc = yaml.safe_load(IFACE.read_text(encoding='utf-8'))
    for c in doc['contracts']:
        if c['status'] == 'exists':
            c['source_artifact'] = 'runtime/khong_ton_tai.yaml'
            break
    _assert_fails('khai lao/phantom', iface_p=_dump(tmp_path, 'i.yaml', doc))


# ---------- CHONG PASS-RONG / drift phu ----------

def test_iface_completeness_two_way(tmp_path):
    """Xoa 1 read-contract -> IFACE-THIEU (khong thieu edge nao duoc phep)."""
    doc = yaml.safe_load(IFACE.read_text(encoding='utf-8'))
    doc['contracts'] = [c for c in doc['contracts']
                        if c['contract_id'] != 'read__world__character']
    _assert_fails('IFACE-THIEU: reader edge world->character',
                  iface_p=_dump(tmp_path, 'i.yaml', doc))


def test_layer_scheme_alien_fails(tmp_path):
    """Don 'layer-scheme la': doi sang L0..L4 -> LAYER-SCHEME FAIL."""
    g = yaml.safe_load(GRAPH.read_text(encoding='utf-8'))
    g['layers'] = {d['domain_id']: 'L1_canon' for d in g['domains']}
    _assert_fails('LAYER-SCHEME', graph_p=_dump(tmp_path, 'g.yaml', g))


def test_planned_interface_missing_metadata_fails(tmp_path):
    doc = yaml.safe_load(IFACE.read_text(encoding='utf-8'))
    for c in doc['contracts']:
        if c['status'] == 'planned':
            del c['reason_not_exists_yet']
            break
    _assert_fails('PLANNED HONESTY — thieu metadata reason_not_exists_yet',
                  iface_p=_dump(tmp_path, 'i.yaml', doc))
