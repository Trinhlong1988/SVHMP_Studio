"""SVHMP — CLAIM-ENFORCER REGISTRY checker (de xuat #1+#4, governance/AUDIT_ROOT_
CAUSE_SYNTHESIS_17_07.md muc 3). Goc re du an = CLAIM-ENFORCER GAP.

Doc THAT governance/claim_enforcer_map.yaml + xac minh:
  (a) COVERAGE — moi claim trong REQUIRED_CLAIMS phai co mat trong map. Thieu -> FAIL.
  (b) MASK-AS-ACTIVE — claim status ENFORCED/PARTIAL ma enforcer:
        - null/rong                                   -> FAIL
        - path (truoc '::') KHONG ton tai tren disk    -> FAIL
        - test node (co '::') KHONG duoc pytest COLLECT -> FAIL (chay --collect-only THAT, khong grep ten)
  (c) MISLABEL — claim status NO_ENFORCER/HONOR_SYSTEM/LLM_JUDGE_ONLY ma VAN gan enforcer
      may (khong null) -> FAIL (chong gan gate gia cho claim thuc te 0 gate).
  + status khong hop le -> FAIL.

structural_problems() = PURE (chi doc map + kiem file ton tai tren repo_root) — de self-test
mutation goi thang, khong can subprocess. collectability_problems() chay pytest --collect-only.

CHU Y (R215.5/R215.6): checker nay + self-test cua no phai BEHAVIORAL. KHONG wire vao
ci_gate.CHECKS (chay trong pytest la du; neu wire phai them gate_mutation_map.yaml — reviewer quyet).
Idempotent — chi doc, khong ghi.
"""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
MAP_PATH = REPO / 'governance' / 'claim_enforcer_map.yaml'

# Danh sach claim cao rui ro nhat PHAI dang ky (bounded scope task).
REQUIRED_CLAIMS = [
    'R_SUPREME', 'R196', 'R197', 'R200', 'R210', 'R211', 'R215', 'R216',
    'ALWAYS_5', 'NEVER_7', 'GHOST_RULES_3', 'ENDING_RULES', 'SERIES_RULES',
]

VALID_STATUS = {'ENFORCED', 'PARTIAL', 'NO_ENFORCER', 'HONOR_SYSTEM', 'LLM_JUDGE_ONLY'}
MACHINE_ENFORCED = {'ENFORCED', 'PARTIAL'}          # yeu cau enforcer may that
NON_MACHINE = {'NO_ENFORCER', 'HONOR_SYSTEM', 'LLM_JUDGE_ONLY'}  # enforcer PHAI null


def load_map(path=MAP_PATH):
    return yaml.safe_load(Path(path).read_text(encoding='utf-8')) or {}


def _as_list(enforcer):
    """Chuan hoa enforcer -> list[str] (chap nhan str don, list, hoac null)."""
    if enforcer is None:
        return []
    if isinstance(enforcer, str):
        return [enforcer]
    if isinstance(enforcer, list):
        return [str(x) for x in enforcer]
    return [str(enforcer)]


def structural_problems(mapping, repo_root=REPO, required=REQUIRED_CLAIMS):
    """PURE (chi doc map + Path.exists tren repo_root) — self-test mutation goi thang.

    Tra ve dict: missing / bad_status / mask (ENFORCED/PARTIAL loi) / mislabel
    (NON_MACHINE ma gan enforcer). collectability KHONG o day (can subprocess)."""
    claims = (mapping or {}).get('claims') or {}
    missing = [c for c in required if c not in claims]
    bad_status, mask, mislabel = [], [], []

    for cid, info in claims.items():
        info = info or {}
        status = info.get('status')
        enf = _as_list(info.get('enforcer'))

        if status not in VALID_STATUS:
            bad_status.append(f"{cid}: status '{status}' khong hop le (phai 1 trong {sorted(VALID_STATUS)})")
            continue

        if status in MACHINE_ENFORCED:
            if not enf:
                mask.append(f"{cid}: status {status} nhung enforcer RONG/null (mask-as-active)")
                continue
            for e in enf:
                file_part = e.split('::')[0].replace('\\', '/')
                if not (repo_root / file_part).exists():
                    mask.append(f"{cid}: enforcer '{e}' tro file KHONG ton tai tren disk ({file_part})")
        elif status in NON_MACHINE:
            if enf:
                mislabel.append(
                    f"{cid}: status {status} (non-machine) ma VAN gan enforcer may {enf} — "
                    "chong gan gate gia; dung llm_ref cho LLM_JUDGE_ONLY, enforcer phai null")

    return {'missing': missing, 'bad_status': bad_status, 'mask': mask, 'mislabel': mislabel}


def _collect_nodeids(files):
    """Chay `pytest --collect-only` THAT -> set nodeid. KHONG grep ten trong source."""
    if not files:
        return set(), 0, ''
    cmd = [sys.executable, '-m', 'pytest', '--collect-only', '-q', *files]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', cwd=str(REPO))
    nodeids = set()
    for ln in (r.stdout or '').splitlines():
        ln = ln.strip().replace('\\', '/')
        if '::' in ln:
            nodeids.add(ln.split(' ')[0])
    return nodeids, r.returncode, (r.stderr or '')[-500:]


def collectability_problems(mapping):
    """Voi moi enforcer test-node (co '::') cua claim ENFORCED/PARTIAL, xac nhan
    pytest COLLECT that. Tra ve (problems, collected)."""
    claims = (mapping or {}).get('claims') or {}
    nodes = []  # (cid, node)
    for cid, info in claims.items():
        info = info or {}
        if info.get('status') not in MACHINE_ENFORCED:
            continue
        for e in _as_list(info.get('enforcer')):
            e = e.replace('\\', '/')
            if '::' in e:
                nodes.append((cid, e))
    files = sorted({n.split('::')[0] for _c, n in nodes})
    collected, rc, tail = _collect_nodeids(files)
    problems = []
    for cid, node in nodes:
        if node not in collected:
            problems.append(
                f"{cid}: test node '{node}' KHONG duoc pytest collect (rc={rc}). "
                f"stderr: {tail.strip()[-200:]}")
    return problems, collected


def main():
    print("=== CLAIM-ENFORCER REGISTRY CHECK ===")
    mapping = load_map()
    claims = (mapping or {}).get('claims') or {}
    st = structural_problems(mapping)
    col_problems, _ = collectability_problems(mapping)

    print(f"  claim trong map: {len(claims)}   REQUIRED: {len(REQUIRED_CLAIMS)}")
    for cid in REQUIRED_CLAIMS:
        info = claims.get(cid) or {}
        status = info.get('status', 'MISSING')
        print(f"    [{'OK' if cid in claims else 'X'}] {cid:14} -> {status}")

    fail = 0
    for key, label in [('missing', 'MISSING (claim REQUIRED thieu trong map)'),
                       ('bad_status', 'BAD-STATUS'),
                       ('mask', 'MASK-AS-ACTIVE (ENFORCED/PARTIAL enforcer khong hop le)'),
                       ('mislabel', 'MISLABEL (non-machine ma gan enforcer)')]:
        if st[key]:
            fail += 1
            print(f"\n[{label}] {len(st[key])}:")
            for s in st[key]:
                print(f"  X {s}")
    if col_problems:
        fail += 1
        print(f"\n[NOT-COLLECTED] {len(col_problems)} test node khong collect that:")
        for s in col_problems:
            print(f"  X {s}")

    verdict = 'PASS (moi REQUIRED claim co mat + enforcer khong mask-as-active)' if not fail \
        else f'FAIL ({fail} nhom van de)'
    print(f"\n=== {verdict} ===")
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
