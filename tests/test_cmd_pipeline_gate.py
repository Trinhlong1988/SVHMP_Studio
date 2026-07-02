"""Test cmd_pipeline_gate — deep-audit (2/7). Helper thuan, khong tao worktree."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import cmd_pipeline_gate as pg  # noqa: E402


def _res(**kv):
    order = ["BUILD", "ARCH", "QA", "RELEASE", "OVERALL"]
    return [{"key": k, "status": kv[k]} for k in order if k in kv]


def test_all_pass_ready_for_owner_freeze():
    r = _res(BUILD="READY_FOR_AUDIT", ARCH="PASS", QA="PASS", RELEASE="PASS", OVERALL="PASS")
    final, action, failed = pg.decide(r)
    assert final == "READY_FOR_OWNER_FREEZE" and action == "Mr.Long" and failed is None


def test_build_not_ready_routes_build():
    final, action, failed = pg.decide(_res(BUILD="NOT_READY"))
    assert final == "NOT_READY" and action == "CMD_BUILD" and failed == "BUILD"


def test_arch_fail_routes_build():
    r = _res(BUILD="READY_FOR_AUDIT", ARCH="FAIL", QA="NOT_VERIFIED",
             RELEASE="NOT_VERIFIED", OVERALL="NOT_VERIFIED")
    final, action, failed = pg.decide(r)
    assert final == "FAIL_AT_ARCH" and action == "CMD_BUILD" and failed == "ARCH"


def test_qa_fail_routes_build():
    r = _res(BUILD="READY_FOR_AUDIT", ARCH="PASS", QA="FAIL",
             RELEASE="NOT_VERIFIED", OVERALL="NOT_VERIFIED")
    final, _, failed = pg.decide(r)
    assert final == "FAIL_AT_QA" and failed == "QA"


def test_missing_tool_not_verified():
    r = [{"key": "BUILD", "status": "READY_FOR_AUDIT"},
         {"key": "ARCH", "status": "PASS"},
         {"key": "RELEASE", "status": "NOT_VERIFIED", "missing": True}]
    final, action, _ = pg.decide(r)
    assert final == "NOT_VERIFIED" and action == "CMD_BUILD"


def test_read_build_ready_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(pg, "REPORTS", tmp_path)
    assert pg.read_build_ready()[0] == "NOT_READY"


def test_read_build_ready_yes(tmp_path, monkeypatch):
    (tmp_path / "build_report.md").write_text("READY FOR AUDIT = YES\n", encoding="utf-8")
    monkeypatch.setattr(pg, "REPORTS", tmp_path)
    assert pg.read_build_ready()[0] == "READY_FOR_AUDIT"


def test_read_build_ready_status_form(tmp_path, monkeypatch):
    (tmp_path / "build_report.md").write_text("x\nSTATUS: READY_FOR_AUDIT\n", encoding="utf-8")
    monkeypatch.setattr(pg, "REPORTS", tmp_path)
    assert pg.read_build_ready()[0] == "READY_FOR_AUDIT"


def test_read_build_ready_no(tmp_path, monkeypatch):
    (tmp_path / "build_report.md").write_text("READY FOR AUDIT = NO\n", encoding="utf-8")
    monkeypatch.setattr(pg, "REPORTS", tmp_path)
    assert pg.read_build_ready()[0] == "NOT_READY"


def test_pid_alive_self_and_invalid():
    assert pg._pid_alive(os.getpid()) is True
    assert pg._pid_alive(0) is False
