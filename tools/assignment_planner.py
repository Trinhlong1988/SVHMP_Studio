"""SVHMP 90 EP audio assignment planner v2.0 — bible/05 v1.1 R_AUDIO_01-10.

CHANGES v1.0 → v2.0 (Mr.Long lệnh round 15 — 2026-06-28):
  - R_AUDIO_04 setting validation: filter forbidden SFX (fire/chandelier/desert/etc)
  - R_AUDIO_05 prioritize HDK_* specialized tracks (MYSTERY/SAD/REVEAL/TENSION/ENDING)
  - R_AUDIO_03 emit ambient_bed schedule (rain + bus_engine + wet_road constant)
  - SFX_BY_SECTION revised — REMOVE fire/glass mid-section default; add wiper/lamp
  - moment_map.yaml emit per EP (for R_AUDIO_02 compliance — moment-level planning)

R1: Match mood/BPM/key by EP intensity curve (bible/09)
R2: HOOK ≠ CLIFFHANGER track in same EP
R3: Cooldown — hard 10 EP for boundary, soft 5 EP for middle sections
"""
import os, json, yaml, random, math
from pathlib import Path
from collections import defaultdict, Counter

BASE = Path(r'D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio')
LIB = BASE / 'assets' / 'sfx' / 'hdk_music_library' / 'library_index.yaml'
HDK_LIB_DIR = BASE / 'assets' / 'sfx' / 'hdk_music_library'
OUT_DIR = BASE / 'output'
OUT_DIR.mkdir(exist_ok=True)

# Bible/09 intensity curve
INTENSITY_PROFILE = [
    {'eps': range(1, 11),  'intensity': 0.45, 'bpm_range': (50, 95),  'minor_bias': 0.55, 'centroid_range': (600, 2200)},
    {'eps': range(11, 31), 'intensity': 0.55, 'bpm_range': (60, 105), 'minor_bias': 0.65, 'centroid_range': (700, 2400)},
    {'eps': range(31, 61), 'intensity': 0.75, 'bpm_range': (70, 120), 'minor_bias': 0.75, 'centroid_range': (800, 2800)},
    {'eps': range(61, 91), 'intensity': 0.95, 'bpm_range': (80, 140), 'minor_bias': 0.80, 'centroid_range': (900, 3500)},
]

def get_ep_profile(ep_num):
    for p in INTENSITY_PROFILE:
        if ep_num in p['eps']: return p
    return INTENSITY_PROFILE[-1]

COOLDOWN = {'HOOK':10, 'CLIFFHANGER':10, 'SETUP':5, 'INCIDENT':5, 'REVEAL':5, 'PAYOFF':5}

# bible/05 R_AUDIO_06 music_section_personality — HDK category mapping
SECTION_TO_HDK_CATEGORY = {
    'HOOK':        'HDK_MYSTERY',    # tò mò horror intro
    'SETUP':       'HDK_TENSION',    # build unease bed
    'INCIDENT':    'HDK_TENSION',    # peak conflict swell
    'REVEAL':      'HDK_REVEAL',     # ethereal floating
    'PAYOFF':      'HDK_SAD',        # emotional swell
    'CLIFFHANGER': 'HDK_ENDING',     # fade silence
}

# bible/05 R_AUDIO_04 forbidden SFX categories cho xe_buyt_dem setting
FORBIDDEN_SFX_KEYWORDS = [
    'fire','fireplace','campfire','chandelier','desert','cactus','ocean','waves',
    'beach','surf','forest_birds','jungle','baby','infant','explosion','gunfire',
    'military','cathedral','organ',
]

# bible/05 R_AUDIO_04 setting_appropriate_sfx — REVISED v2.0 (remove fire/glass mid-section)
SFX_BY_SECTION_V2 = {
    'HOOK':        ['wind','rain','thunder','old-house','whoosh'],
    'SETUP':       ['rain','wind','clock','water','old-house'],          # REMOVED 'fire'
    'INCIDENT':    ['footsteps','door','whisper','heartbeat','breath'],  # REMOVED 'glass'
    'REVEAL':      ['whisper','bell','music-box','drone'],
    'PAYOFF':      ['rain','wind','clock','breath'],                     # REMOVED 'fire'
    'CLIFFHANGER': ['bell','train','crow','wind','drone'],               # REMOVED 'wolf' (xe buýt KHÔNG có sói)
}

