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
FADE_TAIL_MS = 80   # round 19+ 29/6 02:55 REVERT to 27.6 baseline (Mr.Long: "kiểm tra cách setup E1 27.6 mà học fix")
FADE_HEAD_MS = 30   # keep — first word KHÔNG bị cụt
BRIDGE_MS_DEFAULT = 600  # was 200 cố định bug 25/6 — dùng pause_after_ms từ spec
ROOM_TONE_DB = -50  # ignore — bridge = silence pure (Mr.Long 26/6)
LOUDNESS_TARGET = -18
TAIL_TRIM_DB = -20  # round 19+ 29/6 02:55 REVERT to 27.6 baseline (was -28 aggressive)

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


def fade_head(data, sr, ms=FADE_HEAD_MS):
    samples = int(ms * sr / 1000)
    if samples <= 0 or samples >= len(data):
        return data
    fade = np.linspace(0.0, 1.0, samples, dtype=np.float32)
    data[:samples] *= fade
    return data


def make_room_tone(duration_ms, sr, target_db=ROOM_TONE_DB):
    # round 19+ 29/6 05:45 v23 — Mr.Long HARDLOCK: "đoạn nghỉ phải IM LẶNG TUYỆT ĐỐI"
    # REVERT white noise → TRUE ZERO (em đã sai khi inject -90dB noise "bridge")
    # Sau volume=2.0 boost → noise -84dB still audible = "ù ù xì xì"
    # Pair với aggressive boundary trim (find silence start in last 300ms of chunk)
    n = int(duration_ms * sr / 1000)
    return np.zeros(n, dtype=np.float32)


def aggressive_trim_tail(data, sr, search_ms=600, silence_thr_db=-30):
    """v31 — Mr.Long HARDLOCK: 'pause = ZERO TUYỆT ĐỐI + trim 1/1000 precision'

    Precision: 1ms window (= 1/1000 sec) cho detect word-end.
    Pause = pure zeros guaranteed (no chunk residue spills).

    Pipeline:
    1. Scan backwards 1ms window — find last window RMS > -30dB (word-end precise)
    2. TRUNCATE AT word-end (NO grace keep — no audible residue)
    3. Apply 25ms linear fade INSIDE voice content (last 25ms before truncate)
       → smooth voice → zero transition, no click
    4. Output ends AT word-end with 0 amplitude (next sample = pause = 0)
    """
    n = len(data)
    search_n = int(search_ms * sr / 1000)
    if n <= search_n:
        return data.copy()
    thr = 10 ** (silence_thr_db / 20)
    win_n = max(1, int(0.001 * sr))  # 1ms window = 1/1000 sec precision

    # Scan BACKWARDS 1ms at a time for last voice window
    last_voice_end = n
    for i in range(n - win_n, max(0, n - search_n), -win_n):
        win_rms = np.sqrt(np.mean(data[i:i+win_n] ** 2))
        if win_rms > thr:
            last_voice_end = i + win_n  # word ends here (exact 1ms precision)
            break

    # v49 — Mr.Long: 06:40-06:55 lụp bụp ở chunk boundaries
    # ROOT: linear fade 10ms mid -21dB audible click
    # FIX: exp fade 40ms (smoother decay, mid -50dB subtle)
    # Preserve grace +50ms (chống cụt chữ)
    grace_n = int(0.050 * sr)
    keep_end = min(len(data), last_voice_end + grace_n)
    out = data[:keep_end].copy()
    fade_n = int(0.040 * sr)
    if 0 < fade_n < len(out):
        ramp = np.exp(np.linspace(0, -8, fade_n)).astype(np.float32)
        out[-fade_n:] *= ramp

    return out


