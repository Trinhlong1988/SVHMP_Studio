"""tests/test_qa_post_render_pause_delegation.py — protective test cho D3 dedup (pause).

CMD_AUDIT phat hien (9/7, qua mutation): sau khi D3 xoa reimplement logic trong
qa_post_render.py::audit_pause() va thay bang delegate qa_pause_silence.audit_array(),
KHONG co test/gate nao bao ve neu ai do go delegation nay (regression se khong bi bat boi
ca g8_qa_runtime_check.py lan architecture_registry_check.py - ca 2 chi kiem file ton tai/
domain map, khong kiem NOI DUNG ham).

3 lop bao ve (mirror pattern DEBT-005 tests/test_no_unlocked_ep01_writer.py):
  1. Dynamic proof: monkeypatch qa_pause_silence.audit_array thanh spy, goi audit_pause()
     that, xac nhan spy THAT SU duoc goi (khong chi text-grep ten ham).
  2. Static proof: dung LAI ham thuan _pause_delegation_body_ok() cua g8_qa_runtime_check.py
     (khong viet lai logic parse, R211) tren source that.
  3. Mutation-proof: mutate source TRONG BO NHO (go dong goi delegation) -> ham thuan PHAI
     lat sang FAIL - chung minh check that su bat duoc, khong phai luon xanh vo dieu kien.
"""
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import qa_post_render as qpr  # noqa: E402
import qa_pause_silence as qps  # noqa: E402
from g8_qa_runtime_check import _pause_delegation_body_ok  # noqa: E402 - tai dung, khong viet lai (R211)


def test_audit_pause_calls_qa_pause_silence_audit_array_dynamic(monkeypatch):
    """Dynamic proof: monkeypatch qa_pause_silence.audit_array thanh spy, goi
    qpr.audit_pause() that, xac nhan spy THAT SU duoc goi voi dung audio/sr."""
    called = {}

    def spy(audio, sr, **kwargs):
        called["hit"] = True
        called["sr"] = sr
        called["kwargs"] = kwargs
        return {"pauses_detected": 3, "clean": 2, "ok": 0, "noisy": 1, "pass": True}

    monkeypatch.setattr(qps, "audit_array", spy)
    audio = np.zeros(22050 * 2, dtype=np.float32)
    result = qpr.audit_pause(audio, 22050, min_pause_ms=1200, pass_thr_db=-70, margin_ms=100)

    assert called.get("hit") is True, (
        "audit_pause() KHONG goi qa_pause_silence.audit_array() - delegation D3 bi mat (regression)")
    assert called["sr"] == 22050
    # audit_pause() PHAI map key tu ket qua audit_array (pauses_detected->total, giu nguyen clean/noisy/pass)
    assert result == {"total": 3, "clean": 2, "noisy": 1, "pass": True}, (
        f"audit_pause() khong map dung key tu qa_pause_silence.audit_array(): {result}")


def test_audit_pause_source_delegation_ok_on_real_file():
    """Static proof tren source THAT: tai dung _pause_delegation_body_ok() cua gate
    (khong viet lai regex rieng - R211)."""
    src = (REPO / "tools" / "qa_post_render.py").read_text(encoding="utf-8")
    ok, detail = _pause_delegation_body_ok(src)
    assert ok, f"audit_pause() source that dang FAIL check: {detail}"


def test_enforcement_detects_mutation_remove_delegation_call():
    """MUTATION PROOF #1: go dong goi qa_pause_silence.audit_array() khoi source (chi trong
    bo nho) -> _pause_delegation_body_ok() PHAI lat tu PASS sang FAIL."""
    src = (REPO / "tools" / "qa_post_render.py").read_text(encoding="utf-8")
    ok_before, _ = _pause_delegation_body_ok(src)
    assert ok_before, "tien de: source that phai dang PASS truoc khi mutate"

    # Chi thay THE loi GOI THAT (co tham so "audio") trong body ham, KHONG dung docstring
    # chi nhac ten ham "qa_pause_silence.audit_array()" (rong, 0 tham so).
    m = re.search(r"def audit_pause\(.*?\n(?=def |\Z)", src, re.DOTALL)
    assert m, "khong tim thay ham audit_pause() de mutate"
    body = m.group(0)
    mutated_body = re.sub(
        r"qa_pause_silence\.audit_array\(\s*audio[^)]*\)",
        '{"pauses_detected": 0, "clean": 0, "noisy": 0, "pass": True}',
        body, count=1,
    )
    assert not re.search(r"qa_pause_silence\.audit_array\(\s*audio\b", mutated_body), (
        "mutation khong thanh cong - regex thay the sai")
    mutated = src.replace(body, mutated_body)
    ok_after, detail_after = _pause_delegation_body_ok(mutated)
    assert not ok_after, (
        f"MUTATION khong bi bat - go delegation nhung check van PASS: {detail_after}. "
        "Enforcement test rong, khong bao ve duoc gi.")


def test_enforcement_detects_mutation_reintroduce_raw_detection_loop():
    """MUTATION PROOF #2: chen lai vong lap detect tho (win_n/energy_db, dau hieu quay ve
    reimplement thay vi delegate) vao body audit_pause() -> PHAI lat sang FAIL du van con
    cau goi delegation (bat truong hop 'vua goi vua tu tinh lai', khong chi xoa trang goi)."""
    src = (REPO / "tools" / "qa_post_render.py").read_text(encoding="utf-8")
    m = re.search(r"def audit_pause\(.*?\n(?=def |\Z)", src, re.DOTALL)
    assert m, "khong tim thay ham audit_pause() de mutate"
    body = m.group(0)
    mutated_body = body.rstrip() + "\n    win_n = int(0.020 * sr)  # REINTRODUCED_STUB\n\n"
    mutated_src = src.replace(body, mutated_body)

    ok_after, detail_after = _pause_delegation_body_ok(mutated_src)
    assert not ok_after, (
        f"MUTATION (chen lai vong lap detect tho) khong bi bat: {detail_after} - "
        "check khong phat hien nhan doi logic quay tro lai")
