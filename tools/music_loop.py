"""Tier 2.1 — Music loop/extend to cover voice duration + outro margin.

Usage:
  python tools/music_loop.py --voice <voice.wav> --music <music.mp3> --output <looped.mp3> [--outro-sec 5]
"""
import argparse
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
import sys
from pathlib import Path
import soundfile as sf


def get_duration_sec(path):
    """Get audio duration via ffprobe."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30)
    return float(r.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", required=True)
    ap.add_argument("--music", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--outro-sec", type=float, default=5.0, help="Outro music margin after voice ends")
    ap.add_argument("--intro-sec", type=float, default=6.0, help="Music starts before voice (intro)")
    args = ap.parse_args()

    voice_dur = get_duration_sec(args.voice)
    music_dur = get_duration_sec(args.music)
    target_dur = args.intro_sec + voice_dur + args.outro_sec

    print(f"=== MUSIC LOOP ===")
    print(f"  Voice: {voice_dur:.2f}s")
    print(f"  Music source: {music_dur:.2f}s")
    print(f"  Target (intro {args.intro_sec}s + voice {voice_dur:.2f}s + outro {args.outro_sec}s): {target_dur:.2f}s")
    print()

    if music_dur >= target_dur:
        print(f"  Music already covers target. Trimming to {target_dur:.2f}s + fade out.")
        # Trim + add fade out at end
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", args.music,
            "-af", f"atrim=0:{target_dur},afade=t=out:st={target_dur-3}:d=3",
            "-c:a", "libmp3lame", "-q:a", "2",
            args.output
        ]
    else:
        loops = int(target_dur / music_dur) + 1
        print(f"  Music shorter. Looping {loops}x + crossfade 2s.")
        # Use aloop filter + trim
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-stream_loop", str(loops),
            "-i", args.music,
            "-af", f"atrim=0:{target_dur},afade=t=out:st={target_dur-3}:d=3",
            "-c:a", "libmp3lame", "-q:a", "2",
            args.output
        ]

    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=300, creationflags=CREATE_NO_WINDOW)
    if r.returncode != 0:
        print(f"ERROR: ffmpeg failed:\n{r.stderr[-500:]}")
        sys.exit(1)

    final_dur = get_duration_sec(args.output)
    print(f"  ✅ Output: {args.output} ({final_dur:.2f}s)")
    # Verify duration close to target
    if abs(final_dur - target_dur) > 1.0:
        print(f"  ⚠️ Duration mismatch: target {target_dur:.2f}s vs actual {final_dur:.2f}s")
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
