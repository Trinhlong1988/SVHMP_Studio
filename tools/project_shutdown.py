"""SVHMP_Studio Project Shutdown — 1-click TẮT all tools + CMD windows.

Mr.Long click đúp Desktop\\SVHMP_Stop.lnk → tự động:
1. Kill all qa_watch / supervisor / bootstrap python processes
2. Close all CMD/PowerShell windows titled CMD-LEAD / CMD-THUC-THI
3. KHÔNG kill Claude sessions (Mr.Long tự đóng tab)
4. Log [INFO] shutdown

Usage:
    python tools/project_shutdown.py
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent


def section(title, num=None):
    bar = "=" * 70
    prefix = f"STEP {num}: " if num else ""
    print(f"\n{bar}\n  {prefix}{title}\n{bar}", flush=True)


def run_ps(cmd_str, timeout=30):
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd_str],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=timeout,
        )
        return r.stdout, r.returncode
    except Exception as e:
        return f"[ERR] {e}", -1


def step1_kill_python_qa():
    section("Kill all qa_watch / supervisor / bootstrap python", 1)
    out, _ = run_ps(
        "Get-WmiObject Win32_Process -Filter \"Name='python.exe' OR Name='pythonw.exe'\" | "
        "Where-Object { $_.CommandLine -match 'qa_watch|supervisor|bootstrap|svhmp_v13' } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue; \"killed PID $($_.ProcessId): $($_.Name)\" }"
    )
    print(out.strip() or "  (no qa/bootstrap python process)")


def step2_close_cmd_windows():
    section("Close CMD-LEAD + CMD-THUC-THI windows", 2)
    out, _ = run_ps(
        "Get-Process | Where-Object { $_.MainWindowTitle -match 'CMD-LEAD|CMD-THUC-THI|SVHMP|qa_watch|supervisor|bootstrap' } | "
        "ForEach-Object { Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue; \"closed PID $($_.Id): $($_.MainWindowTitle)\" }"
    )
    print(out.strip() or "  (no CMD/wt window matched)")


def step3_verify_clean():
    section("Verify all clean", 3)
    out, _ = run_ps(
        "$qa = Get-WmiObject Win32_Process -Filter \"Name='python.exe' OR Name='pythonw.exe'\" | "
        "Where-Object { $_.CommandLine -match 'qa_watch|supervisor|bootstrap' }; "
        "if ($qa) { \"⚠ Remaining python qa/bootstrap: $($qa.Count)\" } else { \"[OK] no qa/bootstrap python\" }; "
        "$wt = Get-Process | Where-Object { $_.MainWindowTitle -match 'CMD-LEAD|CMD-THUC-THI' }; "
        "if ($wt) { \"⚠ Remaining CMD windows: $($wt.Count)\" } else { \"[OK] no CMD-LEAD/CMD-THUC-THI window\" }"
    )
    print(out.strip())


def step4_log_ping():
    section("Log [INFO] shutdown", 4)
    try:
        subprocess.run(
            [sys.executable, str(SVHMP / "tools" / "log_ping.py"),
             "INFO", "CMD LEAD project_shutdown — killed qa_watch + supervisor + closed CMD windows. Claude sessions still alive (Mr.Long tự đóng tab)."],
            capture_output=True, timeout=10,
        )
        print("  ✓ logged")
    except Exception as e:
        print(f"  [WARN] log fail: {e}")


def main():
    print(f"""
######################################################################
# SVHMP PROJECT SHUTDOWN — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# TẮT all tools + CMD windows
######################################################################""")
    step1_kill_python_qa()
    step2_close_cmd_windows()
    step3_verify_clean()
    step4_log_ping()
    print("\n" + "=" * 70)
    print("  SHUTDOWN DONE — Mr.Long tự đóng Claude tab nếu cần")
    print("=" * 70)
    input("\nPress Enter để đóng cửa sổ này...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CANCELLED]")
        sys.exit(0)
