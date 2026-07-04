# G2 HYBRID CLASSIFICATION — 41 findings ep_01-50 (theo Mr.Long duyệt PING 21:39)

- Nguồn: `runtime/roster_backfill_draft.yaml` → section `hybrid_classification` (rows) + `name_pool_wave1_proposal`
- Sinh bởi: máy phân loại (executor) — **NGƯỜI DUYỆT trước khi merge roster**
- Phạm vi: F1 (41 tên không dùng PAS_ id) — gồm ep_01 (không có passenger_main) + 40 unmatched (ep_11..ep_50)
- Status: **PROPOSAL_AWAITING_MR_LONG** — chưa merge vào `passenger_roster_100.yaml`

## Tổng số
| Verdict | Số lượng | Ý nghĩa |
|---|---|---|
| SẠCH | 0 | (không có ep nào sạch tuyệt đối trong batch này — 2 ca gần-sạch bị giữ lại NGƯỜI DUYỆT vì đụng cốt truyện, xem dưới) |
| PHẠM | 37 | Vi phạm rule_02 (trùng âm tiết với roster 100) hoặc forbidden_words (15 từ Mr.Long 27/6) — đề xuất 2-3 tên thay theo pool đợt 1 |
| NGƯỜI DUYỆT | 4 | ep_01 (thiếu passenger_main — do golden EP01 lock riêng) · ep_11 (header dị dạng, không parse được tên) · **ep_30 và ep_50 (tên đính cốt truyện — xem cảnh báo dưới)** |

## ⚠️ Cảnh báo cốt truyện (máy KHÔNG tự đề xuất đổi — cần Mr.Long quyết)
- **ep_30**: khách tên **"anh Nguyễn"** — tình tiết là khách trùng TÊN với thầy giáo đã cứu nhân vật khỏi bỏ học (twist cố ý). Đổi tên = phá plot. Vi phạm hình thức: 1-âm-tiết (rule_01). Đề xuất: Mr.Long cân nhắc waiver (giữ nguyên, ghi lý do cốt truyện) thay vì đổi tên.
- **ep_50**: khách tên **"Hạ Nhi"** — nghi liên quan trực tiếp đến **Hạ Vy** (nhân vật khóa `bible/31_golden_samples.yaml#characters_locked`, dòng "lần đầu thấy anh sau tám năm trong đời"). Vi phạm hình thức: trùng âm "Hạ" (với Hạ Diệu) và "Nhi" (với Mỹ Nhi). Đổi tên có thể phá liên kết cố ý với Hạ Vy — cần Mr.Long xác nhận đây có phải easter egg chủ đích không trước khi quyết waiver hay đổi.

## Mẫu 5 ca PHẠM đầu (đủ trong draft yaml, đây chỉ trích minh họa)
| ep | tên hiện tại | vi phạm | đề xuất thay (pool đợt 1) |
|---|---|---|---|
| 12 | Vy An | trùng "Vy" (Vy Vi) + cấm "An" | Huyền Trâm / Huyền Oanh / Huyền Duyên |
| 13 | Bình Mỹ | trùng "Bình" + "Mỹ" | Chương Dương / Chương Thạch / Chương Vượng |
| 34 | Văn Tuấn | trùng "Văn" (Văn Triệu) + "Tuấn" (Tuấn Quốc) | Dương Quyết / Thạch Chương / Thạch Dương |
| 36 | Văn Khải | trùng "Văn" + "Khải" (Khải Toàn) | Thạch Vượng / Thạch Tân / Thạch Chiến |
| 18 | Linh Trang | cấm "Linh" + cấm "Trang" (2 lần cấm) | Nhã Miên / Nhã Ý / Nhã Đài |

Toàn bộ 37 ca + đề xuất cụ thể (2-3 alternative/ca) nằm trong `roster_backfill_draft.yaml#hybrid_classification.rows`.

## Pool tên đợt 1 (PROPOSAL — trình Mr.Long duyệt)
`runtime/roster_backfill_draft.yaml#name_pool_wave1_proposal` — cấu trúc: `{nu|nam}.{bac|trung|nam}.{cu|pt|tre}` → danh sách tên 2 âm tiết.
- **cu** = sinh ≤1970 (rule_07 tên mộc/Hán-Việt cũ) · **pt** = sinh 1970-1995 (tên phổ thông) · **tre** = sinh ≥1995 (tên trẻ hiện đại, vẫn thuần Việt)
- Máy-verify: mọi tên 2 âm tiết, **0 âm tiết trùng roster-200 hiện có**, **0 từ trong 15 từ cấm** (assert trong script, không đếm tay)
- Quy mô: mỗi vùng × thế hệ ~20-30 tên/giới (đủ dư cho 37 ca PHẠM + margin tương lai ep_51-90)
- **Ghi chú:** đây là tên GHÉP từ âm tiết do executor soạn theo khung rule_06 (tên gần quê) — Mr.Long duyệt/sửa/loại trực tiếp trong draft yaml, không phải danh sách chốt.

## Hành động tiếp theo (chờ Mr.Long)
1. Duyệt/sửa pool đợt 1 trong draft yaml.
2. Quyết ep_30 và ep_50: waiver giữ nguyên hay đổi tên (nếu đổi, đề xuất thay đã có sẵn dự phòng — có thể bổ sung nếu cần).
3. Sau khi duyệt: executor gán PAS_id thật (đề xuất 0101+) + merge vào `passenger_roster_100.yaml` (vẫn KHÔNG song song BP6/flip ceremony).
4. Flip ceremony (proposals→planned_path, bible/37 v2.1, bible/23 v1.1, C4/C5) chạy SAU khi BP6 landed trên origin/main — route riêng, đã ghi PING.

Commit: LOCAL only (chưa push) — chờ Mr.Long duyệt trước khi đẩy lên chung.
