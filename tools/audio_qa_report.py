"""Audio QA Report — orchestrator generates 10-field report post-render.

Fields (per Mr.Long lệnh):
  1. Path
  2. Duration
  3. Chunk Count
  4. Failed Chunk
  5. Voice Drift
  6. Repeated Line
  7. Technical Audio Metrics (10 sub-metrics)
  8. Whisper Compare Score
  9. Manual Listening (flag NEEDS_MR_LONG_LISTEN)
 10. Final Verdict (AUDIO_PASS / AUDIO_FAIL)

Usage:
  python tools/audio_qa_report.py --section hook
  python tools/audio_qa_report.py --full EP01_FULL_v100.mp3 EP01_VOICE_v100.wav
"""
import argparse
import json
import sys
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
from pathlib import Path
from datetime import datetime

BASE = Path(r"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio")
SECTIONS_DIR = BASE / "output/ep_01/sections"


def run_audio_metrics(wav_path):
    r = subprocess.run([sys.executable, str(BASE / "tools/audio_qa_metrics.py"), str(wav_path)],
                       capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=180)
    # Parse JSON from stdout
    try:
        json_start = r.stdout.find("{")
        if json_start >= 0:
            return json.loads(r.stdout[json_start:])
    except Exception:
        pass
    return None


def run_whisper_compare(section_name, model="medium"):
    r = subprocess.run([sys.executable, str(BASE / "tools/qa_whisper_compare.py"),
                        "--section", section_name, "--model", model, "--threshold", "0.20"],
                       capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=600)
    # Read JSON output
    wav = SECTIONS_DIR / f"{section_name}.wav"
    json_file = wav.with_suffix(".whisper_compare.json")
    if json_file.exists():
        return json.loads(json_file.read_text(encoding="utf-8"))
    return None


def run_post_render_audit(wav_path):
    r = subprocess.run([sys.executable, str(BASE / "tools/qa_post_render.py"), str(wav_path)],
                       capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=120)
    passed = "POST-RENDER GATE: PASS" in r.stdout
    # Extract specific numbers
    import re
    failed_chunks = 0
    repeated = 0
    voice_drift_score = "N/A"
    click_count = 0
    m = re.search(r"click_count:\s*(\d+)", r.stdout)
    if m: click_count = int(m.group(1))
    m = re.search(r"slow_onsets:\s*(\d+)", r.stdout)
    if m: failed_chunks = int(m.group(1))
    return {
        "post_render_pass": passed,
        "click_count": click_count,
        "slow_onsets": failed_chunks,
        "raw_output_tail": r.stdout[-500:],
    }


def generate_report(section_name=None, full_mp3=None, full_wav=None, whisper_model="medium"):
    report = {
        "report_timestamp": datetime.now().isoformat(),
        "git_version": "v1.0.0-rc1",
    }

    if section_name:
        wav = SECTIONS_DIR / f"{section_name}.wav"
        spec_file = SECTIONS_DIR / f"spec_{section_name}.json"
        if not wav.exists():
            return {"error": f"WAV not found: {wav}"}
        spec = json.loads(spec_file.read_text(encoding="utf-8")) if spec_file.exists() else {"sentences": []}
        report["1_path"] = str(wav)
        report["2_duration_sec"] = None  # filled below
        report["3_chunk_count"] = len(spec.get("sentences", []))

        # Audio metrics
        m = run_audio_metrics(wav)
        if m:
            report["2_duration_sec"] = m.get("duration_sec")
            report["7_technical_audio_metrics"] = m
        # Post-render audit (click/slow_onset/etc)
        pra = run_post_render_audit(wav)
        report["4_failed_chunks"] = pra.get("slow_onsets", "N/A")
        report["voice_drift_note"] = "Em LLM text-only — voice drift requires resemblyzer (TBD R143)"
        report["5_voice_drift"] = "NEEDS_RESEMBLYZER"
        report["6_repeated_line"] = "Em text-level KHÔNG detect audio repeat — requires Whisper diarization"
        report["post_render_audit"] = pra

        # Whisper compare
        wc = run_whisper_compare(section_name, model=whisper_model)
        if wc:
            report["8_whisper_compare_score"] = {
                "wer_pct": wc.get("overall_wer_pct"),
                "similarity_pct": wc.get("similarity_pct"),
                "verdict": wc.get("verdict"),
            }
        else:
            report["8_whisper_compare_score"] = "FAILED_TO_RUN"

        report["9_manual_listening"] = "NEEDS_MR_LONG_LISTEN (em LLM không có ear)"

        # Final verdict
        all_pass = (
            pra.get("post_render_pass", False)
            and wc and wc.get("verdict") == "PASS"
            and (m.get("clip_count", 99) == 0 if m else False)
        )
        report["10_final_verdict"] = "AUDIO_PASS" if all_pass else "AUDIO_FAIL_REVIEW_NEEDED"

    elif full_mp3 and full_wav:
        report["1_path"] = str(full_mp3)
        m_mp3 = run_audio_metrics(full_mp3)
        m_wav = run_audio_metrics(full_wav)
        if m_mp3:
            report["2_duration_sec"] = m_mp3.get("duration_sec")
            report["7_technical_audio_metrics"] = {
                "mp3": m_mp3,
                "wav_source": m_wav,
            }
        report["3_chunk_count"] = "271 (total across 6 sections)"
        report["4_failed_chunks"] = "see per-section reports"
        report["5_voice_drift"] = "NEEDS_RESEMBLYZER"
        report["6_repeated_line"] = "NEEDS_WHISPER_DIARIZATION"
        report["8_whisper_compare_score"] = "Skip full mp3 (use per-section)"
        report["9_manual_listening"] = "NEEDS_MR_LONG_LISTEN"
        report["10_final_verdict"] = "PENDING_PER_SECTION_AGGREGATE"

    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", help="hook/setup/incident/reveal/payoff/cliffhanger")
    ap.add_argument("--full-mp3", help="EP01_FULL_v100.mp3 path")
    ap.add_argument("--full-wav", help="EP01_VOICE_v100.wav path")
    ap.add_argument("--whisper-model", default="medium")
    ap.add_argument("--out", default=None, help="Output JSON path")
    args = ap.parse_args()

    report = generate_report(
        section_name=args.section,
        full_mp3=args.full_mp3,
        full_wav=args.full_wav,
        whisper_model=args.whisper_model,
    )

    print(json.dumps(report, indent=2, ensure_ascii=False))

    if args.out:
        Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nReport saved: {args.out}")


if __name__ == "__main__":
    main()
