"""SESSION START AUDIT — load state BEFORE any action.

Mr.Long lệnh 29/6: chặn vector "memory drift cross-session".

Run MỌI session start (em CMD LEAD hoặc bất kỳ CMD nào):
    python tools/session_start_audit.py

Output structured:
  1. GIT — last 10 commits + uncommitted state
  2. PING — last 20 events + delta since em last commit
  3. ACTIVE CMDs — Python loops (qa_watch / render)
  4. RULES — bible/00: dem codified-entry dai R86..R200 + R-ID conflicts
  5. EP01 STATUS — R86 + R98 + STAGE 3 6 sections + post_render_gate
  6. EP02-50 status — R86 batch count (legacy debt)
  7. PENDING — uncommitted + untracked + PING [VIOLATION] unresolved
  8. MEMORY HEAD — first 10 entries MEMORY.md (lessons load)
  9. PRE-COMMIT HOOK — verify active + sections enabled

KHÔNG suy luận — chỉ FACT. Em ngồi đọc → biết state thực tế trước action.
"""
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent
MEMORY_INDEX = (Path.home() / r'.claude/projects/C--Users-Administrator/memory/MEMORY.md')


def run(cmd, cwd=None, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace",
                          cwd=cwd or SVHMP, timeout=timeout, shell=False)
        return r.stdout, r.returncode
    except Exception as e:
        return f"[ERR] {e}", -1


def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def s1_git():
    section("1. GIT — last 10 commits + uncommitted")
    out, _ = run(["git", "log", "--oneline", "-10"])
    print(out)
    out, _ = run(["git", "status", "--short"])
    mods = out.strip().split("\n") if out.strip() else []
    print(f"Uncommitted ({len(mods)} files):")
    for line in mods[:15]:
        print(f"  {line}")
    if len(mods) > 15:
        print(f"  ... + {len(mods)-15} more")


