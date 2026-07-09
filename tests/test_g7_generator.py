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

SCHEMA_PATH = REPO / "governance" / "blueprint" / "schemas" / "episode_schema.yaml"


def _schema_frontmatter_fields():
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    return schema["schema"]["episode_frontmatter"]["fields"]


def test_reality_build_packet_ep01_no_crash():
    packet = eg.build_episode_packet(1)
    assert "episode_frontmatter" in packet
    assert packet.get("pending") is not True


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
    forbidden_patterns = ['open(', "mode='w'", 'mode="w"', ".write_text(", ".write_bytes("]
    # yaml.safe_dump chi dung de PRINT ra stdout trong main(), khong ghi file - xac nhan
    # khong co Path(...).write_text/open(...'w') nao trong module.
    assert "open(" not in src, "episode_generator.py KHONG duoc tu mo file (chi doc qua yaml.safe_load(Path(...).read_text()))"
    assert ".write_text(" not in src and ".write_bytes(" not in src, (
        "episode_generator.py vi pham forbidden_operations:write (interface_contracts.yaml)")
