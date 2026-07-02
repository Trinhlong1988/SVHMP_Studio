"""Lock hanh vi tools/validate_project_config.py (PACK4 enforcer cho doc 15).

Nham TOOL (khong phai doc): chay qua subprocess --path, doc EXIT-CODE that -
giong het production/ci_gate. Chong weak-verifier + khoa fix empty-value.

>=1 valid  -> exit 0
>=5 invalid -> exit 1: thieu-field / sai-kieu / EMPTY-value / YAML-hong / not-a-mapping
BOM: valid + BOM -> exit 0 (chot PyYAML nuot BOM la mong doi).
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TOOL = REPO / 'tools' / 'validate_project_config.py'

VALID = """genre: horror
distribution:
  age_child: [0.1, 0.15]
dialect: south
beat:
  - opening
  - ending
taxonomy:
  object: bible/12
"""


def _run(text, tmp_path, name='project_config.yaml', encoding='utf-8'):
    p = tmp_path / name
    p.write_text(text, encoding=encoding)
    r = subprocess.run([sys.executable, str(TOOL), '--path', str(p)],
                       capture_output=True, text=True)
    return r.returncode


def test_valid_config_exit_0(tmp_path):
    assert _run(VALID, tmp_path) == 0


def test_missing_field_exit_1(tmp_path):
    text = VALID.replace('dialect: south\n', '')  # thieu dialect
    assert _run(text, tmp_path) == 1


def test_wrong_type_exit_1(tmp_path):
    text = VALID.replace('beat:\n  - opening\n  - ending\n', 'beat: not_a_list\n')
    assert _run(text, tmp_path) == 1


def test_empty_value_exit_1(tmp_path):
    """Khoa fix #1: field co mat nhung RONG ('' / [] / {}) PHAI bi reject."""
    text = "genre: ''\ndistribution: {}\ndialect: '   '\nbeat: []\ntaxonomy: {}\n"
    assert _run(text, tmp_path) == 1


def test_broken_yaml_exit_1(tmp_path):
    assert _run(': : bad : :\n  - x\n y', tmp_path) == 1


def test_not_a_mapping_exit_1(tmp_path):
    assert _run('- just\n- a\n- list\n', tmp_path) == 1


def test_missing_path_exit_1():
    """--path tro toi file khong ton tai -> exit 1 (khong crash, bao ro)."""
    r = subprocess.run(
        [sys.executable, str(TOOL), '--path', str(REPO / 'khong_ton_tai_xyz.yaml')],
        capture_output=True, text=True)
    assert r.returncode == 1


def test_valid_with_bom_exit_0(tmp_path):
    """Valid + BOM -> exit 0 (PyYAML nuot BOM la hanh vi mong doi)."""
    assert _run(VALID, tmp_path, name='project_config_bom.yaml',
                encoding='utf-8-sig') == 0
