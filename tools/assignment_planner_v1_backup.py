"""SVHMP 90 EP audio assignment planner — apply R1-R3 rules.

R1: Match mood/BPM/key by EP intensity curve (EP1-10/11-30/31-60/61-90) + section
R2: HOOK ≠ CLIFFHANGER track in same EP
R3: Cooldown — hard 10 EP for boundary (HOOK/CLIFFHANGER), soft 5 EP for middle sections

Output:
  output/ep_audio_plan.yaml      — 90 EP × 6 sections piano + scene SFX
  output/library_usage_log.json  — track usage history
  output/assignment_report.txt   — coverage + violation report
"""
import os, json, yaml, random, sys
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path(__file__).resolve().parents[1]
LIB = BASE / 'assets' / 'sfx' / 'hdk_music_library' / 'library_index.yaml'
OUT_DIR = BASE / 'output'
OUT_DIR.mkdir(exist_ok=True)

# Intensity curve → BPM + key bias per EP range (from bible/09_emotion_intensity.yaml)
INTENSITY_PROFILE = [
    {'eps': range(1, 11),  'intensity': 0.45, 'bpm_range': (50, 95),  'minor_bias': 0.55, 'centroid_range': (600, 2200)},
    {'eps': range(11, 31), 'intensity': 0.55, 'bpm_range': (60, 105), 'minor_bias': 0.65, 'centroid_range': (700, 2400)},
    {'eps': range(31, 61), 'intensity': 0.75, 'bpm_range': (70, 120), 'minor_bias': 0.75, 'centroid_range': (800, 2800)},
    {'eps': range(61, 91), 'intensity': 0.95, 'bpm_range': (80, 140), 'minor_bias': 0.80, 'centroid_range': (900, 3500)},
]

def get_ep_profile(ep_num):
    for p in INTENSITY_PROFILE:
        if ep_num in p['eps']:
            return p
    return INTENSITY_PROFILE[-1]

# Cooldown per section (R3)
COOLDOWN = {
    'HOOK':        10,  # signature opening — hard
    'CLIFFHANGER': 10,  # signature closing — hard
    'SETUP':       5,
    'INCIDENT':    5,
    'REVEAL':      5,
    'PAYOFF':      5,
}

# SFX preferred per section (per-EP scene needs SFX too)
SFX_BY_SECTION = {
    'HOOK':        ['wind', 'rain', 'thunder', 'old-house', 'whoosh'],
    'SETUP':       ['rain', 'wind', 'clock', 'fire', 'water', 'old-house'],
    'INCIDENT':    ['footsteps', 'door', 'glass', 'whisper', 'heartbeat', 'breath'],
    'REVEAL':      ['whisper', 'bell', 'music-box', 'ethereal', 'drone'],
    'PAYOFF':      ['rain', 'wind', 'clock', 'fire', 'breath'],
    'CLIFFHANGER': ['bell', 'train', 'wolf', 'crow', 'wind', 'drone'],
}

def score_track(track, profile, section):
    """Higher score = better match for this EP+section."""
    score = 0
    bpm = track.get('bpm')
    if bpm:
        lo, hi = profile['bpm_range']
        if lo <= bpm <= hi:
            score += 30
        else:
            # Penalty proportional to distance
            dist = min(abs(bpm - lo), abs(bpm - hi))
            score -= dist * 0.5
    # Key bias toward minor
    key = track.get('key', '')
    if 'minor' in key.lower():
        score += 15 if profile['minor_bias'] > 0.5 else -5
    # Centroid match (brightness)
    cent = track.get('centroid_hz')
    if cent:
        lo, hi = profile['centroid_range']
        if lo <= cent <= hi:
            score += 10
    # Section-specific bonuses
    onset = track.get('onset_density', 0) or 0
    if section == 'INCIDENT' and onset > 3:
        score += 8  # high density for tension
    if section == 'REVEAL' and onset < 2:
        score += 8  # sparse for ethereal
    if section == 'SETUP' and 0.5 <= onset <= 2.5:
        score += 5
    return score

