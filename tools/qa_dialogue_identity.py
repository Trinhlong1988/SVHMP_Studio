"""
qa_dialogue_identity.py — R191 enforcement
Per-dialogue speaker embedding match: KP must remain KP, DRIVER must remain DRIVER.

Phase 2 placeholder uses MFCC-summary embedding (extract_speaker_embedding.py).
Phase 3 will swap to ECAPA-TDNN per Mr.Long docx 30/6.

Workflow:
  - Load section WAV
  - Detect VAD segments (assume each non-silence segment = 1 dialogue/narration chunk)
  - Extract embedding per segment
  - Compare cross-segment within same speaker label (heuristic: assume all
    segments are NARRATOR unless explicit dialogue markers detected in spec)
  - Flag if any segment cosine sim < threshold vs section centroid
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

SEGMENT_MIN_MS = 500
COSINE_THRESHOLD = 0.85


@dataclass
class IdentityIssue:
    segment_start_sec: float
    segment_end_sec: float
    cosine_sim: float
    severity: str
    note: str


def mfcc_embedding(seg: np.ndarray, sr: int, target_dim: int = 192) -> np.ndarray:
    n_mfcc = 32
    mfcc = librosa.feature.mfcc(y=seg, sr=sr, n_mfcc=n_mfcc)
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)
    stats = []
    for m in (mfcc, delta, delta2):
        stats.append(np.mean(m, axis=1))
        stats.append(np.std(m, axis=1))
    emb = np.concatenate(stats).astype(np.float32)
    if emb.size < target_dim:
        emb = np.concatenate([emb, np.zeros(target_dim - emb.size, dtype=np.float32)])
    else:
        emb = emb[:target_dim]
    norm = np.linalg.norm(emb) + 1e-9
    return (emb / norm).astype(np.float32)


def detect_segments(audio: np.ndarray, sr: int, min_ms: int = SEGMENT_MIN_MS) -> list[tuple[int, int]]:
    rms = librosa.feature.rms(y=audio, frame_length=2048, hop_length=512)[0]
    hop = 512
    silence_thresh = np.percentile(rms, 30) * 0.6
    in_seg = False
    seg_start = 0
    segments = []
    min_frames = int(min_ms / 1000.0 * sr / hop)
    for i, r in enumerate(rms):
        if r > silence_thresh and not in_seg:
            seg_start = i
            in_seg = True
        elif r <= silence_thresh and in_seg:
            if i - seg_start >= min_frames:
                segments.append((seg_start * hop, i * hop))
            in_seg = False
    if in_seg:
        segments.append((seg_start * hop, len(audio)))
    return segments


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    if librosa is None:
        print("[R191] FAIL — librosa not installed")
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", required=True)
    ap.add_argument("--threshold", type=float, default=COSINE_THRESHOLD)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    audio, sr = librosa.load(args.wav, sr=22050, mono=True)
    segments = detect_segments(audio, sr)
    if len(segments) < 2:
        print(f"[R191] {Path(args.wav).name}  segments={len(segments)}  verdict=SKIP (need >= 2 segments)")
        return 0

    embeddings = []
    for s, e in segments:
        seg = audio[s:e]
        if len(seg) < 512:
            continue
        try:
            embeddings.append((s / sr, e / sr, mfcc_embedding(seg, sr)))
        except Exception:
            continue
    if len(embeddings) < 2:
        print(f"[R191] {Path(args.wav).name}  usable_segments={len(embeddings)}  verdict=SKIP")
        return 0

    matrix = np.stack([e for _, _, e in embeddings])
    centroid = np.mean(matrix, axis=0)
    centroid /= np.linalg.norm(centroid) + 1e-9

    findings: list[IdentityIssue] = []
    for ts0, ts1, emb in embeddings:
        sim = float(np.dot(emb, centroid))
        if sim < args.threshold:
            findings.append(IdentityIssue(
                segment_start_sec=round(ts0, 3),
                segment_end_sec=round(ts1, 3),
                cosine_sim=round(sim, 4),
                severity="HIGH" if sim < args.threshold * 0.95 else "MEDIUM",
                note=f"cosine {sim:.3f} < threshold {args.threshold}",
            ))

    n_high = sum(1 for f in findings if f.severity == "HIGH")
    verdict = "PASS" if n_high == 0 else "FAIL"
    report = {
        "rule": "R191 dialogue_identity",
        "wav": args.wav,
        "segments": len(embeddings),
        "threshold": args.threshold,
        "n_high": n_high,
        "verdict": verdict,
        "findings": [asdict(f) for f in findings],
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"[R191] {Path(args.wav).name}  segments={len(embeddings)}  HIGH={n_high}  verdict={verdict}")
        for f in findings[:20]:
            print(f"  {f.severity} {f.segment_start_sec}-{f.segment_end_sec}s  sim={f.cosine_sim}")
    return 0 if n_high == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
