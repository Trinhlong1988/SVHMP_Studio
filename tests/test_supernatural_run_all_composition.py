"""tests/test_supernatural_run_all_composition.py — Bug #2 (TASK_AUDIT_CRITICAL_G3_G5.md).

CMD_AUDIT phat hien (10/7, workflow da-agent 9-10/7, tu mutation song xac nhan): test DUY
NHAT goi run_all() (tests/test_supernatural_validator.py:30) chi assert run_all()==[] tren
du lieu SACH - khong co test nao xac nhan CA 3 sub-check THAT SU duoc cong don. Neu ai vo
tinh xoa 1/3 hoac ca 3 dong "errs += check_*()" trong run_all(), gate g5_supernatural_check.py
(chay run_all() qua CI) van bao PASS tren du lieu sach - mat kha nang phat hien loi that.

Mirror pattern D3 (tests/test_qa_post_render_pause_delegation.py): dung LAI ham thuan
_run_all_body_ok() cua chinh supernatural_validator.py (R211, khong viet lai logic), mutation-
proof tren CA 3 sub-check rieng biet (khong chi 1) de dam bao khong sub-check nao bi "quen".
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from supernatural_validator import _run_all_body_ok, run_all  # noqa: E402


def test_run_all_body_ok_on_real_source():
    """Static proof tren source THAT: run_all() dang goi du 3/3 sub-check."""
    src = (REPO / "tools" / "supernatural_validator.py").read_text(encoding="utf-8")
    ok, detail = _run_all_body_ok(src)
    assert ok, f"run_all() source that dang FAIL check: {detail}"


def test_run_all_returns_clean_on_good_data():
    """Sanity giu nguyen hanh vi cu (khong doi test hien co): du lieu sach -> []."""
    assert run_all() == []


def _mutate_remove_call(src, sub_check_call):
    """Go dung 1 dong 'errs += check_X()' khoi body run_all() (chi trong bo nho)."""
    m = re.search(r"def run_all\(.*?\n(?=def |\Z)", src, re.DOTALL)
    assert m, "khong tim thay ham run_all()"
    body = m.group(0)
    line_to_remove = f"    errs += {sub_check_call}\n"
    assert line_to_remove in body, f"dong '{line_to_remove.strip()}' khong ton tai trong body - kiem tra lai format that"
    mutated_body = body.replace(line_to_remove, "", 1)
    assert mutated_body != body
    return src.replace(body, mutated_body)


_ALL_THREE_SUB_CHECKS = [
    "check_typology()",
    "check_possession_state_machine()",
    "check_no_duplicate_compliance_files()",
]


def test_enforcement_detects_mutation_remove_check_typology():
    """MUTATION-PROOF sub-check #1/3: go 'errs += check_typology()' -> check PHAI FAIL."""
    src = (REPO / "tools" / "supernatural_validator.py").read_text(encoding="utf-8")
    mutated = _mutate_remove_call(src, "check_typology()")
    ok, detail = _run_all_body_ok(mutated)
    assert not ok, f"MUTATION (go check_typology) khong bi bat: {detail}"
    assert "check_typology" in detail


def test_enforcement_detects_mutation_remove_check_possession_state_machine():
    """MUTATION-PROOF sub-check #2/3: go 'errs += check_possession_state_machine()' -> FAIL."""
    src = (REPO / "tools" / "supernatural_validator.py").read_text(encoding="utf-8")
    mutated = _mutate_remove_call(src, "check_possession_state_machine()")
    ok, detail = _run_all_body_ok(mutated)
    assert not ok, f"MUTATION (go check_possession_state_machine) khong bi bat: {detail}"
    assert "check_possession_state_machine" in detail


