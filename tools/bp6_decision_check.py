"""BP6 DECISION CHECK v1.0.0 — gate máy cho BP6 Decision Architecture.

Check:
  1  DUP-KEY loader single-impl (import blueprint_constitution_check) + version
     khớp checker/contract/io (2 file bp6).
  2  contract: ĐÚNG 12 knob (máy đếm, khớp danh sách TASK đã đóng) · mỗi knob đủ
     field (knob_id/type/units/consumer/calibration_source/lifecycle/status) ·
     type ∈ {scalar, curve, enum} · scalar/curve phải có valid_range · enum phải
     có values HOẶC values_source.
  3  NO-HARDCODE (R195): key cấm (default/value/values_default/baseline/initial/
     fixed) trong knob = FAIL · số (int/float) trong knob CHỈ được nằm dưới key
     valid_range = FAIL nếu lạc chỗ khác (enum values chứa số = FAIL).
  4  consumer: mọi knob consumer.domain == generator, access == read_only —
     khớp reader grant decision_engine BP-C (blueprint_domains: [generator,
     qa_runtime]) · io.writer ⊆ {decision_engine, mr_long} (BP3 1-writer).
  5  io: packet per_scene.knobs.keys_must_equal trỏ đúng contract · required
     packet fields đủ (packet_id/ep_number/plan_ref/calibration_evidence/
     per_scene) · input.source_schema planned đủ 5 metadata · reader khớp BP0.

Exit 0 = PASS, exit 1 = FAIL.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402

__version__ = '1.0.0'

BP6 = REPO / 'governance' / 'blueprint' / 'bp6'
D_CONTRACT = BP6 / 'decision_contract.yaml'
D_IO = BP6 / 'decision_io.yaml'
D_BP0 = REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml'

# Danh sách 12 knob ĐÓNG theo TASK_BP6 (đổi = RFC + Mr.Long)
EXPECTED_KNOBS = ['dialogue_ratio', 'narration_ratio', 'emotion_curve', 'fear_curve',
                  'suspense_curve', 'reveal_curve', 'pacing', 'scene_budget',
                  'information_budget', 'silence_budget', 'character_focus', 'pov']
KNOB_REQUIRED_FIELDS = ['knob_id', 'type', 'units', 'consumer',
                        'calibration_source', 'lifecycle', 'status']
VALID_TYPES = {'scalar', 'curve', 'enum'}
FORBIDDEN_VALUE_KEYS = {'default', 'value', 'values_default', 'baseline',
                        'initial', 'fixed', 'preset'}
NUMERIC_ALLOWED_KEYS = {'valid_range'}   # số CHỈ được sống dưới key này (R195)
PLANNED_META = ['planned_path', 'owner', 'reason_not_exists_yet',
                'target_milestone', 'blocking_dependency']
PACKET_REQUIRED = ['packet_id', 'ep_number', 'plan_ref', 'calibration_evidence',
                   'per_scene']


def _load(path, errs, label):
    try:
        return load_yaml_no_dup(Path(path).read_text(encoding='utf-8'))
    except DupKeyError as e:
        errs.append(f'{label}: DUP-KEY — {e}')
    except Exception as e:
        errs.append(f'{label}: khong doc duoc: {e}')
    return None


def _numeric_leaks(node, path, allowed_parent=False):
    """R195: tra ve list vi tri co so nam NGOAI key duoc phep (valid_range)."""
    leaks = []
    if isinstance(node, bool):
        return leaks
    if isinstance(node, (int, float)):
        if not allowed_parent:
            leaks.append(path)
    elif isinstance(node, list):
        for i, x in enumerate(node):
            leaks.extend(_numeric_leaks(x, f'{path}[{i}]', allowed_parent))
    elif isinstance(node, dict):
        for k, v in node.items():
            leaks.extend(_numeric_leaks(
                v, f'{path}.{k}', allowed_parent or k in NUMERIC_ALLOWED_KEYS))
    return leaks


def check_contract(contract):
    """Check 2+3+4 tren dict contract. Tra ve list loi."""
    errs = []
    knobs = (contract or {}).get('knobs') or []
    ids = [k.get('knob_id') for k in knobs]
    missing = [k for k in EXPECTED_KNOBS if k not in ids]
    extra = [k for k in ids if k not in EXPECTED_KNOBS]
    if missing:
        errs.append(f'KNOB-THIEU: {missing}')
    if extra:
        errs.append(f'KNOB-LA (13th+): {extra} — them knob = RFC + Mr.Long')
    if len(ids) != len(set(ids)):
        errs.append('KNOB-TRUNG: knob_id lap lai')

    for k in knobs:
        kid = k.get('knob_id', '?')
        for f in KNOB_REQUIRED_FIELDS:
            if f not in k:
                errs.append(f'{kid}: thieu field {f}')
        t = k.get('type')
        if t not in VALID_TYPES:
            errs.append(f'{kid}: type "{t}" khong thuoc {sorted(VALID_TYPES)}')
        if t in ('scalar', 'curve') and 'valid_range' not in k:
            errs.append(f'{kid}: {t} thieu valid_range')
        if t == 'enum' and not (k.get('values') or k.get('values_source')):
            errs.append(f'{kid}: enum thieu values/values_source')
        # R195 no-hardcode
        bad_keys = FORBIDDEN_VALUE_KEYS & set(k)
        if bad_keys:
            errs.append(f'{kid}: R195-HARDCODE key cam {sorted(bad_keys)} — so that phai calibrate tu golden')
        for leak in _numeric_leaks(k, kid):
            errs.append(f'{kid}: R195-HARDCODE so nam ngoai valid_range tai {leak}')
        if t == 'enum':
            for v in (k.get('values') or []):
                if isinstance(v, (int, float)) and not isinstance(v, bool):
                    errs.append(f'{kid}: R195-HARDCODE enum value so: {v}')
        # consumer read-only
        c = k.get('consumer') or {}
        if c.get('domain') != 'generator':
            errs.append(f'{kid}: consumer.domain "{c.get("domain")}" != generator')
        if c.get('access') != 'read_only':
            errs.append(f'{kid}: LEO-THANG consumer.access "{c.get("access")}" != read_only (BP3)')
        # calibration_source phai tro golden
        cs = k.get('calibration_source') or {}
        if 'golden' not in str(cs.get('calibrate_from', '')).lower():
            errs.append(f'{kid}: calibration_source khong tro golden (R195)')
    return errs


def check_io(io, contract, bp0):
    """Check 5 + doi chieu reader grant BP0. Tra ve list loi."""
    errs = []
    out = (io or {}).get('output') or {}
    ps = out.get('packet_schema') or {}
    for f in PACKET_REQUIRED:
        if f not in ps:
            errs.append(f'packet_schema thieu field bat buoc: {f}')
    extra = [f for f in ps if f not in PACKET_REQUIRED]
    if extra:
        errs.append(f'FIELD-MA trong packet_schema: {extra} — moi field generator doc phai duoc khai dong')
    knobs_ref = (((ps.get('per_scene') or {}).get('item') or {}).get('knobs') or {})
    if 'knob_id' not in str(knobs_ref.get('keys_must_equal', '')):
        errs.append('per_scene.item.knobs thieu keys_must_equal tro contract knob_id (field ma se lot)')
    # input planned ref 5 metadata
    src = ((io or {}).get('input') or {}).get('source_schema') or {}
    if src.get('status') == 'planned':
        for m in PLANNED_META:
            if not src.get(m):
                errs.append(f'input.source_schema planned thieu metadata: {m}')
    # reader/writer khop BP0 + BP3
    grant = ((bp0 or {}).get('domains') or {}).get('decision_engine', {}).get('reader', [])
    for r in (out.get('consumer_contract') or {}).get('reader', []):
        if r not in grant:
            errs.append(f'reader "{r}" ngoai grant BP0 decision_engine {grant}')
    for w in out.get('writer', []):
        if w not in ('decision_engine', 'mr_long'):
            errs.append(f'writer "{w}" vi pham BP3 1-writer (chi decision_engine + mr_long)')
    return errs


def main():
    errs = []
    contract = _load(D_CONTRACT, errs, 'decision_contract')
    io = _load(D_IO, errs, 'decision_io')
    bp0 = _load(D_BP0, errs, 'blueprint_domains')
    if contract is not None and io is not None:
        for doc, label in ((contract, 'contract'), (io, 'io')):
            v = str((doc.get('meta') or {}).get('version'))
            if v != __version__:
                errs.append(f'{label}: version {v} != checker {__version__}')
        errs += check_contract(contract)
        errs += check_io(io, contract, bp0)

    print(f'=== BP6 DECISION CHECK v{__version__} ===')
    for e in errs:
        print(f'  [VIOLATION] {e}')
    n = len(((contract or {}).get('knobs')) or [])
    print(f'  knobs: {n}/12 khai — R195 no-hardcode scan + consumer read-only + packet dong')
    print(f"=== {'FAIL — ' + str(len(errs)) + ' vi pham' if errs else 'PASS'} ===")
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
