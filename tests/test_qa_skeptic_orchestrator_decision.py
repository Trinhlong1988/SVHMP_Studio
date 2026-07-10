"""Behavior test — qa_skeptic_orchestrator.orchestrate() decision tree (TASK_AUDIT_HIGH G8-5).

orchestrate() = verdict CUỐI của toàn hệ QA (Claude-QA + Skeptic + VNQA escalation) nhưng TRƯỚC
đây chưa từng được import/gọi trong bất kỳ test nào — đổi 1 nhánh `final = ...` vẫn xanh. Test này
gọi HÀM THẬT, mock RUNTIME_DIR + subprocess (skeptic/vnqa) để điều khiển input, assert final_verdict
cho MỌI nhánh cây quyết định (mutation-proof: đổi bất kỳ nhánh nào làm ít nhất 1 case vỡ).

KHÔNG sửa source (g8 LOCKED) — chỉ thêm test.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))
import qa_skeptic_orchestrator as orch  # noqa: E402

EP = 1


class _FakeProc:
    def __init__(self, rc=0):
        self.returncode = rc
        self.stdout = ""
        self.stderr = ""


def _install(tmp_path, monkeypatch, qa_verdict, skeptic_verdict=None, missed=None,
             vnqa_verdict=None, skeptic_rc=0):
    """Chuẩn bị: RUNTIME_DIR->tmp, ghi qa_output, mock subprocess ghi JSON skeptic/vnqa."""
    monkeypatch.setattr(orch, "RUNTIME_DIR", tmp_path)
    (tmp_path / f"qa_output_ep_{EP}.json").write_text(
        json.dumps({"verdict": qa_verdict, "verdict_reasoning": "r", "findings": []}),
        encoding="utf-8")

    def fake_run(cmd, **kw):
        joined = " ".join(str(c) for c in cmd)
        out = cmd[cmd.index("--output") + 1] if "--output" in cmd else None
        if "adversarial_skeptic.py" in joined:
            if out:
                Path(out).write_text(json.dumps(
                    {"final_verdict": skeptic_verdict, "missed_issues": missed or [],
                     "verdict_reasoning": "sk"}), encoding="utf-8")
            return _FakeProc(skeptic_rc)
        if "pipeline.py" in joined:  # VNQA
            if out:
                Path(out).write_text(json.dumps(
                    {"verdict": vnqa_verdict, "issues_count_by_severity": {"critical": 0}}),
                    encoding="utf-8")
            return _FakeProc(0)
        return _FakeProc(0)  # auto_fix (không dùng ở đây)

    monkeypatch.setattr(orch.subprocess, "run", fake_run)


def _final(tmp_path, monkeypatch, run_vnqa=False, **kw):
    _install(tmp_path, monkeypatch, **kw)
    res = orch.orchestrate(EP, str(tmp_path / "episode.md"),
                           run_vnqa=run_vnqa, run_autofix=False)
    return res


def test_qa_regen_short_circuits_no_skeptic(tmp_path, monkeypatch):
    res = _final(tmp_path, monkeypatch, qa_verdict="REGEN")
    assert res["final_verdict"] == "REGEN"
    assert res["skeptic_invoked"] is False


def test_accept_no_critical_missed_is_pass(tmp_path, monkeypatch):
    res = _final(tmp_path, monkeypatch, qa_verdict="PASS", skeptic_verdict="ACCEPT", missed=[])
    assert res["final_verdict"] == "PASS"


def test_accept_with_critical_missed_is_review_required(tmp_path, monkeypatch):
    res = _final(tmp_path, monkeypatch, qa_verdict="PASS", skeptic_verdict="ACCEPT",
                 missed=[{"severity": "critical", "desc": "x"}])
    assert res["final_verdict"] == "REVIEW_REQUIRED"


def test_skeptic_reject_is_regen(tmp_path, monkeypatch):
    res = _final(tmp_path, monkeypatch, qa_verdict="PASS", skeptic_verdict="REJECT")
    assert res["final_verdict"] == "REGEN"


def test_skeptic_needs_human_is_review_required(tmp_path, monkeypatch):
    res = _final(tmp_path, monkeypatch, qa_verdict="PASS", skeptic_verdict="NEEDS_HUMAN")
    assert res["final_verdict"] == "REVIEW_REQUIRED"


def test_skeptic_subprocess_fail_is_review_required(tmp_path, monkeypatch):
    res = _final(tmp_path, monkeypatch, qa_verdict="PASS", skeptic_verdict="ACCEPT", skeptic_rc=1)
    assert res["final_verdict"] == "REVIEW_REQUIRED"


def test_vnqa_fail_escalates_pass_to_regen(tmp_path, monkeypatch):
    res = _final(tmp_path, monkeypatch, run_vnqa=True, qa_verdict="PASS",
                 skeptic_verdict="ACCEPT", missed=[], vnqa_verdict="FAIL")
    assert res["final_verdict"] == "REGEN", "VNQA FAIL phải escalate PASS->REGEN"


def test_vnqa_warn_does_not_downgrade_pass(tmp_path, monkeypatch):
    res = _final(tmp_path, monkeypatch, run_vnqa=True, qa_verdict="PASS",
                 skeptic_verdict="ACCEPT", missed=[], vnqa_verdict="WARN")
    assert res["final_verdict"] == "PASS", "VNQA WARN KHÔNG được hạ PASS xuống REGEN"
