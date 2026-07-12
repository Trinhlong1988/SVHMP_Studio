"""tests/test_regret_variety_check.py — DEBT-032 check #2 (regret variety), per Mr.Long
authorization 12/7 (TASK_DEBT030_031_CONTENT_FIX.md Buoc 3, giao kem DEBT-031 content fix).

Mirror pattern tests/test_supernatural_run_all_composition.py (_run_all_body_ok): dung LAI ham
thuan cua chinh tools/regret_variety_check.py (R211, khong viet lai logic), mutation-proof tren
CA 3 sub-check (khong chi 1) de dam bao khong sub-check nao bi "quen" khoi check_regret_variety().

Reality anchor: check tren du lieu THAT sau khi DEBT-031 sua noi dung (EP03/04/06/07/09/10 doi
pillar) phai PASS (0 issue) — chung minh fix dung. Injection test: gia lap lai TRANG THAI TRUOC
KHI SUA (EP02-10 toan REG_FAM, dung du lieu that DEBT-031 mo ta) -> check PHAI bat duoc vi pham,
chung minh check nay se KHONG lot qua regression tuong tu lan sau (DEBT-032 muc tieu).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import regret_variety_check as rv  # noqa: E402
from regret_variety_check import (  # noqa: E402
    _run_all_body_ok,
    check_family_max_per_window,
    check_min_distinct_per_window,
    check_pillar_distance,
    check_regret_variety,
    load_pillar_sequence,
    load_variety_rules,
)


# ============================================================
# Composition proof (mirror _run_all_body_ok pattern)
# ============================================================

def test_check_regret_variety_body_ok_on_real_source():
    """Static proof tren source THAT: check_regret_variety() dang goi du 3/3 sub-check."""
    src = (REPO / "tools" / "regret_variety_check.py").read_text(encoding="utf-8")
    ok, detail = _run_all_body_ok(src)
    assert ok, f"check_regret_variety() source that dang FAIL check: {detail}"


def _mutate_remove_subcheck_call(src, call_snippet):
    """Go 1 dong 'errs += check_X(...)' khoi body check_regret_variety() (chi trong bo nho)."""
    m = re.search(r"def check_regret_variety\(.*?\n(?=def |\Z)", src, re.DOTALL)
    assert m, "khong tim thay ham check_regret_variety()"
    body = m.group(0)
    assert call_snippet in body, f"'{call_snippet}' khong ton tai trong body - kiem tra lai format"
    line_re = re.compile(r"^ {4}errs \+= " + re.escape(call_snippet) + r".*\n", re.MULTILINE)
    mutated_body, n = line_re.subn("", body, count=1)
    assert n == 1, f"khong go duoc dong chua '{call_snippet}'"
    assert mutated_body != body
    return src.replace(body, mutated_body)


_ALL_SUB_CHECKS = [
    "check_pillar_distance(",
    "check_family_max_per_window(",
    "check_min_distinct_per_window(",
]


def test_enforcement_detects_mutation_remove_check_pillar_distance():
    """MUTATION-PROOF sub-check #1/3: go 'errs += check_pillar_distance(...)' -> FAIL."""
    src = (REPO / "tools" / "regret_variety_check.py").read_text(encoding="utf-8")
    mutated = _mutate_remove_subcheck_call(src, "check_pillar_distance(")
    ok, detail = _run_all_body_ok(mutated)
    assert not ok, f"MUTATION (go check_pillar_distance) khong bi bat: {detail}"
    assert "check_pillar_distance" in detail


def test_enforcement_detects_mutation_remove_check_family_max_per_window():
    """MUTATION-PROOF sub-check #2/3: go 'errs += check_family_max_per_window(...)' -> FAIL."""
    src = (REPO / "tools" / "regret_variety_check.py").read_text(encoding="utf-8")
    mutated = _mutate_remove_subcheck_call(src, "check_family_max_per_window(")
    ok, detail = _run_all_body_ok(mutated)
    assert not ok, f"MUTATION (go check_family_max_per_window) khong bi bat: {detail}"
    assert "check_family_max_per_window" in detail


def test_enforcement_detects_mutation_remove_check_min_distinct_per_window():
    """MUTATION-PROOF sub-check #3/3: go 'errs += check_min_distinct_per_window(...)' -> FAIL."""
    src = (REPO / "tools" / "regret_variety_check.py").read_text(encoding="utf-8")
    mutated = _mutate_remove_subcheck_call(src, "check_min_distinct_per_window(")
    ok, detail = _run_all_body_ok(mutated)
    assert not ok, f"MUTATION (go check_min_distinct_per_window) khong bi bat: {detail}"
    assert "check_min_distinct_per_window" in detail


def test_enforcement_detects_mutation_remove_all_sub_checks():
    """MUTATION-PROOF toan phan: go CA 3 dong -> FAIL, liet ke du 3/3 sub-check con thieu."""
    src = (REPO / "tools" / "regret_variety_check.py").read_text(encoding="utf-8")
    mutated = src
    for call in _ALL_SUB_CHECKS:
        mutated = _mutate_remove_subcheck_call(mutated, call)
    ok, detail = _run_all_body_ok(mutated)
    assert not ok
    for call in _ALL_SUB_CHECKS:
        assert call.rstrip("(") in detail, f"mutation toan phan nhung detail thieu {call}: {detail}"


# ============================================================
# Sub-check unit behavior (synthetic, khong dua tren du lieu that)
# ============================================================

