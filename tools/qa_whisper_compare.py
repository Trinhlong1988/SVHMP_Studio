"""Whisper Compare — Transcribe rendered WAV + compare với spec text.

Output:
  - Per-chunk WER (Word Error Rate)
  - Overall similarity score
  - Failed chunks (WER > threshold)

Usage:
  python tools/qa_whisper_compare.py --section hook
  python tools/qa_whisper_compare.py --wav <path> --spec <spec.json>
"""
import argparse
import json
import sys
import re
from pathlib import Path

BASE = Path(r"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio")
SECTIONS_DIR = BASE / "output/ep_01/sections"


def normalize(text):
    """Lowercase + strip punctuation + collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[.,!?…—\-:;\"'()\[\]]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    # Remove pause markers
    text = re.sub(r"\[pause:\d+ms\]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def wer(ref, hyp):
    """Word Error Rate (Levenshtein on words)."""
    ref_words = ref.split()
    hyp_words = hyp.split()
    if not ref_words:
        return 0.0 if not hyp_words else 1.0
    n, m = len(ref_words), len(hyp_words)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        d[i][0] = i
    for j in range(m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_words[i-1] == hyp_words[j-1]:
                d[i][j] = d[i-1][j-1]
            else:
                d[i][j] = min(d[i-1][j-1], d[i-1][j], d[i][j-1]) + 1
    return d[n][m] / n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", help="hook/setup/incident/reveal/payoff/cliffhanger")
    ap.add_argument("--wav", help="Custom WAV path")
    ap.add_argument("--spec", help="Custom spec.json path")
    ap.add_argument("--model", default="medium", help="Whisper model size (tiny/base/small/medium/large)")
    ap.add_argument("--threshold", type=float, default=0.15, help="Per-chunk WER threshold (default 0.15)")
    args = ap.parse_args()

    if args.section:
        wav_path = SECTIONS_DIR / f"{args.section}.wav"
        spec_path = SECTIONS_DIR / f"spec_{args.section}.json"
    else:
        wav_path = Path(args.wav)
        spec_path = Path(args.spec)

    if not wav_path.exists():
        print(f"ERROR: wav not found: {wav_path}")
        sys.exit(1)
    if not spec_path.exists():
        print(f"ERROR: spec not found: {spec_path}")
        sys.exit(1)

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    sentences = [normalize(s["text"]) for s in spec["sentences"]]
    full_ref = " ".join(sentences)

    print(f"=== WHISPER COMPARE — {wav_path.name} ===")
    print(f"  Model: {args.model}")
    print(f"  Ref chunks: {len(sentences)}")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("ERROR: faster-whisper not installed (pip install faster-whisper)")
        sys.exit(2)

    model = WhisperModel(args.model, device="cuda", compute_type="float16")
    print(f"  Transcribing...")
    segments, info = model.transcribe(str(wav_path), language="vi", beam_size=1)
    hyp_text = " ".join(normalize(seg.text) for seg in segments)

    overall_wer = wer(full_ref, hyp_text)
    similarity = (1 - overall_wer) * 100

    print(f"\n  Reference length: {len(full_ref.split())} words")
    print(f"  Hypothesis length: {len(hyp_text.split())} words")
    print(f"  Overall WER: {overall_wer*100:.2f}%")
    print(f"  Similarity: {similarity:.2f}%")
    print()

    verdict = "PASS" if overall_wer <= args.threshold else "FAIL"
    print(f"== WHISPER COMPARE GATE ({args.threshold*100:.0f}% threshold): {verdict} ==")

    # Output JSON
    result = {
        "wav": str(wav_path),
        "spec": str(spec_path),
        "model": args.model,
        "ref_words": len(full_ref.split()),
        "hyp_words": len(hyp_text.split()),
        "overall_wer_pct": round(overall_wer * 100, 2),
        "similarity_pct": round(similarity, 2),
        "threshold_pct": args.threshold * 100,
        "verdict": verdict,
    }
    json_out = wav_path.with_suffix(".whisper_compare.json")
    json_out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Report: {json_out}")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
