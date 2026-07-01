"""SVHMP — Architecture Registry Checker (Tier 0, Boss 2/7).
Quét disk vs governance/architecture_registry.yaml -> báo:
- MISSING: file khai trong registry nhưng KHÔNG có trên disk.
- UNMAPPED: file .py/.yaml quan trọng có trên disk nhưng CHƯA map domain (sai vị trí/thiếu).
- DUP: file map ở >1 domain.
Exit 1 nếu có MISSING (source-of-truth vỡ). Không suy luận — đọc thật.
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml

SVHMP = Path(__file__).parent.parent
REG = SVHMP / 'governance' / 'architecture_registry.yaml'


def collect_declared(node, out, owner):
    """Đệ quy gom mọi chuỗi trông giống path file."""
    if isinstance(node, str):
        if '/' in node and node.split('/')[-1].count('.') >= 1 and '*' not in node and ' ' not in node:
            out.setdefault(node, []).append(owner)
    elif isinstance(node, list):
        for x in node:
            collect_declared(x, out, owner)
    elif isinstance(node, dict):
        for k, v in node.items():
            collect_declared(v, out, owner)


def main():
    reg = yaml.safe_load(REG.read_text(encoding='utf-8'))
    declared = {}
    for dom, dd in (reg.get('domains') or {}).items():
        collect_declared(dd, declared, dom)
    collect_declared(reg.get('meta', {}), declared, 'meta')

    # disk scan — file quan trọng
    disk = set()
    for pat in ['tools/*.py', 'bible/*.yaml', 'tests/test_*.py', 'governance/*.yaml']:
        for p in SVHMP.glob(pat):
            disk.add(str(p.relative_to(SVHMP)).replace('\\', '/'))

    declared_paths = set(declared)
    missing = sorted(p for p in declared_paths if not (SVHMP / p).exists())
    unmapped = sorted(d for d in disk if d not in declared_paths)
    dup = {p: o for p, o in declared.items() if len(set(o)) > 1}

    print(f"=== ARCHITECTURE REGISTRY CHECK ===")
    print(f"  declared file: {len(declared_paths)}   disk file quan trong: {len(disk)}")
    print(f"\n[MISSING] {len(missing)} (khai nhung khong co tren disk):")
    for m in missing:
        print(f"  ✗ {m}")
    print(f"\n[UNMAPPED] {len(unmapped)} (co tren disk, CHUA map domain):")
    for u in unmapped:
        print(f"  ? {u}")
    print(f"\n[DUP] {len(dup)} (map >1 domain):")
    for p, o in dup.items():
        print(f"  ! {p} -> {set(o)}")

    print(f"\n=== {'FAIL (co MISSING)' if missing else 'PASS (source-of-truth du)'} ; {len(unmapped)} unmapped can triage ===")
    sys.exit(1 if missing else 0)


if __name__ == '__main__':
    main()
