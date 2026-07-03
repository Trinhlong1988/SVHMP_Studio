# BP-C v2 — PHÁN QUYẾT CHỐT (kiểm duyệt 3/7, sau ARCH_AUDIT vòng 2 chấm 9.8/10)
> Văn bản ĐÓNG vòng tranh luận thiết kế. Bảng E (Mr.Long ký 3/7) GIỮ NGUYÊN HIỆU LỰC —
> không cần chữ ký mới. A1-A8 chạy theo prompts/TASK_BPC_AMENDMENT_V2.md không đổi scope.

## Phân xử 8 điểm "xiết thêm" của ARCH_AUDIT vòng 2
| # | Điểm | Phán quyết |
|---|---|---|
| 1 | Inventory 31 mục khoá luôn | BÁC lần 2 — list vẫn sót Production/StoryPlanner/Decision/Object (bằng chứng list gõ tay sai); bảng B phân tầng + RESERVED là phán quyết cuối |
| 2 | Facet inventory machine-check | ĐÃ CÓ (A7 format · BP3 data) |
| 3 | Ownership 1-writer | ĐÃ CÓ (BP3 machine-checkable) |
| 4 | Cross-domain event bus | ĐÃ CÓ (A7/BP4) + NHẬN 1 note: hop trong chain phải là domain HOẶC facet đã khai (Music/Lighting = facet audio/video) — checker BP4 bắt |
| 5 | "Chưa có Decision Layer" | ĐỌC SÓT — decision_engine đã có (A5, L5). Thứ tự chuẩn GIỮ: story_planner(L4: CÁI GÌ) → decision_engine(L5: NHỊP) → generator(L6: VIẾT) |
| 6 | "Chưa có versioning" | ĐỌC SÓT — A4 đã có + cross-check __version__ |
| 7 | Lifecycle 5-trạng-thái gộp | BÁC nhẹ — A2 (status file) + A3 (lifecycle contract) tách khái niệm chuẩn hơn, giữ |
| 8 | Calibration format-not-hardcode · tuần tự lock từng pack | ĐỒNG THUẬN — bảng E đã đúng vậy |

## LUẬT ĐÓNG
1. Sau re-lock blueprint-constitution-v2.0: **Domain Inventory ĐÓNG** — mọi thêm/bớt domain
   = RFC mới + chữ ký Mr.Long (không tranh luận lại trong BP1-BP8).
2. Ba bên (Builder · ARCH_AUDIT · kiểm duyệt) đã hội tụ: decision_engine, versioning,
   lifecycle, facet-ownership, event-format — KHÔNG mở lại các mục này.
3. Mốc giá trị thật = EP01 re-render (không phải số trang doc) — chống blueprint-paralysis.