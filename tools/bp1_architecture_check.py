"""BP1 ARCHITECTURE CHECK v1.0.0 — gate may cho BP1 Core Architecture (TASK_BP1_CORE ban va).

Nguon luat: Blueprint Constitution v2.0 LOCKED (blueprint_domains.yaml).
Layer model = SO 1-12 + layer_groups 4 nhan DA LOCK — scheme la (L0..L4...) = FAIL.

Check (11 theo TASK + equality chong sua-tay-lech):
  1  Moi domain BP0 co trong dependency_graph (22+1); dung 1 lan.
  2  Khong domain LA ngoai inventory (graph/layers/groups/iface).
  3  DUP-KEY loader moi file BP1 (tai dung C10 BP0).
  4  L1 canon: depends_on RONG (L1-CROSS-DEP mirror BP0 Cond 1).
  5  Khong tham chieu domain archived/deprecated (graph + iface).
  6  Interface du owner/source/version/lifecycle/status; exists -> source_artifact
     phai ton tai (khai lao = FAIL); planned -> du 5 metadata PLANNED HONESTY
     (milestone phai co trong BP0 milestones).
  8  CIRCULAR dependency = FAIL (belt-and-braces tren luat layer-thap-hon).
  9  LECH-BP0: depends_on == BP0.dependencies tung domain; reads_from == dan xuat
     reader grants; lifecycle khop; LAYER-SCHEME: layers + layer_groups ==
     BP0 nguyen ven; layer so khop tung domain.
 10  VERSION: validator_version == __version__; source_constitution_version ==
     BP0 meta.contract_version (moi file BP1).
 11  REPORT-CLAIM: moi path `...` trong bang cua report phai ton tai (Test-Path).
  +  IFACE-THIEU/THUA: contracts phu DUNG tap reader-edge BP0 (2 chieu);
     layer_contracts: 4 nhan dung, dep-edge thoa rang buoc nhom.

Exit 0 = PASS, exit 1 = FAIL. Khong tu phong PASS ngoai exit-code.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402

__version__ = '1.0.0'

BP1 = REPO / 'governance' / 'blueprint' / 'bp1'
D_GRAPH = BP1 / 'dependency_graph.yaml'
D_IFACE = BP1 / 'interface_contracts.yaml'
D_LAYER = BP1 / 'layer_contracts.yaml'
D_BP0 = REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml'
D_REPORT = REPO / 'reports' / 'BP1_CORE_ARCHITECTURE_REPORT.md'

SEMVER = re.compile(r'^\d+\.\d+\.\d+$')
GROUPS = ['narrative', 'runtime', 'presentation', 'business']
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


def run_checks(graph_p=D_GRAPH, iface_p=D_IFACE, layer_p=D_LAYER,
               bp0_p=D_BP0, report_p=D_REPORT, root=REPO):
    errs, warns = [], []
    bp0 = _load(bp0_p, errs, 'BP0')
    graph = _load(graph_p, errs, 'dependency_graph')
    iface = _load(iface_p, errs, 'interface_contracts')
    layersc = _load(layer_p, errs, 'layer_contracts')
    if not all([bp0, graph, iface, layersc]):
        return errs, warns

    inv = bp0.get('domains') or {}
    src_ver = str((bp0.get('meta') or {}).get('contract_version'))
    milestones = bp0.get('milestones') or {}

    # 10 VERSION moi file BP1
    for label, doc in (('dependency_graph', graph), ('interface_contracts', iface),
                       ('layer_contracts', layersc)):
        if str(doc.get('validator_version')) != __version__:
            errs.append(f"{label}: VERSION validator_version {doc.get('validator_version')} "
                        f'!= checker {__version__}')
        if str(doc.get('source_constitution_version')) != src_ver:
            errs.append(f"{label}: VERSION source_constitution_version "
                        f"{doc.get('source_constitution_version')} != BP0 contract {src_ver}")

    # 9 LAYER-SCHEME: layers + layer_groups phai COPY nguyen ven BP0
    if (graph.get('layers') or {}) != (bp0.get('layers') or {}):
        errs.append('LAYER-SCHEME: graph.layers != BP0.layers (layer model SO 1-12 da LOCK — '
                    'scheme la/drift = RFC BP0, khong duoc tu che)')
    g_groups = {k: sorted(v or []) for k, v in (graph.get('layer_groups') or {}).items()}
    b_groups = {k: sorted(v or []) for k, v in (bp0.get('layer_groups') or {}).items()}
    if g_groups != b_groups:
        errs.append('LAYER-SCHEME: graph.layer_groups != BP0.layer_groups (4 nhan da LOCK)')

    gdoms = {d.get('domain_id'): d for d in (graph.get('domains') or [])}

    # 1 + 2
    for n in inv:
        if n not in gdoms:
            errs.append(f'THIEU domain trong graph: {n}')
    for n in gdoms:
        if n not in inv:
            errs.append(f'DOMAIN-LA trong graph (ngoai inventory — can RFC): {n}')
    ids = [d.get('domain_id') for d in (graph.get('domains') or [])]
    for n in set(ids):
        if ids.count(n) > 1:
            errs.append(f'{n}: xuat hien {ids.count(n)} lan trong graph.domains')

    # dan xuat reader edges + reads_from ky vong
    reader_edges = set()
    reads_expect = {n: set() for n in inv}
    for prov, d in inv.items():
        for cons in (d.get('reader') or []):
            reader_edges.add((prov, cons))
            if cons in reads_expect:
                reads_expect[cons].add(prov)

    group_of = {}
    for g, members in (bp0.get('layer_groups') or {}).items():
        for m in (members or []):
            group_of[m] = g
    layer_rules = {lc.get('layer_id'): lc for lc in (layersc.get('layers') or [])}

    for n, gd in gdoms.items():
        if n not in inv:
            continue
        deps = gd.get('depends_on') or []
        my_ly = gd.get('layer')
        # 9 equality voi BP0
        if my_ly != (bp0.get('layers') or {}).get(n):
            errs.append(f'{n}: LECH-BP0 layer so {my_ly} != BP0 {(bp0.get("layers") or {}).get(n)}')
        if sorted(deps) != sorted(inv[n].get('dependencies') or []):
            errs.append(f'{n}: LECH-BP0 depends_on {deps} != BP0 {inv[n].get("dependencies")} (drift = FAIL)')
        if sorted(gd.get('reads_from') or []) != sorted(reads_expect.get(n, set())):
            errs.append(f'{n}: LECH-BP0 reads_from khong khop reader grants BP0')
        if gd.get('lifecycle') != inv[n].get('lifecycle'):
            errs.append(f'{n}: LECH-BP0 lifecycle')
        if not gd.get('owner_artifact'):
            errs.append(f'{n}: thieu owner_artifact')
        # 4 L1 canon
        if my_ly == 1 and deps:
            errs.append(f'{n}: L1-CROSS-DEP — canon L1 phai depends_on RONG (chi reader grant)')
        for dep in deps:
            if dep not in inv:
                errs.append(f'{n}: dep DOMAIN-LA {dep!r}')
                continue
            # 5 archived/deprecated
            lc = inv[dep].get('lifecycle')
            if lc in ('archived', 'deprecated'):
                errs.append(f'{n}: tham chieu domain {dep!r} lifecycle={lc} — CAM')
            # rang buoc nhom (layer_contracts)
            ga, gb = group_of.get(n), group_of.get(dep)
            rule = layer_rules.get(ga) or {}
            if gb and gb in (rule.get('forbidden_dependencies') or []):
                errs.append(f'{n}({ga}) dep {dep}({gb}) — nhom {gb} nam trong forbidden cua {ga}')

    # 8 CIRCULAR
    color = {}
    def dfs(u, stack):
        color[u] = 1
        for v in (gdoms.get(u, {}).get('depends_on') or []):
            if v not in gdoms:
                continue
            if color.get(v) == 1:
                errs.append(f'CIRCULAR dependency: {" -> ".join(stack + [v])}')
                return
            if color.get(v, 0) == 0:
                dfs(v, stack + [v])
        color[u] = 2
    for n in gdoms:
        if color.get(n, 0) == 0:
            dfs(n, [n])

    # 6 interface + honesty + completeness + 5
    seen_read = set()
    for i, c in enumerate(iface.get('contracts') or []):
        cid = c.get('contract_id') or f'#{i}'
        for k in ('contract_id', 'provider_domain', 'consumer_domain', 'interface_type',
                  'version', 'lifecycle', 'owner_artifact', 'source_artifact', 'status'):
            if not c.get(k):
                errs.append(f'iface {cid}: thieu {k}')
        if c.get('version') and not SEMVER.match(str(c['version'])):
            errs.append(f'iface {cid}: version khong semver')
        p, q = c.get('provider_domain'), c.get('consumer_domain')
        for who in (p, q):
            if who and who not in inv:
                errs.append(f'iface {cid}: DOMAIN-LA {who!r}')
            elif who and inv[who].get('lifecycle') in ('archived', 'deprecated'):
                errs.append(f'iface {cid}: tro domain {who!r} lifecycle=archived/deprecated — CAM')
        st = c.get('status')
        if st == 'exists':
            sa = c.get('source_artifact')
            if sa and not (Path(root) / sa).exists():
                errs.append(f'iface {cid}: khai exists nhung source_artifact KHONG ton tai '
                            f'(khai lao/phantom): {sa}')
        elif st == 'planned':
            for k in PLANNED_META:
                if not c.get(k):
                    errs.append(f'iface {cid}: PLANNED HONESTY — thieu metadata {k}')
            tm = c.get('target_milestone')
            if tm and tm not in milestones:
                errs.append(f'iface {cid}: target_milestone {tm!r} khong co trong milestones BP0')
        elif st:
            errs.append(f"iface {cid}: status '{st}' khong thuoc exists|planned")
        if str(c.get('interface_type')) == 'data_read' and p in inv and q in inv:
            if (p, q) not in reader_edges:
                errs.append(f'iface {cid}: IFACE-THUA — edge ({p}->{q}) khong co trong reader BP0')
            seen_read.add((p, q))
    for edge in sorted(reader_edges - seen_read):
        errs.append(f'IFACE-THIEU: reader edge {edge[0]}->{edge[1]} chua co contract')

    # layer_contracts sanity
    if sorted(layer_rules.keys()) != sorted(GROUPS):
        errs.append(f'layer_contracts: layer_id phai la DUNG 4 nhan {GROUPS} — '
                    f'nhan duoc {sorted(layer_rules.keys())} (scheme la = RFC BP0)')
    for lid, lc in layer_rules.items():
        for k in ('purpose', 'allowed_outputs', 'forbidden_outputs'):
            if not lc.get(k):
                errs.append(f'layer {lid}: thieu {k}')
        for a in (lc.get('allowed_dependencies') or []) + (lc.get('forbidden_dependencies') or []):
            if a not in GROUPS:
                errs.append(f'layer {lid}: nhom la {a!r}')

    # 11 REPORT-CLAIM
    if not Path(report_p).exists():
        errs.append(f'REPORT-CLAIM: report khong ton tai: {report_p}')
    else:
        rtext = Path(report_p).read_text(encoding='utf-8')
        for mline in re.finditer(r'`([\w][\w/.\-]+\.(?:md|yaml|py))`', rtext):
            rel = mline.group(1)
            if not (Path(root) / rel).exists():
                errs.append(f'REPORT-CLAIM: report khai file khong ton tai: {rel}')
    return errs, warns


def main(argv):
    kw = {}
    flags = {'--graph': 'graph_p', '--iface': 'iface_p', '--layers': 'layer_p',
             '--bp0': 'bp0_p', '--report': 'report_p', '--root': 'root'}
    for fl, key in flags.items():
        if fl in argv:
            kw[key] = Path(argv[argv.index(fl) + 1])
    print(f'=== BP1 ARCHITECTURE CHECK v{__version__} ===')
    errs, warns = run_checks(**kw)
    for w in warns:
        print(f'  [WARN] {w}')
    if errs:
        for e in errs:
            print(f'  [VIOLATION] {e}')
        print(f'=== FAIL — {len(errs)} vi pham ===')
        return 1
    print('=== PASS — BP1 core architecture hop le (0 vi pham; equality BP0 + honesty interface) ===')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
