# pytest config — bo qua test script-style (chay bang python + sys.exit, khong phai pytest-func).
# Chung duoc chay qua subprocess trong test_ci_suite.py (assert exit 0).
#
# deep-audit F3 (2/7): test_full_text_gate_r86_broad.py (R197 TOI THUONG, 5 test)
# va test_voice_profile_manager.py (15 test) la PYTEST-FUNC bi ignore NHAM +
# KHONG co trong test_ci_suite -> mo coi (khong gate nao chay). Da go khoi ignore
# -> `pytest tests/` (va ci_gate) nay chay chung.
# test_voice_qa_tools.py: F8 da fix (prosody detector bat duoc synthetic
# 220->110Hz drop) -> da un-ignore, gio `pytest tests/` chay (15 pass + skip).
# test_harness.py van ignore: script-style + phu thuoc content/daemon (flaky).
collect_ignore_glob = [
    'test_tail_*.py', 'test_qa_*.py', 'test_intro_*.py',
    'test_character_*.py', 'test_story_*.py', 'test_dialogue_*.py',
    'test_harness.py',
]
