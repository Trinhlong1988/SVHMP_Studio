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

    # G1: file_index.yaml — tinh la DA MAP (tru 'unclassified' de con show gap that)
    fi = SVHMP / 'governance' / 'file_index.yaml'
    if fi.exists():
        idx = yaml.safe_load(fi.read_text(encoding='utf-8')) or {}
        for f, info in (idx.get('files') or {}).items():
            if (info or {}).get('domain') != 'unclassified':
                declared.setdefault(f, []).append('file_index:' + str(info.get('domain')))

    # disk scan — file quan trọng
    disk = set()
    for pat in ['tools/*.py', 'bible/*.yaml', 'tests/test_*.py', 'governance/*.yaml']:
        for p in SVHMP.glob(pat):
            disk.add(str(p.relative_to(SVHMP)).replace('\\', '/'))

    declared_paths = set(declared)
    missing = sorted(p for p in declared_paths if not (SVHMP / p).exists())
    unmapped = sorted(d for d in disk if d not in declared_paths)
    # DUP chi tinh giua REGISTRY domain (bo qua file_index auto-map — chi la cross-ref)
    dup = {p: o for p, o in declared.items()
           if len(set(x for x in o if not x.startswith('file_index'))) > 1}

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

    # deep-audit F5 (2/7): truoc day CHI exit 1 khi MISSING -> nhan auditor.py
    # "0 MISSING/DUP/UNMAPPED" noi qua (unmapped/dup KHONG chan). G1 da dua ve
    # 0/0/0 nen gio ENFORCE strict: bat ky MISSING/DUP/UNMAPPED -> exit 1.
    bad = bool(missing or dup or unmapped)
    verdict = 'FAIL' if bad else 'PASS (source-of-truth du, 0/0/0)'
    print(f"\n=== {verdict} ; MISSING={len(missing)} DUP={len(dup)} UNMAPPED={len(unmapped)} ===")
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
