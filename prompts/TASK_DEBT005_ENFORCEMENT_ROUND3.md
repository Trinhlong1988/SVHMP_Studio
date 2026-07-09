# TASK — DEBT-005 VÒNG 3: vá 7 writer bỏ sót + cưỡng chế máy (chặn tái diễn vĩnh viễn)

> Viết bởi CMD_AUDIT 9/7, sau khi Mr.Long hỏi thẳng "triệt để bug?" — 2 vòng fix trước (5/7, 9/7)
> đều chỉ vá ĐÚNG file đã biết từ báo cáo cũ, không quét toàn diện. Đây là lần thứ 3 lỗi này bị bắt
> lại — theo đúng luật TỐI THƯỢNG (test_process_failure_principle): **không chỉ vá instance, phải
> làm quy trình để lớp lỗi này KHÔNG THỂ lọt qua lần thứ 4.**

## HIỆN TRẠNG (đã tự `grep` + đọc code xác nhận, không suy đoán)

7 file ghi trực tiếp vào `output/ep_01/episode.md` **THẬT** (dùng chung với mọi phiên CMD khác),
theo mẫu: đọc `orig` → ghi đè nội dung test → chạy subprocess check → `finally: restore` — **KHÔNG
CÓ `golden_lock`** bọc quanh, nên 2 phiên `pytest` chạy đồng thời (đã xảy ra thật nhiều lần trong
dự án) có thể corrupt file dùng chung, đúng y hệt lớp lỗi DEBT-005 gốc:

1. `tests/cases/test_action_repeat.py` (đã đọc code xác nhận, `EPISODE.write_text`/`finally`)
2. `tests/cases/test_anti_generic.py` (cùng khuôn mẫu `EPISODE = BASE/"output/ep_01/episode.md"`)
3. `tests/cases/test_fact_contradiction.py` (cùng khuôn mẫu)
4. `tests/cases/test_name_repetition.py` (cùng khuôn mẫu)
5. `tests/cases/test_object_state.py` (cùng khuôn mẫu)
6. `tests/cases/test_tts_pause.py` (đã đọc code xác nhận, cùng khuôn mẫu)
7. `tests/regression/generate_dataset.py` (đã đọc code xác nhận dòng 148-162 — RỦI RO CAO HƠN: backup
   bằng `shutil.copy` tên **CỐ ĐỊNH** `.md.posverify_bak`, không PID/random — 2 tiến trình chạy cùng
   lúc có thể giẫm backup của nhau, không chỉ giẫm `episode.md`)

**Phụ, khác loại (không tính vào 7, xử lý riêng nếu cần):** `tools/rewrite_ep01_final.py` — công cụ
sửa nội dung 1 lần thủ công (không tự restore), ghi trực tiếp EP01 thật không khóa. Nếu ai chạy tool
này trong lúc có phiên khác đang test, vẫn có thể đụng độ — ghi chú cảnh báo trong docstring tool là
đủ (không bắt buộc golden_lock vì đây không phải test tự động chạy lặp lại).

## D1 — Vá 7 file (mirror ĐÚNG pattern đã dùng, không tự sáng tác API mới)

Mẫu chuẩn đã có trong `tests/cases/test_forbidden_phrases.py` (dòng 20, 44-46):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # tests/
from _golden_lock import golden_lock

# bọc TOÀN BỘ khối đọc-orig → ghi-đè → chạy-check → finally-restore trong 1 khối:
with golden_lock():
    orig = EPISODE.read_text(encoding="utf-8")
    EPISODE.write_text(text, encoding="utf-8")
    try:
        ...
    finally:
        EPISODE.write_text(orig, encoding="utf-8")
