"""Gate F1 — git hooks PHAI duoc wire (deep-audit 2/7).

Bug goc (deep-audit): .githooks/ ton tai + pre-push goi ci_gate, NHUNG
`git config core.hooksPath` RONG tren clone moi -> git dung .git/hooks/ (trong)
-> pre-commit/pre-push INERT -> ci_gate KHONG BAO GIO chay khi push.
Ky luc do hook 'built nhung chua wire' (giong bug cap_peak R198).

Test nay:
  1. Kiem cac hook file con nguyen ven + tro dung gate (portable, doc file).
  2. Self-heal + assert core.hooksPath=.githooks (dam bao hooks that su active
     o moi may ci_gate chay qua -> khong bao gio inert am tham nua).
pytest-native -> chay trong `pytest tests/` va ci_gate.
"""
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOOKS = REPO / ".githooks"


def _git(*args):
    r = subprocess.run(["git", "-C", str(REPO), *args],
                       capture_output=True, text=True)
    return r.returncode, (r.stdout or "").strip()


def test_hook_files_intact():
    for name in ("pre-commit", "pre-push"):
        p = HOOKS / name
        assert p.exists(), f".githooks/{name} missing"
        assert p.stat().st_size > 0, f".githooks/{name} empty"


def test_pre_push_invokes_ci_gate():
    txt = (HOOKS / "pre-push").read_text(encoding="utf-8")
    assert "ci_gate.py" in txt, "pre-push khong goi ci_gate.py -> push khong duoc gate"


def test_pre_commit_delegates_to_python_orchestrator():
    # F1c: hook la wrapper sh mong -> Python (MinGit khong co bash/coreutils).
    txt = (HOOKS / "pre-commit").read_text(encoding="utf-8")
    assert txt.startswith("#!/bin/sh"), "pre-commit phai la sh (MinGit khong co bash)"
    assert "git_hook_pre_commit.py" in txt, "pre-commit khong goi orchestrator Python"


def test_pre_commit_orchestrator_has_core_guards():
    orch = (REPO / "tools" / "git_hook_pre_commit.py").read_text(encoding="utf-8")
    for kw in ("check_rule_id_free", "check_rule_mention_codified", "post_render_gate"):
        assert kw in orch, f"orchestrator thieu guard: {kw}"


def test_hooks_are_sh_not_bash():
    # MinGit khong co bash.exe -> hook #!/bin/bash se 'cannot spawn' -> INERT.
    for name in ("pre-commit", "pre-push", "commit-msg"):
        first = (HOOKS / name).read_text(encoding="utf-8").splitlines()[0]
        assert first.strip() == "#!/bin/sh", f"{name} shebang='{first}' (phai /bin/sh)"


def test_hooks_are_lf_not_crlf():
    """F1b: CRLF o dong shebang -> git 'cannot spawn' -> hook INERT.
    .gitattributes giu LF; test nay chan regression neu ai checkout ra CRLF."""
    for name in ("pre-commit", "pre-push", "commit-msg"):
        raw = (HOOKS / name).read_bytes()
        first_lf = raw.find(b"\n")
        assert first_lf > 0, f"{name}: no newline"
        assert raw[first_lf - 1] != 0x0D, (
            f".githooks/{name} co CRLF o shebang -> git khong spawn duoc")


def test_hooks_path_activated_selfheal():
    """core.hooksPath PHAI = .githooks; neu chua thi set (self-heal) roi assert.
    Nho vay bat ky may nao chay ci_gate/pytest se KICH HOAT hook -> het inert."""
    _, cur = _git("config", "--get", "core.hooksPath")
    if cur != ".githooks":
        _git("config", "core.hooksPath", ".githooks")
        _, cur = _git("config", "--get", "core.hooksPath")
    assert cur == ".githooks", f"core.hooksPath='{cur}' (hooks se INERT)"
