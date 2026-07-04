"""BP9 — mutation battery cho bp9_compliance_check (đòn audit báo trước TASK_BP9).

Mutation TASK sẽ bắn: gate trỏ domain má → FAIL · content_policy thiếu 1 trong 2
lằn ranh → FAIL · threshold/số hardcode ngoài chỗ cho phép → FAIL · publisher.schema
BP0 KHÔNG khớp path file thật đã field-hóa (drift) → FAIL · dup-key trong 2 file
bp9 → FAIL · gỡ stage khỏi doc Mandatory Rules mà không xóa validator tương ứng
(unwire ngầm) → FAIL.

pytest-func FLAT -> collect trong `pytest tests/` và ci_gate.
"""
import copy
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402
from bp9_compliance_check import (  # noqa: E402
    check_content_policy, check_policy_gates, check_bp0_reconcile,
    D_POLICY, D_GATES, D_BP0, EXPECTED_HB)

POLICY = load_yaml_no_dup(D_POLICY.read_text(encoding='utf-8'))
GATES = load_yaml_no_dup(D_GATES.read_text(encoding='utf-8'))
BP0 = load_yaml_no_dup(D_BP0.read_text(encoding='utf-8'))
CLI = REPO / 'tools' / 'bp9_compliance_check.py'
DOC = REPO / 'governance' / 'blueprint' / 'bp9' / '00_compliance.md'


# ---------- POSITIVE (reality anchor: data thật) ----------

def test_cli_exit_zero_on_real_data():
    r = subprocess.run([sys.executable, str(CLI)], capture_output=True,
                       text=True, encoding='utf-8')
    assert r.returncode == 0, f'checker phai PASS tren data bp9 that:\n{r.stdout}'


def test_real_content_policy_zero_violations():
    assert check_content_policy(POLICY) == []


def test_real_policy_gates_zero_violations():
    assert check_policy_gates(GATES, BP0) == []


def test_real_bp0_reconcile_zero_violations():
    assert check_bp0_reconcile(BP0) == []


def test_real_2_hard_boundaries_machine_counted():
    ids = [h['rule_id'] for h in POLICY['hard_boundaries']]
    assert len(ids) == 2 and set(ids) == set(EXPECTED_HB)


def test_real_7_gates_machine_counted():
    assert len(GATES['gates']) == 7


# ---------- MUTATIONS (đòn TASK báo trước — mỗi cái phải CẮN) ----------

def _mut_policy():
    return copy.deepcopy(POLICY)


def _mut_gates():
    return copy.deepcopy(GATES)


def _mut_bp0():
    return copy.deepcopy(BP0)


def test_mut_missing_hard_boundary_bites():
    """Đòn TASK: content_policy thiếu 1 trong 2 lằn ranh → FAIL."""
    p = _mut_policy()
    p['hard_boundaries'] = [h for h in p['hard_boundaries'] if h['rule_id'] != 'HB02_no_real_profit_solicitation_link']
    errs = check_content_policy(p)
    assert any('HARD-BOUNDARY-THIEU' in e and 'HB02' in e for e in errs), errs


def test_mut_hard_boundary_empty_law_bites():
    p = _mut_policy()
    p['hard_boundaries'][0]['can_cu_phap_ly'] = []
    errs = check_content_policy(p)
    assert any('thieu can_cu_phap_ly' in e for e in errs), errs


def test_mut_content_policy_hardcode_bites():
    """Đòn TASK: threshold/số hardcode ngoài chỗ cho phép → FAIL."""
    p = _mut_policy()
    p['sensitivity_tiers']['medium']['min_word_count'] = 50
    errs = check_content_policy(p)
    assert any('R195-HARDCODE' in e and 'min_word_count' in e for e in errs), errs


def test_mut_gate_domain_ma_bites():
    """Đòn TASK: gate trỏ domain má → FAIL."""
    g = _mut_gates()
    g['gates'][0]['ap_dung_domain'] = ['khong_ton_tai_domain']
    errs = check_policy_gates(g, BP0)
    assert any('DOMAIN-MA' in e and 'khong_ton_tai_domain' in e for e in errs), errs


def test_mut_gate_loai_check_la_bites():
    g = _mut_gates()
    g['gates'][0]['loai_check'] = 'loai_bia_dat'
    errs = check_policy_gates(g, BP0)
    assert any('loai_check "loai_bia_dat"' in e for e in errs), errs


def test_mut_gate_high_missing_mrlong_review_bites():
    g = _mut_gates()
    high_gate = next(x for x in g['gates'] if x['severity'] == 'HIGH')
    high_gate['owner_review'] = 'Executor tu duyet khong can ai khac'
    errs = check_policy_gates(g, BP0)
    assert any('may tu quyet' in e for e in errs), errs


def test_mut_policy_gates_hardcode_bites():
    g = _mut_gates()
    g['meta']['max_gates'] = 20
    errs = check_policy_gates(g, BP0)
    assert any('R195-HARDCODE' in e and 'max_gates' in e for e in errs), errs


def test_mut_bp0_schema_drift_status_bites():
    """Đòn TASK: publisher.schema BP0 KHÔNG khớp path/status field-hóa (drift) → FAIL."""
    b = _mut_bp0()
    b['domains']['publisher']['schema']['status'] = 'planned'
    errs = check_bp0_reconcile(b)
    assert any('publisher.schema' in e and 'DRIFT-BP0' in e for e in errs), errs


def test_mut_bp0_validator_drift_path_bites():
    b = _mut_bp0()
    b['domains']['publisher']['validator']['path'] = 'tools/duong_dan_khac.py'
    errs = check_bp0_reconcile(b)
    assert any('publisher.validator' in e and 'DRIFT-BP0' in e for e in errs), errs


def test_dup_key_in_bp9_file_bites():
    """DUP-KEY loader single-impl phải bắt (lớp bug H6 blueprint)."""
    with pytest.raises(DupKeyError):
        load_yaml_no_dup('meta:\n  version: 1.0.0\nmeta:\n  version: 2.0.0\n')


# ---------- UNWIRE-GUARD (doc-code consistency, mirror BP5/BP7 pattern) ----------

def test_doc_mandatory_rules_mentions_all_real_checks():
    """gỡ mô tả rule khỏi 00_compliance.md Mandatory Rules ma KHONG xoa validator
    tuong ung = tai lieu noi mot dang, may lam mot nao khac (unwire ngam ve tai lieu).
    Moi check THAT trong bp9_compliance_check.py phai co dau vet trong doc."""
    text = DOC.read_text(encoding='utf-8')
    markers = ['hard_boundaries', 'domain', 'loai_check', 'Mr.Long',
              'publisher.schema', 'publisher.validator', 'DUP-KEY']
    missing = [m for m in markers if m not in text]
    assert not missing, f'00_compliance.md Mandatory Rules thieu nhac toi: {missing}'


def test_doc_11_elements_present():
    text = DOC.read_text(encoding='utf-8').lower()
    for e in ['mission', 'purpose', 'scope', 'authority', 'responsibilit',
              'workflow', 'mandatory', 'pass', 'fail', 'promotion', 'example']:
        assert e in text, f'doc thieu element {e}'
