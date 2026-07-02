"""SVHMP — Validate project_config contract (PACK4 doc 15_project_config).

Hop dong "same code, khac project": moi khac biet the loai/thi truong phai nap
tu project_config, KHONG hard-code trong engine. Tool nay kiem 5 field bat buoc
hien dien + dung kieu tren MOI project_config.yaml tim thay.

5 field bat buoc (bar 15_project_config.md):
  genre        (str)  — the loai truyen
  distribution (map)  — phan bo muc tieu xuyen tap (age/region/death)
  dialect      (str)  — vung giong chu dao
  beat         (list) — khung nhip episode
  taxonomy     (map)  — phan loai object/setting/regret (tro toi bible)

Usage:
  python tools/validate_project_config.py                 # quet repo tim project_config*.yaml
  python tools/validate_project_config.py --path <file>   # validate 1 file cu the

Exit: 0 = hop le (hoac chua co config — template-pack stage) ; 1 = INVALID.
"""
import sys
import argparse
from pathlib import Path

try:
    import yaml
except ImportError:
    print('[validate_project_config] PyYAML chua cai', file=sys.stderr)
    sys.exit(1)

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SVHMP = Path(__file__).resolve().parents[1]

# field -> kieu Python mong doi (isinstance)
REQUIRED = {
    'genre': str,
    'distribution': dict,
    'dialect': str,
    'beat': list,
    'taxonomy': dict,
}


def find_configs():
    """Tim moi project_config*.yaml tren disk (bo qua .git)."""
    out = []
    for p in SVHMP.rglob('project_config*.yaml'):
        if '.git' in p.parts:
            continue
        out.append(p)
    return sorted(out)


def validate_one(path):
    """Tra ve list loi (rong = hop le)."""
    errors = []
    try:
        data = yaml.safe_load(path.read_text(encoding='utf-8'))
    except Exception as e:  # noqa: BLE001
        return [f'khong parse duoc YAML: {e}']
    if not isinstance(data, dict):
        return ['project_config phai la mapping (key: value) o top-level']
    for field, typ in REQUIRED.items():
        if field not in data:
            errors.append(f'thieu field bat buoc: {field}')
        elif not isinstance(data[field], typ):
            errors.append(
                f'field {field} sai kieu: can {typ.__name__}, co {type(data[field]).__name__}')
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser(description='Validate project_config contract (PACK4/15)')
    ap.add_argument('--path', help='validate 1 file cu the thay vi quet repo')
    args = ap.parse_args(argv)

    if args.path:
        targets = [Path(args.path)]
    else:
        targets = find_configs()

    print('=== VALIDATE PROJECT_CONFIG (PACK4/15) ===')
    print(f'required fields: {", ".join(REQUIRED)}')

    if not targets:
        # PACK4 la TEMPLATE pack: co the chua project cu the nao duoc khai.
        # Khong co gi de fail, nhung noi ro (khong im lang = weak-verifier).
        print('[INFO] chua co project_config*.yaml nao tren disk (template-pack stage).')
        print('=== PASS (khong co config de validate; validator san sang khi project khai) ===')
        return 0

    bad = 0
    for t in targets:
        errs = validate_one(t)
        rel = t.relative_to(SVHMP) if t.is_absolute() and str(t).startswith(str(SVHMP)) else t
        if errs:
            bad += 1
            print(f'[INVALID] {rel}')
            for e in errs:
                print(f'    - {e}')
        else:
            print(f'[OK] {rel}  (du {len(REQUIRED)} field)')

    if bad:
        print(f'=== FAIL: {bad}/{len(targets)} project_config INVALID ===')
        return 1
    print(f'=== PASS: {len(targets)}/{len(targets)} project_config hop le ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
