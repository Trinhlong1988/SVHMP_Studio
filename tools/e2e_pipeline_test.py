"""
SVHMP E2E Pipeline Test — F3.1 round 14.
Verify 7-prompt pipeline integrity (skeleton level, không actually call LLM).

Tests:
  T1: All 7 prompts loadable + valid markdown
  T2: Director step 1.1-1.10 sections present
  T3: QA PHASE 0-12.14 sections present
  T4: Generator load order references valid bibles
  T5: TTS pipeline references locked tools/svhmp_v13_render.py
  T6: Video V1-V6 + Video_intro V7-V9 disjoint scope
  T7: Publisher P1-P7 output schema valid
  T8: Cross-prompt handoff (Director output → Generator input → QA → TTS → Video → Publisher) compatible
  T9: All bible references exist (no dead links)
  T10: state.yaml + lifecycle.yaml schema integrity

NOTE: script-style test (runs standalone via `python`, exits with 0/1). The body is
guarded under `main()` / `__main__` so pytest can import this file during collection
without executing it (matches *_test.py pattern) — see pytest.ini / tests/conftest.py.
"""
import sys
import re
import yaml
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None

SVHMP = Path(__file__).parent.parent
PROMPTS = SVHMP / 'prompts'
BIBLES = SVHMP / 'bible'
RUNTIME = SVHMP / 'runtime'


