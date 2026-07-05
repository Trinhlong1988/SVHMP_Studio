"""G3 DIALOGUE CHECK v1.0.0 — GATE 1 CUA cho domain dialogue (TASK_G3_DIALOGUE.md D7).

Mirror pattern tools/g4_world_check.py / tools/g5_supernatural_check.py: goi tuan tu cac
stage, in matrix PASS/FAIL, KHONG short-circuit (chay het roi moi ket luan), exit 0 CHI KHI
tat ca xanh. Ghi runtime/reports/dialogue_system_report.md (mirror
runtime/reports/character_system_report.md).

  D3_D4_pytest        pytest tests/test_g3_dialogue.py (generator + validate_generated_batch)
  D5_confusion_pytest pytest tests/test_g3_dialogue_confusion.py (confusion matrix 0FN/0FP)
  validators_smoke    3 validator hien co (dialog_voice_validator, audit_dialogue_hierarchy,
                       audit_driver_dialogue_context) IMPORT + GOI that tren 1 case sach biet
                       truoc (sanity, KHONG quet lai toan bo 50 tap - no ky thuat 34 HIGH cua
                       corpus cu KHONG phai viec cua gate nay, xem reports/G3_REALITY_AUDIT.md)
  D3_generator_real   dialogue_generator.generate_line() chay that tren >=10 passenger THAT
                       da vung tu roster (REALITY ANCHOR TASK D3)
  G3_7_output_audit_real  DONG KHOANG TRONG G3-7 (kiem duyet doc lap 5/7): ghi output THAT
                       (output/ep_g3_sample/episode.md, KHONG bao gio dung 50 tap that) roi
                       chay 2 tool audit cu TREN CHINH file do — xac nhan chung QUET DUOC
                       (khong phai 0-file PASS RONG khi G3 sinh o path khac output/ep_NN/)

R191 (qa_dialogue_identity.py) KHONG wire vao gate nay (can WAV da render, ci_gate chay
TRUOC render) - xem reports/G3_HANDOFF_G8.md.
"""
import os
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable
sys.path.insert(0, str(REPO / 'tools'))

__version__ = '1.0.0'

# Re-entrancy guard (mirror tools/ci_gate.py _PYTEST_GUARD pattern — lesson-ci-gate-pytest-
# recursion): tests/test_g3_dialogue.py::test_g3_dialogue_check_gate_runs_and_writes_report
# goi LAI chinh g3_dialogue_check.py nay qua subprocess. Neu KHONG co guard, stage
# D3_D4_pytest o duoi se goi `pytest tests/test_g3_dialogue.py` -> gap lai chinh test do ->
# goi lai g3_dialogue_check.py -> goi lai pytest -> ... de quy vo han (fork-bomb THAT da xay
# ra 1 lan trong qua trinh build, xem git history/PING). Set env nay khi tu goi pytest o day;
# test tuong ung PHAI tu skip khi thay guard (xem tests/test_g3_dialogue.py).
_PYTEST_GUARD = 'SVHMP_G3_GATE_PYTEST_RUNNING'


def _run_pytest(rel_path: str) -> dict:
    if os.environ.get(_PYTEST_GUARD):
        return {'rc': 0, 'tail': '[SKIP] re-entrant guard active - khong goi pytest long nhau'}
    env = dict(os.environ)
    env[_PYTEST_GUARD] = '1'
    r = subprocess.run([PY, '-m', 'pytest', rel_path, '-q'], capture_output=True, text=True,
                        cwd=str(REPO), env=env, encoding='utf-8')
    return {'rc': r.returncode, 'tail': ((r.stdout or '') + (r.stderr or ''))[-500:]}


