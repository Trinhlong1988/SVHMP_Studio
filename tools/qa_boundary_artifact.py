"""
qa_boundary_artifact.py — R188 enforcement (Mr.Long TOP priority 5-star)
Detect "ù / xì / ẹ" artifacts at [pause] boundaries via spectral analysis.

Mr.Long docx 30/6: TTS vocoder mất ổn định tại boundary → "ù ù / xì / ẹ".
Detect window: ±200ms around chunk boundaries (concat seams + pause inserts).

Method:
  1. Load section WAV
  2. Identify boundary timestamps from concat_silence.json (R94b 1500ms gaps)
  3. For each boundary: extract ±200ms window
  4. Compute spectral signature:
     - high-freq energy ratio (4-8kHz) — sibilance "xì"
     - low-freq drone (40-150Hz) — "ù"
     - sub-harmonic instability — "ẹ"
  5. Compare vs clean reference (mid-chunk same section)
  6. Flag if any band > threshold

Usage:
    python tools/qa_boundary_artifact.py --wav output/ep_01/sections/cliffhanger.wav
    python tools/qa_boundary_artifact.py --wav output/ep_01/EP01_VOICE_v108.wav --boundaries output/ep_01/EP01_VOICE_v108.concat_silence.json
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np

try:
    import librosa
except ImportError:
    librosa = None

REPO_ROOT = Path(__file__).resolve().parent.parent

WINDOW_MS = 200
SIBILANCE_BAND = (4000, 8000)
DRONE_BAND = (40, 150)
SIBILANCE_THRESHOLD_RATIO = 2.5
DRONE_THRESHOLD_DB = 6.0
SUBHARMONIC_THRESHOLD = 0.35


@dataclass
class BoundaryArtifact:
    boundary_ts_sec: float
    artifact_type: str
    severity: str
    metric_value: float
    threshold: float
    detail: str


def band_energy_db(y: np.ndarray, sr: int, fmin: float, fmax: float) -> float:
    if len(y) < 256:
        return -120.0
    n_fft = min(2048, 2 ** int(np.floor(np.log2(len(y)))))
    if n_fft < 256:
        return -120.0
    S = np.abs(librosa.stft(y, n_fft=n_fft))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    mask = (freqs >= fmin) & (freqs <= fmax)
    if not np.any(mask):
        return -120.0
    band_pow = np.mean(S[mask] ** 2) + 1e-12
    return 10.0 * np.log10(band_pow)


def detect_boundary_artifacts(
    audio: np.ndarray, sr: int, boundary_ts: list[float], window_ms: int = WINDOW_MS
) -> list[BoundaryArtifact]:
    findings: list[BoundaryArtifact] = []
    w = int(window_ms / 1000.0 * sr)
    if len(boundary_ts) == 0:
        return findings

    mid_sample = int(len(audio) * 0.5)
    ref_window = audio[max(0, mid_sample - w) : mid_sample + w]
    ref_sibilance = band_energy_db(ref_window, sr, *SIBILANCE_BAND)
    ref_drone = band_energy_db(ref_window, sr, *DRONE_BAND)

    for ts in boundary_ts:
        center = int(ts * sr)
        lo = max(0, center - w)
        hi = min(len(audio), center + w)
        win = audio[lo:hi]
        if len(win) < 256:
            continue
        sib = band_energy_db(win, sr, *SIBILANCE_BAND)
        drone = band_energy_db(win, sr, *DRONE_BAND)

        sib_ratio = (sib - ref_sibilance) if ref_sibilance > -120 else 0.0
        drone_offset = (drone - ref_drone) if ref_drone > -120 else 0.0

        if sib_ratio > SIBILANCE_THRESHOLD_RATIO:
            findings.append(
                BoundaryArtifact(
                    boundary_ts_sec=round(ts, 3),
                    artifact_type="boundary_sibilance_xi",
                    severity="HIGH",
                    metric_value=round(sib_ratio, 2),
                    threshold=SIBILANCE_THRESHOLD_RATIO,
                    detail=f"4-8kHz energy +{sib_ratio:.2f}dB vs mid-chunk ref",
                )
            )
        if drone_offset > DRONE_THRESHOLD_DB:
            findings.append(
                BoundaryArtifact(
                    boundary_ts_sec=round(ts, 3),
                    artifact_type="boundary_drone_uu",
                    severity="HIGH",
                    metric_value=round(drone_offset, 2),
                    threshold=DRONE_THRESHOLD_DB,
                    detail=f"40-150Hz drone +{drone_offset:.2f}dB vs mid-chunk ref",
                )
            )

        # Sub-harmonic instability — measure pitch confusion at boundary
        try:
            f0 = librosa.yin(
                win.astype(np.float32),
                fmin=80,
                fmax=400,
                sr=sr,
                frame_length=min(1024, max(256, len(win) // 4 * 4)),
            )
            if len(f0) > 4:
                f0_valid = f0[~np.isnan(f0)]
                if len(f0_valid) > 2:
                    f0_std = float(np.std(f0_valid))
                    f0_mean = float(np.mean(f0_valid))
                    if f0_mean > 0 and f0_std / f0_mean > SUBHARMONIC_THRESHOLD:
                        findings.append(
                            BoundaryArtifact(
                                boundary_ts_sec=round(ts, 3),
                                artifact_type="boundary_subharmonic_e",
                                severity="MEDIUM",
                                metric_value=round(f0_std / f0_mean, 3),
                                threshold=SUBHARMONIC_THRESHOLD,
                                detail=f"F0 std/mean {f0_std / f0_mean:.3f} (unstable pitch)",
                            )
                        )
        except Exception:
            pass

    return findings


def boundaries_from_concat_silence(json_path: Path) -> list[float]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    out = []
    for b in data.get("boundaries", []):
        ts = b.get("end_sec") or b.get("start_sec")
        if ts is not None:
            out.append(float(ts))
    return out


def boundaries_auto(audio: np.ndarray, sr: int, min_gap_ms: int = 800) -> list[float]:
    """Fallback: detect silence gaps as boundaries."""
    rms = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
    hop = 512
    silence_mask = rms < (np.percentile(rms, 20) * 0.5)
    boundaries = []
    in_silence = False
    silence_start = 0
    min_frames = int(min_gap_ms / 1000.0 * sr / hop)
    for i, s in enumerate(silence_mask):
        if s and not in_silence:
            silence_start = i
            in_silence = True
        elif not s and in_silence:
            if i - silence_start >= min_frames:
                ts = (silence_start + (i - silence_start) // 2) * hop / sr
                boundaries.append(float(ts))
            in_silence = False
    return boundaries


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if librosa is None:
        print("[R188] FAIL — librosa not installed")
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--boundaries", default=None, help="concat_silence.json with boundary list")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    wav_path = Path(args.wav)
    if not wav_path.exists():
        print(f"[R188] FAIL — missing {wav_path}")
        return 2

    audio, sr = librosa.load(wav_path, sr=None, mono=True)

    if args.boundaries and Path(args.boundaries).exists():
        boundaries = boundaries_from_concat_silence(Path(args.boundaries))
    else:
        boundaries = boundaries_auto(audio, sr)

    findings = detect_boundary_artifacts(audio, sr, boundaries)

    n_high = sum(1 for f in findings if f.severity == "HIGH")
    n_med = sum(1 for f in findings if f.severity == "MEDIUM")
    verdict = "PASS" if n_high == 0 else "FAIL"

    report = {
        "rule": "R188 boundary_artifact",
        "wav": str(wav_path),
        "duration_sec": round(len(audio) / sr, 2),
        "boundaries_count": len(boundaries),
        "n_high": n_high,
        "n_medium": n_med,
        "verdict": verdict,
        "findings": [asdict(f) for f in findings],
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[R188] {wav_path.name}  boundaries={len(boundaries)}  HIGH={n_high}  MED={n_med}  verdict={verdict}")
        for f in findings[:20]:
            print(f"  {f.severity} @{f.boundary_ts_sec}s  {f.artifact_type}  {f.detail}")

    return 0 if n_high == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
