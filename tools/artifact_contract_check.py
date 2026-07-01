"""SVHMP — ARTIFACT CONTRACT CHECK (PACK2 08, Boss 2/7).
Chong bao cao lao: MAY tu sinh DoD matrix tu registry + verify moi artifact KHAI
phai TON TAI tren disk. Khai ma khong co = Critical -> exit 1.
DoD dims: schema/manager/validator/report/test/md_doc/sample_yaml/regression.
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml

SVHMP = Path(__file__).parent.parent
DIMS = ['schema', 'manager', 'validator', 'report', 'test', 'md_doc', 'sample_yaml', 'regression']


def _list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _paths(v, acc):
    if isinstance(v, str):
        if '/' in v and v.rsplit('.', 1)[-1] in ('py', 'yaml', 'yml', 'md'):
            acc.append(v)
    elif isinstance(v, list):
        for x in v:
            _paths(x, acc)
    elif isinstance(v, dict):
        for x in v.values():
            _paths(x, acc)


def _matrix(dom):
    p = []
    _paths(dom, p)
    md = any(s.endswith('.md') for s in p)
    yml = any(s.endswith(('.yaml', '.yml')) for s in p)
    sot_engine = any('tools/' in s and s.endswith('.py') for s in _list(dom.get('source_of_truth')))
    return {
        'schema': 'schema' in dom,
        'manager': sot_engine or any(k in dom for k in ('manager', 'checker', 'migration', 'ci_gate', 'auditor')),
        'validator': any(k in dom for k in ('validators', 'checker', 'triage')),
        'report': any(k in dom for k in ('reports', 'manifests_dir', 'note')) or 'deprecation_report' in str(dom),
        'test': 'tests' in dom,
        'md_doc': md,
        'sample_yaml': yml,
        'regression': 'tests' in dom,
    }


def check():
    """-> (matrix: {domain: {dim: bool}}, missing: [(domain, rel_path)]).
    Tach ra de test R212 chung thuc (khong sys.exit)."""
    reg = yaml.safe_load((SVHMP / 'governance' / 'architecture_registry.yaml').read_text(encoding='utf-8'))
    domains = reg.get('domains') or {}
    matrix, missing = {}, []
    for name, dom in domains.items():
        matrix[name] = _matrix(dom)
        p = []
        _paths(dom, p)
        for rel in p:
            if not (SVHMP / rel).exists():
                missing.append((name, rel))
    return matrix, missing


def main():
    matrix, missing = check()
    print("=== ARTIFACT CONTRACT CHECK (DoD matrix, may sinh) ===")
    header = 'domain'.ljust(15) + ''.join(d[:4].ljust(6) for d in DIMS)
    print(header)
    for name, m in matrix.items():
        row = name.ljust(15) + ''.join(('  ✓  ' if m[d] else '  ·  ').ljust(6) for d in DIMS)
        print(row)
    print("-" * len(header))
    if missing:
        print(f"[CRITICAL] {len(missing)} artifact KHAI nhung KHONG co tren disk:")
        for name, rel in missing:
            print(f"  ! {name}: {rel}")
        print("=== FAIL ===")
        sys.exit(1)
    print(f"OK: moi artifact khai deu ton tai ({len(matrix)} domain).  === PASS ===")
    sys.exit(0)


if __name__ == '__main__':
    main()
