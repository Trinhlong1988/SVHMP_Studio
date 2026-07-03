"""BLUEPRINT CONSTITUTION CHECK v2.0.0 — gate may cho SYSTEM_BLUEPRINT_CONSTITUTION v2.0.

Amendment v2 (Mr.Long ky bang E 3/7 + 2 dieu kien kiem duyet). Cuong che:
  C1  meta du (name/version/promotion_status) + CAM Builder tu-lock.
  C1b VERSIONING (A4): schema_version/contract_version/validator_version bat buoc,
      dung semver; validator_version PHAI khop __version__ cua checker (may so).
  C2  Du 22 domain bat buoc (thieu 1 = FAIL); domain them (vd quest RESERVED)
      van phai du contract.
  C3  Moi domain du 12 field + lifecycle enum moi (draft|candidate|approved|
      deprecated|archived) + lock_type (bible|tool|none).
  C4  Layer + huong: dep phai layer THAP HON strictly; 2 domain cung L1 dep nhau
      = L1-CROSS-DEP (Cond 1: canon chi tham chieu qua reader); dep vao domain
      lifecycle=archived = FAIL; deprecated = WARN (di cu dan).
  C5  Supernatural DOC LAP (khong sub_of/contains/dep host).
  C6  Memory: du 6 scope, owner la domain da khai.
  C7  Status ref: exists|planned|deprecated|archived.
      exists  -> path phai tren disk (khai lao = FAIL phantom).
      planned -> PLANNED HONESTY 5 metadata; planned_path DA tren disk =
                 VIOLATION (Cond 2 chong stub — nang tu WARN len FAIL).
      deprecated/archived -> phai co path (tung ton tai).
  C8  layer_groups: moi domain thuoc DUNG 1 nhom; thanh vien nhom la domain that.
  C9  FORMAT (A7): facets (1 facet = 1 writer) / events (hop sau thuoc reader
      hop truoc) / state_machines (transition trong states) — validate khi xuat hien.

Exit 0 = PASS, exit 1 = FAIL. Khong tu phong PASS ngoai exit-code.
Usage: python tools/blueprint_constitution_check.py [--file <yaml>] [--registry <yaml>]
"""
import re
import sys
from pathlib import Path

import yaml

__version__ = '2.0.0'

REPO = Path(__file__).resolve().parent.parent
DEFAULT_FILE = REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml'
DEFAULT_REGISTRY = REPO / 'governance' / 'architecture_registry.yaml'

REQUIRED_DOMAINS = [
    'world', 'timeline', 'location', 'weather', 'culture', 'belief', 'ritual',
    'supernatural', 'character', 'object', 'dialogue', 'event', 'story_planner',
    'decision_engine', 'generator', 'qa_runtime', 'tts', 'audio', 'production',
    'video', 'publisher', 'analytics',
]
REQUIRED_FIELDS = [
    'responsibility', 'non_responsibility', 'source_of_truth', 'manager',
    'schema', 'validator', 'reader', 'writer', 'lifecycle', 'dependencies',
    'forbidden_dependencies', 'audit_rule',
]
NONEMPTY_FIELDS = [f for f in REQUIRED_FIELDS
                   if f not in ('reader', 'dependencies', 'forbidden_dependencies')]
REQUIRED_MEMORY = ['global_memory', 'series_memory', 'episode_memory',
                   'character_memory', 'event_memory', 'supernatural_memory']
LIFECYCLES = ['draft', 'candidate', 'approved', 'deprecated', 'archived']
LOCK_TYPES = ['bible', 'tool', 'none']
REF_STATUSES = ['exists', 'planned', 'deprecated', 'archived']
EXTRA_WRITERS = ['mr_long']
SUPERNATURAL_HOSTS = ['world', 'event', 'story_planner']
SEMVER = re.compile(r'^\d+\.\d+\.\d+$')

# PLANNED HONESTY RULE: planned PHAI du 5 metadata, thieu 1 = FAIL.
PLANNED_META = ['planned_path', 'owner', 'reason_not_exists_yet',
                'target_milestone', 'blocking_dependency']


