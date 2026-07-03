"""Guard: file_index.yaml 'total' PHẢI == len(files) — máy đếm, cấm đếm tay.

Bug class bắt tại G2 build 3/7: total=260 nhưng files thực = 278 (các pack
append entry tay quên bump). Bài học 3/7 Mr.Long: "mọi inventory ký chốt phải
có test assert len == N". registry_check không soi field này -> guard riêng.

pytest-func -> tự động collect trong `pytest tests/` và ci_gate.
"""
from pathlib import Path

import yaml

SVHMP = Path(__file__).resolve().parent.parent


def test_file_index_total_matches_len_files():
    d = yaml.safe_load((SVHMP / 'governance' / 'file_index.yaml')
                       .read_text(encoding='utf-8'))
    assert d['total'] == len(d['files']), (
        f"file_index total={d['total']} nhưng len(files)={len(d['files'])} — "
        "append entry phải bump total (máy đếm: registry_triage ghi total=len)")
