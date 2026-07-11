# DEBT-023 — Rà tay 50 tập (ep_01..ep_50) theo HB01/HB02 + sensitivity tier

> CMD_BUILD_2, 2026-07-11, per Mr.Long giao (ping 08:51, claim `debt_020_021_023`).
> Tiêu chí: `governance/blueprint/bp9/content_policy.yaml` (HB01/HB02 + sensitivity_tiers + disclaimer_rule).
> Phương pháp: 5 subagent đọc read-only toàn văn 50 tập (10 tập/agent) + CMD_BUILD_2 tự verify tận tay
> 4 tập tier=HIGH (tôn giáo thật) + grep độc lập disclaimer/solicitation toàn bộ 50 tập.
> **KHÔNG xây `publish_gate.py` tự động** (đúng phạm vi Mr.Long giao — chỉ rà + báo cáo).

## KẾT LUẬN NGẮN
- **HB01 (mô tả nghi thức đủ chi tiết để làm theo thật): 0 vi phạm / 50 tập.**
- **HB02 (thông tin liên hệ/tài khoản/tổ chức thật kêu gọi đóng góp): 0 vi phạm / 50 tập.**
- **→ Hai lằn ranh cứng pháp lý (Nghị định 38/2021 Điều 14 + Điều 320 BLHS) SẠCH toàn bộ.**
- **Phát hiện phụ (KHÔNG phải vi phạm HB01/HB02):** 0/50 tập có dòng disclaimer hư cấu; 25 tập tier
  medium/high chạm phong tục/tôn giáo thật → theo `disclaimer_rule` đáng lẽ cần disclaimer. **Nhưng**
  `content_policy.yaml:74` ghi vị trí/câu chữ disclaimer "do G8 (QA Runtime wire) quyết định" → có thể
  chèn ở stage sau, không nằm trong episode.md. Cần Mr.Long xác nhận hướng (xem "Câu hỏi mở" cuối).

## HB01 — mô tả nghi thức tái tạo được: 0 vi phạm
Mọi cảnh nghi lễ (thắp hương, quỳ, tụng, cúng dường, cúng cơm, đốt bó hương, chôn theo nghi lễ Công
giáo) đều ở mức **allusive/lướt qua** — KHÔNG có chuỗi bước + vật liệu + câu khấn cụ thể đủ để tái
tạo. Đúng `ap_dung` của HB01 ("truyện CÓ THỂ mô tả nghi thức ở mức KHÔNG-THỂ-LÀM-THEO"). Cận nhất:
ep_06:192 là công thức nấu **bánh chưng** trong sổ kỷ vật (chế biến món ăn, không phải nghi thức).

**Verify tận tay 4 tập tier=HIGH (tôn giáo đang thực hành):**
- **ep_16** (Phật giáo, "Chùa Phú Đường" hư cấu): ":177 đặt chậu cúc trước chánh điện, cúng dường,
  nói lời xin lỗi mẹ; :207 quỳ, tụng rất khẽ" — allusive, tôn kính. Không how-to.
- **ep_28** (Công giáo, "Giáo xứ Vĩnh Hòa" hư cấu): ":197 đặt nhẫn trên bục thờ Chúa, 'Chúa ơi xin
  Chúa truyền lời em'" — hành vi cầu nguyện tự sự, không nghi thức tái tạo.
- **ep_36** (Công giáo): ":187 chôn theo nghi lễ, đặt ảnh trên bục thờ, gửi ảnh cho Chúa" — allusive.
- **ep_46** (Công giáo, "Nhà thờ Diêm Điền"): ":175 đặt túi cát giữa nhà thờ, xin Chúa; :197 quỳ,
  cúi đầu" — allusive, tôn kính.
- Cả 4 thỏa `extra_rule` high tier (tôn kính, KHÔNG nhại/xúc phạm).

