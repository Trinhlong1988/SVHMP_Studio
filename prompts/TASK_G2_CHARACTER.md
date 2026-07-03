# TASK G2 — CHARACTER FILL & GATE (Mr.Long duyệt 3/7 · chạy sau BP3 LOCK, không đợi BP8)
> Khung dữ liệu ĐÃ ĐÓNG ở BP2 (23 facet character, tag bp2-domain-v1.0). G2 = ĐỔ DỮ LIỆU
> vào khung + bật gate — KHÔNG xây engine, KHÔNG thêm facet (facet mới = RFC).
> Luật chung BP_PIPELINE_MASTER áp toàn bộ (R200, no-stub, machine-first, 6 lệnh self-test).

## NGUYÊN LÝ: "ĐÀO DỮ LIỆU THẬT, KHÔNG BỊA"
90 tập đã viết = mỏ hồ sơ nhân vật. Máy trích xuất → người DUYỆT. AI không sáng tác đời tư.

## 4 BƯỚC
### B1. SCHEMA (nửa buổi — cần chữ ký Mr.Long vì bible writer = mr_long)
- `bible/37_character_schema.yaml` v2: thêm trường cho 10 G2-core facet còn thiếu
  (knowledge/goal/fear/arc/reveal_permission/continuity_risk/trauma_backstory_lock/state...)
  — khớp ĐÚNG facet_id đã đóng trong bp2/domain_specs.yaml (drift = FAIL).
- `bible/23_passenger_naming.yaml` v1.1: 4 rule mới (region/generation/culture/vietnamese)
  + pool tên theo vùng — SOẠN ĐỀ XUẤT, Mr.Long ký mới ghi (bible immutable).

### B2. MÁY ĐÀO NGƯỢC (song song B1)
- `tools/roster_backfill_miner.py` (MỚI — tool governance, được phép): quét `output/ep_*/episode.md`
  ĐÃ CÓ → trích per-character: xuất hiện tập nào · chết/mất tích tập nào (continuity_risk!) ·
  nói gì (speech evidence) · biết bí mật gì (knowledge candidates) → ghi ĐỀ XUẤT vào
  `runtime/roster_backfill_draft.yaml` với `status: draft` — KHÔNG tự ghi vào roster chính.
- Bonus bắt buộc: report mâu thuẫn sẵn có phát hiện được (chết rồi xuất hiện lại...) →
  `reports/G2_CONTINUITY_FINDINGS.md`.

### B3. FILL THEO RỦI RO (executor/Mr.Long duyệt nội dung — AI chỉ đề xuất)
- Thứ tự: continuity_risk CAO trước (đã-chết/biết-bí-mật/recurring) → Tier2 có thoại → Tier1.
- Mỗi batch duyệt xong merge vào `runtime/passenger_roster_100.yaml` + chạy validator.
- Validator MỚI `tools/roster_validator.py`: name↔quê↔tuổi↔belief (naming rules) ·
  đủ 10 G2-core facet theo tier · reveal_permission↔knowledge nhất quán · arc map state machine.

### B4. GATE TĂNG DẦN
- Ngưỡng: Tier1 100% · Tier2 ≥90% · Tier3 (recurring) 100% → bật `--strict-characters`
  mặc định trong quy trình render (KHÔNG sửa svhmp_v13_render.py LOCKED — bật qua flag/wrapper).
- Wire `roster_validator.py` vào ci_gate CHECKS (named→ENFORCED).

## DoD (đo được — thiếu 1 = chưa DONE)
strict bật ✅ · confusion-run nhân vật 500/500 ✅ · 10 facet core đầy theo ngưỡng ✅ ·
naming validator 0 lệch ✅ · Mr.Long tai-người duyệt 5 hồ sơ mẫu ✅ · registry 0/0/0 ·
G2_CONTINUITY_FINDINGS đã route executor xử.

## PHÂN VAI
CMD_BUILD: schema đề xuất + miner + validator + wire (máy). Executor/Mr.Long: DUYỆT nội dung
hồ sơ + ký bible v2/v1.1. Kiểm duyệt: audit 7 bước + mutation (roster giả lệch quê/tuổi → FAIL).
STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.
