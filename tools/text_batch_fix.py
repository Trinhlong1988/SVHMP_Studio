"""Tier 2.1 — Apply text fixes from YAML registry.

NO BASH PATCH. All fixes go through this tool + verified per fix.

Usage:
  python tools/text_batch_fix.py --dry-run
  python tools/text_batch_fix.py --apply
"""
import argparse
import sys
import subprocess
import yaml
from pathlib import Path

BASE = Path(r"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio")
EPISODE = BASE / "output/ep_01/episode.md"
GOLDEN = BASE / "output/ep_01/episode_golden_text.md"
REGISTRY = BASE / "bible/35_text_fix_registry.yaml"


def verify_post_fix(text, verify_rules):
    """Apply text to episode.md temp + run verify rules."""
    backup = EPISODE.with_suffix(".md.batchfix_bak")
    backup.write_text(EPISODE.read_text(encoding="utf-8"), encoding="utf-8")
    EPISODE.write_text(text, encoding="utf-8")
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
    # restore backup
    EPISODE.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
    backup.unlink()
    return failed


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
