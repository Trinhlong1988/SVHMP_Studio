"""g7_generator_check.py — G7 GATE 1 CUA (mirror pattern g4_world_check.py /
g6_story_planner_check.py / g3_dialogue_check.py: goi tuan tu cac stage, in matrix
PASS/FAIL, KHONG short-circuit, exit 0 CHI KHI tat ca xanh).

Stage rieng cho generator (TASK_G7 D4), KHAC voi cac gate truoc vi generator co 2
rui ro dac thu khong gate nao khac gap: (a) doc 14 domain read-only — phai chung
minh KHONG ghi nguoc; (b) budget sheet PHAI di kem moi canh (M4), khong duoc thieu.

  pytest              tests/test_g7_generator.py (13 test, reality anchor; sua so 10/7 audit ML #23)
  self_check          python tools/episode_generator.py 1 (subprocess, exit 0)
  budget_sheet_M4     moi scene trong episode_plan_ref PHAI co budget/knobs tuong
                      ung trong decision_packet.per_scene (M4: "canh thieu budget
                      sheet dinh kem = VIOLATION")
  no_write_domain     git diff --name-only (working tree) KHONG duoc chua bat ky
                      file domain nguon nao (doc DONG tu blueprint_domains.yaml
                      dependencies cua generator, khong hardcode list rieng - R211
                      reconcile) trong CUNG lan thay doi voi tools/episode_generator.py
  static_no_write_src source code episode_generator.py KHONG duoc chua loi goi ghi
                      file (mirror test_module_source_has_no_write_calls_to_domain_files)

LUU Y (bai hoc G14 — ci_gate pytest fork-bomb): _PYTEST_GUARD ngan pytest goi lai
gate nay goi lai pytest vo han (mirror tools/g3_dialogue_check.py).
"""
import os
import subprocess
import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable
sys.path.insert(0, str(REPO / 'tools'))

__version__ = '1.0.0'

_PYTEST_GUARD = 'SVHMP_G7_GATE_PYTEST_RUNNING'

BLUEPRINT_DOMAINS = REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml'
GENERATOR_MODULE = REPO / 'tools' / 'episode_generator.py'


def _run_pytest(rel_path: str) -> dict:
    if os.environ.get(_PYTEST_GUARD):
        return {'rc': 0, 'tail': '[SKIP] re-entrant guard active - khong goi pytest long nhau'}
    env = dict(os.environ)
    env[_PYTEST_GUARD] = '1'
    r = subprocess.run([PY, '-m', 'pytest', rel_path, '-q'], capture_output=True, text=True,
                        cwd=str(REPO), env=env, encoding='utf-8')
    return {'rc': r.returncode, 'tail': ((r.stdout or '') + (r.stderr or ''))[-500:]}


def _stage_self_check() -> dict:
    r = subprocess.run([PY, str(GENERATOR_MODULE), '1'], capture_output=True, text=True,
                        cwd=str(REPO), encoding='utf-8')
    tail = ((r.stdout or '') + (r.stderr or ''))[-500:]
    return {'rc': r.returncode, 'tail': tail}


def _stage_budget_sheet_m4() -> dict:
    """M4: 'canh thieu budget sheet dinh kem = VIOLATION'. Kiem tren du lieu THAT
    (EP01, khong mock) - moi scene_id trong episode_plan_ref.scenes PHAI co 1 entry
    tuong ung trong decision_packet.per_scene voi >=1 knob khac None."""
    try:
        import episode_generator as eg
        packet = eg.build_episode_packet(1)
        plan = packet.get('episode_plan_ref')
        decision = packet.get('decision_packet')
        if not plan or not decision:
            return {'rc': 1, 'tail': 'thieu episode_plan_ref hoac decision_packet trong packet EP01'}
        plan_components = {s['component_ref'] for s in plan['scenes_detail']}
        per_scene = {row['scene_id']: row['knobs'] for row in decision['per_scene']}
        missing = plan_components - set(per_scene.keys())
        if missing:
            return {'rc': 1, 'tail': f'scene thieu budget sheet: {missing}'}
        empty = [sid for sid, knobs in per_scene.items()
                 if all(v is None for v in knobs.values())]
        if empty:
            return {'rc': 1, 'tail': f'scene co budget sheet nhung TOAN BO knob None: {empty}'}
        return {'rc': 0, 'tail': f'{len(plan_components)}/{len(plan_components)} scene co budget sheet du knob'}
    except Exception as e:  # noqa: BLE001
        return {'rc': 1, 'tail': f'budget_sheet_M4 EXCEPTION: {e!r}'}


