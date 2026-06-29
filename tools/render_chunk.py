"""R146 — Per-chunk render tool (Minimal Edit principle).

Render CHỈ 1 chunk lỗi, KHÔNG re-render cả section. Splice into existing WAV.

Usage:
  python tools/render_chunk.py --section payoff --chunk_idx 5
  python tools/render_chunk.py --section reveal --chunk_idx 12

Workflow:
  1. Load spec_<section>.json
  2. Extract sentence at chunk_idx
  3. Render single chunk → temp.wav
  4. Run patch_audio_chunk.py to splice into <section>.wav

NOTE: cần PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python uv run env (IndexTTS2)
"""
import json
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path

BASE = Path(r"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio")
SECTIONS_DIR = BASE / "output/ep_01/sections"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--section", required=True, choices=["hook", "setup", "incident", "reveal", "payoff", "cliffhanger"])
    ap.add_argument("--chunk_idx", type=int, required=True)
    ap.add_argument("--output", help="Single chunk WAV output (default temp)")
    args = ap.parse_args()

    spec_file = SECTIONS_DIR / f"spec_{args.section}.json"
    spec = json.loads(spec_file.read_text(encoding="utf-8"))
    sentences = spec["sentences"]

    if args.chunk_idx < 0 or args.chunk_idx >= len(sentences):
        print(f"ERROR: chunk_idx {args.chunk_idx} out of range [0, {len(sentences)})")
        sys.exit(1)

    chunk = sentences[args.chunk_idx]
    print(f"=== RENDER CHUNK ===")
    print(f"  Section: {args.section}")
    print(f"  Chunk idx: {args.chunk_idx}")
    print(f"  Text: \"{chunk['text'][:100]}\"")
    print(f"  Pause after: {chunk.get('pause_ms', 1200)}ms")
    print()

    # Build single-chunk spec
    single_spec = {
        "sentences": [chunk],
        "sample_prompt": spec["sample_prompt"],
    }
    if "section_emo" in spec:
        single_spec["section_emo"] = spec["section_emo"]

    # Write temp spec
    temp_spec = Path(tempfile.gettempdir()) / f"svhmp_chunk_{args.section}_{args.chunk_idx}_spec.json"
    temp_spec.write_text(json.dumps(single_spec, ensure_ascii=False, indent=2), encoding="utf-8")

    # Output WAV
    out_wav = Path(args.output) if args.output else (Path(tempfile.gettempdir()) / f"svhmp_chunk_{args.section}_{args.chunk_idx}.wav")

    print(f"TO RENDER (UV venv):")
    print(f"  cd C:/Users/Administrator/index-tts")
    print(f"  uv run --no-sync python {BASE}/tools/svhmp_v13_render.py \\")
    print(f"    --spec \"{temp_spec}\" \\")
    print(f"    --output \"{out_wav}\"")
    print()
    print(f"AFTER render, splice via:")
    print(f"  python {BASE}/tools/patch_audio_chunk.py \\")
    print(f"    --section {args.section} --chunk_idx {args.chunk_idx} \\")
    print(f"    --new_wav \"{out_wav}\"")


if __name__ == "__main__":
    main()
