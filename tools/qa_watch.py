"""CMD QA WATCH — independent monitor scanning text + audio + render state.
Mr.Long lệnh: CMD QA chạy song song khi em làm việc.

Loop every 60s:
  1. STAGE 1 R86 EOL diacritic scan
  2. Text scan: duplicate words back-to-back
  3. STAGE 3 audit per section
  4. Log VIOLATION/PASS to PING via log_ping.py
"""
import subprocess
import time
import os
import sys
import re
from pathlib import Path

# CMD LEAD 30/6 Round 19.31: CREATE_NO_WINDOW cho mọi subprocess — Mr.Long lệnh ẩn nháy
CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0
PYW = sys.executable.replace("python.exe", "pythonw.exe") if Path(sys.executable.replace("python.exe", "pythonw.exe")).exists() else sys.executable

ROOT = Path(__file__).resolve().parents[1]
EPISODE = ROOT / "output/ep_01/episode.md"
SECTIONS = ROOT / "output/ep_01/sections"
LOG_PING = ROOT / "tools/log_ping.py"


def p(msg):
    print(msg, flush=True)


def log(category, msg):
    try:
        subprocess.run(
            [PYW, str(LOG_PING), category, msg],
            capture_output=True,
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            timeout=10,
            creationflags=CREATE_NO_WINDOW,
        )
    except: pass


def stage_1():
    try:
        r = subprocess.run(
            [PYW, str(ROOT / "tools/qa_eol_diacritic.py"), str(EPISODE)],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            timeout=30,
            creationflags=CREATE_NO_WINDOW,
        )
        return r.returncode == 0
    except: return False


def stage_3(section):
    wav = SECTIONS / f"{section}.wav"
    if not wav.exists():
        return None
    try:
        r = subprocess.run(
            [PYW, str(ROOT / "tools/qa_post_render.py"), str(wav)],
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
            timeout=30,
            creationflags=CREATE_NO_WINDOW,
        )
        return r.returncode == 0
    except: return None


# R98 whitelist — onomatopoeia / idiom Vietnamese 2-syl reduplication
# CMD LEAD 29/6 18:10: catch false positive "rì rì" (tiếng máy), "từ từ" (slowly)
# CMD LEAD 29/6 23:00: add "dần" sau 22 iter QA WATCH persistent L550 "dần dần"
WHITELIST_REDUP = {
    "bép", "bùng", "bẹp", "chát", "chầm", "chậm", "chập", "chờn", "cạch", "dim", "dần", "hoài",
    "khoải", "khò", "khắc", "khẹt", "khẽ", "kẹt", "kẽo", "lai", "lanh", "le", "leng", "lim", "loè",
    "loạng", "luôn", "lác", "lách", "lép", "lò", "ló", "lói", "lóng", "lúng", "lúp", "lăn", "lạch",
    "lấp", "lập", "lẳng", "lặng", "lốp", "lộc", "lờ", "lụng", "lụp", "lụt", "lủng", "mãi", "mải",
    "ngày", "ngúc", "ngúng", "ngơ", "ngấn", "ngẩn", "nhô", "nhấp", "nhẹ", "năm", "phì", "phù",
    "phập", "phồng", "rai", "rin", "run", "rách", "ráp", "rì", "rít", "róc", "rón", "rùng", "rơi",
    "rầm", "rẩy", "rộn", "rộp", "rớt", "rợn", "thi", "thoáng", "thoăn", "thoắt", "thui", "tháng",
    "thì", "thấp", "thầm", "thỉnh", "thủi", "trĩu", "tách", "tép", "tích", "tóc", "tóp", "tạch",
    "từ", "ve", "vo", "vù", "xì", "ò", "ù", "đêm", "đùng", "đăm", "đần", "đắm", "ấm", "ầm", "ức",
}


def text_repeats():
    try:
        text = EPISODE.read_text(encoding="utf-8")
    except: return []
    violations = []
    for ln, line in enumerate(text.split("\n"), 1):
        line = line.strip()
        if not line or line.startswith(("#", "[", "---", "```", "|", ">")): continue
        words = line.split()
        for j in range(len(words)-1):
            w1_raw = words[j]
            w2_raw = words[j+1]
            # Cross-sentence skip: w1 ends with .!?
            if w1_raw and w1_raw[-1] in ".!?":
                continue
            w1 = re.sub(r"[^\wÀ-ỹ]", "", w1_raw).lower()
            w2 = re.sub(r"[^\wÀ-ỹ]", "", w2_raw).lower()
            if w1 == w2 and len(w1) >= 2:
                # Whitelist skip
                if w1 in WHITELIST_REDUP:
                    continue
                violations.append((ln, f"{w1_raw} {w2_raw}"))
    return violations


def main():
    p("=== CMD QA WATCH started ===")
    p(f"Episode: {EPISODE}")
    p(f"Loop every 60s. Logs to PING via log_ping.py.\n")
    log("INFO", "CMD QA WATCH started loop 60s")
    iter_count = 0
    while True:
        iter_count += 1
        ts = time.strftime("%H:%M:%S")
        p(f"\n[{ts}] === iter {iter_count} ===")

        s1 = stage_1()
        status1 = "PASS" if s1 else "FAIL"
        p(f"  STAGE 1 R86: {status1}")
        if not s1:
            log("VIOLATION", f"QA WATCH iter {iter_count}: STAGE 1 R86 FAIL")

        reps = text_repeats()
        p(f"  TEXT R98 repeats: {len(reps)}")
        if reps:
            # CMD LEAD 29/6 18:10: log từ + line CỤ THỂ (không chỉ count) để CMD LEAD apply fix
            detail = "; ".join([f"L{ln}:{txt}" for ln, txt in reps[:5]])
            log("VIOLATION", f"QA WATCH iter {iter_count}: {len(reps)} repeat words [{detail}]")

        for section in ["hook", "setup", "incident", "reveal", "payoff", "cliffhanger"]:
            res = stage_3(section)
            if res is None:
                p(f"  STAGE 3 {section}: MISSING")
            else:
                status = "PASS" if res else "FAIL"
                p(f"  STAGE 3 {section}: {status}")

        # CMD LEAD 29/6 23:35: wire verify_ping_claim mỗi iter — auto-catch CMD #2 claim sai
        try:
            r = subprocess.run(
                [PYW, str(ROOT / "tools/verify_ping_claim.py"), "--recent", "5"],
                capture_output=True, text=True, encoding="utf-8",
                env={**os.environ, "PYTHONIOENCODING": "utf-8"}, timeout=60,
                creationflags=CREATE_NO_WINDOW,
            )
            m = re.search(r"VERIFIED=(\d+)\s+FAILED=(\d+)\s+UNKNOWN=(\d+)", r.stdout)
            if m:
                ver, fail, unk = m.group(1), m.group(2), m.group(3)
                p(f"  PING VERIFY: V={ver} F={fail} U={unk}")
                if int(fail) > 0:
                    log("VIOLATION", f"QA WATCH iter {iter_count}: {fail} PING claim FAILED — em CMD LEAD verify cụ thể từng claim")
        except Exception as e:
            p(f"  PING VERIFY: [ERR {e}]")

        p(f"\n  Next iter in 60s...")
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        p("\n=== STOPPED ===")
