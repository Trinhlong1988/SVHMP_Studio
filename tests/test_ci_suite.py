"""pytest bridge — chay cac test script-style qua subprocess, assert exit 0.
Cho phep `pytest -q` xac minh toan bo bo test lõi (Boss 2/7 yeu cau pytest).
"""
import subprocess
import sys
from pathlib import Path
import pytest

SVHMP = Path(__file__).resolve().parent.parent
SCRIPTS = [
    'tools/architecture_registry_check.py',
    'tests/test_tail_pathology_r199.py',
    'tests/test_qa_clean_tail_r201.py',
    'tests/test_intro_tail_50cases_r202.py',
    'tests/test_qa_confusion_200_r203.py',
    'tests/test_qa_waiver_r204.py',
    'tests/test_character_manager_r205.py',
    'tests/test_character_system_1000_r206.py',
    'tests/test_story_consistency_1000_r207.py',
    'tests/test_dialogue_appropriateness_1000_r208.py',
]


@pytest.mark.parametrize('script', SCRIPTS)
def test_script_exit_zero(script):
    r = subprocess.run([sys.executable, str(SVHMP / script)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"{script} exit={r.returncode}\n{r.stdout[-600:]}\n{r.stderr[-300:]}"
