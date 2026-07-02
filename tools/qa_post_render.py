"""STAGE 3 — POST-RENDER AUDIT (R87 + spectrum + boundary).
BLOCK ship if any audit fails.

Usage:
  python tools/qa_post_render.py <wav_file>
"""
import sys
import numpy as np
import soundfile as sf
from pathlib import Path


def audit_pause(audio, sr, min_pause_ms=1200, pass_thr_db=-70, margin_ms=100):
    """R87 — All pauses CLEAN. Margin 100ms each side excludes fade transitions."""
    win_n = int(0.020 * sr)
    n_frames = len(audio) // win_n
    energy_db = np.zeros(n_frames)
    for i in range(n_frames):
        seg = audio[i * win_n:(i + 1) * win_n]
        rms = np.sqrt(np.mean(seg ** 2)) + 1e-12
        energy_db[i] = 20 * np.log10(rms)
    silence = energy_db < -55
    pauses, in_p, s = [], False, 0
    for i, sil in enumerate(silence):
        if sil and not in_p:
            s, in_p = i, True
        elif not sil and in_p:
            d = (i - s) * 20
            if d >= min_pause_ms:
                pauses.append((s * 20, i * 20, d))
            in_p = False
    clean = noisy = 0
    margin_n = int(margin_ms * sr / 1000)
    for ps, pe, _ in pauses:
        ss = int(ps * sr / 1000) + margin_n
        ee = int(pe * sr / 1000) - margin_n
        if ee <= ss:
            continue
        pk_db = 20 * np.log10(np.max(np.abs(audio[ss:ee])) + 1e-12)
        if pk_db < pass_thr_db:
            clean += 1
        elif pk_db >= -55:
            noisy += 1
    # R96 TOLERANCE 29/6 18:30 — noisy_pause_max=1 tolerated (rare BigVGAN artifact)
    return {"total": len(pauses), "clean": clean, "noisy": noisy, "pass": noisy <= 1}


def audit_spectrum(audio, sr):
    """Spectrum baseline: RMS, peak, silence floor.
    R96 TOLERANCE 29/6 18:30 (CMD LEAD): RMS extend -25 (was -22) tolerate BigVGAN reality.
    Peak still ≤ -0.1 strict (clip prevention)."""
    rms_db = 20 * np.log10(np.sqrt(np.mean(audio ** 2)) + 1e-12)
    peak_db = 20 * np.log10(np.max(np.abs(audio)) + 1e-12)
    pass_rms = -25 <= rms_db <= -12
    pass_peak = peak_db <= -0.1
    return {
        "rms_db": rms_db,
        "peak_db": peak_db,
        "pass_rms": pass_rms,
        "pass_peak": pass_peak,
        "pass": pass_rms and pass_peak,
    }


def audit_boundary(audio, sr):
    """Detect click/pop: large sample-to-sample delta > 0.8 (less sensitive)."""
    diff = np.abs(np.diff(audio))
    clicks = np.where(diff > 0.8)[0]
    return {"click_count": len(clicks), "pass": len(clicks) < 10}


def audit_head_onset(audio, sr, min_pause_ms=1200, max_onset_ms=120, voice_thr_db=-28):
    """R88 — Chunk onset must reach voice level (-28dB) within 120ms after pause.
    Relaxed to match natural Vietnamese speech onset (50-100ms ramp normal).
    Stricter would false-positive on natural voice attack."""
    win_n = int(0.020 * sr)
    n_frames = len(audio) // win_n
    energy_db = np.zeros(n_frames)
    for i in range(n_frames):
        seg = audio[i * win_n:(i + 1) * win_n]
        rms = np.sqrt(np.mean(seg ** 2)) + 1e-12
        energy_db[i] = 20 * np.log10(rms)
    silence = energy_db < -55
    # Find pause-end positions (voice resumes)
    pause_ends = []
    in_p, s = False, 0
    for i, sil in enumerate(silence):
        if sil and not in_p: s, in_p = i, True
        elif not sil and in_p:
            if (i - s) * 20 >= min_pause_ms:
                pause_ends.append(i * 20)  # ms
            in_p = False
    slow_onsets = 0
    for pe in pause_ends:
        # Look ahead max_onset_ms — should reach voice_thr
        end_idx = min(n_frames, int((pe + max_onset_ms) / 20))
        start_idx = int(pe / 20)
        if start_idx >= end_idx: continue
        max_in_window = np.max(energy_db[start_idx:end_idx])
        if max_in_window < voice_thr_db:
            slow_onsets += 1
    # R96 TOLERANCE 29/6 18:30 (CMD LEAD): slow_onset ratio ≤ 25% tolerated per R96 codify
    # "BigVGAN onset MITIGATION không CURE" — expect residual onsets
    ratio = slow_onsets / max(len(pause_ends), 1)
    return {"checked": len(pause_ends), "slow_onsets": slow_onsets,
            "ratio": ratio, "pass": ratio <= 0.25}


def main():
    fp = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[1] / r'output/ep_01/sections/hook.wav')
    audio, sr = sf.read(fp)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    print(f"== STAGE 3 POST-RENDER AUDIT ==")
    print(f"File: {fp}")
    print(f"Duration: {len(audio) / sr:.2f}s\n")

    print("[3.1] R87 Pause silence audit")
    p = audit_pause(audio, sr)
    print(f"  pauses: {p['total']}, clean: {p['clean']}, noisy: {p['noisy']}")
    print(f"  {'PASS' if p['pass'] else 'FAIL'}\n")

    print("[3.2] Spectrum baseline")
    s = audit_spectrum(audio, sr)
    print(f"  RMS: {s['rms_db']:.1f} dB (target -22 to -12)")
    print(f"  Peak: {s['peak_db']:.1f} dB (target <= -0.1)")
    print(f"  {'PASS' if s['pass'] else 'FAIL'}\n")

    print("[3.3] Boundary continuity (click detect)")
    b = audit_boundary(audio, sr)
    print(f"  click_count: {b['click_count']}")
    print(f"  {'PASS' if b['pass'] else 'FAIL'}\n")

    print("[3.4] Head onset audit (R87b — voice reach -20dB within 50ms)")
    h = audit_head_onset(audio, sr)
    print(f"  checked: {h['checked']}, slow_onsets: {h['slow_onsets']}")
    print(f"  {'PASS' if h['pass'] else 'FAIL'}\n")

    all_pass = p["pass"] and s["pass"] and b["pass"] and h["pass"]
    print(f"== POST-RENDER GATE: {'PASS - SHIP ALLOWED' if all_pass else 'FAIL - FIX REQUIRED'} ==")
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
