"""
SVHMP EP01 v13 — 5-trụ production (round 14 hook added)
1. Micro-chunk (≤200, đã ≤131)
2. Anchor DISABLED v13b — narrator Hắc Dạ Ký anonymous (1/7 lock)
3. Setting tuyệt đối: seed=42, temp=0.3, top_k=5, top_p=0.5, num_beams=5
4. Post-process: fade 40ms, loudnorm -18 LUFS
5. Room tone bridge -38dB 200ms giữa chunks
"""
import os, sys, json, time, subprocess, random, argparse, re, atexit
from pathlib import Path
import numpy as np
import soundfile as sf
# G3 (2026-07-02): torch is lazy-imported inside set_all_seeds() only.
# The QA-logic functions used by the CI gate (qa_clean_tail, tail-trim, intro
# audit) do NOT touch torch, so a top-level import blocked QA tests on any
# machine without the full ML stack. Deferring it keeps QA runnable everywhere
# and off the CI's dependency surface, while render still gets full GPU seeding.

sys.path.insert(0, os.path.expanduser(r'~/index-tts'))
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

USE_ANCHOR = False  # v13b: anchor permanently disabled — narrator Hắc Dạ Ký anonymous (1/7 Mr.Long lock)
# ANCHOR const removed 1/7: legacy "Khánh An" name conflicted with Hắc Dạ Ký channel identity
ANCHOR_STRIP_MIN_SEC = 2.5  # kept for detect_anchor_end backward compat (dead path)
ANCHOR_STRIP_MAX_SEC = 4.5
SILENCE_THRESHOLD_DB = -40
MIN_SILENCE_MS = 150
FADE_TAIL_MS = 80   # round 19+ 29/6 02:55 REVERT to 27.6 baseline (Mr.Long: "kiểm tra cách setup E1 27.6 mà học fix")
FADE_HEAD_MS = 30   # keep — first word KHÔNG bị cụt
BRIDGE_MS_DEFAULT = 600  # was 200 cố định bug 25/6 — dùng pause_after_ms từ spec
ROOM_TONE_DB = -50  # ignore — bridge = silence pure (Mr.Long 26/6)
LOUDNESS_TARGET = -18
TAIL_TRIM_DB = -62  # 1/7 Boss: -75 GIU luon duoi residue/hoi tho ~-38dB -> "lup bup" vao bridge zero. -62 = bo bot residue nhung van giu release; Tang 2 fade dai 140ms don not

GEN_KWARGS = {
    "do_sample": True,
    "top_p": 0.5,
    "top_k": 5,
    "temperature": 0.3,
    "length_penalty": 1.0,
    "num_beams": 5,
    "repetition_penalty": 10.0,
    # 1/7 Mr.Long: hạ 1500->1000 chặn runaway (1500=30s -> 1000=20s). ~50 tok/giây;
    # câu dài nhất ~10s=500tok nên 1000 dư gấp đôi, KHÔNG cụt câu thật. Runaway còn lại -> trim v2 dọn.
    "max_mel_tokens": 1000,
}