def s2_ping():
    section("2. PING — AUTO LOG latest 20 events")
    ping = SVHMP / "PING_CMD_LEAD_29_06.md"
    if not ping.exists():
        print("[NO PING file]")
        return
    text = ping.read_text(encoding="utf-8")
    # Find AUTO LOG section
    m = re.search(r"## AUTO LOG.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
    if not m:
        print("[no AUTO LOG section]")
        return
    lines = [l for l in m.group(1).split("\n") if l.strip().startswith("- `")][:20]
    for line in lines:
        print(line)


def s3_active_cmds():
    section("3. ACTIVE CMDs — Python loops")
    out, _ = run(["powershell", "-NoProfile", "-Command",
                  "Get-WmiObject Win32_Process -Filter \"Name='python.exe'\" | "
                  "Where-Object { $_.CommandLine -match 'qa_watch|render|svhmp' } | "
                  "Select-Object ProcessId, CommandLine | Format-List"])
    print(out.strip() or "[no active SVHMP python loops]")


def s4_rules():
    section("4. RULES — bible/00: dem codified-entry dai R86..R200")
    bible = SVHMP / "bible" / "00_constitution.yaml"
    if not bible.exists():
        print("[bible/00 missing]")
        return
    text = bible.read_text(encoding="utf-8")
    found = set()
    dups = []
    for n in range(40, 200):
        defs = []
        for m in re.finditer(rf"^R{n}_[a-zA-Z]", text, re.MULTILINE):
            defs.append(("top_level", m.start()))
        for m in re.finditer(rf"^\s*-\s*id:\s*R{n}\b", text, re.MULTILINE):
            defs.append(("list_id", m.start()))
        if len(defs) >= 1:
            found.add(n)
        if len(defs) >= 2:
            dups.append((n, defs))
    found = sorted(found)
    if found:
        print(f"Codified: R{found[0]}-R{found[-1]} ({len(found)} rules)")
        gaps = [n for n in range(found[0], found[-1]+1) if n not in found]
        if gaps:
            print(f"GAPS in range: {gaps[:20]}")
    if dups:
        print(f"\n[CONFLICTS] {len(dups)} duplicate rule IDs:")
        for n, defs in dups:
            print(f"  R{n}: {len(defs)} definitions")
    else:
        print("[OK] No rule ID conflicts")


def s5_ep01_status():
    section("5. EP01 STATUS — R86 + R98 + STAGE 3 + post_render_gate")
    # R86
    out, code = run(["python", "tools/qa_eol_diacritic.py", "output/ep_01/episode.md"])
    m = re.search(r"R86 EOL violations:\s*(\d+)", out)
    r86 = int(m.group(1)) if m else "?"
    print(f"  R86 EOL: {r86} violations (exit {code})")
    # R98 via qa_watch text_repeats
    sys.path.insert(0, str(SVHMP / "tools"))
    try:
        import qa_watch
        v = qa_watch.text_repeats()
        print(f"  R98 repeats: {len(v)} real")
    except Exception as e:
        print(f"  R98: [ERR {e}]")
    # STAGE 3 per section
    print("  STAGE 3 sections:")
    for sec in ["hook", "setup", "incident", "reveal", "payoff", "cliffhanger"]:
        wav = SVHMP / "output" / "ep_01" / "sections" / f"{sec}.wav"
        if not wav.exists():
            print(f"    {sec}: MISSING")
            continue
        out, _ = run(["python", "tools/qa_post_render.py", str(wav)], timeout=60)
        verdict = "PASS" if "GATE: PASS" in out else "FAIL"
        # Extract key metrics
        peak_m = re.search(r"Peak:\s*([-\d.]+)\s*dB", out)
        rms_m = re.search(r"RMS:\s*([-\d.]+)\s*dB", out)
        peak = peak_m.group(1) if peak_m else "?"
        rms = rms_m.group(1) if rms_m else "?"
        print(f"    {sec:12s} {verdict:4s} peak={peak} rms={rms}")
    # post_render_gate
    out, _ = run(["python", "tools/post_render_gate.py", "--ep", "1"], timeout=60)
    gate = "PASS" if "GATE PASS" in out else "FAIL"
    print(f"  post_render_gate EP01: {gate}")


def s6_legacy_r86():
    section("6. EP02-50 R86 LEGACY (mass debt)")
    total_eps = 0
    viol_eps = 0
    total_viol = 0
    for n in range(2, 51):
        p = SVHMP / "output" / f"ep_{n:02d}" / "episode.md"
        if not p.exists(): continue
        total_eps += 1
        out, _ = run(["python", "tools/qa_eol_diacritic.py", str(p)], timeout=15)
        m = re.search(r"R86 EOL violations:\s*(\d+)", out)
        v = int(m.group(1)) if m else 0
        if v > 0:
            viol_eps += 1
            total_viol += v
    print(f"  EP02-50: {viol_eps}/{total_eps} EPs có R86 violation")
    print(f"  Total violations: {total_viol}")
    if total_viol > 0:
        print(f"  PENDING: batch fix R86 EP02-50 (not started)")


def s7_pending():
    section("7. PENDING — actions needed")
    # Untracked tools
    out, _ = run(["git", "ls-files", "--others", "--exclude-standard", "tools/"])
    new_tools = [l for l in out.strip().split("\n") if l]
    if new_tools:
        print(f"  Untracked tools/ ({len(new_tools)}):")
        for t in new_tools[:10]:
            print(f"    {t}")
    # Unresolved VIOLATION trong PING (last 20)
    ping = SVHMP / "PING_CMD_LEAD_29_06.md"
    if ping.exists():
        text = ping.read_text(encoding="utf-8")
        m = re.search(r"## AUTO LOG.*?\n(.*?)(?=\n##|\Z)", text, re.DOTALL)
        if m:
            viol = [l for l in m.group(1).split("\n")[:30]
                    if "[VIOLATION]" in l and "WATCH iter" not in l]
            if viol:
                print(f"\n  Recent VIOLATIONs (top 5):")
                for v in viol[:5]:
                    print(f"    {v.strip()[:100]}")


def s8_memory():
    section("8. MEMORY HEAD — load top 10 lessons")
    if not MEMORY_INDEX.exists():
        print(f"[MEMORY.md missing: {MEMORY_INDEX}]")
        return
    lines = MEMORY_INDEX.read_text(encoding="utf-8").split("\n")[:10]
    for line in lines:
        if line.strip():
            print(f"  {line[:150]}")


def s9_hook():
    section("9. PRE-COMMIT HOOK — verify active")
    hook = SVHMP / ".githooks" / "pre-commit"
    if not hook.exists():
        print(f"[hook missing: {hook}]")
        return
    text = hook.read_text(encoding="utf-8")
    sections = []
    if "SECTION A" in text or "R-ID CONFLICT" in text:
        sections.append("A:R-ID guard")
    if "SECTION B" in text or "R41" in text or "post_render_gate" in text:
        sections.append("B:R41 gate")
    print(f"  Hook: {hook.exists()}")
    print(f"  Sections active: {sections}")
    out, _ = run(["git", "config", "--get", "core.hooksPath"])
    print(f"  core.hooksPath: {out.strip() or '[NOT SET — hook will NOT run!]'}")


def main():
    print(f"\n{'#'*70}")
    print(f"# SESSION START AUDIT — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"# SVHMP_Studio — load state BEFORE any action")
    print(f"{'#'*70}")
    s1_git()
    s2_ping()
    s3_active_cmds()
    s4_rules()
    s5_ep01_status()
    s6_legacy_r86()
    s7_pending()
    s8_memory()
    s9_hook()
    print(f"\n{'#'*70}")
    print("# AUDIT DONE — em CMD LEAD đọc structured output trước MỌI action")
    print(f"{'#'*70}\n")


if __name__ == "__main__":
    main()