# bible/05 R_AUDIO_03 ambient bed constant per EP
AMBIENT_BED_PROFILE = {
    'rain_light':  {'volume_db': -22, 'fade_in_ms': 1500, 'loop': True},
    'bus_engine':  {'volume_db': -27, 'fade_in_ms': 1500, 'loop': True},
    'wet_road':    {'volume_db': -28, 'loop': True, 'when': 'xe đang chạy'},
}

def get_hdk_tracks_for_category(category):
    """Find all HDK_* tracks matching category. Returns list of (file, path)."""
    if not HDK_LIB_DIR.exists(): return []
    pattern = f'{category}_*.wav'
    files = list(HDK_LIB_DIR.glob(pattern))
    return [{'id': f.stem, 'file': f.name, 'title': f.stem, 'is_hdk_specialized': True,
             'path': str(f.relative_to(HDK_LIB_DIR))} for f in files]

def score_track(track, profile, section):
    score = 0
    bpm = track.get('bpm')
    if bpm:
        lo, hi = profile['bpm_range']
        if lo <= bpm <= hi: score += 30
        else: score -= min(abs(bpm-lo), abs(bpm-hi)) * 0.5
    key = track.get('key', '')
    if 'minor' in key.lower(): score += 15 if profile['minor_bias'] > 0.5 else -5
    cent = track.get('centroid_hz')
    if cent:
        lo, hi = profile['centroid_range']
        if lo <= cent <= hi: score += 10
    onset = track.get('onset_density', 0) or 0
    if section == 'INCIDENT' and onset > 3: score += 8
    if section == 'REVEAL' and onset < 2: score += 8
    if section == 'SETUP' and 0.5 <= onset <= 2.5: score += 5
    return score

def pick_piano(library, section, ep_num, profile, used_recent, ep_assignments):
    """v2.0: Try HDK specialized FIRST per R_AUDIO_05, fallback to pixabay pool."""
    # Layer 1: HDK specialized (per R_AUDIO_05 category mapping)
    hdk_cat = SECTION_TO_HDK_CATEGORY.get(section)
    if hdk_cat:
        hdk_tracks = get_hdk_tracks_for_category(hdk_cat)
        if hdk_tracks:
            recent_ids = used_recent.get(section, set())
            avail = [t for t in hdk_tracks if t['id'] not in recent_ids]
            if section in ('HOOK','CLIFFHANGER'):
                other = 'CLIFFHANGER' if section == 'HOOK' else 'HOOK'
                already = ep_assignments.get(other, {}).get('id')
                if already: avail = [t for t in avail if t['id'] != already]
            if avail:
                pick = random.choice(avail)
                pick['source'] = 'HDK_specialized'
                return pick

    # Layer 2: Pixabay piano pool fallback
    candidates = library['piano'].get(section, [])
    recent_ids = used_recent.get(section, set())
    avail = [t for t in candidates if t['id'] not in recent_ids]
    if section in ('HOOK','CLIFFHANGER'):
        other = 'CLIFFHANGER' if section == 'HOOK' else 'HOOK'
        already = ep_assignments.get(other, {}).get('id')
        if already: avail = [t for t in avail if t['id'] != already]
    if not avail: avail = candidates
    scored = [(score_track(t, profile, section), t) for t in avail]
    scored.sort(key=lambda x: -x[0])
    top = scored[:20]
    if not top: return None
    weights = [max(1, math.sqrt(max(0, s)+10)) for s, _ in top]
    pick = random.choices([t for _, t in top], weights=weights)[0]
    pick['source'] = 'pixabay_fallback'
    return pick

def is_sfx_forbidden(sfx_title, sfx_file):
    """v2.0: R_AUDIO_04 setting validation."""
    s = (sfx_title or '').lower() + ' ' + (sfx_file or '').lower()
    for kw in FORBIDDEN_SFX_KEYWORDS:
        if kw in s: return kw
    return None

def pick_sfx(library, section, ep_num, sfx_recent_global):
    """v2.0: Filter forbidden + cooldown across categories."""
    cats = SFX_BY_SECTION_V2.get(section, [])
    random.shuffle(cats)
    for cat in cats:
        avail_sfx = library['sfx'].get(cat, [])
        if not avail_sfx: continue
        # Filter forbidden (R_AUDIO_04)
        clean = [s for s in avail_sfx
                 if not is_sfx_forbidden(s.get('title'), s.get('file'))]
        # Filter cooldown
        avail = [s for s in clean if s['id'] not in sfx_recent_global]
        if not avail: avail = clean if clean else avail_sfx
        if avail:
            return [random.choice(avail)]
    return []

