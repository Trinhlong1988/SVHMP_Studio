"""SVHMP — Pre-render checklist (BẮT BUỘC chạy trước khi viết EP mới).

Mr.Long 27/6 lệnh: "đọc kỹ trước khi render — phải có định hướng dựng chuẩn trước
                    — tránh làm đi làm lại."

Output: ep_N_scaffold.yaml — fill từ bible lookups → AI/em đọc trước khi viết.

Usage:
    python tools/pre_render_checklist.py --ep 26
    → tạo runtime/ep_26_scaffold.yaml
    → in stdout summary checklist PASS/FAIL
"""
import yaml
import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).resolve().parents[1]

def load_yaml(path):
    return yaml.safe_load((SVHMP / path).read_text(encoding='utf-8'))

def main(ep_number):
    print(f"=== SVHMP PRE-RENDER CHECKLIST — EP{ep_number:02d} ===\n")

    checklist = {
        'ep_number': ep_number,
        'must_read': [],
        'arc_lookups': {},
        'hard_constraints': {},
        'pre_write_status': 'PENDING',
    }

    # === STEP 1: must_read files ===
    must_read = [
        'bible/00_constitution.yaml',
        'bible/09_emotion_intensity.yaml',
        'bible/11_regret_catalog.yaml',
        'bible/12_object_library.yaml',
        'bible/13_setting_library.yaml',
        'bible/21_series_arc_design.yaml',
        'prompts/ep_scaffold_template.md',
        'BUGS_FIXED.md',
    ]

    for f in must_read:
        exists = (SVHMP / f).exists()
        checklist['must_read'].append({'file': f, 'exists': exists})
        status = '✓' if exists else '✗'
        print(f"  {status} {f}")

    # === STEP 2: arc lookups ===
    print(f"\n=== ARC LOOKUPS (bible/21) ===")
    try:
        arc = load_yaml('bible/21_series_arc_design.yaml')
    except Exception as e:
        print(f"  ✗ ERR load bible/21: {e}")
        return 1

    # 2.1 Pillar R33
    pillar_map = arc.get('pillar_interleave_ep01_50', {})
    pillar = pillar_map.get(f'ep_{ep_number:02d}', '?')
    checklist['arc_lookups']['pillar'] = pillar
    print(f"  Pillar (R33): {pillar}")

    # 2.2 Intensity R34
    intensity_map = arc.get('intensity_level_per_ep', {})
    if ep_number <= 10:
        intensity = intensity_map.get('ep_1_to_10', 0.45)
    elif ep_number <= 30:
        intensity = intensity_map.get('ep_11_to_30', 0.55)
    elif ep_number <= 60:
        intensity = intensity_map.get('ep_31_to_60', 0.70)
    elif ep_number <= 80:
        intensity = intensity_map.get('ep_61_to_80', 0.85)
    else:
        intensity = intensity_map.get('ep_81_to_90', 0.95)
    if ep_number in [10, 20, 30, 40, 50, 60, 70, 80, 90]:
        ms_key = f'ep_{ep_number}_milestone'
        intensity = intensity_map.get(ms_key, intensity)
    checklist['arc_lookups']['intensity_level'] = intensity
    print(f"  Intensity (R34): {intensity}")

    # 2.3 Memory fragment R35
    memory_arc = arc.get('quang_memory_arc', {})
    memory_fragment = None
    memory_text = None
    memory_hint = None
    milestone_special = None
    for m_key, m_val in memory_arc.items():
        if ep_number in m_val.get('eps', []):
            memory_fragment = m_key
            memory_text = m_val.get('fragment', '')
            memory_hint = m_val.get('cliffhanger_hint', '')
            if m_val.get('milestone_ep') == ep_number:
                milestone_special = m_val.get('milestone_special', '')
            break
    checklist['arc_lookups']['memory_fragment'] = memory_fragment
    checklist['arc_lookups']['memory_text'] = memory_text
    checklist['arc_lookups']['cliffhanger_hint'] = memory_hint
    print(f"  Memory (R35): {memory_fragment} — {memory_text}")
    print(f"  Cliffhanger hint: {memory_hint}")

    # 2.4 Callback R36
    callback_map = arc.get('callback_schedule_s1', {})
    callback = callback_map.get(f'ep_{ep_number:02d}') or callback_map.get(f'ep_{ep_number}')
    checklist['arc_lookups']['callback'] = callback
    print(f"  Callback (R36): {callback}")

    # 2.5 Milestone R37
    milestone = ep_number in [10, 20, 30, 40, 50, 60, 70, 80, 90]
    checklist['arc_lookups']['milestone'] = milestone
    if milestone:
        print(f"  ★ MILESTONE EP — special: {milestone_special}")

    # 2.6 Object sub-arc R38
    sub_arc_map = arc.get('object_sub_arc_s1', {})
    sub_arc_match = None
    for range_key, sub_arc in sub_arc_map.items():
        # parse range like "ep_11_to_20"
        parts = range_key.split('_')
        if len(parts) >= 4:
            try:
                start = int(parts[1])
                end = int(parts[3])
                if start <= ep_number <= end:
                    sub_arc_match = {'range': range_key, **sub_arc}
                    break
            except ValueError:
                continue
    checklist['arc_lookups']['object_sub_arc'] = sub_arc_match
    print(f"  Object sub-arc (R38): {sub_arc_match}")

    # === STEP 3: hard constraints ===
    print(f"\n=== HARD CONSTRAINTS (R1-R40) ===")
    hard = {
        'word_count_target_min': 2200,  # R39
        'word_count_target_max': 2500,  # R39
        'word_count_hard_floor': 2000,  # R39 hard_floor
        'word_count_hard_ceiling': 2700,  # R39 hard_ceiling
        'duration_min_minutes': 13,  # R39
        'bell_count_max': 1,  # SERIES_RULES.bell
        'ghost_manifest_max': 1,  # SERIES_RULES.ghost_visual
        'driver_lines_max': 2 if not milestone and ep_number not in [73, 90] else 3,
        'intro_required': True,  # R40
        'name_rename_required': {'Hà': 'Hạ Vy (selective)', 'Quang': 'Khải Phong (full)'},
        'aftertaste': 'unresolved',  # ENDING_RULES
    }
    checklist['hard_constraints'] = hard
    for k, v in hard.items():
        print(f"  {k}: {v}")

    # === STEP 4: write scaffold yaml ===
    out_path = SVHMP / 'runtime' / f'ep_{ep_number:02d}_scaffold.yaml'
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(
        yaml.dump(checklist, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding='utf-8'
    )
    print(f"\n=== SCAFFOLD SAVED ===")
    print(f"  {out_path}")
    print(f"\n  → AI/em ĐỌC scaffold này TRƯỚC khi viết episode.md")
    print(f"  → Fill template từ prompts/ep_scaffold_template.md")
    print(f"  → Sau khi render: python tools/post_render_gate.py --ep {ep_number}")

    # Final status
    all_files_exist = all(item['exists'] for item in checklist['must_read'])
    arc_complete = all([pillar != '?', memory_fragment is not None, intensity is not None])
    if all_files_exist and arc_complete:
        print(f"\n  ✓ PASS — sẵn sàng viết EP{ep_number:02d}")
        return 0
    else:
        print(f"\n  ✗ FAIL — fix vấn đề trước khi viết")
        return 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ep', type=int, required=True, help='EP number to scaffold')
    args = parser.parse_args()
    sys.exit(main(args.ep))
