"""Tier 2.1 — Audio Pre-Ship Gate.

Run ALL audio QA before SHIP:
  1. audio_qa_metrics (peak/LUFS/clip/silence)
  2. qa_concat_silence (R94b silence bridges)
  3. qa_post_render per section (R87/R88/R89/R96)

Block ship if ANY critical fails.

Usage:
  python tools/audio_pre_ship_gate.py --mp3 output/ep_01/EP01_FULL_v102.mp3
  python tools/audio_pre_ship_gate.py --wav output/ep_01/EP01_VOICE_v102.wav --mp3 output/ep_01/EP01_FULL_v102.mp3
"""
import argparse
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def run_tool(args_list, timeout=300):
    r = subprocess.run([sys.executable] + args_list,
                       capture_output=True, text=True, cwd=str(BASE), timeout=timeout,
                       encoding="utf-8", errors="ignore")
    return r.returncode, r.stdout, r.stderr


def parse_metrics_json(stdout):
    """Extract last JSON block from audio_qa_metrics output."""
    j_start = stdout.rfind("{")
    if j_start < 0:
        return None
    try:
        return json.loads(stdout[j_start:])
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mp3", help="Final mix MP3 path")
    ap.add_argument("--wav", help="Voice-only WAV path")
    ap.add_argument("--expected-boundaries", type=int, default=5)
    args = ap.parse_args()

    print("=" * 60)
    print("AUDIO PRE-SHIP GATE (Tier 2.1)")
    print("=" * 60)

    results = []

    # 1. Audio metrics on final mix
    if args.mp3:
        print(f"\n[1] audio_qa_metrics — {Path(args.mp3).name}")
        code, out, _ = run_tool([str(BASE / "tools/audio_qa_metrics.py"), args.mp3])
        m = parse_metrics_json(out)
        if m:
            clip = m.get("clip_count", 999)
            peak = m.get("peak_dbfs", 99)
            verdict = "PASS" if (clip == 0 and peak <= -0.1) else "FAIL"
            print(f"  Peak: {peak} dBFS / Clip: {clip} → {verdict}")
            results.append(("audio_metrics_mp3", verdict, m))
        else:
            print("  ERROR: Failed to parse metrics")
            results.append(("audio_metrics_mp3", "ERROR", {}))

    # 2. Concat silence on voice WAV (R94b)
    if args.wav:
        print(f"\n[2] qa_concat_silence (R94b) — {Path(args.wav).name}")
        code, out, _ = run_tool([str(BASE / "tools/qa_concat_silence.py"),
                                  "--wav", args.wav,
                                  "--expected_count", str(args.expected_boundaries)])
        passed = code == 0
        print(out.split("== R94b GATE")[1][:100] if "R94b GATE" in out else out[-200:])
        verdict = "PASS" if passed else "FAIL"
        print(f"  → {verdict}")
        results.append(("concat_silence_r94b", verdict, {"exit_code": code}))

    # 3. Post-render audit per section
    print(f"\n[3] qa_post_render — 6 sections STAGE 3")
    sec_pass = 0
    sec_fail = 0
    for s in ["hook", "setup", "incident", "reveal", "payoff", "cliffhanger"]:
        wav_path = BASE / "output/ep_01/sections" / f"{s}.wav"
        if not wav_path.exists():
            print(f"  ⚠️ {s}: WAV not found, skip")
            continue
        code, out, _ = run_tool([str(BASE / "tools/qa_post_render.py"), str(wav_path)], timeout=60)
        passed = code == 0
        if passed: sec_pass += 1
        else: sec_fail += 1
        mark = "✅" if passed else "❌"
        print(f"  {mark} {s}: exit={code}")
    print(f"  Sections: {sec_pass} PASS / {sec_fail} FAIL")
    results.append(("post_render_audit", "PASS" if sec_fail == 0 else "FAIL",
                    {"sections_pass": sec_pass, "sections_fail": sec_fail}))

    # Final verdict
    print()
    print("=" * 60)
    all_pass = all(r[1] == "PASS" for r in results)
    final = "🟢 AUDIO PRE-SHIP GATE: PASS — SHIP ALLOWED" if all_pass else "🔴 AUDIO PRE-SHIP GATE: FAIL — BLOCK SHIP"
    print(final)
    print("=" * 60)
    for name, verdict, _ in results:
        mark = "✅" if verdict == "PASS" else "❌"
        print(f"  {mark} {name}: {verdict}")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
