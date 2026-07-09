"""Test R86 + R128 — Forbidden phrases.

PASS: clean text
FAIL R86: ngã/nặng/hỏi EOL
FAIL R128: generic AI phrase overuse
EDGE: phrase ở threshold boundary
"""
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
EPISODE = BASE / "output/ep_01/episode.md"
READY = BASE / "output/ep_01/episode_tts_ready.md"
R86_TOOL = BASE / "tools/qa_eol_diacritic.py"
R128_TOOL = BASE / "tools/qa_anti_generic.py"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # tests/
from _golden_lock import golden_lock  # FIX DEBT-005: serialize ghi episode.md THAT cross-process


def _atomic_write(path, content):
    """Write atomically (tmp + os.replace) so a write interrupted mid-flight
    never leaves `path` half-written. See tools/text_batch_fix.py for the
    same helper — this file has the same golden-EP01-write hazard: it
    replaces output/ep_01/episode.md with throwaway probe text and must
    guarantee restore even if a subprocess call raises/times out."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def run_tool(tool):
    result = subprocess.run(
        [sys.executable, str(tool)],
        capture_output=True, text=True, cwd=str(BASE),
        encoding="utf-8", errors="ignore", timeout=30,
    )
    return result.returncode, result.stdout


def case(name, text, tool, expect_fail):
    # golden_lock: doc orig + toan bo mutate/restore trong khoa cross-process -> khong tien
    # trinh nao khac ghi/doc episode.md THAT giua chung (FIX TRIET DE DEBT-005).
    with golden_lock():
        orig = EPISODE.read_text(encoding="utf-8")
        ready_orig = READY.read_text(encoding="utf-8") if READY.exists() else None
        try:
            _atomic_write(EPISODE, text)
            # Rebuild tts_ready so the pipeline stays internally consistent for the
            # duration of the probe. NOTE: writes into the REAL
            # output/ep_01/episode_tts_ready.md — finally restores byte-for-byte from
            # ready_orig (process_ep() re-derivation khong byte-match golden committed).
            subprocess.run([sys.executable, str(BASE / "tools/tts_adapter_pre_render.py"), "--ep", "1", "--apply"],
                           capture_output=True, cwd=str(BASE), timeout=30)
            code, out = run_tool(tool)
            if expect_fail:
                assert code != 0, f"{name} should FAIL: {out[-200:]}"
                print(f"  ✅ {name}: caught")
            else:
                assert code == 0, f"{name} should PASS: {out[-200:]}"
                print(f"  ✅ {name}: passed")
        finally:
            # ALWAYS restore, even if the try block raised (timeout/crash/etc).
            _atomic_write(EPISODE, orig)
            if ready_orig is not None:
                _atomic_write(READY, ready_orig)


def main():
    # R86 tests
    print("=== TEST R86 EOL diacritic ===")
    case("PASS clean EOL", "## 1. HOOK\nĐây là câu rõ ràng.\n", R86_TOOL, expect_fail=False)
    case("FAIL ngã EOL 'cũ'", "## 1. HOOK\nĐây là câu thử với từ cũ.\n", R86_TOOL, expect_fail=True)
    case("FAIL nặng EOL 'đợi'", "## 1. HOOK\nAnh ngồi đợi.\n", R86_TOOL, expect_fail=True)
    case("FAIL hỏi EOL 'bảy'", "## 1. HOOK\nGhế số bảy.\n", R86_TOOL, expect_fail=True)

    # R128 tests
    print("\n=== TEST R128 anti-generic ===")
    case("PASS no generic", "## 1. HOOK\nĐây là câu kể chuyện bình thường.\n", R128_TOOL, expect_fail=False)
    case("FAIL 'có lẽ' x5", "## 1. HOOK\nCó lẽ vậy. Có lẽ thế. Có lẽ ngày mai. Có lẽ không. Có lẽ lúc khác.\n", R128_TOOL, expect_fail=True)
    case("FAIL 'không hiểu sao' x3", "## 1. HOOK\nKhông hiểu sao. Không hiểu sao. Không hiểu sao một lần nữa.\n", R128_TOOL, expect_fail=True)
    case("EDGE 'có lẽ' x2 (boundary)", "## 1. HOOK\nCó lẽ thế. Có lẽ vậy.\n", R128_TOOL, expect_fail=False)

    print("\n=== ALL TESTS DONE ===")


if __name__ == "__main__":
    main()