```
Với 6 file `tests/cases/test_*.py` (1-6): bọc `with golden_lock():` quanh toàn bộ thân hàm `case()`
(từ dòng đọc `orig` tới hết `finally`). Với `generate_dataset.py` (7): bọc quanh khối
`shutil.copy`+`write_text`+restore tương ứng — VÀ đổi tên backup từ cố định `.md.posverify_bak`
sang có PID (`f".md.posverify_bak.{os.getpid()}"`) làm lớp phòng thủ thứ 2 (golden_lock đã đủ
nhưng tên cố định vẫn là code smell nên sửa luôn, rẻ).

**KHÔNG đổi logic test/assert nào khác** — chỉ thêm khóa quanh đúng đoạn đụng file thật.

## D2 — Enforcement test (QUAN TRỌNG NHẤT — đây là phần "quy trình" Mr.Long yêu cầu, không phải vá xong là thôi)

Viết `tests/test_no_unlocked_ep01_writer.py` (hoặc thêm vào `tests/test_golden_ep01_write_safety_reality_anchor.py`
nếu hợp lý hơn) — quét TĨNH (không cần chạy subprocess):
1. Glob toàn bộ `tests/**/*.py` + `tools/*.py`.
2. Với mỗi file, nếu source chứa pattern ghi (`\.write_text\(` hoặc `open\([^)]*['"]w`) **VÀ** file
   đó có tham chiếu tới `output/ep_01/episode.md` hoặc `output/ep_01/episode_tts_ready.md` (đường dẫn
   thật, không phải biến trỏ tempfile/sandbox) → file đó **BẮT BUỘC** phải có `golden_lock` xuất
   hiện trong cùng file (grep `golden_lock` trong nội dung file).
3. Bất kỳ file nào khớp điều kiện ghi-vào-ep01-thật mà KHÔNG có `golden_lock` → test FAIL, in rõ tên
   file (không chỉ đếm số).
4. **Whitelist tường minh** (không phải "khớp assert là lọt"): `tools/rewrite_ep01_final.py` (đã ghi
   chú lý do ở D1) là ngoại lệ DUY NHẤT được phép, khai rõ trong 1 constant `_MANUAL_TOOL_EXCEPTION`
   ở đầu file test — không để danh sách trắng mở, ai thêm file mới vào whitelist phải sửa code test
   (tự nó là 1 lớp cảnh báo).
5. Test này chính là thứ SẼ bắt được đúng lỗi vừa tìm (nếu chạy sớm hơn đã bắt được 7 file này ngay
   từ vòng 1) — mirror tinh thần "regression test cho chính class bug, không chỉ cho instance".

## RÀNG BUỘC
- KHÔNG sửa `tests/_golden_lock.py` (đã đúng, đã có PROOF concurrency thật từ vòng 2 — không cần
  viết lại cơ chế lock, chỉ áp dụng nó rộng hơn).
- KHÔNG đổi hành vi test hiện có (assert cũ phải y nguyên) — chỉ thêm khóa.
- Chạy full `pytest tests/ -q` sau khi xong — pass count phải KHÔNG giảm so với baseline hiện tại
  (601 passed + 8 skipped, theo audit G8 gần nhất), CỘNG thêm 1 test mới (enforcement) PASS.
- Ghi cập nhật `governance/TECH_DEBT.md` DEBT-005: đổi trạng thái từ "OPEN (RE-OPENED vòng 3)" sang
  "CLOSED vòng 3" kèm bằng chứng thật (không phải "đã sửa là xong" — phải có kết quả enforcement
  test PASS + pytest full suite xanh).

## DoD
D1: 7/7 file có `golden_lock` bọc đúng đoạn ghi-thật, hành vi test cũ không đổi ✅ · D2: enforcement
test tồn tại, tự chạy PASS trên trạng thái đã vá, và **tự FAIL nếu mutate xóa `golden_lock` khỏi 1
trong 7 file** (mutation battery tối thiểu 1 đòn để chứng minh test thật sự bắt được, không phải
test rỗng) ✅ · pytest full suite xanh, không giảm baseline ✅ · TECH_DEBT.md DEBT-005 cập nhật CLOSED
vòng 3 với bằng chứng thật ✅.

## THAM CHIẾU
`tests/_golden_lock.py` (cơ chế lock, KHÔNG sửa) · `tests/cases/test_forbidden_phrases.py` (mẫu
dùng đúng, dòng 20/44-46) · `governance/TECH_DEBT.md` DEBT-005 (lịch sử đầy đủ 3 vòng) ·
CLAUDE.md TỐI THƯỢNG (test_process_failure_principle).