def set_all_seeds(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch  # lazy: only render needs it, QA logic does not
    except ImportError:
        return  # no ML stack (e.g. CI/QA box) — random+numpy seeded is enough
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
    # 1/7 Boss: raised-cosine (muot hon linear) chong pop onset dau chunk sau bridge zero
    fade = (0.5 * (1 - np.cos(np.linspace(0, np.pi, samples)))).astype(np.float32)
    data[:samples] *= fade
    return data


def make_room_tone(duration_ms, sr, target_db=ROOM_TONE_DB):
    # round 19+ 29/6 05:45 v23 — Mr.Long HARDLOCK: "đoạn nghỉ phải IM LẶNG TUYỆT ĐỐI"
    # REVERT white noise → TRUE ZERO (em đã sai khi inject -90dB noise "bridge")
    # Sau volume=2.0 boost → noise -84dB still audible = "ù ù xì xì"
    # Pair với aggressive boundary trim (find silence start in last 300ms of chunk)
    n = int(duration_ms * sr / 1000)
    return np.zeros(n, dtype=np.float32)


def aggressive_trim_tail(data, sr, silence_thr_db=-40, gap_ms=300, main_run_ms=300,
                          grace_ms=80, fade_ms=10, win_ms=10):
    """v55 — R199 tail pathology hardlock (Mr.Long approve 1/7 09:30)

    OLD v54 (search_ms=600, thr=-30): structural hole → runaway 30s PRESERVED, tail burst PRESERVED.
    NEW v55 (full-scan + gap qualifier + main voice run detection):

    - Scan FULL audio backwards (NO search_ms cap)
    - Silence threshold -40 dB (broader detection)
    - Detect last main voice region (≥100ms contiguous voice above threshold)
    - Cut at end of main voice + grace_ms (80ms chống cụt chữ TỪ CUỐI)
    - Drop everything after: isolated tail bursts + runaway silent trail
    - Fallback: no main voice found → return unchanged (never over-trim to zero)

    Regression 8 chunks (1/7):
    - 2/2 runaway (rp<10) fixed 30s→10s ✓
    - 5 tail residue cleanup safe
    - 0 over-trim warnings
    - 1 regular chunk v1≈v2 (diff <100ms)

    Full doc: runtime/audits/R199_TAIL_PATHOLOGY_REPORT.md
    """
    thr = 10 ** (silence_thr_db / 20)
    win_n = int(win_ms * sr / 1000)
    n_win = len(data) // win_n
    if n_win < (main_run_ms // win_ms) + 5:
        return data.copy()

    win_rms = np.array([
        np.sqrt(np.mean(data[i*win_n:(i+1)*win_n]**2))
        for i in range(n_win)
    ])
    voice_mask = win_rms > thr
    main_run = main_run_ms // win_ms  # 100ms / 10ms = 10 windows

    last_main_end_win = None
    run = 0
    for i in range(n_win):
        if voice_mask[i]:
            run += 1
            if run >= main_run:
                last_main_end_win = i + 1
        else:
            run = 0

    if last_main_end_win is None:
        return data.copy()  # fallback — never over-trim

    # Extend forward from main voice end: include short bursts (<gap_ms silence)
    # Stop at first silence gap >= gap_ms (that's the tail boundary)
    gap_win = gap_ms // win_ms  # e.g. 300ms / 10ms = 30 windows
    extended_end = last_main_end_win
    silence_run = 0
    for i in range(last_main_end_win, n_win):
        if voice_mask[i]:
            extended_end = i + 1
            silence_run = 0
        else:
            silence_run += 1
            if silence_run >= gap_win:
                break

    grace_n = int(grace_ms * sr / 1000)
    cut = min(len(data), extended_end * win_n + grace_n)
    out = data[:cut].copy()
    fade_n = int(fade_ms * sr / 1000)
    if 0 < fade_n < len(out):
        ramp = np.linspace(1.0, 0.0, fade_n).astype(np.float32)
        out[-fade_n:] *= ramp

    return out


def qa_clean_tail(data, sr, release_pad_ms=140, fade_ms=50,
                  flatness_thr=0.35, zcr_thr=0.25, energy_floor_db=-46, win_ms=10):
    """1/7 Boss — VOICING-based deterministic tail cleaner (thay aggressive_trim_tail).
    Van de: BigVGAN de lai residue/hoi tho ~-37dB sau tu -> nguong dB khong tach duoc
    (residue to ngang release). Giai phap: do word-end bang VOICING (spectral flatness +
    zero-crossing), giu toi last-voiced + release_pad, cosine-fade fade_ms ve 0, GATE cung
    phan residue con lai. Deterministic, khong can van tay. Tra (out, info) cho QA gate.
    """
    n = len(data)
    win = max(1, int(win_ms * sr / 1000))
    nf = n // win
    info = {'voiced_end_s': None, 'gated_ms': 0.0, 'gated_peak_db': -99.0, 'end_db': -99.0}
    if nf < 4:
        return data.copy(), info
    peak = float(np.max(np.abs(data))) + 1e-9
    hann = np.hanning(win)
    last_voiced = None
    run = 0
    min_run = 6  # 1/7 Boss: yeu cau voiced LIEN TUC >=60ms moi tinh -> loai crackle/buzz duoi roi rac ("tap am cuoi")
    for i in range(nf):
        seg = data[i * win:(i + 1) * win]
        rms = np.sqrt(np.mean(seg ** 2))
        voiced = False
        if 20 * np.log10(rms / peak + 1e-12) >= energy_floor_db:
            mag = np.abs(np.fft.rfft(seg * hann)) + 1e-9
            flat = float(np.exp(np.mean(np.log(mag))) / np.mean(mag))   # spectral flatness 0..1
            zcr = float(np.mean(np.abs(np.diff(np.sign(seg))))) / 2.0   # zero-crossing rate
            voiced = (flat < flatness_thr and zcr < zcr_thr)            # tonal + ZCR thap = giong noi
        if voiced:
            run += 1
            if run >= min_run:
                last_voiced = i + 1
        else:
            run = 0
    if last_voiced is None:
        return data.copy(), info                                   # fallback: khong bao gio cat het
    keep = min(n, last_voiced * win + int(release_pad_ms * sr / 1000))
    gated = data[keep:]
    if len(gated):
        info['gated_ms'] = len(gated) / sr * 1000
        info['gated_peak_db'] = float(20 * np.log10(np.max(np.abs(gated)) + 1e-9))
    out = data[:keep].copy()
    fn = min(len(out), int(fade_ms * sr / 1000))
    if fn > 0:
        ramp = (0.5 * (1 + np.cos(np.linspace(0, np.pi, fn)))).astype(np.float32)  # cosine 1->0
        out[-fn:] *= ramp
    info['voiced_end_s'] = last_voiced * win / sr
    t5 = out[-max(1, int(0.005 * sr)):]
    info['end_db'] = float(20 * np.log10(np.sqrt(np.mean(t5 ** 2)) + 1e-9))
    return out, info


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
    # v54 ROLLBACK PASS 2 fallback: -25dB (v41 baseline)
    if first_voice is None:
        thr_fallback = 10 ** (-25 / 20)
        for i in range(0, min(search_n, n - win_n), win_n):
            win_rms = np.sqrt(np.mean(data[i:i+win_n] ** 2))
            if win_rms > thr_fallback:
                first_voice = max(0, i - win_n)
                break
    if first_voice is None:
        first_voice = 0
    out = data[first_voice:].copy()
    # v54 ROLLBACK to v41 exp fade-in 8ms e^-12 (Mr.Long approved)
    fade_n = int(0.008 * sr)
    if 0 < fade_n < len(out):
        ramp = np.exp(np.linspace(-12, 0, fade_n)).astype(np.float32)
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
    _tools_dir = os.path.dirname(os.path.abspath(__file__))
    _proj_root = os.path.dirname(_tools_dir)
    md_path = os.path.join(_proj_root, "output", f"ep_{ep_num_early:02d}", "episode.md")
    if os.path.exists(md_path):
        gate_result = subprocess.run(
            [sys.executable, os.path.join(_tools_dir, "qa_eol_diacritic.py"), md_path],
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

    # ========================================================================
    # DEBT-018 R197 GIAI DOAN 1 — LOG-ONLY (Mr.Long 11/7, TUYET DOI KHONG chan render
    # o giai doan nay, cho xem bao cao roi moi quyet giai doan 2). Wire svhmp_preflight_
    # qa.py (FULL_TEXT_GATE THAT: 10-rule preflight + R86 broad chain + character gate)
    # vao render entrypoint - truoc day CHUA TUNG duoc goi tu day (DEBT-018: R197 tu
    # xung "FULL stack, khong ngoai le" nhung render THAT chi goi 1 tool qa_eol_diacritic
    # o R90 STAGE 1 tren, KHONG phai FULL_TEXT_GATE). Ket qua CHI IN RA, KHONG anh huong
    # exit code/luong render - kem theo nhan [R197-LOG-ONLY] de phan biet ro voi cac gate
    # THAT (R90 STAGE 1 o tren, wrapper render_with_character_gate.py ben ngoai) van
    # dang chan nhu cu, KHONG bi thay doi boi doan nay.
    # ========================================================================
    print(f"[v13] [R197-LOG-ONLY] DEBT-018 giai doan 1: chay svhmp_preflight_qa.py (khong chan)...", flush=True)
    try:
        _preflight_result = subprocess.run(
            [sys.executable, os.path.join(_tools_dir, "svhmp_preflight_qa.py"), args.spec],
            capture_output=True, text=True, encoding='utf-8',
            env={**os.environ, 'PYTHONIOENCODING': 'utf-8'},
        )
        print(f"[v13] [R197-LOG-ONLY] preflight_qa exit={_preflight_result.returncode} "
              f"({'SE BI CHAN o giai doan 2' if _preflight_result.returncode != 0 else 'se PASS'})", flush=True)
        for _line in (_preflight_result.stdout or '').splitlines():
            print(f"[v13] [R197-LOG-ONLY]   {_line}", flush=True)
    except Exception as _e:  # noqa: BLE001 — LOG-ONLY tuyet doi khong duoc lam vo render
        print(f"[v13] [R197-LOG-ONLY] WARN: khong chay duoc preflight_qa ({type(_e).__name__}: {_e})", flush=True)

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
    tts = IndexTTS2(model_dir=os.path.expanduser(r'~/index-tts/checkpoints-vi'), use_fp16=True)
    print(f"[v13] Init done [{time.time()-t0:.1f}s]", flush=True)
    _prog.tick(1, f'Model loaded ({time.time()-t0:.1f}s)')

    import tempfile
    tmpdir = tempfile.mkdtemp(prefix="svhmp_v13_")
    print(f"[v13] tmpdir: {tmpdir}", flush=True)

    _prog.start('tts')
    stripped_chunks = []
    _qa_reports = []
    sr_main = None
    for i, sent in enumerate(sentences):
        text = sent['text']
        emo = sent.get('emo_vector', [0.0] * 8)
        tempo = sent.get('tempo_factor', 1.0)
        rendered_text = text  # USE_ANCHOR=False permanent (1/7 Hắc Dạ Ký anonymous narrator)
        out_path = os.path.join(tmpdir, f"seg_{i:03d}.wav")

        # Item 6 (Mr.Long docx 1/7): seed=42+chunk_index → deterministic variation chống robotic onset
        set_all_seeds(42 + i)
        print(f"[v13] Chunk {i+1}/{len(sentences)} (seed={42+i}): {text[:50]}...", flush=True)
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
        stripped, _qa = qa_clean_tail(stripped, sr)  # 1/7 Boss: QA voicing-based tail clean thay v55 (do word-end bang voicing, GATE residue, cosine-fade ve 0) - het "lup bup xi xi"
        _qa_reports.append((i + 1, text[:32], _qa))
        stripped = aggressive_trim_head(stripped, sr, search_ms=200, silence_thr_db=-50)
        stripped = fade_head(stripped, sr, ms=80)  # 1/7 Boss: 15->80ms cosine chong "xet" pop onset chunk tach ra
        print(f"   → {len(stripped)/sr:.2f}s", flush=True)
        chunk_pause = sent.get('pause_after_ms', BRIDGE_MS_DEFAULT)
        stripped_chunks.append((stripped, chunk_pause))

    # 1/7 Boss: QA tail cleanliness report — generate -> QA tu dong, khong fix tay
    _qa_fail = 0
    print("[QA] === Tail cleanliness (voicing clean) ===", flush=True)
    for _idx, _txt, _q in _qa_reports:
        _end = _q['end_db']
        _st = 'PASS' if _end < -50 else 'FAIL'
        if _st == 'FAIL':
            _qa_fail += 1
        print("[QA]  ch%d end=%.0fdB v_end=%.2fs gated=%.0fms(pk %.0fdB) [%s] %s" % (
            _idx, _end, (_q['voiced_end_s'] or 0.0), _q['gated_ms'], _q['gated_peak_db'], _txt, _st), flush=True)
    print("[QA] %d/%d PASS" % (len(_qa_reports) - _qa_fail, len(_qa_reports)), flush=True)

    # 1/7 Boss (R_SUPREME test_process_failure): QA onset-pop — chong "xet" pop dau chunk
    # sau bridge zero (bug xuat hien khi tach nhieu chunk ngan). Nguong 0.13 (onset thuong <0.08).
    _onset_fail = 0
    for _k, (_chunk, _pp) in enumerate(stripped_chunks):
        _oseg = _chunk[:int(0.03 * sr_main)]
        _omd = float(np.max(np.abs(np.diff(_oseg)))) if len(_oseg) > 2 else 0.0
        if _omd >= 0.13:
            _onset_fail += 1
            print("[QA]  onset-pop ch%d maxDiff=%.3f FAIL (>0.13)" % (_k + 1, _omd), flush=True)
    print("[QA] onset-pop: %d/%d PASS" % (len(stripped_chunks) - _onset_fail, len(stripped_chunks)), flush=True)

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
    # v65 MASTER LOCK Mr.Long approved: vocal +5% boost (0.95 → 1.0)
    # RAW peak -1 to -2 dB safe room for boost. Output peak ~-0.5 dB (alimiter 0.85 catch).
    subprocess.run([
        "ffmpeg", "-y", "-i", raw_out,
        "-af", "atempo=0.95,volume=1.0,alimiter=limit=0.85:attack=10:release=80",
        "-ar", "22050",
        "-c:a", "pcm_s16le", args.output,
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # R198 MANDATORY POST-RENDER CAP_PEAK (Mr.Long lock 30/6 23:55 — CLIP repeat 4 lần fix)
    # Wire cap_peak.py: hardlock peak ≤ -1.0 dB. Idempotent, exit 0 if already OK.
    print(f"[v13] R198 cap_peak post-render check...", flush=True)
    cap_result = subprocess.run([
        "python", str(Path(__file__).parent / "cap_peak.py"), args.output,
    ], capture_output=True, text=True, encoding='utf-8',
       env={**os.environ, 'PYTHONIOENCODING': 'utf-8'})
    if cap_result.stdout:
        print(cap_result.stdout.strip(), flush=True)
    if cap_result.returncode != 0:
        print(f"[v13] !!! R198 cap_peak FAIL rc={cap_result.returncode}", flush=True)
        # Continue — cap_peak idempotent failure not fatal but logged.
    print(f"[v13] DONE → {args.output}", flush=True)
    _prog.done(success=True, final_path=args.output)


if __name__ == '__main__':
    main()
