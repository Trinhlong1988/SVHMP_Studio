"""BP2 DOMAIN CHECK v1.0.0 — gate may cho BP2 Domain Architecture.

Nguon luat: BP0 v2.0 LOCKED + BP1 locked. Kiem domain_specs.yaml:
  1  Du 13 domain tang thap (canon 8 + character/object/dialogue/event + story_planner);
     domain la ngoai inventory BP0 = FAIL; domain thieu facets = FAIL.
  2  facet_id DUY NHAT TOAN CUC (1 facet thuoc dung 1 domain — trung 2 domain = FAIL).
  3  Facet du field: facet_id/desc/data_type/sot.
  4  SoT exists: path phai ton tai + neu co key thi KEY PHAI RESOLVE that trong yaml
     (dotted path, vd tier_1_mandatory.core_id) — khai lao = FAIL.
  5  SoT/enforcer planned: PLANNED HONESTY 5 metadata + milestone thuoc BP0
     + planned_path chua ton tai (drift/stub = FAIL).
  6  Invariant: co rule + enforcer; enforcer exists ma path khong ton tai = ENFORCER-MA FAIL.
  7  DUP-KEY loader (C10) + VERSION khop checker/BP0.

Exit 0 = PASS, exit 1 = FAIL.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402

__version__ = '1.0.0'

D_SPEC = REPO / 'governance' / 'blueprint' / 'bp2' / 'domain_specs.yaml'
D_BP0 = REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml'

REQUIRED_BP2_DOMAINS = ['world', 'timeline', 'location', 'weather', 'culture', 'belief',
                        'ritual', 'supernatural', 'character', 'object', 'dialogue',
                        'event', 'story_planner']
PLANNED_META = ['planned_path', 'owner', 'reason_not_exists_yet',
                'target_milestone', 'blocking_dependency']


def _resolve_key(doc, dotted):
    cur = doc
    for part in str(dotted).split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    return True


def _planned_errors(label, ref, milestones, root):
    errs = []
    for k in PLANNED_META:
        if not ref.get(k):
            errs.append(f'{label}: PLANNED HONESTY — thieu metadata {k}')
    tm = ref.get('target_milestone')
    if tm and tm not in milestones:
        errs.append(f'{label}: target_milestone {tm!r} khong co trong milestones BP0')
    pp = ref.get('planned_path')
    if pp and (Path(root) / pp).exists():
        errs.append(f'{label}: khai planned nhung path DA ton tai — DRIFT/STUB: {pp}')
    return errs


def run_checks(spec_p=D_SPEC, bp0_p=D_BP0, root=REPO):
    errs, warns = [], []
    try:
        spec = load_yaml_no_dup(Path(spec_p).read_text(encoding='utf-8'))
    except DupKeyError as e:
        return [f'domain_specs: DUP-KEY — {e}'], warns
    except Exception as e:
        return [f'domain_specs: khong doc duoc: {e}'], warns
    try:
        bp0 = load_yaml_no_dup(Path(bp0_p).read_text(encoding='utf-8'))
    except Exception as e:
        return [f'BP0: khong doc duoc: {e}'], warns

    inv = bp0.get('domains') or {}
    milestones = bp0.get('milestones') or {}
    src_ver = str((bp0.get('meta') or {}).get('contract_version'))

    if str(spec.get('validator_version')) != __version__:
        errs.append(f"VERSION validator_version {spec.get('validator_version')} != checker {__version__}")
    if str(spec.get('source_constitution_version')) != src_ver:
        errs.append(f"VERSION source_constitution_version != BP0 contract {src_ver}")

    doms = spec.get('domains') or {}
    for d in REQUIRED_BP2_DOMAINS:
        if d not in doms:
            errs.append(f'THIEU domain block: {d}')
    for d in doms:
        if d not in inv:
            errs.append(f'DOMAIN-LA ngoai inventory BP0: {d}')

    yaml_cache = {}
    def _load_target(path):
        if path not in yaml_cache:
            try:
                yaml_cache[path] = load_yaml_no_dup((Path(root) / path).read_text(encoding='utf-8'))
            except Exception:
                yaml_cache[path] = None
        return yaml_cache[path]

    seen_facets = {}
    for dname, block in doms.items():
        block = block or {}
        facets = block.get('facets') or []
        if not facets:
            errs.append(f'{dname}: THIEU facets (domain phai co sub-scope inventory)')
        if not (block.get('entities') or []):
            errs.append(f'{dname}: thieu entities')
        if not (block.get('invariants') or []):
            errs.append(f'{dname}: thieu invariants')
        for f in facets:
            fid = f.get('facet_id')
            if not fid:
                errs.append(f'{dname}: facet thieu facet_id')
                continue
            if fid in seen_facets:
                errs.append(f'facet {fid!r}: TRUNG 2 domain ({seen_facets[fid]} + {dname}) '
                            '— 1 facet thuoc dung 1 domain')
            seen_facets[fid] = dname
            for k in ('desc', 'data_type', 'sot'):
                if not f.get(k):
                    errs.append(f'{dname}.{fid}: thieu {k}')
            sot = f.get('sot') or {}
            st = sot.get('status')
            if st == 'exists':
                p = sot.get('path')
                if not p:
                    errs.append(f'{dname}.{fid}: sot exists thieu path')
                elif not (Path(root) / p).exists():
                    errs.append(f'{dname}.{fid}: SoT khai exists nhung path KHONG ton tai '
                                f'(khai lao/phantom): {p}')
                elif sot.get('key'):
                    doc = _load_target(p)
                    if doc is None or not _resolve_key(doc, sot['key']):
                        errs.append(f"{dname}.{fid}: SoT key {sot['key']!r} KHONG resolve "
                                    f'duoc trong {p} (khai key lao)')
            elif st == 'planned':
                errs += _planned_errors(f'{dname}.{fid}.sot', sot, milestones, root)
            else:
                errs.append(f"{dname}.{fid}: sot.status {st!r} khong thuoc exists|planned")
        for i, iv in enumerate(block.get('invariants') or []):
            iv = iv or {}
            if not iv.get('rule'):
                errs.append(f'{dname}.invariants[{i}]: thieu rule')
            enf = iv.get('enforcer') or {}
            est = enf.get('status')
            if est == 'exists':
                p = enf.get('path')
                if not p or not (Path(root) / p).exists():
                    errs.append(f'{dname}.invariants[{i}]: ENFORCER-MA — khai exists nhung '
                                f'khong ton tai: {p}')
            elif est == 'planned':
                errs += _planned_errors(f'{dname}.invariants[{i}].enforcer', enf, milestones, root)
            else:
                errs.append(f'{dname}.invariants[{i}]: enforcer.status {est!r} khong thuoc exists|planned')
    return errs, warns


def main(argv):
    kw = {}
    if '--spec' in argv:
        kw['spec_p'] = Path(argv[argv.index('--spec') + 1])
    if '--bp0' in argv:
        kw['bp0_p'] = Path(argv[argv.index('--bp0') + 1])
    print(f'=== BP2 DOMAIN CHECK v{__version__} ===')
    errs, warns = run_checks(**kw)
    for w in warns:
        print(f'  [WARN] {w}')
    if errs:
        for e in errs:
            print(f'  [VIOLATION] {e}')
        print(f'=== FAIL — {len(errs)} vi pham ===')
        return 1
    spec = load_yaml_no_dup(Path(kw.get('spec_p', D_SPEC)).read_text(encoding='utf-8'))
    n_f = sum(len((b or {}).get('facets') or []) for b in spec['domains'].values())
    n_ex = sum(1 for b in spec['domains'].values() for f in ((b or {}).get('facets') or [])
               if (f.get('sot') or {}).get('status') == 'exists')
    print(f'  domains: {len(spec["domains"])}/13 · facets: {n_f} ({n_ex} exists / {n_f - n_ex} planned)'
          f' · facet_id unique toan cuc')
    print('=== PASS — BP2 domain specs hop le (0 vi pham) ===')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
