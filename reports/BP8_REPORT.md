# BP8 REPORT — Production Architecture (candidate, chờ audit 7 bước + Mr.Long ký)
> **Pack CUỐI CÙNG chuỗi BP-C (BP0-BP8).** Lock xong → báo kiểm duyệt FINAL AUDIT BP0-BP8 → Mr.Long tag `system-blueprint-v1.0`.

## Số đo (REALITY ANCHOR — luật 9: validator PASS trên dữ liệu THẬT)

| Số đo | Giá trị | Nguồn máy |
|---|---|---|
| Stage khai | **7/7** mirror CHÍNH XÁC `bp4/runtime_flow.yaml` hop 3-9 (LOCKED) | `bp8_production_check.py` máy đếm |
| Golden criteria khai | **8/8** (logic/language/tts/boundary/breath/prosody/onset/dialogue_identity) | máy đếm |
| Checker trên data thật | **exit 0, 0 violation** | `tools/bp8_production_check.py` |
| Mutation test | **19/19 pass** | `tests/test_bp8_production.py` |
| Gate `automated` có grep_evidence xác minh | 6/6 (FULL_TEXT_GATE, G2_CHARACTER_GATE_PREFLIGHT/RENDER, R90_STAGE1, R41_POST_RENDER_GATE, SERVER_CI) | verify thủ công bằng Grep trước khi ghi (xem "Ghi chú kỹ thuật") |
| Gate `manual` (có thật, chưa auto-wire) | 1/1 (AUDIO_METRICS_SCAN) | không bịa "automated" |

## Ghi chú kỹ thuật quan trọng (verify TRƯỚC khi ghi, không suy luận)

Trước khi khai bất kỳ gate nào là `enforcement_mode: automated`, đã **grep xác nhận điểm gọi thật** trong file nguồn cho từng cái:
- `FULL_TEXT_GATE`: `svhmp_preflight_qa.py` gọi subprocess `qa_eol_diacritic.py` (dòng 171).
- `G2_CHARACTER_GATE_PREFLIGHT`: `svhmp_preflight_qa.py` import `CharacterRegistry` (dòng 199-205).
- `G2_CHARACTER_GATE_RENDER`: `svhmp_v13_render.py` dòng 339 (`episode_completeness`) + 344 (`render_gate_lines`).
- `R41_POST_RENDER_GATE_HARDLOCK`: `git_hook_pre_commit.py` gọi `tools/post_render_gate.py --ep N` (dòng 94), wired qua `.githooks/pre-commit`.
- `SERVER_CI`: `.githooks/pre-push` dòng 17 gọi `tools/ci_gate.py`, block push nếu FAIL.

**Phát hiện trong lúc verify:** ban đầu định khai gate audio (`svhmp_audio_qa.py`) trỏ `tools/audio_qa_metrics.py` làm "wired" — grep xác nhận **KHÔNG có file .py nào gọi `audio_qa_metrics.py` hay `svhmp_audio_qa.py` tự động**. Đây là bước QA audio hiện tại **người chạy tay, đọc report** (vd `AUDIO_QA_REPORT_v100.md`), KHÔNG phải gate tự động. Đã sửa lại thành `enforcement_mode: manual` — tránh đúng lỗi "named ≠ enforced" mà TASK cảnh báo trước.

## Defect phát hiện trong lúc build (đã route đúng kênh, KHÔNG tự sửa)

`bible/31_golden_samples.yaml` dòng 113 lỗi cú pháp YAML (chuỗi quote không bọc hết) — **crash cứng mọi YAML parser** (không riêng loader strict), nghiêm trọng hơn defect bible/00 R142/R143 (đó chỉ là silent-overwrite, còn đây crash toàn file). Đã báo kiểm duyệt/Mr.Long kèm đề xuất fix 1 dòng; kiểm duyệt xác nhận tái hiện đúng + test bản vá sạch + quét toàn file không còn ca nào khác — đang chờ Mr.Long "ok" để áp fix "per Mr.Long authorization" (đúng thủ tục dù chỉ là lỗi chính tả kỹ thuật). `golden_output.yaml` thiết kế né vùng vỡ: SoT trỏ `bible/31_golden_samples.yaml` **KHÔNG kèm `key:`** (chỉ xác nhận file tồn tại trên đĩa, không cần parse toàn bộ) — khi bible/31 được fix, có thể amendment nhẹ thêm `key:` cụ thể sau.

## Deliverables

1. `governance/blueprint/bp8/render_chain.yaml` — 7 stage (generator→qa_runtime→tts→audio→production→video→publisher), mỗi stage đối chiếu domain/input/output/tool.status/path CHÍNH XÁC với `bp4/runtime_flow.yaml` hop 3-9 (LOCKED) — không rebuild, không tả sai. Thêm gate (6 automated + 1 manual, đều có bằng chứng grep) + failure_route.
2. `governance/blueprint/bp8/golden_output.yaml` — R196: 8 tiêu chí FORMAT trỏ detector thật (`publish_score.py` + 5 tool R188-191), 0 số ngưỡng hardcode (threshold_source chỉ mô tả nguồn calibrate).
3. `governance/blueprint/bp8/distribution_spec.yaml` — video/publisher planned mirror BP4 hop 8/9; analytics exists (`tools/analytics_populate.py`) nhưng input từ publish_artifact vẫn planned (gap ghi rõ, không bịa liên kết).
4. `governance/blueprint/bp8/00_production.md` — 11-element.
5. `tools/bp8_production_check.py` — DUP-KEY loader single-impl + version khớp 3 file; drift-vs-BP4 (domain/input/output/tool); gate named≠enforced (automated bắt buộc grep_evidence); numeric-leak toàn file (tái dùng `_numeric_leaks`); detector/tool-má.
6. `tests/test_bp8_production.py` — 19 test: đủ 4 đòn TASK báo trước (tool má, render_chain lệch runtime_flow, gate "auto-caption" không tồn tại, ngưỡng hardcode) + drift domain/hop/io, named≠enforced, planned-thiếu-metadata, detector-má, distribution drift.

## Ghi chú cho auditor

- Registry: `bp8_production: candidate` (1 dòng, không dup-key).
- **Sau khi BP8 lock: báo kiểm duyệt chạy FINAL AUDIT BP0-BP8 → Mr.Long tag `system-blueprint-v1.0`** (đúng chỉ dẫn cuối TASK_BP8_PRODUCTION.md).
- Builder không kết luận PASS/FREEZE — chỉ READY FOR AUDIT.