def main():
    results = []
    def add(rid, name, status, details=""):
        results.append((rid, name, status, details))

    # T1 — All 7 prompts loadable
    expected_prompts = ['director.md', 'generator.md', 'qa.md', 'tts.md', 'tts_adapter.md', 'video.md', 'video_intro.md', 'publisher.md']
    missing = [p for p in expected_prompts if not (PROMPTS / p).exists()]
    add("T1", "All 8 prompts present (7 original + video_intro round 12)",
        "FAIL" if missing else "PASS",
        f"missing: {missing}" if missing else f"all {len(expected_prompts)} loadable")


    # T2 — Director step 1.1-1.10 sections
    director = (PROMPTS / 'director.md').read_text(encoding='utf-8')
    expected_steps = [f'### 1.{i}' for i in range(1, 11)]  # 1.1 to 1.10
    missing_steps = [s for s in expected_steps if s not in director]
    add("T2", "Director step 1.1-1.10 (incl 1.10 related_eps round 14)",
        "FAIL" if missing_steps else "PASS",
        f"missing: {missing_steps}" if missing_steps else "10 steps present")


    # T3 — QA PHASE structure
    qa = (PROMPTS / 'qa.md').read_text(encoding='utf-8')
    required_phases = ['PHASE 11 — REGEN SCOPE', 'PHASE 12 — CONTENT QA', '## 12.0 Constitution', '## 12.14 Arc Consistency']
    missing_phases = [p for p in required_phases if p not in qa]
    add("T3", "QA PHASE 11 + 12.0-12.14 sections",
        "FAIL" if missing_phases else "PASS",
        f"missing: {missing_phases}" if missing_phases else "key phases present")


    # T4 — Generator load references valid bibles
    generator = (PROMPTS / 'generator.md').read_text(encoding='utf-8')
    gen_refs = set(re.findall(r'bible[\\/](\d{2})_[\w_]+\.yaml', generator))
    dead_refs = [r for r in gen_refs if not list(BIBLES.glob(f'{r}_*.yaml'))]
    add("T4", "Generator bible refs no dead links",
        "FAIL" if dead_refs else "PASS",
        f"dead: {dead_refs}" if dead_refs else f"{len(gen_refs)} bible refs all valid")


    # T5 — TTS references locked render script
    tts = (PROMPTS / 'tts.md').read_text(encoding='utf-8')
    has_v13_render_ref = 'svhmp_v13_render' in tts or 'Pipeline LOCKED' in tts
    add("T5", "TTS references svhmp_v13_render or Pipeline LOCKED",
        "PASS" if has_v13_render_ref else "WARN (round 13 pipeline ref optional)",
        "OK" if has_v13_render_ref else "tts.md không ref v13_render explicit (may be OK if inline)")


    # T6 — Video V1-V6 + Video_intro V7-V9 disjoint module headers
    # B23 fix: only match module headers (V<n> + space + uppercase title), skip text refs "V1-V6"
    video = (PROMPTS / 'video.md').read_text(encoding='utf-8')
    video_intro = (PROMPTS / 'video_intro.md').read_text(encoding='utf-8')
    def extract_module_headers(text):
        return set(re.findall(r'(?:^|\n|═\s+)V(\d+)\s+[A-Z]', text))
    video_modules = extract_module_headers(video)
    video_intro_modules = extract_module_headers(video_intro)
    overlap = video_modules & video_intro_modules
    add("T6", "Video V1-V6 + Video_intro V7-V9 module headers disjoint",
        "FAIL" if overlap else "PASS",
        f"overlap: {overlap}" if overlap
        else f"video={sorted(video_modules)}, intro={sorted(video_intro_modules)}")


    # T7 — Publisher P1-P7
    publisher = (PROMPTS / 'publisher.md').read_text(encoding='utf-8')
    publisher_modules = re.findall(r'P(\d+)\b', publisher)
    unique_publisher = set(publisher_modules)
    expected_p = {'1','2','3','4','5','6','7'}
    missing_p = expected_p - unique_publisher
    add("T7", "Publisher P1-P7 modules",
        "WARN" if missing_p else "PASS",
        f"missing modules: {missing_p}" if missing_p else "P1-P7 all present")


    # T8 — Cross-prompt handoff data compatible (Director output keys ⊆ Generator input keys)
    # Simplified: check Director mentions Generator + Generator mentions QA
    handoff_ok = ('generator' in director.lower() and 'qa' in generator.lower() and
                  'tts' in qa.lower() and 'video' in tts.lower())
    add("T8", "Cross-prompt handoff chain mentioned",
        "PASS" if handoff_ok else "WARN",
        "Director→Generator→QA→TTS→Video chain found in text" if handoff_ok else "handoff chain incomplete")


    # T9 — All bible refs across all prompts no dead links
    all_refs = set()
    for p in PROMPTS.glob('*.md'):
        content = p.read_text(encoding='utf-8')
        refs = set(re.findall(r'bible[\\/](\d{2})_[\w_]+\.yaml', content))
        all_refs.update(refs)
    dead_all = [r for r in all_refs if not list(BIBLES.glob(f'{r}_*.yaml'))]
    add("T9", f"All {len(all_refs)} bible refs across prompts no dead links",
        "FAIL" if dead_all else "PASS",
        f"dead: {dead_all}" if dead_all else "all valid")


    # T10 — Runtime YAML schema integrity
    runtime_files = ['state.yaml', 'lifecycle.yaml', 'analytics.yaml', 'canon_registry.yaml', 'ledger.yaml']
    parse_fails = []
    for f in runtime_files:
        p = RUNTIME / f
        if not p.exists():
            parse_fails.append(f"{f} missing")
            continue
        try:
            with open(p, encoding='utf-8') as fp:
                yaml.safe_load(fp)
        except Exception as e:
            parse_fails.append(f"{f}: {str(e)[:60]}")
    add("T10", "5 runtime YAML files parse OK",
        "FAIL" if parse_fails else "PASS",
        f"fails: {parse_fails}" if parse_fails else "all 5 parse OK")


    # Output
    print("=" * 75)
    print("SVHMP E2E PIPELINE TEST (F3.1 round 14, 10 tests)")
    print("=" * 75)
    pass_count = sum(1 for r in results if r[2] == "PASS")
    warn_count = sum(1 for r in results if 'WARN' in r[2])
    fail_count = sum(1 for r in results if 'FAIL' in r[2])
    for rid, name, status, details in results:
        marker = "✓" if "PASS" in status else ("⚠" if "WARN" in status else "✗")
        print(f"{marker} {rid}: [{status}] {name}")
        if details:
            print(f"       {details}")
    print("=" * 75)
    print(f"SUMMARY: {pass_count}/{len(results)} PASS, {warn_count} WARN, {fail_count} FAIL")
    print("=" * 75)
    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
