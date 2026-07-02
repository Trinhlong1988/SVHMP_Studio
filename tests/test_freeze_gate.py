"""Test freeze_gate — deep-audit (2/7). Chi test helper nhe (khong chay auditor)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import freeze_gate as fg  # noqa: E402


def test_find_pack_progress_nested():
    reg = {"domains": {"gov": {"x": 1, "enterprise_pack_progress": {"pack2_governance": "locked"}}}}
    prog = fg.find_pack_progress(reg)
    assert prog == {"pack2_governance": "locked"}


def test_find_pack_progress_absent():
    assert fg.find_pack_progress({"a": {"b": [1, 2]}}) is None


def test_pack2_locked_live():
    # trang thai THAT: PACK2 da FROZEN -> phai 'locked'
    ok, detail = fg.check_pack_locked("pack2_governance")
    assert ok, f"pack2_governance khong locked: {detail}"


def test_unknown_pack_not_locked():
    ok, _ = fg.check_pack_locked("pack99_nonexistent")
    assert ok is False


def test_tag_local_missing_is_false():
    ok, _ = fg.check_tag_local("no-such-tag-zzz-999")
    assert ok is False
