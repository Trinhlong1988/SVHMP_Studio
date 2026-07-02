"""
SVHMP Related Episode Recommendation — Pattern 7 adapted from ainovel-cli buildRelatedChapters.
Lock date: 2026-06-26 (Mr.Long approve Phase D2)
Loaded by: Director.step_1.5 (optional context aid before metadata pick)

Algorithm: 4-dimensional related episode lookup
  1. Foreshadow dim — arcs OPEN matching current ep passengers/objects
  2. Character dim — passenger appeared in earlier ep (recent_window=3 skip)
  3. State change dim — emotion/regret pattern recent (FIFO used_patterns)
  4. Relationship dim — passenger pairs co-appeared earlier

Adapt for SVHMP scale (90 ep vs ainovel 200-500 chapter):
  - recent_window = 3 (3.3% of 90 ep, ainovel 10 = 5% of 200)
  - max_results = 5
  - Data sources: state.yaml + canon_registry.yaml + bible/11_regret_catalog.yaml + output/ep_*/episode.md

Output: list of dicts [{ep, dimension, reason, relevance_score}] sorted desc by score.
Director consumes as "episodic_memory.related_eps" hint, NOT authority.

Source pattern: voocel/ainovel-cli internal/tools/novel_context.go buildRelatedChapters
"""

import sys
import re
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP_ROOT = Path(__file__).parent.parent
RECENT_WINDOW = 3
MAX_RESULTS = 5

# Dimension priority (higher = more relevant)
DIM_PRIORITY = {
    'foreshadow': 90,
    'character':  70,
    'state':      65,
    'relationship': 60,
}


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def load_episode_files(output_dir: Path) -> Dict[int, str]:
    """Load all output/ep_N/episode.md as text dict {ep_num: content}"""
    episodes = {}
    if not output_dir.exists():
        return episodes
    for ep_dir in output_dir.iterdir():
        if not ep_dir.is_dir(): continue
        m = re.match(r'ep_(\d+)$', ep_dir.name)
        if not m: continue
        ep_num = int(m.group(1))
        ep_md = ep_dir / 'episode.md'
        if ep_md.exists():
            try:
                episodes[ep_num] = ep_md.read_text(encoding='utf-8')
            except Exception:
                pass
    return episodes


def find_passenger_in_text(pas_id: str, text: str, state: dict) -> bool:
    """Check if passenger PAS_XXXX appears in episode text.
    Match by ID + display_name + seat number (best-effort).
    """
    if pas_id in text:
        return True
    passenger = state.get('passengers', {}).get(pas_id, {})
    if not passenger:
        return False
    display_name = passenger.get('display_name', '')
    if display_name and display_name in text:
        return True
    seat = passenger.get('seat')
    if seat:
        # "ghế 7" pattern
        if re.search(rf'\bghế\s*{seat}\b', text, re.IGNORECASE):
            return True
    return False


def current_arc_overlap(current_input: dict, arc: dict) -> bool:
    """Check if current ep planning overlaps with arc.
    Overlap = shared passengers OR shared objects OR shared payoff target.
    """
    current_pas = set(current_input.get('related_passengers', []))
    arc_pas = set(arc.get('related_passengers', []))
    if current_pas & arc_pas:
        return True
    current_obj = set(current_input.get('related_objects', []))
    arc_obj = set(arc.get('related_objects', []))
    if current_obj & arc_obj:
        return True
    if arc.get('payoff_owner') in current_pas:
        return True
    return False


def dim_foreshadow(current_input: dict, state: dict, current_ep: int) -> List[dict]:
    """Dim 1: Arcs OPEN matching current ep."""
    results = []
    arcs = state.get('arcs', {})
    for arc_id, arc in arcs.items():
        if arc.get('status') != 'OPEN':
            continue
        planted = arc.get('planted_ep', 0)
        if planted >= current_ep or planted <= 0:
            continue
        # Skip if planted within recent window (too close)
        if current_ep - planted <= RECENT_WINDOW:
            continue
        if not current_arc_overlap(current_input, arc):
            continue
        importance = arc.get('importance', 'MED')
        score = DIM_PRIORITY['foreshadow']
        if importance == 'HIGH':
            score += 10
        elif importance == 'LOW':
            score -= 10
        title = arc.get('title', '')[:40]
        results.append({
            'ep': planted,
            'dimension': 'foreshadow',
            'reason': f"Arc {arc_id} ({title}) — payoff_owner {arc.get('payoff_owner', '?')}",
            'relevance_score': score,
        })
    return results


def dim_character(current_input: dict, state: dict, current_ep: int, episodes: Dict[int, str]) -> List[dict]:
    """Dim 2: Passenger PAS_X recently appeared in earlier eps (skip recent window)."""
    results = []
    current_pas = set(current_input.get('related_passengers', []))
    if not current_pas or not episodes:
        return results
    # Iterate eps in reverse (newest first), find last appearance per passenger
    sorted_eps = sorted([e for e in episodes if e < current_ep and current_ep - e > RECENT_WINDOW], reverse=True)
    found_pas: Set[str] = set()
    for ep_num in sorted_eps:
        ep_text = episodes[ep_num]
        for pas_id in current_pas:
            if pas_id in found_pas:
                continue
            if find_passenger_in_text(pas_id, ep_text, state):
                results.append({
                    'ep': ep_num,
                    'dimension': 'character',
                    'reason': f"Passenger {pas_id} last appeared",
                    'relevance_score': DIM_PRIORITY['character'],
                })
                found_pas.add(pas_id)
        if len(found_pas) >= MAX_RESULTS:
            break
    return results


