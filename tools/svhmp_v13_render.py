"""
SVHMP EP01 v13 — 5-trụ production (round 14 hook added)
1. Micro-chunk (≤200, đã ≤131)
2. Voice anchor "Khánh An kể chậm rãi rằng," → strip sau render
3. Setting tuyệt đối: seed=42, temp=0.3, top_k=5, top_p=0.5, num_beams=5
4. Post-process: fade 40ms, loudnorm -18 LUFS
5. Room tone bridge -38dB 200ms giữa chunks
"""
import os, sys, json, time, subprocess, random, argparse, re, atexit
import numpy as np
import soundfile as sf
import torch

sys.path.insert(0, r'C:\Users\Administrator\index-tts')
# Round 14: dashboard live render hook
_TOOLS = os.path.dirname(os.path.abspath(__file__))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)
try:
    from render_progress_hook import RenderProgress
except ImportError:
    class RenderProgress:  # no-op fallback nếu hook missing
        def __init__(self, **kw): pass
        def start(self, *a, **k): pass
        def tick(self, *a, **k): pass
        def done(self, *a, **k): pass
        def fail(self, *a, **k): pass

USE_ANCHOR = False  # v13b: skip anchor (silence strip unreliable)
ANCHOR = "Khánh An kể chậm rãi rằng,"
ANCHOR_STRIP_MIN_SEC = 2.5
ANCHOR_STRIP_MAX_SEC = 4.5
SILENCE_THRESHOLD_DB = -40
MIN_SILENCE_MS = 150
FADE_TAIL_MS = 80  # REVERT s3 baseline OK config (Mr.Long 26/6: tuân thủ ngay sau s3 v13e)
BRIDGE_MS_DEFAULT = 600  # was 200 cố định bug 25/6 — dùng pause_after_ms từ spec
ROOM_TONE_DB = -50  # ignore — bridge = silence pure (Mr.Long 26/6)
LOUDNESS_TARGET = -18
TAIL_TRIM_DB = -20  # -25→-20dB (Mr.Long 26/6: "buồn dài" trailing vowel BigVGAN phù 2s)

GEN_KWARGS = {
    "do_sample": True,
    "top_p": 0.5,
    "top_k": 5,
    "temperature": 0.3,
    "length_penalty": 1.0,
    "num_beams": 5,
    "repetition_penalty": 10.0,
    "max_mel_tokens": 1500,
}


