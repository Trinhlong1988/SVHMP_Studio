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
import json
import re
import subprocess
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
# Wiring vao svhmp_preflight_qa.py (unwire-guard BEHAVIORAL — DEBT-037 phan (a),
# nang tu TEXT-GREP len BEHAVIORAL theo R215 diem 5 + CLAUDE.md).
# ============================================================
#
# LICH SU (DEBT-037): ban cu cua test_preflight_has_regret_variety_gate_wired chi co
#   assert "check_regret_variety" in src  +  assert "R-REGRET-VARIETY" in src
# tren source svhmp_preflight_qa.py -> MU voi unwire: thay call THAT
#   `_rv_issues = check_regret_variety(max_ep=_ep) if _ep else []`  ->  `_rv_issues = []`
# ma GIU dong `from regret_variety_check import check_regret_variety` + dong
# `issues.append(f'R-REGRET-VARIETY {_rvi}')` -> ca 2 chuoi VAN con trong source ->
# grep-test VAN PASS du gate da bi vo hieu hoan toan. R215 diem 5 cam dung grep lam
# bang chung "da-wired". Duoi day dung ledger vi pham CO Y roi chay CA pipeline
# svhmp_preflight_qa.py end-to-end (dung entrypoint __main__ that qua runpy trong 1
# subprocess) va assert no THUC SU chan (exit!=0 + R-REGRET-VARIETY xuat hien), dong
# thoi input SACH -> KHONG chan (chong over-tighten). Unwire -> nhanh vi pham mat
# R-REGRET-VARIETY va exit ve 0 -> test FAIL (mutation kill that su).


