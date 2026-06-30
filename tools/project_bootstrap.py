"""SVHMP_Studio Project Bootstrap — 1-click setup full stack.

Mr.Long click đúp Desktop\\SVHMP_Start.lnk → tự động:
1. Kill qa_watch_supervisor cũ + restart fresh
2. Run session_start_audit (9 sections)
3. Run verify_ping_claim --recent 20
4. Count orphan rules
5. Verify hooks 4 sections active
6. Write 2 PROMPT files cho 2 Claude tab
7. Open Windows Terminal 2 tabs ready
8. Copy PROMPT LEAD vào clipboard
9. Show Mr.Long checklist 2 paste

Usage:
    python tools/project_bootstrap.py
"""
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
PROMPT_LEAD_FILE = SVHMP / "PROMPT_CMD_LEAD.txt"
PROMPT_THUCTHI_FILE = SVHMP / "PROMPT_CMD_THUC_THI.txt"


def section(title, num=None):
    bar = "=" * 70
    prefix = f"STEP {num}: " if num else ""
    print(f"\n{bar}\n  {prefix}{title}\n{bar}", flush=True)


def run(cmd, timeout=60, capture=True):
    try:
        if capture:
            r = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace",
                              cwd=SVHMP, timeout=timeout, shell=False)
            return r.stdout, r.returncode
        else:
            return subprocess.Popen(cmd, cwd=SVHMP, shell=False), 0
    except Exception as e:
        return f"[ERR] {e}", -1


def step1_kill_old_supervisor():
    section("Kill qa_watch_supervisor cũ", 1)
    out, _ = run([
        "powershell", "-NoProfile", "-Command",
        "Get-WmiObject Win32_Process -Filter \"Name='python.exe'\" | "
        "Where-Object { $_.CommandLine -match 'qa_watch' } | "
        "ForEach-Object { Stop-Process -Id $_.ProcessId -Force; \"killed PID $($_.ProcessId)\" }"
    ])
    print(out.strip() or "  (no old qa_watch process)")
    time.sleep(2)


def step2_launch_supervisor():
    section("Launch fresh qa_watch_supervisor (hidden window)", 2)
    log_path = SVHMP / "runtime" / "realtime_logs" / "qa_watch_supervisor.log"
    log_path.parent.mkdir(exist_ok=True, parents=True)
    # Use pythonw.exe (no console window) — Mr.Long lệnh ẩn supervisor
    pyw = sys.executable.replace("python.exe", "pythonw.exe")
    if not Path(pyw).exists():
        pyw = sys.executable
    CREATE_NO_WINDOW = 0x08000000
    subprocess.Popen(
        [pyw, str(SVHMP / "tools" / "qa_watch_supervisor.py")],
        cwd=SVHMP,
        stdout=open(log_path, "a", encoding="utf-8"),
        stderr=subprocess.STDOUT,
        creationflags=CREATE_NO_WINDOW,
    )
    time.sleep(4)
    out, _ = run([
        "powershell", "-NoProfile", "-Command",
        "Get-WmiObject Win32_Process -Filter \"Name='python.exe'\" | "
        "Where-Object { $_.CommandLine -match 'qa_watch' } | "
        "Select-Object ProcessId, @{N='T';E={if($_.CommandLine -match 'supervisor'){'SUP'}else{'WATCH'}}} | "
        "Format-Table -AutoSize"
    ])
    print(out.strip() or "[ERR] no qa_watch process started")


def step3_session_audit():
    section("Session start audit (9 sections)", 3)
    out, _ = run([sys.executable, str(SVHMP / "tools" / "session_start_audit.py")], timeout=120)
    print(out[:3000])


def step4_verify_ping():
    section("Verify PING claims (recent 20)", 4)
    out, _ = run([sys.executable, str(SVHMP / "tools" / "verify_ping_claim.py"),
                  "--recent", "20"], timeout=60)
    print(out[:2000])


def step5_orphan_count():
    section("Orphan rules count", 5)
    out, _ = run([sys.executable, str(SVHMP / "tools" / "flush_rules_from_test.py")], timeout=30)
    print(out[:1000])


