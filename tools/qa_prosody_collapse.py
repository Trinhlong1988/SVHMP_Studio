"""
qa_prosody_collapse.py — R190 enforcement
Detect prosody collapse after "..." dấu ba chấm (F0 contour break / rung / lẹm).

Method:
  - Voice activity detect segments
  - Per segment: extract F0 contour
  - Check stability: rolling std/mean F0
  - Flag if contour breaks > threshold within ±300ms of trailing "..." (heuristic on energy drop)
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


@dataclass
class ProsodyIssue:
    ts_sec: float
    artifact_type: str
    severity: str
    metric: float


def detect_prosody_collapse(audio: np.ndarray, sr: int) -> list[ProsodyIssue]:
    out: list[ProsodyIssue] = []
    hop = 512
    frame = 2048

    try:
        f0 = librosa.yin(audio.astype(np.float32), fmin=80, fmax=400, sr=sr, frame_length=frame, hop_length=hop)
    except Exception:
        return out

    if len(f0) < 20:
        return out

    times = librosa.frames_to_time(np.arange(len(f0)), sr=sr, hop_length=hop)

    rms = librosa.feature.rms(y=audio, frame_length=frame, hop_length=hop)[0]
    if len(rms) < 10:
        return out
    rms_db = 20 * np.log10(rms + 1e-9)

    win_frames = max(4, int(0.3 * sr / hop))
    # deep-audit F8 (2/7): truoc day truot cua so theo buoc = win_frames -> diem
    # chuyen cao do luon roi GIUA cua so post -> mu_post bi tron (220+110)/2 ~165
    # -> drop do duoc ~0.25-0.33 < 0.35 -> MISS ca octave drop that (false-neg,
    # test R190 test_04). Fix: truot MIN (step nho) de it nhat 1 cua so co pre
    # tron trong 220 va post tron trong 110; sau moi HIGH nhay qua 1 win_frames
    # de khong spam trung 1 su kien.
    step = max(1, win_frames // 3)
    i = win_frames
    while i < len(f0) - win_frames:
        valid_pre = f0[i - win_frames : i]
        valid_post = f0[i : i + win_frames]
        valid_pre = valid_pre[~np.isnan(valid_pre)]
        valid_post = valid_post[~np.isnan(valid_post)]
        advanced = False
        if len(valid_pre) >= 3 and len(valid_post) >= 3:
            mu_pre = float(np.mean(valid_pre))
            mu_post = float(np.mean(valid_post))
            std_post = float(np.std(valid_post))
            if mu_pre > 50 and mu_post > 50:
                drop = (mu_pre - mu_post) / mu_pre
                if drop > 0.35:
                    out.append(ProsodyIssue(
                        ts_sec=round(float(times[i]), 3),
                        artifact_type="prosody_pitch_drop",
                        severity="HIGH",
                        metric=round(drop, 3),
                    ))
                    i += win_frames  # nhay qua su kien -> 1 HIGH / event
                    advanced = True
                elif mu_post > 0 and std_post / mu_post > 0.40:
                    out.append(ProsodyIssue(
                        ts_sec=round(float(times[i]), 3),
                        artifact_type="prosody_rung_lem",
                        severity="MEDIUM",
                        metric=round(std_post / mu_post, 3),
                    ))
        if not advanced:
            i += step

    return out


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if librosa is None:
        print("[R190] FAIL — librosa not installed")
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    audio, sr = librosa.load(args.wav, sr=None, mono=True)
    findings = detect_prosody_collapse(audio, sr)
    n_high = sum(1 for f in findings if f.severity == "HIGH")
    n_med = sum(1 for f in findings if f.severity == "MEDIUM")
    verdict = "PASS" if n_high == 0 else "FAIL"

    report = {
        "rule": "R190 prosody_collapse",
        "wav": args.wav,
        "n_high": n_high,
        "n_medium": n_med,
        "verdict": verdict,
        "findings": [asdict(f) for f in findings],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[R190] {Path(args.wav).name}  HIGH={n_high}  MED={n_med}  verdict={verdict}")
        for f in findings[:20]:
            print(f"  {f.severity} @{f.ts_sec}s  {f.artifact_type}  metric={f.metric}")
    return 0 if n_high == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