def pick_piano(library, section, ep_num, profile, used_recent, ep_assignments):
    """Pick best piano track for this section."""
    candidates = library['piano'].get(section, [])
    cooldown_n = COOLDOWN[section]
    recent_ids = used_recent.get(section, set())

    # R3: filter cooldown
    avail = [t for t in candidates if t['id'] not in recent_ids]

    # R2: boundary distinct
    if section in ('HOOK', 'CLIFFHANGER'):
        other = 'CLIFFHANGER' if section == 'HOOK' else 'HOOK'
        already = ep_assignments.get(other, {}).get('id')
        if already:
            avail = [t for t in avail if t['id'] != already]

    if not avail:
        # Cooldown exhausted — fallback: pick least-recently-used
        avail = candidates

    # Score & sort
    scored = [(score_track(t, profile, section), t) for t in avail]
    scored.sort(key=lambda x: -x[0])
    # Wider pool (top 20) + uniform random for high variety
    top = scored[:20]
    if not top: return None
    # Mildly weighted toward higher scores (sqrt to flatten)
    import math
    weights = [max(1, math.sqrt(max(0, s)+10)) for s, _ in top]
    pick = random.choices([t for _, t in top], weights=weights)[0]
    return pick

def pick_sfx(library, section, ep_num, sfx_recent):
    """Pick 1 SFX per section from random category (full pool, no duration bias)."""
    cats = SFX_BY_SECTION.get(section, [])
    random.shuffle(cats)  # category rotation for variety
    for cat in cats:
        avail_sfx = library['sfx'].get(cat, [])
        if not avail_sfx: continue
        recent = sfx_recent.get(cat, set())
        avail = [s for s in avail_sfx if s['id'] not in recent]
        if not avail: avail = avail_sfx
        # No duration bias — pick uniformly from full pool
        return [random.choice(avail)]
    return []

