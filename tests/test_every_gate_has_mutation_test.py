"""META-GATE self-test — moi stage ci_gate.CHECKS phai co mutation-proof test dang ky.

De xuat #2 (governance/AUDIT_ROOT_CAUSE_SYNTHESIS_17_07.md muc 3). Enforcer:
tools/gate_mutation_registry_check.py + governance/gate_mutation_map.yaml.

Test nay TU no mutation-proof + BEHAVIORAL (R215.5/R215.6) — KHONG grep-only:
  (a) chay checker tren repo THAT qua subprocess -> exit 0 (moi stage da phu).
  (b) MUTATION: monkeypatch them 1 stage GIA vao ci_gate.CHECKS (khong map/allowlist)
      roi goi ham danh gia THAT coverage_problems() -> PHAI liet ke stage gia la uncovered.
      Neu coverage_problems la no-op (return rong) -> assert nay do -> chung minh checker
      that su kiem, khong luon-PASS.
  (c) ALLOWLIST LOAD-BEARING: go 1 entry known_no_mutation_test khoi map (trong bo nho)
      roi goi coverage_problems() tren CHECKS that -> stage do PHAI thanh uncovered.
      Chung minh allowlist giu gate xanh THAT SU, khong phai trang tri.
  (d) collectability THAT: moi test_node mapped duoc pytest collect (khong grep ten).

Khong dung 'if __name__'/exit trong file nay (tranh bi coi la script-style, xem
test_no_orphan_tests.py). Dung monkeypatch + subprocess -> co behavioral marker nen
KHONG bi test_no_greponly_wiring_guards.py gan co.
"""
import copy
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))

import ci_gate  # noqa: E402
import gate_mutation_registry_check as gm  # noqa: E402


# ---------- (a) reality anchor: checker PASS tren repo that ----------

