"""SVHMP — CANON-FACT PROVENANCE checker (de xuat #3, R216 hard-lock).

Doc THAT governance/canon_facts.yaml + xac minh moi canon-fact recurring khai du
PROVENANCE (chong "backward codification" DEBT-035 — field-hoa canon theo tap sau):
  (a) COVERAGE   — moi fact trong REQUIRED_FACTS phai co mat. Thieu -> FAIL.
  (b) value      — thieu/rong -> FAIL.
  (c) anchor_ep  — thieu / KHONG phai int -> FAIL (anchor R216 = tap sinh som nhat).
  (d) anchor_commit — thieu / KHONG resolve qua GIT THAT (`git cat-file -e
      <sha>^{commit}`) -> FAIL. KHONG grep source; chay git that.

provenance_problems(facts, required) = PURE (chi doc dict + kiem field, KHONG chay
git) -> self-test mutation goi thang, deepcopy/monkeypatch. commit_resolves(sha,
repo_root) = fn RIENG chay `git cat-file -e` that -> self-test co the monkeypatch.
commit_problems(facts, resolver) tach resolver ra de test bom resolver gia.

CHU Y (R215.5/R215.6): checker + self-test phai BEHAVIORAL, KHONG grep-only.
KHONG wire vao ci_gate.CHECKS (chay trong pytest la du; neu wire phai them
gate_mutation_map.yaml — reviewer quyet). Idempotent — chi doc, khong ghi.
"""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
import yaml  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
FACTS_PATH = REPO / 'governance' / 'canon_facts.yaml'

# Canon-fact recurring PHAI khai provenance (bounded scope task, anchor EP01).
REQUIRED_FACTS = [
    'kp_seat',
    'havy_death_place',
    'havy_death_mechanism',
    'havy_death_context',
    'havy_death_notifier',
    'havy_death_time',
]


def load_facts(path=FACTS_PATH):
    return yaml.safe_load(Path(path).read_text(encoding='utf-8')) or {}


def provenance_problems(mapping, required=REQUIRED_FACTS):
    """PURE (chi doc dict, KHONG chay git) — self-test mutation goi thang.

    Tra ve dict:
      missing      : REQUIRED fact vang trong map.
      no_value     : fact thieu/rong 'value'.
      bad_anchor_ep: fact thieu 'anchor_ep' hoac KHONG phai int.
      no_commit    : fact thieu/rong 'anchor_commit' (RESOLVE git kiem o commit_problems).
    """
    facts = (mapping or {}).get('facts') or {}
    missing = [f for f in required if f not in facts]
    no_value, bad_anchor_ep, no_commit = [], [], []

    for fid, info in facts.items():
        info = info or {}

        val = info.get('value')
        if val is None or (isinstance(val, str) and not val.strip()):
            no_value.append(f"{fid}: thieu/rong 'value'")

        ep = info.get('anchor_ep')
        # bool la subclass cua int -> loai truong hop True/False lot.
        if ep is None or isinstance(ep, bool) or not isinstance(ep, int):
            bad_anchor_ep.append(f"{fid}: 'anchor_ep'={ep!r} thieu hoac KHONG phai int")

        sha = info.get('anchor_commit')
        if sha is None or (isinstance(sha, str) and not sha.strip()):
            no_commit.append(f"{fid}: thieu/rong 'anchor_commit'")

    return {'missing': missing, 'no_value': no_value,
            'bad_anchor_ep': bad_anchor_ep, 'no_commit': no_commit}


def commit_resolves(sha, repo_root=REPO):
    """Chay `git cat-file -e <sha>^{commit}` THAT -> True neu commit ton tai trong
    repo. KHONG grep. sha rong/None -> False (khong goi git)."""
    if not sha or not str(sha).strip():
        return False
    r = subprocess.run(
        ['git', 'cat-file', '-e', f'{str(sha).strip()}^{{commit}}'],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        cwd=str(repo_root))
    return r.returncode == 0


def commit_problems(mapping, resolver=commit_resolves, repo_root=REPO):
    """Voi moi fact co 'anchor_commit', xac nhan resolver(sha) True (git that).
    resolver tach ra de self-test bom resolver gia -> mutation-proof KHONG can bia
    commit that. Tra ve list mo ta fact co anchor_commit KHONG resolve."""
    facts = (mapping or {}).get('facts') or {}
    problems = []
    for fid, info in facts.items():
        info = info or {}
        sha = info.get('anchor_commit')
        if sha is None or (isinstance(sha, str) and not sha.strip()):
            continue  # 'no_commit' da bat o provenance_problems
        if not resolver(sha, repo_root):
            problems.append(
                f"{fid}: anchor_commit '{sha}' KHONG resolve qua git "
                "(git cat-file -e <sha>^{commit} that FAIL) — SHA bia hoac chua co trong repo")
    return problems


def main():
    print("=== CANON-FACT PROVENANCE CHECK (R216 — EP01 = anchor) ===")
    mapping = load_facts()
    facts = (mapping or {}).get('facts') or {}
    pv = provenance_problems(mapping)
    cp = commit_problems(mapping)

    print(f"  fact trong map: {len(facts)}   REQUIRED: {len(REQUIRED_FACTS)}")
    for fid in REQUIRED_FACTS:
        info = facts.get(fid) or {}
        ep = info.get('anchor_ep', 'MISSING')
        sha = str(info.get('anchor_commit', 'MISSING'))[:12]
        ok = fid in facts
        print(f"    [{'OK' if ok else 'X'}] {fid:22} anchor_ep={ep} commit={sha}")

    fail = 0
    for key, label in [('missing', 'MISSING (REQUIRED fact thieu trong map)'),
                       ('no_value', 'NO-VALUE'),
                       ('bad_anchor_ep', 'BAD-ANCHOR-EP (thieu/khong-int)'),
                       ('no_commit', 'NO-COMMIT (thieu anchor_commit)')]:
        if pv[key]:
            fail += 1
            print(f"\n[{label}] {len(pv[key])}:")
            for s in pv[key]:
                print(f"  X {s}")
    if cp:
        fail += 1
        print(f"\n[COMMIT-UNRESOLVED] {len(cp)} anchor_commit khong resolve qua git that:")
        for s in cp:
            print(f"  X {s}")

    verdict = ('PASS (moi REQUIRED fact co provenance: value+anchor_ep(int)+'
               'anchor_commit resolve git that)') if not fail else f'FAIL ({fail} nhom van de)'
    print(f"\n=== {verdict} ===")
    return 1 if fail else 0


if __name__ == '__main__':
    sys.exit(main())