def _pathref_errors(label, ref, root, warns=None, milestones=None, domains=None):
    """exists: path tren disk. planned: 5 metadata + planned_path CHUA tren disk
    (Cond 2: da xuat hien = VIOLATION chong stub). deprecated/archived: co path."""
    errs = []
    if not isinstance(ref, dict) or not ref.get('status'):
        return [f'{label}: phai la mapping co status — nhan duoc {ref!r}']
    st = ref['status']
    if st not in REF_STATUSES:
        errs.append(f"{label}: status '{st}' khong thuoc {REF_STATUSES}")
    elif st == 'exists':
        if not ref.get('path'):
            errs.append(f'{label}: exists phai co path')
        elif not (root / ref['path']).exists():
            errs.append(f"{label}: khai exists nhung KHONG co tren disk (khai lao/phantom): {ref['path']}")
    elif st == 'planned':
        for k in PLANNED_META:
            if not ref.get(k):
                errs.append(f'{label}: PLANNED HONESTY — thieu metadata {k}')
        tm = ref.get('target_milestone')
        if tm and milestones is not None and tm not in milestones:
            errs.append(f'{label}: target_milestone {tm!r} khong co trong milestones map')
        ow = ref.get('owner')
        if ow and domains is not None and ow not in domains and ow not in EXTRA_WRITERS:
            errs.append(f'{label}: owner {ow!r} khong phai domain da khai')
        pp = ref.get('planned_path')
        if pp and (root / pp).exists():
            errs.append(f'{label}: khai planned nhung path DA co tren disk — DRIFT/STUB '
                        f'(Cond 2 kiem duyet: VIOLATION, cap nhat contract sang exists co duyet): {pp}')
    else:  # deprecated | archived
        if not ref.get('path'):
            errs.append(f'{label}: {st} phai co path (tung ton tai de truy vet)')
    return errs


