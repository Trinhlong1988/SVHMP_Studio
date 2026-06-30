"""Audio QA Metrics — compute 10 metrics per Mr.Long lệnh.

Metrics:
  1. Peak (dBFS)        — max sample amplitude (peak-of-peaks)
  2. LUFS-I             — integrated loudness (EBU R128)
  3. True Peak (dBTP)   — inter-sample peak (-1 sample reconstruction)
  4. Noise Floor (dBFS) — bottom 10% percentile RMS
  5. Silence Ratio (%)  — % samples < -50dBFS
  6. Longest Silence    — seconds of contiguous silence < -50dBFS
  7. Clip Count         — samples at or above 0 dBFS
  8. DC Offset (dBFS)   — mean sample offset from 0
  9. Sample Rate        — Hz
 10. Bit Depth          — bits/sample

Usage:
  python tools/audio_qa_metrics.py <input.wav_or_mp3>
"""
import sys
import json
import subprocess
import re
import soundfile as sf
import numpy as np
from pathlib import Path


def compute_metrics(audio_path):
    audio_path = str(audio_path)
    # Read audio
    audio, sr = sf.read(audio_path)
    if audio.ndim > 1:
        audio = audio[:, 0]  # mono first channel
    info = sf.info(audio_path)

    # 1. Peak dBFS
    peak = np.max(np.abs(audio))
    peak_dbfs = 20 * np.log10(peak + 1e-12)

    # 4. Noise Floor: bottom 10% percentile of windowed RMS
    win = int(sr * 0.05)  # 50ms windows
    if win > 0:
        rms_windows = np.sqrt(np.convolve(audio**2, np.ones(win)/win, mode='valid'))
        rms_windows = rms_windows[rms_windows > 1e-8]
        noise_floor = np.percentile(rms_windows, 10) if len(rms_windows) > 0 else 0
        noise_floor_dbfs = 20 * np.log10(noise_floor + 1e-12)
    else:
        noise_floor_dbfs = -120

    # 5. Silence Ratio: % samples below -50 dBFS
    silence_thr = 10 ** (-50 / 20)
    silence_samples = np.sum(np.abs(audio) < silence_thr)
    silence_ratio = silence_samples / len(audio) * 100

    # 6. Longest Silence (seconds)
    is_silent = np.abs(audio) < silence_thr
    longest_silence_samples = 0
    cur = 0
    for s in is_silent:
        if s:
            cur += 1
            if cur > longest_silence_samples:
                longest_silence_samples = cur
        else:
            cur = 0
    longest_silence_sec = longest_silence_samples / sr

    # 7. Clip Count: samples >= 0 dBFS (1.0)
    clip_count = int(np.sum(np.abs(audio) >= 0.999))

    # 8. DC Offset
    dc_mean = np.mean(audio)
    dc_offset_dbfs = 20 * np.log10(abs(dc_mean) + 1e-12)

    # 9. Sample Rate
    sample_rate = info.samplerate

    # 10. Bit Depth
    subtype = info.subtype
    bit_depth_map = {
        "PCM_16": 16, "PCM_24": 24, "PCM_32": 32,
        "FLOAT": 32, "DOUBLE": 64, "PCM_S8": 8, "PCM_U8": 8,
    }
    bit_depth = bit_depth_map.get(subtype, "unknown")
    if isinstance(bit_depth, str) and subtype.startswith("MPEG"):
        bit_depth = "MP3-VBR"

    # 2 + 3 LUFS-I + True Peak via ffmpeg loudnorm
    cmd = [
        "ffmpeg", "-hide_banner", "-i", audio_path,
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json",
        "-f", "null", "-"
    ]
    lufs_i = None
    true_peak = None
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=180)
        out = (r.stderr or "") + (r.stdout or "")
        # ffmpeg prints JSON block after "[Parsed_loudnorm_..." header
        # Find LAST JSON block (most relevant)
        json_blocks = re.findall(r"\{[^{}]+\}", out)
        if json_blocks:
            ln = json.loads(json_blocks[-1])
            if "input_i" in ln:
                lufs_i = float(ln["input_i"])
            if "input_tp" in ln:
                true_peak = float(ln["input_tp"])
    except Exception as e:
        pass

    duration_sec = len(audio) / sr

    return {
        "file": audio_path,
        "duration_sec": round(duration_sec, 2),
        "peak_dbfs": round(float(peak_dbfs), 2),
        "lufs_i": round(lufs_i, 2) if lufs_i is not None else "ffmpeg_unavailable",
        "true_peak_dbtp": round(true_peak, 2) if true_peak is not None else "ffmpeg_unavailable",
        "noise_floor_dbfs": round(float(noise_floor_dbfs), 2),
        "silence_ratio_pct": round(float(silence_ratio), 2),
        "longest_silence_sec": round(float(longest_silence_sec), 3),
        "clip_count": clip_count,
        "dc_offset_dbfs": round(float(dc_offset_dbfs), 2),
        "sample_rate_hz": sample_rate,
        "bit_depth": bit_depth,
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/audio_qa_metrics.py <input.wav_or_mp3>")
        sys.exit(1)
    audio_path = Path(sys.argv[1])
    if not audio_path.exists():
        print(f"ERROR: file not found: {audio_path}")
        sys.exit(1)

    print(f"=== AUDIO QA METRICS — {audio_path.name} ===")
    m = compute_metrics(audio_path)
    for k, v in m.items():
        print(f"  {k:25s}: {v}")
    print()
    # JSON output too
    print(json.dumps(m, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
