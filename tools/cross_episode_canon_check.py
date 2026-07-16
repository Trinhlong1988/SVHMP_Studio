#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CROSS-EPISODE CANON CHECK (R216, 17/7) — khoa chat nguyen tac "tap sinh truoc =
ground truth". Voi moi canon-fact recurring, trich gia tri TUNG tap, neu phan ky
thi FLAG + chi ra ANCHOR = tap sinh SOM NHAT (KHONG auto-tin so dong / tap sau).

Vi sao khong tin so dong: bug goc la EP02-50 (49 tap) dung "ghe thu ba" + "Ha Vy
chet xe may Ha Noi" khac EP01 (goc) "ghe so bay" + "Ha Vy chet taxi New York", roi
bible/03+21 codify theo so dong -> hop thuc hoa cai sai. Gate nay lam nguoc lai:
tap SOM NHAT la chuan; tap sau khac = tap sau SAI (bug can sua xuoi ve tap truoc).

RATCHET (R215.6 — gate that su chay, KHONG phai advisory nam im):
  - Divergence DA BIET dang reconcile (DEBT-035: ghe, noi-chet-Ha-Vy) nam trong
    KNOWN_PENDING -> in [TRACKED-DEBT-035], KHONG fail (no-tracked, khong im lang).
  - BAT KY fact nao phan ky ma KHONG nam trong KNOWN_PENDING -> [FAIL] -> exit 1.
  - Khi reconcile xong 1 fact (49 tap ve EP01) -> XOA key khoi KNOWN_PENDING ->
    gate tu dong tro thanh guard vinh vien cho fact do (phan ky lai = FAIL ngay).

Phan biet:
  - MAU THUAN FACTUAL (bat): cung 1 fact bat bien (cho ngoi/noi chet co dinh) ma
    cac tap ghi khac nhau.
  - REVEAL tang dan (KHONG bat): fact he lo dan qua cac moc — khong thuoc pham vi.

Dung: python tools/cross_episode_canon_check.py
Exit 0 = khong co divergence MOI (ngoai allowlist); exit 1 = co divergence moi.
Wired vao tools/ci_gate.py (chay trong pre-push hook).
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]

# ============================================================================
# FACT 1 — cho ngoi co dinh cua Khai Phong (anchor EP01 = ghe 7)
# ============================================================================
_SEAT_WORDS = (r"thứ\s+ba|ba|bốn|tư|năm|sáu|bảy|tám|chín|mười\s+hai|mười\s+một|"
               r"mười|một|hai|\d+")
_KP_SEAT = re.compile(r"Khải[-\s]?Phong[^.\n]{0,25}?(?:ngồi|ở)\s+(?:trên\s+)?"
                      r"(?:chiếc\s+|cái\s+)?ghế\s+(?:số\s+)?(" + _SEAT_WORDS + r")")
_NORM = {"một": "1", "hai": "2", "ba": "3", "thứ ba": "3", "bốn": "4", "tư": "4",
         "năm": "5", "sáu": "6", "bảy": "7", "tám": "8", "chín": "9", "mười": "10",
         "mười một": "11", "mười hai": "12"}


def _norm_seat(tok):
    t = re.sub(r"\s+", " ", tok).strip().lower()
    return _NORM.get(t, t)


def extract_kp_seat(text):
    """Gia tri ghe cua Khai Phong khai bao trong 1 tap (None neu tap khong noi)."""
    m = _KP_SEAT.search(text)
    return _norm_seat(m.group(1)) if m else None


# ============================================================================
# FACT 2 — noi Ha Vy mat (anchor EP01 = New York/taxi/du hoc). Bao thu: chi phan
# loai khi co ngu canh CAI CHET Ha Vy gan token dia diem (tranh false-positive
# tu boi canh xe chay o Ha Noi — hop le, KHONG phai noi chet).
# ============================================================================
_HAVY = r"Hạ[-\s]?Vy"
_DEATH_CTX = r"(?:mất|chết|tai nạn|qua đời|ra đi|đi rồi|mộ|đám tang)"
# Trong 1 doan gan Ha Vy + tu chet: co token New-York-cluster hay Ha-Noi-cluster?
_NY_TOKENS = re.compile(r"New York|Kennedy|du học Hoa Kỳ|sân bay.*(?:cô|Hạ)|taxi.*(?:New York|Kennedy)")
_HN_DEATH_TOKENS = re.compile(r"phố Huế|Hai Bà Trưng|Bạch Mai|xe máy|ngã tư.*(?:tông|va)|"
                             r"tông ngang|xe tải.*tông")


def extract_havy_death_place(text):
    """'NY' | 'HN' | None tren INPUT SACH (1 nhan vat). KHONG dung lam gate fact:
    tren episode THAT (nhieu hanh khach/tap, moi nguoi 1 cai chet rieng) token dia
    diem thuong thuoc HANH KHACH KHAC -> false-positive (da chung: EP27 'du hoc Hoa
    Ky' la ky su hoa hoc 1997 KHONG phai Ha Vy; EP47 'san bay Noi Bai'+xe may la Dai
    Nga/Nam KHONG phai New York/Ha Vy). Cai chet Ha Vy o EP01 lai trai nhieu dong
    (ten/tu-chet/New-York tach roi) nen khong bind regex chat duoc. => Death enforce
    o tang STRUCTURED (R207 story_consistency_validator khoa bible/03 core_wound) sau
    reconcile, KHONG phai regex prose. Ham nay + unit test giu de tham chieu, KHONG
    wire vao FACTS. Xem R215.1 'chua co enforcer day du'."""
    lines = text.splitlines()
    joined = "\n".join(lines)
    # Phai co dong nhac Ha Vy + chet o dau do trong tap:
    if not re.search(_HAVY, joined) or not re.search(_DEATH_CTX, joined):
        return None
    if _NY_TOKENS.search(joined):
        return "NY"
    if _HN_DEATH_TOKENS.search(joined):
        return "HN"
    return None


