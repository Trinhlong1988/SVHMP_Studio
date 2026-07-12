# TASK — DEBT-036: siết `DRIVER_QUOTE_PATTERN` chống bắt nhầm lời hành khách thành lời bác tài

> Viết bởi CMD_AUDIT 12/7, per Mr.Long "làm đúng vai trò fix sạch lỗi". Đây là fix 1 bug kỹ thuật
> trong tool audit (`tools/audit_hidden_bugs.py`), KHÔNG phải nội dung episode — không đụng
> `output/ep_*/episode.md`.

## Bối cảnh (đã xác nhận thật, xem `governance/TECH_DEBT.md` DEBT-036 + phản biện đối kháng 12/7)

`DRIVER_QUOTE_PATTERN` (dòng 46-48):
```python
DRIVER_QUOTE_PATTERN = re.compile(
    r'Bác tài[^\n.]*?(?:cất lời|nói|đáp|bảo|hỏi|tiếp|liếc gương)[^"]*?"([^"]+)"'
)
```
Phần `[^"]*?"` SAU từ khóa kích hoạt được phép băng qua NEWLINE + dấu chấm để tìm dấu `"` gần nhất
— khi câu có từ khóa nhưng KHÔNG có quote ngay sau (vd `"Bác tài liếc gương. Không nói."` —
`output/ep_15/episode.md` dòng 93), regex nhảy tới quote GẦN NHẤT phía sau, kể cả khi đó là lời
hành khách.

**QUAN TRỌNG — đã phản biện đối kháng, phạm vi RỘNG HƠN ban đầu tưởng, và phương án regex đơn giản
ĐÃ BỊ BÁC BỎ, đọc kỹ trước khi làm:**
- Phạm vi ảnh hưởng thật KHÔNG phải chỉ EP15/25/35/45 — chạy thử regex gốc trên toàn bộ 50 tập cho
  thấy hình dạng lỗi này (bắt nhầm quote phản ứng ngắn của hành khách như `"Tôi..."`, `"Mẹ..."`)
  xuất hiện ở **khoảng 43/50 tập**. Bước 1 dưới đây phải tự đo lại con số CHÍNH XÁC, không dùng số
  này làm chốt cuối (chỉ là ước lượng ban đầu để biết quy mô thật của việc cần làm).
- Phương án sửa `[^"]*?` → `[^".\n]*?` (cấm băng chấm/newline) đã bị THỬ TRÊN DỮ LIỆU THẬT và BỊ BÁC
  BỎ: corpus dùng idiom chuẩn `Bác tài [từ khóa].\n\n"quote"` (có CẢ dấu chấm VÀ xuống dòng đoạn giữa
  từ khóa và quote hợp lệ) — cấm cả 2 ký tự đó làm mất match ở ~46/50 tập, tức làm mù công cụ thay vì
  sửa bug. **KHÔNG dùng phương án này.**
- Phương án chặt hơn `[.:\s]*"` (chỉ cho phép dấu chấm/hai chấm/khoảng trắng, không cho từ ngữ nào
  khác) sửa đúng case EP15 nhưng lại làm mất 1 quote bác tài THẬT ở EP11 (`"Bác tài liếc gương — lần
  này dừng trên người đàn ông lâu hơn thường lệ nhiều."` rồi mới tới quote thật — có cụm mô tả dài
  cùng hình dạng với case lỗi). **Không có regex character-class đơn giản nào phân biệt được "cụm mô
  tả hợp lệ trước quote thật" với "bug: nhảy qua nhiều đoạn tới quote không liên quan" — CHỈ dựa vào
  độ dài/loại ký tự.**
