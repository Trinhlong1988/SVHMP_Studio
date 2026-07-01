"""R87 QA — Pause silence audit (HARDLOCK).
Detect pauses >=1200ms in audio file, verify ALL pauses peak < -70 dBFS.

Pass criteria: ALL pauses CLEAN (peak < -70 dBFS true silence)
Fail criteria: ANY pause NOISY (peak > -55 dBFS audible residue)

Usage:
  python tools/qa_pause_silence.py <wav_file>
"""
import sys
import numpy as np
import soundfile as sf
from pathlib import Path


def audit(wav_path, min_pause_ms=1200, silence_thr_db=-55, pass_thr_db=-70):
    audio, sr = sf.read(wav_path)
    if audio.ndim == 2:
        audio = audio.mean(axis=1)
    total_dur = len(audio) / sr

    # Detect silent frames (20ms windows)
    win_n = int(0.020 * sr)
    n_frames = len(audio) // win_n
    energy_db = np.zeros(n_frames)
    for i in range(n_frames):
        seg = audio[i * win_n:(i + 1) * win_n]
        rms = np.sqrt(np.mean(seg ** 2)) + 1e-12
        energy_db[i] = 20 * np.log10(rms)

    silence = energy_db < silence_thr_db
    pauses = []
    in_p = False
    s_start = 0
    for i, sil in enumerate(silence):
        if sil and not in_p:
            s_start = i
            in_p = True
        elif not sil and in_p:
            dur = (i - s_start) * 20
            if dur >= min_pause_ms:
                pauses.append((s_start * 20, i * 20, dur))
            in_p = False

    clean = ok = noisy = 0
    results = []
    # Margin 100ms each side — exclude fade-in/fade-out transitions of adjacent chunks
    margin_ms = 100
    margin_n = int(margin_ms * sr / 1000)
    for i, (s, e, d) in enumerate(pauses):
        s_samp = int(s * sr / 1000) + margin_n
        e_samp = int(e * sr / 1000) - margin_n
        if e_samp <= s_samp:
            continue  # pause too short after margin
        pa = audio[s_samp:e_samp]
        pmax_db = 20 * np.log10(np.max(np.abs(pa)) + 1e-12)
        if pmax_db < pass_thr_db:
            verdict = "CLEAN"
            clean += 1
        elif pmax_db < silence_thr_db:
            verdict = "OK"
            ok += 1
        else:
            verdict = "NOISY"
            noisy += 1
        results.append((i + 1, s / 1000, d, pmax_db, verdict))

    return {
        "file": str(wav_path),
        "duration_sec": total_dur,
        "pauses_detected": len(pauses),
        "clean": clean,
        "ok": ok,
        "noisy": noisy,
        "results": results,
        "pass": noisy == 0,
    }


def report(audit_result):
    r = audit_result
    print(f"== R87 PAUSE SILENCE AUDIT ==")
    print(f"File: {r['file']}")
    print(f"Duration: {r['duration_sec']:.2f}s")
    print(f"Pauses >=1200ms: {r['pauses_detected']}")
    print()
    print(f"{'P':<4} {'start':<8} {'dur':<6} {'PEAK_dB':<10} VERDICT")
    print("-" * 50)
    for p, s, d, pk, v in r["results"]:
        print(f"{p:<4} {s:<8.2f} {d:<6} {pk:<10.1f} {v}")
    print()
    print(f"SUMMARY: CLEAN={r['clean']}/{r['pauses_detected']} OK={r['ok']} NOISY={r['noisy']}")
    print(f"R87 PASS: {r['pass']}")
    return r["pass"]


if __name__ == "__main__":
    fp = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parents[1] / r'output/ep_01/sections/hook.wav')
    res = audit(fp)
    passed = report(res)
    sys.exit(0 if passed else 1)
