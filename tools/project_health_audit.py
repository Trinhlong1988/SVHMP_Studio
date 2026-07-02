"""Project health audit — toàn diện scan bug ẩn dự án.

Mr.Long lệnh 30/6: "check lại xem còn bug ẩn không toàn diện dự án".

10 dim check:
1. Python syntax — tất cả tools/*.py compile OK?
2. Subprocess.run thiếu CREATE_NO_WINDOW (console nháy hidden bug)
3. Bible/00 — bible_audit.py PASS?
4. Hook pre-commit — 4 sections all wired + executable?
5. EP01 — R86 + R98 + STAGE 3 6/6 PASS?
6. Background processes — supervisor + qa_watch alive?
7. Backup .bak files — count + size (cleanup needed?)
8. Cross-ref: tools mention rule không codified
9. Cross-ref: rule reference tool không exist
10. Git uncommitted — risk lose work

Usage:
    python tools/project_health_audit.py
    python tools/project_health_audit.py --strict  # exit 1 nếu HIGH bug
"""
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
TOOLS = SVHMP / "tools"


def section(title, num=None):
    bar = "=" * 70
    p = f"DIM {num}: " if num else ""
    print(f"\n{bar}\n  {p}{title}\n{bar}", flush=True)


def run(cmd, timeout=60):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          cwd=SVHMP, timeout=timeout)
        return r.stdout, r.returncode
    except Exception as e:
        return f"[ERR] {e}", -1


bugs = {"HIGH": [], "MEDIUM": [], "LOW": [], "INFO": []}


def d1_syntax():
    section("Python syntax check tools/*.py", 1)
    fail = []
    for f in sorted(TOOLS.glob("*.py")):
        out, code = run([sys.executable, "-m", "py_compile", str(f)])
        if code != 0:
            fail.append((f.name, out.strip()[:100]))
    if fail:
        bugs["HIGH"].extend([f"syntax: {f[0]} — {f[1]}" for f in fail])
        print(f"  ✗ {len(fail)} files syntax error")
        for f, msg in fail[:5]:
            print(f"    {f}: {msg}")
    else:
        print(f"  ✓ {len(list(TOOLS.glob('*.py')))} files syntax OK")


def d2_subprocess_hidden():
    section("Subprocess.run thiếu CREATE_NO_WINDOW (console nháy)", 2)
    suspects = []
    for f in sorted(TOOLS.glob("*.py")):
        text = f.read_text(encoding="utf-8", errors="replace")
        # Find subprocess.run|Popen calls
        calls = re.findall(r"subprocess\.(?:run|Popen)\s*\(", text)
        has_flag = "CREATE_NO_WINDOW" in text
        if calls and not has_flag and f.name not in ("project_shutdown.py", "log_ping.py", "session_start_audit.py", "project_bootstrap.py", "verify_ping_claim.py", "bible_audit.py", "project_health_audit.py", "check_rule_mention_codified.py", "check_counter_canonical.py", "flush_rules_from_test.py"):
            suspects.append((f.name, len(calls)))
    if suspects:
        bugs["MEDIUM"].extend([f"console nháy risk: {f[0]} ({f[1]} subprocess)" for f in suspects])
        print(f"  ⚠ {len(suspects)} files có subprocess KHÔNG CREATE_NO_WINDOW (chỉ chạy fg OK)")
        for f, n in suspects[:8]:
            print(f"    {f}: {n} call(s)")
    else:
        print(f"  ✓ All background loops có CREATE_NO_WINDOW")


def d3_bible_audit():
    section("Bible/00 audit (tools/bible_audit.py)", 3)
    out, code = run([sys.executable, str(TOOLS / "bible_audit.py")], timeout=120)
    if code != 0:
        bugs["HIGH"].append(f"bible_audit FAIL: exit {code}")
        print(f"  ✗ bible_audit exit {code}")
        return
    # Parse SUMMARY
    m = re.search(r"HIGH issues:\s*(\d+)", out)
    high = int(m.group(1)) if m else "?"
    m = re.search(r"MEDIUM:\s*(\d+)", out)
    med = int(m.group(1)) if m else "?"
    print(f"  HIGH={high}  MEDIUM={med}")
    if high not in ("?", 0):
        bugs["HIGH"].append(f"bible: {high} HIGH issues")
    if med not in ("?", 0):
        bugs["LOW"].append(f"bible: {med} MEDIUM (rules thiếu why/detection)")


