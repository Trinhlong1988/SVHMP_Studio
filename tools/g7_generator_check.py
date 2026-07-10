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
  no_write_domain     commit(s) HEAD chua len origin/main (G7-1 10/7: doi tu working-
                      tree diff luon rong luc pre-push sang merge-base..HEAD, kiem
                      DUNG noi dung sap push) KHONG duoc chua bat ky file domain nguon
                      nao (doc DONG tu blueprint_domains.yaml dependencies cua
                      generator, khong hardcode list rieng - R211 reconcile) trong
                      CUNG commit(s) voi tools/episode_generator.py
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


def _changed_files_vs_origin_main(repo=None):
    """G7-1 (audit HIGH, TASK_AUDIT_HIGH_G2_G8.md): tra ve set file thay doi trong cac
    commit HEAD CHUA co tren origin/main (git diff merge-base(origin/main,HEAD)..HEAD)
    - day la noi dung THAT SU sap len remote luc push, KHAC voi working-tree diff (luon
    rong sau khi da commit). Tra ve None neu KHONG resolve duoc origin/main (vd repo
    chua fetch/chua co remote) - caller PHAI tu quyet dinh fallback, KHONG duoc am
    tham coi None nhu '0 file thay doi' (se che mat that bai that, dung loi cu R7-1
    dang sua)."""
    repo = repo or REPO
    base_r = subprocess.run(['git', 'merge-base', 'HEAD', 'origin/main'], capture_output=True,
                            text=True, cwd=str(repo), encoding='utf-8')
    if base_r.returncode != 0 or not base_r.stdout.strip():
        return None
    merge_base = base_r.stdout.strip()
    diff_r = subprocess.run(['git', 'diff', '--name-only', f'{merge_base}..HEAD'],
                            capture_output=True, text=True, cwd=str(repo), encoding='utf-8')
    return set(diff_r.stdout.strip().splitlines()) if diff_r.stdout.strip() else set()


def _stage_no_write_domain() -> dict:
    """G7-1 redesign (10/7, per Mr.Long authorization, TASK_AUDIT_HIGH_G2_G8.md): ban
    cu dung 'git diff --name-only HEAD' (working-tree vs HEAD) - LUON RONG dung luc
    pre-push chay that (da commit xong, working-tree sach voi HEAD), nen check nay
    tu-skip 100% thoi gian o dung tinh huong can kiem nhat (dang push code moi). Doi
    sang so sanh commit(s) HEAD CHUA len origin/main (qua _changed_files_vs_origin_
    main()) - kiem DUNG noi dung sap len remote, khop dung y nghia 'dang push cai gi'.

    origin/main khong resolve duoc -> FAIL AN TOAN (rc=1), KHONG im lang bo qua check
    (dung tinh than R195/R_SUPREME 'uncertainty -> STOP khong ACT', tranh lap lai
    chinh loi 'check tu-skip am tham' dang sua)."""
    try:
        changed = _changed_files_vs_origin_main()
        if changed is None:
            return {'rc': 1, 'tail': "khong resolve duoc origin/main (git merge-base that bai) "
                                     "- khong xac dinh duoc commit(s) sap push, FAIL an toan "
                                     "thay vi im lang bo qua check (chay 'git fetch origin main' truoc)"}
        generator_rel = str(GENERATOR_MODULE.relative_to(REPO)).replace('\\', '/')
        if generator_rel not in changed:
            return {'rc': 0, 'tail': f'tools/episode_generator.py khong doi trong {len(changed)} '
                                     'file cua commit(s) chua len origin/main - skip'}
        domain_paths = _generator_dependency_source_paths()
        overlap = changed & domain_paths
        if overlap:
            return {'rc': 1, 'tail': f'generator dang sua CUNG commit(s) voi domain nguon '
                                     f'(chua len origin/main): {overlap}'}
        return {'rc': 0, 'tail': f'0/{len(domain_paths)} domain source bi dung cham trong '
                                 f'{len(changed)} file cua commit(s) chua len origin/main'}
    except Exception as e:  # noqa: BLE001
        return {'rc': 1, 'tail': f'no_write_domain EXCEPTION: {e!r}'}


def _stage_static_no_write_src() -> dict:
    """Mirror tests/test_g7_generator.py::test_module_source_has_no_write_calls_to_domain_files
    - kiem tra LAI o day (khong phu thuoc pytest) de gate tu dung duoc doc lap."""
    src = GENERATOR_MODULE.read_text(encoding='utf-8')
    # audit ML #21 (10/7): mo rong pattern - ngoai open/write_text/write_bytes, cam ca ghi/exec
    # GIAN TIEP (shutil.copy/move, os.system, subprocess, os.replace) co the ne truoc do.
    # Van text-grep (nhat quan cach tiep can codebase, khong AST) - chi mo rong do phu.
    forbidden = ['open(', '.write_text(', '.write_bytes(', 'shutil.copy', 'shutil.move',
                 'os.system', 'subprocess', 'os.replace']
    hit = [p for p in forbidden if p in src]
    if hit:
        return {'rc': 1, 'tail': f'source chua pattern ghi/exec bi cam (read-only): {hit}'}
    return {'rc': 0, 'tail': '0 loi goi ghi/exec file trong source'}


def run_suite():
    rows = []
    rows.append({'key': 'pytest', 'detail': 'tests/test_g7_generator.py',
                 **_run_pytest('tests/test_g7_generator.py')})
    rows.append({'key': 'self_check', 'detail': 'python tools/episode_generator.py 1',
                 **_stage_self_check()})
    rows.append({'key': 'budget_sheet_M4', 'detail': 'moi scene EP01 co budget sheet du knob',
                 **_stage_budget_sheet_m4()})
    rows.append({'key': 'no_write_domain', 'detail': 'commit(s) chua len origin/main: generator vs 14 domain source',
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
