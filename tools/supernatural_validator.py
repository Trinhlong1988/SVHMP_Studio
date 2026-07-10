"""D5 — Supernatural Validator (TASK_G5_SUPERNATURAL.md, CMD_BUILD_3 4-5/7).
Validate CAU TRUC typology proposal (D1) + possession state machine (D3) — KHONG
quet noi dung episode that (do la viec runtime scanner cua G8, xem
reports/G5_HANDOFF_G8.md). Enum sensitivity doc TRUC TIEP tu
governance/blueprint/bp9/content_policy.yaml (KHONG hardcode list — neu BP9 mo
rong enum, validator nay tu dong theo, khong can sua code).

R211 RECONCILE (2026-07-05, fix/g5-4-possession-dup): possession KHONG con la state
machine rieng trong runtime/supernatural_state_machine.yaml (da bi audit xac nhan
la nhan doi voi entity 'ghost' cua governance/blueprint/bp4/state_machines.yaml).
check_possession_state_machine() gio doc THANG tu bp4/state_machines.yaml entity
'ghost' (da duoc MO RONG them state 'entering'/'exorcising' de gia dung ngu nghia
possession) — xem note tai bp4/state_machines.yaml#entity=ghost va
reports/G5_FIX_POSSESSION_DEDUP.md.

Mutation coverage (TASK_G5 "MUTATION AUDIT SE BAN"):
  M1 nang luc ngoai typology -> check_claimed_powers()
  M2 nghi le khong map cultural_spec (bp7 facet ma) -> check_typology()
  M3 possession khong truc xuat (treo mai) -> check_possession_state_machine()
  M4 sensitivity ngoai enum BP9 -> check_typology()
  M7 tool tu tao trung bp9_compliance_check.py/content_policy.yaml -> check_no_duplicate_compliance_files()
M6 (entity_class thieu o nhan vat linh_hon) CHUA enforce duoc: D2 (entity_class vao
bible/37) khong lam trong pham vi CMD_BUILD_3 lan nay (bible/*.yaml bi cam, bp2 dang
LOCKED, can RFC + Mr.Long authorization rieng) — ghi ro ROADMAP, khong bia check gia.
"""
import re
import sys
from pathlib import Path

import yaml

SVHMP = Path(__file__).resolve().parent.parent
TYPOLOGY = SVHMP / 'governance' / 'proposals' / 'supernatural_typology_proposal.yaml'
STATE_MACHINE = SVHMP / 'governance' / 'blueprint' / 'bp4' / 'state_machines.yaml'
POSSESSION_ENTITY = 'ghost'
CULTURAL_SPEC = SVHMP / 'governance' / 'blueprint' / 'bp7' / 'cultural_spec.yaml'
CONTENT_POLICY = SVHMP / 'governance' / 'blueprint' / 'bp9' / 'content_policy.yaml'


def _load(p):
    return yaml.safe_load(Path(p).read_text(encoding='utf-8'))


def valid_sensitivity_values(content_policy=None):
    """M4: doc dung enum tu BP9, KHONG hardcode list (chong-drift neu BP9 doi enum)."""
    cp = content_policy if content_policy is not None else _load(CONTENT_POLICY)
    return set((cp.get('sensitivity_tiers') or {}).keys())


def valid_bp7_facets(cultural_spec=None):
    cs = cultural_spec if cultural_spec is not None else _load(CULTURAL_SPEC)
    return {item['domain_facet'] for item in (cs.get('items') or [])}


def check_typology(typology=None, valid_sensitivity=None, valid_facets=None):
    """M2 + M4 tren D1 typology proposal."""
    ty = typology if typology is not None else _load(TYPOLOGY)
    v_sens = valid_sensitivity if valid_sensitivity is not None else valid_sensitivity_values()
    v_facets = valid_facets if valid_facets is not None else valid_bp7_facets()
    errs = []
    ids = []
    for e in ty.get('entities') or []:
        eid = e.get('entity_type', '?')
        ids.append(eid)
        sens = e.get('sensitivity')
        if sens not in v_sens:
            errs.append(f"{eid}: sensitivity {sens!r} khong thuoc enum BP9 {sorted(v_sens)} (M4)")
        facet_raw = (e.get('nguon_goc') or {}).get('bp7_facet_mirror') or ''
        facet_id = facet_raw.split(' ')[0] if facet_raw else ''
        if facet_id and facet_id not in v_facets:
            errs.append(f"{eid}: bp7_facet_mirror {facet_id!r} khong ton tai trong "
                        f"bp7/cultural_spec.yaml (M2 facet-ma)")
        ev = (e.get('nguon_goc') or {}).get('evidence') or {}
        if ev.get('status') not in ('verified', 'hypothesis'):
            errs.append(f"{eid}: evidence.status {ev.get('status')!r} khong hop le "
                        "(phai verified|hypothesis)")
    if len(ids) != len(set(ids)):
        errs.append(f"entity_type trung: {ids}")
    return errs