def _generator_dependency_source_paths() -> set:
    """Doc DONG tu blueprint_domains.yaml (KHONG hardcode list rieng - R211 reconcile,
    bai hoc DEBT-005/006 'khong hardcode snapshot so lieu cua file khac'). Gom
    source_of_truth + manager.path (neu status=exists) cua 14 domain generator phu
    thuoc - day la tap file 'domain nguon' generator TUYET DOI khong duoc ghi vao."""
    domains = yaml.safe_load(BLUEPRINT_DOMAINS.read_text(encoding='utf-8'))['domains']
    deps = domains['generator']['dependencies']
    paths = set()
    for dep in deps:
        dd = domains.get(dep, {})
        for entry in dd.get('source_of_truth', []) or []:
            if isinstance(entry, dict) and entry.get('status') == 'exists':
                paths.add(entry['path'])
        mgr = dd.get('manager') or {}
        if isinstance(mgr, dict) and mgr.get('status') == 'exists' and mgr.get('path'):
            paths.add(mgr['path'])
    return paths


def _stage_no_write_domain() -> dict:
    """git diff --name-only (working tree, KHONG commit) - neu tools/episode_generator.py
    dang thay doi (dang lam viec tren no) thi KHONG duoc co bat ky domain source path
    nao (dong tu blueprint_domains.yaml) xuat hien CUNG trong diff do.

    PHAM VI (ghi ro, khong noi qua): CHI kiem working-tree diff hien tai luc gate chay
    (khop voi cach ci_gate.py chay pre-push tren state dang co) - KHONG doc lai toan bo
    lich su commit da push truoc do (qua ton kem, va cac lan push truoc da tung qua
    chinh gate nay roi)."""
    try:
        r = subprocess.run(['git', 'diff', '--name-only', 'HEAD'], capture_output=True,
                            text=True, cwd=str(REPO), encoding='utf-8')
        changed = set(r.stdout.strip().splitlines()) if r.stdout.strip() else set()
        generator_rel = str(GENERATOR_MODULE.relative_to(REPO)).replace('\\', '/')
        if generator_rel not in changed:
            return {'rc': 0, 'tail': 'tools/episode_generator.py khong doi trong working tree - skip (khong co gi de kiem)'}
        domain_paths = _generator_dependency_source_paths()
        overlap = changed & domain_paths
        if overlap:
            return {'rc': 1, 'tail': f'generator dang sua CUNG luc voi domain nguon: {overlap}'}
        return {'rc': 0, 'tail': f'0/{len(domain_paths)} domain source bi dung cham trong working tree diff'}
    except Exception as e:  # noqa: BLE001
        return {'rc': 1, 'tail': f'no_write_domain EXCEPTION: {e!r}'}


def _stage_static_no_write_src() -> dict:
    """Mirror tests/test_g7_generator.py::test_module_source_has_no_write_calls_to_domain_files
    - kiem tra LAI o day (khong phu thuoc pytest) de gate tu dung duoc doc lap."""
    src = GENERATOR_MODULE.read_text(encoding='utf-8')
    if 'open(' in src:
        return {'rc': 1, 'tail': 'source chua open( - vi pham read-only (forbidden_operations:write)'}
    if '.write_text(' in src or '.write_bytes(' in src:
        return {'rc': 1, 'tail': 'source chua write_text/write_bytes - vi pham read-only'}
    return {'rc': 0, 'tail': '0 loi goi ghi file trong source'}


def run_suite():
    rows = []
    rows.append({'key': 'pytest', 'detail': 'tests/test_g7_generator.py',
                 **_run_pytest('tests/test_g7_generator.py')})
    rows.append({'key': 'self_check', 'detail': 'python tools/episode_generator.py 1',
                 **_stage_self_check()})
    rows.append({'key': 'budget_sheet_M4', 'detail': 'moi scene EP01 co budget sheet du knob',
                 **_stage_budget_sheet_m4()})
    rows.append({'key': 'no_write_domain', 'detail': 'working-tree diff: generator vs 14 domain source',
                 **_stage_no_write_domain()})
    rows.append({'key': 'static_no_write_src', 'detail': 'source code khong co loi goi ghi file',
                 **_stage_static_no_write_src()})
    return rows


def main():
    print(f'=== G7 GENERATOR CHECK v{__version__} (D4 - 1 cua) ===')
    rows = run_suite()
    fails = [row for row in rows if row['rc'] != 0]
    for row in rows:
        mark = 'PASS' if row['rc'] == 0 else 'FAIL'
        print(f"  [{mark}] {row['key']:<20} {row['detail']} (exit {row['rc']})")
        if row['rc'] != 0:
            print(row['tail'])
    if fails:
        print(f"=== FAIL — {len(fails)}/{len(rows)} tang do: "
              f"{', '.join(row['key'] for row in fails)} ===")
        return 1
    print(f'=== PASS — {len(rows)}/{len(rows)} tang G7 generator xanh ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
