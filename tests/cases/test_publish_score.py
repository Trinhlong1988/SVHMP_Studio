"""Test R140 — Publish Score gate dedicated."""
import os
import subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EPISODE = BASE / "output/ep_01/episode.md"
READY = BASE / "output/ep_01/episode_tts_ready.md"
TOOL = BASE / "tools/publish_score.py"


def _atomic_write(path, content):
    """Write atomically (tmp + os.replace) so a write interrupted mid-flight
    never leaves `path` half-written. See tools/text_batch_fix.py for the
    same helper — this file has the same golden-EP01-write hazard: it
    replaces output/ep_01/episode.md with throwaway probe text and must
    guarantee restore even if a subprocess call raises/times out."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def run():
    r = subprocess.run([sys.executable, str(TOOL)], capture_output=True, text=True,
                       cwd=str(BASE), encoding="utf-8", errors="ignore", timeout=120)
    return r.returncode, r.stdout


def main():
    print("=== TEST R140 publish_score gate ===")

    # PASS case: use current clean episode (should PASS)
    code, out = run()
    print(f"  Clean episode → exit_{code}")
    has_pass = "PUBLISH GATE: PASS" in out or "SHIP ALLOWED" in out
    has_fail = "KILL SWITCH" in out
    if has_pass:
        print(f"  ✅ PASS: gate detected PUBLISH GATE: PASS")
    elif has_fail:
        print(f"  ⚠️ FAIL: gate said KILL — current episode has violation")
    else:
        print(f"  ⚠️ AMBIGUOUS output")

    # FAIL case: inject R86 violation
    orig = EPISODE.read_text(encoding="utf-8")
    ready_orig = READY.read_text(encoding="utf-8") if READY.exists() else None
    bad = orig.replace("## 1. HOOK", "## 1. HOOK\n\nĐây là câu test với từ cũ.\n", 1)
    try:
        _atomic_write(EPISODE, bad)
        # Rebuild tts_ready. NOTE: writes into the REAL
        # output/ep_01/episode_tts_ready.md — restored byte-for-byte from
        # ready_orig in the finally block below (process_ep()'s
        # re-derivation does not byte-match the committed golden file, so
        # regenerating forward instead of restoring from backup would leave
        # permanent uncommitted drift after every test run).
        subprocess.run([sys.executable, str(BASE / "tools/tts_adapter_pre_render.py"), "--ep", "1", "--apply"],
                       capture_output=True, cwd=str(BASE), timeout=30)
        code, out = run()
        if "KILL SWITCH" in out or code != 0:
            print(f"  ✅ FAIL injected R86 → gate triggered KILL SWITCH")
        else:
            print(f"  ❌ Gate FAILED to catch R86 inject: {out[-300:]}")
            sys.exit(1)
    finally:
        # ALWAYS restore, even if the try block raised (timeout/crash/etc).
        _atomic_write(EPISODE, orig)
        if ready_orig is not None:
            _atomic_write(READY, ready_orig)

    print("=== TEST DONE ===")


if __name__ == "__main__":
    main()
