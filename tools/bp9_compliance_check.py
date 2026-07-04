"""BP9 COMPLIANCE CHECK v1.0.0 — gate máy CẤU TRÚC cho BP9 Compliance/Publish Gate.

KHÔNG quét nội dung episode thật (đó là G8 QA Runtime sau này). CHỈ kiểm cấu trúc
2 file bp9 + đối chiếu BP0 (blueprint_domains.yaml).

Check:
  1  DUP-KEY loader single-impl (import blueprint_constitution_check) + version
     khớp checker/2 file bp9 (content_policy/policy_gates).
  2  content_policy: ĐÚNG 2 hard_boundaries (HB01, HB02) — thiếu 1 = FAIL · mỗi
     hard_boundary PHẢI có can_cu_phap_ly >=1 (chống luật rỗng/bịa) · KHÔNG số
     (int/float) bất kỳ đâu trong toàn file (scan TOÀN FILE ngay từ đầu — mirror
     bài học BP6/BP7/BP8, tái sử dụng `_numeric_leaks`, không viết lại).
  3  policy_gates: mọi gate.ap_dung_domain[] PHẢI resolve thật trong
     blueprint_domains.yaml#domains (domain má = FAIL) · gate.loai_check PHẢI
     thuộc đúng 4 giá trị enum khai ở meta.loai_check_enum (loại_check lạ = FAIL)
     · gate.severity=HIGH PHẢI có owner_review nhắc "Mr.Long" (chống máy tự quyết).
  4  BP0 reconcile: domains.publisher.schema/validator (blueprint_domains.yaml)
     PHẢI status=exists VÀ path khớp CHÍNH XÁC 2 file bp9 tương ứng (field-hóa
     đúng slot, không lệch — drift = FAIL).

Exit 0 = PASS, exit 1 = FAIL.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402
from bp6_decision_check import _numeric_leaks  # noqa: E402 (tai su dung — khong viet lai)

__version__ = '1.0.0'

BP9 = REPO / 'governance' / 'blueprint' / 'bp9'
D_POLICY = BP9 / 'content_policy.yaml'
D_GATES = BP9 / 'policy_gates.yaml'
D_BP0 = REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml'

EXPECTED_HB = ['HB01_no_actionable_ritual_detail', 'HB02_no_real_profit_solicitation_link']


def _load(path, errs, label):
    try:
        return load_yaml_no_dup(Path(path).read_text(encoding='utf-8'))
    except DupKeyError as e:
        errs.append(f'{label}: DUP-KEY — {e}')
    except Exception as e:
        errs.append(f'{label}: khong doc duoc: {e}')
    return None


def check_content_policy(policy):
    """Check 2. Tra ve list loi."""
    errs = []
    hbs = (policy or {}).get('hard_boundaries') or []
    ids = [h.get('rule_id') for h in hbs]
    missing = [h for h in EXPECTED_HB if h not in ids]
    if missing:
        errs.append(f'HARD-BOUNDARY-THIEU: {missing}')
    for h in hbs:
        rid = h.get('rule_id', '?')
        cc = h.get('can_cu_phap_ly') or []
        if not cc:
            errs.append(f'{rid}: thieu can_cu_phap_ly (luat rong — chong bia)')
    for leak in _numeric_leaks(policy, 'content_policy', allowed_keys=set()):
        errs.append(f'R195-HARDCODE: so hardcode trong content_policy tai {leak} '
                    '(content_policy la LUAT+FORMAT thuan, 0 so duoc phep)')
    return errs


def check_policy_gates(gates, bp0):
    """Check 3. Tra ve list loi."""
    errs = []
    doms = set(((bp0 or {}).get('domains') or {}).keys())
    enum = set((gates or {}).get('meta', {}).get('loai_check_enum') or [])
    for g in (gates or {}).get('gates') or []:
        gid = g.get('gate_id', '?')
        for d in g.get('ap_dung_domain') or []:
            if d not in doms:
                errs.append(f'{gid}: DOMAIN-MA "{d}" khong ton tai trong blueprint_domains.yaml')
        lc = g.get('loai_check')
        if lc not in enum:
            errs.append(f'{gid}: loai_check "{lc}" khong thuoc enum {sorted(enum)}')
        if g.get('severity') == 'HIGH':
            orv = str(g.get('owner_review', ''))
            if 'Mr.Long' not in orv:
                errs.append(f'{gid}: severity=HIGH nhung owner_review khong nhac "Mr.Long" (may tu quyet noi dung nhay cam = FAIL)')
    for leak in _numeric_leaks(gates, 'policy_gates', allowed_keys=set()):
        errs.append(f'R195-HARDCODE: so hardcode trong policy_gates tai {leak} '
                    '(policy_gates la khai bao thuan, 0 so duoc phep)')
    return errs


def check_bp0_reconcile(bp0, root=REPO):
    """Check 4. Tra ve list loi."""
    errs = []
    pub = ((bp0 or {}).get('domains') or {}).get('publisher') or {}
    expected = {
        'schema': 'governance/blueprint/bp9/content_policy.yaml',
        'validator': 'tools/bp9_compliance_check.py',
    }
    for slot, want_path in expected.items():
        ref = pub.get(slot) or {}
        if ref.get('status') != 'exists':
            errs.append(f'publisher.{slot}: DRIFT-BP0 status "{ref.get("status")}" != exists (chua field-hoa dung)')
        elif ref.get('path') != want_path:
            errs.append(f'publisher.{slot}: DRIFT-BP0 path "{ref.get("path")}" != "{want_path}" (field-hoa lech slot)')
        elif not (Path(root) / want_path).exists():
            errs.append(f'publisher.{slot}: DRIFT-BP0 path khai exists nhung KHONG ton tai tren dia: {want_path}')
    return errs


def main():
    errs = []
    policy = _load(D_POLICY, errs, 'content_policy')
    gates = _load(D_GATES, errs, 'policy_gates')
    bp0 = _load(D_BP0, errs, 'blueprint_domains')

    if None not in (policy, gates, bp0):
        for doc, label in ((policy, 'content_policy'), (gates, 'policy_gates')):
            v = str((doc.get('meta') or {}).get('version'))
            if v != __version__:
                errs.append(f'{label}: version {v} != checker {__version__}')
        errs += check_content_policy(policy)
        errs += check_policy_gates(gates, bp0)
        errs += check_bp0_reconcile(bp0)

    print(f'=== BP9 COMPLIANCE CHECK v{__version__} ===')
    for e in errs:
        print(f'  [VIOLATION] {e}')
    n_hb = len(((policy or {}).get('hard_boundaries')) or [])
    n_g = len(((gates or {}).get('gates')) or [])
    print(f'  hard_boundaries: {n_hb}/2 · policy gates: {n_g}/7')
    print(f"=== {'FAIL — ' + str(len(errs)) + ' vi pham' if errs else 'PASS'} ===")
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
