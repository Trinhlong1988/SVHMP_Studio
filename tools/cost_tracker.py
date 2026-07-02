"""
SVHMP Cost Tracker — F4.2 round 14.
Schema cost_per_ep + collect script + dashboard 90 ep total estimate.

Storage: runtime/cost_ledger.yaml (NEW)
Schema:
  total_estimated_90ep_usd: float
  per_ep_actual:
    ep_1:
      llm_cost: {claude_input: N, claude_output: N, gemini: N, ...}
      compute_cost: {gpu_hours: N, electricity_kwh: N}
      assets_cost: {voice_clone_minutes: N, sfx_downloads: N}
      external_cost: {youtube_upload: N, thumbnail_design: N}
      total_usd: float
      ts: ISO8601

Usage:
  python tools/cost_tracker.py log --ep 1 --claude-input-tokens 50000 --claude-output-tokens 12000 --gpu-hours 0.5
  python tools/cost_tracker.py report      # show running total
  python tools/cost_tracker.py estimate --target-ep 90 --base-ep 1   # extrapolate 90 ep
"""
import argparse
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
LEDGER = SVHMP / 'runtime' / 'cost_ledger.yaml'

# Cost rates — TENTATIVE_SUY_LUẬN, Mr.Long verify + lock
# Source: Anthropic pricing 2026-06 (https://anthropic.com/pricing)
COST_RATES_TENTATIVE = {
    'claude_opus_4_7': {
        'input_usd_per_1m_tokens': None,   # Mr.Long fill thực tế
        'output_usd_per_1m_tokens': None,
    },
    'gemini_2_5_pro': {
        'input_usd_per_1m_tokens': None,
        'output_usd_per_1m_tokens': None,
    },
    'gpt_4o': {
        'input_usd_per_1m_tokens': None,
        'output_usd_per_1m_tokens': None,
    },
    'rtx_5060_ti_gpu_hour_kwh': 0.36,        # ~360W avg under load
    'electricity_vn_per_kwh_usd': 0.10,      # average VN residential
}


def init_ledger():
    if LEDGER.exists():
        with open(LEDGER, encoding='utf-8') as f:
            return yaml.safe_load(f) or {'per_ep_actual': {}, 'total_estimated_90ep_usd': None}
    return {
        'meta': {
            'schema_version': 1,
            'created': datetime.now(timezone.utc).isoformat(),
            'note': 'Cost rates TENTATIVE — Mr.Long verify actual provider pricing',
        },
        'per_ep_actual': {},
        'total_estimated_90ep_usd': None,
    }


def save_ledger(data):
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with open(LEDGER, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)


def calc_llm_cost(tokens: int, rate_per_1m: float) -> float:
    if rate_per_1m is None:
        return 0.0
    return (tokens / 1_000_000) * rate_per_1m


def cmd_log(args):
    ledger = init_ledger()
    ep_key = f'ep_{args.ep}'

    rates = COST_RATES_TENTATIVE
    llm_cost = (
        calc_llm_cost(args.claude_input_tokens or 0, rates['claude_opus_4_7']['input_usd_per_1m_tokens'])
        + calc_llm_cost(args.claude_output_tokens or 0, rates['claude_opus_4_7']['output_usd_per_1m_tokens'])
        + calc_llm_cost(args.gemini_input_tokens or 0, rates['gemini_2_5_pro']['input_usd_per_1m_tokens'])
        + calc_llm_cost(args.gemini_output_tokens or 0, rates['gemini_2_5_pro']['output_usd_per_1m_tokens'])
    )

    gpu_kwh = (args.gpu_hours or 0) * rates['rtx_5060_ti_gpu_hour_kwh']
    compute_cost = gpu_kwh * rates['electricity_vn_per_kwh_usd']

    other_cost = (args.assets_cost_usd or 0) + (args.external_cost_usd or 0)

    total = llm_cost + compute_cost + other_cost

    ledger['per_ep_actual'][ep_key] = {
        'llm_cost_usd': round(llm_cost, 4),
        'compute_cost_usd': round(compute_cost, 4),
        'assets_cost_usd': args.assets_cost_usd or 0,
        'external_cost_usd': args.external_cost_usd or 0,
        'total_usd': round(total, 4),
        'raw': {
            'claude_input_tokens': args.claude_input_tokens or 0,
            'claude_output_tokens': args.claude_output_tokens or 0,
            'gemini_input_tokens': args.gemini_input_tokens or 0,
            'gemini_output_tokens': args.gemini_output_tokens or 0,
            'gpu_hours': args.gpu_hours or 0,
            'gpu_kwh': round(gpu_kwh, 3),
        },
        'ts': datetime.now(timezone.utc).isoformat(),
    }
    save_ledger(ledger)
    print(f"✓ Logged {ep_key}: ${total:.4f} (LLM ${llm_cost:.4f} + compute ${compute_cost:.4f} + other ${other_cost:.4f})")
    if any(rates[m].get('input_usd_per_1m_tokens') is None for m in ['claude_opus_4_7', 'gemini_2_5_pro']):
        print("⚠  TENTATIVE rates — Mr.Long fill COST_RATES_TENTATIVE actual provider pricing")