def main():
    print('Loading library_index.yaml...')
    lib = yaml.safe_load(LIB.read_text(encoding='utf-8'))
    print(f'  Piano: {sum(len(v) for v in lib["piano"].values())} across {len(lib["piano"])} sections')
    print(f'  SFX:   {sum(len(v) for v in lib["sfx"].values())} across {len(lib["sfx"])} categories')

    random.seed(42)  # reproducible
    plan = {'version': '1.0', 'rules': 'R1-R3 SVHMP HDK 28/6', 'episodes': {}}
    usage = defaultdict(list)  # track_id -> [(ep, section)]
    sfx_usage = defaultdict(list)  # sfx_id -> [(ep, section, cat)]
    section_used_recent = {s: set() for s in COOLDOWN}  # section -> rolling set
    section_used_history = {s: [] for s in COOLDOWN}    # section -> list of (ep, id) for sliding window

    for ep in range(1, 91):
        profile = get_ep_profile(ep)
        ep_data = {
            'ep': ep,
            'intensity': profile['intensity'],
            'piano': {},
            'sfx': {},
        }

        # Pick piano for each section
        for section in ['HOOK', 'SETUP', 'INCIDENT', 'REVEAL', 'PAYOFF', 'CLIFFHANGER']:
            pick = pick_piano(lib, section, ep, profile, section_used_recent, ep_data['piano'])
            if pick is None:
                continue
            ep_data['piano'][section] = {
                'id': pick['id'],
                'file': pick.get('file'),
                'title': pick.get('title'),
                'bpm': pick.get('bpm'),
                'key': pick.get('key'),
                'duration_sec': pick.get('duration_sec'),
            }
            # Track usage
            usage[pick['id']].append((ep, section))
            section_used_history[section].append((ep, pick['id']))

        # Apply cooldown window — update recent sets
        for section, hist in section_used_history.items():
            cd = COOLDOWN[section]
            section_used_recent[section] = {pid for e, pid in hist if ep - e < cd}

        # Pick SFX for each section
        sfx_used_in_ep = set()
        for section in ['HOOK', 'SETUP', 'INCIDENT', 'REVEAL', 'PAYOFF', 'CLIFFHANGER']:
            # SFX cooldown 5 EP (was 3)
            sfx_cd_by_cat = defaultdict(set)
            for sid, hist in sfx_usage.items():
                for e, _ in hist:
                    if ep - e < 5:
                        sfx_cd_by_cat[sid].add(sid)
            sfx_recent_set = {sid for sid, hist in sfx_usage.items() if any(ep - e < 5 for e, _ in hist)}
            sfx_picks = pick_sfx(lib, section, ep, {cat: sfx_recent_set for cat in SFX_BY_SECTION.get(section, [])})
            ep_data['sfx'][section] = []
            for sx in sfx_picks:
                if sx['id'] in sfx_used_in_ep:
                    continue
                sfx_used_in_ep.add(sx['id'])
                ep_data['sfx'][section].append({
                    'id': sx['id'],
                    'file': sx.get('file'),
                    'title': sx.get('title'),
                    'duration_sec': sx.get('duration_sec'),
                })
                sfx_usage[sx['id']].append((ep, section))

        plan['episodes'][f'EP{ep:02d}'] = ep_data
        if ep <= 5 or ep % 30 == 0:
            print(f'  EP{ep:02d}: piano={list(ep_data["piano"].keys())} SFX={sum(len(v) for v in ep_data["sfx"].values())}')

    # Save plan
    plan_path = OUT_DIR / 'ep_audio_plan.yaml'
    plan_path.write_text(yaml.dump(plan, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print(f'\nPlan: {plan_path} ({plan_path.stat().st_size/1024:.0f} KB)')

    # Save usage log
    usage_log = {tid: [(e, s) for e, s in eps] for tid, eps in usage.items()}
    log_path = OUT_DIR / 'library_usage_log.json'
    log_path.write_text(json.dumps({
        'piano': usage_log,
        'sfx': {k: list(v) for k, v in sfx_usage.items()},
    }, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'Log:  {log_path} ({log_path.stat().st_size/1024:.0f} KB)')

    # Report
    counts = Counter(len(eps) for eps in usage.values())
    boundary_dup = 0
    cd_violations = 0
    for ep_key, ep_data in plan['episodes'].items():
        hook = ep_data['piano'].get('HOOK', {}).get('id')
        cliff = ep_data['piano'].get('CLIFFHANGER', {}).get('id')
        if hook and cliff and hook == cliff:
            boundary_dup += 1

    # Cooldown violation check
    for tid, eps_list in usage.items():
        eps_list.sort()
        for i in range(1, len(eps_list)):
            ep_prev, sec_prev = eps_list[i-1]
            ep_cur, sec_cur = eps_list[i]
            if sec_cur == sec_prev:
                cd = COOLDOWN[sec_cur]
                if ep_cur - ep_prev < cd:
                    cd_violations += 1

    report = f"""=== SVHMP 90 EP AUDIO PLAN REPORT ===
Generated: {plan['rules']}
EPs planned: 90 × 6 sections = 540 piano slots + ~540 SFX slots

PIANO USAGE DISTRIBUTION:
  Tracks used: {len(usage)}/{sum(len(v) for v in lib['piano'].values())}
  Usage histogram: {dict(sorted(counts.items()))}
  Mean uses/track: {sum(c*n for c,n in counts.items())/len(usage):.2f}

R2 VIOLATIONS (HOOK == CLIFFHANGER in same EP):
  {boundary_dup}/90 (0 expected)

R3 VIOLATIONS (cooldown violated):
  {cd_violations} total

SFX USAGE:
  Unique SFX used: {len(sfx_usage)}/{sum(len(v) for v in lib['sfx'].values())}

OUTPUT FILES:
  {plan_path}
  {log_path}
"""
    rpt_path = OUT_DIR / 'assignment_report.txt'
    rpt_path.write_text(report, encoding='utf-8')
    print('\n' + report)

if __name__ == '__main__':
    main()