def _reachable_to(edges, target):
    """BFS nguoc: tra ve set state co duong di TOI target (qua 0..N canh)."""
    reach = {target}
    changed = True
    while changed:
        changed = False
        for (frm, to) in edges:
            if to in reach and frm not in reach:
                reach.add(frm)
                changed = True
    return reach


def _find_state_machine_entity(data, entity_name):
    for m in (data.get('state_machines') or []):
        if m.get('entity') == entity_name:
            return m
    return None


def check_possession_state_machine(sm=None):
    """M3: moi state (tru 'released') phai co duong toi 'released' — chong treo mai.

    R211 RECONCILE: possession KHONG con la key 'possession_state_machine' rieng —
    doc THANG tu bp4/state_machines.yaml entity 'ghost' (da MO RONG them state
    'entering'/'exorcising' de chi tiet hoa qua trinh possession, xem note tai
    bp4/state_machines.yaml#entity=ghost)."""
    data = sm if sm is not None else _load(STATE_MACHINE)
    entity = _find_state_machine_entity(data, POSSESSION_ENTITY)
    errs = []
    if entity is None:
        errs.append(f"bp4/state_machines.yaml: khong tim thay entity {POSSESSION_ENTITY!r} "
                    "(possession reconcile)")
        return errs
    states = entity.get('states') or []
    transitions = entity.get('transitions') or []
    if 'released' not in states:
        errs.append(f"{POSSESSION_ENTITY} state machine: khong co state 'released' "
                    "(khong the truc xuat)")
        return errs
    edges = [(t['from'], t['to']) for t in transitions]
    reach = _reachable_to(edges, 'released')
    stuck = [s for s in states if s != 'released' and s not in reach]
    if stuck:
        errs.append(f"{POSSESSION_ENTITY} state {stuck} KHONG co duong toi 'released' "
                    "(M3 treo mai)")
    return errs


def check_claimed_powers(entity_type, claimed_powers, typology=None):
    """M1 — API tai dung cho consumer tuong lai (vd G8 runtime scanner): claimed_powers
    la list chuoi tu do, FAIL neu KHONG duoc nhac toi (substring, khong phan biet hoa
    thuong) trong entity.quyen_nang da khai."""
    ty = typology if typology is not None else _load(TYPOLOGY)
    entity = next((e for e in ty.get('entities') or [] if e.get('entity_type') == entity_type), None)
    if entity is None:
        return [f"entity_type {entity_type!r} khong ton tai trong typology (M1)"]
    known = (entity.get('quyen_nang') or '').lower()
    errs = []
    for p in claimed_powers:
        if p.lower() not in known:
            errs.append(f"{entity_type}: quyen nang '{p}' KHONG co trong typology da khai (M1)")
    return errs


def check_no_duplicate_compliance_files():
    """M7 (R211, tuyet doi): tu-guard cam CMD_BUILD_3 tao file trung BP9."""
    errs = []
    forbidden = [SVHMP / 'bible' / 'content_policy.yaml',
                 SVHMP / 'tools' / 'compliance_check.py']
    for f in forbidden:
        if f.exists():
            errs.append(f"M7 R211: {f.relative_to(SVHMP)} TON TAI — trung BP9, PHAI xoa/khong tao")
    return errs


def run_all():
    errs = []
    errs += check_typology()
    errs += check_possession_state_machine()
    errs += check_no_duplicate_compliance_files()
    return errs


def _run_all_body_ok(src):
    """Pure check TREN SOURCE TEXT (10/7, per Mr.Long authorization - TASK_AUDIT_CRITICAL_
    G3_G5.md Bug #2, CMD_AUDIT phat hien run_all() KHONG co test composition that): body ham
    run_all() PHAI goi DU CA 3 sub-check (check_typology/check_possession_state_machine/
    check_no_duplicate_compliance_files) - neu ai vo tinh xoa 1 dong 'errs += check_*()',
    gate g5_supernatural_check.py van bao PASS tren du lieu sach vi 2 sub-check con lai khong
    phat hien loi. Ham nay generalize tu tools/g8_qa_runtime_check.py::_pause_delegation_
    body_ok (mirror pattern: pure check tren source text, dung chung boi gate va mutation-
    proof test, R211 khong viet lai logic tu dau)."""
    m = re.search(r"def run_all\(.*?\n(?=def |\Z)", src, re.DOTALL)
    if not m:
        return False, "khong tim thay ham run_all() trong supernatural_validator.py"
    body = m.group(0)
    required = ["check_typology()", "check_possession_state_machine()",
                "check_no_duplicate_compliance_files()"]
    missing = [c for c in required if f"errs += {c}" not in body]
    if missing:
        return False, f"run_all() thieu loi goi 'errs += {{sub-check}}()': {missing}"
    return True, "run_all() goi du 3/3 sub-check (typology/possession/compliance)"


if __name__ == '__main__':
    problems = run_all()
    for p in problems:
        print(f"  [VIOLATION ONT5001] {p}")
    print(f"=== {'FAIL — ' + str(len(problems)) + ' vi pham' if problems else 'PASS'} ===")
    sys.exit(1 if problems else 0)
