# G2 HYBRID CLASSIFICATION — 41 findings ep_01-50 (theo Mr.Long duyệt PING 21:39)

- Nguồn: `runtime/roster_backfill_draft.yaml` → section `hybrid_classification` (rows) + `name_pool_wave1_proposal`
- Sinh bởi: máy phân loại (executor) — **NGƯỜI DUYỆT trước khi merge roster**
- Phạm vi: F1 (41 tên không dùng PAS_ id) — gồm ep_01 (không có passenger_main) + 40 unmatched (ep_11..ep_50)
- Status: **APPROVED_WAVE1 (Mr.Long duyệt 2026-07-04)** — 37/37 PHẠM đã chốt tên + 2 waiver đã quyết. **CHƯA merge vào `passenger_roster_100.yaml`** (khóa đúng 100 passenger; 39 nhân vật này còn thiếu Tier1 đầy đủ — chờ B3 fill theo thứ tự continuity_risk)

## CẬP NHẬT 2026-07-04 — Mr.Long đã duyệt pool đợt 1 + 2 waiver
- **Pool đợt 1: DUYỆT.** Thực thi phát hiện pool ban đầu THIẾU quy mô (database `feminine_syllables` chỉ còn 8/142 mục free, cả 8 đều dính cấm → 0 khả dụng). Mr.Long chọn phương án **(a) mở rộng database**: `data/vietnamese_names_extended.yaml` +32 âm tiết nữ +34 âm tiết nam (section mới `g2_wave1_2026_07`, chỉ THÊM — không sửa/xóa mục cũ, máy-verify 0 trùng roster-200/forbidden-15/nội bộ batch).
- **2 waiver: DUYỆT GIỮ NGUYÊN.** ep_30 "anh Nguyễn" và ep_50 "Hạ Nhi" — giữ tên gốc, `waiver_approved: true`.
- **Kết quả cuối: 37/37 PHẠM đã chốt tên** (0 còn PENDING), **0 trùng âm tiết lẫn nhau/roster-200/forbidden-15** (máy-verify), **12/37 (32%) cần era-fallback nhẹ** (vd dự định "phổ thông" nhưng chốt "cũ" — cùng vùng, chỉ lệch thế hệ), **0 ca cần region-fallback** (đúng vùng dự định 100%). Toàn bộ 39 tên (37 PHẠM + 2 waiver) đã qua C4b (rule_09 content-check) — sạch.
- Chi tiết đầy đủ: `runtime/roster_backfill_draft.yaml#hybrid_classification` (mỗi row có `final_name`, `final_pas_id`, `decision`, `naming_fallback_note` nếu có).
- **BUG FIX (bắt được nhờ test tự viết khi bắt đầu B3):** PAS_id ban đầu gán cho 39 nhân vật (đề xuất `PAS_0101`-`PAS_0139`) **giả định SAI** rằng `passenger_roster_100.yaml` dùng dải liên tục `PAS_0001`-`PAS_0100`. Thực tế roster khóa dùng `PAS_0013`-`PAS_0112` (không liên tục từ 1) — nghĩa là dải đề xuất ban đầu **đụng thẳng** 12 ID thật (`PAS_0101`-`PAS_0112`) đang tồn tại trong roster khóa! Phát hiện bởi `test_batch1_no_overlap_with_locked_roster_100` (tự chứng minh cắn ngay lần chạy đầu). **Đã renumber toàn bộ 39 ID về dải tự do thật `PAS_0113`-`PAS_0151`** (mapping đầy đủ ghi trong `hybrid_classification.meta.pas_id_bug_fix_2026_07_04`).

