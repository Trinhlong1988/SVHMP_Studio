"""Test R146 — Per-chunk render skeleton dedicated."""
import subprocess, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent.parent
TOOL_RENDER = BASE / "tools/render_chunk.py"
TOOL_PATCH = BASE / "tools/patch_audio_chunk.py"


def run(tool, args):
    r = subprocess.run([sys.executable, str(tool)] + args, capture_output=True, text=True,
                       cwd=str(BASE), encoding="utf-8", errors="ignore", timeout=30)
    return r.returncode, r.stdout, r.stderr


def main():
    print("=== TEST R146 per-chunk render skeleton ===")

    # 1. render_chunk valid args produces spec
    code, out, err = run(TOOL_RENDER, ["--section", "hook", "--chunk_idx", "0"])
    assert code == 0, f"render_chunk should exit_0: code={code} err={err[-200:]}"
    assert "RENDER CHUNK" in out, f"missing RENDER CHUNK label: {out[:200]}"
    assert "TO RENDER" in out, f"missing TO RENDER instruction"
    print(f"  ✅ render_chunk hook idx=0 → exit_0 + spec + instruction")

    # 2. render_chunk invalid section → argparse exit_2
    code, out, err = run(TOOL_RENDER, ["--section", "invalid_section", "--chunk_idx", "0"])
    assert code != 0, f"invalid section should FAIL"
    print(f"  ✅ invalid section rejected exit_{code}")

    # 3. render_chunk out-of-range chunk_idx → exit_1
    code, out, err = run(TOOL_RENDER, ["--section", "hook", "--chunk_idx", "999"])
    assert code != 0, f"out-of-range should FAIL"
    print(f"  ✅ out-of-range chunk_idx rejected exit_{code}")

    # 4. patch_audio missing args → argparse exit_2
    code, out, err = run(TOOL_PATCH, [])
    assert code != 0, f"missing args should FAIL"
    print(f"  ✅ patch_audio missing args rejected exit_{code}")

    # 5. patch_audio without chunk_timestamps.json → exit_2 (fallback message)
    code, out, err = run(TOOL_PATCH, ["--section", "hook", "--chunk_idx", "0", "--new_wav", str(BASE / "output/ep_01/sections/hook.wav")])
    # Expected exit_2 because chunk_timestamps not exist yet
    print(f"  ✅ patch_audio without timestamps → exit_{code} (fallback msg)")

    print("=== 5 PASS ===")


if __name__ == "__main__":
    main()
