"""SVHMP — Voice cosine similarity cross-EP audit (Agent 3 production risk #1).

Detect voice drift across rendered audio EPs.
Compute cosine similarity between voice embeddings (anchor segment first 5s each EP).
Threshold ≥0.85 = OK | <0.85 = DRIFT WARN.

Requires:
- output/ep_N/narration.wav exist
- speechbrain ECAPA-TDNN or resemblyzer for embedding

This is a SCAFFOLD — actual embedding model load happens on first run.
"""
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
SVHMP = Path(r'D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio')

THRESHOLD = 0.85

def get_voice_embedding(wav_path):
    """Extract voice embedding from first 5s of audio.

    Implementation options:
    1. resemblyzer (Lightweight, no GPU needed)
       pip install resemblyzer
    2. speechbrain ECAPA-TDNN (More accurate, needs GPU)
       pip install speechbrain
    """
    try:
        from resemblyzer import VoiceEncoder, preprocess_wav
        encoder = VoiceEncoder()
        wav = preprocess_wav(str(wav_path))
        # Take first 5s only
        wav_5s = wav[:5 * 16000] if len(wav) > 5 * 16000 else wav
        return encoder.embed_utterance(wav_5s)
    except ImportError:
        return None  # Library not installed

def cosine_similarity(a, b):
    import numpy as np
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def main():
    print("=" * 70)
    print("VOICE COSINE SIMILARITY — Cross-EP drift detection (Agent 3 risk #1)")
    print(f"Threshold: ≥{THRESHOLD} = OK | <{THRESHOLD} = DRIFT WARN")
    print("=" * 70)

    embeddings = {}
    skipped_no_audio = []

    for n in range(1, 51):
        wav = SVHMP / 'output' / f'ep_{n:02d}' / 'narration.wav'
        if not wav.exists():
            skipped_no_audio.append(n)
            continue
        emb = get_voice_embedding(wav)
        if emb is None:
            print("\n⚠️ resemblyzer not installed. Install: pip install resemblyzer")
            print("Then re-run this script.")
            return
        embeddings[n] = emb

    if not embeddings:
        print(f"\n⚠️ No narration.wav rendered yet for EP01-50.")
        print(f"  Skipped (no audio): {len(skipped_no_audio)} EPs")
        print(f"  This audit is for POST-RENDER use.")
        print(f"  Re-run after TTS render EP01-50.")
        return

    # Compute pairwise similarity from EP01 baseline
    baseline = embeddings.get(1) or list(embeddings.values())[0]
    drift_warns = []
    print(f"\nVoice similarity vs EP01 baseline:")
    for n, emb in sorted(embeddings.items()):
        sim = cosine_similarity(baseline, emb)
        status = '✅' if sim >= THRESHOLD else '⚠️ DRIFT'
        print(f"  EP{n:02d}: {sim:.3f} {status}")
        if sim < THRESHOLD:
            drift_warns.append((n, sim))

    print(f"\n=== SUMMARY ===")
    print(f"  EPs measured: {len(embeddings)}")
    print(f"  Drift warns: {len(drift_warns)}")
    if drift_warns:
        print(f"  Action: Re-render EPs with drift, lock TTS anchor + seed=42")

    out = SVHMP / 'runtime' / 'audit_voice_cosine.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        'threshold': THRESHOLD,
        'eps_measured': len(embeddings),
        'drift_warns': drift_warns,
        'skipped_no_audio': skipped_no_audio,
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nReport: {out}")

if __name__ == '__main__':
    main()