def build_moment_map_template(ep_num, ep_data):
    """v2.0: Emit moment_map.yaml template per R_AUDIO_02.

    Skeleton for Mr.Long to fill in moments per EP — does NOT auto-generate
    moments (per R_AUDIO_10: no inference, requires episode.md text analysis).
    """
    return {
        'ep': ep_num,
        'note': 'TEMPLATE — Mr.Long pick moments từ episode.md per R_AUDIO_02 viewer empathy',
        'ambient_bed': AMBIENT_BED_PROFILE,
        'section_default_picks': ep_data['piano'],
        'moments': [
            {
                'line_range': 'L120-130',
                'section': 'HOOK',
                'text_quote': 'TODO: Mr.Long paste câu',
                'emotion_label': 'TODO: setup/tension/death_announce/memory_of_dead/haunting/regret/farewell',
                'music_pick': 'TODO: HDK_MYSTERY_seed42 hoặc HDK_SAD_seed123 etc',
                'music_category': 'TODO: HDK_MYSTERY/HDK_SAD/HDK_REVEAL/HDK_TENSION/HDK_ENDING',
                'dB_level': -20,
                'transition_type': 'cross_fade_3s',
                'impact_moment': False,
                'mute_window': None,
                'special_treatment': None,
            },
        ],
        '_schema_required_per_moment': [
            'line_range', 'emotion_label', 'music_pick', 'dB_level', 'transition_type',
        ],
        '_per_R_AUDIO_02': 'min 15 moments per EP, sub-pick per moment NOT 1 track sustained',
    }

