# TASK PACK5 (quality) — KHUNG CHO CMD_BUILD (kiểm duyệt thiết kế 2/7, Mr.Long duyệt)

> Chạy SAU khi P1 lock xong. Nguyên tắc: FORMALIZE hạ tầng QA **ĐÃ CÓ THẬT** —
> mọi enforcer dưới đây đã verify tồn tại trên disk (kiểm duyệt Test-Path từng cái 2/7).
> Cái gì CHƯA wire → dán nhãn `(ROADMAP — CHƯA gate)`. CẤM claim gate cho thứ không chạy
> (lesson pack4: "named ≠ enforced").

## 4 doc — governance/pack5/ (11-element/doc, 0 placeholder, khuôn pack4)

### 19_qa_pipeline.md — Render-time content-QA pipeline
- Enforcer ENFORCED THẬT: gate TRONG render = `tools/character_manager.py`
  (`CharacterRegistry.episode_completeness` + `render_gate_lines` — svhmp_v13_render
  L339/L344, kiểm duyệt đọc code 2/7).
- `tools/svhmp_preflight_qa.py` = content-QA STANDALONE — render KHÔNG gọi nó (chỉ comment
  tham chiếu; xem BUG P0 dưới). Doc phải trình bày đúng vai: preflight = bước verify-chain riêng.
- Scope: preflight → render(gate G2) → verify (`svhmp_final_verify.py`, `svhmp_100check_master.py`).
- Phân ranh với pack3/11 (ci_gate = code-QA; doc này = content-QA render-time — reconcile, không nhân đôi).
- ⚠️ KHÔNG sửa `svhmp_v13_render.py` (LOCKED v1.3) — chỉ mô tả + trỏ.

### 20_golden_dataset.md — Golden samples + calibration policy (R195)
- Enforcer: `bible/31_golden_samples.yaml` (data) + `tools/hardcode_classifier.py`
  (INVENTORY — phân loại hardcode nào cần calibrate theo R195; nó KHÔNG tự calibrate).
- Tool calibrate-từ-Golden tự động: **CHƯA CÓ → dán (ROADMAP — CHƯA gate)**, ghi thẳng.
- Codify bài học: detector PHẢI calibrate từ Golden Audio, chứng minh bằng confusion-matrix
  (R203 240-case) — không tin detector chưa calibrate.

## 🐞 BUG P0 — FIX TRONG TASK NÀY (kiểm duyệt tái hiện 2/7)
`svhmp_final_verify.py` L95: `subprocess.run(['python', r'C:\tmp\svhmp_preflight_qa.py',...])`
và `svhmp_100check_master.py` L31: `PREFLIGHT = r'C:\tmp\...'` — **C:\tmp\svhmp_preflight_qa.py
KHÔNG TỒN TẠI** (Test-Path False) → bước preflight của final_verify ĐANG CHẾT. 2 lớp bug cũ
tái xuất: hard-path C:\tmp + `'python'` trần (Store-stub PATH).
FIX: repath `Path(__file__).parent / 'svhmp_preflight_qa.py'` + `sys.executable`;
kèm negative-test khoá (path resolve trong repo). KHÔNG sửa logic preflight.

### 21_detector_suite.md — Voice/audio detector suite (R188–R191)
- Enforcers: `tools/qa_boundary_artifact.py` · `qa_breath_artifact.py` · `qa_onset_artifact.py`
  · `qa_prosody_collapse.py` · `qa_dialogue_identity.py` · `tools/audio_qa_metrics.py`.
- Certify: `tests/test_voice_qa_tools.py` (ĐÃ trong pytest/ci_gate — ENFORCED).
- Ghi known-limitation thật: F8 prosody false-negative (deep-audit 2/7) = ROADMAP.

### 22_waiver_watch.md — Waiver policy (R204) + QA watch daemon
- Enforcers: `runtime/qa_waivers.json` (waiver explicit + LEAD duyệt, chống re-spam)
  + `tools/qa_watch.py` + `tools/qa_watch_supervisor.py` (single-instance lock + circuit breaker).
- Certify: `tests/test_supervisor_dedup.py` (ĐÃ có).
- Known-limitation: F2 harness/daemon còn nợ (deep-audit) = ROADMAP.

## Bắt buộc kèm
1. `tests/test_pack5_docs.py` — copy khuôn `test_pack4_docs.py`: exist+nonempty · 11-element
   · no-placeholder · reference_real_enforcers (19→svhmp_preflight_qa.py · 20→hardcode_classifier.py
   · 21→qa_prosody_collapse.py · 22→qa_watch_supervisor.py).
2. Map mọi file mới vào `governance/file_index.yaml` → registry giữ 0/0/0.
3. KHÔNG tạo tool mới (mọi enforcer đã có). Nếu phát hiện enforcer nào KHÔNG làm đúng
   điều doc định claim → dán ROADMAP + báo, KHÔNG bịa.

## Self-test trước khi ký (dán lệnh + exit-code + tail)
```
python tools/architecture_registry_check.py     # 0/0/0
python -m pytest tests/ -q                      # all pass (gồm test_pack5_docs)
python tools/cmd_pipeline_gate.py --ref origin/main --pack pack5_quality \
  --tag pack5-quality-v1.0 --doc-test tests/test_pack5_docs.py --skip-build
#  → ARCH+QA XANH; RELEASE ĐỎ (pack5=todo) = ĐÚNG — lock là chữ ký Mr.Long sau audit.
```
Commit qua worktree riêng · pull --rebase trước · log_ping + push sau (R200) · KHÔNG --no-verify
· KHÔNG tự đổi promotion_status/tag. Sign-off: `reports/build_report.md` (local, không commit)
dòng `READY FOR AUDIT = YES` chỉ khi 50/50 đã chạy. Dòng cuối: `STATUS: READY_FOR_AUDIT` / `NOT_READY`.

## Sau khi READY
Kiểm duyệt audit adversarial (soi từng chữ + đối chiếu enforcer thật) → PASS → Mr.Long ký
"lock P5" → freeze_gate 5/5 → Final Governance Audit P1–P5 → tag `governance-v1.0`.
