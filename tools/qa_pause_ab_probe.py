"""qa_pause_ab_probe.py — G8 D3 A/B HARNESS (turnkey cho CMD_AUDIO, per Mr.Long approve 9/7).

MỤC ĐÍCH: đo tác động của QUYẾT ĐỊNH ngưỡng `noisy<=1` (thay `noisy==0` lỗi thời của
`qa_pause_silence.py`) TRÊN 87 wav golden — bằng chứng A/B BẮT BUỘC trước khi CMD_AUDIO merge
dedup PAUSE (TASK_G8 D3: "phải chạy A/B golden set trước/sau, báo bao nhiêu case đổi verdict").

RÀNG BUỘC (Mr.Long 9/7): KHÔNG sửa/không import 4 file audio_qa (CMD_AUDIO sở hữu). Harness này
chỉ `subprocess` gọi `tools/qa_pause_silence.py <wav>` (đọc NOISY count từ stdout) rồi ÁP CẢ HAI
ngưỡng để đếm số wav đổi verdict. Không đụng 1 dòng code nào của domain audio_qa.

Ý nghĩa A/B:
  - v_old = PASS nếu noisy == 0   (qa_pause_silence.py HIỆN TẠI — bản lỗi thời)
  - v_new = PASS nếu noisy <= 1   (ngưỡng ĐÃ DUYỆT R96 v3.3 — cũng là qa_post_render.audit_pause)
  FLIP = wav FAIL(old) nhưng PASS(new): chính là wav có đúng 1 noisy pause (rare BigVGAN artifact
  mà R96 v3.3 chấp nhận). Sau dedup (qa_pause_silence chuyển sang noisy<=1), các wav này đổi verdict.

Usage:
  python tools/qa_pause_ab_probe.py                       # full 87 wav
  python tools/qa_pause_ab_probe.py --limit 5             # nhanh
  python tools/qa_pause_ab_probe.py --json runtime/d3_pause_ab.json
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PAUSE_TOOL = REPO / "tools" / "qa_pause_silence.py"
NOISY_RE = re.compile(r"NOISY=(\d+)")
PAUSES_RE = re.compile(r"CLEAN=\d+/(\d+)")


def probe_wav(wav: Path):
    """Trả (noisy, pauses) từ stdout qa_pause_silence.py, hoặc None nếu lỗi/không đọc được."""
    try:
        r = subprocess.run(
            [sys.executable, str(PAUSE_TOOL), str(wav)],
            capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=180,
        )
    except subprocess.TimeoutExpired:
        return None
    m = NOISY_RE.search(r.stdout)
    if not m:
        return None
    p = PAUSES_RE.search(r.stdout)
    return int(m.group(1)), (int(p.group(1)) if p else None)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--glob", default="output/**/*.wav")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    wavs = sorted(REPO.glob(args.glob))
    if args.limit:
        wavs = wavs[:args.limit]

    rows, flips, errors = [], [], 0
    for i, w in enumerate(wavs, 1):
        res = probe_wav(w)
        if res is None:
            errors += 1
            print(f"[{i}/{len(wavs)}] {w.name}: ERROR (không đọc được NOISY)")
            continue
        noisy, pauses = res
        v_old = "PASS" if noisy == 0 else "FAIL"
        v_new = "PASS" if noisy <= 1 else "FAIL"
        flip = v_old != v_new
        rel = str(w.relative_to(REPO)).replace("\\", "/")
        row = {"wav": rel, "pauses": pauses, "noisy": noisy,
               "old_noisy==0": v_old, "new_noisy<=1": v_new, "flip": flip}
        rows.append(row)
        if flip:
            flips.append(row)
        print(f"[{i}/{len(wavs)}] {w.name}: pauses={pauses} noisy={noisy} "
              f"old(==0)={v_old} new(<=1)={v_new}{'  <-- FLIP' if flip else ''}")

    n_old_pass = sum(1 for r in rows if r["old_noisy==0"] == "PASS")
    n_new_pass = sum(1 for r in rows if r["new_noisy<=1"] == "PASS")
    print("\n" + "=" * 70)
    print(f"A/B SUMMARY — {len(rows)} wav đo được, {errors} lỗi")
    print(f"  PASS dưới ngưỡng CŨ (noisy==0):  {n_old_pass}/{len(rows)}")
    print(f"  PASS dưới ngưỡng MỚI (noisy<=1): {n_new_pass}/{len(rows)}")
    print(f"  FLIP verdict (FAIL->PASS): {len(flips)}  <-- số case đổi verdict do quyết định ngưỡng")
    if flips:
        print("  Các wav FLIP (đều là noisy==1, rare BigVGAN artifact R96 v3.3 chấp nhận):")
        for r in flips:
            print(f"    - {r['wav']} (noisy={r['noisy']}/{r['pauses']} pauses)")
    print("  Ghi chú: KHÔNG có case PASS(old)->FAIL(new) về mặt logic (noisy<=1 lỏng hơn noisy==0),")
    print("  nên dedup theo hướng noisy<=1 chỉ NỚI verdict, không siết — an toàn 1 chiều.")
    print("=" * 70)

    if args.json:
        out = {"total": len(rows), "errors": errors, "old_pass": n_old_pass,
               "new_pass": n_new_pass, "flips": len(flips), "rows": rows}
        Path(args.json).write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[json] {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