def main():
    print('Loading library_index.yaml...')
    lib = yaml.safe_load(LIB.read_text(encoding='utf-8'))
    print(f'  Piano: {sum(len(v) for v in lib["piano"].values())} across {len(lib["piano"])} sections')
    print(f'  SFX:   {sum(len(v) for v in lib["sfx"].values())} across {len(lib["sfx"])} categories')

    # HDK specialized inventory
    print('\n[HDK specialized tracks]:')
    for cat in ['HDK_MYSTERY','HDK_SAD','HDK_REVEAL','HDK_TENSION','HDK_ENDING']:
        tracks = get_hdk_tracks_for_category(cat)
        print(f'  {cat}: {len(tracks)} tracks')

    random.seed(42)
    plan = {
        'version': '2.0',
        'rules': 'R1-R3 + bible/05 v1.1 R_AUDIO_01-10',
        'ambient_bed': AMBIENT_BED_PROFILE,
        'forbidden_sfx_keywords': FORBIDDEN_SFX_KEYWORDS,
        'episodes': {},
    }
    usage = defaultdict(list)
    sfx_usage = defaultdict(list)
    section_used_recent = {s: set() for s in COOLDOWN}
    section_used_history = {s: [] for s in COOLDOWN}

    print('\n[PLANNING 90 EPs]')
    for ep in range(1, 91):
        profile = get_ep_profile(ep)
        ep_data = {'ep': ep, 'intensity': profile['intensity'], 'piano': {}, 'sfx': {}}

        for section in ['HOOK','SETUP','INCIDENT','REVEAL','PAYOFF','CLIFFHANGER']:
            pick = pick_piano(lib, section, ep, profile, section_used_recent, ep_data['piano'])
            if pick is None: continue
            ep_data['piano'][section] = {
                'id': pick['id'], 'file': pick.get('file'), 'title': pick.get('title'),
                'bpm': pick.get('bpm'), 'key': pick.get('key'),
                'duration_sec': pick.get('duration_sec'),
                'source': pick.get('source'),
            }
            usage[pick['id']].append((ep, section))
            section_used_history[section].append((ep, pick['id']))

        for section, hist in section_used_history.items():
            cd = COOLDOWN[section]
            section_used_recent[section] = {pid for e, pid in hist if ep - e < cd}

        sfx_used_in_ep = set()
        sfx_recent_global = {sid for sid, hist in sfx_usage.items()
                             if any(ep - e < 5 for e, _ in hist)}
        for section in ['HOOK','SETUP','INCIDENT','REVEAL','PAYOFF','CLIFFHANGER']:
            sfx_picks = pick_sfx(lib, section, ep, sfx_recent_global)
            ep_data['sfx'][section] = []
            for sx in sfx_picks:
                if sx['id'] in sfx_used_in_ep: continue
                sfx_used_in_ep.add(sx['id'])
                ep_data['sfx'][section].append({
                    'id': sx['id'], 'file': sx.get('file'),
                    'title': sx.get('title'), 'duration_sec': sx.get('duration_sec'),
                })
                sfx_usage[sx['id']].append((ep, section))

        plan['episodes'][f'EP{ep:02d}'] = ep_data
        if ep <= 3 or ep % 30 == 0:
            hdk_count = sum(1 for p in ep_data['piano'].values()
                           if p.get('source') == 'HDK_specialized')
            print(f'  EP{ep:02d}: piano={list(ep_data["piano"].keys())} HDK={hdk_count}/6 SFX={sum(len(v) for v in ep_data["sfx"].values())}')

        # Emit moment_map.yaml TEMPLATE per EP (R_AUDIO_02)
        ep_dir = OUT_DIR / f'ep_{ep:02d}'
        ep_dir.mkdir(exist_ok=True)
        mm_path = ep_dir / 'moment_map_template.yaml'
        if not (ep_dir / 'moment_map.yaml').exists():
            mm_path.write_text(yaml.dump(build_moment_map_template(ep, ep_data),
                                         allow_unicode=True, sort_keys=False),
                              encoding='utf-8')

    plan_path = OUT_DIR / 'ep_audio_plan.yaml'
    plan_path.write_text(yaml.dump(plan, allow_unicode=True, sort_keys=False), encoding='utf-8')
    print(f'\nPlan: {plan_path} ({plan_path.stat().st_size/1024:.0f} KB)')

    log_path = OUT_DIR / 'library_usage_log.json'
    log_path.write_text(json.dumps({
        'piano': {tid: [(e, s) for e, s in eps] for tid, eps in usage.items()},
        'sfx': {k: list(v) for k, v in sfx_usage.items()},
    }, indent=2, ensure_ascii=False), encoding='utf-8')

    # Report
    hdk_picks = sum(1 for ep in plan['episodes'].values()
                    for p in ep['piano'].values() if p.get('source') == 'HDK_specialized')
    pixa_picks = sum(1 for ep in plan['episodes'].values()
                     for p in ep['piano'].values() if p.get('source') == 'pixabay_fallback')
    forbid_caught = sum(1 for ep in plan['episodes'].values()
                        for lst in ep['sfx'].values() for s in lst
                        if is_sfx_forbidden(s.get('title'), s.get('file')))

    boundary_dup = 0
    for ep_data in plan['episodes'].values():
        h = ep_data['piano'].get('HOOK', {}).get('id')
        c = ep_data['piano'].get('CLIFFHANGER', {}).get('id')
        if h and c and h == c: boundary_dup += 1

    cd_violations = 0
    for tid, eps_list in usage.items():
        eps_list.sort()
        for i in range(1, len(eps_list)):
            ep_prev, sec_prev = eps_list[i-1]
            ep_cur, sec_cur = eps_list[i]
            if sec_cur == sec_prev and ep_cur - ep_prev < COOLDOWN[sec_cur]:
                cd_violations += 1

    report = f"""=== SVHMP 90 EP AUDIO PLAN REPORT v2.0 ===
Generated: {plan['rules']}
EPs planned: 90 x 6 sections = 540 piano slots + ~540 SFX slots

PIANO SOURCE BREAKDOWN (R_AUDIO_05):
  HDK_specialized picks: {hdk_picks}/540 ({hdk_picks*100/540:.0f}%)
  pixabay_fallback:      {pixa_picks}/540 ({pixa_picks*100/540:.0f}%)

SETTING VALIDATION (R_AUDIO_04):
  Forbidden SFX caught (in final picks): {forbid_caught} (must be 0)

R2 VIOLATIONS (HOOK==CLIFFHANGER): {boundary_dup}/90 (0 expected)
R3 VIOLATIONS (cooldown): {cd_violations}

OUTPUT:
  {plan_path}
  {log_path}
  output/ep_NN/moment_map_template.yaml (90 files)
"""
    (OUT_DIR / 'assignment_report.txt').write_text(report, encoding='utf-8')
    print('\n' + report)

if __name__ == '__main__':
    main()
