"""VN NUMBER WORDS — parse so dem tieng Viet viet chu (khong dung digit) thanh int.

Ly do can rieng: tat ca episode.md hien co (ep_01..ep_50) VIET SO BANG CHU
("mười năm trước", "ba mươi mốt tuổi") — KHONG dung chu so ("10 năm trước").
timeline_check.py (G4 D1) + event_ledger_miner.py (G4 D2) deu can parse duoc
dang nay de doi chieu tuoi/nam xuyen tap — khong duoc bia/doan, phai parse that.

Ho tro 0-999 (du dai cho tuoi doi/so nam trong truyen). KHONG ho tro so am,
phan so, hoac tu dac biet ("mấy chục", "vài năm" — mo ho, tra None thay vi doan).
"""
import re

_UNITS = {'không': 0, 'một': 1, 'mốt': 1, 'hai': 2, 'ba': 3, 'bốn': 4, 'tư': 4,
          'năm': 5, 'lăm': 5, 'nhăm': 5, 'sáu': 6, 'bảy': 7, 'bẩy': 7, 'tám': 8, 'chín': 9}
_TEEN_ZERO = {'mười': 10}


def _parse_under_100(tokens):
    """tokens: list tu da tach (khong con 'trăm'). Tra (value, so_tu_da_dung) hoac (None, 0)."""
    if not tokens:
        return None, 0
    t0 = tokens[0]
    if t0 in _UNITS and len(tokens) == 1:
        return _UNITS[t0], 1
    if t0 == 'mười':
        if len(tokens) == 1:
            return 10, 1
        t1 = tokens[1]
        if t1 in _UNITS:
            # 'mười lăm' = 15 (lăm o vi tri hang don vi sau muoi van la 5)
            return 10 + _UNITS[t1], 2
        return 10, 1
    if t0 in ('mươi',):  # khong dung dau cau (loi ngu phap) -> bo qua
        return None, 0
    # 'X mươi [Y]' — X la don vi hang chuc (hai/ba/.../chin), roi tu 'mươi'
    if t0 in _UNITS and len(tokens) >= 2 and tokens[1] == 'mươi':
        chuc = _UNITS[t0] * 10
        if len(tokens) >= 3:
            t2 = tokens[2]
            if t2 == 'mốt' and chuc >= 20:
                return chuc + 1, 3
            if t2 in _UNITS:
                return chuc + _UNITS[t2], 3
        return chuc, 2
    # 'X mốt' ELIDED (van noi that: "hai mốt" = "hai mươi mốt" = 21) — X phai
    # la tu hang chuc hop le (2-9), tranh nham voi 'một mốt' vo nghia
    if (t0 in _UNITS and _UNITS[t0] >= 2 and len(tokens) >= 2 and tokens[1] == 'mốt'):
        return _UNITS[t0] * 10 + 1, 2
    return None, 0


def parse_vn_number(text):
    """Parse cum so dem tieng Viet o DAU chuoi text (da lower, da tach tu).
    Tra (value:int|None, n_token_dung:int). Ho tro 0-999."""
    tokens = text.strip().lower().split()
    if not tokens:
        return None, 0
    # hang tram: 'X trăm [Y...]'
    if tokens[0] in _UNITS and len(tokens) >= 2 and tokens[1] == 'trăm':
        tram = _UNITS[tokens[0]] * 100
        rest = tokens[2:]
        if rest and rest[0] in ('linh', 'lẻ') and len(rest) >= 2 and rest[1] in _UNITS:
            return tram + _UNITS[rest[1]], 4
        v, n = _parse_under_100(rest)
        if v is not None:
            return tram + v, 2 + n
        return tram, 2
    v, n = _parse_under_100(tokens)
    return v, n


# Cum regex thuong gap trong episode.md that (KHONG bia them pattern chua thay)
_NUM_WORD_PATTERN = r'(?:không|một|mốt|hai|ba|bốn|tư|năm|lăm|nhăm|sáu|bảy|bẩy|tám|chín|mười|mươi|trăm|linh|lẻ)'
RE_YEARS_AGO = re.compile(
    rf'((?:{_NUM_WORD_PATTERN}\s*){{1,4}})năm trước', re.IGNORECASE)
RE_AGE = re.compile(
    rf'((?:{_NUM_WORD_PATTERN}\s*){{1,4}})tuổi', re.IGNORECASE)
RE_LIVED_YEARS = re.compile(
    rf'sống\s+((?:{_NUM_WORD_PATTERN}\s*){{1,4}})năm', re.IGNORECASE)


def extract_years_ago(text):
    """Tra list (value:int, matched_text:str, span) cho moi cum 'X năm trước' parse duoc."""
    out = []
    for m in RE_YEARS_AGO.finditer(text):
        v, n = parse_vn_number(m.group(1))
        if v is not None:
            out.append((v, m.group(0), m.span()))
    return out


def extract_ages(text):
    out = []
    for m in RE_AGE.finditer(text):
        v, n = parse_vn_number(m.group(1))
        if v is not None and 0 < v <= 130:  # tuoi nguoi hop ly, chong false-positive so khac
            out.append((v, m.group(0), m.span()))
    return out


def extract_lived_years(text):
    out = []
    for m in RE_LIVED_YEARS.finditer(text):
        v, n = parse_vn_number(m.group(1))
        if v is not None:
            out.append((v, m.group(0), m.span()))
    return out


if __name__ == '__main__':
    # test qua dung pipeline regex-extraction (khong goi parse_vn_number tren
    # ca cum co hau to 'trước'/'tuổi' — do la loi dung sai, khong phai API that)
    years_ago_tests = [
        ('mười năm trước', 10), ('hai mươi năm trước', 20),
        ('mười năm trước — tôi hai mốt tuổi', 10),
    ]
    for s, expected in years_ago_tests:
        r = extract_years_ago(s)
        got = r[0][0] if r else None
        status = 'OK' if got == expected else f'FAIL (got {got})'
        print(f'years_ago {s!r} -> {got} (expect {expected}) [{status}]')

    age_tests = [
        ('ba mươi mốt tuổi', 31), ('ba mươi tám tuổi', 38),
        ('hai mốt tuổi', 21), ('năm mươi tám tuổi', 58),
    ]
    for s, expected in age_tests:
        r = extract_ages(s)
        got = r[0][0] if r else None
        status = 'OK' if got == expected else f'FAIL (got {got})'
        print(f'age {s!r} -> {got} (expect {expected}) [{status}]')

    lived_tests = [('sống mười năm', 10), ('sống sáu mươi năm', 60)]
    for s, expected in lived_tests:
        r = extract_lived_years(s)
        got = r[0][0] if r else None
        status = 'OK' if got == expected else f'FAIL (got {got})'
        print(f'lived {s!r} -> {got} (expect {expected}) [{status}]')