def _stage_validators_smoke() -> dict:
    """Sanity import + goi that tren 1 case SACH biet truoc - khong phai full-corpus scan."""
    try:
        import dialog_voice_validator as dvv
        from audit_dialogue_hierarchy import detect_pronoun_issues_in_quote
        from audit_driver_dialogue_context import audit_text

        clean_profile = {'region_dialect': 'bac', 'hometown': 'Hà Nội', 'pronoun_system': 'tôi'}
        assert dvv.validate_line(clean_profile, 'Con về nhé mẹ.') == [], 'dvv sanity clean FAIL'
        assert dvv.validate_line(clean_profile, 'Con dìa nghen.') != [], 'dvv sanity leak FAIL'

        assert detect_pronoun_issues_in_quote('Con nhớ mẹ nhiều lắm.') == [], 'pronoun sanity clean FAIL'

        rpt = audit_text('"Con đã nhớ ra chưa?"', src='<sanity>')
        assert rpt['verdict'] == 'PASS', 'driver-context sanity Q1 FAIL'
        return {'rc': 0, 'tail': 'dvv + pronoun + driver-context sanity: OK'}
    except Exception as e:  # noqa: BLE001
        return {'rc': 1, 'tail': f'validators_smoke EXCEPTION: {e!r}'}


def _stage_generator_real_data() -> dict:
    try:
        from dialogue_manager import DialogueManager
        from dialogue_generator import generate_line
        dm = DialogueManager()
        pas = [c for c in dm.registry.all('passenger') if c.assigned_ep][:15]
        if len(pas) < 10:
            return {'rc': 1, 'tail': f'chi co {len(pas)} passenger co assigned_ep (< 10)'}
        regions = set()
        ok = 0
        for c in pas:
            r = generate_line(c.id, {'emotion_beat': 'nhớ nhà', 'listener_call': 'Mẹ ơi'}, dm)
            regions.add(c.voice.region_dialect)
            if r['status'] == 'OK':
                ok += 1
        if len(regions) < 3:
            return {'rc': 1, 'tail': f'chi {len(regions)} vung ({regions}), can >=3'}
        if ok < 10:
            return {'rc': 1, 'tail': f'chi {ok}/{len(pas)} sinh OK (can >=10)'}
        return {'rc': 0, 'tail': f'{ok}/{len(pas)} OK, vung={sorted(regions)}'}
    except Exception as e:  # noqa: BLE001
        return {'rc': 1, 'tail': f'generator_real_data EXCEPTION: {e!r}'}


SANDBOX_DIR = REPO / 'output' / 'ep_g3_sample'


def _stage_output_audit_real() -> dict:
    """G3-7 (kiem duyet doc lap 5/7): sinh 1 dong thoai THAT + ghi ra sandbox path THAT
    (output/ep_g3_sample/episode.md — ten CHU, khong bao gio trung so tap that/tuong lai),
    roi chay 2 tool audit cu (audit_driver_dialogue_context.py qua --file, audit_dialogue_
    hierarchy.audit_ep() import truc tiep — ham nay khong phu thuoc duong dan, chi can text)
    NGAY TREN file do. Assert ca 2 THAT SU quet duoc noi dung (>=1 quote extract duoc), khong
    phai 0-file/0-quote PASS RONG."""
    try:
        from dialogue_manager import DialogueManager
        from dialogue_generator import generate_line, write_episode_line
        from audit_dialogue_hierarchy import audit_ep, extract_quotes

        dm = DialogueManager()
        pas = [c for c in dm.registry.all('passenger') if c.assigned_ep]
        sample = next((c for c in pas if generate_line(
            c.id, {'emotion_beat': 'nhớ nhà', 'listener_call': 'Mẹ ơi'}, dm)['status'] == 'OK'), None)
        if sample is None:
            return {'rc': 1, 'tail': 'khong tim duoc passenger nao sinh OK de ghi sandbox'}
        r = generate_line(sample.id, {'emotion_beat': 'nhớ nhà', 'listener_call': 'Mẹ ơi'}, dm)

        out_path = write_episode_line(REPO / 'output', 'g3_sample', r['line'],
                                      header_kv={'g3_sandbox': 'true', 'character_id': sample.id})
        if out_path.resolve() != (SANDBOX_DIR / 'episode.md').resolve():
            return {'rc': 1, 'tail': f'sandbox path sai vi tri: {out_path}'}

        text = out_path.read_text(encoding='utf-8')
        quotes = extract_quotes(text)
        if not quotes:
            return {'rc': 1, 'tail': f'extract_quotes() 0 quote tren {out_path} — 0-quote PASS RONG (G3-7)'}

        rel = out_path.relative_to(REPO).as_posix()
        p = subprocess.run([PY, 'tools/audit_driver_dialogue_context.py', '--file', rel],
                           capture_output=True, text=True, cwd=str(REPO), encoding='utf-8')
        if 'MISSING' in (p.stdout or ''):
            return {'rc': 1, 'tail': f'audit_driver_dialogue_context.py bao MISSING tren {rel} (khong quet duoc)'}

        issues = audit_ep(0, text, detail=False)
        return {'rc': 0, 'tail': f'{out_path.relative_to(REPO)}: {len(quotes)} quote extract duoc, '
                                  f'audit_driver rc={p.returncode}, audit_ep() chay xong ({len(issues)} issue)'}
    except Exception as e:  # noqa: BLE001
        return {'rc': 1, 'tail': f'output_audit_real EXCEPTION: {e!r}'}


