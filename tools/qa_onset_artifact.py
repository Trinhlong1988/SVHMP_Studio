"""
qa_onset_artifact.py — R190b enforcement
Detect onset artifacts ("ẹ" at chunk start, slow ramp, wrong F0).

Method:
  - First 100ms of each chunk:
    - Check sharp pitch jump in F0
    - Check abnormal spectral peak vs rest of chunk
  - Flag if onset stats deviate > threshold
"""
from __future__ import annotations
import argparse, json, sys
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np

try:
    import librosa
except ImportError:
    librosa = None

ONSET_MS = 100
F0_JUMP_RATIO = 1.5
SPECTRAL_PEAK_RATIO = 2.0


@dataclass
class OnsetArtifact:
    boundary_ts_sec: float
    artifact_type: str
    severity: str
    metric: float


def detect_onset_artifacts(audio: np.ndarray, sr: int, boundary_ts: list[float]) -> list[OnsetArtifact]:
    out: list[OnsetArtifact] = []
    onset_samples = int(ONSET_MS / 1000.0 * sr)
    if onset_samples < 256:
        return out

    for ts in boundary_ts:
        center = int(ts * sr)
        onset_window = audio[center : center + onset_samples]
        rest_window = audio[center + onset_samples : center + onset_samples + 4 * onset_samples]
        if len(onset_window) < 256 or len(rest_window) < 256:
            continue

        try:
            f0_onset = librosa.yin(onset_window.astype(np.float32), fmin=80, fmax=400, sr=sr,
                                   frame_length=min(512, max(256, len(onset_window) // 4 * 4)))
            f0_rest = librosa.yin(rest_window.astype(np.float32), fmin=80, fmax=400, sr=sr,
                                  frame_length=512)
            f0_o = f0_onset[~np.isnan(f0_onset)]
            f0_r = f0_rest[~np.isnan(f0_rest)]
            if len(f0_o) > 0 and len(f0_r) > 0:
                mu_o = float(np.mean(f0_o))
                mu_r = float(np.mean(f0_r))
                if mu_r > 10 and mu_o > 10:
                    jump = max(mu_o, mu_r) / max(1.0, min(mu_o, mu_r))
                    if jump > F0_JUMP_RATIO:
                        out.append(OnsetArtifact(
                            boundary_ts_sec=round(ts, 3),
                            artifact_type="onset_f0_jump_e",
                            severity="HIGH",
                            metric=round(jump, 2),
                        ))
        except Exception:
            pass

        peak_o = float(np.max(np.abs(onset_window)))
        peak_r = float(np.max(np.abs(rest_window)))
        if peak_r > 1e-4:
            ratio = peak_o / peak_r
            if ratio > SPECTRAL_PEAK_RATIO:
                out.append(OnsetArtifact(
                    boundary_ts_sec=round(ts, 3),
                    artifact_type="onset_peak_spike",
                    severity="MEDIUM",
                    metric=round(ratio, 2),
                ))
    return out


def boundaries_auto(audio: np.ndarray, sr: int, min_gap_ms: int = 600) -> list[float]:
    rms = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
    hop = 512
    silence_mask = rms < (np.percentile(rms, 20) * 0.5)
    boundaries = []
    min_frames = int(min_gap_ms / 1000.0 * sr / hop)
    in_silence = False
    silence_start = 0
    for i, s in enumerate(silence_mask):
        if s and not in_silence:
            silence_start = i
            in_silence = True
        elif not s and in_silence:
            if i - silence_start >= min_frames:
                ts = i * hop / sr
                boundaries.append(float(ts))
            in_silence = False
    return boundaries


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if librosa is None:
        print("[R190b] FAIL — librosa not installed")
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    audio, sr = librosa.load(args.wav, sr=None, mono=True)
    boundaries = boundaries_auto(audio, sr)
    findings = detect_onset_artifacts(audio, sr, boundaries)
    n_high = sum(1 for f in findings if f.severity == "HIGH")
    n_med = sum(1 for f in findings if f.severity == "MEDIUM")
    verdict = "PASS" if n_high == 0 else "FAIL"

    report = {
        "rule": "R190b onset_artifact",
        "wav": args.wav,
        "boundaries_count": len(boundaries),
        "n_high": n_high,
        "n_medium": n_med,
        "verdict": verdict,
        "findings": [asdict(f) for f in findings],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[R190b] {Path(args.wav).name}  boundaries={len(boundaries)}  HIGH={n_high}  MED={n_med}  verdict={verdict}")
        for f in findings[:20]:
            print(f"  {f.severity} @{f.boundary_ts_sec}s  {f.artifact_type}  metric={f.metric}")
    return 0 if n_high == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