def check(data, root=REPO, registry_path=DEFAULT_REGISTRY, warns=None):
    errs = []
    if warns is None:
        warns = []
    if not isinstance(data, dict):
        return ['blueprint yaml khong phai mapping']
    meta = data.get('meta') or {}
    domains = data.get('domains') or {}
    layers = data.get('layers') or {}
    memory = data.get('memory') or {}
    milestones = data.get('milestones') or {}
    groups = data.get('layer_groups') or {}

    # C1 meta + chong tu-lock
    for k in ('name', 'version', 'promotion_status'):
        if not meta.get(k):
            errs.append(f'meta.{k} thieu/rong')
    status = meta.get('promotion_status')
    if status == 'locked':
        reg_status = None
        try:
            reg = yaml.safe_load(Path(registry_path).read_text(encoding='utf-8'))
            reg_status = (reg.get('domains', {}).get('governance', {})
                          .get('enterprise_pack_progress', {}).get('blueprint_constitution'))
        except Exception as e:
            errs.append(f'khong doc duoc registry de xac thuc lock: {e}')
        if isinstance(reg_status, str):
            reg_status = reg_status.split()[0] if reg_status else reg_status
        if reg_status != 'locked':
            errs.append('SELF-LOCK: yaml khai locked nhung registry blueprint_constitution '
                        f'= {reg_status!r} (lock la chu ky Mr.Long trong registry, Builder CAM tu lock)')
    elif status not in ('candidate', 'draft', None):
        errs.append(f"meta.promotion_status '{status}' khong thuoc candidate|draft|locked")

    # C1b versioning (A4)
    for k in ('schema_version', 'contract_version', 'validator_version'):
        v = meta.get(k)
        if not v:
            errs.append(f'VERSIONING: meta.{k} thieu (A4 bat buoc)')
        elif not SEMVER.match(str(v)):
            errs.append(f'VERSIONING: meta.{k}={v!r} khong phai semver X.Y.Z')
    vv = str(meta.get('validator_version') or '')
    if vv and SEMVER.match(vv) and vv != __version__:
        errs.append(f'VERSIONING: validator_version {vv} != checker __version__ {__version__} '
                    '(contract va checker lech doi — dong bo truoc khi audit)')

    # C2 du 22 domain bat buoc
    for d in REQUIRED_DOMAINS:
        if d not in domains:
            errs.append(f'THIEU domain bat buoc: {d}')

    # C5 supernatural doc lap
    if 'supernatural' in domains:
        sn = domains['supernatural'] or {}
        if sn.get('sub_of'):
            errs.append(f"supernatural bi khai sub_of={sn['sub_of']!r} — phai DOC LAP")
        if set(sn.get('dependencies') or []) & set(SUPERNATURAL_HOSTS):
            errs.append('supernatural depend vao world/event/story_planner — pha doc lap')
    for name, d in domains.items():
        if name != 'supernatural' and 'supernatural' in (d or {}).get('contains', []):
            errs.append(f"domain '{name}' contains supernatural — CAM gop/an domain sieu nhien")

    # C3/C4/C7 tung domain
    for name, d in domains.items():
        d = d or {}
        for f in REQUIRED_FIELDS:
            if f not in d:
                errs.append(f'{name}: THIEU field {f}')
            elif f in NONEMPTY_FIELDS and not d[f]:
                errs.append(f'{name}: field {f} RONG')
        if name not in layers:
            errs.append(f'{name}: thieu layer trong layers map')
        lc = d.get('lifecycle')
        if lc and lc not in LIFECYCLES:
            errs.append(f"{name}: lifecycle '{lc}' khong thuoc {LIFECYCLES}")
        lt = d.get('lock_type')
        if lt is not None and lt not in LOCK_TYPES:
            errs.append(f"{name}: lock_type '{lt}' khong thuoc {LOCK_TYPES}")
        # deps: ton tai + huong + forbidden + vong doi target
        my_layer = layers.get(name)
        forb = d.get('forbidden_dependencies') or []
        for dep in (d.get('dependencies') or []):
            if dep not in domains:
                errs.append(f'{name}: dep {dep!r} khong phai domain da khai')
                continue
            if dep in forb:
                errs.append(f'{name}: dep {dep!r} nam trong forbidden_dependencies cua chinh no')
            dep_layer = layers.get(dep)
            if isinstance(my_layer, int) and isinstance(dep_layer, int):
                if my_layer == 1 and dep_layer == 1:
                    errs.append(f'{name}: L1-CROSS-DEP {dep!r} — canon L1 dong-tang CAM '
                                'dependencies, tham chieu CHI qua reader (Cond 1 kiem duyet)')
                elif dep_layer >= my_layer:
                    errs.append(f'{name}(L{my_layer}) depend {dep}(L{dep_layer}) — SAI HUONG '
                                '(chi duoc depend layer thap hon strictly)')
            dep_lc = (domains.get(dep) or {}).get('lifecycle')
            if dep_lc == 'archived':
                errs.append(f'{name}: dep {dep!r} co lifecycle=archived — CAM tham chieu domain archived')
            elif dep_lc == 'deprecated':
                warns.append(f'{name}: dep {dep!r} dang deprecated — len ke hoach di cu')
        # reader/writer hop le (+ cam tro archived)
        for role in ('reader', 'writer'):
            for who in (d.get(role) or []):
                if who not in domains and who not in EXTRA_WRITERS:
                    errs.append(f"{name}: {role} {who!r} khong phai domain/mr_long")
                elif who in domains and (domains[who] or {}).get('lifecycle') == 'archived':
                    errs.append(f'{name}: {role} {who!r} co lifecycle=archived — CAM tham chieu')
        # C7 path/status check
        for i, ref in enumerate(d.get('source_of_truth') or []):
            errs += _pathref_errors(f'{name}.source_of_truth[{i}]', ref, root,
                                    warns, milestones, domains)
        for f in ('manager', 'schema', 'validator'):
            if isinstance(d.get(f), dict):
                errs += _pathref_errors(f'{name}.{f}', d[f], root, warns, milestones, domains)
        # C9 facets format (neu domain khai facets)
        for fname, facet in ((d.get('facets') or {}) if isinstance(d.get('facets'), dict) else {}).items():
            facet = facet or {}
            w = facet.get('writer')
            if isinstance(w, list):
                errs.append(f'{name}.facets.{fname}: {len(w)} writer — FORMAT facet: '
                            '1 facet = DUNG 1 writer (chong nhieu manager cung sua)')
            elif not w:
                errs.append(f'{name}.facets.{fname}: thieu writer')
            elif w not in domains and w not in EXTRA_WRITERS:
                errs.append(f'{name}.facets.{fname}: writer {w!r} khong phai domain')
            for r in (facet.get('readers') or []):
                if r not in domains and r not in EXTRA_WRITERS:
                    errs.append(f'{name}.facets.{fname}: reader {r!r} khong phai domain')

    # C8 layer_groups: moi domain DUNG 1 nhom
    if groups:
        seen = {}
        for g, members in groups.items():
            for m in (members or []):
                if m not in domains:
                    errs.append(f'layer_groups.{g}: {m!r} khong phai domain da khai')
                seen[m] = seen.get(m, 0) + 1
        for name in domains:
            n = seen.get(name, 0)
            if n == 0:
                errs.append(f'layer_groups: domain {name!r} khong thuoc nhom nao')
            elif n > 1:
                errs.append(f'layer_groups: domain {name!r} thuoc {n} nhom (phai dung 1)')
    else:
        errs.append('layer_groups thieu (A6 bat buoc: narrative/runtime/presentation/business)')

    # C9 events format (top-level, forward-compat)
    for i, ev in enumerate(data.get('events') or []):
        ev = ev or {}
        for k in ('name', 'emitter', 'chain'):
            if not ev.get(k):
                errs.append(f'events[{i}]: thieu {k} (FORMAT event)')
        chain = [ev.get('emitter')] + list(ev.get('chain') or [])
        for a, b in zip(chain, chain[1:]):
            if a in domains and b in domains:
                if b not in ((domains[a] or {}).get('reader') or []):
                    errs.append(f"events[{i}] '{ev.get('name')}': hop {b!r} KHONG nam trong "
                                f"reader cua {a!r} — chain pham quyen doc")
            elif b not in (domains or {}):
                errs.append(f"events[{i}]: hop {b!r} khong phai domain")

    # C9 state_machines format
    for i, sm in enumerate(data.get('state_machines') or []):
        sm = sm or {}
        for k in ('entity', 'states', 'transitions'):
            if not sm.get(k):
                errs.append(f'state_machines[{i}]: thieu {k} (FORMAT state_machine)')
        states = set(sm.get('states') or [])
        for t in (sm.get('transitions') or []):
            if not (isinstance(t, list) and len(t) == 2 and set(t) <= states):
                errs.append(f"state_machines[{i}] '{sm.get('entity')}': transition {t!r} "
                            'ngoai states da khai')

    # C6 memory
    for m in REQUIRED_MEMORY:
        if m not in memory:
            errs.append(f'THIEU memory scope: {m}')
            continue
        entry = memory[m] or {}
        if not entry.get('owner'):
            errs.append(f'{m}: KHONG co owner — memory phai co chu')
        elif entry['owner'] not in domains:
            errs.append(f"{m}: owner {entry['owner']!r} khong phai domain da khai")
        if not entry.get('scope'):
            errs.append(f'{m}: thieu scope')
        if not entry.get('store'):
            errs.append(f'{m}: thieu store')
        elif isinstance(entry.get('store'), dict):
            errs += _pathref_errors(f'{m}.store', entry['store'], root,
                                    warns, milestones, domains)
    return errs


