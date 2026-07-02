"""Test audit_clean — deep-audit (2/7). Test helper thuan (khong tao worktree)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import audit_clean as ac  # noqa: E402


def test_gate_cmds_default_only_ci_gate():
    cmds = ac.gate_cmds("/wt", "py", with_freeze=False)
    labels = [c[0] for c in cmds]
    assert labels == ["ci_gate"]
    assert cmds[0][1][0] == "py"
    assert cmds[0][1][1].endswith("ci_gate.py")


def test_gate_cmds_with_freeze_adds_freeze_gate():
    cmds = ac.gate_cmds("/wt", "py", with_freeze=True)
    labels = [c[0] for c in cmds]
    assert labels == ["ci_gate", "freeze_gate"]
    assert "--skip-remote" in cmds[1][1]


def test_gate_cmds_paths_rooted_at_worktree():
    cmds = ac.gate_cmds("/somewt", "py", with_freeze=True)
    for _, argv in cmds:
        assert argv[1].startswith("/somewt") or "somewt" in argv[1]
