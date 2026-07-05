"""D5 Supernatural Validator (TASK_G5_SUPERNATURAL.md, CMD_BUILD_3 4-5/7): kiem chung
data that (governance/proposals/supernatural_typology_proposal.yaml + governance/
blueprint/bp4/state_machines.yaml entity 'ghost') PASS 0 vi pham, + mutation
behavioral M1/M2/M3/M4/M7 (TASK_G5 "MUTATION AUDIT SE BAN") tu bien PHAI bat duoc
loi. Unwire-guard chong stage g5_supernatural bi go khoi ci_gate.CHECKS.

R211 RECONCILE (2026-07-05, fix/g5-4-possession-dup): possession state machine
KHONG con doc tu runtime/supernatural_state_machine.yaml (file da bi audit xac
nhan la nhan doi voi entity 'ghost' cua bp4) — nguon THAT gio la bp4/state_machines.yaml
entity 'ghost' (da duoc MO RONG state), xem reports/G5_FIX_POSSESSION_DEDUP.md."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import ci_gate
from supernatural_validator import (
    check_claimed_powers, check_no_duplicate_compliance_files,
    check_possession_state_machine, check_typology, run_all,
    valid_bp7_facets, valid_sensitivity_values,
)

SVHMP = Path(__file__).resolve().parent.parent
REAL_TYPOLOGY_YAML = SVHMP / 'governance' / 'proposals' / 'supernatural_typology_proposal.yaml'
REAL_SM_YAML = SVHMP / 'governance' / 'blueprint' / 'bp4' / 'state_machines.yaml'


# ---------- data that PASS 0 vi pham ----------

def test_real_typology_and_state_machine_clean():
    assert run_all() == []


def test_real_typology_has_at_least_5_entities_with_evidence():
    """DoD TASK_G5: Typology >=5 loai co nguon."""
    import yaml
    ty = yaml.safe_load(REAL_TYPOLOGY_YAML.read_text(encoding='utf-8'))
    entities = ty['entities']
    assert len(entities) >= 5
    for e in entities:
        ev = e['nguon_goc']['evidence']
        assert ev['status'] in ('verified', 'hypothesis')


# ---------- M4: sensitivity ngoai enum BP9 ----------

def test_m4_sensitivity_outside_bp9_enum_fails():
    typology = {'entities': [{'entity_type': 'ma_bia', 'sensitivity': 'critical',
                              'nguon_goc': {'bp7_facet_mirror': 'belief.tin_nguong_he',
                                            'evidence': {'status': 'hypothesis'}}}]}
    errs = check_typology(typology=typology, valid_sensitivity={'low', 'medium', 'high'},
                          valid_facets={'belief.tin_nguong_he'})
    assert any('M4' in e for e in errs)


def test_sensitivity_enum_read_from_bp9_not_hardcoded():
    vals = valid_sensitivity_values()
    assert vals == {'low', 'medium', 'high'}


# ---------- M2: facet mirror khong ton tai trong bp7 ----------

def test_m2_facet_ma_fails():
    typology = {'entities': [{'entity_type': 'ma_bia', 'sensitivity': 'low',
                              'nguon_goc': {'bp7_facet_mirror': 'belief.facet_khong_ton_tai',
                                            'evidence': {'status': 'hypothesis'}}}]}
    errs = check_typology(typology=typology, valid_sensitivity={'low', 'medium', 'high'},
                          valid_facets={'belief.tin_nguong_he'})
    assert any('M2' in e for e in errs)


def test_bp7_facets_loaded_from_real_file():
    facets = valid_bp7_facets()
    assert 'belief.tin_nguong_he' in facets
    assert 'belief.am_duong_quan_niem' in facets


# ---------- M3: possession khong truc xuat (treo mai) ----------

def test_m3_possession_stuck_state_fails():
    bad_sm = {'state_machines': [{'entity': 'ghost',
        'states': ['dormant', 'entering', 'stuck_forever', 'released'],
        'transitions': [
            {'from': 'dormant', 'to': 'entering'},
            {'from': 'entering', 'to': 'released'},
            {'from': 'stuck_forever', 'to': 'stuck_forever'},   # tu-lap, khong ra duoc
        ]}]}
    errs = check_possession_state_machine(sm=bad_sm)
    assert any('stuck_forever' in e and 'M3' in e for e in errs)


def test_m3_missing_ghost_entity_fails():
    errs = check_possession_state_machine(sm={'state_machines': []})
    assert any('ghost' in e for e in errs)


def test_real_state_machine_no_stuck_state():
    assert check_possession_state_machine() == []


def test_real_state_machine_reads_from_bp4_ghost_entity():
    """R211 reconcile: nguon THAT la bp4/state_machines.yaml entity 'ghost', KHONG
    phai runtime/supernatural_state_machine.yaml (da xoa possession_state_machine
    block khoi file do — xem reports/G5_FIX_POSSESSION_DEDUP.md)."""
    import supernatural_validator as sv
    assert sv.STATE_MACHINE == REAL_SM_YAML
    import yaml
    data = yaml.safe_load(REAL_SM_YAML.read_text(encoding='utf-8'))
    ghost = next(m for m in data['state_machines'] if m['entity'] == 'ghost')
    assert 'entering' in ghost['states'] and 'exorcising' in ghost['states']


# ---------- M1: nang luc ngoai typology da khai ----------

def test_m1_claimed_power_outside_typology_fails():
    errs = check_claimed_powers('ma_da', ['bay tren khong trung'])
    assert any('M1' in e for e in errs)


def test_m1_claimed_power_matching_typology_passes():
    errs = check_claimed_powers('ma_da', ['nuoc'])   # "nuoc" co trong mo ta quyen_nang ma_da
    assert errs == []


def test_m1_unknown_entity_type_fails():
    errs = check_claimed_powers('ma_khong_ton_tai', ['gi_cung_duoc'])
    assert errs and 'khong ton tai' in errs[0]


# ---------- M7: cam tao file trung BP9 (R211 tuyet doi) ----------

def test_m7_no_duplicate_compliance_files_on_real_repo():
    """CMD_BUILD_3 KHONG duoc tu tao 2 file nay — phai luon rong tren repo that."""
    assert check_no_duplicate_compliance_files() == []


def test_m7_detects_forbidden_file_if_present(tmp_path, monkeypatch):
    import supernatural_validator as sv
    fake_repo = tmp_path
    (fake_repo / 'bible').mkdir()
    (fake_repo / 'bible' / 'content_policy.yaml').write_text('x: 1', encoding='utf-8')
    (fake_repo / 'tools').mkdir()
    monkeypatch.setattr(sv, 'SVHMP', fake_repo)
    errs = sv.check_no_duplicate_compliance_files()
    assert any('content_policy.yaml' in e and 'M7' in e for e in errs)


# ---------- Unwire-guard (mirror test_g2_roster_stage_wired_in_ci_gate) ----------

def test_g5_supernatural_stage_wired_in_ci_gate():
    """Chong unwire: go ('g5_supernatural', tools/g5_supernatural_check.py) khoi
    ci_gate CHECKS -> test nay do."""
    assert ('g5_supernatural', 'tools/g5_supernatural_check.py') in ci_gate.CHECKS, \
        'stage g5_supernatural bi go khoi ci_gate CHECKS (unwire!)'


def test_g5_supernatural_has_error_code():
    assert ci_gate.STAGE_CODES.get('g5_supernatural') == 'ONT5001'
