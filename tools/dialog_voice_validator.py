"""SVHMP — Dialog Voice Validator (Boss 1/7): kiem soat CHAT giong/vung mien cho SINH DIALOG.

Vi sao critical: tieng Viet 3 vung khac TU VUNG + TIEU TU + XUNG HO (khong chi accent).
Mot ba cu mien Bac, mot tai xe mien Tay, mot nu sinh do thi KHONG the noi giong nhau (Đúng.docx).

Cung cap:
- validate_profile(voice): kiem tra ho so giong DAY DU + NHAT QUAN (region<->quehuong<->xung ho<->tieu tu).
- validate_line(voice, line): kiem 1 cau thoai co RO RI phuong ngu / dung forbidden / xung ho sai vung khong.
Du lieu phuong ngu = sociolinguistics that (khong suy luan).
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
sys.path.insert(0, str(Path(__file__).parent))
from migrate_roster_v2 import HOME  # single-source map vung->que hop le (D1, per Mr.Long ky 5/7)

# ── Bang phuong ngu (marker DAC TRUNG, dung de bat ro ri) ──
REGIONS = {
    'bac':   {'pronouns': {'tôi', 'tớ', 'cậu', 'mày', 'tao', 'cháu', 'con', 'ông', 'bà'},
              'particles': {'nhé', 'nhỉ', 'đấy', 'cơ', 'ạ'},
              'lexicon': {'mẹ', 'bát', 'vào', 'thế', 'đâu'}},
    'trung': {'pronouns': {'tui', 'tau', 'mi', 'choa', 'con', 'o', 'mụ'},
              'particles': {'hè', 'hỉ', 'rứa', 'mô', 'tê', 'nờ'},
              'lexicon': {'mạ', 'tô', 'vô', 'rứa', 'mô', 'chi', 'tê'}},
    'nam':   {'pronouns': {'tui', 'tao', 'mày', 'tía', 'má', 'ba', 'con', 'cưng'},
              'particles': {'nghen', 'hén', 'hen', 'nè', 'ha'},
              'lexicon': {'má', 'chén', 'vô', 'hông', 'nè', 'dữ'}},
    'tay':   {'pronouns': {'tui', 'qua', 'bậu', 'tía', 'má', 'con'},
              'particles': {'nghen', 'hén', 'hông', 'ha'},
              'lexicon': {'má', 'vô', 'hông', 'dữ', 'bậu', 'trời đất'}},
    'do_thi': {'pronouns': {'tôi', 'mình', 'bạn', 'em', 'anh', 'chị'},
               'particles': {'nhé', 'ạ', 'thôi'},
               'lexicon': {'mẹ', 'ba', 'vào'}},
}
VALID_REGIONS = set(REGIONS)

# marker DOC QUYEN moi vung (dung phat hien ro ri — loai tu chung nhu 'tui','con','vô','má')
EXCLUSIVE = {
    'bac':   {'nhé', 'nhỉ', 'cơ', 'tớ', 'cậu'},
    'trung': {'rứa', 'mô', 'tê', 'hỉ', 'hè', 'mạ', 'mi', 'choa', 'chi', 'nờ'},
    'nam':   {'nghen', 'hén', 'nè', 'cưng'},
    'tay':   {'qua', 'bậu', 'trời đất'},
}

# quehuong -> vung (D1 SSOT reconcile, per Mr.Long ky 5/7): suy nguoc tu HOME (migrate_roster_v2,
# nguon that roster_validator.py dang dung cho C2 R210) — KHONG con hand-code rieng o day (truoc day
# 'hải dương' co trong HOME['bac'] nhung THIEU o day -> false negative cam lang, da phat hien qua audit).
HOMETOWN_REGION = {town.lower(): region for region, towns in HOME.items() for town in towns}

# 2 vung dialogue can nhung HOME (character roster, chi 3 vung bac/trung/nam) chua co — giu lam hang so
# PHU rieng cho dialogue, KHONG suy luan them que moi ngoai danh sach nay (TASK_G3_DIALOGUE.md D1).
EXTRA_REGIONS_DIALOGUE_ONLY = {
    'tay':   {'bến tre': 'tay', 'cần thơ': 'tay', 'an giang': 'tay', 'cà mau': 'tay',
              'đồng tháp': 'tay', 'vĩnh long': 'tay'},
    'do_thi': {},  # do_thi = giong khong gan 1 que cu the (dan nhap cu/gioi tre thanh thi), khong co bang que rieng
}
for _region, _towns in EXTRA_REGIONS_DIALOGUE_ONLY.items():
    HOMETOWN_REGION.update(_towns)

MANDATORY_VOICE = ('region_dialect', 'hometown', 'pronoun_system')  # dialogue-critical, PHAI co

# Dialogue Consistency (phan bien.txt module 4): nguoi gia KHONG noi tieng long hien dai
MODERN_SLANG = {'ok', 'okay', 'oke', 'bro', 'chill', 'vibe', 'deal', 'hi', 'hello',
                'wow', 'sorry', 'plan', 'style', 'auto', 'check', 'fine'}
ELDERLY_AGE = {'66+', 'elderly', 'nguoi_gia', '51-65', '56-65'}


def _norm(s): return (s or '').strip().lower()
def _tokens(line): return re.findall(r"[\wàáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]+", (line or '').lower())


def validate_profile(voice: dict) -> list:
    """Kiem ho so giong: mandatory + nhat quan region/quehuong/xung ho/tieu tu."""
    issues = []
    for f in MANDATORY_VOICE:
        if not _norm(voice.get(f)):
            issues.append({'code': 'MISSING_MANDATORY', 'field': f})
    region = _norm(voice.get('region_dialect')).split('_')[0]  # 'nam_saigon'->'nam'
    if region and region not in VALID_REGIONS:
        issues.append({'code': 'BAD_REGION', 'region': region})
        return issues
    # quehuong <-> region
    ht = _norm(voice.get('hometown'))
    if ht and ht in HOMETOWN_REGION and region and HOMETOWN_REGION[ht] != region:
        issues.append({'code': 'HOMETOWN_REGION_MISMATCH', 'hometown': ht,
                       'expected': HOMETOWN_REGION[ht], 'got': region})
    # xung ho hop vung
    if region:
        allowed = REGIONS[region]['pronouns']
        for p in (voice.get('pronoun_system') or '').replace('/', ' ').split():
            pl = _norm(p)
            # neu la marker DOC QUYEN cua vung KHAC -> sai
            for r2, ex in EXCLUSIVE.items():
                if r2 != region and pl in ex:
                    issues.append({'code': 'PRONOUN_WRONG_REGION', 'pronoun': pl, 'belongs': r2})
        # tieu tu hop vung
        for pt in (voice.get('particles') or []):
            for r2, ex in EXCLUSIVE.items():
                if r2 != region and _norm(pt) in ex:
                    issues.append({'code': 'PARTICLE_WRONG_REGION', 'particle': _norm(pt), 'belongs': r2})
    return issues


def validate_line(voice: dict, line: str) -> list:
    """Kiem 1 cau thoai: ro ri phuong ngu vung khac / dung forbidden."""
    issues = []
    region = _norm(voice.get('region_dialect')).split('_')[0]
    toks = set(_tokens(line))
    low = (line or '').lower()
    # forbidden words
    for fw in (voice.get('forbidden_words') or []):
        if _norm(fw) and _norm(fw) in toks:
            issues.append({'code': 'FORBIDDEN_WORD', 'word': _norm(fw)})
    # ro ri phuong ngu: cau chua marker doc quyen cua vung KHAC vung nhan vat
    if region in REGIONS:
        for r2, ex in EXCLUSIVE.items():
            if r2 == region:
                continue
            for m in ex:
                if (' ' in m and m in low) or (' ' not in m and m in toks):
                    issues.append({'code': 'DIALECT_LEAK', 'marker': m, 'belongs': r2, 'char_region': region})
    # Dialogue Consistency: nguoi gia noi tieng long hien dai -> sai (module 4)
    if _norm(voice.get('age_group')) in ELDERLY_AGE:
        for s in MODERN_SLANG:
            if s in toks:
                issues.append({'code': 'AGE_INAPPROPRIATE_SLANG', 'word': s, 'age': _norm(voice.get('age_group'))})
    return issues


def validate(voice: dict, line: str = None) -> list:
    out = validate_profile(voice)
    if line is not None:
        out += validate_line(voice, line)
    return out


def validate_generated_batch(voice: dict, lines: list) -> dict:
    """D4 (TASK_G3_DIALOGUE.md): kiem 1 loat cau DA SINH (vd batch output cua
    tools/dialogue_generator.py) qua validate_line() HIEN CO — chi loop + tong hop, KHONG
    viet lai logic phat hien (R211). Dung khi can check theo batch thay vi tung dong 1."""
    results = [{'line': ln, 'issues': validate_line(voice, ln)} for ln in lines]
    for r in results:
        r['ok'] = not r['issues']
    n_ok = sum(1 for r in results if r['ok'])
    return {'total': len(lines), 'ok': n_ok, 'failed': len(lines) - n_ok, 'results': results}


if __name__ == '__main__':
    import json
    demo = {'region_dialect': 'nam', 'hometown': 'Bến Tre', 'pronoun_system': 'tui/má',
            'particles': ['nghen'], 'forbidden_words': ['vãi']}
    print("profile issues:", validate_profile(demo))
    print("line OK:", validate_line(demo, "Má ơi, con dìa nghen."))
    print("line LEAK (bac 'nhé'):", validate_line(demo, "Con về nhé mẹ."))