def step6_verify_hooks():
    section("Verify pre-commit hook sections", 6)
    hook = SVHMP / ".githooks" / "pre-commit"
    if not hook.exists():
        print("[ERR] hook missing")
        return
    text = hook.read_text(encoding="utf-8")
    for sec, kw in [("A R-ID conflict", "R-ID CONFLICT"),
                    ("B R41 post_render_gate", "R41 PRE-COMMIT"),
                    ("C MASS-REPLACE log", "MASS-REPLACE"),
                    ("D Rule mention orphan", "RULE MENTION")]:
        status = "✓" if kw in text else "✗"
        print(f"  SECTION {sec}: {status}")
    out, _ = run(["git", "config", "--get", "core.hooksPath"])
    path = out.strip()
    print(f"  core.hooksPath: {path or '[NOT SET — hook WILL NOT RUN]'}")


def step7_write_prompts():
    section("Write 2 PROMPT TEMPLATES", 7)
    lead = f"""Em là CMD LEAD session SVHMP_Studio (Claude Opus 4.7 1M context).

Mr.Long mở session này via project_bootstrap.py.

NHIỆM VỤ:
1. Đọc memory `feedback_session_29_6_lessons_4_mang.md` + `user_cmd_lead_role.md`
2. Đọc `COORDINATION_HUB.md` — protocol multi-CMD
3. Đọc `PING_CMD_LEAD_29_06.md` AUTO LOG 20 events latest
4. Track CMD THỰC THI work + apply hardlocks
5. KHÔNG suy luận — verify FACT mỗi claim
6. Log mọi action via `python tools/log_ping.py CATEGORY "msg"`

TOOLS ACTIVE:
- qa_watch_supervisor (PID running) — auto-restart qa_watch nếu die
- pre-commit hook 4 sections (A R-ID + B R41 + C mass-replace + D rule orphan)
- session_start_audit.py — chạy mọi session start
- verify_ping_claim.py --recent N — cross-check CMD THỰC THI claims

NGAY:
- Run `python tools/session_start_audit.py` để load state
- Đợi anh signal
"""
    cmd2 = f"""CMD THỰC THI session SVHMP_Studio render TTS (Claude khác CMD LEAD).

Mr.Long mở session này via project_bootstrap.py.

CONTEXT:
- EP01_FULL_v103.mp3 APPROVED 30/6 12:17 (11.69 MB / 19m07s)
- Pipeline v103 LOCKED — voice + music + R94b silence bridges PASS
- Rules range bible/00 từ 86 trở lên (verify thực qua tools/check_rule_id_free.py)
- Orphan rules tích lũy — 6 đã flush stub Round 19.26
- 13 rules còn cần CMD THỰC THI full spec — xem tools/flush_rules_from_test.py output

NHIỆM VỤ:
1. Đọc `PING_CMD_LEAD_29_06.md` AUTO LOG
2. Đọc `bible/00_constitution.yaml` full spec rules
3. Flush 13 rules orphan vào bible/00 với spec đầy đủ
4. Render EP02+ với pipeline v103
5. Log mọi action via log_ping.py

HOOK STACK ACTIVE (commit sẽ BLOCK nếu vi phạm):
- SECTION A: R-ID conflict
- SECTION B: R41 post_render_gate
- SECTION C: mass-replace log warn
- SECTION D: rule mention orphan (CẤM claim "R{{N}} codified" mà bible/00 chưa có)

NGAY: load context + signal Mr.Long ready
"""
    PROMPT_LEAD_FILE.write_text(lead, encoding="utf-8")
    PROMPT_THUCTHI_FILE.write_text(cmd2, encoding="utf-8")
    print(f"  ✓ {PROMPT_LEAD_FILE.name} ({len(lead)} chars)")
    print(f"  ✓ {PROMPT_THUCTHI_FILE.name} ({len(cmd2)} chars)")
    # Ship .md ra Desktop cho Mr.Long mở dễ
    import os as _os
    desktop = Path(_os.path.join(_os.path.expanduser("~"), "Desktop"))
    desktop_lead = desktop / "PROMPT_CMD_LEAD.md"
    desktop_thucthi = desktop / "PROMPT_CMD_THUC_THI.md"
    desktop_lead.write_text(f"# PROMPT CMD LEAD\n\n```\n{lead}\n```\n", encoding="utf-8")
    desktop_thucthi.write_text(f"# PROMPT CMD THỰC THI\n\n```\n{cmd2}\n```\n", encoding="utf-8")
    print(f"  ✓ Desktop\\{desktop_lead.name}")
    print(f"  ✓ Desktop\\{desktop_thucthi.name}")


