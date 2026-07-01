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


if __name__ == '__main__':
    b = {'character_id': 'PAS_0013', 'full_name': 'Hạ Diệu', 'gender': 'nu',
         'hometown': 'Huế', 'occupation': 'giáo viên', 'age_group': '18-25'}
    print("same:", validate_consistency(b, dict(b)))
    print("changed nghe:", validate_consistency(b, {**b, 'occupation': 'bác sĩ'}))
    print("changed que:", validate_consistency(b, {**b, 'hometown': 'Hà Nội'}))
