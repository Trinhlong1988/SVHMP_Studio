"""SVHMP — Canon Consistency Check (DEBT-035, R215 enforcer parity).

Khóa chặt một class bug đã lọt EP01: mô tả CÁI CHẾT của Hạ Vy bằng khung cảnh
NƯỚC NGOÀI (New York / Kennedy / taxi / cao tốc / du học Hoa Kỳ) — trái CANON đã
KHÓA ở bible/21 (Hạ Vy mất 12/4/2018 tại Hà Nội, tai nạn XE MÁY).

Nguyên tắc chống false-positive (CỰC KỲ QUAN TRỌNG):
  Rất nhiều hành khách KHÁC (EP14/27/36/47 ...) HỢP LỆ có yếu tố nước ngoài / sân
  bay / du học. Ta KHÔNG bắt token trần toàn tập. Chỉ FLAG khi một token nước-ngoài
  NẰM GẦN đồng thời (a) một từ chỉ CÁI CHẾT và (b) một mention "Hạ Vy" — tức token
  đó thực sự mô tả cảnh Hạ Vy chết ở nước ngoài.

Behavioral, importable:
  - find_canon_violations(text) -> list[dict]  (mutation-proof: đảo token/ngữ cảnh
    trong bộ nhớ => số finding đổi theo).
  - scan_file(path) -> list[dict]
CLI:
  python tools/canon_consistency_check.py            # quét output/ep_01..50/episode.md
  python tools/canon_consistency_check.py <file>...   # quét file cụ thể
  python tools/canon_consistency_check.py --debug     # in offset để tune
Exit 1 nếu có bất kỳ finding (dùng làm gate).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SVHMP = Path(__file__).resolve().parent.parent

# --- Cửa sổ proximity (ký tự). Tune bằng thực nghiệm 50 tập (xem test). ---
#   W_DEATH: token nước-ngoài phải nằm trong khoảng này với 1 TỪ-CHẾT (cảnh chết).
#   W_HAVY : token nước-ngoài phải nằm trong khoảng này với 1 mention "Hạ Vy"
#            (khẳng định người chết là Hạ Vy, không phải hành khách khác).
W_DEATH = 260
W_HAVY = 1300

# PLACE tokens = chỉ dấu MẠNH "chết ở NƯỚC NGOÀI" — CHỈ những token này mới TỰ KÍCH
# một finding (khi nằm gần đồng thời từ-chết + mention Hạ Vy). Canon: Hạ Vy mất tại
# Hà Nội, tai nạn xe máy => bất kỳ PLACE token nào trong ngữ cảnh Hạ Vy chết = vi phạm.
#   Lưu ý chống false-positive:
#   - "Hoa Kỳ" loại trừ địa danh "Chương Hoa Kỳ" (EP14) qua negative lookbehind.
#   - "Mỹ" chỉ bắt khi là QUỐC GIA trong ngữ cảnh di chuyển/định cư, tránh "thẩm mỹ".
PLACE_PATTERNS = {
    "New York": re.compile(r"New\s*York", re.IGNORECASE),
    "Kennedy": re.compile(r"Kennedy", re.IGNORECASE),
    "du học": re.compile(r"du\s+học", re.IGNORECASE),
    "Hoa Kỳ": re.compile(r"(?<!Chương )Hoa\s+Kỳ"),
    "Mỹ (quốc gia)": re.compile(r"(?:sang|đi|ở|về|đến|tại|nước)\s+Mỹ\b"),
}

# CORROBORATING tokens = phương tiện/đường (taxi, cao tốc). CỐ Ý KHÔNG tự kích finding:
# Hà Nội cũng có taxi & đường (EP25: Khải Phong bắt TAXI tới BV Bạch Mai — canon ĐÚNG,
# Hạ Vy chết vì xe máy). Chỉ REPORT kèm khi một PLACE token đã kích finding cùng vùng.
CORROB_PATTERNS = {
    "taxi": re.compile(r"\btaxi\b", re.IGNORECASE),
    "cao tốc": re.compile(r"cao\s+tốc", re.IGNORECASE),
}

# Từ chỉ CÁI CHẾT / hung tin.
DEATH_RE = re.compile(
    r"(qua đời|tai nạn|tử vong|thiệt mạng|hung tin|từ trần|ra đi mãi|đã mất|"
    r"mất ngay|mất tại|lúc .{0,6}mất|giờ .{0,6}mất|\bmất\b)",
    re.IGNORECASE,
)

HAVY_RE = re.compile(r"Hạ\s*[-‐‑]?\s*Vy", re.IGNORECASE)


def _positions(regex: re.Pattern, text: str):
    return [m.start() for m in regex.finditer(text)]


def find_canon_violations(text: str, w_death: int = W_DEATH,
                          w_havy: int = W_HAVY) -> list[dict]:
    """Trả về danh sách vi phạm canon (token nước-ngoài mô tả cảnh Hạ Vy chết).

    Behavioral: nếu gỡ token nước-ngoài HOẶC gỡ từ-chết HOẶC gỡ mention 'Hạ Vy'
    khỏi cửa sổ, finding tương ứng biến mất (mutation-proof).
    """
    death_pos = _positions(DEATH_RE, text)
    havy_pos = _positions(HAVY_RE, text)
    if not death_pos or not havy_pos:
        return []  # không có cảnh chết HOẶC không nhắc Hạ Vy -> không thể vi phạm

    # vị trí các token corroborating (dùng để đính kèm bằng chứng phụ)
    corrob_hits = []
    for ctok, cpat in CORROB_PATTERNS.items():
        for cm in cpat.finditer(text):
            corrob_hits.append((cm.start(), ctok, cm.group()))

    findings: list[dict] = []
    for token, pat in PLACE_PATTERNS.items():
        for m in pat.finditer(text):
            fpos = m.start()
            near_death = min((abs(fpos - d) for d in death_pos), default=10 ** 9)
            near_havy = min((abs(fpos - h) for h in havy_pos), default=10 ** 9)
            if near_death <= w_death and near_havy <= w_havy:
                lo = max(0, fpos - 40)
                hi = min(len(text), fpos + 40)
                corrob = sorted({f"{ct}('{cg}')" for cp, ct, cg in corrob_hits
                                 if abs(cp - fpos) <= w_death})
                findings.append({
                    "token": token,
                    "matched": m.group(),
                    "offset": fpos,
                    "dist_death": near_death,
                    "dist_havy": near_havy,
                    "corroborating": corrob,
                    "context": text[lo:hi].replace("\n", " "),
                })
    return findings


def scan_file(path: str | Path) -> list[dict]:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    out = find_canon_violations(text)
    for f in out:
        f["file"] = str(p)
    return out


def _default_targets() -> list[Path]:
    targets = []
    for n in range(1, 51):
        p = SVHMP / "output" / f"ep_{n:02d}" / "episode.md"
        if p.exists():
            targets.append(p)
    return targets


def main(argv: list[str]) -> int:
    try:  # Windows console/pipe hay cp1252 -> crash khi in "Hạ Vy"; ép utf-8 cho bền (CMD_AUDIT 16/7)
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    debug = "--debug" in argv
    args = [a for a in argv if not a.startswith("--")]
    targets = [Path(a) for a in args] if args else _default_targets()

    total = 0
    print("=== CANON CONSISTENCY CHECK (Hạ Vy death vs canon Hà Nội/xe máy) ===")
    for p in targets:
        findings = scan_file(p)
        if debug:
            text = p.read_text(encoding="utf-8")
            print(f"  [debug] {p.name}: death={len(_positions(DEATH_RE, text))} "
                  f"havy={len(_positions(HAVY_RE, text))}")
        if findings:
            total += len(findings)
            print(f"\n[FLAG] {p}")
            for f in findings:
                corr = (" | kèm: " + ", ".join(f["corroborating"])) if f["corroborating"] else ""
                print(f"  ✗ token='{f['token']}' (khớp '{f['matched']}') "
                      f"@offset {f['offset']} | d_death={f['dist_death']} "
                      f"d_havy={f['dist_havy']}{corr}")
                print(f"      …{f['context']}…")
    verdict = "FAIL" if total else "PASS (0 canon contradiction)"
    print(f"\n=== {verdict} ; findings={total} ; files={len(targets)} ===")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
