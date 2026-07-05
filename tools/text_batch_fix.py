"""Tier 2.1 — Apply text fixes from YAML registry.

NO BASH PATCH. All fixes go through this tool + verified per fix.

Usage:
  python tools/text_batch_fix.py --dry-run
  python tools/text_batch_fix.py --apply
"""
import argparse
import os
import sys
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
import yaml
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
EPISODE = BASE / "output/ep_01/episode.md"
GOLDEN = BASE / "output/ep_01/episode_golden_text.md"
REGISTRY = BASE / "bible/35_text_fix_registry.yaml"


def _atomic_write(path, content):
    """Write `content` to `path` atomically: write to a sibling .tmp file then
    os.replace() over the real path. A write interrupted mid-flight (kill /
    crash / disk full) never leaves `path` half-written — it holds either the
    OLD full content or the NEW full content, never a partial one."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def verify_post_fix(text, verify_rules):
    """Apply text to episode.md (the REAL golden EP01) temp + run verify rules.

    SAFETY: this is the only place in the whole tool/test suite that writes
    directly into the golden output/ep_01/episode.md. The write+restore MUST
    be crash-safe:
      - every write to episode.md/backup goes through _atomic_write() (tmp +
        os.replace) so a write interrupted mid-flight never leaves a
        half-written file at the real path.
      - the mutate + subprocess-verify block runs inside try/finally so that
        ANY exception (including subprocess.TimeoutExpired or a raised error
        from subprocess.run) still restores episode.md from backup before
        the exception propagates. Previously there was no try/finally: an
        exception between the write (line ~27 pre-fix) and the restore
        (line ~51 pre-fix) left episode.md permanently overwritten with the
        probe text.
    """
    backup = EPISODE.with_suffix(".md.batchfix_bak")
    original = EPISODE.read_text(encoding="utf-8")
    _atomic_write(backup, original)
    try:
        _atomic_write(EPISODE, text)
        subprocess.run([sys.executable, str(BASE / "tools/tts_adapter_pre_render.py"), "--ep", "1", "--apply"],
                       capture_output=True, timeout=30)
        tool_map = {
            "R86": "qa_eol_diacritic.py",
            "R92b": "qa_honorific.py",
            "R110": "qa_continuity.py",
            "R111": "qa_phonetic_safe.py",
            "R113": "qa_repeat_action.py",
            "R114": "qa_honorific.py",  # share with R92b
            "R117": "qa_fact_check.py",
            "R128": "qa_anti_generic.py",
            "R141": "qa_ssot_diff.py",
        }
        failed = []
        for rule in set(verify_rules):
            tool = tool_map.get(rule)
            if not tool: continue
            r = subprocess.run([sys.executable, str(BASE / "tools" / tool)],
                               capture_output=True, text=True, cwd=str(BASE), timeout=60,
                               encoding="utf-8", errors="ignore")
            if r.returncode != 0:
                failed.append(rule)
        return failed
    finally:
        # ALWAYS restore, even if the try block raised (timeout/crash/etc).
        _atomic_write(EPISODE, backup.read_text(encoding="utf-8"))
        backup.unlink(missing_ok=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if not args.dry_run and not args.apply:
        print("Specify --dry-run or --apply")
        sys.exit(1)

    reg = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    fixes = reg.get("fixes", [])
    print(f"=== TEXT BATCH FIX — {len(fixes)} entries ===\n")

    t = EPISODE.read_text(encoding="utf-8")
    applied = []
    skipped = []
    failed_verify = []

    for f in fixes:
        fid = f["id"]
        if "old" not in f or "new" not in f:
            skipped.append((fid, "skipped (no old/new field, status: " + f.get("status", "unknown") + ")"))
            continue
        old = f["old"]
        new = f["new"]
        verify = f.get("verify_rules", [])
        if old not in t:
            skipped.append((fid, "OLD pattern not found"))
            print(f"  ⏭️  {fid}: OLD pattern not in text")
            continue
        if args.dry_run:
            print(f"  📋 {fid} ({f['section']}): would replace")
            print(f"      OLD: {old[:80]}...")
            print(f"      NEW: {new[:80]}...")
            applied.append(fid)
            continue
        # Apply + verify
        new_text = t.replace(old, new, 1)
        failed = verify_post_fix(new_text, verify)
        if failed:
            failed_verify.append((fid, failed))
            print(f"  ❌ {fid}: post-fix verify FAIL on {failed}")
        else:
            t = new_text
            applied.append(fid)
            print(f"  ✅ {fid}: applied + verified {verify}")

    if args.apply:
        EPISODE.write_text(t, encoding="utf-8")
        GOLDEN.write_text(t, encoding="utf-8")
        print(f"\n  Applied {len(applied)} fixes. Episode + Golden updated.")
        subprocess.run([sys.executable, str(BASE / "tools/tts_adapter_pre_render.py"), "--ep", "1", "--apply"],
                       capture_output=True, timeout=30)

    print(f"\n=== SUMMARY ===")
    print(f"  Applied: {len(applied)}")
    print(f"  Skipped: {len(skipped)}")
    print(f"  Failed verify: {len(failed_verify)}")

    sys.exit(0 if not failed_verify else 1)


if __name__ == "__main__":
    main()
