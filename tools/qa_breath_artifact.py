"""
qa_breath_artifact.py — R189 enforcement
Detect breath artifacts ("xì / phù / ẹ / hự") trong TTS output.

Method:
  - Detect high-energy sibilance bursts (5-10kHz) > N std vs baseline
  - Detect aspiration breaks (sudden energy spikes in 200-2000Hz)
  - Map back to text chunks via timestamps if provided
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

SIBILANCE_BAND_HZ = (5000, 10000)
ASPIRATION_BAND_HZ = (200, 2000)
SIBILANCE_BURST_Z = 3.0
ASPIRATION_BURST_Z = 3.5
MIN_BURST_MS = 30


@dataclass
class BreathArtifact:
    ts_sec: float
    artifact_type: str
    severity: str
    z_score: float
    duration_ms: int


def detect_breath_artifacts(audio: np.ndarray, sr: int) -> list[BreathArtifact]:
    out: list[BreathArtifact] = []
    hop = 512
    frame = 2048

    sib_filt = librosa.effects.preemphasis(audio)
    S_sib = np.abs(librosa.stft(sib_filt, n_fft=frame, hop_length=hop))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=frame)
    sib_mask = (freqs >= SIBILANCE_BAND_HZ[0]) & (freqs <= SIBILANCE_BAND_HZ[1])
    sib_energy = np.mean(S_sib[sib_mask] ** 2, axis=0)
    sib_db = 10 * np.log10(sib_energy + 1e-12)

    asp_mask = (freqs >= ASPIRATION_BAND_HZ[0]) & (freqs <= ASPIRATION_BAND_HZ[1])
    asp_energy = np.mean(S_sib[asp_mask] ** 2, axis=0)
    asp_db = 10 * np.log10(asp_energy + 1e-12)

    sib_mu, sib_std = float(np.mean(sib_db)), float(np.std(sib_db))
    asp_mu, asp_std = float(np.mean(asp_db)), float(np.std(asp_db))

    min_frames = max(1, int(MIN_BURST_MS / 1000.0 * sr / hop))

    def find_bursts(z_signal: np.ndarray, threshold: float, label: str, severity: str):
        mask = z_signal > threshold
        i = 0
        while i < len(mask):
            if mask[i]:
                j = i
                while j < len(mask) and mask[j]:
                    j += 1
                if j - i >= min_frames:
                    ts = i * hop / sr
                    dur = int((j - i) * hop / sr * 1000)
                    out.append(
                        BreathArtifact(
                            ts_sec=round(ts, 3),
                            artifact_type=label,
                            severity=severity,
                            z_score=round(float(np.max(z_signal[i:j])), 2),
                            duration_ms=dur,
                        )
                    )
                i = j
            else:
                i += 1

    if sib_std > 0:
        find_bursts((sib_db - sib_mu) / sib_std, SIBILANCE_BURST_Z, "breath_sibilance_xi", "HIGH")
    if asp_std > 0:
        find_bursts((asp_db - asp_mu) / asp_std, ASPIRATION_BURST_Z, "breath_aspiration_phu", "MEDIUM")

    return out


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if librosa is None:
        print("[R189] FAIL — librosa not installed")
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    audio, sr = librosa.load(args.wav, sr=None, mono=True)
    findings = detect_breath_artifacts(audio, sr)
    n_high = sum(1 for f in findings if f.severity == "HIGH")
    n_med = sum(1 for f in findings if f.severity == "MEDIUM")
    verdict = "PASS" if n_high == 0 else "FAIL"

    report = {
        "rule": "R189 breath_artifact",
        "wav": args.wav,
        "duration_sec": round(len(audio) / sr, 2),
        "n_high": n_high,
        "n_medium": n_med,
        "verdict": verdict,
        "findings": [asdict(f) for f in findings],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[R189] {Path(args.wav).name}  HIGH={n_high}  MED={n_med}  verdict={verdict}")
        for f in findings[:20]:
            print(f"  {f.severity} @{f.ts_sec}s  {f.artifact_type}  z={f.z_score}  {f.duration_ms}ms")
    return 0 if n_high == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
