"""Test verify_commit_claim — deep-audit (2/7) claim-check logic (khong dung git)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import verify_commit_claim as vcc  # noqa: E402


def test_style_claim_detected():
    for m in ["style: no logic change", "chore: format only", "reformat tools",
              "chore: khong doi logic", "chi format lai"]:
        assert vcc.is_style_claim(m), m


def test_non_style_claim_ignored():
    for m in ["feat(G2): wire gate into render", "fix: close registry gap",
              "test: add guard"]:
        assert not vcc.is_style_claim(m), m


def test_ast_equivalent_true_for_whitespace_and_docstring_reflow():
    old = 'def f():\n    """one line doc."""\n    x = [1,2,3]\n    return x\n'
    new = ('def f():\n    """one\n    line doc."""\n    x = [\n        1, 2, 3,\n    ]\n'
           '    return x\n')
    assert vcc.ast_equivalent(old, new)


def test_ast_diff_for_behavior_preserving_refactor():
    # ternary-expr-statement -> if (b771384 class): AST cau truc DOI -> phai flag
    old = "x() if cond else None\n"
    new = "if cond:\n    x()\n"
    assert not vcc.ast_equivalent(old, new)


def test_ast_diff_for_real_logic_change():
    # doi nguong 8 -> 11 (b771384 test file class)
    old = "def need(n):\n    return n >= 8\n"
    new = "def need(n):\n    return n >= 11\n"
    assert not vcc.ast_equivalent(old, new)


def test_check_no_claim_returns_false():
    has, mism = vcc.check("feat: real feature", "HEAD", None)
    assert has is False and mism == []