def test_enforcement_detects_mutation_remove_check_no_duplicate_compliance_files():
    """MUTATION-PROOF sub-check #3/3: go 'errs += check_no_duplicate_compliance_files()' -> FAIL.
    Day la sub-check DE BI QUEN NHAT (cuoi danh sach) - dam bao khong sub-check nao duoc
    "mien tru" khoi bao ve, dung 3/3 nhu task yeu cau."""
    src = (REPO / "tools" / "supernatural_validator.py").read_text(encoding="utf-8")
    mutated = _mutate_remove_call(src, "check_no_duplicate_compliance_files()")
    ok, detail = _run_all_body_ok(mutated)
    assert not ok, f"MUTATION (go check_no_duplicate_compliance_files) khong bi bat: {detail}"
    assert "check_no_duplicate_compliance_files" in detail


def test_enforcement_detects_mutation_remove_all_three():
    """MUTATION-PROOF toan phan: go CA 3 dong (mo phong dung kich ban CMD_AUDIT tu mutation
    song da xac nhan - xoa het 3 sub-check van co the PASS neu khong co test nay) -> FAIL,
    liet ke du 3/3 sub-check con thieu."""
    src = (REPO / "tools" / "supernatural_validator.py").read_text(encoding="utf-8")
    mutated = src
    for call in _ALL_THREE_SUB_CHECKS:
        mutated = _mutate_remove_call(mutated, call)
    ok, detail = _run_all_body_ok(mutated)
    assert not ok
    for call in _ALL_THREE_SUB_CHECKS:
        assert call in detail, f"mutation toan phan nhung detail thieu bao cao {call}: {detail}"


def test_injection_bad_typology_data_propagates_through_run_all(monkeypatch):
    """Option (b) bo sung (khong thay the (a), lam them cho chac): inject 1 case bad-data
    THAT (mirror M2 cua test_supernatural_validator.py) qua CHINH run_all() (khong goi thang
    check_typology()) - xac nhan loi VAN propagate ra ngoai qua duong composition day du."""
    import supernatural_validator as sv

    def bad_check_typology():
        return ["INJECTED: quyen nang gia khong co trong typology (M2 mirror qua run_all)"]

    monkeypatch.setattr(sv, "check_typology", bad_check_typology)
    errs = sv.run_all()
    assert any("INJECTED" in e for e in errs), (
        "run_all() khong propagate loi tu check_typology() - composition vo hieu")


# ============================================================
# Follow-up 10/7 (per Mr.Long authorization, ping 09:30): wire _run_all_body_ok() vao
# tools/g5_supernatural_check.py lam invariant thu 2 - truoc do gate chay DOC LAP (ngoai
# pytest) khong bat duoc mutation xoa het composition (chi pytest test nay moi bat). Test
# duoi day BAO VE chinh viec WIRING do - chong ai go invariant nay khoi gate ma khong ai biet.
# ============================================================

def test_g5_gate_has_run_all_composition_invariant_wired():
    """Unwire-guard: g5_supernatural_check.SUITE PHAI co invariant 'run_all_composition' goi
    _run_all_body_ok() - neu bi go, gate quay lai khoang ho CMD_AUDIT da phat hien (chay doc
    lap ngoai pytest khong bat duoc mutation composition)."""
    sys.path.insert(0, str(REPO / "tools"))
    import g5_supernatural_check as g5c
    keys = [k for k, _ in g5c.SUITE]
    assert "run_all_composition" in keys, (
        "invariant 'run_all_composition' bi go khoi g5_supernatural_check.SUITE (unwire!)")
    src = (REPO / "tools" / "g5_supernatural_check.py").read_text(encoding="utf-8")
    assert "_run_all_body_ok" in src, "grep tinh tren SOURCE THAT (khong chi object in-memory)"


def test_g5_gate_pass_on_real_data():
    """Reality anchor: gate chay standalone (subprocess, dung dung cach CI goi) tren du lieu
    that PHAI PASS (2/2 invariant)."""
    import subprocess
    r = subprocess.run([sys.executable, str(REPO / "tools" / "g5_supernatural_check.py")],
                        capture_output=True, text=True, cwd=str(REPO), encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