def d4_hook_sections():
    section("Pre-commit hook 4 sections wired", 4)
    hook = SVHMP / ".githooks" / "pre-commit"
    if not hook.exists():
        bugs["HIGH"].append("hook pre-commit MISSING")
        print("  ✗ hook missing")
        return
    text = hook.read_text(encoding="utf-8")
    # deep-audit F1/F3-followup: pre-commit gio la wrapper sh -> orchestrator
    # Python (git_hook_pre_commit.py). Guard sections nam TRONG orchestrator,
    # KHONG con o file hook (truoc day grep file hook -> false-positive HIGH).
    orch = SVHMP / "tools" / "git_hook_pre_commit.py"
    orch_text = orch.read_text(encoding="utf-8") if orch.exists() else ""
    missing = []
    if "git_hook_pre_commit" not in text:
        missing.append("wrapper-delegation")
    sections = [
        ("A R-ID conflict", "check_rule_id_free"),
        ("B R41 post_render_gate", "post_render_gate"),
        ("C MASS-REPLACE log", "MASS-REPLACE"),
        ("D Rule mention orphan", "check_rule_mention_codified"),
    ]
    for nm, kw in sections:
        if kw in orch_text:
            print(f"  ✓ SECTION {nm}")
        else:
            print(f"  ✗ SECTION {nm} — missing")
            missing.append(nm)
    if missing:
        bugs["HIGH"].append(f"hook missing sections: {missing}")
    # core.hooksPath
    out, _ = run(["git", "config", "--get", "core.hooksPath"])
    path = out.strip()
    if path != ".githooks":
        bugs["HIGH"].append(f"core.hooksPath: '{path}' (must be .githooks)")
        print(f"  ✗ core.hooksPath: '{path or 'NOT SET'}'")
    else:
        print(f"  ✓ core.hooksPath: .githooks")


def d5_ep01_health():
    section("EP01 health (R86 + R98 + STAGE 3)", 5)
    out, _ = run([sys.executable, str(TOOLS / "qa_eol_diacritic.py"), "output/ep_01/episode.md"])
    m = re.search(r"R86 EOL violations:\s*(\d+)", out)
    r86 = int(m.group(1)) if m else -1
    print(f"  R86: {r86} violations")
    if r86 > 0:
        bugs["HIGH"].append(f"EP01 R86: {r86} violations")

    # R98 via qa_watch
    sys.path.insert(0, str(TOOLS))
    try:
        import qa_watch
        v = qa_watch.text_repeats()
        print(f"  R98 real repeats: {len(v)}")
        if len(v) > 0:
            bugs["MEDIUM"].append(f"EP01 R98: {len(v)} real repeats")
    except Exception as e:
        bugs["LOW"].append(f"R98 check fail: {e}")
        print(f"  ⚠ R98 check fail: {e}")

    # STAGE 3 per section
    sections = ["hook", "setup", "incident", "reveal", "payoff", "cliffhanger"]
    pass_count = 0
    for sec in sections:
        wav = SVHMP / "output" / "ep_01" / "sections" / f"{sec}.wav"
        if not wav.exists():
            print(f"    {sec}: MISSING")
            bugs["MEDIUM"].append(f"EP01 {sec}.wav missing")
            continue
        out, _ = run([sys.executable, str(TOOLS / "qa_post_render.py"), str(wav)], timeout=60)
        if "GATE: PASS" in out:
            pass_count += 1
            print(f"    {sec}: PASS")
        else:
            print(f"    {sec}: FAIL")
            bugs["MEDIUM"].append(f"EP01 {sec} STAGE 3 FAIL")
    print(f"  STAGE 3: {pass_count}/6 PASS")


def d6_processes():
    section("Background processes (supervisor + qa_watch)", 6)
    out, _ = run([
        "powershell", "-NoProfile", "-Command",
        "Get-WmiObject Win32_Process -Filter \"Name='python.exe' OR Name='pythonw.exe'\" | "
        "Where-Object { $_.CommandLine -match 'qa_watch|supervisor' } | "
        "Select-Object ProcessId, @{N='T';E={if($_.CommandLine -match 'supervisor'){'SUP'}else{'WATCH'}}} | "
        "Format-Table -AutoSize"
    ])
    text = out.strip()
    print(text or "  (no qa_watch/supervisor running)")
    if not text:
        bugs["INFO"].append("supervisor + qa_watch OFF (Mr.Long kill, chưa restart)")


