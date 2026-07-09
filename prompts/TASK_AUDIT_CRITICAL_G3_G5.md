# TASK — 2 bug CRITICAL từ audit đa-agent 9-10/7 (workflow 222 agent, G2-G8)

> Viết bởi CMD_AUDIT 10/7, sau khi TỰ KIỂM CHỨNG ĐỘC LẬP lại cả 2 (đọc code trực tiếp + 1 mutation
> sống cho #2) — không tin lại kết quả workflow. Cả 2 đã qua 3-skeptic phản biện độc lập trong
> workflow gốc, giờ xác nhận thêm lần nữa bằng tay. Full report: xem artifact audit đã gửi Mr.Long.

## BUG #1 (CRITICAL) — `tools/dialogue_generator.py::write_episode_line()` không có guard chặn ghi đè tập thật

### Bằng chứng đã tự xác nhận
Đọc trực tiếp dòng 214-234: docstring dòng 217 cam kết *"KHÔNG BAO GIỜ trỏ vào 50 tập thật đã
locked"*, nhưng thân hàm **không có 1 dòng guard nào** — `out.write_text(text, encoding='utf-8')`
chạy vô điều kiện. Nếu gọi `write_episode_line(REPO/'output', 5, line)` sẽ ghi đè thật
`output/ep_05/episode.md` (tập đã lock).

**Hiện trạng rủi ro thật (đã tự grep toàn repo):** hiện chỉ có 3 caller — 2 test dùng `tmp_path`
(an toàn), 1 caller production duy nhất (`tools/g3_dialogue_check.py:124`) gọi với
`root=REPO/'output'` + `ep_n='g3_sample'` (chuỗi, an toàn nhờ KỶ LUẬT của caller, không phải do
code chặn). Chưa bị khai thác, nhưng đây đúng lớp lỗi race/overwrite mà DEBT-005 đã xử lý cho
6+ writer khác — hàm này lọt hoàn toàn qua `tests/test_no_unlocked_ep01_writer.py` vì đường dẫn
ghép động bằng f-string, không phải literal `"ep_01/episode.md"` mà regex quét tĩnh tìm.

### Fix bắt buộc
Thêm guard trong `write_episode_line()`: nếu `Path(root).resolve() == (REPO/'output').resolve()`
(tức đang ghi vào thư mục production thật) **VÀ** `ep_n` là số nguyên hoặc chuỗi toàn chữ số (ép
`int()` thành công) → `raise ValueError` rõ ràng ("write_episode_line() KHÔNG được gọi với ep_n số
+ root production — dùng ep_n dạng chuỗi non-numeric cho sandbox, hoặc golden_lock nếu thật sự cần
ghi tập thật"). **KHÔNG đổi hành vi** cho 2 trường hợp đang dùng hợp lệ (tmp_path bất kỳ ep_n nào;
root production + ep_n chuỗi non-numeric) — chỉ chặn đúng tổ hợp nguy hiểm mới.

### Test bắt buộc (mutation-proof, mirror `tests/test_no_unlocked_ep01_writer.py`)
1. Test mới: `write_episode_line(REPO/'output', 5, '...')` phải `raise ValueError` (không được
   tạo file `output/ep_05/...`).
2. Test xác nhận 2 case hợp lệ cũ (`tmp_path` + numeric, production root + string) **vẫn PASS y
   nguyên** — không phá hành vi đang dùng.
3. Mutation-proof: test tự gỡ guard (trong bộ nhớ, đọc source rồi mutate string) → xác nhận nếu
   guard bị revert, `ValueError` không còn raise — chứng minh test thật sự bắt được, không rỗng.

## BUG #2 (CRITICAL) — `tools/supernatural_validator.py::run_all()` composition không có test thật

### Bằng chứng đã tự xác nhận (kể cả tự mutation sống)
Đọc dòng 157-162: `run_all()` cộng dồn kết quả 3 sub-check (`check_typology`,
`check_possession_state_machine`, `check_no_duplicate_compliance_files`). Test DUY NHẤT gọi
`run_all()` là `assert run_all() == []` trên dữ liệu sạch (`tests/test_supernatural_validator.py:30`)
— các test mutation khác (M2/M3/M4/M7) đều gọi THẲNG từng sub-check với dữ liệu giả, KHÔNG qua
`run_all()`.

**Tự chạy thật để xác nhận (không suy đoán):** monkeypatch `run_all` thành hàm rỗng `return []`
trong bộ nhớ → gọi lại → kết quả `[]`, y hệt baseline sạch. Nếu ai vô tình xóa 1/3 hoặc cả 3 dòng
`errs += check_*()` trong code thật, gate `g5_supernatural_check.py` (chạy `run_all()` qua CI) vẫn
báo PASS — đúng lớp lỗi `qa_post_render.audit_pause()` đã bắt ở G8 D3, lần này ở G5 chưa ai vá.

### Fix bắt buộc
Thêm test mới xác nhận **composition thật** của `run_all()` — theo 1 trong 2 cách (ưu tiên cách a):
(a) **Mutation-proof trực tiếp trên nguồn** (mirror `test_enforcement_detects_mutation` của D3):
đọc source `tools/supernatural_validator.py`, xác nhận cả 3 lời gọi `check_typology()` /
`check_possession_state_machine()` / `check_no_duplicate_compliance_files()` đều xuất hiện trong
thân `run_all()`; rồi mutate (trong bộ nhớ) xóa từng lời gọi 1, xác nhận mỗi lần mutate phải làm
mất khả năng propagate lỗi (viết 1 hàm `_run_all_body_ok(src)` thuần tương tự
`_pause_delegation_body_ok` của G8, tái dùng logic, KHÔNG viết lại từ đầu nếu có thể generalize).
(b) **Injection thật qua run_all()**: với ÍT NHẤT 1 case bad-data đã có sẵn trong M2/M3/M4/M7,
dựng lại đúng điều kiện đó nhưng gọi qua `run_all()` (không gọi thẳng sub-check) — xác nhận lỗi
vẫn propagate ra ngoài. Làm cho CẢ 3 sub-check (không phải chỉ 1) để đảm bảo không sub-check nào bị
"quên" trong composition.

## RÀNG BUỘC CHUNG (áp cho cả 2 bug)
- KHÔNG đổi hành vi test/case hiện có — chỉ thêm guard + test mới.
- `python tools/architecture_registry_check.py` phải vẫn PASS 0/0/0 sau khi sửa.
- `pytest tests/ -q` full suite phải xanh, KHÔNG giảm baseline (hiện 616+ passed).
- Bug #2 chạm vào `tools/supernatural_validator.py` — domain `supernatural` (G5), đã LOCKED
  (`g5-supernatural-v1.0`). Đây là TU CHỈNH có ủy quyền (per Mr.Long — audit độc lập phát hiện qua
  workflow đa-agent 9-10/7, mirror mẫu `bp4_runtime`/`bp6_decision`/G8-D3) — commit PHẢI ghi rõ
  "per Mr.Long authorization 10/7" + cập nhật dòng `g5_supernatural: locked` trong
  `governance/architecture_registry.yaml` thêm 1 câu "TU CHINH 10/7" theo đúng mẫu đã dùng.
- Bug #1 chạm `tools/dialogue_generator.py` — domain `dialogue` (G3), đã LOCKED (`dialogue-v1.0`).
  Tương tự — TU CHỈNH có ủy quyền, ghi rõ trong commit + registry.
- Cập nhật `governance/TECH_DEBT.md`: mở 2 mục mới (hoặc phụ lục vào mục gần nhất) ghi nhận 2 bug
  này + trạng thái CLOSED kèm bằng chứng thật sau khi fix xong (không phải "đã sửa là xong" — phải
  có kết quả mutation-proof PASS + pytest full suite xanh).

## DoD
Bug #1: guard raise đúng case nguy hiểm, 2 case hợp lệ cũ không đổi, mutation-proof test PASS ✅.
Bug #2: composition có test thật (mutation-proof hoặc injection qua run_all(), đủ cả 3 sub-check)
✅. Registry 0/0/0, pytest full suite xanh, cả 2 domain LOCKED đã ghi TU CHỈNH đúng mẫu, TECH_DEBT.md
cập nhật với bằng chứng thật ✅.

## THAM CHIẾU
Artifact báo cáo audit đa-agent 222 agent (32 finder × 4 lens, 3-skeptic phản biện) — 9-10/7 · mẫu
mutation-proof: `tests/test_qa_post_render_pause_delegation.py` (D3) ·
`tests/test_no_unlocked_ep01_writer.py` (DEBT-005 vòng 3) · `tools/g8_qa_runtime_check.py::_pause_delegation_body_ok`.
