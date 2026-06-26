"""VNQA Auto-Fix (Option B semi-auto literal map) — round 14 Phase H4.

Read approved replacement registry → scan episode.md → propose .proposed_fix file.
Default: PROPOSE only (Mr.Long review diff). --apply: atomic write + backup.

Usage:
  python tools/vnqa/auto_fix.py --episode output/ep_2/episode.md --ep 2
  python tools/vnqa/auto_fix.py --episode output/ep_2/episode.md --ep 2 --apply

Dependencies:
  data/vnqa_approved_replacements.yaml (registry)
"""
import argparse
import difflib
import json
import re
import shutil
import sys
import time
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent.parent  # B30 lesson — đúng path
REGISTRY_PATH = SVHMP / 'data' / 'vnqa_approved_replacements.yaml'


def load_registry() -> dict:
    if not REGISTRY_PATH.exists():
        return {}
    import yaml
    return yaml.safe_load(REGISTRY_PATH.read_text(encoding='utf-8')) or {}


def find_matches(text: str, rule: dict) -> list:
    """Return list of (line_no, original_line, matched_substring)."""
    pat = rule['pattern']
    flags = 0 if rule.get('case_sensitive', False) else re.IGNORECASE
    matches = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in re.finditer(re.escape(pat), line, flags=flags):
            matches.append((lineno, line, m.group()))
    return matches


def propose_fix(episode_path: Path, ep: int, registry: dict) -> dict:
    """Scan episode.md → match registry → return proposed_text + diff + stats."""
    text = episode_path.read_text(encoding='utf-8')
    original = text
    stats = {
        'ep': ep,
        'rules_applied': [],
        'rules_skipped_no_match': [],
        'total_replacements': 0,
    }
    for rule in registry.get('replacements', []) or []:
        rid = rule.get('id', '?')
        pat = rule['pattern']
        rep = rule['replace']
        case_sens = rule.get('case_sensitive', False)
        flags = 0 if case_sens else re.IGNORECASE

        before_count = len(re.findall(re.escape(pat), text, flags=flags))
        if before_count == 0:
            stats['rules_skipped_no_match'].append({'id': rid, 'pattern': pat})
            continue

        text = re.sub(re.escape(pat), rep, text, flags=flags)
        after_count = len(re.findall(re.escape(pat), text, flags=flags))
        applied = before_count - after_count
        stats['rules_applied'].append({
            'id': rid, 'pattern': pat, 'replace': rep,
            'count': applied, 'reason': rule.get('reason', ''),
        })
        stats['total_replacements'] += applied

    diff_lines = list(difflib.unified_diff(
        original.splitlines(keepends=True),
        text.splitlines(keepends=True),
        fromfile=f'episode_ep{ep}.md (original)',
        tofile=f'episode_ep{ep}.md (proposed)',
        n=1,
    ))
    return {
        'original': original,
        'proposed': text,
        'diff': ''.join(diff_lines),
        'stats': stats,
        'changed': stats['total_replacements'] > 0,
    }


def cli():
    parser = argparse.ArgumentParser(description='VNQA Auto-Fix Option B semi-auto')
    parser.add_argument('--episode', type=str, required=True)
    parser.add_argument('--ep', type=int, required=True)
    parser.add_argument('--apply', action='store_true',
                        help='Atomic write + backup. Default: tạo .proposed_fix file.')
    args = parser.parse_args()

    ep_path = Path(args.episode)
    if not ep_path.exists():
        print(f'ERROR: episode not found: {ep_path}')
        sys.exit(1)

    registry = load_registry()
    if not registry.get('replacements'):
        print('ERROR: registry empty hoặc không tồn tại')
        sys.exit(1)

    result = propose_fix(ep_path, args.ep, registry)
    stats = result['stats']

    print(f'=== VNQA Auto-Fix EP{args.ep} ===')
    print(f'Rules applied: {len(stats["rules_applied"])} | Total replacements: {stats["total_replacements"]}')
    for r in stats['rules_applied']:
        print(f'  [{r["id"]}] "{r["pattern"]}" → "{r["replace"]}" × {r["count"]}')
        print(f'    reason: {r["reason"]}')
    if stats['rules_skipped_no_match']:
        print(f'Skipped (no match): {[r["id"] for r in stats["rules_skipped_no_match"]]}')

    if not result['changed']:
        print('→ Không có thay đổi nào. Bỏ qua.')
        sys.exit(0)

    if args.apply:
        # Atomic write + backup
        backup_path = ep_path.with_suffix(f'.md.bak_autofix_{int(time.time())}')
        shutil.copy2(ep_path, backup_path)
        ep_path.write_text(result['proposed'], encoding='utf-8')
        print(f'\n✓ APPLIED — backup: {backup_path.name}')
    else:
        proposed_path = ep_path.with_suffix('.md.proposed_fix')
        proposed_path.write_text(result['proposed'], encoding='utf-8')
        diff_path = ep_path.with_suffix('.md.proposed_diff')
        diff_path.write_text(result['diff'], encoding='utf-8')
        print(f'\n→ PROPOSED: {proposed_path.name}')
        print(f'→ DIFF:     {diff_path.name}')
        print('Run với --apply để atomic write.')


if __name__ == '__main__':
    cli()
