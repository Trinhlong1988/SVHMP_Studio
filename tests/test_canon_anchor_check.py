"""Mutation-proof self-test cho CANON-FACT PROVENANCE registry (de xuat #3, R216).
Enforcer: tools/canon_anchor_check.py + governance/canon_facts.yaml.

BEHAVIORAL (R215.5/R215.6) — KHONG grep-only, KHONG assert "x" in source:
  (a) checker PASS tren repo THAT (subprocess exit 0) + provenance_problems() sach
      + commit_problems() sach (anchor_commit resolve THAT qua git).
  (b) go 'anchor_ep' 1 fact (bo nho) -> provenance_problems().bad_anchor_ep bat.
  (c) doi 'anchor_commit' thanh SHA bia 'deadbeef...' -> commit_problems() bat
      (chung minh commit-resolve chay GIT THAT, khong grep: SHA co dung format hex
      40 ky tu nhung KHONG ton tai trong repo -> git cat-file -e that FAIL).
  (d) bo 1 REQUIRED fact khoi map -> provenance_problems().missing bat.

Dung monkeypatch/deepcopy pure-fn — khong 'if __name__'/exit. Co subprocess +
goi ham danh gia that (git that) -> behavioral marker, KHONG bi
test_no_greponly_wiring_guards.py gan co.
"""
import copy
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / 'tools'))

import canon_anchor_check as ca  # noqa: E402


def _clean_map():
    return ca.load_facts()


# ---------- (a) reality anchor ----------

def test_checker_passes_on_real_repo():
    r = subprocess.run([sys.executable, str(REPO / 'tools' / 'canon_anchor_check.py')],
                       capture_output=True, text=True, encoding='utf-8',
                       errors='replace', cwd=str(REPO))
    assert r.returncode == 0, (
        f"checker FAIL tren repo that (exit {r.returncode}):\n{r.stdout[-1800:]}\n{r.stderr[-400:]}")


def test_provenance_clean_on_real_map():
    pv = ca.provenance_problems(_clean_map())
    assert pv['missing'] == [], f"REQUIRED fact thieu: {pv['missing']}"
    assert pv['no_value'] == [], pv['no_value']
    assert pv['bad_anchor_ep'] == [], pv['bad_anchor_ep']
    assert pv['no_commit'] == [], pv['no_commit']


def test_all_required_facts_present():
    facts = _clean_map().get('facts') or {}
    for fid in ca.REQUIRED_FACTS:
        assert fid in facts, f"REQUIRED fact '{fid}' vang trong map that"


def test_real_anchor_commits_resolve_via_git():
    """anchor_commit trong map that PHAI resolve qua git THAT (khong grep)."""
    cp = ca.commit_problems(_clean_map())
    assert cp == [], f"anchor_commit khong resolve qua git tren repo that: {cp}"


# ---------- (b) MUTATION: go anchor_ep -> bad_anchor_ep bat ----------

def test_removing_anchor_ep_flips_to_bad_anchor_ep():
    mapping = copy.deepcopy(_clean_map())
    victim = ca.REQUIRED_FACTS[0]  # 'kp_seat'
    del mapping['facts'][victim]['anchor_ep']
    pv = ca.provenance_problems(mapping)
    assert any(victim in s for s in pv['bad_anchor_ep']), (
        f"go anchor_ep cua '{victim}' ma provenance_problems KHONG bao bad_anchor_ep -> "
        "anchor_ep check la no-op. Phai bat. bad_anchor_ep=" + repr(pv['bad_anchor_ep']))


def test_non_int_anchor_ep_flagged():
    """anchor_ep phai INT — chuoi '1' (khong phai int) van sai."""
    mapping = copy.deepcopy(_clean_map())
    mapping['facts']['kp_seat']['anchor_ep'] = "1"
    pv = ca.provenance_problems(mapping)
    assert any('kp_seat' in s for s in pv['bad_anchor_ep'])


def test_bad_anchor_ep_empty_when_all_valid():
    """Doi xung (b): map that day du -> bad_anchor_ep rong."""
    assert ca.provenance_problems(_clean_map())['bad_anchor_ep'] == []


# ---------- (c) MUTATION: anchor_commit bia -> commit_problems bat (git that) ----------

def test_fake_anchor_commit_is_flagged_via_real_git():
    """Kich ban: ai do doi anchor_commit thanh SHA BIA (hex hop le nhung khong ton
    tai trong repo). commit_problems() chay `git cat-file -e` THAT phai bat.
    Chung minh buoc resolve la GIT THAT, khong grep source."""
    mapping = copy.deepcopy(_clean_map())
    mapping['facts']['kp_seat']['anchor_commit'] = 'deadbeef' * 5  # 40 hex, khong ton tai
    cp = ca.commit_problems(mapping)
    assert any('kp_seat' in p for p in cp), (
        "anchor_commit BIA (deadbeef...) ma commit_problems KHONG bat -> khong resolve "
        "git that (co the dang grep). cp=" + repr(cp))


def test_commit_resolves_true_for_real_head():
    """commit_resolves() tra True cho HEAD that -> chung git that chay dung chieu."""
    head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True,
                          text=True, cwd=str(REPO)).stdout.strip()
    assert ca.commit_resolves(head), f"commit_resolves False cho HEAD that {head}"


def test_commit_resolves_false_for_fake_sha():
    """commit_resolves() tra False cho SHA bia -> git cat-file -e that FAIL."""
    assert ca.commit_resolves('deadbeef' * 5) is False


def test_commit_problems_uses_injected_resolver():
    """commit_problems tach resolver -> bom resolver luon-False chung moi anchor_commit
    bi bat; luon-True chung khong bat. (mutation-proof khong can commit that.)"""
    mapping = _clean_map()
    all_false = ca.commit_problems(mapping, resolver=lambda sha, root: False)
    assert len(all_false) == len(ca.REQUIRED_FACTS), (
        "resolver luon-False phai bat MOI fact co anchor_commit")
    all_true = ca.commit_problems(mapping, resolver=lambda sha, root: True)
    assert all_true == [], "resolver luon-True khong duoc bat fact nao"


# ---------- (d) MUTATION: bo 1 REQUIRED fact -> missing bat ----------

def test_removing_required_fact_flips_to_missing():
    mapping = copy.deepcopy(_clean_map())
    victim = ca.REQUIRED_FACTS[-1]  # 'havy_death_time'
    assert victim in mapping['facts']
    del mapping['facts'][victim]
    pv = ca.provenance_problems(mapping)
    assert victim in pv['missing'], (
        f"bo REQUIRED fact '{victim}' ma provenance_problems KHONG bao missing -> "
        "coverage check la no-op. Phai bat. missing=" + repr(pv['missing']))


def test_missing_empty_when_all_present():
    """Doi xung (d): map that day du -> missing rong."""
    assert ca.provenance_problems(_clean_map())['missing'] == []


def test_removing_value_flagged():
    """MUTATION phu: go 'value' -> no_value bat."""
    mapping = copy.deepcopy(_clean_map())
    del mapping['facts']['havy_death_place']['value']
    pv = ca.provenance_problems(mapping)
    assert any('havy_death_place' in s for s in pv['no_value'])
