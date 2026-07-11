# TASK — Quét toàn diện: đối chiếu MỌI lời khẳng định "BẮT BUỘC/CẤM/PHẢI" trong CLAUDE.md + bible/*.yaml với enforcer máy thật

> Viết bởi CMD_AUDIT 11/7. Nguồn gốc: sau khi phát hiện R197 (DEBT-018, `svhmp_v13_render.py` chỉ
> gọi 1 tool dù CLAUDE.md nói "FULL stack, không ngoại lệ") và ngay sau đó thử lại đúng phương pháp
> cho R210 — trúng ngay lần 2 (`bible/37` nói "Voice Profile + Relationship Graph = BẮT BUỘC... completeness
> gate", nhưng `dialogue_generator.py::Tier1IncompleteError` chỉ thực chặn nhóm `voice`, 6/7 nhóm còn
> lại — kể cả `relationships` được gọi "BẮT BUỘC" ngang hàng — KHÔNG có cổng chặn nào). 2/2 lần thử
> đều trúng → đủ tín hiệu đây là lớp lỗi **có hệ thống**, cần quét hết chứ không dò tay từng cái.

## Phương pháp (đã 2 lần chứng minh hiệu quả — dùng lại nguyên xi, không phát minh lại)

Với MỖI câu chứa từ khoá khẳng định ("BẮT BUỘC", "CẤM", "KHÔNG BAO GIỜ", "PHẢI", "TUYỆT ĐỐI",
"0 ngoại lệ"/"không ngoại lệ") trong `CLAUDE.md` hoặc `bible/*.yaml`:

1. Xác định **rõ đối tượng** câu đó áp lên cái gì (1 field, 1 hành vi, 1 luồng xử lý...).
2. Grep/đọc trực tiếp code — tìm hàm/gate THẬT được cho là enforce câu đó.
3. Đọc kỹ hàm đó: nó có kiểm **ĐỦ phạm vi** câu khẳng định nói, hay chỉ kiểm **1 phần** (như R197 chỉ
   1/N tool, R210 chỉ 1/7 nhóm field)?
4. **CHẠY THẬT** để xác nhận (không suy đoán) — vd tạo case vi phạm giả, gọi hàm, xem có chặn không.
5. Phân loại kết quả:
   - **SẠCH** — enforcer thật, đủ phạm vi. Ghi 1 dòng xác nhận, không cần sửa.
   - **THIẾU ENFORCER** — có claim, KHÔNG có gate nào cả. Đúng lớp R215 "chưa có enforcer" → ghi
     TECH_DEBT.md, KHÔNG tự vá (rủi ro sai phạm vi).
   - **ENFORCER HẸP HƠN CLAIM** (lớp R197/R210) — có gate nhưng chỉ che 1 phần phạm vi đã tuyên bố.
     Đây là loại NGUY HIỂM NHẤT (tạo cảm giác an toàn giả) — ưu tiên báo cáo trước.

## Phạm vi quét

- `CLAUDE.md` — toàn bộ block "TỐI THƯỢNG" (R196, R197 [đã xử lý riêng DEBT-018, KHÔNG lặp lại],
  R_SUPREME R1-R10, R200, R210 [đã tìm 1 gap, tiếp tục soi phần còn lại], R211, R215).
- `bible/*.yaml` — 40 file, trong đó **12 file có chứa từ khoá khẳng định** (đã tự grep xác nhận):
  chạy `grep -lE "BẮT BUỘC|CẤM |KHÔNG BAO GIỜ|PHẢI " bible/*.yaml` để lấy danh sách chính xác tại thời
  điểm làm (danh sách có thể đổi nếu bible cập nhật).
- **KHÔNG cần quét lại** R197 (đã có DEBT-018 riêng) — tránh trùng việc.

## Ràng buộc

- Đây là bible/CLAUDE.md — nhiều file SIGNED/TỐI THƯỢNG. **KHÔNG tự sửa bible hay CLAUDE.md** dù tìm
  ra gap — chỉ ghi nhận vào `TECH_DEBT.md` theo đúng mẫu DEBT-018 (mô tả + bằng chứng chạy thật +
  2 hướng: (a) xây enforcer đủ phạm vi, hay (b) sửa lời khai khớp thực tế) — Mr.Long chọn hướng qua
  CMD_AUDIT như đã làm với DEBT-018/020/021/023.
- KHÔNG cần quét hết 1 lượt — báo tiến độ theo `log_ping.py` sau mỗi vài file, không đợi xong hết.
- `pytest tests/ -q` + `architecture_registry_check.py` phải vẫn xanh (việc này chủ yếu là ĐỌC +
  GHI TECH_DEBT.md, không sửa logic — không nên làm hỏng gì).

## DoD
Mỗi câu khẳng định trong phạm vi quét có 1 trong 3 kết quả (SẠCH / THIẾU ENFORCER / ENFORCER HẸP HƠN
CLAIM) kèm bằng chứng chạy thật. Case "ENFORCER HẸP HƠN CLAIM" được ưu tiên báo cáo ngay khi tìm thấy
(không đợi quét hết mới báo), theo đúng mẫu DEBT-018/DEBT tương ứng.

## THAM CHIẾU
`governance/TECH_DEBT.md` DEBT-018 (R197, mẫu chuẩn cho case "enforcer hẹp hơn claim").
R215 (`CLAUDE.md`) — nguyên tắc gốc "rule phải có enforcer máy".
