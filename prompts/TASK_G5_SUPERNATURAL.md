# TASK G5 — SUPERNATURAL (finalize từ Desktop draft 4/7, kiểm chứng + phản biện 4/7)

> Reconciled từ kiểm thử THẬT: nửa "hồ sơ vong-như-nhân-vật" đã chắc (roster/BP4);
> nửa "thực thể siêu nhiên có luật riêng" CHƯA có. Nạp trực tiếp từ Cultural KB (**đã qua
> deep-research + adversarial-verify + Evidence Schema, KHÔNG còn "đang verify" như draft gốc**)
> + BP7 cultural_spec (song song) + compliance_gate (**ĐÃ ĐƯỢC BP9 XÂY — xem PHẢN BIỆN dưới,
> KHÔNG làm lại**).

## ĐIỀU KIỆN CHẠY
Không phụ thuộc G2/G3 trực tiếp (world/supernatural là domain nền theo BP3 dependency_detail.yaml).
Nên chạy gần nhịp với G4 (G4 tự khai "nuôi trực tiếp G5 supernatural typology"). Claim pack trước
khi build: `python tools/build_claim.py claim g5_supernatural <phiên>`.

## ⚠️ PHẢN BIỆN QUAN TRỌNG (đọc trước khi build D4 — nếu bỏ qua sẽ vi phạm R211)
Draft gốc (4/7) liệt "Compliance gate ❌ KHÔNG AI OWN (lỗ hổng đã chỉ mặt 4/7)" và đề xuất D4 tự
xây `bible/content_policy.yaml` + `tools/compliance_check.py`. **Claim này đã LỖI THỜI** — BP9
(cũng khóa 4/7, sau thời điểm draft ghi nhận gap) đã xây sẵn:
- `governance/blueprint/bp9/content_policy.yaml`: 2 hard_boundaries **HB01_no_actionable_ritual_detail**
  + **HB02_no_real_profit_solicitation_link**, căn cứ đúng Nghị định 38/2021/NĐ-CP Điều 14 + Điều 320
  BLHS 2015 — **NGUYÊN VĂN GIỐNG CĂN CỨ PHÁP LÝ DRAFT G5 TỰ TRA** (deep-research 4/7, trùng nguồn).
- `governance/blueprint/bp9/policy_gates.yaml`: `sensitivity_tiers` (low/medium/high) + `disclaimer_rule`
  — đã đọc trực tiếp file, xác nhận đây CHÍNH LÀ nội dung D4 gốc định làm lại.
- File tự ghi rõ (dòng 2-5 `policy_gates.yaml`): **"Runtime scanner THẬT (quét episode thật) là việc
  G8 QA Runtime sau này — BP9 chỉ ra LUẬT để G8 áp dụng, KHÔNG tự wire vào ci_gate.py"** — và
  `tools/publish_gate.py` được nêu đích danh là tool **G8 sẽ xây**, KHÔNG phải G5.

→ **D4 gốc bị CẮT/THAY** (xem D4 mới bên dưới). Đây là phát hiện chồng lấn thật (R211: cấm nhân đôi),
không phải suy đoán — đã đọc nguyên văn cả 2 file BP9 trước khi kết luận.

## MISSION
"Ma hoạt động theo luật gì" — không để tập trước ma không chạm được người, tập sau kéo người đi vô lý.
Mọi năng lực/nghi lễ siêu nhiên PHẢI neo vào tín ngưỡng ĐÃ KHAI trong bible văn hóa (có nguồn), không bịa.

## NỀN ĐÃ CÓ (đã re-verify 4/7, có đính chính vị trí field)
| Đã có | Ở đâu (đính chính nếu cần) |
|---|---|
| `life_status`, `regret_sub_archetype`, `haunting_symbol` (TIER1_TOP) | **`tools/roster_validator.py` dòng 51** (đính chính: field này nằm trong LOGIC VALIDATOR, không phải khai trực tiếp trong `bible/37_character_schema.yaml` như draft gốc ghi — đã grep bible/37 không thấy tên field này, grep roster_validator.py thấy đúng) |
| `continuity_risk.allowed_flags`: `da_chet_xuat_hien_lai, mat_tich, doi_ten, bi_nhap, biet_bi_mat, recurring_cross_ep, roster_drift_no_pas_id` | `bible/37_character_schema.yaml` (xác nhận đúng, danh sách đầy đủ hơn draft gốc liệt — draft chỉ nêu 4/7 flag, thực tế có 7) |
| Chuỗi hiện hình: `ghost_appears → world → emotion_trigger → dialogue → audio → qa_runtime` | `bp4/event_bus.yaml` (xác nhận `ghost_appears` có thật trong 8 event_id đã khai) |
| Kho văn hóa typology (ma da/ma trành/ma xó/mộ gió...) | Cultural KB — **đã verify xong** (không còn "đang verify"), xem `governance/evidence_schema_cultural_kb.yaml` |
| Compliance rules (HB01/HB02, sensitivity_tiers) | **`bp9/content_policy.yaml` + `bp9/policy_gates.yaml` — ĐÃ CÓ, LOCKED** (xem PHẢN BIỆN trên) |

