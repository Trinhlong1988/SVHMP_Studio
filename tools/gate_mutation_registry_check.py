"""SVHMP — META-GATE checker: moi stage trong ci_gate.CHECKS PHAI co mutation-proof
test da DANG KY (governance/gate_mutation_map.yaml), hoac nam trong 1 allowlist bucket.

De xuat #2 (governance/AUDIT_ROOT_CAUSE_SYNTHESIS_17_07.md muc 3). Chan lop "gate-gia":
gate them vao CHECKS ma khong ai chung minh no bat duoc vi pham that (vd post_render_gate
hardcode results.append((True,...)) luon PASS).

FAIL (exit 1) neu:
  - 1 stage trong CHECKS KHONG o bucket nao (mapped / known_self_battery /
    known_no_mutation_test)  -> gate moi them ma chua co mutation-test / chua allowlist.
  - 1 stage o >1 bucket (nhap nhang).
  - 1 stage co test_node (mapped) nhung node do KHONG duoc pytest COLLECT that
    (chay `pytest --collect-only` that su, KHONG grep chuoi ten).
WARN (khong FAIL): map entry tro stage KHONG con trong CHECKS (stale — gate da go).

CHU Y (R215.6): CHINH checker nay + self-test cua no phai mutation-proof/behavioral.
KHONG wire vao ci_gate.CHECKS (chay trong pytest_suite la du, tranh de quy).

Idempotent — chi doc, khong ghi.
"""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
MAP_PATH = REPO / 'governance' / 'gate_mutation_map.yaml'
BUCKETS = ('mapped', 'known_self_battery', 'known_no_mutation_test')


def ci_gate_check_keys():
    """Doc THAT ci_gate.CHECKS (nguon su that stage). Import, khong grep."""
    sys.path.insert(0, str(REPO / 'tools'))
    import ci_gate  # noqa: E402
    return [k for k, _rel in ci_gate.CHECKS]


def load_map(path=MAP_PATH):
    return yaml.safe_load(Path(path).read_text(encoding='utf-8')) or {}


def _bucket_membership(mapping):
    """stage -> [bucket,...] cho moi stage xuat hien trong bat ky bucket nao."""
    member = {}
    for b in BUCKETS:
        for stage in (mapping.get(b) or {}):
            member.setdefault(stage, []).append(b)
    return member


def coverage_problems(check_keys, mapping):
    """PURE (khong pytest/IO ngoai) — de self-test monkeypatch CHECKS/map goi truc tiep.

    Tra ve dict: uncovered / duplicate / stale (list stage/thong bao)."""
    member = _bucket_membership(mapping)
    check_set = set(check_keys)
    uncovered = [k for k in check_keys if k not in member]
    duplicate = [f"{k} -> {member[k]}" for k in check_keys if len(member.get(k, [])) > 1]
    stale = sorted(s for s in member if s not in check_set)
    return {'uncovered': uncovered, 'duplicate': duplicate, 'stale': stale}


def _collect_nodeids(files):
    """Chay `pytest --collect-only` THAT tren cac file -> set nodeid da collect.
    Tra ve (nodeids_set, returncode, tail_stderr). KHONG grep ten trong source."""
    if not files:
        return set(), 0, ''
    cmd = [sys.executable, '-m', 'pytest', '--collect-only', '-q', *files]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', cwd=str(REPO))
    nodeids = set()
    for ln in (r.stdout or '').splitlines():
        ln = ln.strip().replace('\\', '/')
        # dong nodeid pytest -q collect-only: 'tests/x.py::func'. Dong summary
        # ('N tests collected...') khong co '::' -> bi loai. Lay token dau (bo chu thich).
        if '::' in ln:
            nodeids.add(ln.split(' ')[0])
    return nodeids, r.returncode, (r.stderr or '')[-500:]


def collectability_problems(mapping):
    """Voi moi entry mapped, xac nhan test_node duoc pytest COLLECT that.
    Tra ve (problems, collected_map) — problems=[] neu tat ca collect duoc."""
    mapped = mapping.get('mapped') or {}
    nodes = {}
    for stage, info in mapped.items():
        tn = (info or {}).get('test_node')
        if not tn or '::' not in tn:
            nodes[stage] = None
            continue
        nodes[stage] = tn.replace('\\', '/')
    files = sorted({tn.split('::')[0] for tn in nodes.values() if tn})
    collected, rc, tail = _collect_nodeids(files)
    problems = []
    for stage, tn in nodes.items():
        if tn is None:
            problems.append(f"{stage}: mapped nhung thieu/khong hop le test_node (can 'path::func')")
            continue
        if tn not in collected:
            problems.append(
                f"{stage}: test_node '{tn}' KHONG duoc pytest collect "
                f"(collect rc={rc}). Kiem tra ten ham/duong dan; stderr: {tail.strip()[-200:]}")
    return problems, collected


def main():
    print("=== GATE MUTATION REGISTRY CHECK ===")
    keys = ci_gate_check_keys()
    mapping = load_map()
    cov = coverage_problems(keys, mapping)

    member = _bucket_membership(mapping)
    print(f"  ci_gate.CHECKS stage: {len(keys)}")
    for b in BUCKETS:
        n = len(mapping.get(b) or {})
        print(f"    {b}: {n}")

    # per-stage summary
    for k in keys:
        buckets = member.get(k, [])
        tag = buckets[0] if len(buckets) == 1 else (','.join(buckets) if buckets else 'UNCOVERED')
        print(f"    [{'OK' if len(buckets) == 1 else 'X'}] {k:18} -> {tag}")

    col_problems, _ = collectability_problems(mapping)

    fail = 0
    if cov['uncovered']:
        fail += 1
        print(f"\n[UNCOVERED] {len(cov['uncovered'])} stage khong o bucket nao "
              f"(gate moi chua mutation-test / chua allowlist):")
        for s in cov['uncovered']:
            print(f"  X {s}")
    if cov['duplicate']:
        fail += 1
        print(f"\n[DUPLICATE] {len(cov['duplicate'])} stage o >1 bucket (nhap nhang):")
        for s in cov['duplicate']:
            print(f"  X {s}")
    if col_problems:
        fail += 1
        print(f"\n[NOT-COLLECTED] {len(col_problems)} test_node khong duoc pytest collect that:")
        for s in col_problems:
            print(f"  X {s}")
    if cov['stale']:
        print(f"\n[WARN-STALE] {len(cov['stale'])} stage trong map nhung khong con trong CHECKS "
              f"(gate da go? — go khoi map):")
        for s in cov['stale']:
            print(f"  ? {s}")

    verdict = 'PASS (moi stage co mutation-test dang ky hoac allowlist)' if not fail \
        else f'FAIL ({fail} nhom van de)'
    print(f"\n=== {verdict} ===")
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
