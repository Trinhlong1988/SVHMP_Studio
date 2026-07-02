"""
cmd_progress_logger.py — R176 enforcement
Mr.Long lock 30/6 16:50.

Realtime progress log mandatory for all long-running CMD tasks
so any other CMD (or next session) can resume after crash/kill.

Usage:
    # Write/start
    from cmd_progress_logger import ProgressLog
    log = ProgressLog(cmd="CMD_THUC_THI", task_id="B60_v108_fix")
    log.start(pending=["edit_md", "render_cliff", "concat", "ship"])
    log.complete_step("edit_md")
    log.set_current("render_cliff", subprocess_pid=12345)
    log.heartbeat()
    log.add_file("output/ep_01/episode.md")
    log.block(type="gpu_busy", reason="payoff render PID 53296")
    log.unblock()
    log.finish()

    # Read/resume (other CMD or next session)
    log = ProgressLog.load("CMD_THUC_THI")
    if log and log.data["status"] == "in_progress":
        print(f"Resume from: {log.data['pending_steps'][0]}")

    # CLI verify
    python tools/cmd_progress_logger.py --verify
"""
from __future__ import annotations
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
PROGRESS_DIR = REPO_ROOT / "runtime" / "cmd_progress"
PROGRESS_DIR.mkdir(parents=True, exist_ok=True)


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


class ProgressLog:
    def __init__(self, cmd: str, task_id: str, path: Optional[Path] = None):
        self.cmd = cmd
        self.task_id = task_id
        self.path = path or (PROGRESS_DIR / f"{cmd}_current.json")
        self.data: dict = {}
        if self.path.exists():
            try:
                self.data = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                self.data = {}

    def _flush(self) -> None:
        self.data["last_heartbeat_at"] = _now()
        tmp = self.path.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(self.path)

    def start(self, pending: list[str], notes: str = "") -> None:
        self.data = {
            "cmd": self.cmd,
            "task_id": self.task_id,
            "started_at": _now(),
            "last_heartbeat_at": _now(),
            "status": "in_progress",
            "current_step": pending[0] if pending else None,
            "completed_steps": [],
            "pending_steps": list(pending),
            "files_touched": [],
            "subprocess_pids": [],
            "blockers": [],
            "notes": notes,
            "resume_instructions": (
                "Read this file -> identify pending_steps[0] -> execute. "
                "If subprocess_pids alive -> wait + monitor; else re-run step."
            ),
        }
        self._flush()

    def heartbeat(self) -> None:
        self._flush()

    def complete_step(self, step: str) -> None:
        if step in self.data.get("pending_steps", []):
            self.data["pending_steps"].remove(step)
        if step not in self.data.get("completed_steps", []):
            self.data.setdefault("completed_steps", []).append(step)
        if self.data.get("pending_steps"):
            self.data["current_step"] = self.data["pending_steps"][0]
        self._flush()

    def set_current(self, step: str, subprocess_pid: Optional[int] = None) -> None:
        self.data["current_step"] = step
        if subprocess_pid is not None:
            pids = self.data.setdefault("subprocess_pids", [])
            if subprocess_pid not in pids:
                pids.append(subprocess_pid)
        self._flush()

    def add_pending(self, step: str) -> None:
        self.data.setdefault("pending_steps", []).append(step)
        self._flush()

    def add_file(self, path: str) -> None:
        files = self.data.setdefault("files_touched", [])
        if path not in files:
            files.append(path)
        self._flush()

    def block(self, type: str, reason: str) -> None:
        self.data["status"] = "blocked"
        self.data.setdefault("blockers", []).append(
            {"type": type, "reason": reason, "since_ts": _now()}
        )
        self._flush()

    def unblock(self) -> None:
        self.data["status"] = "in_progress"
        self.data["blockers"] = []
        self._flush()

    def finish(self) -> None:
        self.data["status"] = "completed"
        self.data["finished_at"] = _now()
        self.data["current_step"] = None
        self._flush()

    def fail(self, reason: str) -> None:
        self.data["status"] = "failed"
        self.data["failed_at"] = _now()
        self.data["fail_reason"] = reason
        self._flush()

    @classmethod
    def load(cls, cmd: str) -> Optional["ProgressLog"]:
        path = PROGRESS_DIR / f"{cmd}_current.json"
        if not path.exists():
            return None
        inst = cls(cmd=cmd, task_id="loaded", path=path)
        inst.task_id = inst.data.get("task_id", "unknown")
        return inst

    @classmethod
    def list_all(cls) -> list[dict]:
        out = []
        for f in sorted(PROGRESS_DIR.glob("*_current.json")):
            try:
                out.append(json.loads(f.read_text(encoding="utf-8")))
            except Exception:
                pass
        return out


def _verify_cli() -> int:
    logs = ProgressLog.list_all()
    if not logs:
        print("[R176] No active CMD progress logs found.")
        return 0
    print(f"[R176] {len(logs)} CMD progress log(s):")
    for d in logs:
        cmd = d.get("cmd", "?")
        task = d.get("task_id", "?")
        status = d.get("status", "?")
        step = d.get("current_step", "?")
        hb = d.get("last_heartbeat_at", "?")
        done = len(d.get("completed_steps", []))
        pending = len(d.get("pending_steps", []))
        print(f"  - {cmd} / {task}")
        print(f"      status={status} step={step} hb={hb} done={done} pending={pending}")
        for b in d.get("blockers", []):
            print(f"      BLOCK {b.get('type')}: {b.get('reason')} since {b.get('since_ts')}")
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if "--verify" in sys.argv or "-v" in sys.argv:
        sys.exit(_verify_cli())
    print(__doc__)
