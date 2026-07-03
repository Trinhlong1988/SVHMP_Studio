"""BP3 Ownership + Dependency — certify (positive + mutation battery theo TASK_BP3).

Don audit bao truoc: 2-writer · facet ma · dep 3-nguon lech · writable leo thang ·
matrix thieu facet BP2 — tu ban het. Behavioral: mutate ban sao tmp_path.

pytest-func FLAT -> collect trong `pytest tests/` va ci_gate.
"""
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from bp3_ownership_check import run_checks, __version__  # noqa: E402

BP3 = REPO / 'governance' / 'blueprint' / 'bp3'
MATRIX = BP3 / 'facet_ownership_matrix.yaml'
DEPD = BP3 / 'dependency_detail.yaml'
DOC = BP3 / '00_ownership.md'


def _load(p):
    return yaml.safe_load(p.read_text(encoding='utf-8'))


def _dump(tmp_path, name, data):
    p = tmp_path / name
    p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')
    return p


def _assert_fails(needle, **kw):
    errs, _ = run_checks(**kw)
    assert errs, f'checker phai FAIL (mong bat: {needle})'
    assert any(needle in e for e in errs), f'khong thay {needle!r} trong: {errs}'


# ---------- POSITIVE ----------

def test_real_bp3_passes():
    errs, _ = run_checks()
    assert errs == [], f'BP3 that phai 0 vi pham: {errs}'


def test_cli_exit_zero():
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    r = subprocess.run([sys.executable, str(REPO / 'tools' / 'bp3_ownership_check.py')],
                       capture_output=True, text=True, encoding='utf-8', env=env)
    assert r.returncode == 0, f'CLI phai exit 0: {r.stdout}\n{r.stderr}'


def test_adjudicated_emotion_owner_character():
    """Phan quyet da chot: emotion owner=character, reader read-only."""
    m = _load(MATRIX)
    f = next(x for x in m['facets'] if x['facet_id'] == 'emotion_trigger')
    assert f['owning_domain'] == 'character'
    assert set(f['writable_by']) <= {'character', 'mr_long'}
    for r in ('dialogue', 'story_planner', 'decision_engine'):
        assert r in f['readable_by'] and r in f['forbidden_writers']


def test_one_writer_rule_holds_everywhere():
    m = _load(MATRIX)
    for f in m['facets']:
        non_ml = [w for w in f['writable_by'] if w != 'mr_long']
        assert len(non_ml) <= 1, f['facet_id']
        assert all(w == f['owning_domain'] for w in non_ml), f['facet_id']


def test_bible_facets_writer_mr_long_only():
    """Bible/tools catalog: writer duy nhat = mr_long."""
    m = _load(MATRIX)
    for f in m['facets']:
        if str(f['owner_artifact']).startswith(('bible/', 'tools/')):
            assert f['writable_by'] == ['mr_long'], f['facet_id']


def test_doc_11_elements():
    text = DOC.read_text(encoding='utf-8').lower()
    for e in ['mission', 'purpose', 'scope', 'authority', 'responsibilit', 'workflow',
              'mandatory', 'pass', 'fail', 'promotion', 'example']:
        assert e in text, f'doc thieu {e}'


# ---------- MUTATION BATTERY ----------

def test_mut_two_writers_fails(tmp_path):
    m = _load(MATRIX)
    f = next(x for x in m['facets'] if x['facet_id'] == 'emotion_trigger')
    f['writable_by'] = ['character', 'dialogue']
    _assert_fails('LUAT VANG', matrix_p=_dump(tmp_path, 'm.yaml', m))


def test_mut_ghost_facet_fails(tmp_path):
    m = _load(MATRIX)
    m['facets'].append(dict(m['facets'][0], facet_id='facet_ma_khong_co'))
    _assert_fails('FACET-MA', matrix_p=_dump(tmp_path, 'm.yaml', m))


def test_mut_matrix_missing_bp2_facet_fails(tmp_path):
    m = _load(MATRIX)
    m['facets'] = [f for f in m['facets'] if f['facet_id'] != 'goal']
    _assert_fails('THIEU facet BP2 da khai: goal', matrix_p=_dump(tmp_path, 'm.yaml', m))


def test_mut_writable_alien_domain_fails(tmp_path):
    m = _load(MATRIX)
    m['facets'][0]['writable_by'] = ['mr_long', 'music']
    _assert_fails("'music' khong trong inventory", matrix_p=_dump(tmp_path, 'm.yaml', m))


def test_mut_writable_escalation_fails(tmp_path):
    """Writable leo thang: domain that nhung KHONG phai owner."""
    m = _load(MATRIX)
    f = next(x for x in m['facets'] if x['facet_id'] == 'voice_states')  # owner dialogue
    f['writable_by'] = ['generator']
    _assert_fails('VUOT owner rule', matrix_p=_dump(tmp_path, 'm.yaml', m))


def test_mut_owner_wrong_block_fails(tmp_path):
    m = _load(MATRIX)
    f = next(x for x in m['facets'] if x['facet_id'] == 'goal')
    f['owning_domain'] = 'dialogue'
    _assert_fails('!= domain block BP2', matrix_p=_dump(tmp_path, 'm.yaml', m))


def test_mut_dep_extra_edge_fails(tmp_path):
    d = _load(DEPD)
    d['dependencies'].append({'dep_id': 'dep__dialogue__event', 'from': 'dialogue',
                              'to': 'event', 'reason': 'x', 'data_flow': 'read'})
    _assert_fails('DEP-3-NGUON lech', dep_p=_dump(tmp_path, 'd.yaml', d))


def test_mut_dep_missing_edge_fails(tmp_path):
    d = _load(DEPD)
    d['dependencies'] = [x for x in d['dependencies']
                         if x['dep_id'] != 'dep__generator__decision_engine']
    _assert_fails('DEP-3-NGUON lech', dep_p=_dump(tmp_path, 'd.yaml', d))


def test_mut_dep_missing_reason_fails(tmp_path):
    d = _load(DEPD)
    d['dependencies'][0]['reason'] = 'MISSING_REASON'
    _assert_fails('thieu reason', dep_p=_dump(tmp_path, 'd.yaml', d))


def test_mut_dup_key_fails(tmp_path):
    bad = tmp_path / 'dup.yaml'
    bad.write_text(MATRIX.read_text(encoding='utf-8') + '\nvalidator_version: 9.9.9\n',
                   encoding='utf-8')
    _assert_fails('DUP-KEY', matrix_p=bad)


def test_mut_version_mismatch_fails(tmp_path):
    m = _load(MATRIX)
    m['validator_version'] = '9.9.9'
    _assert_fails('VERSION', matrix_p=_dump(tmp_path, 'm.yaml', m))
