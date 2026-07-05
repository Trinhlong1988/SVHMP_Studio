"""Regression tests for Tier 2.1 Audio/Mix Gate.

5 cases per Mr.Long lệnh:
  1. bad 0-gap mix → must FAIL R94b
  2. internal long pause (NOT at boundary) → must NOT satisfy boundary silence
  3. valid boundary silence → must PASS
  4. music shorter than voice → must FAIL music_loop check
  5. substitute still violates R111 → must FAIL self-verify
"""
import subprocess
import sys
from pathlib import Path
import soundfile as sf
import numpy as np
import tempfile

BASE = Path(__file__).resolve().parent.parent.parent
SECTIONS_DIR = BASE / "output/ep_01/sections"


def run(args, timeout=120):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True,
                       cwd=str(BASE), timeout=timeout, encoding="utf-8", errors="ignore")
    return r.returncode, r.stdout, r.stderr


def make_silence(duration_sec, sr=22050):
    return np.zeros(int(sr * duration_sec), dtype=np.float32)


def make_tone(duration_sec, sr=22050, freq=440, amp=0.1):
    t = np.linspace(0, duration_sec, int(sr * duration_sec), dtype=np.float32)
    return amp * np.sin(2 * np.pi * freq * t)


def case_1_bad_0gap():
    """0-gap concat between sections — must FAIL R94b."""
    print("\n--- Case 1: 0-gap concat (must FAIL) ---")
    # Create temp 6 fake sections (each 10s tone) + concat 0-gap
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # 6 fake sections
        for i, name in enumerate(["hook", "setup", "incident", "reveal", "payoff", "cliffhanger"]):
            audio = make_tone(10.0, freq=400 + i*50)
            sf.write(str(tmp_path / f"{name}.wav"), audio, 22050)
        # Concat 0-gap (no silence)
        all_audio = np.concatenate([
            sf.read(str(tmp_path / f"{n}.wav"))[0]
            for n in ["hook", "setup", "incident", "reveal", "payoff", "cliffhanger"]
        ])
        bad_wav = tmp_path / "bad_0gap.wav"
        sf.write(str(bad_wav), all_audio, 22050)
        # Run qa with custom sections_dir
        code, out, _ = run([str(BASE / "tools/qa_concat_silence.py"),
                            "--wav", str(bad_wav),
                            "--sections_dir", str(tmp_path),
                            "--expected_count", "5"])
        assert code != 0, f"Case 1 should FAIL but exit={code}: {out[-200:]}"
        print(f"  ✅ Case 1: FAIL caught (exit={code})")


def case_2_internal_pause_not_boundary():
    """Audio with many internal long pauses but NOT at section boundaries.
    Must FAIL because timestamp-based check requires silence AT boundaries."""
    print("\n--- Case 2: internal pause not at boundary (must FAIL) ---")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # 6 sections each 10s. Boundaries at 10, 20, 30, 40, 50
        # But put 2s silence at 5s, 15s, 25s (inside sections, NOT at boundary)
        sections_audio = []
        for i, name in enumerate(["hook", "setup", "incident", "reveal", "payoff", "cliffhanger"]):
            tone = make_tone(5.0, freq=400 + i*50)
            internal_pause = make_silence(2.0)
            tone2 = make_tone(3.0, freq=400 + i*50)
            section = np.concatenate([tone, internal_pause, tone2])  # 10s total
            sf.write(str(tmp_path / f"{name}.wav"), section, 22050)
            sections_audio.append(section)
        # Concat 0-gap → no silence at boundaries (despite internal pauses)
        bad_wav = tmp_path / "internal_pause.wav"
        sf.write(str(bad_wav), np.concatenate(sections_audio), 22050)
        code, out, _ = run([str(BASE / "tools/qa_concat_silence.py"),
                            "--wav", str(bad_wav),
                            "--sections_dir", str(tmp_path),
                            "--expected_count", "5"])
        assert code != 0, f"Case 2 should FAIL but exit={code}: {out[-300:]}"
        print(f"  ✅ Case 2: FAIL caught (internal pause not satisfying boundary)")