def test_check_pillar_distance_flags_back_to_back_same_pillar():
    pairs = [(1, "love_regret"), (2, "family_regret"), (3, "family_regret")]
    errs = check_pillar_distance(pairs, min_distance=3)
    assert errs and "family_regret" in errs[0]


def test_check_pillar_distance_passes_when_gap_sufficient():
    pairs = [(1, "family_regret"), (4, "family_regret")]
    assert check_pillar_distance(pairs, min_distance=3) == []


def test_check_family_max_per_window_flags_overuse():
    pairs = [(n, "family_regret") for n in range(1, 6)]  # 5 lan trong 1 cua so 10 tap
    errs = check_family_max_per_window(pairs, max_family=4, window=10)
    assert errs and "family_regret" in errs[0]


def test_check_family_max_per_window_passes_within_cap():
    pairs = [(1, "family_regret"), (4, "family_regret"), (7, "family_regret"), (10, "family_regret")]
    assert check_family_max_per_window(pairs, max_family=4, window=10) == []


def test_check_min_distinct_per_window_flags_low_variety():
    pairs = [(n, "family_regret") for n in range(1, 11)]  # 10 tap, 1 pillar duy nhat
    errs = check_min_distinct_per_window(pairs, min_distinct=4, window=10)
    assert errs and "1 pillar" in errs[0]


def test_check_min_distinct_per_window_skips_incomplete_window():
    """Cua so chua du du lieu (vd chi 3 tap trong 1 batch 10-ep) -> KHONG bao gia gia
    (R195 khong bia tren du lieu chua day du)."""
    pairs = [(1, "family_regret"), (2, "love_regret"), (3, "promise_regret")]
    assert check_min_distinct_per_window(pairs, min_distinct=4, window=10) == []


# ============================================================
# Reality anchor (du lieu THAT sau DEBT-031 fix)
# ============================================================

def test_reality_check_regret_variety_passes_on_real_data():
    """runtime/event_ledger_draft.yaml THAT (sau khi DEBT-031 sua EP03/04/06/07/09/10)
    PHAI PASS bible/11 variety_rules — chung minh fix dung tren du lieu that, khong chi
    tren du lieu gia lap."""
    issues = check_regret_variety()
    assert issues == [], f"regret variety van vi pham tren du lieu that sau fix: {issues}"


def test_reality_pillar_sequence_matches_debt031_table():
    """EP01-11 phai dung dung bang pillar da sua trong TASK_DEBT030_031_CONTENT_FIX.md Buoc 2."""
    pairs = dict(load_pillar_sequence(max_ep=11))
    expected = {
        2: "family_regret", 3: "promise_regret", 4: "love_regret", 5: "family_regret",
        6: "kindness_regret", 7: "self_regret", 8: "family_regret", 9: "promise_regret",
        10: "love_regret",
    }
    for ep, pillar in expected.items():
        assert pairs.get(ep) == pillar, f"ep_{ep:02d}: mong {pillar}, that {pairs.get(ep)}"
    # EP01 (love_regret, giu nguyen) va EP11 (null/pending) KHONG nam trong known-prefix set
    # cua REGRET_SUB_PREFIX_TO_PILLAR (EP01 co regret_sub=None trong ledger, EP11 cung None)
    assert 1 not in pairs and 11 not in pairs


def test_injection_pre_fix_state_would_have_failed():
    """MUTATION/injection quan trong nhat: gia lap CHINH XAC trang thai TRUOC KHI SUA
    (EP02-10 toan REG_FAM_001, nhu TECH_DEBT.md DEBT-031 da ghi nhan bang chung that) qua
    ledger_events override -> check PHAI bat duoc vi pham. Chung minh check nay se BAT duoc
    regression tuong tu neu no tai dien o EP12+ (muc tieu DEBT-032)."""
    pre_fix_events = {
        f"ep_{n:02d}": {"primary_event": {"regret_sub": {"value": "REG_FAM_001 - Me doi con ve Tet"}}}
        for n in range(2, 11)
    }
    issues = check_regret_variety(ledger_events=pre_fix_events)
    assert issues, "trang thai TRUOC KHI SUA (9/10 tap family_regret) khong bi bat - enforcer vo hieu"
    assert any("family_regret" in i for i in issues)


def test_load_variety_rules_reads_real_bible11_thresholds():
    """Reality anchor: nguong doc THAT tu bible/11 (khong hardcode trong check nay)."""
    rules = load_variety_rules()
    assert rules["pillar_distance"] == 3
    assert rules["family_regret_max_per_10_ep"] == 4
    assert rules["pillar_per_10_ep_min_distinct"] == 4


# ============================================================
# Wiring vao svhmp_preflight_qa.py (unwire-guard, mirror test_g5_gate_has_..._wired)
# ============================================================

def test_preflight_has_regret_variety_gate_wired():
    """Unwire-guard: svhmp_preflight_qa.py PHAI goi check_regret_variety() - neu bi go,
    quay lai khoang ho DEBT-032 da ghi nhan (0 tool QA nao doi chieu bible/11 variety_rules)."""
    src = (REPO / "tools" / "svhmp_preflight_qa.py").read_text(encoding="utf-8")
    assert "check_regret_variety" in src, "REGRET_VARIETY_GATE bi go khoi svhmp_preflight_qa.py (unwire!)"
    assert "R-REGRET-VARIETY" in src, "issues.append prefix R-REGRET-VARIETY bi go (gate khong con block duoc)"
