"""Tier 2.1 — Apply text fixes from YAML registry.

NO BASH PATCH. All fixes go through this tool + verified per fix.

Usage:
  python tools/text_batch_fix.py --dry-run
  python tools/text_batch_fix.py --apply

CẢNH BÁO CONCURRENCY (DEBT-005): với --apply, main() ghi output/ep_01/episode.md + episode_golden_text.md
THẬT (dùng chung mọi phiên) KHÔNG có golden_lock. CHỈ chạy 1 lần bằng tay khi KHÔNG có phiên pytest/
render nào khác đang chạy. (verify_post_fix() đã cô lập tempfile từ DEBT-005 vòng 1 — an toàn; chỉ
đường --apply là ghi thật.) Được whitelist trong tests/test_no_unlocked_ep01_writer.py
(_MANUAL_TOOL_EXCEPTION) vì là công cụ thủ công, 0 caller tự động, không chạy lặp trong pytest suite.
"""
import argparse
import os
import shutil
import sys
import subprocess
import tempfile

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


TOOL_MAP = {
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

# Bo phu (bible/27) ma 2 tool trong TOOL_MAP can doc canh episode.md - copy luon
# vao tmp de khong bi thieu file khi chay trong thu muc cach ly.
_EXTRA_COPY_FILES = ["bible/27_fact_db.yaml"]


def verify_post_fix(text, verify_rules):
    """Apply `text` len 1 BAN COPY episode.md trong tempfile.TemporaryDirectory()
    rieng va chay verify rules TREN BAN COPY DO — KHONG BAO GIO dung vao
    output/ep_01/episode.md THAT, du chi tam thoi (DEBT-005 fix, kiem duyet 5/7
    toi: 2 phien chay dong thoi tren cung thu muc dung chung co the giam len
    file backup CO DINH cua nhau (episode.md.batchfix_bak) -> corrupt du lieu
    that. Trien khai cu ghi thang vao file that + backup/restore try-finally AN
    TOAN cho 1 tien trinh don le nhung KHONG an toan khi >=2 tien trinh chay
    cung luc — loai bo hoan toan rui ro bang cach khong bao gio cham vao file
    that, thay vi giam thieu bang lock/ten-file-ngau-nhien.

    Ca 8 tool trong TOOL_MAP + qa_eol_diacritic.py deu tu tinh duong dan episode.md
    bang `Path(__file__).resolve().parents[1] / 'output/ep_01/episode.md'` (dua
    tren VI TRI SCRIPT, khong phai cwd) — nen chi can COPY tool sang thu muc tam
    + dat episode.md dung cho tuong doi la moi tool TU DONG doc dung ban trong
    tmp, KHONG can sua logic ben trong bat ky tool QA nao."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        tmp_tools = tmp_root / "tools"
        tmp_ep_dir = tmp_root / "output" / "ep_01"
        tmp_tools.mkdir(parents=True)
        tmp_ep_dir.mkdir(parents=True)
        tmp_episode = tmp_ep_dir / "episode.md"
        tmp_episode.write_text(text, encoding="utf-8")

        needed_tools = {"tts_adapter_pre_render.py"} | {
            TOOL_MAP[r] for r in set(verify_rules) if r in TOOL_MAP}
        for tool_name in needed_tools:
            shutil.copy(BASE / "tools" / tool_name, tmp_tools / tool_name)
        for rel in _EXTRA_COPY_FILES:
            src = BASE / rel
            if src.exists():
                dst = tmp_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(src, dst)

        # Regen episode_tts_ready.md tren BAN COPY (giu dung y do ban goc:
        # 1 so QA tool tuong lai co the can file nay ke episode.md).
        subprocess.run([sys.executable, str(tmp_tools / "tts_adapter_pre_render.py"),
                        "--ep", "1", "--apply"], capture_output=True, timeout=30,
                       cwd=str(tmp_root))

        failed = []
        for rule in set(verify_rules):
            tool = TOOL_MAP.get(rule)
            if not tool:
                continue
            r = subprocess.run([sys.executable, str(tmp_tools / tool)],
                               capture_output=True, text=True, cwd=str(tmp_root), timeout=60,
                               encoding="utf-8", errors="ignore")
            if r.returncode != 0:
                failed.append(rule)
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