- **Do đó hướng khuyến nghị CHÍNH (không phải phương án dự phòng) là track SPEAKER gần nhất**: với
  mỗi quote trong văn bản, xác định đoạn văn/câu dẫn NGAY TRƯỚC nó có nhắc "Bác tài" (hoặc từ khóa
  kích hoạt) hay nhắc tên/đại từ nhân vật khác — chỉ tính quote đó là của bác tài nếu đoạn dẫn ngay
  trước KHÔNG có tên/dấu hiệu speaker khác chen vào giữa. Cách làm cụ thể (gợi ý, không bắt buộc
  nguyên văn): quét TOÀN BỘ vị trí quote trong văn bản theo thứ tự, với mỗi quote tìm đoạn text
  ngay trước nó (tới quote/xuống-dòng-kép trước đó), nếu đoạn đó chứa cụm kích hoạt bác tài (không bị
  chen bởi câu có chủ ngữ khác + động từ nói năng) → gán cho bác tài.
- **EP1 (và có thể vài tập sớm khác) dùng văn phong thoại gạch đầu dòng (`— Con đã nhớ ra chưa?`)
  KHÔNG dùng dấu `"..."` — regex nào cũng KHÔNG thấy được các tập này.** Đây là giới hạn TỒN TẠI SẴN
  của cả 2 pattern cũ/mới, KHÔNG phải lỗi của fix này — KHÔNG được báo cáo "0 quote match" ở các tập
  này là "đã fix", ghi rõ đây là out-of-scope/known-blind-spot trong TECH_DEBT.md, không tự mở rộng
  regex để bắt cả 2 kiểu (việc đó là thay đổi phạm vi lớn hơn, cần task riêng nếu Mr.Long muốn).

Phần TRƯỚC từ khóa (`Bác tài[^\n.]*?keyword`) đã ĐÚNG (giới hạn cùng câu, không băng chấm/newline)
— chỉ cần sửa phần SAU.

## Việc cần làm

### Bước 1 — Đo baseline THẬT trên toàn bộ 50 tập trước khi sửa

Chạy `driver_extra_overuse_flag()` hiện tại trên `output/ep_01..ep_50/episode.md` (dùng đúng hàm có
sẵn, không viết lại), ghi lại: EP nào bị flag, bao nhiêu "extras" mỗi EP, nội dung quote đó (2 dòng
context quanh mỗi quote để xác định bằng mắt: đây là lời bác tài thật hay lời nhân vật khác bị bắt
nhầm). Đây là bằng chứng "before" — lưu vào file tạm (vd `runtime/debt036_before.json`, không commit
nếu chỉ là working file, hoặc ghi vào phần bằng chứng của TECH_DEBT.md nếu súc tích).

### Bước 2 — Xây fix theo hướng speaker-tracking (xem Bối cảnh ở trên), TỰ KIỂM bằng dữ liệu thật

KHÔNG dùng 2 phương án regex character-class đã bị bác bỏ ở trên. Xây cơ chế xác định speaker gần
nhất trước mỗi quote (gợi ý cách làm trong Bối cảnh). Test bắt buộc trên CẢ 2 case đối chứng đã xác
nhận qua phản biện đối kháng, TRƯỚC KHI chạy full 50 tập:
- `output/ep_15/episode.md` dòng ~93-107 (case lỗi: "Bác tài liếc gương. Không nói." rồi tới quote
  hành khách "Tôi...") → SAU fix, quote đó KHÔNG được gán cho bác tài.
- `output/ep_11/episode.md` (case dễ vỡ: "Bác tài liếc gương — lần này dừng... nhiều." rồi mới tới
  quote thật của bác tài) → SAU fix, quote thật VẪN PHẢI được gán đúng cho bác tài (không mất true
  positive).

Nếu cách làm speaker-tracking vẫn không xử lý đúng CẢ 2 case trên, tiếp tục điều chỉnh logic (không
quay lại dùng character-class regex đơn giản đã bị bác bỏ) — có thể cần thêm danh sách từ khóa nhận
diện speaker khác (tên riêng, "hành khách", đại từ nhân xưng ngôi nhất kèm động từ nói) để phân biệt.

Sau khi 2 case đối chứng PASS, chạy trên TOÀN BỘ 50 tập — so sánh "after" với "before" (Bước 1): mọi
quote KHÔNG còn bị bắt phải do quote đó THẬT SỰ không thuộc bác tài (đọc bằng mắt xác nhận mẫu, không
chỉ tin đếm số giảm).

