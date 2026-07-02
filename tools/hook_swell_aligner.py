"""Hook swell aligner — forced-align để tìm vowel center từ đầu tiên HOOK content.

Per bible/05 v1.1 R_AUDIO_08:
  - Peak music align với midpoint(word_start, word_end) của từ đầu tiên HOOK
  - Examples: Đêm/Mưa/Tháng/Cuối/Phố (any opening word per R49 variants)

Usage:
  python tools/hook_swell_aligner.py --tts output/ep_01/EP01_R38_FULL.wav

Output: output/ep_NN/hook_align.json
  {
    "first_word": "Đêm",
    "start_ms": 120,
    "end_ms": 540,
    "center_ms": 330,
    "paragraph_1_end_ms": 8200
  }
"""
import sys, json, argparse
from pathlib import Path
from faster_whisper import WhisperModel

BASE = Path(__file__).resolve().parents[1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tts', type=Path, required=True, help='TTS narration WAV (no intro prepended)')
    ap.add_argument('--output', type=Path, default=None)
    ap.add_argument('--model', default='medium', help='whisper model: tiny/base/small/medium/large')
    ap.add_argument('--max-scan-s', type=float, default=30.0, help='only scan first N seconds')
    args = ap.parse_args()

    if not args.tts.exists():
        print(f'TTS not found: {args.tts}'); sys.exit(1)

    print(f'[ALIGN] Loading whisper {args.model}...')
    try:
        model = WhisperModel(args.model, device='cuda', compute_type='float16')
    except RuntimeError as e:
        print(f'  CUDA load FAIL ({e}). Fallback CPU int8...')
        model = WhisperModel(args.model, device='cpu', compute_type='int8')

    print(f'[ALIGN] Transcribing {args.tts.name} (word_timestamps, lang=vi)...')
    segments, info = model.transcribe(
        str(args.tts), language='vi', word_timestamps=True,
        beam_size=5, vad_filter=False,
    )

    first_word = None
    first_start_ms = None
    first_end_ms = None
    paragraph_1_end_ms = None
    para_end_keywords = []  # detect paragraph break via long silence (>1.5s) between words
    last_word_end = 0.0

    for seg in segments:
        if seg.start > args.max_scan_s and first_word: break
        for w in (seg.words or []):
            txt = (w.word or '').strip()
            if not txt: continue
            # Skip leading silence / punctuation-only
            if first_word is None and any(c.isalpha() for c in txt):
                first_word = txt.lstrip()
                first_start_ms = int(w.start * 1000)
                first_end_ms = int(w.end * 1000)
                print(f'  FIRST WORD: "{first_word}" @ {first_start_ms}-{first_end_ms} ms (center={(first_start_ms+first_end_ms)//2}ms)')
            # Detect paragraph break: silence > 1.5s before this word
            elif first_word and (w.start - last_word_end) > 1.5 and paragraph_1_end_ms is None:
                paragraph_1_end_ms = int(last_word_end * 1000)
                print(f'  PARAGRAPH 1 END: {paragraph_1_end_ms} ms (silence {w.start - last_word_end:.2f}s before next word)')
            last_word_end = w.end
        if paragraph_1_end_ms: break

    if first_word is None:
        print('FAIL: no word detected in first 30s')
        sys.exit(2)

    if paragraph_1_end_ms is None:
        # No paragraph break found — use end of first sentence/segment
        # Fallback: 8s after first word
        paragraph_1_end_ms = first_end_ms + 8000
        print(f'  PARAGRAPH 1 END (fallback): {paragraph_1_end_ms} ms (no >1.5s silence found)')

    center_ms = (first_start_ms + first_end_ms) // 2

    result = {
        'tts_file': str(args.tts),
        'first_word': first_word,
        'start_ms': first_start_ms,
        'end_ms': first_end_ms,
        'center_ms': center_ms,
        'paragraph_1_end_ms': paragraph_1_end_ms,
        'whisper_model': args.model,
        'note': 'For R_AUDIO_08: HOOK crescendo peak should hit at center_ms (after intro 4.5s prepend = absolute peak_ms = 4500 + center_ms)',
    }

    out = args.output or args.tts.parent / 'hook_align.json'
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'\n[OUTPUT] {out}')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
