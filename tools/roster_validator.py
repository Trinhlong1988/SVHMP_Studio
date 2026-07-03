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
  C4 naming region/generation/culture (rule_06..08): PENDING_SCHEMA — chờ Mr.Long
     ký bible/23 v1.1 (governance/blueprint/schemas/proposals/naming_extension_rules.yaml)
  C5 reveal_permission↔knowledge + arc↔state machine: PENDING_SCHEMA — chờ ký
     bible/37 v2 (governance/blueprint/schemas/proposals/character_ext_schema.yaml)

Exit: violation (C1-C3) -> 1; sạch -> 0. PENDING_SCHEMA in rõ SKIP + lý do
(KHÔNG đếm là pass ngầm). --strict: WARN-class cũng fail (B4 bật khi fill đạt ngưỡng
Tier1 100% / Tier2 >=90% / recurring 100%).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml

from migrate_roster_v2 import HOME  # single-source map vùng->quê hợp lệ

SVHMP = Path(__file__).parent.parent
ROSTER = SVHMP / 'runtime' / 'passenger_roster_100.yaml'
NAMES_DB = SVHMP / 'data' / 'vietnamese_names_extended.yaml'

TIER1_TOP = ['char_name', 'gender', 'regret_sub_archetype', 'haunting_symbol']
VOICE_REQ = ['region_dialect', 'hometown', 'pronoun_system']


def load_forbidden():
    db = yaml.safe_load(NAMES_DB.read_text(encoding='utf-8'))
    return {i['syl'] for i in db.get('forbidden_words', [])}


def validate(passengers, forbidden):
    """Trả (violations, warns). Mỗi item: 'Cx pas_id: mô tả'."""
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

    return violations, warns


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--roster', default=str(ROSTER))
    ap.add_argument('--strict', action='store_true',
                    help='WARN-class cũng fail (B4 bật khi fill đạt ngưỡng)')
    args = ap.parse_args(argv)

    data = yaml.safe_load(Path(args.roster).read_text(encoding='utf-8'))
    passengers = data.get('passengers', [])
    violations, warns = validate(passengers, load_forbidden())

    print("=== ROSTER VALIDATOR (G2 B3) ===")
    print(f"  roster: {args.roster} ({len(passengers)} passenger)")
    for v in violations:
        print(f"  [FAIL] {v}")
    for w in warns:
        print(f"  [WARN] {w}")
    print(f"  C1 naming + C2 quê↔giọng + C3 tier1: {len(violations)} violation, {len(warns)} warn")
    print("  [SKIP] C4 naming region/generation/culture — PENDING_SCHEMA "
          "(chờ Mr.Long ký bible/23 v1.1; đề xuất: governance/blueprint/schemas/proposals/naming_extension_rules.yaml)")
    print("  [SKIP] C5 reveal_permission↔knowledge + arc↔BP4 state machine — PENDING_SCHEMA "
          "(chờ Mr.Long ký bible/37 v2; đề xuất: governance/blueprint/schemas/proposals/character_ext_schema.yaml)")

    fail = bool(violations) or (args.strict and bool(warns))
    print(f"=== {'FAIL' if fail else 'PASS (trong phạm vi C1-C3 hiện hành)'} ===")
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
