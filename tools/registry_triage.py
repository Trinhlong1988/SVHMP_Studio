"""SVHMP — Registry Triage (G1, Boss 2/7): map 186 file UNMAPPED vao domain bang LUAT
(deterministic, khong suy luan), co canh bao DEPRECATED (backup/one-off) + DUP (version).
Xuat governance/file_index.yaml + report histogram. Checker se tinh file_index la da map.
"""
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml

SVHMP = Path(__file__).parent.parent

# Luat phan loai theo prefix/keyword — thu tu tren xuong, match dau tien thang.
# (domain, tier, [regex tren ten file stem])
RULES = [
    ('governance_audit', 0, [r'^bible_audit', r'_audit$', r'^audit_r\d', r'^check_rule', r'^verify_',
                             r'^deep_200', r'^historical_bug', r'^hidden_audit', r'^hardcode_classifier',
                             r'^session_start', r'^project_health', r'^svhmp_100check', r'^svhmp_final',
                             r'^svhmp_dupe', r'^flush_rules', r'^svhmp_audit', r'^bible_consumer',
                             r'^registry_triage', r'^check_counter', r'^architecture_registry',
                             r'^ci_gate', r'^deprecation_report', r'^gen_domain_manifests']),
    ('text_migration_DEPRECATED', 1, [r'^rewrite_ep', r'^rewrite_batch', r'^rewrite_pov', r'^fix_anaphora',
                                      r'^fix_chains', r'^auto_fix_r61', r'^rewrite_ep01']),
    ('text_autofix', 3, [r'^auto_fix_', r'^fix_', r'^text_batch_fix', r'^detect_template', r'^pre_write_enforcer']),
    ('text_qa', 3, [r'^audit_', r'^qa_anti_generic', r'^qa_honorific', r'^qa_fact', r'^qa_repeat',
                    r'^qa_continuity', r'^qa_dialogue_identity', r'^qa_phonetic', r'^qa_ssot',
                    r'^vnsl_validator', r'^whitelist_gen_vn', r'^vietnamese_qa']),
    ('audio_qa', 3, [r'^qa_boundary', r'^qa_breath', r'^qa_onset', r'^qa_concat', r'^qa_prosody',
                     r'^qa_whisper', r'^qa_pause', r'^qa_post_render', r'^qa_pre_render', r'^audio_qa_',
                     r'^qa_output_writer', r'^qa_watch', r'^audit_audio']),
    ('audio_render', 4, [r'^render_', r'^build_mix', r'^music_', r'^sfx_', r'^gen_sfx', r'^vary_',
                         r'^apply_pause', r'^spec_chunk', r'^tts_adapter', r'^patch_audio', r'^hook_swell',
                         r'^audio_pre_ship', r'^post_render_gate', r'^post_rotate', r'^pre_render',
                         r'^pre_verify_word', r'^ab_test_tail', r'^cleanup_vary']),
    ('generation', 2, [r'^auto_gen_ep', r'^sequential_', r'^build_specs', r'^sync_specs', r'^assignment_planner',
                       r'^related_eps', r'^episode_state', r'^auto_qa_orchestrator', r'^qa_skeptic',
                       r'^adversarial_skeptic', r'^spec_']),
    ('orchestration', 2, [r'^auto_watch', r'^qa_watch', r'^cmd_progress', r'^render_progress',
                          r'^e2e_pipeline', r'^project_bootstrap', r'^project_shutdown', r'^log_rename',
                          r'^verify_ping', r'^trim_driver']),
    ('voice', 2, [r'^voice_profile', r'^extract_speaker', r'^audit_voice', r'^audit_driver_dialogue']),
    ('analytics', 5, [r'^analytics_', r'^cost_tracker', r'^publish_score']),
    ('infra', 0, [r'^llm_router', r'^pre_render_checklist', r'^pre_render_audit']),
    ('bible_library', 1, [r'^\d\d[a-z]?_']),  # bible/NN_*
    ('tests', 3, [r'^test_']),
]
DEPRECATED_PAT = [r'backup', r'_v1_', r'^rewrite_ep', r'^rewrite_batch', r'_r61', r'zero_tolerance',
                  r'^fix_anaphora', r'^fix_chains', r'aggressive$']


def classify(rel: str):
    stem = Path(rel).stem
    dep = any(re.search(p, stem) for p in DEPRECATED_PAT)
    for dom, tier, pats in RULES:
        if any(re.search(p, stem) for p in pats):
            status = 'deprecated' if (dep or dom.endswith('DEPRECATED')) else 'active'
            return dom.replace('_DEPRECATED', ''), tier, status
    return 'unclassified', None, ('deprecated' if dep else 'active')


def main():
    files = []
    for pat in ['tools/*.py', 'bible/*.yaml', 'tests/test_*.py']:
        for p in SVHMP.glob(pat):
            files.append(str(p.relative_to(SVHMP)).replace('\\', '/'))

    index = {}
    hist = Counter()
    dep = []
    stems = defaultdict(list)
    for f in sorted(files):
        dom, tier, status = classify(f)
        index[f] = {'domain': dom, 'tier': tier, 'status': status}
        hist[dom] += 1
        if status == 'deprecated':
            dep.append(f)
        base = re.sub(r'(_v\d+|_backup|_final|_r\d+)$', '', Path(f).stem)
        stems[base].append(f)

    dups = {b: v for b, v in stems.items() if len(v) > 1}

    (SVHMP / 'governance' / 'file_index.yaml').write_text(
        yaml.safe_dump({'generated_by': 'tools/registry_triage.py', 'date': '2026-07-02',
                        'total': len(index), 'files': index}, allow_unicode=True, sort_keys=True),
        encoding='utf-8')

    print(f"=== REGISTRY TRIAGE — {len(files)} file ===")
    print("[HISTOGRAM domain]")
    for d, n in hist.most_common():
        print(f"  {d:26}: {n}")
    print(f"\n[DEPRECATED] {len(dep)} (backup/one-off/v1) — de xuat archive:")
    for d in dep[:20]:
        print(f"  ~ {d}")
    if len(dep) > 20:
        print(f"  ... +{len(dep)-20}")
    print(f"\n[UNCLASSIFIED] {hist['unclassified']} (can Boss/CMD gan tay)")
    print(f"[DUP groups] {len(dups)} (nhieu version):")
    for b, v in list(dups.items())[:10]:
        print(f"  ! {b}: {[Path(x).name for x in v]}")
    print(f"\n→ governance/file_index.yaml ({len(index)} file mapped)")


if __name__ == '__main__':
    main()
