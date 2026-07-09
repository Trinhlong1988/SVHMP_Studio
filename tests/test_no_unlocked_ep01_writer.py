"""ENFORCEMENT — chặn DEBT-005 tái diễn (vòng 3, per TASK_DEBT005_ENFORCEMENT_ROUND3.md).

Đây là phần "quy trình" Mr.Long yêu cầu: KHÔNG chỉ vá instance, mà làm 1 test tĩnh để lớp lỗi
"ghi output/ep_01/episode.md THẬT mà không có golden_lock" KHÔNG THỂ lọt qua lần thứ 4. Nếu test
này chạy từ vòng 1 đã bắt được cả 7+ file writer ngay.

CƠ CHẾ (quét TĨNH, không chạy subprocess):
  1. Glob tests/**/*.py + tools/*.py.
  2. Trong mỗi file, tìm BIẾN trỏ đường dẫn ep_01 THẬT — dòng gán `VAR = ...` mà RHS (sau khi bỏ
     dấu nháy) chứa `ep_01/episode.md` hoặc `ep_01/episode_tts_ready.md`. Cách này bắt cả literal
     đầy đủ ("output/ep_01/episode.md") lẫn ghép mảnh (REPO/"output"/"ep_01"/"episode.md"), NHƯNG
     KHÔNG bắt biến tempfile (tmp_ep_dir/"episode.md" — không có "ep_01/" liền kề sau bỏ nháy).
  3. File "ghi ep_01 thật" nếu có `VAR.write_text(`, `VAR.write_bytes(`, `open(VAR, 'w'|'a')`, hoặc
     `shutil.copy/copy2/move/copyfile(..., VAR)` với VAR là biến ở bước 2.
  4. File ghi ep_01 thật BẮT BUỘC có `golden_lock` xuất hiện trong chính file — nếu không → FAIL,
     in RÕ TÊN file (không chỉ đếm số).

WHITELIST tường minh (không phải "khớp assert là lọt"): chỉ công cụ SỬA NỘI DUNG THỦ CÔNG chạy 1
lần bằng cờ `--apply` (KHÔNG phải test tự chạy lặp trong pytest suite → không nằm trong nguồn đụng độ
concurrent-pytest mà golden_lock sinh ra để chặn). Thêm file mới vào whitelist BẮT BUỘC sửa constant
này (tự nó là 1 lớp cảnh báo — không để danh sách trắng mở).
"""
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Công cụ sửa nội dung THỦ CÔNG (--apply), 0 caller tự động, không chạy trong pytest suite.
# Mỗi file đã có cảnh báo concurrent trong docstring (điều kiện được miễn golden_lock theo task).
_MANUAL_TOOL_EXCEPTION = {
    # Ghi trực tiếp EP01 1 lần thủ công, không tự restore (task ROUND3 nêu đích danh là ngoại lệ).
    "tools/rewrite_ep01_final.py",
    # Batch-apply text fix từ bible/35 qua cờ --apply; 0 caller tự động (chỉ test import verify_post_fix
    # vốn đã cô lập tempfile). main() ghi EPISODE+GOLDEN thật — writer thứ 8 tìm thêm ở vòng 3 (R9).
    "tools/text_batch_fix.py",
}

_EP_REAL_TOKENS = ("ep_01/episode.md", "ep_01/episode_tts_ready.md")
# Bỏ file test NÀY khỏi scan (nó chứa token ep_01 trong regex/whitelist, không phải writer thật).
_SELF = "tests/test_no_unlocked_ep01_writer.py"

_ASSIGN_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*=\s*(.+)$")


def _rel(p: Path) -> str:
    return str(p.relative_to(REPO)).replace("\\", "/")


def _real_ep01_vars(src: str):
    """Tên biến được gán đường dẫn ep_01 THẬT (không phải tempfile)."""
    vars_ = set()
    for line in src.splitlines():
        m = _ASSIGN_RE.match(line)
        if not m:
            continue
        var, rhs = m.group(1), m.group(2)
        rhs_noquote = rhs.replace('"', "").replace("'", "")
        if any(tok in rhs_noquote for tok in _EP_REAL_TOKENS):
            vars_.add(var)
    return vars_


def _writes_real_ep01(src: str, vars_) -> bool:
    for v in vars_:
        ev = re.escape(v)
        # 1. method ghi truc tiep tren bien:  EPISODE.write_text(...) / .write_bytes(...)
        if re.search(rf"\b{ev}\.write_(?:text|bytes)\(", src):
            return True
        # 2. open(VAR, 'w'|'a')
        if re.search(rf"\bopen\(\s*{ev}\b[^)]*['\"][wa]", src):
            return True
        # 3. shutil copy/move VAO bien (bien la dich - doi so cuoi): shutil.copy(src, EPISODE)
        if re.search(rf"\bshutil\.(?:copy|copy2|copyfile|move)\([^)]*,\s*{ev}\b", src):
            return True
        # 4. os.replace/os.rename VAO bien (atomic move dich): os.replace(tmp, EPISODE)
        if re.search(rf"\bos\.(?:replace|rename)\([^)]*,\s*{ev}\b", src):
            return True
        # 5. helper ghi atomic goi voi bien la doi so dau: _atomic_write(EPISODE, text) / save_x(EPISODE,...)
        #    (ham co 'write'/'save' trong ten -> ghi; reader khong dat ten kieu nay). Bat lop
        #    tmp+os.replace an trong helper ma buoc 1-4 khong thay truc tiep tren VAR.
        if re.search(rf"\b\w*(?:write|save)\w*\(\s*{ev}\b", src):
            return True
    return False