## GAP THẬT (việc của G5 — đã trừ phần BP9 đã làm)
1. **Typology ma** — chưa có schema phân loại (ma da ≠ ma trành ≠ oan hồn ≠ quỷ)
2. **Quy tắc hiện hình/quyền năng** — chưa có máy trạng thái theo mùa/lịch âm
3. **Possession state machine** — `bi_nhap` mới là cờ, chưa có chuỗi nhập→biểu hiện→trục xuất
4. **`entity_class`** — chưa phân biệt người / linh hồn / thực thể siêu nhiên / nhân vật lịch sử
5. ~~Compliance gate không ai own~~ — **ĐÃ CÓ CHỦ (BP9 khai luật + G8 sẽ wire runtime scanner)**.
   Việc còn lại của G5 chỉ là: dùng ĐÚNG enum `sensitivity_tiers` của BP9 trong typology, KHÔNG tự
   định nghĩa lại thang đo.

## DELIVERABLES

### D1 — Ghost/Entity Typology
`bible/supernatural_typology.yaml` (đề xuất, proposals/ — writer mr_long): mỗi loại: `entity_type ·
nguồn_gốc (map cultural_spec BP7 đã ký — CẤM bịa nghi thức ngoài văn hóa đã duyệt) · quyền_năng ·
giới_hạn · cách_hóa_giải · sensitivity` — **field `sensitivity` PHẢI dùng đúng 3 giá trị enum đã khóa
trong `bp9/content_policy.yaml#sensitivity_tiers` (low/medium/high), KHÔNG tự tạo thang đo mới (R211)**.
Seed từ Cultural KB đã verify: ma da (kéo thế mạng), ma trành (dẫn hổ), ma xó (giữ của — sensitivity
cao), oan hồn chiến trận, hồn quy y Phật giáo.

### D2 — `entity_class` vào schema nhân vật
Thêm field `entity_class: nguoi | linh_hon | thuc_the_sieu_nhien | nhan_vat_lich_su` vào bible/37 —
diff tối thiểu (RFC nhỏ vì bp2 locked, cần "per Mr.Long authorization"), mở đường cho cả ma HDK lẫn
nhân vật lịch sử HSV.

### D3 — Possession & Power State Machine
`runtime/supernatural_state_machine.yaml`: chuỗi possession (nhập → biểu hiện → trục xuất/thoát) +
power level theo lịch âm (link D1 timeline_check của G4 — mạnh hơn rằm tháng 7, yếu đi giờ Ngọ...).
Reconcile BP4 state_machines (4 entity xác nhận: ghost/character_fear/character_life/voice_state,
0 orphan) — KHÔNG viết engine riêng, mở rộng cái có.

### D4 — Handoff Compliance cho G8 (THAY THẾ "Compliance Gate" gốc — KHÔNG tự build)
**KHÔNG tạo `bible/content_policy.yaml` mới, KHÔNG tạo `tools/compliance_check.py`** (trùng BP9 —
xem PHẢN BIỆN). Việc của G5 chỉ:
- Mọi entry `sensitivity: high` trong D1 typology PHẢI trỏ nguồn thật (deep-research) + qua Mr.Long
  duyệt trước khi lock (đúng REALITY ANCHOR).
- Ghi 1 file `reports/G5_HANDOFF_G8.md`: liệt kê rõ các entity/nghi thức sensitivity cao cần G8's
  `tools/publish_gate.py` (khi G8 xây) quét kỹ, kèm evidence — KHÔNG tự wire vào ci_gate hay preflight
  publish (đó là quyền của BP9/G8, không phải G5).

### D5 — Validator + Gate 1 cửa
`tools/supernatural_validator.py`: entity dùng năng lực KHÔNG có trong typology đã khai → FAIL ·
nghi lễ không map cultural_spec → FAIL · possession thiếu trục xuất hợp lệ → FAIL · **sensitivity
field dùng giá trị ngoài enum BP9 → FAIL** (check mới, thay cho compliance_check cũ).
`tools/g5_supernatural_check.py` (mirror pattern) wire ci_gate + unwire-guard.

## REALITY ANCHOR
Mọi mục sensitivity=high trong typology phải trỏ nguồn thật (deep-research kết quả) — 0 mục
"needs-source" được lock; Boss duyệt cách thể hiện từng ca sensitivity cao trước khi merge.

## MUTATION AUDIT SẼ BẮN
M1 ma bịa năng lực ngoài typology (vd ma da biết bay) → FAIL · M2 nghi lễ không map cultural_spec →
FAIL · M3 possession không trục xuất (treo mãi) → FAIL · M4 `sensitivity` dùng giá trị ngoài enum
BP9 (vd tự chế "critical") → FAIL · M5 gỡ stage G5 → unwire đỏ · M6 entity_class thiếu ở nhân vật
linh_hon → FAIL (cross-check D2↔roster) · M7 tool tự tạo trùng `bp9_compliance_check.py`/`content_policy.yaml`
→ FAIL ngay từ review (R211 tối cao, kiểm duyệt bác thẳng không cần mutation).

## DoD
Typology ≥5 loại có nguồn ✅ · entity_class flip vào schema ✅ · possession SM chạy được ✅ ·
sensitivity field dùng đúng enum BP9 (không tự định nghĩa) ✅ · `reports/G5_HANDOFF_G8.md` bàn giao
rõ ràng ✅ · registry 0/0/0 · KHÔNG đụng render LOCKED · KHÔNG tạo file trùng BP9.

## RÀNG BUỘC
Claim pack trước khi build (luật 11) · KHÔNG mô tả nghi thức thật đủ chi tiết để làm theo (an toàn
pháp lý) · số/pool bịa = BÁC · nhân đôi = BÁC (R211, đặc biệt nghiêm với BP9 — xem PHẢN BIỆN).

STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.
