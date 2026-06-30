"""
extract_speaker_embedding.py — R181c support
Extract speaker embedding (192-dim) from WAV using lightweight MFCC summary
as Phase 2 placeholder. Phase 3 will swap to ECAPA-TDNN (wespeaker / pyannote).

Reason for placeholder: ECAPA-TDNN model download requires either wespeaker or
pyannote-audio + huggingface token + ~80MB weights. Phase 2 needs working
similarity check NOW. MFCC-summary embeddings are coarse but consistent
within same speaker/recording quality — sufficient for chunk-vs-golden detection
while ECAPA model integration follows in Phase 3 audit.

Usage:
    python tools/extract_speaker_embedding.py --wav assets/voice_refs/NARRATOR_golden.wav --output assets/voice_refs/NARRATOR_embedding.npy
    python tools/extract_speaker_embedding.py --sha256 --npy assets/voice_refs/NARRATOR_embedding.npy
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
import numpy as np

try:
    import librosa
except ImportError:
    librosa = None


def extract_placeholder_embedding(wav_path: Path, target_dim: int = 192) -> np.ndarray:
    """Return 192-dim deterministic embedding from MFCC + delta + delta2 summary.
    NOT a real speaker embedding — Phase 3 will replace with ECAPA-TDNN.
    """
    if librosa is None:
        raise RuntimeError("librosa required: pip install librosa")
    audio, sr = librosa.load(wav_path, sr=22050, mono=True)
    n_mfcc = 32
    mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)
    stats = []
    for matrix in (mfcc, delta, delta2):
        stats.append(np.mean(matrix, axis=1))
        stats.append(np.std(matrix, axis=1))
    emb = np.concatenate(stats).astype(np.float32)
    if emb.size < target_dim:
        emb = np.concatenate([emb, np.zeros(target_dim - emb.size, dtype=np.float32)])
    else:
        emb = emb[:target_dim]
    norm = np.linalg.norm(emb) + 1e-9
    return (emb / norm).astype(np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a = a / (np.linalg.norm(a) + 1e-9)
    b = b / (np.linalg.norm(b) + 1e-9)
    return float(np.dot(a, b))


def sha256_of_array(arr: np.ndarray) -> str:
    h = hashlib.sha256()
    h.update(arr.tobytes())
    return h.hexdigest()


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--wav", type=str)
    ap.add_argument("--output", type=str)
    ap.add_argument("--sha256", action="store_true")
    ap.add_argument("--npy", type=str)
    ap.add_argument("--compare", nargs=2, metavar=("A", "B"))
    args = ap.parse_args()

    if args.compare:
        a = np.load(args.compare[0])
        b = np.load(args.compare[1])
        sim = cosine_similarity(a, b)
        print(json.dumps({"cosine_similarity": round(sim, 4)}))
        return 0

    if args.sha256:
        if not args.npy:
            ap.error("--sha256 requires --npy PATH")
        arr = np.load(args.npy)
        print(sha256_of_array(arr))
        return 0

    if not args.wav:
        ap.error("--wav PATH required (or --sha256 --npy / --compare A B)")
    wav_path = Path(args.wav)
    if not wav_path.exists():
        print(f"[R181c] FAIL — missing {wav_path}")
        return 2

    emb = extract_placeholder_embedding(wav_path)
    if args.output:
        np.save(args.output, emb)
        sha = sha256_of_array(emb)
        print(f"[R181c] extracted {len(emb)}-dim -> {args.output}")
        print(f"[R181c] sha256: {sha}")
    else:
        print(json.dumps({"dim": len(emb), "norm": float(np.linalg.norm(emb)), "sha256": sha256_of_array(emb)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
