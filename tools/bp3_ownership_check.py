"""BP3 OWNERSHIP CHECK v1.0.0 — gate may cho BP3 Ownership + Dependency.

LUAT VANG: 1 facet = DUNG 1 writer-domain (mirror "bible writer = mr_long").
Check:
  1  DUP-KEY loader moi file BP3 (C10 pattern) + VERSION khop checker/BP0.
  2  COVERAGE 2 CHIEU voi bp2/domain_specs: matrix thieu facet BP2 da khai = FAIL;
     facet MA (khong co trong BP2) = FAIL.
  3  owning_domain phai DUNG domain block chua facet trong BP2 (drift = FAIL).
  4  1-facet-1-writer: writable_by ⊆ {owner, mr_long}; dung ≤1 domain (va phai la owner);
     writable ∩ forbidden_writers = ∅; moi ten trong readable/writable/forbidden
     phai la domain inventory hoac mr_long.
  5  DEP 3-NGUON-KHOP: blueprint_domains.dependencies == bp1 graph.depends_on
     == bp3 dependency_detail (exact set, lech bat ky = FAIL); reason 1 dong
     bat buoc (MISSING_REASON = FAIL); data_flow ∈ read|write.
  6  Phan quyet ngu nghia (da chot, khong mo lai): emotion_trigger owner=character;
     narration_voice owner=dialogue.

Exit 0 = PASS, exit 1 = FAIL.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402

__version__ = '1.0.0'

BP3 = REPO / 'governance' / 'blueprint' / 'bp3'
D_MATRIX = BP3 / 'facet_ownership_matrix.yaml'
D_DEP = BP3 / 'dependency_detail.yaml'
D_BP2 = REPO / 'governance' / 'blueprint' / 'bp2' / 'domain_specs.yaml'
D_BP1 = REPO / 'governance' / 'blueprint' / 'bp1' / 'dependency_graph.yaml'
D_BP0 = REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml'

ADJUDICATED = {'emotion_trigger': 'character', 'narration_voice': 'dialogue'}


def _load(path, errs, label):
    try:
        return load_yaml_no_dup(Path(path).read_text(encoding='utf-8'))
    except DupKeyError as e:
        errs.append(f'{label}: DUP-KEY — {e}')
    except Exception as e:
        errs.append(f'{label}: khong doc duoc: {e}')
    return None


def run_checks(matrix_p=D_MATRIX, dep_p=D_DEP, bp2_p=D_BP2, bp1_p=D_BP1, bp0_p=D_BP0):
    errs, warns = [], []
    matrix = _load(matrix_p, errs, 'facet_ownership_matrix')
    depd = _load(dep_p, errs, 'dependency_detail')
    bp2 = _load(bp2_p, errs, 'BP2')
    bp1 = _load(bp1_p, errs, 'BP1-graph')
    bp0 = _load(bp0_p, errs, 'BP0')
    if not all([matrix, depd, bp2, bp1, bp0]):
        return errs, warns

    inv = bp0.get('domains') or {}
    src = str((bp0.get('meta') or {}).get('contract_version'))
    for label, doc in (('facet_ownership_matrix', matrix), ('dependency_detail', depd)):
        if str(doc.get('validator_version')) != __version__:
            errs.append(f'{label}: VERSION validator_version != checker {__version__}')
        if str(doc.get('source_constitution_version')) != src:
            errs.append(f'{label}: VERSION source_constitution_version != BP0 {src}')

    # facet map tu BP2 (facet_id -> domain)
    bp2_owner = {}
    for dname, block in (bp2.get('domains') or {}).items():
        for f in ((block or {}).get('facets') or []):
            bp2_owner[f.get('facet_id')] = dname

    seen = set()
    for f in (matrix.get('facets') or []):
        fid = f.get('facet_id')
        if not fid:
            errs.append('matrix: facet thieu facet_id')
            continue
        if fid in seen:
            errs.append(f'matrix {fid}: khai 2 lan')
        seen.add(fid)
        own = f.get('owning_domain')
        if fid not in bp2_owner:
            errs.append(f'matrix {fid}: FACET-MA — khong ton tai trong bp2/domain_specs (drift)')
        elif own != bp2_owner[fid]:
            errs.append(f'matrix {fid}: owner {own!r} != domain block BP2 ({bp2_owner[fid]!r})')
        if own not in inv:
            errs.append(f'matrix {fid}: owner {own!r} khong trong inventory')
        wb = f.get('writable_by') or []
        non_ml = [w for w in wb if w != 'mr_long']
        if len(non_ml) > 1:
            errs.append(f'matrix {fid}: {len(non_ml)} writer-domain — LUAT VANG 1 facet = DUNG 1 writer')
        for w in non_ml:
            if w != own:
                errs.append(f'matrix {fid}: writable_by {w!r} VUOT owner rule (chi {own}/mr_long)')
        if not wb:
            errs.append(f'matrix {fid}: writable_by rong — facet vo chu but')
        fw = f.get('forbidden_writers') or []
        for w in set(wb) & set(fw):
            errs.append(f'matrix {fid}: {w!r} vua writable vua forbidden')
        for who in list(f.get('readable_by') or []) + list(wb) + list(fw):
            if who not in inv and who != 'mr_long':
                errs.append(f'matrix {fid}: ten la {who!r} khong trong inventory')
        for k in ('lifecycle', 'owner_artifact'):
            if not f.get(k):
                errs.append(f'matrix {fid}: thieu {k}')
    for fid in set(bp2_owner) - seen:
        errs.append(f'matrix: THIEU facet BP2 da khai: {fid} (coverage 2 chieu)')

    # phan quyet ngu nghia
    for fid, own in ADJUDICATED.items():
        if fid in bp2_owner and bp2_owner[fid] != own:
            errs.append(f'PHAN-QUYET: {fid} phai owner={own} (da chot, khong mo lai)')

    # dep 3 nguon
    set0 = {(n, t) for n, d in inv.items() for t in (d.get('dependencies') or [])}
    set1 = {(d.get('domain_id'), t) for d in (bp1.get('domains') or [])
            for t in (d.get('depends_on') or [])}
    set3 = set()
    for dp in (depd.get('dependencies') or []):
        edge = (dp.get('from'), dp.get('to'))
        set3.add(edge)
        if not dp.get('reason') or dp.get('reason') == 'MISSING_REASON':
            errs.append(f'dep {dp.get("dep_id")}: thieu reason (vi sao dep ton tai)')
        if dp.get('data_flow') not in ('read', 'write'):
            errs.append(f'dep {dp.get("dep_id")}: data_flow phai read|write')
        for who in edge:
            if who not in inv:
                errs.append(f'dep {dp.get("dep_id")}: domain la {who!r}')
    for a, b, name in ((set0, set3, 'BP0 vs BP3'), (set1, set3, 'BP1 vs BP3'), (set0, set1, 'BP0 vs BP1')):
        for e in sorted(a - b):
            errs.append(f'DEP-3-NGUON lech ({name}): thieu {e[0]}->{e[1]} o nguon sau')
        for e in sorted(b - a):
            errs.append(f'DEP-3-NGUON lech ({name}): thua {e[0]}->{e[1]} o nguon sau')
    return errs, warns


def main(argv):
    kw = {}
    flags = {'--matrix': 'matrix_p', '--dep': 'dep_p', '--bp2': 'bp2_p',
             '--bp1': 'bp1_p', '--bp0': 'bp0_p'}
    for fl, key in flags.items():
        if fl in argv:
            kw[key] = Path(argv[argv.index(fl) + 1])
    print(f'=== BP3 OWNERSHIP CHECK v{__version__} ===')
    errs, warns = run_checks(**kw)
    for w in warns:
        print(f'  [WARN] {w}')
    if errs:
        for e in errs:
            print(f'  [VIOLATION] {e}')
        print(f'=== FAIL — {len(errs)} vi pham ===')
        return 1
    m = load_yaml_no_dup(Path(kw.get('matrix_p', D_MATRIX)).read_text(encoding='utf-8'))
    d = load_yaml_no_dup(Path(kw.get('dep_p', D_DEP)).read_text(encoding='utf-8'))
    print(f'  facets: {len(m["facets"])} (coverage 2 chieu BP2) · deps: {len(d["dependencies"])}'
          ' (3 nguon khop) · 1-facet-1-writer OK')
    print('=== PASS — BP3 ownership hop le (0 vi pham) ===')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
