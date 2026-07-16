"""
DEBT-hook (16/7): tools/promotion_guard.py::_git PHAI capture git output bang
encoding='utf-8', errors='replace' — KHONG duoc de text=True mac dinh (Windows
= cp1252) vi git output cua range push (commit message tieng Viet co dau qua
_range_messages, hoac byte nhi phan) lam reader-thread subprocess crash
UnicodeDecodeError (byte 0x90...). Bug that quan sat: trace pre-push 16/7.

Mutation-proof (R215.1/R215.5 — behavioral, KHONG grep-only):
  1. test_git_reads_vietnamese_commit_message_roundtrip  — dung repo git that co
     commit message dau tieng Viet, _git tra ve dung chuoi (end-to-end decode OK).
  2. test_cp1252_would_raise_on_same_input                — chung minh CHINH input do
     lam cp1252 crash (neu bo encoding='utf-8' tren Windows se FAIL) -> anchor byte.
  3. test_git_passes_utf8_replace_kwargs                  — introspect call runtime:
     _git PHAI truyen encoding='utf-8' + errors='replace'. Go 1 trong 2 -> test FAIL
     (deterministic moi OS, la mutation anchor chinh).
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import promotion_guard  # noqa: E402

VN_MSG = "Hạ Vy đêm mưa cuói tháng tư"
VN_NEEDLE = "Hạ Vy"  # "Hạ Vy"


def _make_repo(tmp_path):
    repo = tmp_path / "r"
    repo.mkdir()

    def run(*a):
        subprocess.run(list(a), cwd=repo, check=True, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")

    run("git", "init", "-q")
    run("git", "config", "user.email", "t@t.t")
    run("git", "config", "user.name", "Tester")
    run("git", "config", "commit.gpgsign", "false")
    run("git", "config", "core.hooksPath", "/dev/null")  # khong chay hook repo test
    run("git", "commit", "--allow-empty", "-q", "-m", VN_MSG)
    return repo


def test_git_reads_vietnamese_commit_message_roundtrip(tmp_path):
    repo = _make_repo(tmp_path)
    out = promotion_guard._git(["log", "--format=%B", "-1"], cwd=str(repo))
    assert VN_NEEDLE in out, repr(out)


@pytest.mark.filterwarnings("ignore::pytest.PytestUnhandledThreadExceptionWarning")
def test_cp1252_cannot_faithfully_decode_same_input(tmp_path):
    """Anchor cross-OS: cp1252 KHONG the doc dung commit message do -> encoding matters.
    POSIX: raise UnicodeDecodeError (main thread). Windows: reader-thread crash bi nuot
    -> stdout mat/mangled (KHONG co needle) — guard se doc NHAM neu de cp1252. Ca 2 =
    'khong faithful' -> chung minh fix utf-8 la bat buoc."""
    repo = _make_repo(tmp_path)
    faithful = False
    try:
        r = subprocess.run(["git", "log", "--format=%B", "-1"], cwd=str(repo),
                           capture_output=True, text=True, encoding="cp1252")
        faithful = (r.stdout is not None) and (VN_NEEDLE in r.stdout)
    except UnicodeDecodeError:
        faithful = False
    assert not faithful, "cp1252 khong nen doc dung duoc — neu doc dung thi input khong con thach thuc encoding"


def test_git_passes_utf8_replace_kwargs(monkeypatch):
    """Mutation anchor deterministic: _git PHAI truyen encoding='utf-8'+errors='replace'."""
    captured = {}

    class _R:
        stdout = ""

    def fake_run(*a, **k):
        captured.update(k)
        return _R()

    monkeypatch.setattr(promotion_guard.subprocess, "run", fake_run)
    promotion_guard._git(["log"])
    assert captured.get("encoding") == "utf-8", captured
    assert captured.get("errors") == "replace", captured