def _classify(rel: str, src: str) -> str:
    """Phân loại 1 file: 'none' (không ghi ep01 thật) / 'whitelisted' / 'guarded' / 'offender'.
    Hàm THUẦN (chỉ phụ thuộc rel+src) để mutation-proof gọi trực tiếp được."""
    vars_ = _real_ep01_vars(src)
    if not vars_ or not _writes_real_ep01(src, vars_):
        return "none"
    if rel in _MANUAL_TOOL_EXCEPTION:
        return "whitelisted"
    if "golden_lock" in src:
        return "guarded"
    return "offender"


def _scan():
    """Trả về (offenders, guarded, whitelisted) — offenders = ghi ep01 thật mà thiếu golden_lock."""
    files = sorted(set(REPO.glob("tests/**/*.py")) | set(REPO.glob("tools/*.py")))
    offenders, guarded, whitelisted = [], [], []
    for f in files:
        rel = _rel(f)
        if rel == _SELF:
            continue
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        bucket = _classify(rel, src)
        if bucket == "offender":
            offenders.append(rel)
        elif bucket == "guarded":
            guarded.append(rel)
        elif bucket == "whitelisted":
            whitelisted.append(rel)
    return offenders, guarded, whitelisted


def test_no_unlocked_ep01_writer():
    """Mọi file ghi output/ep_01/episode(_tts_ready).md THẬT phải có golden_lock (trừ whitelist manual)."""
    offenders, guarded, whitelisted = _scan()
    assert offenders == [], (
        "DEBT-005 tái diễn — file ghi output/ep_01 THẬT mà THIẾU golden_lock (cross-process):\n  "
        + "\n  ".join(offenders)
        + "\n=> bọc đoạn đọc-ghi-restore trong `with golden_lock():` (mẫu tests/cases/test_forbidden_phrases.py) "
        "hoặc thêm vào _MANUAL_TOOL_EXCEPTION nếu là công cụ --apply thủ công (kèm cảnh báo docstring)."
    )
    # Sanity: phải thật sự có writer được canh giữ — nếu 0, heuristic hỏng (không bắt được gì).
    assert len(guarded) >= 7, (
        f"chỉ thấy {len(guarded)} file có golden_lock — kỳ vọng >=7 (6 tests/cases + generate_dataset). "
        f"Heuristic có thể vỡ (không nhận diện được writer thật): guarded={guarded}"
    )


def test_whitelist_is_closed_and_justified():
    """Whitelist chỉ gồm công cụ thủ công đã biết — chống 'danh sách trắng mở'."""
    assert _MANUAL_TOOL_EXCEPTION == {
        "tools/rewrite_ep01_final.py",
        "tools/text_batch_fix.py",
    }, "whitelist đổi — mọi thay đổi phải có review + cảnh báo docstring trong tool tương ứng"
    # Whitelist phải trỏ file THẬT tồn tại (không để entry chết che giấu writer đã xóa/đổi tên).
    for rel in _MANUAL_TOOL_EXCEPTION:
        assert (REPO / rel).exists(), f"whitelist trỏ file không tồn tại: {rel}"


def test_enforcement_detects_mutation():
    """MUTATION PROOF — với TỪNG file trong 7 file đã vá, gỡ golden_lock khỏi source → _classify PHẢI
    lật từ 'guarded' sang 'offender'. Chứng minh test THẬT SỰ bắt được (không phải test rỗng luôn xanh)."""
    seven = [
        "tests/cases/test_action_repeat.py",
        "tests/cases/test_anti_generic.py",
        "tests/cases/test_fact_contradiction.py",
        "tests/cases/test_name_repetition.py",
        "tests/cases/test_object_state.py",
        "tests/cases/test_tts_pause.py",
        "tests/regression/generate_dataset.py",
    ]
    for rel in seven:
        src = (REPO / rel).read_text(encoding="utf-8", errors="replace")
        assert _classify(rel, src) == "guarded", f"tiền đề: {rel} phải đang 'guarded' (có golden_lock)"
        mutated = re.sub(r".*golden_lock.*\n?", "", src)  # gỡ mọi dấu vết golden_lock (chỉ trong bộ nhớ)
        assert "golden_lock" not in mutated
        assert _classify(rel, mutated) == "offender", (
            f"MUTATION không bị bắt: gỡ golden_lock khỏi {rel} nhưng _classify vẫn không ra 'offender' "
            "— enforcement test rỗng, không bảo vệ được gì"
        )
