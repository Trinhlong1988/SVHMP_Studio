# G5 SUPERNATURAL — HANDOFF cho G8 QA Runtime

**Ngày:** 2026-07-05 · **Từ:** CMD_BUILD_3 (TASK_G5_SUPERNATURAL.md, deliverable D4)
**Đến:** phiên G8 QA Runtime (chưa build tại thời điểm ghi report này)

## Vì sao report này tồn tại (KHÔNG phải compliance_check mới)

`TASK_G5_SUPERNATURAL.md` mục "⚠️ PHẢN BIỆN QUAN TRỌNG" xác nhận: BP9 (`governance/blueprint/bp9/content_policy.yaml` + `policy_gates.yaml`, đã lock) đã khai đủ 2 hard_boundaries (HB01/HB02) + `sensitivity_tiers` (low/medium/high) + `disclaimer_rule`. `bp9/policy_gates.yaml` tự ghi rõ: **"Runtime scanner THẬT (quét episode thật) là việc G8 QA Runtime sau này — BP9 chỉ ra LUẬT để G8 áp dụng, KHÔNG tự wire vào ci_gate.py"**. Vì vậy G5 **KHÔNG** tự tạo `bible/content_policy.yaml` hay `tools/compliance_check.py` mới (sẽ trùng BP9, vi phạm R211) — D4 chỉ là **bàn giao danh sách** cho G8 dùng khi G8's `tools/publish_gate.py` được xây.

## Enum sensitivity dùng (từ BP9, KHÔNG tự định nghĩa lại)

Nguồn: `governance/blueprint/bp9/content_policy.yaml#sensitivity_tiers`
- `low`: yếu tố siêu nhiên thuần hư cấu, không gắn tín ngưỡng/tôn giáo thật — `disclaimer_required: false`
- `medium`: nhắc phong tục/tín ngưỡng dân gian thật ở mức khái quát — `disclaimer_required: true`
- `high`: dùng tôn giáo/tín ngưỡng ĐANG được thực hành thật hoặc DTTS — `disclaimer_required: true` + `extra_rule`: tôn kính tuyệt đối, cấm giễu nhại

## Danh sách entity sensitivity=HIGH cần G8 quét kỹ

Nguồn: `governance/proposals/supernatural_typology_proposal.yaml` (D1, đề xuất — writer chính thức = Mr.Long)

| entity_type | Lý do sensitivity=high | Evidence status | HB áp dụng |
|---|---|---|---|
| `ma_xo` | Đụng tín ngưỡng dân tộc thiểu số phía Bắc đang được thực hành — draft tự đánh dấu `⚠️needs-source` | hypothesis (chưa có nguồn học thuật riêng — **G8 nên chặn cho tới khi Mr.Long/researcher bổ sung nguồn**) | HB01 (không mô tả cách "trừ/đuổi" cụ thể) |
| `hon_sieu_thoat_phat_giao` | Dùng khái niệm Phật giáo đang được thực hành thật (Vu Lan, siêu thoát, hồi hướng công đức) | hypothesis (khái niệm phổ biến, draft không trích kinh điển cụ thể) | HB01 (không hướng dẫn nghi thức tụng kinh cụ thể) |

## Entity sensitivity=MEDIUM (disclaimer bắt buộc, không cần chặn cứng)

| entity_type | Lý do |
|---|---|
| `oan_hon_chien_tran` | Chạm sự kiện lịch sử thật (liên hệ Thất thủ Kinh đô 1885 / Đàn Âm Hồn Huế 1894 — phần Đàn Âm Hồn đã **verified**, phần "oan hồn chiến trận" nói chung vẫn hypothesis) |

## Việc CỦA G8 (không phải của G5)

1. Khi xây `tools/publish_gate.py`: đọc `governance/proposals/supernatural_typology_proposal.yaml` field `sensitivity` + `evidence.status`, áp `bp9/content_policy.yaml#disclaimer_rule` (chèn disclaimer khi `sensitivity IN [medium, high]`).
2. Entity `status: hypothesis` (4/5 entity hiện tại) — G8 nên coi đây là **cần Mr.Long duyệt nguồn trước khi cho phép lock** vào production thật, đúng REALITY ANCHOR của TASK_G5 ("0 mục needs-source được lock").
3. `tools/supernatural_validator.py` (D5, CMD_BUILD_3 xây cùng phiên này) đã tự FAIL nếu `sensitivity` dùng giá trị ngoài enum BP9 — G8 có thể tái dùng logic này, KHÔNG cần viết lại.

## Việc CỦA G4 (World/Timeline/Event — xem thêm `runtime/supernatural_state_machine.yaml`)

`power_level_by_lunar_date` trong file D3 là **handoff cho G4**, không phải claim đã wire — G4 timeline_check (chưa tồn tại lúc D3 được viết) sẽ đọc bảng đó khi build timeline engine thật.

## KHÔNG có trong report này

Report này KHÔNG thay thế `bp9/content_policy.yaml`/`policy_gates.yaml`, KHÔNG tự đặt luật mới, KHÔNG tự wire vào `ci_gate.py` cho mục đích compliance runtime (chỉ wire `tools/g5_supernatural_check.py` cho mục đích validate CẤU TRÚC typology/state-machine — xem D5 — không phải quét nội dung episode thật).
