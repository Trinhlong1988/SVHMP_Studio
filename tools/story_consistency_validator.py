"""SVHMP — Story Consistency Validator (Boss 1/7, nhom 'Story Consistency' phan bien.txt).

Khoa cross-episode: 1 nhan vat KHONG duoc doi field da khoa giua cac tap
(khong doi ten/tuoi/gioi/que/nghe/id). Chong mau thuan xuyen suot du an.
So voi baseline (lan dinh danh dau) -> flag moi thay doi.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Field KHOA — bible/37 story_consistency + Canon Lock (phan bien.txt module 6)
# Vinh vien KHONG doi: id/ten/gioi/nam sinh/tuoi/que/nghe/giong/cha me/ngay chet/loai chet/noi dau/cau cua mieng
LOCKED_FIELDS = ('character_id', 'full_name', 'gender', 'date_of_birth',
                 'age_group', 'hometown', 'occupation', 'region_dialect',
                 'parents', 'death_date', 'death_type', 'pain_core', 'catchphrase')


def _n(x): return (str(x).strip().lower()) if x not in (None, '') else ''


def validate_consistency(baseline: dict, current: dict) -> list:
    """Tra ve list issue neu current DOI field khoa so voi baseline."""
    issues = []
    if _n(baseline.get('character_id')) and _n(current.get('character_id')) \
            and _n(baseline['character_id']) != _n(current['character_id']):
        issues.append({'code': 'ID_MISMATCH', 'was': baseline.get('character_id'),
                       'now': current.get('character_id')})
        return issues  # khac id -> khong so tiep
    for f in LOCKED_FIELDS:
        if f == 'character_id':
            continue
        b, c = _n(baseline.get(f)), _n(current.get(f))
        if b and c and b != c:
            issues.append({'code': 'LOCKED_FIELD_CHANGED', 'field': f,
                           'was': baseline.get(f), 'now': current.get(f)})
    return issues


def validate_against_registry(reg, char_id: str, current: dict) -> list:
    """So current voi profile da load trong registry (baseline)."""
    base = reg.get(char_id)
    if base is None:
        return [{'code': 'UNKNOWN_ID', 'id': char_id}]
    import dataclasses
    bd = dataclasses.asdict(base) if dataclasses.is_dataclass(base) else dict(base)
    bd.setdefault('character_id', base.id)
    bd.setdefault('full_name', base.char_name)
    bd.setdefault('age_group', base.age_range)
    return validate_consistency(bd, current)


# ============================================================
# G4 D4 (TASK_G4_WORLD) — mo rong R207 sang 2 field-lock MOI: su kien + do vat.
# GOP vao module nay (KHONG tach pack rieng — da co R207 lam nen, dung ham
# validate_consistency() chung, chi doi LOCKED_FIELDS cho tung loai entity).
# ============================================================

# Su kien: thoi diem/nguyen nhan KHONG doi giua cac tap nhac lai CUNG 1 su kien
# (khac character: su kien khong co "tuoi/nghe" ma co thoi_diem/nguyen_nhan).
EVENT_LOCKED_FIELDS = ('event_id', 'thoi_diem', 'nguyen_nhan')

# Do vat: vi tri/tinh trang — LUU Y day KHONG phai "khong bao gio doi" (do vat
# co the doi chu/hong theo tap, hop le) — day la check RIENG: phat hien nhay
# VO LY (vd "ao rach" -> "ao lanh" giua 2 dong LIEN KE, KHONG co su kien vá/sửa
# duoc nhac toi giai thich chuyen doi).
OBJECT_STATE_TRANSITIONS_NEED_EXPLANATION = {
    # (trang_thai_truoc, trang_thai_sau): tu-khoa giai thich hop le neu co mat gan do
    ('rách', 'lành'): ['vá', 'sửa', 'may lại', 'thay mới'],
    ('vỡ', 'lành'): ['dán', 'sửa', 'thay mới'],
    ('mất', 'còn'): ['tìm thấy', 'trả lại', 'nhặt được'],
}


def validate_event_consistency(baseline: dict, current: dict) -> list:
    """D4: khoa su kien — thoi_diem/nguyen_nhan KHONG doi giua cac lan nhac lai
    CUNG 1 event_id xuyen tap. Mirror validate_consistency() (character) nhung
    dung EVENT_LOCKED_FIELDS."""
    issues = []
    if _n(baseline.get('event_id')) and _n(current.get('event_id')) \
            and _n(baseline['event_id']) != _n(current['event_id']):
        issues.append({'code': 'EVENT_ID_MISMATCH', 'was': baseline.get('event_id'),
                       'now': current.get('event_id')})
        return issues
    for f in EVENT_LOCKED_FIELDS:
        if f == 'event_id':
            continue
        b, c = _n(baseline.get(f)), _n(current.get(f))
        if b and c and b != c:
            issues.append({'code': 'EVENT_LOCKED_FIELD_CHANGED', 'field': f,
                           'was': baseline.get(f), 'now': current.get(f)})
    return issues


def validate_object_state_transition(obj_id: str, state_before: str, state_after: str,
                                     nearby_text: str = '') -> list:
    """D4: phat hien do vat doi trang thai VO LY giua 2 lan xuat hien LIEN KE
    ma KHONG co tu-khoa giai thich (va/sua/thay moi...) trong van ban gan do.
    KHAC voi character/event lock (khong phai 'vinh vien khong doi' — do vat
    duoc PHEP doi, chi CAM nhay vo ly khong giai thich)."""
    issues = []
    key = (_n(state_before), _n(state_after))
    if key in OBJECT_STATE_TRANSITIONS_NEED_EXPLANATION:
        allowed_words = OBJECT_STATE_TRANSITIONS_NEED_EXPLANATION[key]
        text_low = nearby_text.lower()
        if not any(w in text_low for w in allowed_words):
            issues.append({'code': 'OBJECT_STATE_JUMP_UNEXPLAINED', 'object': obj_id,
                           'was': state_before, 'now': state_after,
                           'expected_explanation_keywords': allowed_words})
    return issues


# ============================================================
# G5-3 (10/7, per Mr.Long authorization, TASK_AUDIT_HIGH_G2_G8.md) — thuc thi that
# cam ket DA KY trong governance/blueprint/schemas/character_ext_schema.yaml:99
# ("validator: story_consistency_validator.py doi chieu 2 chieu, lech = FAIL") va
# bible/37_character_schema.yaml:126 ("entity_class=linh_hon PHAI khop life_status=
# linh_hon", da doi ten tu alive_status theo DEBT-011). Truoc do KHONG co ham nao
# lam viec nay - claim gia, chi la text mo ta trong schema.
# ============================================================
ENTITY_CLASS_DEFAULT = 'nguoi'      # bible/37 g5_extension.entity_class.default
ENTITY_CLASS_LINH_HON = 'linh_hon'
LIFE_STATUS_LINH_HON = 'linh_hon'   # bible/37 tier_1_mandatory.core_id life_status (DEBT-011)


def validate_entity_class_life_status(passengers: list) -> list:
    """Doi chieu 2 CHIEU dung loi hua da ky: entity_class=linh_hon <-> life_status=
    linh_hon. Field entity_class vang mat dung DUNG default cua schema ('nguoi').

    passengers: list dict THO tu runtime/passenger_roster_100.yaml['passengers']
    (doc THANG, KHONG qua CharacterRegistry/CharacterProfile - entity_class CHUA
    duoc khai lam dataclass field trong tools/character_manager.py nen se bi loc
    mat neu di qua do; tranh dung cham character_manager.py ngoai pham vi duoc
    giao boi G5-3, chi sua story_consistency_validator.py nhu task yeu cau)."""
    issues = []
    for p in passengers:
        entity_class = p.get('entity_class') or ENTITY_CLASS_DEFAULT
        life_status = p.get('life_status', '')
        ec_linh_hon = entity_class == ENTITY_CLASS_LINH_HON
        ls_linh_hon = life_status == LIFE_STATUS_LINH_HON
        if ec_linh_hon != ls_linh_hon:
            issues.append({'code': 'ENTITY_CLASS_LIFE_STATUS_MISMATCH', 'id': p.get('id', '?'),
                           'entity_class': entity_class, 'life_status': life_status})
    return issues


def _self_check_entity_class_life_status():
    """Mutation-proof tren du lieu TONG HOP (khong dung real roster de quyet PASS/
    FAIL dieu kien code - 47/139 passenger THAT co life_status=linh_hon nhung 0/139
    khai entity_class=linh_hon (field moi tu G5 extension 5/7 chua duoc backfill,
    xem governance/TECH_DEBT.md DEBT-016) - day la khoang trong DATA co san, KHONG
    phai loi CODE moi, nen KHONG duoc lam self-check nay tu sys.exit(1))."""
    clean = [{'id': 'PAS_TEST1', 'entity_class': 'nguoi', 'life_status': 'song'},
             {'id': 'PAS_TEST2', 'entity_class': 'linh_hon', 'life_status': 'linh_hon'}]
    clean_issues = validate_entity_class_life_status(clean)
    if clean_issues:
        print(f"[G5-3 self-check] FAIL: du lieu tong hop SACH van bi bao issue: {clean_issues}")
        sys.exit(1)

    mismatched = [{'id': 'PAS_TEST3', 'entity_class': 'linh_hon', 'life_status': 'song'}]
    mismatched_issues = validate_entity_class_life_status(mismatched)
    if not any(i.get('code') == 'ENTITY_CLASS_LIFE_STATUS_MISMATCH' for i in mismatched_issues):
        print(f"[G5-3 self-check] FAIL: entity_class=linh_hon + life_status=song (lech ro rang) "
              f"KHONG bi bat: {mismatched_issues}")
        sys.exit(1)

    reverse_mismatched = [{'id': 'PAS_TEST4', 'entity_class': 'nguoi', 'life_status': 'linh_hon'}]
    reverse_issues = validate_entity_class_life_status(reverse_mismatched)
    if not any(i.get('code') == 'ENTITY_CLASS_LIFE_STATUS_MISMATCH' for i in reverse_issues):
        print(f"[G5-3 self-check] FAIL: life_status=linh_hon + entity_class=nguoi (lech CHIEU "
              f"NGUOC, dung tinh than '2 chieu' da ky) KHONG bi bat: {reverse_issues}")
        sys.exit(1)

    print("[G5-3 self-check] PASS: validate_entity_class_life_status() bat dung ca 2 "
          "chieu lech tren du lieu tong hop")

    import yaml
    roster_path = Path(__file__).resolve().parent.parent / 'runtime' / 'passenger_roster_100.yaml'
    real = yaml.safe_load(roster_path.read_text(encoding='utf-8')) or {}
    real_issues = validate_entity_class_life_status(real.get('passengers', []))
    print(f"[G5-3 real-data report] {len(real_issues)} passenger co entity_class/life_status "
          "lech tren roster THAT (KHONG chan build - khoang trong BACKFILL DATA da biet tu "
          "G5 extension 5/7, xem governance/TECH_DEBT.md DEBT-016, KHONG phai loi code moi)")


def _self_check_validate_against_registry():
    """G2-2 (10/7, per Mr.Long authorization, TASK_AUDIT_HIGH_G2_G8.md): validate_against_
    registry() truoc day 0 caller - __main__ chi print(), khong sys.exit() theo ket qua, nen
    g4_world_check.py D4 (goi script nay qua subprocess, chi kiem exit code) LUON PASS du logic
    co chay hay khong. Ham nay goi THAT validate_against_registry() tren du lieu roster THAT
    (khong mock) + tu mutate 1 field khoa (gender) -> BAT BUOC phat hien duoc, neu khong tu
    sys.exit(1) - bien D4 thanh gate THAT (khong chi smoke-test)."""
    sys.path.insert(0, str(Path(__file__).parent))
    from character_manager import CharacterRegistry
    import dataclasses

    reg = CharacterRegistry()
    real_id = next((c.id for c in reg.all('passenger')), None)
    if real_id is None:
        print("[D4 self-check] KHONG tim thay passenger nao trong roster - SKIP (khong co du lieu de kiem)")
        return

    base = reg.get(real_id)
    bd = dataclasses.asdict(base)
    bd.setdefault('character_id', base.id)
    bd.setdefault('full_name', base.char_name)
    bd.setdefault('age_group', base.age_range)

    clean_issues = validate_against_registry(reg, real_id, dict(bd))
    if clean_issues:
        print(f"[D4 self-check] FAIL: du lieu SACH (khong doi gi) van bi bao issue: {clean_issues}")
        sys.exit(1)

    mutated = dict(bd)
    mutated['gender'] = 'nam' if bd.get('gender') != 'nam' else 'nu'
    mutated_issues = validate_against_registry(reg, real_id, mutated)
    if not any(i.get('code') == 'LOCKED_FIELD_CHANGED' and i.get('field') == 'gender'
               for i in mutated_issues):
        print(f"[D4 self-check] FAIL: doi 'gender' (field khoa) nhung validate_against_registry() "
              f"KHONG bat duoc - enforcement rong: {mutated_issues}")
        sys.exit(1)

    print(f"[D4 self-check] PASS: validate_against_registry() tren {real_id} - "
          f"du lieu sach = 0 issue, gender-mutation = bat duoc dung LOCKED_FIELD_CHANGED")


if __name__ == '__main__':
    b = {'character_id': 'PAS_0013', 'full_name': 'Hạ Diệu', 'gender': 'nu',
         'hometown': 'Huế', 'occupation': 'giáo viên', 'age_group': '18-25'}
    print("same:", validate_consistency(b, dict(b)))
    print("changed nghe:", validate_consistency(b, {**b, 'occupation': 'bác sĩ'}))
    print("changed que:", validate_consistency(b, {**b, 'hometown': 'Hà Nội'}))

    # G2-3 (10/7, per Mr.Long authorization): key dung 'nguyen_nhan' (khong dau) khop
    # EVENT_LOCKED_FIELDS - truoc day dung 'nguyên_nhân' (co dau) nen nhanh kiem khoa nay
    # (1/3 EVENT_LOCKED_FIELDS) chua tung thuc su chay trong self-test (lech chinh ta).
    eb = {'event_id': 'EVT_001', 'thoi_diem': 'tám năm trước', 'nguyen_nhan': 'tai nạn'}
    print("event same:", validate_event_consistency(eb, dict(eb)))
    print("event changed thoi_diem:", validate_event_consistency(
        eb, {**eb, 'thoi_diem': 'mười năm trước'}))
    _changed_nn = validate_event_consistency(eb, {**eb, 'nguyen_nhan': 'oan khuất'})
    print("event changed nguyen_nhan:", _changed_nn)
    if not any(i.get('field') == 'nguyen_nhan' for i in _changed_nn):
        print("[D4 self-check] FAIL: doi 'nguyen_nhan' (event lock field) nhung "
              "validate_event_consistency() KHONG bat duoc")
        sys.exit(1)

    _self_check_validate_against_registry()
    _self_check_entity_class_life_status()
    print("=== story_consistency_validator D4 self-check: ALL PASS ===")

    print("object jump unexplained:", validate_object_state_transition(
        'OBJ_AO_LEN_NAU', 'rách', 'lành', nearby_text='Cô mặc áo, lành lặn.'))
    print("object jump explained:", validate_object_state_transition(
        'OBJ_AO_LEN_NAU', 'rách', 'lành', nearby_text='Cô đã vá lại áo cẩn thận.'))
