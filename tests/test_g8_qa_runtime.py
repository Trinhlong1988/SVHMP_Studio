"""test_g8_qa_runtime.py — G8 D7 gate: wire + unwire-guard 2 LOP + invariant that.

Mirror pattern test_g3_dialogue.py (D7). G8 = RECONCILE domain qa_runtime — gate
tools/g8_qa_runtime_check.py canh gac 6 invariant (D2 domain / D4 pack5-19 / VNQA H1-H10 /
DEBT-005 golden_lock / D5 verdict schema / D3 pause delegation, them 9/7 sau khi CMD_AUDIT
phat hien D3 thieu bao ve). G8 la stage CUOI cua ci_gate.CHECKS (sau G7_generator).

Guard chong de-quy: gate g8_qa_runtime_check.py la STATIC-check (khong goi pytest), nen file
test nay KHONG bi chay long trong gate — khong can bien SVHMP_G3_GATE_PYTEST_RUNNING.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))


# ============================================================
# Invariant THAT — goi truc tiep ham check cua gate (khong chi test wiring)
# ============================================================

def test_g8_gate_passes_standalone():
    """Gate chay standalone phai exit 0 (6/6 invariant xanh o trang thai repo hien tai)."""
    r = subprocess.run(
        [sys.executable, str(REPO / "tools" / "g8_qa_runtime_check.py")],
        capture_output=True, text=True, cwd=str(REPO), encoding="utf-8",
    )
    assert r.returncode == 0, r.stdout + r.stderr


def test_g8_each_invariant_reports_pass():
    """Goi tung ham check truc tiep — moi invariant tra (True, ...)."""
    import g8_qa_runtime_check as g8
    for name, fn in g8.SUITE:
        ok, detail = fn()
        assert ok, f"invariant {name} FAIL: {detail}"


def test_g8_gate_fails_when_invariant_broken(monkeypatch):
    """Unwire-guard cho CHINH gate: neu 1 invariant gia lap FAIL, main() phai exit 1
    (bat truong hop ai lam gate luon-xanh vo dieu kien)."""
    import g8_qa_runtime_check as g8
    patched = [(k, fn) for (k, fn) in g8.SUITE if k != "DEBT005_golden_lock"]
    patched.append(("DEBT005_golden_lock", lambda: (False, "gia lap FAIL")))
    monkeypatch.setattr(g8, "SUITE", patched)
    assert g8.main() == 1, "gate phai exit 1 khi co invariant FAIL"


# ============================================================
# D7 — wire + unwire-guard 2 LOP trong ci_gate.CHECKS
# ============================================================

def test_g8_qa_runtime_stage_wired_in_ci_gate():
    """Lop (a) — grep TINH: 'G8_qa_runtime' phai co mat trong CHECKS THAT, la stage CUOI,
    ngay SAU G7_generator; STAGE_CODES co ma."""
    import ci_gate
    assert ('G8_qa_runtime', 'tools/g8_qa_runtime_check.py') in ci_gate.CHECKS, \
        'stage G8_qa_runtime bi go khoi ci_gate CHECKS (unwire!)'
    keys = [k for k, _ in ci_gate.CHECKS]
    assert keys[-1] == 'G8_qa_runtime', 'G8_qa_runtime phai la stage CUOI'
    assert keys[keys.index('G8_qa_runtime') - 1] == 'G7_generator', \
        'G8_qa_runtime phai dat NGAY SAU G7_generator'
    assert 'G8_qa_runtime' in ci_gate.STAGE_CODES, 'thieu ma STAGE_CODES cho G8_qa_runtime'
    src = (REPO / 'tools' / 'ci_gate.py').read_text(encoding='utf-8')
    assert "'G8_qa_runtime'" in src, 'grep tinh tren SOURCE THAT (khong chi object in-memory)'


def test_g8_qa_runtime_unwire_guard_behavior_changes_when_removed(monkeypatch):
    """Lop (b) — monkeypatch xoa stage TAM roi assert CHECKS thay doi that (bat truong hop
    lop (a) bi vo hieu). Cac stage con lai giu nguyen thu tu."""
    import ci_gate
    orig = list(ci_gate.CHECKS)
    patched = [c for c in orig if c[0] != 'G8_qa_runtime']
    assert len(patched) == len(orig) - 1, 'stage phai ton tai truoc khi test nay chay'
    monkeypatch.setattr(ci_gate, 'CHECKS', patched)
    assert ('G8_qa_runtime', 'tools/g8_qa_runtime_check.py') not in ci_gate.CHECKS
    assert [k for k, _ in ci_gate.CHECKS] == [k for k, _ in orig if k != 'G8_qa_runtime']