def _run_preflight_e2e(tmp_path, ledger_events, spec_sentences, ep=98765):
    """Chay svhmp_preflight_qa.py END-TO-END qua entrypoint __main__ that (runpy trong
    subprocess), inject ledger GIA bang cach patch story_planner.EVENT_LEDGER truoc khi
    runpy chay preflight — REGRET_VARIETY_GATE se doc dung ledger nay (load_pillar_sequence
    goi sp._load(sp.EVENT_LEDGER) tai call-time). Tra ve subprocess.CompletedProcess.
    --skip-r86 de bo qua FULL_TEXT_GATE (khong lien quan gate nay); ep=98765 (khong ton tai)
    de VERDICT_JSON ghi ra 1 file runtime/preflight_ep_98765.json duoc DON DEP ngay sau."""
    import yaml  # story_planner phu thuoc yaml -> luon co san trong env

    tmp_path.mkdir(parents=True, exist_ok=True)
    ledger_path = tmp_path / "fake_event_ledger.yaml"
    ledger_path.write_text(
        yaml.safe_dump({"events": ledger_events}, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    # Filename chua 'ep_<N>' de svhmp_preflight_qa.py bat duoc _ep (dieu kien de gate chay).
    spec_path = tmp_path / f"spec_ep_{ep}.json"
    spec_path.write_text(
        json.dumps({"sentences": spec_sentences}, ensure_ascii=False), encoding="utf-8"
    )
    preflight = REPO / "tools" / "svhmp_preflight_qa.py"
    tools_dir = REPO / "tools"
    boot = tmp_path / "boot_preflight.py"
    boot.write_text(
        "import sys, runpy\n"
        "from pathlib import Path\n"
        f"sys.path.insert(0, {json.dumps(str(tools_dir))})\n"
        "import story_planner as sp\n"
        f"sp.EVENT_LEDGER = Path({json.dumps(str(ledger_path))})\n"
        f"preflight = {json.dumps(str(preflight))}\n"
        f"sys.argv = [preflight, {json.dumps(str(spec_path))}, '--skip-r86']\n"
        "runpy.run_path(preflight, run_name='__main__')\n",
        encoding="utf-8",
    )
    try:
        proc = subprocess.run(
            [sys.executable, str(boot)],
            capture_output=True, text=True, encoding="utf-8",
        )
    finally:
        # Don dep artifact VERDICT_JSON (ep 98765 khong phai tap that -> an toan).
        stray = REPO / "runtime" / f"preflight_ep_{ep}.json"
        if stray.exists():
            stray.unlink()
    return proc


# Spec text SACH: qua het cac rule text preflight (R1 khong co fragment <=3 tu, khong
# trigger/lap/cut; chunk cuoi chua ending-phrase 'nho mai'; khong ten nhan vat -> R10 skip)
# -> voi ledger SACH thi exit==0; khac biet duy nhat giua 2 nhanh la LEDGER.
_CLEAN_SPEC_SENTENCES = [
    {"text": "Chiều hôm đó trời đổ mưa rất lớn trên con phố nhỏ ven sông."},
    {"text": "Câu chuyện ấy về sau tôi vẫn còn nhớ mãi đến tận bây giờ."},
]

# Ledger VI PHAM co y: ep_02 + ep_03 deu family_regret, cach nhau 1 tap (<3) -> pillar_distance FAIL.
_VIOLATING_LEDGER = {
    "ep_02": {"primary_event": {"regret_sub": {"value": "REG_FAM_001 - Me doi con ve Tet"}}},
    "ep_03": {"primary_event": {"regret_sub": {"value": "REG_FAM_002 - Cha cho con o cong truong"}}},
}

# Ledger SACH: 3 pillar khac nhau, khong lap gan -> 0 vi pham variety.
_CLEAN_LEDGER = {
    "ep_02": {"primary_event": {"regret_sub": {"value": "REG_FAM_001 - Me doi con ve Tet"}}},
    "ep_03": {"primary_event": {"regret_sub": {"value": "REG_LOV_001 - Nguoi yeu cu"}}},
    "ep_04": {"primary_event": {"regret_sub": {"value": "REG_PRO_001 - Loi hua do dang"}}},
}


def test_preflight_has_regret_variety_gate_wired(tmp_path):
    """DEBT-037 (a) — BEHAVIORAL unwire-guard (thay ban grep-thuan cu, xem block comment tren).

    Nhanh 1 (VI PHAM): chay full pipeline svhmp_preflight_qa.py voi ledger 2 tap family
    lien ke -> gate PHAI chan: exit != 0 VA 'R-REGRET-VARIETY' xuat hien trong output.
    Neu ai unwire (thay call that bang `_rv_issues = []`) -> issue bien mat, spec sach nen
    exit ve 0 -> ca 2 assert duoi FAIL (day la mutation kill that su, khac ban grep cu).

    Nhanh 2 (SACH): cung spec sach + ledger 3 pillar khac nhau -> gate KHONG dong gop
    issue nao -> 'R-REGRET-VARIETY' vang mat VA pipeline PASS (exit 0) -> chong over-tighten.
    """
    # --- Nhanh VI PHAM: gate phai chan ---
    viol = _run_preflight_e2e(tmp_path / "viol", _VIOLATING_LEDGER, _CLEAN_SPEC_SENTENCES)
    out_viol = viol.stdout + viol.stderr
    assert viol.returncode != 0, (
        f"Ledger vi pham nhung preflight KHONG chan (exit={viol.returncode}) — "
        f"REGRET_VARIETY_GATE co the da bi unwire.\nOUTPUT:\n{out_viol}"
    )
    assert "R-REGRET-VARIETY" in out_viol, (
        f"Ledger vi pham nhung khong thay issue R-REGRET-VARIETY trong output — "
        f"gate khong con block duoc (unwire?).\nOUTPUT:\n{out_viol}"
    )

    # --- Nhanh SACH: gate khong duoc chan ---
    clean = _run_preflight_e2e(tmp_path / "clean", _CLEAN_LEDGER, _CLEAN_SPEC_SENTENCES)
    out_clean = clean.stdout + clean.stderr
    assert "R-REGRET-VARIETY" not in out_clean, (
        f"Input SACH nhung gate van bao vi pham (over-tighten).\nOUTPUT:\n{out_clean}"
    )
    assert clean.returncode == 0, (
        f"Input SACH (spec + ledger) nhung preflight FAIL (exit={clean.returncode}) — "
        f"co the spec text vo tinh vi pham rule khac, hoac gate over-tighten.\nOUTPUT:\n{out_clean}"
    )
    # BO SUNG (R215.5: grep CHI dung BO SUNG, khong thay the) — 2 assert grep cu lam smoke nhanh,
    # nam TRONG test behavioral nay (da co subprocess-marker) nen KHONG phai standalone grep-only
    # guard (khong bi test_no_greponly_wiring_guards flag). Reconcile DEBT-037a+b, CMD_AUDIT 16/7.
    src = (REPO / "tools" / "svhmp_preflight_qa.py").read_text(encoding="utf-8")
    assert "check_regret_variety" in src, "REGRET_VARIETY_GATE bi go khoi svhmp_preflight_qa.py (unwire!)"
    assert "R-REGRET-VARIETY" in src, "issues.append prefix R-REGRET-VARIETY bi go (gate khong con block duoc)"