def d7_backup_files():
    section("Backup .bak files (cleanup needed?)", 7)
    baks = list(SVHMP.rglob("*.bak*"))
    total_mb = sum(p.stat().st_size for p in baks if p.is_file()) / 1024 / 1024
    print(f"  {len(baks)} files, total {total_mb:.1f} MB")
    if total_mb > 500:
        bugs["MEDIUM"].append(f".bak files {total_mb:.0f} MB — cleanup recommended")
    elif total_mb > 50:
        bugs["LOW"].append(f".bak files {total_mb:.0f} MB")


def d8_tool_mention_unmapped():
    section("Tools mention rule NOT codified bible/00", 8)
    out, code = run([sys.executable, str(TOOLS / "flush_rules_from_test.py")], timeout=30)
    m = re.search(r"MISSING from bible/00:\s*\[([\d, ]+)\]", out)
    if m:
        missing = m.group(1).strip()
        if missing:
            print(f"  ⚠ Test orphan: R[{missing}]")
            bugs["MEDIUM"].append(f"test orphan: R[{missing}]")
        else:
            print("  ✓ No test orphan")
    else:
        print("  (no MISSING line found)")


def d9_git_uncommitted():
    section("Git uncommitted (risk lose work)", 9)
    out, _ = run(["git", "status", "--short"])
    lines = [l for l in out.strip().split("\n") if l]
    modified = [l for l in lines if l.startswith(" M")]
    staged = [l for l in lines if l.startswith("M ") or l.startswith("A ")]
    untracked = [l for l in lines if l.startswith("??")]
    print(f"  Modified: {len(modified)}, Staged: {len(staged)}, Untracked: {len(untracked)}")
    if len(modified) > 30:
        bugs["LOW"].append(f"git: {len(modified)} files modified uncommitted")


def d10_orphan_claims():
    section("Orphan rule mention claims trong PING", 10)
    out, code = run([sys.executable, str(TOOLS / "check_rule_mention_codified.py"),
                     "--file", "PING_CMD_LEAD_29_06.md"], timeout=30)
    m = re.search(r"Missing \(orphan\):\s*(\d+)", out)
    n = int(m.group(1)) if m else -1
    print(f"  Orphan claims in PING: {n}")
    if n > 5:
        bugs["MEDIUM"].append(f"PING orphan claims: {n}")
    elif n > 0:
        bugs["LOW"].append(f"PING orphan claims: {n}")


def main():
    print(f"""
######################################################################
# PROJECT HEALTH AUDIT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# 10-dim toàn diện bug scan
######################################################################""")
    d1_syntax()
    d2_subprocess_hidden()
    d3_bible_audit()
    d4_hook_sections()
    d5_ep01_health()
    d6_processes()
    d7_backup_files()
    d8_tool_mention_unmapped()
    d9_git_uncommitted()
    d10_orphan_claims()
    print(f"\n{'='*70}\n  HEALTH SUMMARY\n{'='*70}")
    print(f"  HIGH:   {len(bugs['HIGH'])}")
    print(f"  MEDIUM: {len(bugs['MEDIUM'])}")
    print(f"  LOW:    {len(bugs['LOW'])}")
    print(f"  INFO:   {len(bugs['INFO'])}")
    if bugs["HIGH"]:
        print(f"\n  ## HIGH issues:")
        for b in bugs["HIGH"]:
            print(f"    - {b}")
    if bugs["MEDIUM"]:
        print(f"\n  ## MEDIUM issues:")
        for b in bugs["MEDIUM"][:10]:
            print(f"    - {b}")
    if bugs["LOW"]:
        print(f"\n  ## LOW issues:")
        for b in bugs["LOW"][:5]:
            print(f"    - {b}")
    # Save report
    rep = SVHMP / "runtime" / "project_health_report.json"
    rep.parent.mkdir(exist_ok=True, parents=True)
    rep.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "bugs": bugs,
        "summary": {k: len(v) for k, v in bugs.items()},
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nReport: {rep}")
    # deep-audit F6 (2/7): HIGH = severity chan (Critical/Major) -> LUON exit 1
    # (truoc day chi fail khi CO --strict -> caller quen flag = luon pass du co HIGH).
    if bugs["HIGH"]:
        return 1
    if "--strict" in sys.argv and bugs["MEDIUM"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
