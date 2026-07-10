"""tests/test_write_episode_line_production_guard.py — Bug #1 (TASK_AUDIT_CRITICAL_G3_G5.md).

CMD_AUDIT phat hien (10/7, workflow da-agent 9-10/7): tools/dialogue_generator.py::
write_episode_line() docstring cam ket "KHONG BAO GIO tro vao 50 tap that da locked"
nhung than ham KHONG co guard nao - goi voi root=output that + ep_n so se ghi de tap
da locked. Fix: raise ValueError dung to hop nguy hiem (root production + ep_n so).

AN TOAN TUYET DOI (tinh than DEBT-005): moi test o day dung tmp_path GIA LAP "production
root" qua monkeypatch dg.SVHMP - KHONG BAO GIO dung cham thu muc output/ that cua repo,
ke ca trong mutation-proof (mutated function cung chay tren tmp_path gia lap).
"""
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import dialogue_generator as dg  # noqa: E402


def test_raises_on_production_root_plus_numeric_ep_n(tmp_path, monkeypatch):
    """To hop nguy hiem: root == SVHMP/'output' (gia lap qua monkeypatch) + ep_n so nguyen
    -> PHAI raise ValueError, KHONG duoc tao file."""
    monkeypatch.setattr(dg, "SVHMP", tmp_path)
    fake_output = tmp_path / "output"
    fake_output.mkdir()

    with pytest.raises(ValueError, match="production"):
        dg.write_episode_line(fake_output, 5, "Câu thử.")

    assert not (fake_output / "ep_05").exists(), (
        "guard raise nhung van tao thu muc ep_05 - phai raise TRUOC khi mkdir/write")


def test_raises_on_production_root_plus_numeric_string_ep_n(tmp_path, monkeypatch):
    """ep_n dang CHUOI TOAN CHU SO ('5') cung phai bi chan - int('5') thanh cong."""
    monkeypatch.setattr(dg, "SVHMP", tmp_path)
    fake_output = tmp_path / "output"
    fake_output.mkdir()

    with pytest.raises(ValueError, match="production"):
        dg.write_episode_line(fake_output, "5", "Câu thử.")
    assert not (fake_output / "ep_05").exists()


def test_valid_case_tmp_path_root_with_numeric_ep_n_unchanged(tmp_path):
    """Case hop le CU #1: root la tmp_path bat ky (KHONG phai SVHMP/'output' that) + ep_n
    so -> PHAI VAN CHAY DUOC nhu truoc (khong bi guard chan oan)."""
    out = dg.write_episode_line(tmp_path, 1, "Câu thử hợp lệ.")
    assert out.exists()
    assert out.parent.name == "ep_01"


def test_valid_case_production_root_with_non_numeric_ep_n_unchanged(tmp_path, monkeypatch):
    """Case hop le CU #2: root production (gia lap) + ep_n CHUOI NON-NUMERIC (vd 'g3_sample')
    -> PHAI VAN CHAY DUOC nhu truoc (day chinh la pattern g3_dialogue_check.py dang dung that
    voi root=SVHMP/'output' that + ep_n='g3_sample')."""
    monkeypatch.setattr(dg, "SVHMP", tmp_path)
    fake_output = tmp_path / "output"
    fake_output.mkdir()

    out = dg.write_episode_line(fake_output, "g3_sample", "Câu thử sandbox.")
    assert out.exists()
    assert out.parent.name == "ep_g3_sample"


def test_enforcement_detects_mutation_guard_removed(tmp_path, monkeypatch):
    """MUTATION-PROOF: doc source THAT, GO guard block (chi trong bo nho qua regex), exec
    vao namespace rieng -> goi ham da mutate voi CUNG to hop nguy hiem (production root gia
    lap + ep_n so) PHAI KHONG CON raise - chung minh guard goc THAT SU la nguyen nhan chan,
    khong phai test rong luon xanh. Van dung tmp_path gia lap - khong dung cham output/ that
    du guard bi mutate mat tac dung."""
    src = (REPO / "tools" / "dialogue_generator.py").read_text(encoding="utf-8")
    assert "ep_n_is_numeric" in src and "raise ValueError(" in src, (
        "tien de: guard phai dang ton tai trong source truoc khi mutate")

    mutated_src = re.sub(
        r"    if ep_n_is_numeric and Path\(root\)\.resolve\(\) == \(SVHMP / 'output'\)\.resolve\(\):\n"
        r"        raise ValueError\(.*?\n        \)\n",
        "",
        src, count=1, flags=re.DOTALL,
    )
    assert "raise ValueError(" not in mutated_src, (
        "mutation khong xoa duoc guard block - regex khong khop, sua lai pattern")
    assert mutated_src != src

    real_file = str(REPO / "tools" / "dialogue_generator.py")
    ns = {"__name__": "dialogue_generator_MUTATED_for_test", "__file__": real_file}
    exec(compile(mutated_src, real_file + " (MUTATED)", "exec"), ns)
    mutated_write = ns["write_episode_line"]
    ns["SVHMP"] = tmp_path  # gia lap production root TRONG namespace mutated, khong dung output/ that

    fake_output = tmp_path / "output"
    fake_output.mkdir()
    out = mutated_write(fake_output, 5, "Câu thử sau khi go guard.")
    assert out.exists(), (
        "MUTATION khong bi bat - go guard nhung ham mutated van raise (loi khac, khong phai "
        "do guard) - kiem tra lai regex mutate co dung dung block khong")
    assert (fake_output / "ep_05" / "episode.md").exists(), (
        "guard da bi go (theo thiet ke mutation) nen PHAI ghi duoc file - neu khong ton tai "
        "nghia la mutation khong that su vo hieu hoa guard, enforcement test khong chung minh duoc gi")