def cmd_report(args):
    ledger = init_ledger()
    eps = ledger.get('per_ep_actual', {})
    if not eps:
        print("Cost ledger empty — log eps first")
        return
    print("=" * 75)
    print(f"SVHMP COST REPORT — {len(eps)} eps logged")
    print("=" * 75)
    total = 0.0
    for ep_key in sorted(eps.keys(), key=lambda k: int(k.split('_')[1])):
        ep = eps[ep_key]
        total += ep['total_usd']
        print(f"  {ep_key:8s} ${ep['total_usd']:>8.4f}  (LLM ${ep['llm_cost_usd']:.4f} / compute ${ep['compute_cost_usd']:.4f})")
    print("-" * 75)
    print(f"  TOTAL    ${total:>8.4f}  ({len(eps)} eps)")
    if eps:
        avg = total / len(eps)
        print(f"  AVG/ep   ${avg:>8.4f}")
        est_90 = avg * 90
        print(f"  EST 90ep ${est_90:>8.4f}  (extrapolated)")


def cmd_estimate(args):
    ledger = init_ledger()
    eps = ledger.get('per_ep_actual', {})
    base_key = f'ep_{args.base_ep}'
    if base_key not in eps:
        print(f"Base {base_key} not in ledger — log it first")
        return
    base_cost = eps[base_key]['total_usd']
    est = base_cost * args.target_ep
    print(f"Extrapolation: ep {args.base_ep} = ${base_cost:.4f} → {args.target_ep} eps = ${est:.2f}")
    ledger['total_estimated_90ep_usd'] = round(est, 2)
    save_ledger(ledger)


def cli():
    parser = argparse.ArgumentParser(description='SVHMP Cost Tracker (F4.2 round 14)')
    sub = parser.add_subparsers(dest='cmd', required=True)

    p_log = sub.add_parser('log', help='Log cost for episode N')
    p_log.add_argument('--ep', type=int, required=True)
    p_log.add_argument('--claude-input-tokens', type=int)
    p_log.add_argument('--claude-output-tokens', type=int)
    p_log.add_argument('--gemini-input-tokens', type=int)
    p_log.add_argument('--gemini-output-tokens', type=int)
    p_log.add_argument('--gpu-hours', type=float)
    p_log.add_argument('--assets-cost-usd', type=float)
    p_log.add_argument('--external-cost-usd', type=float)
    p_log.set_defaults(func=cmd_log)

    p_rep = sub.add_parser('report', help='Show cost summary')
    p_rep.set_defaults(func=cmd_report)

    p_est = sub.add_parser('estimate', help='Extrapolate 90 ep cost')
    p_est.add_argument('--base-ep', type=int, default=1)
    p_est.add_argument('--target-ep', type=int, default=90)
    p_est.set_defaults(func=cmd_estimate)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    cli()
