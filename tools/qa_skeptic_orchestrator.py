"""
SVHMP QA → Skeptic Orchestrator — G2 round 14 Phase G
Lock date: 2026-06-26 (Mr.Long approve full automation chain)

Atomic chain: QA output → Skeptic invoke → final verdict.
Used by Director after Claude QA prompt completes + qa_output JSON written.

Decision tree:
  Claude QA verdict = FAIL              → REGEN (skeptic skipped)
  Claude QA verdict = PASS              → invoke skeptic
  Claude QA verdict = PASS_WITH_WARNING → invoke skeptic
  Claude QA verdict = REVIEW_REQUIRED   → human intervention (skeptic optional)

Skeptic verdict:
  ACCEPT + 0 critical missed  → final PASS, pipeline → TTS
  ACCEPT + minor missed       → final PASS, log skeptic findings (non-critical)
  REJECT                      → final REGEN scope=story_only, Generator re-write with skeptic feedback
  NEEDS_HUMAN                 → final REVIEW_REQUIRED, Mr.Long approve before proceed

Usage:
  python tools/qa_skeptic_orchestrator.py --ep 2 --episode output/ep_2/episode.md

Output:
  runtime/final_verdict_ep_2.json (atomic write)
"""
import argparse
import json
import subprocess

CREATE_NO_WINDOW = 0x08000000 if __import__("sys").platform == "win32" else 0
import sys
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
RUNTIME_DIR = SVHMP / 'runtime'


