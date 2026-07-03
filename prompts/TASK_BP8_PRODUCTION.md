# TASK BP8 — PRODUCTION ARCHITECTURE (theo BP_PIPELINE_MASTER.md)

## MISSION
Kiến trúc chuỗi render → phân phối: formalize chuỗi ĐANG CHẠY THẬT (tts/audio/production)
+ spec planned cho video/publisher/analytics. RECONCILE — cấm rebuild, cấm tả sai hệ đang chạy.

## DELIVERABLES
1. `governance/blueprint/bp8/render_chain.yaml` — stages: stage_id · tool (status exists|planned:
   render = `tools/svhmp_v13_render.py` LOCKED exists · preflight = `tools/svhmp_preflight_qa.py`
   exists · final_verify/100check exists · video/publisher planned 5-metadata) · input/output
   artifact · gate (G2 char-gate trong render L339/344 · post_render_gate R41 · server-CI) ·
   failure_route.
2. `governance/blueprint/bp8/golden_output.yaml` — chuẩn nghiệm thu output (R196: Engineering
   PASS ≠ Production; golden = `bible/31_golden_samples.yaml` exists + EP01 golden text) —
   FORMAT tiêu chí (loudness/tail/duration-ratio...) TRỎ detector thật (qa_boundary/breath/
   onset/prosody/dialogue R188-191 exists), số ngưỡng = calibrate (không bịa — R195).
3. `governance/blueprint/bp8/distribution_spec.yaml` — video/publisher/analytics contract
   (planned; analytics có `tools/analytics_populate.py` exists — trỏ).
4. `governance/blueprint/bp8/00_production.md` (11-element).
5. Validator: mọi stage exists trỏ tool thật · chuỗi stage khớp runtime_flow BP4 (drift = FAIL) ·
   gate khai phải là gate ĐANG wired (grep điểm gọi — named≠enforced!) · planned đủ metadata.
6. Negative test: stage exists tool ma · chuỗi lệch BP4 · gate khai không wired · ngưỡng hardcode.

## MUTATION AUDIT SẼ BẮN
tool ma trong stage exists · render_chain lệch runtime_flow · khai gate "auto-caption" không tồn tại.
STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.

---
# SAU KHI BP8 LOCK: báo kiểm duyệt chạy FINAL AUDIT BP0-BP8 → Mr.Long tag `system-blueprint-v1.0` → G2.
