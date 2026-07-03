"""BP4 Runtime+Event — certify (positive + mutation battery theo TASK_BP4).

Don audit bao truoc: hop bia (Lighting tran) · event trigger ma · state orphan ·
memory 2-writer · flow nguoc — tu ban het. Behavioral tmp_path.

pytest-func FLAT -> collect trong `pytest tests/` va ci_gate.
"""
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from bp4_runtime_check import run_checks, __version__  # noqa: E402

BP4 = REPO / 'governance' / 'blueprint' / 'bp4'
FLOW = BP4 / 'runtime_flow.yaml'
BUS = BP4 / 'event_bus.yaml'
SM = BP4 / 'state_machines.yaml'
MEM = BP4 / 'memory_architecture.yaml'
DOC = BP4 / '00_runtime_event.md'


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

def test_real_bp4_passes():
    errs, _ = run_checks()
    assert errs == [], f'BP4 that phai 0 vi pham: {errs}'


def test_cli_exit_zero():
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    r = subprocess.run([sys.executable, str(REPO / 'tools' / 'bp4_runtime_check.py')],
                       capture_output=True, text=True, encoding='utf-8', env=env)
    assert r.returncode == 0, f'CLI phai exit 0: {r.stdout}\n{r.stderr}'


def test_mandatory_ghost_appears_chain():
    bus = _load(BUS)
    ga = next(e for e in bus['events'] if e['event_id'] == 'ghost_appears')
    assert ga['emitter'] == 'supernatural'
    assert 'character.emotion_trigger' in ga['chain'], 'cam xuc nhan vat phai trong chain mau'
    assert 'analytics' in ga['chain']


def test_flow_layers_strictly_increase():
    flow = _load(FLOW)
    bp0 = _load(REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml')
    lys = [bp0['layers'][h['domain']] for h in flow['flow']]
    assert lys == sorted(lys) and len(set(lys)) == len(lys), lys


def test_character_life_maps_arc():
    """BP2b: story_arc_personal PHAI map state machine BP4 — day la cai map."""
    sm = _load(SM)
    m = next(x for x in sm['state_machines'] if x['entity'] == 'character_life')
    assert m['owner_domain'] == 'character'
    assert set(m['states']) == {'alive', 'dead', 'ghost', 'released'}


def test_doc_11_elements():
    text = DOC.read_text(encoding='utf-8').lower()
    for e in ['mission', 'purpose', 'scope', 'authority', 'responsibilit', 'workflow',
              'mandatory', 'pass', 'fail', 'promotion', 'example']:
        assert e in text, f'doc thieu {e}'


# ---------- MUTATION BATTERY ----------

def test_mut_alien_hop_lighting_fails(tmp_path):
    bus = _load(BUS)
    for e in bus['events']:
        if e['event_id'] == 'ghost_appears':
            e['chain'].append('lighting')
    _assert_fails("hop 'lighting' KHONG phai domain", bus_p=_dump(tmp_path, 'b.yaml', bus))


def test_mut_facet_wrong_domain_hop_fails(tmp_path):
    bus = _load(BUS)
    bus['events'][0]['chain'].append('world.emotion_trigger')  # facet cua character, khong phai world
    _assert_fails('KHONG khai trong BP2', bus_p=_dump(tmp_path, 'b.yaml', bus))


def test_mut_ghost_trigger_fails(tmp_path):
    sm = _load(SM)
    sm['state_machines'][0]['transitions'][0]['trigger'] = 'ghost_dances'
    _assert_fails('EVENT-MA', sm_p=_dump(tmp_path, 's.yaml', sm))


def test_mut_orphan_state_fails(tmp_path):
    sm = _load(SM)
    sm['state_machines'][0]['states'].append('possessed')  # khong co transition vao
    _assert_fails('ORPHAN', sm_p=_dump(tmp_path, 's.yaml', sm))


def test_mut_memory_second_writer_fails(tmp_path):
    mem = _load(MEM)
    for m in mem['memory_scopes']:
        if m['scope'] == 'episode_memory':
            m['writers'] = ['generator', 'dialogue']
    _assert_fails('VUOT BP3', mem_p=_dump(tmp_path, 'm.yaml', mem))


def test_mut_reversed_flow_fails(tmp_path):
    flow = _load(FLOW)
    flow['flow'][4], flow['flow'][5] = flow['flow'][5], flow['flow'][4]  # audio truoc tts
    _assert_fails('NGUOC LAYER', flow_p=_dump(tmp_path, 'f.yaml', flow))


def test_mut_memory_owner_drift_fails(tmp_path):
    mem = _load(MEM)
    for m in mem['memory_scopes']:
        if m['scope'] == 'event_memory':
            m['owner'] = 'character'
    _assert_fails('!= BP0', mem_p=_dump(tmp_path, 'm.yaml', mem))


def test_mut_reader_outside_grant_fails(tmp_path):
    mem = _load(MEM)
    for m in mem['memory_scopes']:
        if m['scope'] == 'global_memory':
            m['readers'] = list(m['readers']) + ['publisher']  # publisher khong trong story_planner.reader
    _assert_fails('ngoai reader grant', mem_p=_dump(tmp_path, 'm.yaml', mem))


def test_mut_missing_ghost_appears_fails(tmp_path):
    bus = _load(BUS)
    bus['events'] = [e for e in bus['events'] if e['event_id'] != 'ghost_appears']
    # trigger ghost_appears trong state machines cung se thanh EVENT-MA — assert chuoi mau
    _assert_fails('THIEU chuoi mau bat buoc', bus_p=_dump(tmp_path, 'b.yaml', bus))


def test_mut_dup_key_fails(tmp_path):
    bad = tmp_path / 'dup.yaml'
    bad.write_text(BUS.read_text(encoding='utf-8') + '\nvalidator_version: 9.9.9\n',
                   encoding='utf-8')
    _assert_fails('DUP-KEY', bus_p=bad)


def test_mut_version_mismatch_fails(tmp_path):
    flow = _load(FLOW)
    flow['validator_version'] = '9.9.9'
    _assert_fails('VERSION', flow_p=_dump(tmp_path, 'f.yaml', flow))