def case_3_valid_boundary_silence():
    """6 sections + 1.5s silence between each → must PASS."""
    print("\n--- Case 3: valid boundary silence (must PASS) ---")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        sections = []
        for i, name in enumerate(["hook", "setup", "incident", "reveal", "payoff", "cliffhanger"]):
            tone = make_tone(10.0, freq=400 + i*50)
            sf.write(str(tmp_path / f"{name}.wav"), tone, 22050)
            sections.append(tone)
        # Concat with 1.5s silence between
        silence = make_silence(1.5)
        parts = []
        for i, s in enumerate(sections):
            parts.append(s)
            if i < len(sections) - 1:
                parts.append(silence)
        good_wav = tmp_path / "good_boundary.wav"
        sf.write(str(good_wav), np.concatenate(parts), 22050)
        code, out, _ = run([str(BASE / "tools/qa_concat_silence.py"),
                            "--wav", str(good_wav),
                            "--sections_dir", str(tmp_path),
                            "--expected_count", "5"])
        assert code == 0, f"Case 3 should PASS but exit={code}: {out[-300:]}"
        print(f"  ✅ Case 3: PASS (5/5 boundaries match)")


def case_4_music_shorter_than_voice():
    """music_loop.py with music shorter than voice — should LOOP to cover."""
    print("\n--- Case 4: music shorter than voice (must auto-loop) ---")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        voice = make_tone(60.0, freq=440)  # 60s voice
        music = make_tone(20.0, freq=200, amp=0.05)  # 20s music
        voice_wav = tmp_path / "voice.wav"
        music_wav = tmp_path / "music.wav"
        sf.write(str(voice_wav), voice, 22050)
        sf.write(str(music_wav), music, 22050)
        out_mp3 = tmp_path / "looped.mp3"
        code, out, _ = run([str(BASE / "tools/music_loop.py"),
                            "--voice", str(voice_wav),
                            "--music", str(music_wav),
                            "--output", str(out_mp3),
                            "--intro-sec", "0", "--outro-sec", "5"])
        assert code == 0, f"Case 4 music_loop failed: {out[-300:]}"
        assert out_mp3.exists(), "Output not created"
        # Verify duration ≈ 65s (0 + 60 + 5)
        info_r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                 "-of", "csv=p=0", str(out_mp3)], capture_output=True, text=True)
        final_dur = float(info_r.stdout.strip())
        assert abs(final_dur - 65) < 1.5, f"Duration {final_dur:.2f}s != 65s"
        print(f"  ✅ Case 4: music looped to {final_dur:.2f}s (target 65s)")


def case_5_substitute_violates_r111():
    """text_batch_fix substitute that still violates R86 → must FAIL self-verify.

    DEBT-005 fix (5/7 tối): tools/text_batch_fix.py::verify_post_fix() giờ chạy
    HOÀN TOÀN trên 1 bản copy episode.md trong tempfile.TemporaryDirectory() riêng
    của chính nó — KHÔNG BAO GIỜ đụng output/ep_01/episode.md / episode_tts_ready.md
    THẬT, dù chỉ tạm thời. Vì vậy test này KHÔNG CÒN CẦN backup/restore 2 file thật
    (đã bỏ toàn bộ khối try/finally cũ) — verify_post_fix() tự cô lập, an toàn kể cả
    khi nhiều tiến trình gọi đồng thời (đã test thủ công 2 terminal song song, xem
    governance/TECH_DEBT.md#DEBT-005)."""
    print("\n--- Case 5: substitute violates R111/R86 (must FAIL self-verify) ---")
    import importlib.util
    spec = importlib.util.spec_from_file_location("tbf", str(BASE / "tools/text_batch_fix.py"))
    tbf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tbf)

    ep = BASE / "output/ep_01/episode.md"
    t = ep.read_text(encoding='utf-8')
    bad_text = t.replace("Khải-Phong đang ngồi trên ghế số bảy của chuyến xe đêm.",
                         "Khải-Phong đang ngồi trên ghế số bảy đó cũ.")
    assert bad_text != t, "substitution did not apply — case setup broken"
    failed = tbf.verify_post_fix(bad_text, ["R86"])
    assert "R86" in failed, f"R86 should fail on 'cũ.' EOL but didn't"
    print(f"  ✅ Case 5: R86 self-verify caught bad substitute")


def main():
    print("=" * 60)
    print("AUDIO GATE REGRESSION TESTS (5 cases per Mr.Long)")
    print("=" * 60)
    case_1_bad_0gap()
    case_2_internal_pause_not_boundary()
    case_3_valid_boundary_silence()
    case_4_music_shorter_than_voice()
    case_5_substitute_violates_r111()
    print("\n" + "=" * 60)
    print("✅ ALL 5 REGRESSION CASES PASS")
    print("=" * 60)


if __name__ == "__main__":
    main()
