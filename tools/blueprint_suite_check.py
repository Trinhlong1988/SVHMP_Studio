"""BP5 BLUEPRINT SUITE CHECK v1.0.0 — MOT CUA cho toan bo blueprint validators.

GOI (khong viet lai — TASK_BP5 rang buoc chong regression-by-overwrite 3/7)
tuan tu 5 checker con qua subprocess, in matrix PASS/FAIL tung tang,
exit 0 CHI KHI tat ca xanh:

  bp0  tools/blueprint_constitution_check.py   (BP-C v2.0 — 22+1 domain)
  bp1  tools/bp1_architecture_check.py         (graph/iface/layer)
  bp2  tools/bp2_domain_check.py               (13 domain / 70 facet)
  bp3  tools/bp3_ownership_check.py            (1-writer + dep 3-nguon)
  bp4  tools/bp4_runtime_check.py              (flow/bus/state/memory)

DUP-KEY: loader dung chung load_yaml_no_dup (1 implementation duy nhat trong
blueprint_constitution_check.py, cac checker con IMPORT — khong copy-paste;
khoa boi tests/test_bp5_validation.py::test_dup_key_loader_single_impl).
Dup-key o BAT KY file blueprint nao -> checker tang do FAIL -> suite exit 1.

Pass-through cho negative test / audit: --bp{N} "<extra args>" chuyen nguyen
van cho checker tang do (vd --bp2 "--spec C:/x/broken.yaml").

Exit 0 = tat ca tang PASS, exit 1 = >=1 tang FAIL.
"""
import shlex
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable

__version__ = '1.0.0'

SUITE = [
    ('bp0', 'BP0 constitution', 'tools/blueprint_constitution_check.py'),
    ('bp1', 'BP1 core',         'tools/bp1_architecture_check.py'),
    ('bp2', 'BP2 domain',       'tools/bp2_domain_check.py'),
    ('bp3', 'BP3 ownership',    'tools/bp3_ownership_check.py'),
    ('bp4', 'BP4 runtime',      'tools/bp4_runtime_check.py'),
]


def run_suite(overrides=None):
    """Chay tuan tu 5 tang; overrides={key: [extra args]} chi de test/audit
    tro checker tang do vao file hong (khong dung o che do gate)."""
    overrides = overrides or {}
    rows = []
    for key, label, rel in SUITE:
        cmd = [PY, str(REPO / rel)] + list(overrides.get(key) or [])
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        rows.append({'key': key, 'label': label, 'script': rel, 'rc': r.returncode,
                     'tail': ((r.stdout or '') + (r.stderr or ''))[-500:]})
    return rows


def main(argv):
    overrides = {}
    for key, _label, _rel in SUITE:
        flag = f'--{key}'
        if flag in argv:
            # posix=False: giu nguyen backslash duong dan Windows (posix mode
            # nuot '\' -> checker con nhan path nat = fail sai loai loi)
            overrides[key] = [t.strip('"') for t in
                              shlex.split(argv[argv.index(flag) + 1], posix=False)]
    print(f'=== BLUEPRINT SUITE CHECK v{__version__} (BP5 — 1 cua) ===')
    rows = run_suite(overrides)
    fails = [row for row in rows if row['rc'] != 0]
    for row in rows:
        mark = 'PASS' if row['rc'] == 0 else 'FAIL'
        print(f"  [{mark}] {row['key']}  {row['label']:<18} {row['script']} (exit {row['rc']})")
        if row['rc'] != 0:
            print(row['tail'])
    if fails:
        print(f"=== FAIL — {len(fails)}/{len(rows)} tang do: "
              f"{', '.join(row['key'] for row in fails)} ===")
        return 1
    print(f'=== PASS — {len(rows)}/{len(rows)} tang blueprint xanh ===')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
