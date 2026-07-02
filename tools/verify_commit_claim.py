"""verify_commit_claim.py — deep-audit (2/7): bat commit khai "no logic change /
style / format only" MA thuc su doi cau truc code.

Van de tai dien: lời khai commit khong khop viec lam (a171120 "wire" ma khong
wire; b771384 "style no logic change" ma doi test 8->11 element). Gate cu "mu"
voi claim prose. Tool nay: neu message co tu khoa style/no-logic -> so AST
(chuan-hoa whitespace trong string) cua tung file .py doi -> file nao KHAC =
KHONG phai format thuan -> canh bao.

WARN mac dinh (khong hard-block): refactor bao toan hanh vi (vd ternary->if) van
doi AST cau truc nen block se false-positive. --strict -> exit 1 (cho auditor/CI).

Dung:
  python tools/verify_commit_claim.py --commit <rev>   # so rev vs rev^
  python tools/verify_commit_claim.py --staged         # so index vs HEAD
  python tools/verify_commit_claim.py --commit <rev> --strict
Exit: 0 = khop (hoac khong co style-claim); 1 = (chi khi --strict) co mismatch.
"""
import ast
import re
import subprocess
import sys
from pathlib import Path

SVHMP = Path(__file__).resolve().parent.parent

STYLE_CLAIMS = [
    r"no[\s-]*logic\s*change", r"no\s*functional\s*change", r"style[\s-]*only",
    r"format(ting)?[\s-]*only", r"\breformat", r"\bcosmetic\b", r"whitespace[\s-]*only",
    r"kh[oô]ng\s*[dđ][oô]?i\s*logic", r"ch[ií]\s*format",
]


def _git(*a):
    return subprocess.run(["git", "-C", str(SVHMP), *a], capture_output=True,
                          text=True, encoding="utf-8", errors="replace").stdout


class _NormStr(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, str):
            node.value = " ".join(node.value.split())
        return node


def _norm_dump(src):
    tree = ast.parse(src)
    _NormStr().visit(tree)
    return ast.dump(tree)


def ast_equivalent(old_src, new_src):
    """True neu 2 nguon TUONG DUONG AST sau khi chuan-hoa whitespace string.
    Tach ra de test."""
    return _norm_dump(old_src) == _norm_dump(new_src)


def is_style_claim(message):
    return any(re.search(p, message, re.IGNORECASE) for p in STYLE_CLAIMS)


def _changed_py(old_rev, new_rev):
    diff = _git("diff", "--name-only", old_rev, new_rev) if new_rev else \
        _git("diff", "--cached", "--name-only")
    return [f.strip() for f in diff.splitlines() if f.strip().endswith(".py")]


def _blob(rev, path):
    return _git("show", f"{rev}:{path}")


def check(message, old_rev, new_rev):
    """-> (has_claim, mismatches[list of (file, why)]). new_rev None = staged."""
    if not is_style_claim(message):
        return False, []
    mism = []
    for f in _changed_py(old_rev, new_rev):
        old = _blob(old_rev, f)
        new = _blob(new_rev, f) if new_rev else _git("show", f":{f}")
        if not old or not new:
            continue  # added/deleted -> khong so duoc
        try:
            if not ast_equivalent(old, new):
                mism.append((f, "AST doi (khong phai format thuan)"))
        except SyntaxError as e:
            mism.append((f, f"parse err: {e}"))
    return True, mism


def main():
    strict = "--strict" in sys.argv
    if "--commit" in sys.argv:
        rev = sys.argv[sys.argv.index("--commit") + 1]
        msg = _git("log", "-1", "--pretty=%B", rev)
        old, new = f"{rev}^", rev
    elif "--staged" in sys.argv:
        msg = ""
        mf = SVHMP / ".git" / "COMMIT_EDITMSG"
        if mf.exists():
            msg = mf.read_text(encoding="utf-8", errors="replace")
        for i, a in enumerate(sys.argv):
            if a == "--msg":
                msg = sys.argv[i + 1]
        old, new = "HEAD", None
    else:
        print(__doc__)
        return 2

    has_claim, mism = check(msg, old, new)
    if not has_claim:
        print("[claim-check] khong co style/no-logic claim — bo qua")
        return 0
    if not mism:
        print("[claim-check] OK — moi file .py TUONG DUONG AST (dung la format thuan)")
        return 0
    print(f"[claim-check] ⚠️ commit khai 'no-logic/style' NHUNG {len(mism)} file doi AST:")
    for f, why in mism:
        print(f"   ⚠️ {f} — {why}")
    print("   → doi nhan commit (refactor/feat/fix) HOAC tach commit style rieng.")
    return 1 if strict else 0


if __name__ == "__main__":
    sys.exit(main())