def dim_state_change(current_input: dict, state: dict, current_ep: int, episodes: Dict[int, str]) -> List[dict]:
    """Dim 3: Recent regret/emotion pattern usage (from used_patterns FIFO)."""
    results = []
    used = state.get('used_patterns', {})
    current_regret = current_input.get('regret_id', '')
    current_pillar = current_input.get('pillar', '')

    # If current regret matches recently used → find which ep used (need episode.md scan)
    recent_regrets = used.get('regrets', [])
    if current_pillar and current_pillar in recent_regrets and episodes:
        # Find latest ep mentioning this regret pillar
        sorted_eps = sorted([e for e in episodes if e < current_ep and current_ep - e > RECENT_WINDOW], reverse=True)
        for ep_num in sorted_eps:
            ep_text = episodes[ep_num].lower()
            if current_pillar.lower() in ep_text:
                results.append({
                    'ep': ep_num,
                    'dimension': 'state',
                    'reason': f"Regret pillar '{current_pillar}' previously used",
                    'relevance_score': DIM_PRIORITY['state'],
                })
                break
    return results


def dim_relationship(current_input: dict, state: dict, current_ep: int, episodes: Dict[int, str]) -> List[dict]:
    """Dim 4: Passenger pair co-appearance in earlier eps."""
    results = []
    current_pas = list(current_input.get('related_passengers', []))
    if len(current_pas) < 2 or not episodes:
        return results
    sorted_eps = sorted([e for e in episodes if e < current_ep and current_ep - e > RECENT_WINDOW], reverse=True)
    for ep_num in sorted_eps:
        ep_text = episodes[ep_num]
        for i in range(len(current_pas)):
            for j in range(i+1, len(current_pas)):
                p1, p2 = current_pas[i], current_pas[j]
                if (find_passenger_in_text(p1, ep_text, state) and
                    find_passenger_in_text(p2, ep_text, state)):
                    results.append({
                        'ep': ep_num,
                        'dimension': 'relationship',
                        'reason': f"Pair {p1} + {p2} co-appeared",
                        'relevance_score': DIM_PRIORITY['relationship'],
                    })
                    return results  # 1 pair per call max
    return results


def get_related_eps(current_ep_input: dict, state_path: Path = None, episodes_dir: Path = None) -> List[dict]:
    """Main entry point. Return top MAX_RESULTS related eps.

    Args:
        current_ep_input: dict with keys [pillar, regret_id, related_passengers, related_objects]
        state_path: path to state.yaml (default: SVHMP_ROOT/runtime/state.yaml)
        episodes_dir: path to output/ (default: SVHMP_ROOT/output/)

    Returns:
        List of dicts sorted desc by relevance_score, deduped by ep.
        Max MAX_RESULTS (5).
        Empty list if current_ep == 1 (no prior eps) or no data.
    """
    state_path = state_path or (SVHMP_ROOT / 'runtime' / 'state.yaml')
    episodes_dir = episodes_dir or (SVHMP_ROOT / 'output')

    state = load_yaml(state_path)
    current_ep = state.get('meta', {}).get('current_ep', 1)

    if current_ep <= 1:
        return []  # No prior eps

    episodes = load_episode_files(episodes_dir)
    if not episodes and not state.get('arcs'):
        return []  # No data sources

    # Aggregate 4 dimensions
    all_results: List[dict] = []
    all_results.extend(dim_foreshadow(current_ep_input, state, current_ep))
    all_results.extend(dim_character(current_ep_input, state, current_ep, episodes))
    all_results.extend(dim_state_change(current_ep_input, state, current_ep, episodes))
    all_results.extend(dim_relationship(current_ep_input, state, current_ep, episodes))

    # Dedup by ep (keep highest relevance per ep)
    seen: Dict[int, dict] = {}
    for r in all_results:
        ep = r['ep']
        if ep not in seen or r['relevance_score'] > seen[ep]['relevance_score']:
            seen[ep] = r

    # Sort desc by score
    sorted_results = sorted(seen.values(), key=lambda r: -r['relevance_score'])
    return sorted_results[:MAX_RESULTS]


def cli():
    """CLI entry: read current_ep_input from JSON stdin or file arg, print related_eps JSON.

    Usage:
        echo '{"pillar":"family_regret","related_passengers":["PAS_0007"]}' | python tools/related_eps.py
        python tools/related_eps.py --input ep_input.json
    """
    import argparse
    parser = argparse.ArgumentParser(description='SVHMP Related Episode Recommendation (Pattern 7)')
    parser.add_argument('--input', type=str, help='Path to current_ep_input.json (default: stdin)')
    parser.add_argument('--state', type=str, help='Path to state.yaml (default: runtime/state.yaml)')
    parser.add_argument('--output-dir', type=str, help='Path to output/ (default: SVHMP/output/)')
    args = parser.parse_args()

    if args.input:
        with open(args.input, encoding='utf-8') as f:
            current_input = json.load(f)
    else:
        current_input = json.load(sys.stdin)

    state_path = Path(args.state) if args.state else None
    episodes_dir = Path(args.output_dir) if args.output_dir else None

    results = get_related_eps(current_input, state_path, episodes_dir)
    print(json.dumps({
        'related_eps': results,
        'count': len(results),
        'algorithm': 'SVHMP Pattern 7 (ainovel-cli adapted)',
        'recent_window_skip': RECENT_WINDOW,
        'max_results': MAX_RESULTS,
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    cli()
