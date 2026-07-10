"""G7 D2 — reality anchor test cho tools/episode_generator.py.

Khong mock du lieu goc (bible/09/12/13/21 that, story_planner/decision_engine that)
- kiem tra dung nguyen tac R195 (khong bia) + Promotion Gate R211 (chi dung domain
lifecycle=approved, decision_engine hien draft phai duoc ghi ro canh bao) + interface
contract read-only (generator KHONG duoc ghi vao 14 domain nguon).
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import episode_generator as eg  # noqa: E402
import g7_ep01_dry_run as dryrun  # noqa: E402
import g7_generator_check as g7c  # noqa: E402

SCHEMA_PATH = REPO / "governance" / "blueprint" / "schemas" / "episode_schema.yaml"


def _schema_frontmatter_fields():
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    return schema["schema"]["episode_frontmatter"]["fields"]


def test_reality_build_packet_ep01_no_crash():
    packet = eg.build_episode_packet(1)
    assert "episode_frontmatter" in packet
    assert packet.get("pending") is not True


def test_g6a_1_decision_packet_plan_ref_has_correct_value_not_just_not_none():
    """G6a-1 (audit HIGH, TASK_AUDIT_HIGH_G2_G8.md): DEBT-007 fix (decision_engine.py
    doc dung key 'episode_number'/'season_ref' tu story plan that thay vi 'plan.get
    ("plan_ref")' sai key) duoc claim CLOSED nhung 30/30 test cu chi assert plan_ref
    IS NOT None (tests/test_g6a_decision_engine.py:159 chi kiem truong hop KHONG co
    plan). Neu ai revert decision_engine.py ve doc sai key (plan.get("plan_ref") thay
    vi f-string ep{episode_number}_{season_ref}), packet van co plan_ref (gia tri None
    tu .get() that bai am tham hoac gia tri rac) ma KHONG test nao bat duoc gia tri SAI.
    Test nay goi dung duong that (episode_generator.py -> decision_engine.build_packet
    voi plan=story_plan that cua EP01) va doi chieu GIA TRI CHINH XAC."""
    import story_planner
    story_plan = story_planner.build_episode_plan_ep01()
    packet = eg.build_episode_packet(1)
    expected = f"ep{story_plan['episode_number']}_{story_plan['season_ref']}"
    assert packet["decision_packet"]["plan_ref"] == expected, (
        f"plan_ref sai gia tri: {packet['decision_packet']['plan_ref']!r} != {expected!r}")


def test_reality_frontmatter_has_every_schema_field_key():
    """D1 schema khai N field cho episode_frontmatter - packet PHAI co dung tung
    key do (gia tri co the None neu khong the tai chinh thuc, nhung key khong duoc
    thieu - thieu key = generator bo sot field, khac voi 'field co gia tri None
    trung thuc')."""
    expected_fields = set(_schema_frontmatter_fields().keys())
    frontmatter = eg.build_episode_frontmatter(1)
    actual_fields = set(frontmatter.keys()) - {"_provenance_note"}
    assert expected_fields.issubset(actual_fields), (
        f"thieu field so voi episode_schema.yaml: {expected_fields - actual_fields}")


def test_reality_non_ep01_returns_pending_not_fabricated():
    """R195: episode_generator v1 CHI EP01 co du du lieu - ep khac PHAI tra ve pending
    kem ly do, KHONG duoc bia gia tri de 'co ve day du'."""
    for ep in (2, 26, 50, 73, 90):
        packet = eg.build_episode_packet(ep)
        assert packet.get("pending") is True, f"ep{ep} khong duoc bia du lieu day du"
        assert packet.get("reason"), f"ep{ep} pending nhung thieu ly do"


def test_reality_no_data_domains_marked_honestly_not_crashed():
    """4/14 domain (weather/culture/belief/ritual) chua co bible file tren dia -
    PHAI bao cao status='no_data_source' kem ly do, KHONG duoc crash hay bia gia tri."""
    reads = eg._domain_reads()
    for domain in ("weather", "culture", "belief", "ritual"):
        assert reads[domain]["status"] == "no_data_source"
        assert reads[domain]["source"] is None
        assert reads[domain]["reason"]


def test_reality_bible_only_domain_sources_exist_on_disk():
    """5/14 domain doc truc tiep bible (world/timeline/location/supernatural/object)
    - moi source file PHAI ton tai that (REALITY ANCHOR, khong tin loi khai)."""
    for domain, path in eg.BIBLE_ONLY_DOMAINS.items():
        assert path.exists(), f"domain {domain} khai source {path} nhung KHONG ton tai tren dia"


def test_reality_passenger_main_none_not_fabricated_for_ep01():
    """EP01 la pilot, KHONG co PAS_id that trong roster 100 (verify by_ep(1) rong) -
    packet PHAI de None, KHONG duoc bia 1 PAS_id gia de 'du field'."""
    from character_manager import CharacterRegistry
    assert CharacterRegistry().by_ep(1) == [], "gia dinh EP01 khong co trong roster da sai - kiem tra lai truoc khi tin test nay"
    frontmatter = eg.build_episode_frontmatter(1)
    assert frontmatter["passenger_main"] is None


def test_reality_decision_packet_lifecycle_warning_present():
    """R211 Promotion Gate: decision_engine domain lifecycle=draft (blueprint_domains.yaml)
    - packet PHAI tu ghi canh bao ro rang, KHONG duoc gia vo la approved."""
    packet = eg.build_episode_packet(1)
    assert packet["decision_packet_lifecycle_warning"] is not None
    assert "draft" in packet["decision_packet_lifecycle_warning"]


def test_reality_signature_object_id_exists_in_bible12():
    """signature_object PHAI la 1 OBJ_id THAT trong bible/12 (khong bia ten)."""
    b12 = yaml.safe_load(eg.BIBLE_12.read_text(encoding="utf-8"))
    frontmatter = eg.build_episode_frontmatter(1)
    obj_id = frontmatter["signature_object"]
    all_ids = set()
    for v in b12.values():
        if isinstance(v, dict):
            all_ids |= set(v.keys())
    assert obj_id in all_ids, f"{obj_id} khong ton tai trong bible/12_object_library.yaml"


def test_g7_gate_wired_in_ci_gate():
    """Unwire-guard (bai hoc G2_roster): stage G7_generator PHAI co trong ci_gate.CHECKS,
    khong duoc de sot lai sau khi build xong gate."""
    import ci_gate
    assert ("G7_generator", "tools/g7_generator_check.py") in ci_gate.CHECKS


def test_g7_gate_pass_on_real_data():
    import subprocess
    r = subprocess.run([sys.executable, str(REPO / "tools" / "g7_generator_check.py")],
                        capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr


def test_reality_d5_dry_run_reconciles_ep01_against_golden_reference():
    """D5: dry-run PHAI co so sanh so lieu THAT voi output/ep_01/episode.md (golden
    reference qua post_render_gate.check_ep(1), khong ghi de) - khong duoc chi 'chay
    duoc la xong'. Ky vong 6/6 field khop (da tu verify thu cong truoc khi ship)."""
    packet = eg.build_episode_packet(1)
    findings = dryrun.reconcile_ep01(packet)
    assert len(findings) == 6, f"thieu/thua field doi chieu: {len(findings)}"
    mismatches = [f for f in findings if f.get("match") is False]
    assert not mismatches, f"field LECH voi golden reference that: {mismatches}"


def test_reality_d5_dry_run_writes_to_sandbox_not_real_ep01():
    """DEBT-005 lesson: D5 dry-run TUYET DOI khong duoc ghi vao output/ep_01/ that,
    du chi tam thoi - PHAI ghi vao sandbox cach ly output/ep_g7_sample/."""
    import subprocess
    before = (REPO / "output" / "ep_01" / "episode.md").read_text(encoding="utf-8")
    r = subprocess.run([sys.executable, str(REPO / "tools" / "g7_ep01_dry_run.py")],
                       capture_output=True, text=True, cwd=str(REPO), encoding="utf-8")
    assert r.returncode == 0, r.stdout + r.stderr
    after = (REPO / "output" / "ep_01" / "episode.md").read_text(encoding="utf-8")
    assert before == after, "output/ep_01/episode.md THAT bi dung cham boi D5 dry-run - VI PHAM DEBT-005 lesson"
    assert (REPO / "output" / "ep_g7_sample" / "episode_packet_ep01.yaml").exists()
    assert (REPO / "output" / "ep_g7_sample" / "D5_dry_run_report.md").exists()


def test_module_source_has_no_write_calls_to_domain_files():
    """Interface contract (bp1/interface_contracts.yaml): generator CHI duoc 'read'
    tren 14 domain, forbidden_operations bao gom 'write'. Static check: source code
    cua episode_generator.py KHONG duoc chua loi goi ghi file (open(..., 'w'/'a'),
    .write_text, yaml.safe_dump ra file) nham vao bat ky domain source nao."""
    src = (REPO / "tools" / "episode_generator.py").read_text(encoding="utf-8")
    # audit ML #21 (10/7): mo rong pattern cam - ngoai open/write_text/write_bytes, cam ca ghi/exec
    # GIAN TIEP (shutil.copy/move, os.system, subprocess, os.replace) co the ne text-grep truoc do.
    # Mirror dung tools/g7_generator_check.py::_stage_static_no_write_src (gate doc lap cung do phu).
    forbidden_patterns = ['open(', ".write_text(", ".write_bytes(", 'shutil.copy', 'shutil.move',
                          'os.system', 'subprocess', 'os.replace']
    hit = [p for p in forbidden_patterns if p in src]
    assert not hit, (
        f"episode_generator.py vi pham forbidden_operations:write/exec (interface_contracts.yaml): {hit}")


# ============================================================
# G7-1 (10/7, per Mr.Long authorization, TASK_AUDIT_HIGH_G2_G8.md): no_write_domain
# ban cu dung 'git diff --name-only HEAD' (working-tree vs HEAD) - LUON RONG luc
# pre-push chay that (da commit xong) nen tu-skip 100% dung luc can kiem nhat. Doi
# sang so sanh commit(s) HEAD chua len origin/main (merge-base..HEAD).
# ============================================================

def _init_temp_git_repo(tmp_path):
    """Tao 1 git repo THAT trong tmp_path (khong gia lap git plumbing) - commit1 la
    baseline, gan lam refs/remotes/origin/main (khong can remote that ket noi)."""
    import subprocess as sp
    sp.run(['git', 'init', '-q'], cwd=str(tmp_path), check=True)
    sp.run(['git', 'config', 'user.email', 'test@test.local'], cwd=str(tmp_path), check=True)
    sp.run(['git', 'config', 'user.name', 'test'], cwd=str(tmp_path), check=True)
    (tmp_path / 'a.txt').write_text('base', encoding='utf-8')
    sp.run(['git', 'add', 'a.txt'], cwd=str(tmp_path), check=True)
    sp.run(['git', 'commit', '-q', '-m', 'base'], cwd=str(tmp_path), check=True)
    base_sha = sp.run(['git', 'rev-parse', 'HEAD'], cwd=str(tmp_path),
                      capture_output=True, text=True, check=True).stdout.strip()
    sp.run(['git', 'update-ref', 'refs/remotes/origin/main', base_sha], cwd=str(tmp_path), check=True)
    return tmp_path


def test_g7_1_changed_files_vs_origin_main_real_repo_no_crash():
    """Reality anchor: tren REPO that (session dang lam viec), origin/main PHAI resolve
    duoc (R200 realtime sync workflow luon fetch/push origin/main) - tra ve set, KHONG
    None."""
    changed = g7c._changed_files_vs_origin_main()
    assert changed is not None, (
        "origin/main khong resolve duoc tren repo that - kiem tra da 'git fetch origin main' chua")
    assert isinstance(changed, set)


def test_g7_1_changed_files_vs_origin_main_returns_none_when_unresolvable(tmp_path):
    """MUTATION-PROOF (git that, khong gia lap): repo KHONG co origin/main ref -> tra
    ve None (khong duoc am tham tra ve set rong - se che mat that bai that)."""
    import subprocess as sp
    _init_temp_git_repo(tmp_path)
    sp.run(['git', 'update-ref', '-d', 'refs/remotes/origin/main'], cwd=str(tmp_path), check=True)
    assert g7c._changed_files_vs_origin_main(repo=tmp_path) is None


def test_g7_1_changed_files_vs_origin_main_detects_real_diff(tmp_path):
    """MUTATION-PROOF (git that): tao 1 commit THAT sau origin/main sua 2 file, xac
    nhan _changed_files_vs_origin_main() tra ve DUNG 2 file do (chung minh git plumbing
    that hoat dong, khong phai gia lap chuoi)."""
    import subprocess as sp
    repo = _init_temp_git_repo(tmp_path)
    (repo / 'tools_episode_generator.py').write_text('x', encoding='utf-8')
    (repo / 'domain_source.yaml').write_text('y', encoding='utf-8')
    sp.run(['git', 'add', '.'], cwd=str(repo), check=True)
    sp.run(['git', 'commit', '-q', '-m', 'push-candidate'], cwd=str(repo), check=True)
    changed = g7c._changed_files_vs_origin_main(repo=repo)
    assert changed == {'tools_episode_generator.py', 'domain_source.yaml'}


def test_g7_1_stage_no_write_domain_catches_real_cross_domain_commit(monkeypatch):
    """MUTATION-PROOF bat buoc (per task doc): gia lap 1 commit sua CUNG luc tools/
    episode_generator.py + 1 domain source path THAT (tu blueprint_domains.yaml
    dependencies cua generator) -> _stage_no_write_domain() PHAI FAIL (rc=1)."""
    generator_rel = str((REPO / "tools" / "episode_generator.py").relative_to(REPO)).replace('\\', '/')
    domain_paths = g7c._generator_dependency_source_paths()
    assert domain_paths, "generator dependencies rong - kiem tra lai blueprint_domains.yaml"
    one_domain_path = sorted(domain_paths)[0]
    monkeypatch.setattr(g7c, "_changed_files_vs_origin_main",
                        lambda: {generator_rel, one_domain_path})
    result = g7c._stage_no_write_domain()
    assert result['rc'] == 1, f"commit sua CUNG generator+domain nguon KHONG bi bat: {result}"
    assert one_domain_path in result['tail']


def test_g7_1_stage_no_write_domain_clean_when_only_generator_changed(monkeypatch):
    generator_rel = str((REPO / "tools" / "episode_generator.py").relative_to(REPO)).replace('\\', '/')
    monkeypatch.setattr(g7c, "_changed_files_vs_origin_main", lambda: {generator_rel})
    result = g7c._stage_no_write_domain()
    assert result['rc'] == 0


def test_g7_1_stage_no_write_domain_skips_when_generator_untouched(monkeypatch):
    monkeypatch.setattr(g7c, "_changed_files_vs_origin_main", lambda: {"bible/00_constitution.yaml"})
    result = g7c._stage_no_write_domain()
    assert result['rc'] == 0
    assert "skip" in result['tail']


def test_g7_1_stage_no_write_domain_fails_safe_when_origin_main_unresolvable(monkeypatch):
    """Ban cu (working-tree diff) se AM THAM bo qua check khi khong co origin/main;
    ban moi PHAI FAIL an toan (R195 'uncertainty -> STOP khong ACT'), khong duoc coi
    None la '0 file thay doi'."""
    monkeypatch.setattr(g7c, "_changed_files_vs_origin_main", lambda: None)
    result = g7c._stage_no_write_domain()
    assert result['rc'] == 1


def test_g7_1_gate_pass_on_real_repo_state():
    """Reality anchor: gate chay standalone tren repo that (khong mutation) PHAI PASS -
    hien tai KHONG co commit nao chua len origin/main dung cham tools/episode_generator.py."""
    result = g7c._stage_no_write_domain()
    assert result['rc'] == 0, result['tail']
