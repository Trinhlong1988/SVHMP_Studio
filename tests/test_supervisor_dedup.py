"""Test qa_watch_supervisor single-instance (deep-audit 2/7 supervisor-dedup).
Ten KHONG dat 'test_qa_*' vi conftest collect_ignore_glob nuot -> orphan."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import qa_watch_supervisor as sup  # noqa: E402


def test_pid_alive_invalid_is_false():
    assert sup._pid_alive(0) is False
    assert sup._pid_alive(-1) is False


def test_pid_alive_self_is_true():
    assert sup._pid_alive(os.getpid()) is True


def test_acquire_first_writes_lock(tmp_path, monkeypatch):
    lock = tmp_path / "sup.lock"
    monkeypatch.setattr(sup, "SUP_LOCK", lock)
    ok, other = sup.acquire_single_instance()
    assert ok is True and other is None
    assert lock.read_text(encoding="utf-8").strip() == str(os.getpid())


def test_acquire_dead_pid_overwrites(tmp_path, monkeypatch):
    lock = tmp_path / "sup.lock"
    lock.write_text("999999", encoding="utf-8")
    monkeypatch.setattr(sup, "SUP_LOCK", lock)
    monkeypatch.setattr(sup, "_pid_alive", lambda p: False)  # coi pid cu da chet
    ok, other = sup.acquire_single_instance()
    assert ok is True and other is None
    assert lock.read_text(encoding="utf-8").strip() == str(os.getpid())


def test_acquire_live_foreign_blocks(tmp_path, monkeypatch):
    lock = tmp_path / "sup.lock"
    lock.write_text("12345", encoding="utf-8")
    monkeypatch.setattr(sup, "SUP_LOCK", lock)
    monkeypatch.setattr(sup, "_pid_alive", lambda p: True)  # ban cu con song
    ok, other = sup.acquire_single_instance()
    assert ok is False and other == 12345