def test_checker_passes_on_real_repo():
    r = subprocess.run([sys.executable, str(REPO / 'tools' / 'gate_mutation_registry_check.py')],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', cwd=str(REPO))
    assert r.returncode == 0, (
        f"checker FAIL tren repo that (exit {r.returncode}):\n{r.stdout[-1500:]}\n{r.stderr[-400:]}")


def test_every_ci_gate_stage_is_covered_now():
    """Trang thai hien tai: moi stage ci_gate.CHECKS phu boi dung 1 bucket."""
    keys = gm.ci_gate_check_keys()
    cov = gm.coverage_problems(keys, gm.load_map())
    assert cov['uncovered'] == [], f"stage chua co mutation-test/allowlist: {cov['uncovered']}"
    assert cov['duplicate'] == [], f"stage o >1 bucket: {cov['duplicate']}"


# ---------- (b) MUTATION-PROOF: gate gia them vao CHECKS -> phai bi bat ----------

def test_fake_stage_added_to_checks_is_flagged_uncovered(monkeypatch):
    """Mo phong dung kich ban de xuat #2: ai do WIRE 1 gate MOI vao CHECKS ma chua co
    mutation-test/allowlist. monkeypatch them stage gia -> coverage_problems() PHAI bao
    uncovered. Neu ham danh gia rong/no-op, test nay do."""
    fake = ('FAKE_GATE_META_XYZ', 'tools/khong_ton_tai_fake.py')
    patched = list(ci_gate.CHECKS) + [fake]
    monkeypatch.setattr(ci_gate, 'CHECKS', patched)

    keys = gm.ci_gate_check_keys()          # doc lai tu CHECKS da patch
    assert 'FAKE_GATE_META_XYZ' in keys, 'monkeypatch CHECKS khong hieu luc — self-test vo nghia'
    cov = gm.coverage_problems(keys, gm.load_map())
    assert 'FAKE_GATE_META_XYZ' in cov['uncovered'], (
        "gate GIA them vao CHECKS ma checker KHONG bao uncovered -> checker la gate-gia "
        "(dung cai dang chong). coverage_problems phai bat.")


def test_clean_checks_has_no_uncovered_after_mutation_reverted(monkeypatch):
    """Doi xung (b): sau khi monkeypatch tra ve CHECKS that (khong stage gia), khong con
    uncovered — chung minh flag o (b) den TU stage gia, khong phai false-positive san co."""
    # khong patch gi — CHECKS that
    cov = gm.coverage_problems(gm.ci_gate_check_keys(), gm.load_map())
    assert cov['uncovered'] == []


# ---------- (c) ALLOWLIST LOAD-BEARING: go entry -> stage do uncovered ----------

def test_removing_allowlist_entry_flips_stage_to_uncovered():
    """Go 1 entry known_no_mutation_test khoi map (trong bo nho) -> stage do PHAI thanh
    uncovered. Neu van covered => allowlist la no-op (khong load-bearing) => that bai
    dung muc tieu deliverable #3(c)."""
    mapping = gm.load_map()
    victims = list((mapping.get('known_no_mutation_test') or {}).keys())
    assert victims, "map phai co it nhat 1 entry known_no_mutation_test de chung load-bearing"
    victim = victims[0]

    # sanity: truoc khi go, stage do KHONG uncovered
    keys = gm.ci_gate_check_keys()
    assert victim in keys, f"entry allowlist '{victim}' phai la stage that trong CHECKS"
    before = gm.coverage_problems(keys, mapping)
    assert victim not in before['uncovered']

    mutated = copy.deepcopy(mapping)
    del mutated['known_no_mutation_test'][victim]
    after = gm.coverage_problems(keys, mutated)
    assert victim in after['uncovered'], (
        f"go entry allowlist '{victim}' ma stage van covered -> allowlist khong load-bearing "
        "(no-op). Checker phai coi allowlist la thu duy nhat giu stage khoi uncovered.")


def test_removing_self_battery_entry_also_flips_uncovered():
    """Doi xung cho bucket known_self_battery: cung load-bearing (go 1 entry -> uncovered)."""
    mapping = gm.load_map()
    victims = list((mapping.get('known_self_battery') or {}).keys())
    assert victims, "map phai co it nhat 1 entry known_self_battery"
    victim = victims[0]
    keys = gm.ci_gate_check_keys()
    mutated = copy.deepcopy(mapping)
    del mutated['known_self_battery'][victim]
    after = gm.coverage_problems(keys, mutated)
    assert victim in after['uncovered']


# ---------- (d) collectability THAT (pytest --collect-only, khong grep ten) ----------

def test_all_mapped_test_nodes_are_pytest_collectable():
    """Moi test_node mapped duoc pytest collect that (BEHAVIORAL: chay --collect-only,
    khong grep chuoi ten trong source)."""
    problems, collected = gm.collectability_problems(gm.load_map())
    assert problems == [], f"test_node khong collect duoc: {problems}"
    assert collected, "collect rong -> nghi pytest collect-only hong"


def test_collectability_catches_a_fake_uncollectable_node():
    """MUTATION cho lop collectability: 1 test_node tro ham KHONG ton tai -> phai bi bao
    NOT-COLLECTED. Chung minh buoc collect that su kiem (khong luon-PASS)."""
    mapping = copy.deepcopy(gm.load_map())
    # chon 1 stage mapped that, doi ham thanh ten khong ton tai trong CUNG file
    stage = next(iter(mapping['mapped']))
    node = mapping['mapped'][stage]['test_node']
    file_part = node.split('::')[0]
    mapping['mapped'][stage]['test_node'] = f"{file_part}::test_KHONG_TON_TAI_META_XYZ"
    problems, _ = gm.collectability_problems(mapping)
    assert any(stage in p for p in problems), (
        "test_node tro ham khong ton tai ma collectability_problems KHONG bat -> buoc "
        "collect la no-op (grep-mu). Phai chay pytest --collect-only that.")