def main(argv):
    file = DEFAULT_FILE
    registry = DEFAULT_REGISTRY
    if '--file' in argv:
        file = Path(argv[argv.index('--file') + 1])
    if '--registry' in argv:
        registry = Path(argv[argv.index('--registry') + 1])
    print(f'=== BLUEPRINT CONSTITUTION CHECK v{__version__} ===')
    print(f'file: {file}')
    try:
        data = yaml.safe_load(Path(file).read_text(encoding='utf-8'))
    except Exception as e:
        print(f'FAIL: khong doc duoc yaml: {e}')
        return 1
    warns = []
    errs = check(data, registry_path=registry, warns=warns)
    n_dom = len((data or {}).get('domains') or {})
    for w in warns:
        print(f'  [WARN] {w}')
    if errs:
        for e in errs:
            print(f'  [VIOLATION] {e}')
        print(f'=== FAIL — {len(errs)} vi pham / {n_dom} domain ===')
        return 1
    planned = sum(1 for d in data['domains'].values()
                  for f in ('manager', 'schema', 'validator')
                  if isinstance(d.get(f), dict) and d[f].get('status') == 'planned')
    print(f'  domains: {n_dom} ({len(REQUIRED_DOMAINS)} bat buoc + RESERVED) · memory: 6/6'
          f' · planned(ROADMAP) refs: {planned} · warn: {len(warns)}')
    print('=== PASS — blueprint constitution v2 hop le (0 vi pham) ===')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