## HB02 — liên hệ/trục lợi thật: 0 vi phạm
Grep độc lập toàn 50 tập: KHÔNG có `https?://` / `www.` / số tài khoản / STK / SĐT / "chuyển khoản" /
"quyên góp...tài khoản". Tên riêng thật xuất hiện (Bệnh viện Bạch Mai/K/Huyết học, ĐH Kiến trúc/Bách
khoa, tàu điện Cát Linh-Hà Đông, hãng bay Vietjet/Vietnam Airlines, THPT Châu Văn Liêm, chùa Hương)
đều chỉ là **bối cảnh/set-dressing**, KHÔNG kèm lời kêu gọi tiền hay thông tin liên hệ thật. "cúng
dường" (ep_16) là hành vi trong truyện, không phải kêu gọi quyên góp thật.

## Phân loại sensitivity tier + disclaimer (25 tập thiếu disclaimer)
Không tập nào có disclaimer ("hư cấu"/"không có thật"/"không khuyến khích" = 0/50 grep). Intro brand
"Hắc Dạ Ký — chuyện kể từ cõi vô hình" KHÔNG phải disclaimer hư cấu.

| Tier | Số tập | Danh sách | Cần disclaimer? |
|---|---|---|---|
| **low** (siêu nhiên thuần hư cấu) | 25 | 01,11,12,15,17,18,19,20,22,23,25,26,27,29,30,32,33,35,37,40,41,42,44,49,50 | Không (na) |
| **medium** (phong tục dân gian thật: thắp hương/bàn thờ/rằm/cúng cơm — mức khái quát) | 21 | 02,03,04,05,06,07,08,09,10,13,14,21,24,31,34,38,39,43,45,47,48 | **CÓ — đang thiếu** |
| **high** (tôn giáo đang thực hành, nêu tên) | 4 | 16 (Phật giáo), 28/36/46 (Công giáo) | **CÓ — đang thiếu** |

Ghi chú ranh giới medium/low: có tính phán đoán. Em phân medium/high chỉ khi tập **mô tả một tập tục
tôn giáo-dân gian có tên** (thắp hương, bàn thờ tổ tiên, rằm/Vu Lan, Công giáo/Phật giáo); tập chỉ có
tang/mộ/hoa-viếng thế tục hoặc ma/điềm thuần thì để low (đúng nguyên tắc "ma/điềm/chết đơn thuần KHÔNG
phải vi phạm"). ep_45/47 dựa mention 1 dòng nhẹ (một ngày rằm / 1 chữ "bàn thờ") — nếu áp chuẩn chặt
hơn "phải mô tả tập tục chứ không chỉ nêu tên ngày/vật" thì 2 tập này rớt về low.

## CÂU HỎI MỞ CHO Mr.Long (không tự quyết)
1. **Disclaimer 25 tập medium/high:** `content_policy.yaml:74` giao vị trí/câu chữ disclaimer cho
   **G8 (QA Runtime)**. Hiện chưa có bằng chứng stage nào (render/publish) thực sự chèn disclaimer.
   Mr.Long quyết: (a) disclaimer sẽ được G8/publish chèn lúc phát hành (episode.md text đúng khi
   không mang) → chỉ cần xác nhận wiring G8; hay (b) cần thêm disclaimer vào chính episode.md 25 tập.
   → Đây là gap "policy yêu cầu, chưa rõ stage nào enforce" (đúng lớp R215) — em KHÔNG tự sửa.
2. Nếu chọn (a): đề xuất 1 test/gate xác nhận mọi tập tier>=medium có disclaimer TRƯỚC khi publish
   (mirror pattern enforcer khác) — nhưng đó là việc xây gate, cần Mr.Long duyệt riêng.

## Ghi chú tin cậy (R215)
- 0 HB01/HB02 do 5 subagent đọc toàn văn + CMD_BUILD_2 tự verify 4 tập high-tier + grep độc lập.
- Không "ép tìm vi phạm": kết quả "sạch HB01/HB02" là kết luận thật, phần lớn tập là low-tier hư cấu
  thuần. Disclaimer-gap là quan sát trung thực kèm caveat G8-deferral, không thổi phồng thành vi phạm.
