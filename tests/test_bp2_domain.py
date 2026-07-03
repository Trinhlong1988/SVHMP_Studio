"""BP2 Domain Architecture — certify (positive + mutation battery theo TASK_BP2_DOMAIN).

Mutation audit se ban: facet 2 domain · facet_id trung · SoT gia · domain canon
thieu block · invariant tro enforcer ma — tu test truoc tat ca. Behavioral:
mutate ban sao spec THAT (tmp_path) -> checker FAIL dung lop.

pytest-func FLAT -> collect trong `pytest tests/` va ci_gate.
"""
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from bp2_domain_check import run_checks, REQUIRED_BP2_DOMAINS, __version__  # noqa: E402

SPEC = REPO / 'governance' / 'blueprint' / 'bp2' / 'domain_specs.yaml'
DOC = REPO / 'governance' / 'blueprint' / 'bp2' / '00_domain_architecture.md'


def load():
    return yaml.safe_load(SPEC.read_text(encoding='utf-8'))


def _dump(tmp_path, data):
    p = tmp_path / 'spec.yaml'
    p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')
    return p


def _assert_fails(tmp_path, data, needle):
    errs, _ = run_checks(spec_p=_dump(tmp_path, data))
    assert errs, f'checker phai FAIL (mong bat: {needle})'
    assert any(needle in e for e in errs), f'khong thay {needle!r} trong: {errs}'


# ---------- POSITIVE ----------

def test_real_spec_passes():
    errs, _ = run_checks()
    assert errs == [], f'spec that phai 0 vi pham: {errs}'


def test_cli_exit_zero():
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    r = subprocess.run([sys.executable, str(REPO / 'tools' / 'bp2_domain_check.py')],
                       capture_output=True, text=True, encoding='utf-8', env=env)
    assert r.returncode == 0, f'CLI phai exit 0: {r.stdout}\n{r.stderr}'


def test_13_domains_and_facet_counts():
    data = load()
    assert set(REQUIRED_BP2_DOMAINS) == set(data['domains'].keys())
    fids = [f['facet_id'] for b in data['domains'].values() for f in b['facets']]
    assert len(fids) == len(set(fids)), 'facet_id phai duy nhat toan cuc'
    assert len(fids) >= 40, f'qua it facet ({len(fids)}) — nghi thieu inventory'


def test_character_facets_anchor_real_bible37_keys():
    """RECONCILE: facet character phai tro key THAT trong bible/37 (khong tach file moi)."""
    data = load()
    keys = {f['sot'].get('key') for f in data['domains']['character']['facets']
            if f['sot'].get('status') == 'exists'}
    assert 'tier_1_mandatory.core_id' in keys
    assert 'tier_1_mandatory.relationships' in keys
    assert 'critical_groups.emotion_trigger' in keys


def test_doc_exists_11_elements():
    text = DOC.read_text(encoding='utf-8').lower()
    for e in ['mission', 'purpose', 'scope', 'authority', 'responsibilit', 'workflow',
              'mandatory', 'pass', 'fail', 'promotion', 'example']:
        assert e in text, f'doc thieu element {e}'


# ---------- MUTATION BATTERY (don audit da bao truoc) ----------

def test_mut_facet_in_two_domains_fails(tmp_path):
    data = load()
    # nhet facet cua character sang dialogue (2 domain cung 1 facet_id)
    data['domains']['dialogue']['facets'].append(
        dict(data['domains']['character']['facets'][0]))
    _assert_fails(tmp_path, data, 'TRUNG 2 domain')


def test_mut_sot_exists_fake_path_fails(tmp_path):
    data = load()
    data['domains']['world']['facets'][0]['sot'] = {
        'status': 'exists', 'path': 'bible/khong_ton_tai.yaml'}
    _assert_fails(tmp_path, data, 'khai lao/phantom')


def test_mut_sot_exists_fake_key_fails(tmp_path):
    data = load()
    data['domains']['character']['facets'][0]['sot'] = {
        'status': 'exists', 'path': 'bible/37_character_schema.yaml',
        'key': 'tier_1_mandatory.khong_co_key_nay'}
    _assert_fails(tmp_path, data, 'khai key lao')


def test_mut_canon_domain_missing_block_fails(tmp_path):
    data = load()
    del data['domains']['supernatural']
    _assert_fails(tmp_path, data, 'THIEU domain block: supernatural')


def test_mut_domain_without_facets_fails(tmp_path):
    data = load()
    data['domains']['ritual']['facets'] = []
    _assert_fails(tmp_path, data, 'ritual: THIEU facets')


def test_mut_invariant_ghost_enforcer_fails(tmp_path):
    data = load()
    data['domains']['character']['invariants'][0]['enforcer'] = {
        'status': 'exists', 'path': 'tools/khong_he_ton_tai_validator.py'}
    _assert_fails(tmp_path, data, 'ENFORCER-MA')


def test_mut_alien_domain_fails(tmp_path):
    data = load()
    data['domains']['music'] = dict(data['domains']['world'])
    _assert_fails(tmp_path, data, 'DOMAIN-LA')


def test_mut_planned_missing_metadata_fails(tmp_path):
    data = load()
    data['domains']['weather']['facets'][0]['sot'] = {
        'status': 'planned', 'planned_path': 'bible/41_weather_bible.yaml'}
    _assert_fails(tmp_path, data, 'PLANNED HONESTY')


def test_mut_dup_key_yaml_fails(tmp_path):
    bad = tmp_path / 'dup.yaml'
    bad.write_text(SPEC.read_text(encoding='utf-8') + '\nvalidator_version: 9.9.9\n',
                   encoding='utf-8')
    errs, _ = run_checks(spec_p=bad)
    assert any('DUP-KEY' in e for e in errs), errs


def test_mut_version_mismatch_fails(tmp_path):
    data = load()
    data['validator_version'] = '9.9.9'
    _assert_fails(tmp_path, data, 'VERSION')