def set_all_seeds(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def detect_anchor_end(data, sr):
    """Find end of anchor section by detecting first long silence in [2.5s, 4.5s] window."""
    win_start = int(ANCHOR_STRIP_MIN_SEC * sr)
    win_end = min(int(ANCHOR_STRIP_MAX_SEC * sr), len(data))
    if win_end <= win_start:
        return int(ANCHOR_STRIP_MIN_SEC * sr)

    thr = 10 ** (SILENCE_THRESHOLD_DB / 20)
    abs_data = np.abs(data[win_start:win_end])
    silence_mask = abs_data < thr

    min_samples = int(MIN_SILENCE_MS * sr / 1000)
    in_run = False
    run_start = 0
    for i, s in enumerate(silence_mask):
        if s and not in_run:
            in_run = True
            run_start = i
        elif not s and in_run:
            run_length = i - run_start
            if run_length >= min_samples:
                return win_start + i
            in_run = False
    return win_start


def fade_tail(data, sr, ms=FADE_TAIL_MS):
    samples = int(ms * sr / 1000)
    if samples <= 0 or samples >= len(data):
        return data
    fade = np.linspace(1.0, 0.0, samples, dtype=np.float32)
    data[-samples:] *= fade
    return data


def fade_head(data, sr, ms=FADE_TAIL_MS):
    samples = int(ms * sr / 1000)
    if samples <= 0 or samples >= len(data):
        return data
    fade = np.linspace(0.0, 1.0, samples, dtype=np.float32)
    data[:samples] *= fade
    return data


def make_room_tone(duration_ms, sr, target_db=ROOM_TONE_DB):
    n = int(duration_ms * sr / 1000)
    return np.zeros(n, dtype=np.float32)  # bridge = pure silence (Mr.Long 26/6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    spec = json.load(open(args.spec, encoding='utf-8'))
    sentences = spec['sentences']
    sample = spec['sample_prompt']

    # Round 14 hook: detect ep from output path "output/ep_NN/narration.wav"
    ep_match = re.search(r'ep_(\d+)', args.output)
    ep_num = int(ep_match.group(1)) if ep_match else 0
    # Total steps: 1 init + N chunks + 1 concat + 1 loudnorm
    _prog = RenderProgress(cmd='v13_render', ep=ep_num, total_steps=len(sentences) + 3)
    # Cleanup on unexpected exit (crash/Ctrl+C): mark active=False
    atexit.register(lambda: _prog.fail('exited without done()') if hasattr(_prog, 'current_step') and _prog.current_step < _prog.total_steps else None)
    _prog.start('init')

    print(f"[v13] Loading IndexTTS2...", flush=True)
    t0 = time.time()
    _prog.tick(1, 'Loading IndexTTS2 model')
    from indextts.infer_v2 import IndexTTS2
    tts = IndexTTS2(model_dir=r"C:\Users\Administrator\index-tts\checkpoints-vi", use_fp16=True)
    print(f"[v13] Init done [{time.time()-t0:.1f}s]", flush=True)
    _prog.tick(1, f'Model loaded ({time.time()-t0:.1f}s)')

    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="svhmp_v13_")
    print(f"[v13] tmpdir: {tmpdir}", flush=True)

    _prog.start('tts')
    stripped_chunks = []
    sr_main = None
    for i, sent in enumerate(sentences):
        text = sent['text']
        emo = sent.get('emo_vector', [0.0] * 8)
        tempo = sent.get('tempo_factor', 1.0)
        rendered_text = f"{ANCHOR} {text}" if USE_ANCHOR else text
        out_path = os.path.join(tmpdir, f"seg_{i:03d}.wav")

        set_all_seeds(42)
        print(f"[v13] Chunk {i+1}/{len(sentences)}: {text[:50]}...", flush=True)
        _prog.tick(1 + i + 1, f'TTS chunk {i+1}/{len(sentences)}: {text[:40]}...')
        t0 = time.time()
        tts.infer(
            spk_audio_prompt=sample,
            text=rendered_text,
            output_path=out_path,
            emo_vector=emo,
            emo_alpha=0.65,
            interval_silence=200,
            max_text_tokens_per_segment=400,
            verbose=False,
            **GEN_KWARGS,
        )
        print(f"   render [{time.time()-t0:.1f}s]", flush=True)

        # Apply tempo if needed
        if tempo != 1.0:
            tmp_t = out_path + '.t.wav'
            subprocess.run([
                "ffmpeg", "-y", "-i", out_path,
                "-af", f"atempo={tempo}",
                "-c:a", "pcm_s16le", tmp_t,
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            os.replace(tmp_t, out_path)

        # Read + (optional anchor strip) + fade
        data, sr = sf.read(out_path, always_2d=False)
        data = data.astype(np.float32)
        if sr_main is None:
            sr_main = sr
        if USE_ANCHOR:
            anchor_end = detect_anchor_end(data, sr)
            stripped = data[anchor_end:].copy()
        else:
            # Skip anchor → trim leading silence -36dB only
            thr_h = 10 ** (-36 / 20)
            abs_h = np.abs(data)
            first = int(np.argmax(abs_h > thr_h)) if (abs_h > thr_h).any() else 0
            stripped = data[first:].copy()
        # Trim trailing silence — AGGRESSIVE -25dB (was -30) chống "phù" BigVGAN tail noise
        thr_tail = 10 ** (TAIL_TRIM_DB / 20)
        abs_t = np.abs(stripped)
        if abs_t.any():
            last_above = len(stripped) - int(np.argmax(abs_t[::-1] > thr_tail))
            stripped = stripped[:last_above]
        # Fade head + tail
        stripped = fade_head(stripped, sr)
        stripped = fade_tail(stripped, sr)
        print(f"   → {len(stripped)/sr:.2f}s", flush=True)
        chunk_pause = sent.get('pause_after_ms', BRIDGE_MS_DEFAULT)
        stripped_chunks.append((stripped, chunk_pause))

    # Concat with VARIABLE room tone bridge (pause_after_ms từ spec)
    _prog.start('concat')
    _prog.tick(1 + len(sentences) + 1, f'Concat {len(stripped_chunks)} chunks')
    print(f"[v13] Concat {len(stripped_chunks)} chunks with variable bridge (default {BRIDGE_MS_DEFAULT}ms)...", flush=True)
    parts = []
    for i, (chunk, pause_ms) in enumerate(stripped_chunks):
        parts.append(chunk)
        if i < len(stripped_chunks) - 1:
            bridge = make_room_tone(pause_ms, sr_main)
            parts.append(bridge)
            print(f"   bridge ch{i+1}→ch{i+2}: {pause_ms}ms", flush=True)
    merged = np.concatenate(parts)
    raw_out = args.output + '.raw.wav'
    sf.write(raw_out, merged, sr_main)
    print(f"[v13] Raw {len(merged)/sr_main:.2f}s @ {sr_main}Hz → {raw_out}", flush=True)

    # Loudnorm -18 LUFS + FORCE SR 22050 (NO compressor → giữ giọng natural không khàn)
    _prog.start('loudnorm')
    _prog.tick(1 + len(sentences) + 2, f'Loudnorm -18 LUFS + SR 22050')
    print(f"[v13] Loudnorm + force SR 22050 (no compressor)...", flush=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", raw_out,
        "-af", f"loudnorm=I={LOUDNESS_TARGET}:LRA=11:TP=-1.5",
        "-ar", "22050",  # FORCE SR same as input chống loudnorm 192kHz upsample click
        "-c:a", "pcm_s16le", args.output,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[v13] DONE → {args.output}", flush=True)
    _prog.done(success=True, final_path=args.output)


if __name__ == '__main__':
    main()
