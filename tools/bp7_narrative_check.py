"""BP7 NARRATIVE CHECK v1.0.0 — gate máy cho BP7 Narrative Architecture.

Check:
  1  DUP-KEY loader single-impl (import blueprint_constitution_check) + version
     khớp checker/3 file bp7 (story_structure/cultural_spec/pacing_format).
  2  story_structure: level 'episode'.components_required PHẢI == ĐÚNG THỨ TỰ
     bible/01_narrative_structure.yaml#bimodal_sentence_length_per_section.
     pattern_per_section keys (thiếu/thừa/sai thứ tự = FAIL) · mọi level.sot
     status=exists path+key PHẢI resolve thật · status=planned đủ 5 metadata.
  3  cultural_spec: mọi item.domain_facet (dạng "domain.facet_id") PHẢI resolve
     thật trong bp2/domain_specs.yaml đúng domain đã khai (facet ma = FAIL).
  4  pacing_format: KHÔNG số (int/float) bất kỳ đâu trong toàn file (scan TOÀN
     FILE ngay từ đầu — mirror bài học BP6 audit 4/7, KHÔNG lặp lỗ hổng cũ) ·
     curve_ref PHẢI khớp đúng knob_id đã khai trong bp6/decision_contract.yaml
     (curve ma = FAIL).

Exit 0 = PASS, exit 1 = FAIL.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402
from bp6_decision_check import _numeric_leaks  # noqa: E402 (tai su dung — khong viet lai)

__version__ = '1.0.0'

BP7 = REPO / 'governance' / 'blueprint' / 'bp7'
D_STRUCTURE = BP7 / 'story_structure.yaml'
D_CULTURAL = BP7 / 'cultural_spec.yaml'
D_PACING = BP7 / 'pacing_format.yaml'
D_BP2 = REPO / 'governance' / 'blueprint' / 'bp2' / 'domain_specs.yaml'
D_BP6 = REPO / 'governance' / 'blueprint' / 'bp6' / 'decision_contract.yaml'
D_BIBLE01 = REPO / 'bible' / '01_narrative_structure.yaml'

EPISODE_COMPONENTS_EXPECTED = ['HOOK', 'SETUP', 'INCIDENT', 'REVEAL', 'PAYOFF', 'CLIFFHANGER']
PLANNED_META = ['planned_path', 'owner', 'reason_not_exists_yet',
                'target_milestone', 'blocking_dependency']


def _load(path, errs, label):
    try:
        return load_yaml_no_dup(Path(path).read_text(encoding='utf-8'))
    except DupKeyError as e:
        errs.append(f'{label}: DUP-KEY — {e}')
    except Exception as e:
        errs.append(f'{label}: khong doc duoc: {e}')
    return None


def _resolve_key(doc, dotted):
    cur = doc
    for part in str(dotted).split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return True


def check_story_structure(structure, bible01, root=REPO):
    """Check 2. Tra ve list loi."""
    errs = []
    levels = {lv.get('level_id'): lv for lv in (structure or {}).get('levels') or []}

    ep = levels.get('episode')
    if ep is None:
        errs.append('story_structure: THIEU level episode')
    else:
        got = ep.get('components_required') or []
        if got != EPISODE_COMPONENTS_EXPECTED:
            errs.append(f'COMPONENT-LECH-BIBLE01: episode.components_required {got} '
                        f'!= bible/01 thu tu {EPISODE_COMPONENTS_EXPECTED}')
        expected_keys = list(((bible01 or {}).get('bimodal_sentence_length_per_section') or {})
                             .get('pattern_per_section', {}).keys())
        if expected_keys and expected_keys != EPISODE_COMPONENTS_EXPECTED:
            errs.append(f'bible/01 pattern_per_section thu tu da doi {expected_keys} — '
                        'checker EPISODE_COMPONENTS_EXPECTED can dong bo (RFC)')

    for lid, lv in levels.items():
        sot = lv.get('sot') or {}
        st = sot.get('status')
        if st == 'exists':
            p = sot.get('path')
            if not p or not (Path(root) / p).exists():
                errs.append(f'{lid}: SoT khai exists nhung KHONG ton tai (phantom): {p}')
        elif st == 'planned':
            for m in PLANNED_META:
                if not sot.get(m):
                    errs.append(f'{lid}.sot: PLANNED HONESTY — thieu metadata {m}')
        else:
            errs.append(f'{lid}: sot.status {st!r} khong thuoc exists|planned')

    # resolve key that (tach rieng vong lap de dung cache doc thuc su)
    yaml_cache = {}
    for lid, lv in levels.items():
        sot = lv.get('sot') or {}
        if sot.get('status') == 'exists' and sot.get('key'):
            p = sot['path']
            if p not in yaml_cache:
                try:
                    yaml_cache[p] = load_yaml_no_dup((Path(root) / p).read_text(encoding='utf-8'))
                except Exception:
                    yaml_cache[p] = None
            doc = yaml_cache[p]
            if doc is None or not _resolve_key(doc, sot['key']):
                errs.append(f"{lid}: SoT key {sot['key']!r} KHONG resolve duoc trong {p} (khai key lao)")
    return errs


def check_cultural_spec(cultural, bp2, root=REPO):
    """Check 3. Tra ve list loi."""
    errs = []
    doms = (bp2 or {}).get('domains') or {}
    for item in (cultural or {}).get('items') or []:
        name = item.get('item', '?')
        df = str(item.get('domain_facet', ''))
        if '.' not in df:
            errs.append(f'{name}: domain_facet {df!r} sai dinh dang (can "domain.facet_id")')
            continue
        dom, fid = df.split('.', 1)
        facets = [f.get('facet_id') for f in (doms.get(dom) or {}).get('facets') or []]
        if dom not in doms:
            errs.append(f'{name}: FACET-MA domain {dom!r} khong ton tai trong bp2')
        elif fid not in facets:
            errs.append(f'{name}: FACET-MA facet_id {fid!r} khong ton tai trong bp2.{dom}')
    return errs


def check_pacing_format(pacing, bp6):
    """Check 4. Tra ve list loi."""
    errs = []
    # R195 full-file scan TU DAU (bai hoc BP6 audit 4/7 — khong lap lo hong scan-thieu)
    for leak in _numeric_leaks(pacing, 'pacing_format', allowed_keys=set()):
        errs.append(f'R195-HARDCODE: so hardcode trong pacing_format tai {leak} '
                    '(pacing_format la FORMAT thuan, 0 so duoc phep)')

    knob_ids = {k.get('knob_id') for k in (bp6 or {}).get('knobs') or []}
    for entry in (pacing or {}).get('curve_application') or []:
        ref = str(entry.get('curve_ref', ''))
        parts = ref.split('.')
        kid = parts[-1] if parts else ''
        if not ref.startswith('bp6.decision_contract.knobs.') or kid not in knob_ids:
            errs.append(f'CURVE-MA: curve_ref {ref!r} khong khop knob_id nao trong bp6/decision_contract.yaml {sorted(knob_ids)}')
    return errs


def main():
    errs = []
    structure = _load(D_STRUCTURE, errs, 'story_structure')
    cultural = _load(D_CULTURAL, errs, 'cultural_spec')
    pacing = _load(D_PACING, errs, 'pacing_format')
    bp2 = _load(D_BP2, errs, 'bp2_domain_specs')
    bp6 = _load(D_BP6, errs, 'bp6_decision_contract')
    bible01 = _load(D_BIBLE01, errs, 'bible01')

    if None not in (structure, cultural, pacing):
        for doc, label in ((structure, 'story_structure'), (cultural, 'cultural_spec'),
                           (pacing, 'pacing_format')):
            v = str((doc.get('meta') or {}).get('version'))
            if v != __version__:
                errs.append(f'{label}: version {v} != checker {__version__}')
        errs += check_story_structure(structure, bible01)
        errs += check_cultural_spec(cultural, bp2)
        errs += check_pacing_format(pacing, bp6)

    print(f'=== BP7 NARRATIVE CHECK v{__version__} ===')
    for e in errs:
        print(f'  [VIOLATION] {e}')
    n_lv = len(((structure or {}).get('levels')) or [])
    n_it = len(((cultural or {}).get('items')) or [])
    n_cv = len(((pacing or {}).get('curve_application')) or [])
    print(f'  levels: {n_lv}/6 · cultural items: {n_it}/7 · curve_application: {n_cv}/5')
    print(f"=== {'FAIL — ' + str(len(errs)) + ' vi pham' if errs else 'PASS'} ===")
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