def atomic_write_json(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_fd, tmp_path = tempfile.mkstemp(prefix=f'.{path.stem}_', suffix='.tmp', dir=str(path.parent))
    try:
        with os.fdopen(tmp_fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        try: os.unlink(tmp_path)
        except Exception: pass
        raise


def orchestrate(ep_number: int, episode_path: str, skeptic_provider: str = 'ollama_local',
                run_vnqa: bool = True, run_autofix: bool = True,
                autofix_mode: str = 'apply') -> dict:
    """Run full chain: AUTO_FIX → VNQA → QA → Skeptic → final verdict.

    Round 14 Phase H4 wire: auto_fix BEFORE VNQA (registry literal map apply).
    autofix_mode: 'apply' = atomic ghi + backup | 'propose' = chỉ tạo .proposed_fix file.
    """
    qa_output_path = RUNTIME_DIR / f'qa_output_ep_{ep_number}.json'
    final_verdict_path = RUNTIME_DIR / f'final_verdict_ep_{ep_number}.json'
    skeptic_path = RUNTIME_DIR / f'adversarial_skeptic_ep_{ep_number}.json'
    vnqa_path = RUNTIME_DIR / f'vnqa_ep_{ep_number}.json'
    autofix_log_path = RUNTIME_DIR / f'autofix_ep_{ep_number}.json'

    # Phase H4 wire: AUTO_FIX BEFORE VNQA (registry literal map Mr.Long approved)
    autofix_result = None
    if run_autofix:
        try:
            autofix_cmd = [
                'python', str(SVHMP / 'tools' / 'vnqa' / 'auto_fix.py'),
                '--episode', episode_path,
                '--ep', str(ep_number),
            ]
            if autofix_mode == 'apply':
                autofix_cmd.append('--apply')
            print(f"[orchestrator] Running auto_fix ({autofix_mode} mode)...")
            af_run = subprocess.run(autofix_cmd, capture_output=True, text=True,
                                    encoding='utf-8', errors='replace', timeout=60, creationflags=CREATE_NO_WINDOW)
            autofix_result = {
                'mode': autofix_mode,
                'returncode': af_run.returncode,
                'stdout_tail': (af_run.stdout or '')[-500:],
                'success': af_run.returncode == 0,
            }
            atomic_write_json(autofix_log_path, autofix_result)
            print(f"[orchestrator] auto_fix done: rc={af_run.returncode}")
        except Exception as e:
            print(f"[orchestrator] auto_fix error: {e}")
            autofix_result = {'error': str(e), 'success': False}

    if not qa_output_path.exists():
        return {
            'error': f'QA output missing: {qa_output_path}',
            'recommendation': 'Run Claude QA first + write JSON via tools/qa_output_writer.py',
            'autofix_result': autofix_result,
            'success': False,
        }

    # Phase H wire: VNQA library check BEFORE skeptic
    vnqa_result = None
    if run_vnqa:
        try:
            vnqa_cmd = [
                'python', str(SVHMP / 'tools' / 'vnqa' / 'pipeline.py'),
                '--episode', episode_path,
                '--output', str(vnqa_path),
                '--ep', str(ep_number),
            ]
            print(f"[orchestrator] Running VNQA library check (H1-H10)...")
            vnqa_run = subprocess.run(vnqa_cmd, capture_output=True, text=True,
                                      encoding='utf-8', errors='replace', timeout=120, creationflags=CREATE_NO_WINDOW)
            if vnqa_run.returncode == 0 and vnqa_path.exists():
                with open(vnqa_path, encoding='utf-8') as f:
                    vnqa_result = json.load(f)
            else:
                print(f"[orchestrator] VNQA skipped: {vnqa_run.stderr[:200]}")
        except Exception as e:
            print(f"[orchestrator] VNQA error: {e}")

    with open(qa_output_path, encoding='utf-8') as f:
        qa_output = json.load(f)
    qa_verdict = qa_output.get('verdict', 'UNKNOWN')

    # Decision: skip skeptic if QA already FAIL (regen anyway) or REVIEW_REQUIRED (human anyway)
    if qa_verdict == 'REGEN':
        result = {
            'ep_number': ep_number,
            'qa_verdict': qa_verdict,
            'skeptic_invoked': False,
            'skeptic_reason_skipped': 'QA verdict REGEN — skeptic skipped (going REGEN anyway)',
            'final_verdict': 'REGEN',
            'final_reasoning': qa_output.get('verdict_reasoning', ''),
            'ts': datetime.now(timezone.utc).isoformat(),
        }
        atomic_write_json(final_verdict_path, result)
        return result

    # Invoke skeptic
    print(f"[orchestrator] QA verdict={qa_verdict} → invoking skeptic ({skeptic_provider})...")
    skeptic_cmd = [
        'python', str(SVHMP / 'tools' / 'adversarial_skeptic.py'),
        '--qa-output', str(qa_output_path),
        '--episode', episode_path,
        '--output', str(skeptic_path),
        '--provider', skeptic_provider,
    ]
    skeptic_run = subprocess.run(skeptic_cmd, capture_output=True, text=True,
                                  encoding='utf-8', errors='replace', timeout=300, creationflags=CREATE_NO_WINDOW)
    if skeptic_run.returncode != 0:
        result = {
            'ep_number': ep_number,
            'qa_verdict': qa_verdict,
            'skeptic_invoked': True,
            'skeptic_error': skeptic_run.stderr[:500],
            'final_verdict': 'REVIEW_REQUIRED',
            'final_reasoning': 'Skeptic failed — Mr.Long manual review needed',
            'ts': datetime.now(timezone.utc).isoformat(),
        }
        atomic_write_json(final_verdict_path, result)
        return result

    # Read skeptic verdict
    with open(skeptic_path, encoding='utf-8') as f:
        skeptic = json.load(f)
    skeptic_verdict = skeptic.get('final_verdict', 'NEEDS_HUMAN')
    missed = skeptic.get('missed_issues', []) or []
    critical_missed = [m for m in missed if m.get('severity') == 'critical']

    # Decision tree
    if skeptic_verdict == 'ACCEPT' and not critical_missed:
        final = 'PASS'
        reasoning = f'QA={qa_verdict} + Skeptic ACCEPT, {len(missed)} non-critical issues noted.'
    elif skeptic_verdict == 'ACCEPT' and critical_missed:
        final = 'REVIEW_REQUIRED'
        reasoning = f'Skeptic ACCEPT but {len(critical_missed)} CRITICAL missed issues — human review.'
    elif skeptic_verdict == 'REJECT':
        final = 'REGEN'
        reasoning = f'Skeptic REJECT: {skeptic.get("verdict_reasoning", "")[:200]}'
    elif skeptic_verdict == 'NEEDS_HUMAN':
        final = 'REVIEW_REQUIRED'
        reasoning = 'Skeptic NEEDS_HUMAN verdict.'
    else:
        final = 'REVIEW_REQUIRED'
        reasoning = f'Unknown skeptic verdict: {skeptic_verdict}'

    # VNQA verdict integration (Phase H wire)
    vnqa_verdict = (vnqa_result or {}).get('verdict')
    vnqa_issues = (vnqa_result or {}).get('issues_count_by_severity', {})

    # Escalate final if VNQA finds critical issues
    if vnqa_verdict == 'FAIL':
        final = 'REGEN'
        reasoning += f' [VNQA FAIL: {vnqa_issues}]'
    elif vnqa_verdict == 'WARN' and final == 'PASS':
        # VNQA WARN: KHONG downgrade ACCEPT->REGEN, nhung danh dau PASS_WITH_WARNING.
        # Canonical mapping WARN -> PASS_WITH_WARNING (qa_verdict_schema_proposal.yaml:88,146)
        # per Mr.Long authorization 10/7 (G8-7). Truoc day quen gan `final` -> enum dead:
        # next_action:224 + exit_code:255 co san nhung final khong bao gio nhan gia tri nay.
        final = 'PASS_WITH_WARNING'
        reasoning += f' [VNQA WARN: {vnqa_issues}]'

    result = {
        'ep_number': ep_number,
        'autofix_invoked': run_autofix and autofix_result is not None,
        'autofix_mode': autofix_mode if run_autofix else None,
        'autofix_success': (autofix_result or {}).get('success', False),
        'qa_verdict': qa_verdict,
        'qa_findings_count': len(qa_output.get('findings', [])),
        'vnqa_invoked': run_vnqa and vnqa_result is not None,
        'vnqa_verdict': vnqa_verdict,
        'vnqa_issues_count': vnqa_issues,
        'skeptic_invoked': True,
        'skeptic_provider': skeptic_provider,
        'skeptic_verdict': skeptic_verdict,
        'skeptic_attacked_count': len(skeptic.get('attacked_qa_findings', [])),
        'skeptic_missed_count': len(missed),
        'skeptic_critical_missed_count': len(critical_missed),
        'final_verdict': final,
        'final_reasoning': reasoning,
        'ts': datetime.now(timezone.utc).isoformat(),
        'next_action': {
            'PASS': 'pipeline → TTS render',
            'PASS_WITH_WARNING': 'pipeline → TTS render (warnings logged)',
            'REGEN': 'Generator re-write with skeptic+VNQA feedback (scope=story_only|language_only)',
            'REVIEW_REQUIRED': 'Mr.Long review final_verdict + skeptic missed + VNQA issues',
        }.get(final, 'unknown'),
    }
    atomic_write_json(final_verdict_path, result)
    return result


def cli():
    parser = argparse.ArgumentParser(description='SVHMP QA → Skeptic Orchestrator (G2 round 14 + Phase H4 autofix)')
    parser.add_argument('--ep', type=int, required=True)
    parser.add_argument('--episode', type=str, required=True)
    parser.add_argument('--provider', type=str, default='ollama_local',
                        help='Skeptic provider (ollama_local=gemma2:9b | ollama_qwen=qwen2.5:14b)')
    parser.add_argument('--no-autofix', action='store_true', help='Skip Phase H4 auto_fix step')
    parser.add_argument('--no-vnqa', action='store_true', help='Skip Phase H VNQA library check')
    parser.add_argument('--autofix-mode', type=str, default='apply', choices=['apply', 'propose'],
                        help='apply = atomic ghi + backup | propose = chỉ tạo .proposed_fix file')
    args = parser.parse_args()

    result = orchestrate(args.ep, args.episode, args.provider,
                         run_vnqa=not args.no_vnqa,
                         run_autofix=not args.no_autofix,
                         autofix_mode=args.autofix_mode)
    print()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result.get('success', True) and 'error' in result:
        sys.exit(1)
    # Exit code mapping for shell pipelines
    final = result.get('final_verdict', 'UNKNOWN')
    exit_code = {'PASS': 0, 'PASS_WITH_WARNING': 0, 'REGEN': 10, 'REVIEW_REQUIRED': 20}.get(final, 1)
    sys.exit(exit_code)


if __name__ == '__main__':
    cli()
