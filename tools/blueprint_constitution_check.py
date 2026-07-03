"""BLUEPRINT CONSTITUTION CHECK — gate may cho SYSTEM_BLUEPRINT_CONSTITUTION v1.0.

Doc governance/blueprint/blueprint_domains.yaml va cuong che:
  C1  meta du (name/version/promotion_status) + CAM Builder tu-lock
      (yaml=locked ma registry blueprint_constitution != locked -> FAIL).
  C2  Du 14 domain bat buoc (thieu 1 = FAIL).
  C3  Moi domain du 12 field contract; field loi (manager/schema/validator/
      source_of_truth/writer/lifecycle/audit_rule/responsibility/
      non_responsibility) khong duoc rong.
  C4  Layer + huong phu thuoc: dep phai la domain da khai + layer THAP HON
      strictly (nguoc chieu = FAIL); dep nam trong forbidden_dependencies = FAIL.
  C5  Supernatural DOC LAP: phai la domain top-level, khong domain nao
      `contains` no, khong co `sub_of`, dependencies rong.
  C6  Memory: du 6 scope, moi scope co owner (la domain da khai) + scope + store.
  C7  Chong phantom: moi path status=exists PHAI ton tai tren disk (khai lao
      = FAIL). status=planned duoc phep, KHONG FAIL (Video/Publisher... chua
      co manager that — khai planned la trung thuc; CAM stub/vaporware de qua
      test). planned ma path DA xuat hien tren disk -> WARN drift (khong chan):
      cap nhat contract sang exists co duyet, khong de lech.
  C8  lifecycle thuoc enum; reader/writer thuoc domains + {mr_long}.

Exit 0 = PASS, exit 1 = FAIL (in tung vi pham). Khong tu phong PASS ngoai exit-code.
Usage: python tools/blueprint_constitution_check.py [--file <yaml>] [--registry <yaml>]
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DEFAULT_FILE = REPO / 'governance' / 'blueprint' / 'blueprint_domains.yaml'
DEFAULT_REGISTRY = REPO / 'governance' / 'architecture_registry.yaml'

REQUIRED_DOMAINS = [
    'character', 'dialogue', 'world', 'timeline', 'event', 'supernatural',
    'story_planner', 'generator', 'qa_runtime', 'production', 'tts',
    'audio', 'video', 'publisher',
]
REQUIRED_FIELDS = [
    'responsibility', 'non_responsibility', 'source_of_truth', 'manager',
    'schema', 'validator', 'reader', 'writer', 'lifecycle', 'dependencies',
    'forbidden_dependencies', 'audit_rule',
]
# reader/dependencies/forbidden_dependencies duoc phep list rong; con lai phai non-empty
NONEMPTY_FIELDS = [f for f in REQUIRED_FIELDS
                   if f not in ('reader', 'dependencies', 'forbidden_dependencies')]
REQUIRED_MEMORY = ['global_memory', 'series_memory', 'episode_memory',
                   'character_memory', 'event_memory', 'supernatural_memory']
LIFECYCLES = ['planned', 'active', 'locked_bible', 'locked_tool']
EXTRA_WRITERS = ['mr_long']
SUPERNATURAL_HOSTS = ['world', 'event', 'story_planner']


# PLANNED HONESTY RULE (Mr.Long 3/7): planned PHAI du 5 metadata, thieu 1 = FAIL.
PLANNED_META = ['planned_path', 'owner', 'reason_not_exists_yet',
                'target_milestone', 'blocking_dependency']


def _pathref_errors(label, ref, root, warns=None, milestones=None, domains=None):
    """exists: {path, status} + path PHAI tren disk (khai lao = FAIL phantom).
    planned: PLANNED HONESTY RULE — du 5 metadata (PLANNED_META), thieu = FAIL;
    khong FAIL vi planned; planned_path da xuat hien tren disk -> WARN drift."""
    errs = []
    if not isinstance(ref, dict) or not ref.get('status'):
        return [f'{label}: phai la mapping co status — nhan duoc {ref!r}']
    st = ref['status']
    if st not in ('exists', 'planned'):
        errs.append(f"{label}: status '{st}' khong thuoc exists|planned")
    elif st == 'exists':
        if not ref.get('path'):
            errs.append(f'{label}: exists phai co path')
        elif not (root / ref['path']).exists():
            errs.append(f"{label}: khai exists nhung KHONG co tren disk (khai lao/phantom): {ref['path']}")
    else:  # planned
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
        if pp and (root / pp).exists() and warns is not None:
            warns.append(f'{label}: khai planned nhung path DA co tren disk — drift/stub? '
                         f'cap nhat contract (co duyet): {pp}')
    return errs


def check(data, root=REPO, registry_path=DEFAULT_REGISTRY, warns=None):
    errs = []
    if not isinstance(data, dict):
        return ['blueprint yaml khong phai mapping']
    meta = data.get('meta') or {}
    domains = data.get('domains') or {}
    layers = data.get('layers') or {}
    memory = data.get('memory') or {}
    milestones = data.get('milestones') or {}

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
        except Exception as e:  # registry khong doc duoc -> nghi ngo mac dinh
            errs.append(f'khong doc duoc registry de xac thuc lock: {e}')
        if isinstance(reg_status, str):
            reg_status = reg_status.split()[0] if reg_status else reg_status
        if reg_status != 'locked':
            errs.append('SELF-LOCK: yaml khai locked nhung registry blueprint_constitution '
                        f'= {reg_status!r} (lock la chu ky Mr.Long trong registry, Builder CAM tu lock)')
    elif status not in ('candidate', 'draft', None):
        errs.append(f"meta.promotion_status '{status}' khong thuoc candidate|draft|locked")

    # C2 du 14 domain
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

    # C3/C4/C7/C8 tung domain
    for name, d in domains.items():
        d = d or {}
        for f in REQUIRED_FIELDS:
            if f not in d:
                errs.append(f'{name}: THIEU field {f}')
            elif f in NONEMPTY_FIELDS and not d[f]:
                errs.append(f'{name}: field {f} RONG')
        if name not in layers:
            errs.append(f'{name}: thieu layer trong layers map')
        if d.get('lifecycle') and d['lifecycle'] not in LIFECYCLES:
            errs.append(f"{name}: lifecycle '{d['lifecycle']}' khong thuoc {LIFECYCLES}")
        # deps: ton tai + huong + forbidden
        my_layer = layers.get(name)
        forb = d.get('forbidden_dependencies') or []
        for dep in (d.get('dependencies') or []):
            if dep not in domains:
                errs.append(f'{name}: dep {dep!r} khong phai domain da khai')
                continue
            if dep in forb:
                errs.append(f'{name}: dep {dep!r} nam trong forbidden_dependencies cua chinh no')
            dep_layer = layers.get(dep)
            if isinstance(my_layer, int) and isinstance(dep_layer, int) and dep_layer >= my_layer:
                errs.append(f'{name}(L{my_layer}) depend {dep}(L{dep_layer}) — SAI HUONG '
                            '(chi duoc depend layer thap hon strictly)')
        # reader/writer hop le
        for role in ('reader', 'writer'):
            for who in (d.get(role) or []):
                if who not in domains and who not in EXTRA_WRITERS:
                    errs.append(f"{name}: {role} {who!r} khong phai domain/mr_long")
        # C7 phantom + planned-honesty check
        for i, ref in enumerate(d.get('source_of_truth') or []):
            errs += _pathref_errors(f'{name}.source_of_truth[{i}]', ref, root,
                                    warns, milestones, domains)
        for f in ('manager', 'schema', 'validator'):
            if isinstance(d.get(f), dict):
                errs += _pathref_errors(f'{name}.{f}', d[f], root, warns, milestones, domains)

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
    print('=== BLUEPRINT CONSTITUTION CHECK ===')
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
        print(f'  [WARN drift] {w}')
    if errs:
        for e in errs:
            print(f'  [VIOLATION] {e}')
        print(f'=== FAIL — {len(errs)} vi pham / {n_dom} domain ===')
        return 1
    planned = sum(1 for d in data['domains'].values()
                  for f in ('manager', 'schema', 'validator')
                  if isinstance(d.get(f), dict) and d[f].get('status') == 'planned')
    print(f'  domains: {n_dom}/14 · memory: 6/6 · planned(ROADMAP) refs: {planned}'
          f' · warn drift: {len(warns)}')
    print('=== PASS — blueprint constitution hop le (0 vi pham) ===')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