### Bước 3 — Đo lại tác động thật lên kết quả hiện có

`driver_extra_overuse_flag()` đang được dùng trong `[3]` (audit_hidden_bugs.py) — chạy lại full audit
sau khi sửa, so sánh danh sách EP bị flag trước/sau (Bước 1 vs sau fix). Ghi rõ trong TECH_DEBT.md
DEBT-036 số EP nào ĐỔI trạng thái (từ flag → không flag, hoặc ngược lại nếu có) kèm bằng chứng.
KHÔNG đổi ngưỡng `>1` trong `driver_extra_overuse_flag()`/`should_flag` logic — chỉ sửa regex đầu
vào; nếu sau khi sửa regex mà ngưỡng `>1` không còn hợp lý nữa (vd giờ 0 EP nào có >1 extras thật),
GHI NHẬN quan sát đó vào TECH_DEBT.md nhưng KHÔNG tự đổi ngưỡng (việc đó thuộc phạm vi task khác).

### Bước 4 — Mutation-proof test

Viết test mới trong `tests/test_audit_hidden_bugs_extra_beat_hook.py` (mở rộng file có sẵn, không
tạo file mới trùng domain) hoặc file test riêng nếu hợp lý hơn:
- Test tái tạo CHÍNH XÁC case lỗi gốc (câu `"Bác tài liếc gương. Không nói."` + quote hành khách
  cách đó vài dòng) → xác nhận SAU fix, `DRIVER_QUOTE_PATTERN`/`split_driver_extra_quotes()` KHÔNG
  bắt quote hành khách đó nữa.
- Test mutation: đảo ngược fix (dùng lại regex cũ) → xác nhận test Ở TRÊN chuyển sang FAIL (chứng
  minh test thật sự bắt được bug, không phải test rỗng).
- Test regression: 1-2 case quote bác tài THẬT hợp lệ (từ dữ liệu thật, vd 1 speech_line chuẩn hoặc
  1 extra_beat_HOOK quote đã biết) vẫn PASS sau fix — không được vô tình làm mất true positive.

## Ràng buộc

- CHỈ sửa `tools/audit_hidden_bugs.py` (regex + docstring liên quan) + file test. KHÔNG đụng
  `output/ep_*/episode.md`, KHÔNG đổi `driver_extra_overuse_flag()` logic ngưỡng `>1`, KHÔNG đụng
  `EXTRA_BEAT_HOOK_EPS`/`milestones.py` (đã đúng, ngoài phạm vi bug này).
- `tools/audit_hidden_bugs.py` KHÔNG nằm trong CI gate (đã tự kiểm — 0 kết quả trong
  `ci_gate.py`/`svhmp_preflight_qa.py`/`qa_skeptic_orchestrator.py`) — đây là audit tool độc lập,
  không chặn production, nhưng vẫn phải sửa đúng vì dùng để báo cáo cho Mr.Long.
- `pytest tests/ -q` + `python tools/architecture_registry_check.py` xanh sau khi sửa.
- Domain của `tools/audit_hidden_bugs.py` theo `governance/architecture_registry.yaml` — kiểm
  ownership trước khi sửa, ghi TU CHỈNH đúng style nếu domain đã locked.

## DoD

Regex fix + bằng chứng before/after trên 50 tập (đọc mắt xác nhận, không chỉ đếm số) + 3 loại test
(repro/mutation/regression) PASS + TECH_DEBT.md DEBT-036 đóng với bằng chứng cụ thể (bao nhiêu EP đổi
trạng thái, vì sao). Registry 0/0/0, pytest xanh.

## THAM CHIẾU
`governance/TECH_DEBT.md` DEBT-036, `tools/audit_hidden_bugs.py` dòng 46-91,
`tests/test_audit_hidden_bugs_extra_beat_hook.py` (mẫu test hiện có để tham khảo idiom).