def run_suite():
    rows = []
    rows.append({'key': 'D3_D4_pytest', 'detail': 'tests/test_g3_dialogue.py',
                 **_run_pytest('tests/test_g3_dialogue.py')})
    rows.append({'key': 'D5_confusion_pytest', 'detail': 'tests/test_g3_dialogue_confusion.py',
                 **_run_pytest('tests/test_g3_dialogue_confusion.py')})
    rows.append({'key': 'validators_smoke', 'detail': '3 validator hien co (import+call sanity)',
                 **_stage_validators_smoke()})
    rows.append({'key': 'D3_generator_real', 'detail': '>=10 passenger that, >=3 vung',
                 **_stage_generator_real_data()})
    rows.append({'key': 'G3_7_output_audit_real',
                 'detail': 'output/ep_g3_sample/episode.md that + 2 tool audit cu quet tren do',
                 **_stage_output_audit_real()})
    return rows


def _write_report(rows, overall_pass: bool):
    out = REPO / 'runtime' / 'reports' / 'dialogue_system_report.md'
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = [f'# G3 Dialogue System Report (g3_dialogue_check.py v{__version__})', '',
             f'STATUS: {"PASS" if overall_pass else "FAIL"}', '', '| Stage | Detail | rc |',
             '|---|---|---|']
    for row in rows:
        lines.append(f"| {row['key']} | {row['detail']} | {row['rc']} |")
    lines.append('')
    lines.append('R191 (qa_dialogue_identity.py) KHONG wire vao gate nay - can WAV da render, '
                 'ci_gate chay TRUOC render. Xem reports/G3_HANDOFF_G8.md.')
    out.write_text('\n'.join(lines), encoding='utf-8')
    return out


def main():
    print(f'=== G3 DIALOGUE CHECK v{__version__} (D7 - 1 cua) ===')
    rows = run_suite()
    fails = [row for row in rows if row['rc'] != 0]
    for row in rows:
        mark = 'PASS' if row['rc'] == 0 else 'FAIL'
        print(f"  [{mark}] {row['key']:<22} {row['detail']} (exit {row['rc']})")
        if row['rc'] != 0:
            print(row['tail'])
    overall_pass = not fails
    out = _write_report(rows, overall_pass)
    print(f'Report: {out}')
    if fails:
        print(f"=== FAIL — {len(fails)}/{len(rows)} tang do: "
              f"{', '.join(row['key'] for row in fails)} ===")
        return 1
    print(f'=== PASS — {len(rows)}/{len(rows)} tang G3 dialogue xanh ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
