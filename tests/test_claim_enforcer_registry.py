"""Mutation-proof self-test cho CLAIM-ENFORCER REGISTRY (de xuat #1+#4).
Enforcer: tools/claim_enforcer_registry_check.py + governance/claim_enforcer_map.yaml.

BEHAVIORAL (R215.5/R215.6) — KHONG grep-only, KHONG assert "x" in source:
  (a) checker PASS tren repo THAT (subprocess exit 0) + structural_problems() sach.
  (b) bo 1 REQUIRED_CLAIM khoi map (bo nho) -> structural_problems().missing bat.
  (c) doi 1 claim -> ENFORCED + enforcer tro file BIA -> structural_problems().mask bat
      (chung minh bat mask-as-active: co gate tren giay, file khong ton tai).
  (d) doi 1 claim non-machine (NO_ENFORCER...) -> gan enforcer may -> mislabel bat.
  (e) collectability THAT: enforcer test-node bia (::ham_khong_ton_tai) -> NOT-COLLECTED
      (chay pytest --collect-only that, khong grep ten).

Dung monkeypatch/deepcopy pure-fn — khong 'if __name__'/exit (tranh script-style,
xem test_no_orphan_tests.py). Co subprocess + goi ham danh gia that -> behavioral marker
nen KHONG bi test_no_greponly_wiring_guards.py gan co.
"""
import copy
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))

import claim_enforcer_registry_check as ce  # noqa: E402


def _clean_map():
    return ce.load_map()


# ---------- (a) reality anchor ----------

def test_checker_passes_on_real_repo():
    r = subprocess.run([sys.executable, str(REPO / 'tools' / 'claim_enforcer_registry_check.py')],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', cwd=str(REPO))
    assert r.returncode == 0, (
        f"checker FAIL tren repo that (exit {r.returncode}):\n{r.stdout[-1800:]}\n{r.stderr[-400:]}")


def test_structural_clean_on_real_map():
    st = ce.structural_problems(_clean_map())
    assert st['missing'] == [], f"REQUIRED claim thieu: {st['missing']}"
    assert st['bad_status'] == [], st['bad_status']
    assert st['mask'] == [], f"enforcer mask-as-active tren repo that: {st['mask']}"
    assert st['mislabel'] == [], st['mislabel']


def test_all_required_claims_present():
    claims = _clean_map().get('claims') or {}
    for cid in ce.REQUIRED_CLAIMS:
        assert cid in claims, f"REQUIRED claim '{cid}' vang trong map that"


# ---------- (b) MUTATION: bo 1 REQUIRED_CLAIM -> missing bat ----------

def test_removing_required_claim_flips_to_missing():
    mapping = copy.deepcopy(_clean_map())
    victim = ce.REQUIRED_CLAIMS[0]  # 'R_SUPREME'
    assert victim in mapping['claims']
    del mapping['claims'][victim]
    st = ce.structural_problems(mapping)
    assert victim in st['missing'], (
        f"bo REQUIRED claim '{victim}' khoi map ma structural_problems KHONG bao missing -> "
        "coverage check la no-op. Phai bat.")


def test_missing_empty_when_all_present():
    """Doi xung (b): map that day du -> missing rong (flag o (b) den tu viec bo, khong san co)."""
    assert ce.structural_problems(_clean_map())['missing'] == []


# ---------- (c) MUTATION: ENFORCED + enforcer file BIA -> mask bat ----------

def test_enforced_pointing_to_fake_file_is_flagged_mask():
    """Kich ban mask-as-active: ai do doi claim thanh ENFORCED + tro file khong ton tai
    (tuong da co gate). structural_problems().mask PHAI bat."""
    mapping = copy.deepcopy(_clean_map())
    mapping['claims']['R196'] = {
        'status': 'ENFORCED',
        'enforcer': ['tools/khong_ton_tai_bia_XYZ.py'],
    }
    st = ce.structural_problems(mapping)
    assert any('R196' in m for m in st['mask']), (
        "claim ENFORCED voi enforcer tro file BIA ma checker KHONG bao mask -> "
        "khong bat mask-as-active. mask=" + repr(st['mask']))


def test_partial_with_null_enforcer_is_flagged_mask():
    """PARTIAL ma enforcer null cung la mask-as-active."""
    mapping = copy.deepcopy(_clean_map())
    mapping['claims']['R197'] = {'status': 'PARTIAL', 'enforcer': None}
    st = ce.structural_problems(mapping)
    assert any('R197' in m for m in st['mask'])


def test_real_enforced_claim_not_flagged():
    """Doi xung (c): claim ENFORCED that (R211 -> file ton tai) KHONG bi mask —
    chung minh flag den tu file BIA, khong false-positive san."""
    st = ce.structural_problems(_clean_map())
    assert not any('R211' in m for m in st['mask'])


# ---------- (d) MUTATION: non-machine ma gan enforcer -> mislabel ----------

def test_non_machine_with_enforcer_is_flagged_mislabel():
    mapping = copy.deepcopy(_clean_map())
    # R200 la HONOR_SYSTEM — gan enforcer may (du file ton tai) van sai nhan
    mapping['claims']['R200'] = {
        'status': 'HONOR_SYSTEM',
        'enforcer': ['tools/architecture_registry_check.py'],
    }
    st = ce.structural_problems(mapping)
    assert any('R200' in m for m in st['mislabel']), (
        "non-machine status ma gan enforcer may ma KHONG bao mislabel -> co the gan gate gia "
        "cho claim thuc te 0 gate. mislabel=" + repr(st['mislabel']))


def test_invalid_status_flagged():
    mapping = copy.deepcopy(_clean_map())
    mapping['claims']['R196'] = {'status': 'TOTALLY_ENFORCED', 'enforcer': None}
    st = ce.structural_problems(mapping)
    assert any('R196' in m for m in st['bad_status'])


# ---------- (e) collectability THAT (pytest --collect-only, khong grep ten) ----------

def test_mapped_test_nodes_are_pytest_collectable():
    problems, collected = ce.collectability_problems(_clean_map())
    assert problems == [], f"enforcer test node khong collect duoc: {problems}"
    assert collected, "collect rong -> nghi pytest collect-only hong"


def test_collectability_catches_fake_uncollectable_node():
    """MUTATION cho collectability: doi enforcer node cua 1 claim ENFORCED/PARTIAL sang ham
    KHONG ton tai -> PHAI bao NOT-COLLECTED. Chung minh buoc collect that su chay, khong grep."""
    mapping = copy.deepcopy(_clean_map())
    # R216 la PARTIAL co test node
    mapping['claims']['R216']['enforcer'] = [
        'tests/test_cross_episode_canon_check.py::test_KHONG_TON_TAI_META_XYZ']
    problems, _ = ce.collectability_problems(mapping)
    assert any('R216' in p for p in problems), (
        "enforcer node tro ham khong ton tai ma collectability KHONG bat -> grep-mu. "
        "Phai chay pytest --collect-only that. problems=" + repr(problems))
