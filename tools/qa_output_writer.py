"""
SVHMP QA Output Writer — G1 round 14 Phase G
Lock date: 2026-06-26 (Mr.Long approve full automation QA → Skeptic chain)

Helper: enforce QA output format JSON → runtime/qa_output_ep_{N}.json
Used by Director after Claude QA prompt completes.

Schema strict (skeptic.py reads this format):
{
  "ep_number": int,
  "qa_version": "v1.4",
  "qa_timestamp_utc": ISO8601,
  "findings": [
    {
      "finding_id": "F<n>",
      "phase": "12.X",
      "type": "ALWAYS_5|NEVER_7|GHOST_RULES|arc_consistency|anti_slop|cove|...",
      "status": "PASS|WARN|FAIL",
      "severity": "ok|minor|major|critical",
      "detail": "<short reason>",
      "evidence_quote": "<from episode if applicable>",
      "regen_scope_if_fail": "<one of allowed_regen_scope or null>"
    }
  ],
  "scores": {
    "content_score": 0-100,
    "axis_breakdown": {...}
  },
  "verdict": "PASS | PASS_WITH_WARNING | REGEN | REVIEW_REQUIRED",
  "verdict_reasoning": "<short>"
}

Usage in Director pipeline:
  python tools/qa_output_writer.py --ep 2 --findings findings.json --verdict PASS_WITH_WARNING
  → runtime/qa_output_ep_2.json (atomic write)
"""
import argparse
import json
import sys
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
QA_OUTPUT_DIR = SVHMP / 'runtime'

REQUIRED_FINDING_FIELDS = ['finding_id', 'phase', 'type', 'status', 'severity', 'detail']
VALID_STATUS = {'PASS', 'WARN', 'FAIL'}
VALID_SEVERITY = {'ok', 'minor', 'major', 'critical'}
VALID_VERDICT = {'PASS', 'PASS_WITH_WARNING', 'REGEN', 'REVIEW_REQUIRED'}


def validate_finding(f: dict) -> list:
    """Return list of validation errors (empty if valid)."""
    errors = []
    for field in REQUIRED_FINDING_FIELDS:
        if field not in f:
            errors.append(f"missing field: {field}")
    if 'status' in f and f['status'] not in VALID_STATUS:
        errors.append(f"invalid status: {f['status']} (must be {VALID_STATUS})")
    if 'severity' in f and f['severity'] not in VALID_SEVERITY:
        errors.append(f"invalid severity: {f['severity']}")
    return errors


def atomic_write_json(path: Path, data: dict):
    """Atomic write — no half-state."""
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


def write_qa_output(ep_number: int, findings: list, verdict: str,
                    verdict_reasoning: str = '', scores: dict = None,
                    qa_version: str = 'v1.4') -> Path:
    """Write QA output JSON. Validate findings + verdict before write."""
    # Validate verdict
    if verdict not in VALID_VERDICT:
        raise ValueError(f"Invalid verdict '{verdict}' (must be {VALID_VERDICT})")

    # Validate each finding
    all_errors = []
    for i, f in enumerate(findings):
        errs = validate_finding(f)
        if errs:
            all_errors.append(f"finding[{i}] ({f.get('finding_id', '?')}): {errs}")
    if all_errors:
        raise ValueError(f"Findings validation failed:\n  " + "\n  ".join(all_errors))

    payload = {
        'ep_number': ep_number,
        'qa_version': qa_version,
        'qa_timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'findings': findings,
        'scores': scores or {},
        'verdict': verdict,
        'verdict_reasoning': verdict_reasoning,
        'findings_count_by_status': {
            'PASS': sum(1 for f in findings if f.get('status') == 'PASS'),
            'WARN': sum(1 for f in findings if f.get('status') == 'WARN'),
            'FAIL': sum(1 for f in findings if f.get('status') == 'FAIL'),
        },
        'findings_count_by_severity': {
            sev: sum(1 for f in findings if f.get('severity') == sev)
            for sev in VALID_SEVERITY
        },
    }

    path = QA_OUTPUT_DIR / f'qa_output_ep_{ep_number}.json'
    atomic_write_json(path, payload)
    return path


def cli():
    parser = argparse.ArgumentParser(description='SVHMP QA Output Writer (G1 round 14)')
    parser.add_argument('--ep', type=int, required=True, help='Episode number')
    parser.add_argument('--findings', type=str, required=True,
                        help='Path to findings JSON (list of finding dicts)')
    parser.add_argument('--verdict', type=str, required=True, choices=list(VALID_VERDICT))
    parser.add_argument('--verdict-reasoning', type=str, default='')
    parser.add_argument('--scores', type=str, help='Path to scores JSON (optional)')
    parser.add_argument('--qa-version', type=str, default='v1.4')
    args = parser.parse_args()

    with open(args.findings, encoding='utf-8') as f:
        findings = json.load(f)
    scores = None
    if args.scores:
        with open(args.scores, encoding='utf-8') as f:
            scores = json.load(f)

    path = write_qa_output(
        ep_number=args.ep, findings=findings, verdict=args.verdict,
        verdict_reasoning=args.verdict_reasoning, scores=scores,
        qa_version=args.qa_version,
    )
    print(f"✓ QA output written: {path}")
    print(f"  Findings: {len(findings)} ({sum(1 for f in findings if f.get('status')=='PASS')} PASS / "
          f"{sum(1 for f in findings if f.get('status')=='WARN')} WARN / "
          f"{sum(1 for f in findings if f.get('status')=='FAIL')} FAIL)")
    print(f"  Verdict: {args.verdict}")


if __name__ == '__main__':
    cli()
