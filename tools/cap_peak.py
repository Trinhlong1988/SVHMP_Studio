"""Peak cap tool — idempotent volume reduction để hardlock peak ≤ -1.0 dB.

Usage:
    python tools/cap_peak.py <wav_file>           # in-place fix
    python tools/cap_peak.py --batch <wav_dir>    # batch cả folder
    python tools/cap_peak.py --check <wav_file>   # check only, exit 0/1

Why exists:
    setup.wav peak -0.0 CLIP recur 2 lần (CMD #2 re-render lặp lại bug).
    svhmp_v13_render.py có alimiter=0.85 nhưng CMD #2 mix step (R104b boost) push peak qua 0.
    Tool này: post-mix gate hardlock cap peak ≤ -1.0 dB cho mọi WAV output.

Pattern wire vào pipeline:
    1. Sau mọi mix output: python tools/cap_peak.py output.wav
    2. Pre-publish hook: python tools/cap_peak.py --check output.wav
    3. Idempotent: nếu peak đã ≤ -1.0 → no-op, exit 0
"""
import argparse
import shutil
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
import sys
import wave
from pathlib import Path

import numpy as np

PEAK_TARGET_DB = -1.0  # Hardlock target — output peak ≤ -1.0 dB
PEAK_TOLERANCE_DB = -0.5  # Trigger fix nếu peak > -0.5 dB (close to clip)


def measure_peak_db(wav_path: Path) -> float:
    w = wave.open(str(wav_path), "rb")
    arr = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768.0
    w.close()
    if len(arr) == 0:
        return -200.0
    return 20 * np.log10(np.max(np.abs(arr)) + 1e-12)


def apply_volume_reduction(wav_path: Path, db_reduce: float) -> None:
    """Apply ffmpeg volume=-X dB in-place (with .bak backup)."""
    backup = wav_path.with_suffix(wav_path.suffix + ".bak.cap_peak")
    shutil.copy2(wav_path, backup)
    tmp = wav_path.with_suffix(wav_path.suffix + ".tmp.cap_peak")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(wav_path),
         "-filter:a", f"volume={db_reduce}dB",
         "-c:a", "pcm_s16le", str(tmp)],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    tmp.replace(wav_path)


def cap_one(wav_path: Path, check_only: bool = False) -> int:
    """Cap peak ≤ PEAK_TARGET_DB. Return 0 if OK or fixed, 1 if check_only and still over."""
    if not wav_path.exists():
        print(f"[ERR] {wav_path} not found")
        return 2
    peak = measure_peak_db(wav_path)
    if peak <= PEAK_TOLERANCE_DB:
        print(f"[OK] {wav_path.name}: peak {peak:.2f} dB (≤ {PEAK_TOLERANCE_DB} threshold)")
        return 0
    if check_only:
        print(f"[FAIL] {wav_path.name}: peak {peak:.2f} dB > {PEAK_TOLERANCE_DB} threshold")
        return 1
    # Need fix: reduce volume to bring peak to PEAK_TARGET_DB
    db_reduce = PEAK_TARGET_DB - peak
    print(f"[FIX] {wav_path.name}: peak {peak:.2f} dB → applying {db_reduce:.2f} dB")
    apply_volume_reduction(wav_path, db_reduce)
    new_peak = measure_peak_db(wav_path)
    print(f"[DONE] {wav_path.name}: peak {new_peak:.2f} dB (backup .bak.cap_peak)")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", help="WAV file or directory")
    ap.add_argument("--batch", help="Batch directory containing *.wav")
    ap.add_argument("--check", action="store_true", help="Check only, no modify")
    args = ap.parse_args()

    if args.batch:
        wavs = sorted(Path(args.batch).glob("*.wav"))
        # Skip .raw / .bak files
        wavs = [w for w in wavs if ".raw" not in w.name and ".bak" not in w.name]
        if not wavs:
            print(f"[ERR] No WAVs in {args.batch}")
            return 2
        fail = 0
        for w in wavs:
            r = cap_one(w, check_only=args.check)
            if r != 0: fail += 1
        print(f"\nProcessed {len(wavs)} WAVs | {fail} fail")
        return 1 if fail else 0

    if not args.path:
        ap.print_help()
        return 2
    return cap_one(Path(args.path), check_only=args.check)


if __name__ == "__main__":
    sys.exit(main())
