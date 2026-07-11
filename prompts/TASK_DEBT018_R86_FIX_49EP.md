# TASK — Sửa vi phạm R86 (EOL diacritic) cho 49 tập EP02-50 trước khi bật DEBT-018 Giai đoạn 2

> Viết bởi CMD_AUDIT 11/7, sau khi Mr.Long xác nhận hướng (không waiver, không regen toàn bộ).
> Nguồn: `reports/DEBT018_R197_PHASE1_LOG_ONLY_REPORT.md` (Giai đoạn 1 LOG-ONLY, CMD_BUILD 11/7).

## Bối cảnh (đọc kỹ trước khi làm)

`tools/qa_eol_diacritic.py` (R86) là **hardlock kỹ thuật thật của Mr.Long** (29/6): cấm câu kết thúc
bằng từ mang dấu **ngã/nặng/hỏi** — lý do: BigVGAN (vocoder TTS) không model chính xác glottal stop ở
3 dấu này, gây **âm cụt/hụt hơi/lệch tone** khi render thật. Đây KHÔNG phải rule quá nghiêm — mỗi vi
phạm là 1 rủi ro chất lượng audio thật nếu tập được render nguyên trạng.

49 tập EP02-50 **chưa từng render TTS thật** (0/49 có `spec.json`) — nên đây là thời điểm rẻ nhất để
sửa (trước khi tốn công TTS/audio QA). Trung bình mỗi tập có **~38 vi phạm R86** (min 25 ep_32, max 53
ep_07) — xem bảng đầy đủ trong report gốc.

## Việc cần làm

Với MỖI tập EP02-50 (49 tập):

1. Chạy `python tools/qa_eol_diacritic.py output/ep_NN/episode.md` lấy danh sách dòng vi phạm (số dòng
   + từ cuối câu mang dấu ngã/nặng/hỏi).
2. Với MỖI câu vi phạm — sửa **CHỈ phần đuôi câu** để từ cuối cùng không còn mang 1 trong 3 dấu đó:
   - Ưu tiên: **đảo trật tự từ** trong câu (đưa từ mang dấu ra giữa câu, không phải cuối).
   - Nếu không đảo được tự nhiên: **thêm trợ từ/từ đệm cuối câu** phù hợp văn phong đang dùng trong
     tập đó (vd "nhé", "đấy", "thôi", "rồi" — tuỳ ngữ cảnh, KHÔNG dùng máy móc 1 từ cho tất cả).
   - **TUYỆT ĐỐI KHÔNG đổi nghĩa câu, KHÔNG đổi thông tin/plot/tên riêng/vật phẩm/địa danh** — chỉ sửa
     cấu trúc câu để đổi từ kết thúc. Đây là sửa NGỮ ÂM, không phải biên tập nội dung.
   - Nếu 1 câu THỰC SỰ không thể sửa mà không đổi nghĩa (hiếm, vd tên riêng/thuật ngữ cố định mang dấu
     đó) — ghi log lại case đó riêng, KHÔNG tự ý bỏ qua âm thầm, báo cáo cho Mr.Long quyết (waiver
     từng câu cụ thể, không phải waiver cả tập).
3. Sau khi sửa hết 1 tập — chạy lại `qa_eol_diacritic.py` xác nhận **0 vi phạm**, rồi chạy full
   `FULL_TEXT_GATE`/`svhmp_preflight_qa.py` cho tập đó xác nhận không phát sinh lỗi mới ngoài R86 (chỉ
   cần xác nhận R86 sạch — các rule khác không thuộc phạm vi task này).
4. Chạy `tests/test_g3_dialogue.py` hoặc test liên quan tập đó (nếu có) xác nhận không phá vỡ gì khác.

## Ràng buộc

- **KHÔNG động vào EP01** (golden/locked, đã sạch R86 — không cần sửa).
- **KHÔNG regen/viết lại nội dung** — chỉ sửa câu kết mang vi phạm R86. Nếu thấy cám dỗ "viết lại cho
  hay hơn" — KHÔNG làm, ngoài phạm vi task.
- 49 tập là khối lượng lớn — **không cần làm hết 1 lần**, báo tiến độ theo `log_ping.py` sau mỗi vài
  tập (vd mỗi 10 tập), không đợi cả 49 tập xong mới báo.
- Domain các file `output/ep_NN/episode.md` — kiểm `governance/architecture_registry.yaml`
  `ownership_matrix` trước khi sửa (nếu thuộc domain đã LOCKED, cần TU CHỈNH đúng mẫu — nhưng
  `episode.md` là NỘI DUNG SẢN XUẤT, không phải code/schema, nên khả năng cao KHÔNG cần TU CHỈNH
  registry, chỉ cần xác nhận qua `git log` không phạm R197 FULL_TEXT_GATE khi commit — chạy
  `tools/svhmp_preflight_qa.py` local trước khi commit từng tập, đúng tinh thần R197 dù chưa Giai
  đoạn 2 chặn máy).
- `output/ep_NN/episode_tts_ready.md` (nếu tồn tại cho tập đó) cũng cần đồng bộ sửa theo (2 file phải
  khớp nội dung — xem tiền lệ DEBT-001 intro retrofit đã xử lý case lệch 2 file này).

## DoD

- 49/49 tập EP02-50: `qa_eol_diacritic.py` báo **0 vi phạm**.
- Chạy lại batch preflight (`scratchpad/debt018_batch_preflight.py` nếu còn, hoặc tương đương) xác
  nhận **0/50 tập** còn bị chặn bởi R86 riêng (không tính R1/R5/R10/R17 — ngoài phạm vi task này).
- Registry 0/0/0, pytest xanh không giảm baseline.
- Cập nhật `governance/TECH_DEBT.md` DEBT-018: ghi rõ 49 tập đã sạch R86, sẵn sàng cho Mr.Long xem
  xét bật Giai đoạn 2 (chặn thật) — **KHÔNG tự ý bật Giai đoạn 2**, đó vẫn là quyết định riêng.

## THAM CHIẾU
`reports/DEBT018_R197_PHASE1_LOG_ONLY_REPORT.md` (bảng đầy đủ vi phạm/tập), `governance/TECH_DEBT.md`
DEBT-018, `tools/qa_eol_diacritic.py` (docstring giải thích lý do kỹ thuật).
