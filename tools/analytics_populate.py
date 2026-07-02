"""
SVHMP Analytics Populate — script auto-update runtime/analytics.yaml.eps[ep_N]
Lock date: 2026-06-26 (Mr.Long approve F2 telemetry gap fix round 14)

Usage:
  # Mr.Long sau khi scrape YouTube T+48h:
  python tools/analytics_populate.py --ep 1 \
    --ctr 5.2 --retention 62.5 --replay 18.3 --completion 51.2 \
    --views 12500 --likes 230 \
    --comments-recognition 45 --comments-empathy 32 --comments-memory 18 \
    --comments-praise 12 --comments-pacing 3 --comments-horror-wrong 2 --comments-spam 5

  # Hoặc dùng --json file (preferred batch):
  python tools/analytics_populate.py --ep 1 --json ep_01_metrics.json
"""
import argparse
import json
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP_ROOT = Path(__file__).parent.parent
ANALYTICS = SVHMP_ROOT / 'runtime' / 'analytics.yaml'


def build_ep_entry(ep_num: int, metrics: dict, comments: dict, total_views: int, total_likes: int) -> dict:
    """Build ep entry theo schema analytics.yaml line 80-96."""
    now = datetime.now(timezone.utc).isoformat()

    desired = (comments.get('regret_recognition', 0)
               + comments.get('empathy_share', 0)
               + comments.get('memory_trigger', 0))
    total_comments = sum(comments.values()) or 1
    desired_ratio = round(desired / total_comments, 3)

    # Drift alerts theo metric_definitions thresholds (analytics.yaml line 17-73)
    alerts = []
    if metrics['ctr'] < 4.0:
        alerts.append('ctr_below_drift_trigger')
    if metrics['avg_retention'] < 50:
        alerts.append('retention_below_drift_trigger')
    if metrics['replay_rate'] < 5:
        alerts.append('replay_below_drift_trigger')
    if metrics['completion_rate'] < 30:
        alerts.append('completion_below_drift_trigger')
    if desired_ratio < 0.60:
        alerts.append('soul_drift_desired_ratio_low')

    like_ratio = round(total_likes / max(total_views, 1) * 100, 2)

    return {
        'upload_ts': metrics.get('upload_ts', now),
        'first_scrape_ts': now,
        'last_scrape_ts': now,
        'metrics': {
            'ctr': metrics['ctr'],
            'avg_retention': metrics['avg_retention'],
            'replay_rate': metrics['replay_rate'],
            'completion_rate': metrics['completion_rate'],
        },
        'comments_classified': comments,
        'total_views': total_views,
        'total_likes': total_likes,
        'like_ratio': like_ratio,
        'desired_ratio': desired_ratio,
        'drift_alerts_triggered': alerts,
        'tuning_actions_applied': [],  # populated bởi feedback_loop trigger
    }


def populate(ep_num: int, ep_data: dict, dry_run: bool = False):
    """Update analytics.yaml.eps[ep_N] với ep_data."""
    with open(ANALYTICS, encoding='utf-8') as f:
        analytics = yaml.safe_load(f) or {}

    if 'eps' not in analytics or analytics['eps'] is None:
        analytics['eps'] = {}

    ep_key = f'ep_{ep_num}'
    if ep_key in analytics['eps']:
        print(f"WARNING: {ep_key} already exists — overwriting")

    analytics['eps'][ep_key] = ep_data
    analytics['meta']['last_scrape'] = ep_data['last_scrape_ts']

    if dry_run:
        print("=== DRY RUN — would write: ===")
        print(yaml.dump({ep_key: ep_data}, allow_unicode=True, default_flow_style=False))
        return

    # Write back preserving structure (YAML reformat OK)
    with open(ANALYTICS, 'w', encoding='utf-8') as f:
        yaml.dump(analytics, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    print(f"✓ Updated analytics.yaml.eps.{ep_key}")
    if ep_data['drift_alerts_triggered']:
        print(f"⚠️  Drift alerts: {ep_data['drift_alerts_triggered']}")
        print(f"   → Check runtime/analytics.yaml.feedback_loop.rules cho auto-tune action")


def cli():
    parser = argparse.ArgumentParser(description='SVHMP Analytics Populate (F2 round 14)')
    parser.add_argument('--ep', type=int, required=True, help='Episode number (e.g., 1)')
    parser.add_argument('--json', type=str, help='Path to JSON file với full ep_data')
    parser.add_argument('--ctr', type=float, help='Click-through rate %')
    parser.add_argument('--retention', type=float, help='Avg retention %')
    parser.add_argument('--replay', type=float, help='Replay rate %')
    parser.add_argument('--completion', type=float, help='Completion rate %')
    parser.add_argument('--views', type=int, default=0)
    parser.add_argument('--likes', type=int, default=0)
    # Comment classifier counts (per analytics.yaml schema)
    parser.add_argument('--comments-recognition', type=int, default=0)
    parser.add_argument('--comments-empathy', type=int, default=0)
    parser.add_argument('--comments-memory', type=int, default=0)
    parser.add_argument('--comments-praise', type=int, default=0)
    parser.add_argument('--comments-pacing', type=int, default=0)
    parser.add_argument('--comments-horror-wrong', type=int, default=0)
    parser.add_argument('--comments-spam', type=int, default=0)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    if args.json:
        with open(args.json, encoding='utf-8') as f:
            ep_data = json.load(f)
    else:
        # Build from CLI args
        if None in (args.ctr, args.retention, args.replay, args.completion):
            parser.error('Either --json OR all 4 metrics (--ctr --retention --replay --completion) required')
        metrics = {
            'ctr': args.ctr,
            'avg_retention': args.retention,
            'replay_rate': args.replay,
            'completion_rate': args.completion,
        }
        comments = {
            'regret_recognition': args.comments_recognition,
            'empathy_share': args.comments_empathy,
            'memory_trigger': args.comments_memory,
            'praise_quality': args.comments_praise,
            'complaint_pacing': args.comments_pacing,
            'complaint_horror_wrong': args.comments_horror_wrong,
            'spam': args.comments_spam,
        }
        ep_data = build_ep_entry(args.ep, metrics, comments, args.views, args.likes)

    populate(args.ep, ep_data, args.dry_run)


if __name__ == '__main__':
    cli()