## B3 FILL — BATCH 1 (5/39, per Mr.Long xác nhận: batch nhỏ + file mở rộng riêng)
- **Kiến trúc:** `runtime/passenger_roster_backfill_ep11_50.yaml` — file mở rộng riêng, cùng schema `passenger_roster_100.yaml`, **KHÔNG** đụng file 100 đã khóa (test `test_character_manager_r205` assert `len==100` vẫn nguyên vẹn). Kiểm bởi `tools/roster_validator.py --roster <file>` (đã có sẵn flag) + test riêng `tests/test_roster_backfill_ep11_50.py` (7 case, bao gồm chống trùng ID/tên với roster-100 khóa).
- **5 nhân vật đã fill Tier1 đầy đủ** (PAS_0113 ep_12, PAS_0114 ep_13, PAS_0115 ep_14, PAS_0117 ep_16, PAS_0118 ep_17): pillar/regret_sub_archetype (map vào 27 sub-archetype LOCKED bible/11) + haunting_symbol (map vào 40 object LOCKED bible/12) + death.type + voice — mỗi field có `evidence_ref` trỏ về `ep:line` thật, **không suy diễn**.
- **death.type = `khong_ro` cho cả 5** (giá trị hợp lệ trong enum `bible/37.death_types`): evidence chỉ kể về NGƯỜI KHÁC mất (mẹ/cha/người yêu cũ/bạn thân), không nêu rõ chính hành khách qua đời thế nào — dùng `khong_ro` thay vì bịa, đúng tinh thần "KHÔNG bịa".
- **2 phát hiện GAP catalog (bible/12 object library, 40 object, LOCKED):** PAS_0114 (cúc khô từ vườn cha) và PAS_0117 (chậu cúc mẹ trồng) — **KHÔNG object hoa/cây cảnh nào** trong 40 object hiện có khớp. Dùng placeholder `GAP_HOA_CUC_KHO`/`GAP_CHAU_CUC` (không phải mã canon, rõ ràng đánh dấu) — đề xuất RFC bổ sung 1-2 object hoa cúc vào bible/12 nếu mô-típ này lặp lại ở batch sau (2/5 batch đầu đã trùng mô-típ — đáng chú ý).
- **3 ca dùng object thật nhưng lệch pillar-tag** (không phải gap, chỉ là bible/12 khai `pairable_pillars` không khớp use-case): PAS_0113 (đồng hồ, pillar khai family/kindness nhưng dùng cho love_regret), PAS_0118 (USB thư — vật lý khác giấy nhưng chức năng tường thuật giống `OBJ_THU_TAY`). Không có validator nào enforce pairing này (đã kiểm tra `tools/`), nên không chặn, nhưng ghi rõ `object_pairing_note` để minh bạch.
- **Còn lại 34/39** cho batch sau (ep_11 tạm gác — chưa có tên do header dị dạng, ep_15/18-29/31-49 trừ đã làm).

## Đề xuất RFC (chờ Mr.Long, không tự quyết)
1. Bổ sung bible/12: 1-2 object liên quan hoa cúc (`cúc khô ép giấy bản` / `chậu cúc kim ngân`) — nếu mô-típ tiếp tục lặp ở batch sau.
2. Bổ sung bible/11 REG_KIN: archetype mới cho case "từ chối giúp người lạ cần cấp thiết → họ chết" (PAS_0115 hiện dùng REG_KIN_001 gần nhất nhưng không khớp hướng — 5 archetype KIN hiện có đều là "chưa trả ơn", ngược hướng).

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

## Hành động tiếp theo
1. ~~Duyệt pool đợt 1~~ ✅ DONE (2026-07-04, phương án a — mở rộng database).
2. ~~Quyết ep_30/ep_50~~ ✅ DONE — cả 2 waiver giữ nguyên.
3. ~~Flip ceremony~~ ✅ DONE (chạy sau BP6 landed, xem commit `c8a6041`).
4. **CÒN LẠI (B3 fill, chưa làm):** 39 nhân vật (37 rename + 2 waiver, PAS_0101-0139) mới chỉ có identity tối thiểu (id/tên/ep nguồn/gender/tuổi/quê thô). Cần fill đủ Tier1 (regret_sub_archetype/haunting_symbol/death.type/voice đầy đủ) theo thứ tự continuity_risk CAO trước (TASK_G2 B3) rồi mới merge từng batch vào `passenger_roster_100.yaml` + chạy `roster_validator.py`. **Kiến trúc lưu ý:** file tên "100" khóa cứng đúng 100 passenger (`tests/test_character_manager_r205.py` assert `len==100`) — 39 nhân vật mới KHÔNG thể append trực tiếp vào file đó mà không phá invariant; cần quyết định kiến trúc (file mở rộng riêng, hay bump invariant có kiểm soát) trước khi B3 merge.
5. ep_01 (golden EP01, Mr.Long quyết riêng) + ep_11 (header dị dạng, người đọc lại episode.md) vẫn NGƯỜI DUYỆT, chưa thuộc quyết định này.

Commit: qua worktree riêng, đã push origin/main (xem commit hash trong git log).
