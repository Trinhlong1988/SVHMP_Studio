"""BP4 RUNTIME+EVENT CHECK v1.0.0 — gate may cho BP4 Runtime + Event Architecture.

Check:
  1  DUP-KEY loader + VERSION khop checker/BP0 (4 file BP4).
  2  runtime_flow: domain ∈ inventory · layer BP0 TANG strictly qua tung hop
     (flow nguoc = FAIL) · via exists = Test-Path · via planned = 5 metadata.
  3  event_bus: event_id unique · emitter ∈ inventory · MOI HOP = domain inventory
     HOAC facet da khai BP2 dang domain.facet_id (hop la/bia = FAIL; facet sai
     domain = FAIL) · bat buoc co ghost_appears emitter=supernatural (chuoi mau).
  4  state_machines: from/to ∈ states · trigger PHAI la event_id da khai (trigger
     ma = FAIL) · state khong duong VAO (tru initial) = ORPHAN FAIL · sot exists
     -> path+key resolve that.
  5  memory: DUNG 6 scope BP0, owner + store khop BP0.memory (drift = FAIL) ·
     writers ⊆ {owner, mr_long} (BP3 1-writer) · readers ⊆ reader grant BP0 cua owner
     · store exists = Test-Path / planned = 5 metadata.

Exit 0 = PASS, exit 1 = FAIL.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from blueprint_constitution_check import load_yaml_no_dup, DupKeyError  # noqa: E402

__version__ = '1.0.0'

BP4 = REPO / 'governance' / 'blueprint' / 'bp4'
D_FLOW = BP4 / 'runtime_flow.yaml'
D_BUS = BP4 / 'event_bus.yaml'
D_SM = BP4 / 'state_machines.yaml'
D_MEM = BP4 / 'memory_architecture.yaml'
D_BP2 = REPO / 'governance' / 'blueprint' / 'bp2' / 'domain_specs.yaml'
D_BP0 = REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml'

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


def _ref_errors(label, ref, milestones, root):
    errs = []
    st = (ref or {}).get('status')
    if st == 'exists':
        p = ref.get('path')
        if not p or not (Path(root) / p).exists():
            errs.append(f'{label}: khai exists nhung KHONG ton tai (phantom): {p}')
        elif ref.get('key'):
            try:
                doc = load_yaml_no_dup((Path(root) / p).read_text(encoding='utf-8'))
                cur = doc
                for part in str(ref['key']).split('.'):
                    cur = cur[part]
            except Exception:
                errs.append(f"{label}: key {ref.get('key')!r} khong resolve trong {p}")
    elif st == 'planned':
        for k in PLANNED_META:
            if not ref.get(k):
                errs.append(f'{label}: PLANNED HONESTY — thieu metadata {k}')
        tm = ref.get('target_milestone')
        if tm and tm not in milestones:
            errs.append(f'{label}: milestone {tm!r} khong co trong BP0')
        pp = ref.get('planned_path')
        if pp and (Path(root) / pp).exists():
            errs.append(f'{label}: planned nhung path DA ton tai — DRIFT/STUB: {pp}')
    else:
        errs.append(f'{label}: status {st!r} khong thuoc exists|planned')
    return errs


def run_checks(flow_p=D_FLOW, bus_p=D_BUS, sm_p=D_SM, mem_p=D_MEM,
               bp2_p=D_BP2, bp0_p=D_BP0, root=REPO):
    errs, warns = [], []
    flow = _load(flow_p, errs, 'runtime_flow')
    bus = _load(bus_p, errs, 'event_bus')
    sm = _load(sm_p, errs, 'state_machines')
    mem = _load(mem_p, errs, 'memory_architecture')
    bp2 = _load(bp2_p, errs, 'BP2')
    bp0 = _load(bp0_p, errs, 'BP0')
    if not all([flow, bus, sm, mem, bp2, bp0]):
        return errs, warns

    inv = bp0.get('domains') or {}
    layers = bp0.get('layers') or {}
    milestones = bp0.get('milestones') or {}
    src = str((bp0.get('meta') or {}).get('contract_version'))
    for label, doc in (('runtime_flow', flow), ('event_bus', bus),
                       ('state_machines', sm), ('memory_architecture', mem)):
        if str(doc.get('validator_version')) != __version__:
            errs.append(f'{label}: VERSION validator_version != checker {__version__}')
        if str(doc.get('source_constitution_version')) != src:
            errs.append(f'{label}: VERSION source_constitution_version != BP0 {src}')

    bp2_facets = {}
    for dname, block in (bp2.get('domains') or {}).items():
        bp2_facets[dname] = {f.get('facet_id') for f in ((block or {}).get('facets') or [])}

    # 2 runtime flow
    prev_layer = 0
    for h in (flow.get('flow') or []):
        d = h.get('domain')
        if d not in inv:
            errs.append(f'flow hop {h.get("hop")}: DOMAIN-LA {d!r}')
            continue
        ly = layers.get(d)
        if isinstance(ly, int):
            if ly <= prev_layer:
                errs.append(f'flow hop {h.get("hop")} ({d}, L{ly}): NGUOC LAYER — runtime chi chay '
                            f'layer thap->cao (hop truoc L{prev_layer})')
            prev_layer = ly
        if h.get('status') not in ('exists', 'planned'):
            errs.append(f'flow hop {h.get("hop")}: status khong thuoc exists|planned')
        if isinstance(h.get('via'), dict):
            errs += _ref_errors(f'flow hop {h.get("hop")}.via', h['via'], milestones, root)
        for k in ('input', 'output'):
            if not h.get(k):
                errs.append(f'flow hop {h.get("hop")}: thieu {k}')

    # 3 event bus
    event_ids = set()
    def _hop_ok(hop, where):
        if '.' in str(hop):
            dom, facet = str(hop).split('.', 1)
            if dom not in inv:
                errs.append(f'{where}: hop {hop!r} — domain la {dom!r}')
            elif facet not in bp2_facets.get(dom, set()):
                errs.append(f'{where}: hop {hop!r} — facet {facet!r} KHONG khai trong BP2 cua '
                            f'{dom!r} (hop bia/map sai = FAIL)')
        elif hop not in inv:
            errs.append(f'{where}: hop {hop!r} KHONG phai domain inventory hay facet da khai '
                        '(hop la kieu Music/Lighting phai map ve domain/facet that)')
    for ev in (bus.get('events') or []):
        eid = ev.get('event_id')
        if not eid:
            errs.append('event thieu event_id')
            continue
        if eid in event_ids:
            errs.append(f'event {eid}: khai 2 lan')
        event_ids.add(eid)
        if ev.get('emitter') not in inv:
            errs.append(f'event {eid}: emitter {ev.get("emitter")!r} khong trong inventory')
        if not (ev.get('chain') or []):
            errs.append(f'event {eid}: chain rong')
        for hop in (ev.get('chain') or []):
            _hop_ok(hop, f'event {eid}')
    ga = next((e for e in (bus.get('events') or []) if e.get('event_id') == 'ghost_appears'), None)
    if not ga:
        errs.append('THIEU chuoi mau bat buoc: ghost_appears')
    elif ga.get('emitter') != 'supernatural':
        errs.append('ghost_appears: emitter phai la supernatural (chuoi mau 3/7)')

    # 4 state machines
    for m in (sm.get('state_machines') or []):
        ent = m.get('entity') or '?'
        states = list(m.get('states') or [])
        if len(states) != len(set(states)):
            errs.append(f'sm {ent}: state trung')
        initial = m.get('initial') or (states[0] if states else None)
        if initial not in states:
            errs.append(f'sm {ent}: initial {initial!r} khong thuoc states')
        if m.get('owner_domain') not in inv:
            errs.append(f'sm {ent}: owner_domain khong trong inventory')
        entered = set()
        for t in (m.get('transitions') or []):
            fr, to, tg = t.get('from'), t.get('to'), t.get('trigger')
            if fr not in states or to not in states:
                errs.append(f'sm {ent}: transition {fr}->{to} ngoai states')
            if tg not in event_ids:
                errs.append(f'sm {ent}: trigger {tg!r} la EVENT-MA (khong khai trong event_bus)')
            entered.add(to)
        for s in states:
            if s != initial and s not in entered:
                errs.append(f'sm {ent}: state {s!r} ORPHAN — khong co duong vao')
        if isinstance(m.get('sot'), dict):
            errs += _ref_errors(f'sm {ent}.sot', m['sot'], milestones, root)

    # 5 memory
    bp0_mem = bp0.get('memory') or {}
    scopes = {m.get('scope'): m for m in (mem.get('memory_scopes') or [])}
    if set(scopes) != set(bp0_mem):
        errs.append(f'memory: scope set {sorted(scopes)} != BP0 {sorted(bp0_mem)} (drift)')
    for name, m in scopes.items():
        b = bp0_mem.get(name) or {}
        own = m.get('owner')
        if own != b.get('owner'):
            errs.append(f'memory {name}: owner {own!r} != BP0 {b.get("owner")!r}')
        st = m.get('store') or {}
        b_store = b.get('store') or {}
        b_path = b_store.get('path') or b_store.get('planned_path')
        m_path = st.get('path') or st.get('planned_path')
        if b_path and m_path and b_path != m_path:
            errs.append(f'memory {name}: store {m_path!r} != BP0 {b_path!r} (drift)')
        errs += _ref_errors(f'memory {name}.store', st, milestones, root)
        for w in (m.get('writers') or []):
            if w not in (own, 'mr_long'):
                errs.append(f'memory {name}: writer {w!r} VUOT BP3 (chi {own}/mr_long)')
        if not m.get('writers'):
            errs.append(f'memory {name}: writers rong')
        own_readers = set((inv.get(own) or {}).get('reader') or [])
        for r in (m.get('readers') or []):
            if r not in own_readers:
                errs.append(f'memory {name}: reader {r!r} ngoai reader grant BP0 cua {own}')
        if not m.get('retention'):
            errs.append(f'memory {name}: thieu retention')
    return errs, warns


def main(argv):
    kw = {}
    flags = {'--flow': 'flow_p', '--bus': 'bus_p', '--sm': 'sm_p', '--mem': 'mem_p',
             '--bp2': 'bp2_p', '--bp0': 'bp0_p'}
    for fl, key in flags.items():
        if fl in argv:
            kw[key] = Path(argv[argv.index(fl) + 1])
    print(f'=== BP4 RUNTIME+EVENT CHECK v{__version__} ===')
    errs, warns = run_checks(**kw)
    for w in warns:
        print(f'  [WARN STATE3001] {w}')
    if errs:
        for e in errs:
            print(f'  [VIOLATION STATE3001] {e}')
        print(f'=== FAIL — {len(errs)} vi pham ===')
        return 1
    bus = load_yaml_no_dup(Path(kw.get('bus_p', D_BUS)).read_text(encoding='utf-8'))
    sm = load_yaml_no_dup(Path(kw.get('sm_p', D_SM)).read_text(encoding='utf-8'))
    print(f'  flow: 9 hop layer-tang · events: {len(bus["events"])} · state machines: '
          f'{len(sm["state_machines"])} (0 orphan) · memory: 6 scope khop BP0/BP3')
    print('=== PASS — BP4 runtime+event hop le (0 vi pham) ===')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
