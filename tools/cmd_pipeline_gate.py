"""cmd_pipeline_gate.py — CMD PIPELINE COORDINATOR (machine-authoritative).

Nguon spec: Mr.Long + Desktop/CMD_QA_AUDIT_CONSTITUTION_v1.0.
Dieu phoi TUAN TU theo cong tren CLEAN COMMITTED REF (khong doc dirty working tree):
    BUILD_READY -> ARCH -> QA -> RELEASE -> OVERALL(auditor) -> Mr.Long FREEZE

KHONG reinvent auditor logic — tai su dung tool co san:
    ARCH    = tools/architecture_registry_check.py
    QA      = tools/ci_gate.py
    RELEASE = tools/freeze_gate.py  (neu ton tai)
    OVERALL = tools/auditor.py

Quy tac (xiet 2 chieu):
 - Gate N FAIL  -> gate N = FAIL; MOI gate sau = NOT_VERIFIED; action_route = CMD_BUILD; exit 1.
 - Thieu tool   -> gate = NOT_VERIFIED; exit 2.
 - TAT CA PASS  -> final = READY_FOR_OWNER_FREEZE; exit 0.
 - LOCK loai tru: 1 luc 1 pipeline (khong chong cheo).

CAM (theo lenh):
 - KHONG cho CMD chat tu khai PASS; KHONG parse 'STATUS: PASS' tu chat lam verdict.
 - KHONG tao tag; KHONG doi promotion_status; KHONG freeze.
 - Builder chi ket luan 'READY FOR AUDIT = YES/NO' (KHONG PASS/FREEZE/SHIP).

Output: reports/cmd_pipeline_gate_report.md + reports/cmd_pipeline_gate_report.json
Usage: python tools/cmd_pipeline_gate.py --ref origin/main [--skip-build] [--json]
Exit: 0 READY_FOR_OWNER_FREEZE | 1 gate FAIL / build not ready | 2 thieu tool / setup.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
PY = sys.executable
WT = SVHMP.parent / ".cmd_pipeline_wt"
REPORTS = SVHMP / "reports"
LOCK = SVHMP / "runtime" / "cmd_pipeline.lock"

# (key, argv[repo-relative])  — thu tu = thu tu cong
def build_gates(pack, tag, doc_test):
    """Cong may theo thu tu. RELEASE nham dung PACK dang xu ly (--pack)."""
    return [
        ("ARCH", ["tools/architecture_registry_check.py"]),
        ("QA", ["tools/ci_gate.py"]),
        ("RELEASE", ["tools/freeze_gate.py", "--skip-remote",
                     "--pack", pack, "--tag", tag, "--doc-test", doc_test]),
        ("OVERALL", ["tools/auditor.py"]),
    ]


def _pid_alive(pid):
    if pid <= 0:
        return False
    try:
        if sys.platform == "win32":
            import ctypes
            h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
            if h:
                ctypes.windll.kernel32.CloseHandle(h)
                return True
            return False
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def acquire_lock():
    try:
        if LOCK.exists():
            old = int((LOCK.read_text(encoding="utf-8") or "0").strip() or "0")
            if old and old != os.getpid() and _pid_alive(old):
                return False, old
        LOCK.parent.mkdir(exist_ok=True, parents=True)
        LOCK.write_text(str(os.getpid()), encoding="utf-8")
        return True, None
    except Exception as e:
        # FAIL-CLOSED (audit 3/7): loi doc/ghi lock KHONG duoc coi la chiem duoc
        # (fail-open cu cho 2 coordinator chay chong -> vi pham non-overlap).
        print(f"[pipeline] lock IO error ({e}) — fail-closed. Xoa {LOCK} neu chac khong co phien khac.")
        return False, "lock-io-error"


def release_lock():
    try:
        if LOCK.exists() and LOCK.read_text(encoding="utf-8").strip() == str(os.getpid()):
            LOCK.unlink()
    except Exception:
        pass


def _git(*a):
    return subprocess.run(["git", "-C", str(SVHMP), *a], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")


def _summary(text, n=6):
    return "\n".join((text or "").strip().splitlines()[-n:])


def read_build_ready():
    """Builder ky 'READY FOR AUDIT = YES/NO' HOAC 'STATUS: READY_FOR_AUDIT'."""
    f = REPORTS / "build_report.md"
    if not f.exists():
        return "NOT_READY", "reports/build_report.md thieu"
    t = f.read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?im)READY\s+FOR\s+AUDIT\s*=\s*YES", t) or \
       re.search(r"(?im)^STATUS:\s*READY_FOR_AUDIT\b", t):
        return "READY_FOR_AUDIT", "reports/build_report.md"
    return "NOT_READY", "build_report khong ky READY FOR AUDIT = YES"


def make_worktree(ref):
    release_wt()
    _git("worktree", "add", "--detach", str(WT), ref)  # lfs hook co the exit!=0
    head = subprocess.run(["git", "-C", str(WT), "rev-parse", "HEAD"],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout.strip()
    return head or None


def release_wt():
    _git("worktree", "remove", str(WT), "--force")
    _git("worktree", "prune")


def run_gate(argv):
    """-> (status, exitcode, cmd_str, summary). Thieu tool -> NOT_VERIFIED."""
    tool = WT / argv[0]
    cmd_str = "python " + " ".join(argv)
    if not tool.exists():
        return "NOT_VERIFIED", None, cmd_str, f"THIEU TOOL: {argv[0]}"
    r = subprocess.run([PY, str(tool)] + argv[1:], cwd=str(WT),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    status = "PASS" if r.returncode == 0 else "FAIL"
    return status, r.returncode, cmd_str, _summary(r.stdout + r.stderr)


def decide(results):
    """results: list dict(key,status,...). -> (final_status, action_route, failed).
    Tach de test."""
    d = {r["key"]: r["status"] for r in results}
    # thieu tool bat ky -> NOT_VERIFIED tong (khong the chung minh -> khong PASS)
    if any(r["status"] == "NOT_VERIFIED" and r.get("missing") for r in results):
        miss = [r["key"] for r in results if r.get("missing")]
        return "NOT_VERIFIED", "CMD_BUILD", f"THIEU TOOL: {miss}"
    if d.get("BUILD") == "NOT_READY":
        return "NOT_READY", "CMD_BUILD", "BUILD"
    for key in ["ARCH", "QA", "RELEASE", "OVERALL"]:
        if d.get(key) == "FAIL":
            return f"FAIL_AT_{key}", "CMD_BUILD", key
    if all(d.get(k) == "PASS" for k in ["ARCH", "QA", "RELEASE", "OVERALL"]):
        return "READY_FOR_OWNER_FREEZE", "Mr.Long", None
    return "NOT_VERIFIED", "CMD_BUILD", "incomplete"


def write_reports(state):
    REPORTS.mkdir(exist_ok=True, parents=True)
    (REPORTS / "cmd_pipeline_gate_report.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# CMD PIPELINE GATE — machine-authoritative report",
        "# Sinh boi tools/cmd_pipeline_gate.py — KHONG sua tay.",
        f"- ref: {state['ref']}",
        f"- resolved_commit: {state['resolved_commit']}",
        f"- clean_worktree: {state['clean_worktree']}",
        f"- time: {state['time']}",
        f"- final_status: **{state['final_status']}**",
        f"- action_route: {state['action_route']}",
        f"- failed_gate: {state['failed_gate']}",
        "",
        "## Gate matrix",
        "| gate | status | exit | command |",
        "|------|--------|------|---------|",
    ]
    for g in state["gates"]:
        lines.append(f"| {g['key']} | {g['status']} | {g['exit']} | `{g['command']}` |")
    lines.append("")
    lines.append("## Evidence (stdout/stderr summary)")
    for g in state["gates"]:
        lines.append(f"### {g['key']} — {g['status']} (exit {g['exit']})")
        lines.append("```\n" + (g["summary"] or "") + "\n```")
    (REPORTS / "cmd_pipeline_gate_report.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--pack", default="pack2_governance",
                    help="PACK dang xu ly cho cong RELEASE (vd pack3_cicd)")
    ap.add_argument("--tag", default="pack2-governance-v1.0")
    ap.add_argument("--doc-test", default="tests/test_pack2_governance_docs.py")
    ap.add_argument("--skip-build", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-lock", action="store_true")
    a = ap.parse_args()

    if not a.no_lock:
        ok, other = acquire_lock()
        if not ok:
            print(f"[pipeline] dang chay PID {other} — khong chong cheo, thoat.")
            return 2

    exit_code = 1
    try:
        resolved = _git("rev-parse", "--short", a.ref).stdout.strip()
        if not resolved:
            print(f"[pipeline] ref khong resolve: {a.ref}")
            return 2

        gates = []           # full gate records
        results = []         # for decide()
        missing_tool = False

        if not a.skip_build:
            bstatus, bnote = read_build_ready()
            results.append({"key": "BUILD", "status": bstatus})
            gates.append({"key": "BUILD", "status": bstatus, "exit": "-",
                          "command": "read reports/build_report.md", "summary": bnote})

        build_ok = a.skip_build or (results and results[0]["status"] == "READY_FOR_AUDIT")

        if build_ok:
            if make_worktree(a.ref) is None:
                print("[pipeline] ERR tao worktree sach")
                return 2
            stopped = False
            for key, argv in build_gates(a.pack, a.tag, a.doc_test):
                if stopped:
                    gates.append({"key": key, "status": "NOT_VERIFIED", "exit": "-",
                                  "command": "python " + " ".join(argv),
                                  "summary": "upstream FAIL — stale, chua chay"})
                    results.append({"key": key, "status": "NOT_VERIFIED"})
                    continue
                status, code, cmd_str, summ = run_gate(argv)
                miss = status == "NOT_VERIFIED"
                if miss:
                    missing_tool = True
                gates.append({"key": key, "status": status,
                              "exit": (code if code is not None else "-"),
                              "command": cmd_str, "summary": summ})
                results.append({"key": key, "status": status, "missing": miss})
                if status in ("FAIL", "NOT_VERIFIED"):
                    stopped = True
            release_wt()

        final_status, action_route, failed = decide(results)
        exit_code = 0 if final_status == "READY_FOR_OWNER_FREEZE" else (2 if missing_tool else 1)

        state = {
            "ref": a.ref, "resolved_commit": resolved, "clean_worktree": str(WT),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "gates": gates, "failed_gate": failed,
            "action_route": action_route, "final_status": final_status,
            "exit_code": exit_code,
        }
        write_reports(state)

        if a.json:
            print(json.dumps(state, ensure_ascii=False, indent=2))
        else:
            print("# CMD PIPELINE GATE (controller: CMD kiem duyet)")
            print(f"Ref: {a.ref} ({resolved})   Worktree sach: {WT}")
            for g in gates:
                mk = "✓" if g["status"] in ("PASS", "READY_FOR_AUDIT") else "✗"
                print(f"  [{mk}] {g['key']:8} {g['status']:16} exit={g['exit']}")
            print(f"FINAL: {final_status}   ACTION_ROUTE: {action_route}")
            print(f"Report: reports/cmd_pipeline_gate_report.md")
        return exit_code
    finally:
        release_wt()
        if not a.no_lock:
            release_lock()


if __name__ == "__main__":
    sys.exit(main())