def step8_open_terminals():
    section("Open Windows Terminal — 2 tab Claude ready", 8)
    # Try wt.exe first
    wt = subprocess.run(["where", "wt.exe"], capture_output=True, text=True)
    if wt.returncode == 0:
        try:
            # chcp 65001 trước khi launch shell — UTF-8 cho tiếng Việt
            subprocess.Popen([
                "wt.exe",
                "new-tab", "--title", "CMD-LEAD", "-d", str(SVHMP),
                "cmd", "/k", "chcp 65001 >nul && echo === CMD-LEAD ready - go: claude ===",
                ";",
                "new-tab", "--title", "CMD-THUC-THI", "-d", str(SVHMP),
                "cmd", "/k", "chcp 65001 >nul && echo === CMD-THUC-THI ready - go: claude ===",
            ])
            print("  ✓ Windows Terminal 2 tabs opened (CMD-LEAD + CMD-THUC-THI) + chcp 65001 UTF-8")
            return
        except Exception as e:
            print(f"  [WARN] wt.exe failed: {e}")
    # Fallback: 2 cmd windows với chcp 65001
    subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", f"chcp 65001 >nul && cd /d {SVHMP} && echo CMD-LEAD ready - go: claude"])
    subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", f"chcp 65001 >nul && cd /d {SVHMP} && echo CMD-THUC-THI ready - go: claude"])
    print("  ✓ 2 CMD windows opened + chcp 65001 (fallback — wt.exe not found)")


def step9_clipboard_prompt():
    section("Copy PROMPT CMD LEAD vào clipboard", 9)
    lead_text = PROMPT_LEAD_FILE.read_text(encoding="utf-8")
    try:
        # PowerShell Set-Clipboard handles unicode
        p = subprocess.Popen(
            ["powershell", "-NoProfile", "-Command", "$input | Set-Clipboard"],
            stdin=subprocess.PIPE,
        )
        p.communicate(input=lead_text.encode("utf-8"))
        print("  ✓ PROMPT CMD LEAD đã copy clipboard (Ctrl+V trong tab CMD-LEAD)")
    except Exception as e:
        print(f"  [WARN] clipboard fail: {e}")


def step10_checklist():
    section("Mr.Long checklist 30 giây", 10)
    print(f"""
  ┌────────────────────────────────────────────────────────┐
  │  THAO TÁC MR.LONG (30 giây):                          │
  │                                                        │
  │  1. Click tab CMD-LEAD trong Windows Terminal          │
  │  2. Gõ:    claude                                      │
  │  3. Nhấn Enter để Claude khởi động                     │
  │  4. Ctrl+V để paste PROMPT (đã trong clipboard)        │
  │  5. Enter để Claude bắt đầu                            │
  │                                                        │
  │  6. Click tab CMD-2                                    │
  │  7. Gõ:    claude                                      │
  │  8. Mở file: {PROMPT_THUCTHI_FILE.name}        │
  │  9. Copy nội dung + paste vào Claude tab               │
  │ 10. Enter để CMD THỰC THI bắt đầu                            │
  └────────────────────────────────────────────────────────┘

  Files prompt:
    LEAD: {PROMPT_LEAD_FILE}
    CMD-THUC-THI: {PROMPT_THUCTHI_FILE}

  Background tools đang chạy:
    - qa_watch_supervisor PID running
    - qa_watch loop 60s
    - Pre-commit hook 4 sections active
""")


def main():
    print(f"""
######################################################################
# SVHMP PROJECT BOOTSTRAP — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 1-click setup full stack
######################################################################""")
    step1_kill_old_supervisor()
    step2_launch_supervisor()
    step3_session_audit()
    step4_verify_ping()
    step5_orphan_count()
    step6_verify_hooks()
    step7_write_prompts()
    step8_open_terminals()
    step9_clipboard_prompt()
    step10_checklist()
    print("\n" + "=" * 70)
    print("  BOOTSTRAP DONE — Mr.Long làm 30 giây 2 paste là xong")
    print("=" * 70)
    # Keep console open
    input("\nPress Enter để đóng cửa sổ này...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[CANCELLED]")
        sys.exit(0)
