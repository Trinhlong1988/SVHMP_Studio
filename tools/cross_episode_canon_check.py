#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CROSS-EPISODE CANON CHECK (R216, 17/7) — khoa chat nguyen tac "tap sinh truoc =
ground truth". Voi moi canon-fact recurring, trich gia tri TUNG tap, neu phan ky
thi FLAG + chi ra ANCHOR = tap sinh SOM NHAT (KHONG auto-tin so dong / tap sau).

Vi sao khong tin so dong: bug goc la EP02-50 (49 tap) dung "ghe thu ba" khac EP01
(goc) "ghe so bay", roi bible/03 codify theo so dong -> hop thuc hoa cai sai. Gate
nay lam nguoc lai: tap SOM NHAT la chuan; tap sau khac = tap sau SAI (bug can sua
xuoi ve tap truoc, KHONG sua tap truoc).

Phan biet:
  - MAU THUAN FACTUAL (bat): cung 1 fact bat bien (cho ngoi co dinh cua KP) ma cac
    tap ghi khac nhau.
  - REVEAL tang dan (KHONG bat): fact duoc he lo dan qua cac moc — khong thuoc pham
    vi tool nay (chi so canh cac fact khai bao la BAT BIEN cross-episode).

Dung: python tools/cross_episode_canon_check.py
Exit 0 = moi canon-fact nhat quan xuyen tap; exit 1 = co phan ky (kem anchor).

TRANG THAI: chua wire vao ci_gate (dang co 1 phan ky THAT chua giai — EP01 ghe 7 vs
EP02-50 ghe 3, cho Mr.Long quyet sua 49 tap hay bible). Chay tay de bao cao.
"""
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[1]

_SEAT_WORDS = (r"thứ\s+ba|ba|bốn|tư|năm|sáu|bảy|tám|chín|mười\s+hai|mười\s+một|"
               r"mười|một|hai|\d+")
# Canon-fact "cho ngoi co dinh cua Khai Phong": cau "Khai Phong ... ngoi ... (chiec) ghe X".
_KP_SEAT = re.compile(r"Khải[-\s]?Phong[^.\n]{0,25}?(?:ngồi|ở)\s+(?:trên\s+)?"
                      r"(?:chiếc\s+|cái\s+)?ghế\s+(?:số\s+)?(" + _SEAT_WORDS + r")")

# Chuan hoa bien the ve 1 khoa: "ba"/"thu ba" -> "3", "bay" -> "7", ...
_NORM = {"một": "1", "hai": "2", "ba": "3", "thứ ba": "3", "bốn": "4", "tư": "4",
         "năm": "5", "sáu": "6", "bảy": "7", "tám": "8", "chín": "9", "mười": "10",
         "mười một": "11", "mười hai": "12"}


def _norm_seat(tok):
    t = re.sub(r"\s+", " ", tok).strip().lower()
    return _NORM.get(t, t)


def _ep_num(path):
    m = re.search(r"ep_(\d+)", str(path))
    return int(m.group(1)) if m else 10**9


def extract_kp_seat(text):
    """Gia tri ghe cua Khai Phong khai bao trong 1 tap (None neu tap khong noi)."""
    m = _KP_SEAT.search(text)
    return _norm_seat(m.group(1)) if m else None


def collect_fact(glob="output/ep_*/episode.md", extractor=extract_kp_seat):
    """{ep_num: (value, path)} cho cac tap co khai bao fact."""
    out = {}
    for p in sorted((ROOT).glob(glob), key=_ep_num):
        n = _ep_num(p)
        try:
            v = extractor(p.read_text(encoding="utf-8"))
        except OSError:
            continue
        if v is not None:
            out[n] = (v, p)
    return out


def find_divergence(fact_map):
    """Neu >1 gia tri phan biet -> tra ve dict mo ta phan ky + anchor (tap som nhat)."""
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


def main():
    print("=== CROSS-EPISODE CANON CHECK (R216 — tập sớm nhất = anchor) ===")
    facts = [("Khải Phong cố định ghế", collect_fact())]
    bad = 0
    for name, fmap in facts:
        if not fmap:
            print(f"  [SKIP] {name}: khong tap nao khai bao")
            continue
        d = find_divergence(fmap)
        if not d:
            v = next(iter(fmap.values()))[0]
            print(f"  [OK] {name}: nhất quán = '{v}' xuyên {len(fmap)} tập")
            continue
        bad += 1
        print(f"  [FLAG] {name}: PHÂN KỲ — {len(d['values'])} giá trị khác nhau")
        print(f"         ANCHOR (tập sớm nhất EP{d['anchor_ep']:02d}) = '{d['anchor_val']}' "
              f"→ đây là GROUND TRUTH (R216)")
        for val, eps in d["values"].items():
            tag = "  <- anchor" if val == d["anchor_val"] else "  <- SAI (sửa xuôi về anchor)"
            head = ", ".join(f"EP{e:02d}" for e in eps[:6]) + ("..." if len(eps) > 6 else "")
            print(f"           '{val}': {len(eps)} tập [{head}]{tag}")
    if bad:
        print(f"\n=== FAIL ({bad} canon-fact phân kỳ) — tập sau mâu thuẫn tập trước (R216) ===")
        return 1
    print("\n=== PASS (mọi canon-fact nhất quán xuyên tập) ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