# ============================================================================
# Danh muc fact + allowlist ratchet
# ============================================================================
# (key, ten hien thi, extractor). CHI gate fact co the trich TIN CAY tu prose (cong
# thuc 1 cau, bind chat vao Khai Phong). Death Ha Vy KHONG o day (prose da hanh khach
# -> false-positive, xem extract_havy_death_place docstring) — enforce qua R207 structured.
FACTS = [
    ("kp_seat", "Khải Phong cố định ghế", extract_kp_seat),
]

# Divergence DA BIET, dang reconcile theo DEBT-035 R216 (EP01 = anchor). Gate KHONG
# fail tren cac key nay (tracked debt, khong im lang) NHUNG in ra de theo doi. XOA
# key khi reconcile xong -> gate tro thanh guard vinh vien cho fact do.
KNOWN_PENDING = {"kp_seat"}


def _ep_num(path):
    m = re.search(r"ep_(\d+)", str(path))
    return int(m.group(1)) if m else 10**9


def collect_fact(extractor, glob="output/ep_*/episode.md"):
    """{ep_num: (value, path)} cho cac tap co khai bao fact."""
    out = {}
    for p in sorted(ROOT.glob(glob), key=_ep_num):
        n = _ep_num(p)
        try:
            v = extractor(p.read_text(encoding="utf-8"))
        except OSError:
            continue
        if v is not None:
            out[n] = (v, p)
    return out


def find_divergence(fact_map):
    """Neu >1 gia tri phan biet -> dict mo ta phan ky + anchor (tap som nhat)."""
    values = {}
    for ep, (v, _p) in fact_map.items():
        values.setdefault(v, []).append(ep)
    if len(values) <= 1:
        return None
    anchor_ep = min(fact_map)                      # tap sinh SOM NHAT
    anchor_val = fact_map[anchor_ep][0]
    diverging = sorted(ep for ep, (v, _p) in fact_map.items() if v != anchor_val)
    return {"anchor_ep": anchor_ep, "anchor_val": anchor_val,
            "values": {k: sorted(v) for k, v in values.items()}, "diverging": diverging}


def evaluate(results, allowlist):
    """PURE fn (mutation-proof, khong dung file that): quyet PASS/FAIL tu ket qua.

    results: list[(key, name, divergence_dict_or_None)]
    allowlist: set[key] duoc phep phan ky (tracked debt).
    Tra ve (fail_count, lines) — lines: list[(status, key, name, divergence)].
    status in {OK, TRACKED, FAIL}. fail_count = so fact phan ky NGOAI allowlist.
    """
    fail = 0
    lines = []
    for key, name, d in results:
        if d is None:
            lines.append(("OK", key, name, None))
        elif key in allowlist:
            lines.append(("TRACKED", key, name, d))
        else:
            lines.append(("FAIL", key, name, d))
            fail += 1
    return fail, lines


def run_all(facts=FACTS, allowlist=KNOWN_PENDING):
    """Chay moi fact tren repo that -> evaluate. Tra ve (fail_count, lines)."""
    results = []
    for key, name, extractor in facts:
        fmap = collect_fact(extractor)
        d = find_divergence(fmap) if fmap else None
        results.append((key, name, d))
    return evaluate(results, allowlist)


def main():
    print("=== CROSS-EPISODE CANON CHECK (R216 — tập sớm nhất = anchor) ===")
    fail, lines = run_all()
    for status, key, name, d in lines:
        if status == "OK":
            print(f"  [OK] {name}: nhất quán xuyên tập")
            continue
        tag = "[TRACKED-DEBT-035]" if status == "TRACKED" else "[FAIL — DIVERGENCE MỚI]"
        print(f"  {tag} {name}: PHÂN KỲ — anchor EP{d['anchor_ep']:02d} = '{d['anchor_val']}' "
              f"(GROUND TRUTH R216)")
        for val, eps in d["values"].items():
            mark = "  <- anchor" if val == d["anchor_val"] else "  <- SAI (sửa xuôi về anchor)"
            head = ", ".join(f"EP{e:02d}" for e in eps[:6]) + ("..." if len(eps) > 6 else "")
            print(f"        '{val}': {len(eps)} tập [{head}]{mark}")
    if fail:
        print(f"\n=== FAIL ({fail} fact phân kỳ MỚI ngoài allowlist) — tập sau mâu thuẫn "
              f"tập trước (R216). Sửa xuôi về anchor hoặc track vào DEBT. ===")
        return 1
    tracked = sum(1 for s, *_ in lines if s == "TRACKED")
    print(f"\n=== PASS (0 divergence mới; {tracked} divergence đang tracked theo DEBT-035) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
