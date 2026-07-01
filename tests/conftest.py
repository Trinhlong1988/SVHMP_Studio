# pytest config — bo qua test script-style (chay bang python + sys.exit, khong phai pytest-func).
# Chung duoc chay qua subprocess trong test_ci_suite.py (assert exit 0).
collect_ignore_glob = [
    'test_tail_*.py', 'test_qa_*.py', 'test_intro_*.py',
    'test_character_*.py', 'test_story_*.py', 'test_dialogue_*.py',
    'test_harness.py', 'test_voice_*.py', 'test_full_text_*.py',
]
