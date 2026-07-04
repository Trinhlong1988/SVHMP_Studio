# BP8 — 00_production.md — Production Architecture (render chain + golden output + distribution)
> Enforce: `tools/bp8_production_check.py` · chứng thực: `tests/test_bp8_production.py` · data: `governance/blueprint/bp8/render_chain.yaml` + `governance/blueprint/bp8/golden_output.yaml` + `governance/blueprint/bp8/distribution_spec.yaml`.

**Mission:** Kiến trúc chuỗi render → phân phối: formalize chuỗi ĐANG CHẠY THẬT (generator/tts/audio/production) + spec planned cho video/publisher/analytics. RECONCILE — cấm rebuild, cấm tả sai hệ đang chạy.

**Purpose:** Khóa "cái gì chảy qua công cụ nào, gate nào thật sự chặn" trước khi tag `system-blueprint-v1.0`: mọi stage `exists` phải trỏ tool có thật trên đĩa, mọi gate khai `automated` phải có bằng chứng grep điểm gọi thật (chống lớp bug "built ≠ wired" tái diễn — case thật a171120 G2 CHARACTER_GATE, F1 git hooks, R198 cap_peak).

**Scope:** `render_chain`: 7 stage (generator→qa_runtime→tts→audio→production→video→publisher), mirror CHÍNH XÁC `bp4/runtime_flow.yaml` hop 3-9 (LOCKED), thêm gate + failure_route. `golden_output`: R196 Engineering PASS ≠ Production, tiêu chí FORMAT trỏ detector thật, số ngưỡng = calibrate (R195, không bịa). `distribution_spec`: video/publisher (planned, mirror BP4) + analytics (exists, input còn thủ công vì publisher chưa có). KHÔNG viết engine mới, KHÔNG sửa render LOCKED (`svhmp_v13_render.py`).

**Authority:** BP0 v2.0 + BP1-BP7 LOCKED = nguồn luật. `bp4/runtime_flow.yaml` (LOCKED v1.0) là NGUỒN THẬT DUY NHẤT cho hop/status/path — BP8 chỉ bổ sung gate/failure_route, không đổi domain/status/path khác BP4 (drift = FAIL). Đổi render chain thật = RFC + Mr.Long (đụng hệ đang chạy production).

**Responsibilities:** `render_chain`: mỗi stage `bp4_hop` khớp đúng hop BP4; gate có `enforcement_mode` (automated = bắt buộc grep_evidence điểm gọi thật; manual = công cụ có thật nhưng chưa auto-wire, không bịa "automated"). `golden_output`: FORMAT tiêu chí trỏ detector R188-191 (qa_boundary/breath/onset/prosody/dialogue_identity, đều exists) + golden reference (bible/31 + EP01 golden text) — số ngưỡng cụ thể KHÔNG được hardcode ở đây (calibrate từ golden, R195). `distribution_spec`: video/publisher giữ nguyên planned + 5 metadata mirror BP4; analytics đã có tool thật nhưng input từ publish_artifact vẫn planned (gap ghi rõ, không bịa liên kết).

**Workflow:** sửa data → `bp8_production_check.py` exit 0 → pytest mutation → commit R200 → audit 7 bước → Mr.Long ký → **SAU KHI BP8 LOCK: báo kiểm duyệt chạy FINAL AUDIT BP0-BP8 → Mr.Long tag `system-blueprint-v1.0`**.

**Mandatory Rules:** (1) Stage/video/publisher status/path PHẢI khớp CHÍNH XÁC BP4 runtime_flow — lệch (thêm/bớt/đổi domain/path) = FAIL. (2) Gate `enforcement_mode: automated` KHÔNG có grep_evidence hợp lệ = FAIL (named ≠ enforced). (3) Stage `tool.status: exists` nhưng path không tồn tại trên đĩa = TOOL-MA FAIL. (4) `golden_output` KHÔNG chứa số ngưỡng hardcode ngoài valid_range (mirror R195/BP6 — scan toàn file ngay từ đầu, tái sử dụng `_numeric_leaks`). (5) DUP-KEY loader single-impl + version khớp 3 file bp8.

**PASS Criteria:** `bp8_production_check.py` exit 0 + mutation battery xanh trong `pytest tests/` (ENFORCED qua ci_gate pytest_suite).

**FAIL Criteria:** stage exists trỏ tool má / render_chain lệch runtime_flow / khai gate "auto-caption" không tồn tại / ngưỡng hardcode trong golden_output → exit 1.

**Examples:** đổi `tts` stage tool thành `tools/khong_ton_tai.py` → FAIL TOOL-MA; thêm hop thứ 10 "auto_caption" không có trong BP4 → FAIL DRIFT-BP4; khai gate mới `enforcement_mode: automated` nhưng không tìm thấy điểm gọi trong file nguồn → FAIL NAMED-KHONG-ENFORCED; `golden_output` thêm `min_loudness_db: -16` → FAIL R195-HARDCODE.

**Promotion Rules:** `bp8_production: candidate` — Builder không lock/tag; Mr.Long ký sau audit (reconcile `governance/constitution/00_constitution.md`). REALITY ANCHOR (luật 9): checker chạy trên data bp8 THẬT + số đo trong `reports/BP8_REPORT.md`. Đây là **pack CUỐI CÙNG của chuỗi BP-C (BP0-BP8)** — lock xong → FINAL AUDIT → tag `system-blueprint-v1.0`.

## Ghi chú semantics (kiểm duyệt phán khi audit)
Audio stage (`svhmp_audio_qa.py`) và `AUDIO_METRICS_SCAN` gate được khai `enforcement_mode: manual` — đã grep xác nhận KHÔNG có file `.py` nào tự động gọi `svhmp_audio_qa.py` (không như `post_render_gate.py`/`G2_CHARACTER_GATE` có bằng chứng gọi trực tiếp). Đây phản ánh đúng thực trạng dự án (QA audio hiện là bước người-chạy-tay-đọc-report, ví dụ `AUDIO_QA_REPORT_v100.md`), KHÔNG phải thiếu sót của BP8 — bịa "automated" ở đây mới là vi phạm nguyên tắc named≠enforced.
