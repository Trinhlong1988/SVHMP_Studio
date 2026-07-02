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
#
# deep-audit (2/7) orphan-fix: glob RONG (vd 'test_character_*') nuot NHAM
# test_character_gate_g2.py (PYTEST-FUNC, 7 test cho G2 gate) -> khong gate nao
# chay = orphan. Chuyen sang DANH SACH TUONG MINH = dung cac file script-style
# (khop test_ci_suite.py SCRIPTS + test_harness). File pytest-func moi se tu dong
# duoc collect. test_no_orphan_tests.py canh cho: cam pytest-func nam trong list nay.
collect_ignore_glob = [
    'test_tail_pathology_r199.py',
    'test_qa_clean_tail_r201.py',
    'test_intro_tail_50cases_r202.py',
    'test_qa_confusion_200_r203.py',
    'test_qa_waiver_r204.py',
    'test_character_manager_r205.py',
    'test_character_system_1000_r206.py',
    'test_story_consistency_1000_r207.py',
    'test_dialogue_appropriateness_1000_r208.py',
    'test_harness.py',
]
