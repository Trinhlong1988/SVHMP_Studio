# BP PIPELINE MASTER — chuỗi tự động BP2→BP8 (Mr.Long duyệt 3/7)
> CMD_BUILD: sau khi pack N được Mr.Long LOCK, **tự đọc `prompts/TASK_BP{N+1}_*.md` và chạy tiếp**
> — không chờ lệnh miệng. Kiểm duyệt audit 7 bước giữa mỗi pack; chỉ Mr.Long ký lock.

## CHUỖI (cập nhật 3/7 tối per Mr.Long — khớp master_roadmap §8 AI Studio)
BP1→BP4 ✅ locked+tag 3/7 → **BP5 Validation** (+ G2-B1/B2 song song per TASK_G2 đã duyệt
"không đợi BP8") → BP6 Decision → BP7 Narrative → BP8 Production (BP6-8 áp luật 10)
→ FINAL AUDIT BP0-BP8 → tag `system-blueprint-v1.0` → **S1 vertical slice EP01 audio + KPI**
(roadmap §8) → G2 B3/B4.

## LUẬT CHUNG MỌI PACK (không lặp lại trong từng task — vi phạm = audit BÁC)
1. **Source of truth:** BP-C v2.0 LOCKED (`blueprint_domains.yaml`: 22+1 domain ĐÓNG, layer 1-12,
   layer_groups 4 nhãn, PLANNED HONESTY 5-metadata, lifecycle/lock_type, versioning semver).
   Mâu thuẫn BP0/BP-pack-đã-lock → **STOP, report FAIL** (RFC nếu cần đổi).
2. **CẤM:** runtime/stub code · sinh content (episode/audio/video) · tự lock/tag/freeze ·
   scheme layer mới · thêm/bớt domain · sửa `svhmp_v13_render.py` (LOCKED).
3. **Machine-first:** dữ liệu vào YAML (dup-key loader C10 pattern), doc .md mỏng đủ 11-element
   + 0 placeholder. Mọi ref file mang `status: exists|planned` — exists láo = FAIL.
4. **Validator:** mỗi pack mở rộng `tools/bp1_architecture_check.py` HOẶC thêm checker riêng
   (bump `__version__`, cross-check `validator_version`); negative test BEHAVIORAL cho từng luật mới.
5. **R200:** worktree riêng · pull --rebase trước · log_ping + push sau · CẤM --no-verify ·
   map mọi file mới vào file_index → registry 0/0/0 · test spawn git scrub `GIT_*`.
6. **Self-test chuẩn 6 lệnh:** blueprint_constitution_check · checker pack · registry_check ·
   pytest -q · cmd_pipeline_gate --skip-build (ARCH+QA PASS) · git status --short sạch.
7. **Report:** `reports/BP{N}_REPORT.md` (verdict/commit/bảng deliverable/validation/mutation/
   drift/limitations) + sign-off `reports/build_report.md`. Dòng cuối `STATUS: READY_FOR_AUDIT`
   / `FAIL_NEEDS_FIX`. Mọi claim phải kèm file-path tồn tại.
8. **Registry pack key:** mỗi pack thêm `bp{N}_<name>: candidate` vào enterprise_pack_progress
   (lock = chữ ký Mr.Long; tag `bp{N}-<name>-v1.0`).
9. **REALITY ANCHOR (Mr.Long 3/7):** pack muốn lock phải kèm ≥1 validator/tool chạy PASS trên
   DỮ LIỆU THẬT đã exists, số liệu đo được ghi trong REPORT — cấm pack thuần lời hứa.
10. **THIN+TIMEBOX (áp BP6-BP8):** chỉ deliverables đã liệt kê trong task, KHÔNG nở thêm doc/scope;
   timebox ≤1 phiên/pack — quá hạn = STOP báo Mr.Long, không âm thầm kéo dài.

## SAU BP8
Kiểm duyệt chạy FINAL AUDIT (freeze_gate mọi bp-pack + cross-pack consistency + mutation tổng
+ **phân loại mọi element planned**: mâu-thuẫn-nội-bộ / không-thể-implement / chưa-implement —
2 loại đầu = FAIL phải xử trước tag) → Mr.Long ký tag `system-blueprint-v1.0`
→ Domain/Facet/Interface/Flow ĐÓNG → **S1 EP01 vertical slice** (roadmap §8) → G2 B3/B4.
Backlog trả trong S0-S1: dup-key loader `architecture_registry_check` (H6) · `verify_ping_claim`
24 UNKNOWN · bảng rule↔enforcer máy-sinh · ADR retro mỏng (`docs/adr/`).
