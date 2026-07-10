"""audit ML #20 (10/7) — episode_schema.yaml rang buoc enum/range/const KHONG co test doi chieu
GIA TRI thuc te. Test cu (test_reality_frontmatter_has_every_schema_field_key) chi kiem TEN key.
Test nay doc schema + doi chieu tung field frontmatter THAT (build_episode_frontmatter(1)) voi
allowed_values/range/const/values enum - FAIL neu gia tri ngoai pham vi. Kem mutation-proof:
validator PHAI bat gia tri sai (driver_lines=5, bell_count ngoai [1,2]).
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))
import yaml
import episode_generator as eg

REPO = Path(__file__).parent.parent
SCHEMA_PATH = REPO / "governance" / "blueprint" / "schemas" / "episode_schema.yaml"


def _schema_fields():
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    return schema["schema"]["episode_frontmatter"]["fields"]


def _value_ok(value, spec):
    """True neu value hop le theo rang buoc spec (const/allowed_values/range/enum values)."""
    if not isinstance(spec, dict):
        return True
    if 'const' in spec:
        return value == spec['const']
    if 'allowed_values' in spec:
        return value in spec['allowed_values']
    if spec.get('type') == 'enum' and 'values' in spec:
        return value in spec['values']
    if 'range' in spec:
        lo, hi = spec['range']
        return isinstance(value, (int, float)) and lo <= value <= hi
    return True


def test_real_ep01_frontmatter_values_within_schema_constraints():
    fields = _schema_fields()
    fm = eg.build_episode_frontmatter(1)
    violations = []
    for name, spec in fields.items():
        if name not in fm:
            continue  # thieu key = test khac lo (test_reality_frontmatter_has_every_schema_field_key)
        if not _value_ok(fm[name], spec):
            violations.append((name, fm[name], spec))
    assert not violations, f"frontmatter EP01 co gia tri ngoai rang buoc schema: {violations}"


def test_validator_catches_out_of_range_values():
    # mutation-proof: validator PHAI bat gia tri sai (neu khong, test that o tren vo nghia)
    fields = _schema_fields()
    assert not _value_ok(5, fields['driver_lines']), "driver_lines=5 ngoai allowed_values [2,3] phai bi bat"
    assert not _value_ok(0, fields['ghost_manifest']), "ghost_manifest=0 khac const 1 phai bi bat"
    assert not _value_ok(99, fields['ep_number']), "ep_number=99 ngoai range [1,90] phai bi bat"
    assert not _value_ok('khong_ton_tai', fields['phase']), "phase ngoai enum phai bi bat"
    # va gia tri dung PHAI qua
    assert _value_ok(2, fields['driver_lines'])
    assert _value_ok(1, fields['ghost_manifest'])
    assert _value_ok(1, fields['ep_number'])
    assert _value_ok('introductory', fields['phase'])
