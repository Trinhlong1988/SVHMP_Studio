"""SVHMP — Story Consistency Validator (Boss 1/7, nhom 'Story Consistency' phan bien.txt).

Khoa cross-episode: 1 nhan vat KHONG duoc doi field da khoa giua cac tap
(khong doi ten/tuoi/gioi/que/nghe/id). Chong mau thuan xuyen suot du an.
So voi baseline (lan dinh danh dau) -> flag moi thay doi.
"""
from __future__ import annotations

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


if __name__ == '__main__':
    b = {'character_id': 'PAS_0013', 'full_name': 'Hạ Diệu', 'gender': 'nu',
         'hometown': 'Huế', 'occupation': 'giáo viên', 'age_group': '18-25'}
    print("same:", validate_consistency(b, dict(b)))
    print("changed nghe:", validate_consistency(b, {**b, 'occupation': 'bác sĩ'}))
    print("changed que:", validate_consistency(b, {**b, 'hometown': 'Hà Nội'}))

    eb = {'event_id': 'EVT_001', 'thoi_diem': 'tám năm trước', 'nguyên_nhân': 'tai nạn'}
    print("event same:", validate_event_consistency(eb, dict(eb)))
    print("event changed:", validate_event_consistency(
        eb, {**eb, 'thoi_diem': 'mười năm trước'}))

    print("object jump unexplained:", validate_object_state_transition(
        'OBJ_AO_LEN_NAU', 'rách', 'lành', nearby_text='Cô mặc áo, lành lặn.'))
    print("object jump explained:", validate_object_state_transition(
        'OBJ_AO_LEN_NAU', 'rách', 'lành', nearby_text='Cô đã vá lại áo cẩn thận.'))
