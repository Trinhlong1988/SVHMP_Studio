"""DEBT-026 (Mr.Long 11/7): character_balance_report.py wired vao ci_gate che do WARN-only.

R215 mutation-proof — 4 test khoa dung 3 thuoc tinh cua quyet dinh:
 1. test_char_balance_wired_warn      : phai co trong WARN_CHECKS (go wiring -> FAIL).
 2. test_char_balance_not_blocking    : KHONG duoc nam trong CHECKS (blocking). Neu ai
    "nang cap" thanh blocking khi roster chua can bang -> chan moi push -> test FAIL.
 3. test_extract_warn_flags_catches   : ham trich flag bat dung dong ⚠ / FLAG LECH
    (test bang input tong hop, KHONG phu thuoc roster live -> mutation-proof that su).
 4. test_run_warn_checks_no_exit      : run_warn_checks() chay that, tra ve entry
    'char_balance' dang list, KHONG raise SystemExit (chung minh WARN khong chan).
"""
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("ci_gate_dbt026", REPO / "tools" / "ci_gate.py")
ci_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ci_gate)


def test_char_balance_wired_warn():
    names = [n for n, _ in ci_gate.WARN_CHECKS]
    assert "char_balance" in names, (
        "DEBT-026: character_balance_report PHAI duoc wire WARN-only vao ci_gate.WARN_CHECKS")
    rel = dict(ci_gate.WARN_CHECKS)["char_balance"]
    assert "character_balance_report" in rel


def test_char_balance_not_blocking():
    blocking = [rel for _, rel in ci_gate.CHECKS]
    assert not any("character_balance" in b for b in blocking), (
        "DEBT-026: WARN-only — character_balance KHONG duoc nam trong CHECKS (blocking list), "
        "neu khong se chan moi push khi roster con lech 4 target")


def test_extract_warn_flags_catches():
    # Input tong hop (giong dung format character_balance_report in ra) — khong doc roster that.
    sample = (
        "=== CHARACTER BALANCE REPORT — 139 passenger ===\n"
        "  child   :   8.6% (12)   target 10-15%\n"
        "=== 4 FLAG LECH CAN BANG ===\n"
        "  ⚠ child 8.6% < target 10-15%\n"
        "  ⚠ elderly 12.9% < target 15-20%\n"
        "binh thuong khong flag\n"
    )
    flags = ci_gate.extract_warn_flags(sample)
    assert any("child" in f for f in flags)
    assert any("FLAG LECH" in f for f in flags)
    assert len(flags) >= 3, f"phai bat >=3 dong canh bao, duoc {len(flags)}: {flags}"
    # Khong co canh bao -> list rong (khong false-positive)
    assert ci_gate.extract_warn_flags("chay ok, khong lech gi\n") == []


def test_run_warn_checks_no_exit():
    try:
        results = dict(ci_gate.run_warn_checks())
    except SystemExit:
        pytest.fail("run_warn_checks() KHONG duoc sys.exit — WARN-only phai non-blocking")
    assert "char_balance" in results, "run_warn_checks phai chay char_balance that"
    assert isinstance(results["char_balance"], list)
