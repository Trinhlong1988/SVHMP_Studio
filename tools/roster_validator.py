"""SVHMP — G2 B3: ROSTER VALIDATOR (TASK_G2_CHARACTER, Mr.Long duyệt 3/7).

Validate runtime/passenger_roster_100.yaml (nguồn LOCK) — KHÔNG trùng tool cũ:
- character_manager: completeness gate per-episode (audit_gate facet)
- dialog_voice_validator: per-dialog giọng/xưng hô
- story_consistency_validator: cross-episode field lock
- character_balance_report: cân bằng target
=> roster_validator: tính hợp lệ NỘI TẠI roster theo bible/23 + R210 quê↔giọng.

CHECKS:
  C1 naming bible/23: rule_01 2-âm-tiết · rule_02 word-uniqueness toàn cục ·
     rule_04 không chứa 'Nam' · forbidden 15 từ (data/vietnamese_names_extended.yaml)
  C2 quê↔giọng: voice.hometown PHẢI thuộc vùng voice.region_dialect
     (map HOME single-source từ tools/migrate_roster_v2.py — không nhân đôi)
  C3 Tier1 R210 hiện diện: char_name/gender/voice đủ field/death.type/haunting_symbol/regret
  C4 naming region/generation/culture (rule_06..09, bible/23 v1.1 — Mr.Long ký
     2026-07-03): KHUNG check — bible/23 v1.1 phải có đủ 4 rule + roster region
     dùng phải có style_by_region khai (structural). Pool cụ thể theo vùng CHƯA
     ký (riêng hybrid classification, PING) — KHÔNG kiểm content-pool tới khi ký.
  C4b rule_09 vietnamese_purity CONTENT-CHECK (Mr.Long lệnh 4/7, sau C4 landed
     chỉ structural): charset Unicode-range (Latin-1 Supplement + Extended-A/B +
     Extended Additional — phủ mọi tổ hợp dấu Việt) + blacklist tên lai/game/
     teencode trên CHÍNH char_name — machine-checkable thật, không cần pool
     (khác C4 rule_06-08 vẫn chờ pool). "Jenny Trần" phải FAIL.
  C5 knowledge↔reveal_permission (bible/37 v2.1 — Mr.Long ký 2026-07-03): bible
     phải có đủ g2_extension section; MỌI passenger có fact secrecy=secret PHẢI
     có entry reveal_permission tương ứng (hiện roster CHƯA có field per-passenger
     này — B3 fill sẽ thêm; 0 passenger có field = 0 violation, gate SẴN SÀNG
     khi B3 đổ dữ liệu, KHÔNG phải giả PASS).

Exit: violation (C1-C5) -> 1; sạch -> 0. --strict: WARN-class cũng fail (B4 bật
khi fill đạt ngưỡng Tier1 100% / Tier2 >=90% / recurring 100%).
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml

from migrate_roster_v2 import HOME  # single-source map vùng->quê hợp lệ

SVHMP = Path(__file__).parent.parent
ROSTER = SVHMP / 'runtime' / 'passenger_roster_100.yaml'
NAMES_DB = SVHMP / 'data' / 'vietnamese_names_extended.yaml'
BIBLE_23 = SVHMP / 'bible' / '23_passenger_naming.yaml'
BIBLE_37 = SVHMP / 'bible' / '37_character_schema.yaml'

TIER1_TOP = ['char_name', 'gender', 'regret_sub_archetype', 'haunting_symbol']
VOICE_REQ = ['region_dialect', 'hometown', 'pronoun_system']
NAMING_RULES_REQUIRED = ['rule_06_region_match', 'rule_07_generation_match',
                         'rule_08_culture_belief', 'rule_09_vietnamese_purity']

# C4b rule_09 (vietnamese_purity, content-check thật — Mr.Long lenh 4/7): charset
# dung UNICODE CODEPOINT RANGE (khong liet ke tay tung ky tu — lan dau liet ke tay
# bo sot 'ú'/'ý' lam false-positive 'Phú Quý'/'Ánh Thúy', da fix bang range) —
# Latin-1 Supplement (À-ÿ) + Extended-A/B (Ā-ɏ, phu ơ/ư) + Extended Additional
# (Ḁ-ỿ, phu to hop dau VN: sac/huyen/hoi/nga/nang). KHONG dung range tho À-ỿ vi
# se lot ca Cyrillic/Hy Lap nam giua 2 block Latin do.
_VN_CHARSET_RE = re.compile(r"^[A-Za-zÀ-ÿĀ-ɏḀ-ỿ\s]+$")
_LAI_GAME_PATTERNS = [
    r'\b(jenny|kevin|kelly|amy|david|john|mary|anna)\b',   # ten lai pho bien
    r'\b(dragon|zed|shadow|blade|phoenix|angel|devil)\b',   # ten game/phi thuc
    r'\d',                                                   # teencode so xen chu
]


def check_vietnamese_purity_content(name):
    """C4b rule_09: FAIL-class content-check that tren char_name. Tra list ly do
    (rong = sach)."""
    reasons = []
    if not _VN_CHARSET_RE.match(name or ''):
        reasons.append('charset ngoai bang chu cai Viet (nghi ten lai/ky tu la)')
    low = (name or '').lower()
    for pat in _LAI_GAME_PATTERNS:
        if re.search(pat, low):
            reasons.append(f'khop pattern lai/game/teencode cam ({pat})')
    return reasons


def check_c4b_vietnamese_purity(passengers):
    """C4b — content-check rule_09 tren TOAN BO passenger (khac C4 structural)."""
    errs = []
    for p in passengers:
        pid = p.get('id', '?')
        name = p.get('char_name', '') or ''
        for reason in check_vietnamese_purity_content(name):
            errs.append(f"C4b {pid}: '{name}' vi phạm rule_09 vietnamese_purity — {reason}")
    return errs


def load_forbidden():
    db = yaml.safe_load(NAMES_DB.read_text(encoding='utf-8'))
    return {i['syl'] for i in db.get('forbidden_words', [])}


def load_bible23():
    return yaml.safe_load(BIBLE_23.read_text(encoding='utf-8'))


def load_bible37():
    return yaml.safe_load(BIBLE_37.read_text(encoding='utf-8'))


def check_c4_naming_framework(bible23, passengers):
    """C4 — khung naming region/generation/culture/vietnamese (bible/23 v1.1)."""
    errs = []
    v = str((bible23 or {}).get('version', ''))
    if not v.startswith('1.1'):
        errs.append(f"C4: bible/23 version '{v}' chưa v1.1 (naming framework chưa ký)")
        return errs
    rules = (bible23 or {}).get('RULES', {})
    for rid in NAMING_RULES_REQUIRED:
        if rid not in rules:
            errs.append(f"C4: thiếu {rid} trong bible/23 v1.1")
    style = (rules.get('rule_06_region_match') or {}).get('style_by_region', {})
    for p in passengers:
        region = (p.get('voice') or {}).get('region_dialect')
        if region and region not in style:
            errs.append(f"C4 {p.get('id', '?')}: vùng '{region}' dùng trong roster "
                        "nhưng bible/23 rule_06 chưa khai style_by_region")
    return errs


def check_c5_knowledge_consistency(bible37, passengers):
    """C5 — bible/37 v2.1 g2_extension đủ section + per-passenger knowledge↔reveal_permission."""
    errs = []
    v = str((bible37 or {}).get('meta', {}).get('version', ''))
    if not v.startswith('2.1'):
        errs.append(f"C5: bible/37 version '{v}' chưa v2.1 (g2_extension chưa ký)")
        return errs
    g2 = (bible37 or {}).get('g2_extension', {})
    for key in ('knowledge', 'reveal_permission', 'continuity_risk'):
        if key not in g2:
            errs.append(f"C5: thiếu section g2_extension.{key} trong bible/37 v2.1")
    for p in passengers:
        pid = p.get('id', '?')
        knowledge = p.get('knowledge') or []
        secret_ids = {k['fact_id'] for k in knowledge
                      if k.get('secrecy') == 'secret' and k.get('fact_id')}
        perm_ids = {rp.get('fact_id') for rp in (p.get('reveal_permission') or [])}
        missing = secret_ids - perm_ids
        if missing:
            errs.append(f"C5 {pid}: fact secret {sorted(missing)} thiếu reveal_permission entry")
    return errs


def validate(passengers, forbidden, bible23=None, bible37=None):
    """Trả (violations, warns). Mỗi item: 'Cx pas_id: mô tả'.
    bible23/bible37 None -> bỏ qua C4/C5 (tương thích test C1-C3 cũ)."""
    violations, warns = [], []
    word_owner = {}
    for p in passengers:
        pid = p.get('id', '?')
        name = p.get('char_name', '') or ''
        words = name.split()

        # C1 naming
        if len(words) < 2:
            violations.append(f"C1 {pid}: '{name}' vi phạm rule_01 (<2 âm tiết)")
        for w in words:
            if w == 'Nam':
                violations.append(f"C1 {pid}: '{name}' chứa 'Nam' (rule_04 recurring collision)")
            if w in forbidden:
                violations.append(f"C1 {pid}: '{name}' chứa từ cấm '{w}' (Mr.Long 27/6)")
            if w in word_owner:
                violations.append(
                    f"C1 {pid}: '{name}' trùng âm tiết '{w}' với '{word_owner[w]}' (rule_02)")
            else:
                word_owner[w] = name

        # C2 quê↔giọng
        voice = p.get('voice') or {}
        region = voice.get('region_dialect', '')
        home = voice.get('hometown', '')
        if region and region not in HOME:
            violations.append(f"C2 {pid}: region_dialect '{region}' không thuộc {sorted(HOME)}")
        elif region and home and home not in HOME[region]:
            violations.append(f"C2 {pid}: quê '{home}' KHÔNG khớp vùng giọng '{region}' (R210)")

        # C3 Tier1 R210
        for field in TIER1_TOP:
            if not p.get(field):
                violations.append(f"C3 {pid}: thiếu tier_1 field '{field}'")
        for vf in VOICE_REQ:
            if not voice.get(vf):
                violations.append(f"C3 {pid}: thiếu voice.{vf}")
        death = p.get('death') or {}
        if not death.get('type'):
            violations.append(f"C3 {pid}: thiếu death.type")
        if not p.get('age_range') and p.get('life_status') != 'linh_hon':
            warns.append(f"C3 {pid}: age_range trống (chỉ hợp lệ với linh_hon)")

    if bible23 is not None:
        violations += check_c4_naming_framework(bible23, passengers)
    violations += check_c4b_vietnamese_purity(passengers)
    if bible37 is not None:
        violations += check_c5_knowledge_consistency(bible37, passengers)

    return violations, warns


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--roster', default=str(ROSTER))
    ap.add_argument('--strict', action='store_true',
                    help='WARN-class cũng fail (B4 bật khi fill đạt ngưỡng)')
    args = ap.parse_args(argv)

    data = yaml.safe_load(Path(args.roster).read_text(encoding='utf-8'))
    passengers = data.get('passengers', [])
    bible23, bible37 = load_bible23(), load_bible37()
    violations, warns = validate(passengers, load_forbidden(), bible23, bible37)

    print("=== ROSTER VALIDATOR (G2 B3) ===")
    print(f"  roster: {args.roster} ({len(passengers)} passenger)")
    for v in violations:
        print(f"  [FAIL QA1001] {v}")
    for w in warns:
        print(f"  [WARN QA1001] {w}")
    print(f"  C1-C5 (naming + quê↔giọng + tier1 + naming-framework + rule_09-content + "
          f"knowledge↔reveal): {len(violations)} violation, {len(warns)} warn")

    fail = bool(violations) or (args.strict and bool(warns))
    print(f"=== {'FAIL' if fail else 'PASS (C1-C5)'} ===")
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