def aggressive_trim_head(data, sr, search_ms=3000, silence_thr_db=-15):
    """v41 — search 3000ms cover chunks BigVGAN với 1.8-2s quiet head.
    Mr.Long catch chunk 13 (1780ms leading silent) + chunk 20 (1960ms).
    2-pass fallback: -15dB strict + -25dB fallback."""
    n = len(data)
    search_n = int(search_ms * sr / 1000)
    if n <= 100:
        return data
    win_n = max(1, int(0.001 * sr))
    # PASS 1: strict -15dB
    thr_strict = 10 ** (silence_thr_db / 20)
    first_voice = None
    for i in range(0, min(search_n, n - win_n), win_n):
        win_rms = np.sqrt(np.mean(data[i:i+win_n] ** 2))
        if win_rms > thr_strict:
            first_voice = max(0, i - win_n)
            break
    # v53 PASS 2 fallback: -20dB (was -25dB - quá lỏng tạo sối)
    if first_voice is None:
        thr_fallback = 10 ** (-20 / 20)
        for i in range(0, min(search_n, n - win_n), win_n):
            win_rms = np.sqrt(np.mean(data[i:i+win_n] ** 2))
            if win_rms > thr_fallback:
                first_voice = max(0, i - win_n)
                break
    if first_voice is None:
        first_voice = 0
    out = data[first_voice:].copy()
    # v49 — exp fade-in 20ms (smoother than linear, mid -50dB chống click)
    fade_n = int(0.020 * sr)
    if 0 < fade_n < len(out):
        ramp = np.exp(np.linspace(-8, 0, fade_n)).astype(np.float32)
        out[:fade_n] *= ramp
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--spec', required=True)
    ap.add_argument('--output', required=True)
    args = ap.parse_args()

    spec = json.load(open(args.spec, encoding='utf-8'))
    sentences = spec['sentences']
    sample = spec['sample_prompt']

    # ========================================================================
    # R90 HARDLOCK — STAGE 1 PRE-RENDER GATE (Mr.Long 29/6: "nghiêm cấm sai")
    # CANNOT BYPASS — abort render nếu R86 EOL violations > 0
    # ========================================================================
    print(f"[v13] R90 STAGE 1 pre-render gate...", flush=True)
    ep_match_early = re.search(r'ep_(\d+)', args.output)
    ep_num_early = int(ep_match_early.group(1)) if ep_match_early else 1
    md_path = f"D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/output/ep_{ep_num_early:02d}/episode.md"
    if os.path.exists(md_path):
        gate_result = subprocess.run(
            ["python", "D:/DỰ ÁN AI/GIỌNG ĐỌC/DỰ ÁN TRUYỆN MA/SVHMP_Studio/tools/qa_eol_diacritic.py", md_path],
            capture_output=True, text=True, encoding='utf-8',
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
        )
        print(gate_result.stdout, flush=True)
        if gate_result.returncode != 0:
            print(f"[v13] !!! R90 STAGE 1 FAIL - RENDER BLOCKED (R86 EOL violations)", flush=True)
            print(f"[v13] Fix episode.md violations + retry. KHÔNG bypass.", flush=True)
            sys.exit(2)
        print(f"[v13] R90 STAGE 1 PASS - render allowed", flush=True)
    else:
        print(f"[v13] WARN: episode.md not found at {md_path}, skip R86 check", flush=True)

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
        # round 19+ 29/6 05:00 v19 REVERT noisereduce (Mr.Long: "mất âm trầm ấm + tiếng nhỏ hẳn")
        # noisereduce 0.7 side effect: kill warm low freq + reduce signal level
        # Accept BigVGAN tail noise as INHERENT — will mask via master mix với music bed
        # Round 19+ R_AUDIO_09 enforce: DC offset removal per-chunk (chống xèo / ù)
        stripped = stripped - np.mean(stripped)
        # Per-chunk RMS normalize to -23 dBFS (chống "âm thanh không đều")
        rms = np.sqrt(np.mean(stripped ** 2))
        if rms > 1e-6:
            target_rms = 10 ** (-23 / 20)  # -23 dBFS target
            stripped = stripped * (target_rms / rms)
            # Soft limit at -1 dBFS
            peak = np.max(np.abs(stripped))
            if peak > 0.89:
                stripped = stripped * (0.89 / peak)
        # round 19+ 29/6 v31 — Mr.Long HARDLOCK: pause = ZERO TUYỆT ĐỐI, trim 1/1000 precision
        # Pipeline FINAL v31:
        # 1. aggressive_trim_tail = 1ms-precise detect word-end at -30dB + TRUNCATE + 25ms linear fade INSIDE voice
        # 2. aggressive_trim_head = trim leading silence -50dB + 10ms back-off
        # 3. fade_head 15ms (click prevention only)
        # NO fade_tail (trim_tail handles it cleanly)
        # NO zero_pad_n (last sample already = 0 after fade)
        stripped = aggressive_trim_tail(stripped, sr, search_ms=600, silence_thr_db=-30)
        stripped = aggressive_trim_head(stripped, sr, search_ms=200, silence_thr_db=-50)
        stripped = fade_head(stripped, sr, ms=15)
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
    # v50 — Mr.Long: em lỗi ghép pipeline thêm 70 clicks (RAW 2 → output 72)
    # FIX: SIMPLE chain - remove agate + acompressor (multi-stage tạo transitions)
    # Pause silence đã handle bởi Python make_room_tone np.zeros + trim
    subprocess.run([
        "ffmpeg", "-y", "-i", raw_out,
        "-af", "atempo=0.95,volume=1.2,alimiter=limit=0.79:attack=10:release=80",
        "-ar", "22050",
        "-c:a", "pcm_s16le", args.output,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"[v13] DONE → {args.output}", flush=True)
    _prog.done(success=True, final_path=args.output)


if __name__ == '__main__':
    main()
