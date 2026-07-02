# PACK 5 — 21_detector_suite.md — Voice/Audio Detector Suite (R188–R191)
> Enforce: `tools/qa_boundary_artifact.py` · `tools/qa_breath_artifact.py` · `tools/qa_onset_artifact.py` · `tools/qa_prosody_collapse.py` · `tools/qa_dialogue_identity.py` · `tools/audio_qa_metrics.py` · chứng thực: `tests/test_voice_qa_tools.py` (trong `pytest tests/` + ci_gate — ENFORCED).

**Mission:** Máy phát hiện lỗi audio TRƯỚC tai Mr.Long — mỗi lớp artifact đã từng lọt phải có detector trực chờ.
**Purpose:** Codify suite detector voice/audio R188–R191 đang tồn tại thật trên disk (kiểm duyệt Test-Path 2/7), vai trò từng detector và giới hạn thật của chúng.
**Scope:** Detector chạy trên AUDIO đã render. KHÔNG gồm text-QA trước render (doc 19), nguồn threshold (doc 20), waiver/daemon (doc 22).
**Authority:** Phái sinh R188–R191 + R195 (threshold phải calibrate — xem doc 20); doc không tự tạo quyền.
**Responsibilities:**
- `qa_boundary_artifact.py` — artifact biên chunk (click/gap tại điểm nối).
- `qa_breath_artifact.py` — hơi thở/breath artifact bất thường.
- `qa_onset_artifact.py` — onset đầu chunk (attack vỡ/click đầu).
- `qa_prosody_collapse.py` — sập prosody (pitch drop bất thường kiểu 220→110Hz).
- `qa_dialogue_identity.py` — nhận dạng giọng nhân vật trong dialog (đúng voice profile R210).
- `audio_qa_metrics.py` — metric nền (peak/LUFS/duration) cho các detector dùng chung.
- Certify: `tests/test_voice_qa_tools.py` — pytest-func ĐƯỢC collect trong `pytest tests/` và ci_gate (đã gỡ khỏi ignore sau deep-audit F8 — ENFORCED).
**Workflow:** audio render xong → chạy detector suite → issue nào phát hiện = VIOLATION (vào flow waiver doc 22 nếu Mr.Long duyệt bỏ qua) → fix → re-render → detector xanh mới được verify tiếp.
**Mandatory Rules:** (1) Detector mới = tool mới → qua Change Request Gate 6 câu (R211) + map registry. (2) Threshold detector tuân chính sách calibrate doc 20 — CẤM chỉnh tay không bằng chứng golden. (3) CẤM khai "audio sạch" khi có detector đỏ chưa waiver.
**PASS Criteria:** cả 6 detector exit 0 trên audio đích · `tests/test_voice_qa_tools.py` xanh trong ci_gate (ENFORCED).
**FAIL Criteria:** bất kỳ detector exit khác 0 không waiver hợp lệ · test_voice_qa_tools đỏ → ci_gate đỏ.
**Examples:** chunk nối bị click → `qa_boundary_artifact` đỏ → fix crossfade → xanh; pitch sập cuối câu 220→110Hz → `qa_prosody_collapse` bắt (case synthetic đã chứng minh trong test F8-fix); giọng ông cụ đọc thoại cô y tá → `qa_dialogue_identity` flag.
*(ROADMAP — CHƯA gate, known-limitation thật từ deep-audit 2/7 F8: prosody false-negative trên REAL AUDIO corpus chưa được chứng minh hết — bản fix mới chứng minh trên synthetic case; calibrate full trên golden real-audio theo doc 20 là nợ. KHÔNG khai "prosody detector bắt mọi collapse".)*
**Promotion Rules:** theo mục Promotion Rules ở `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.

## Reconcile
Suite này TIÊU THỤ threshold từ chính sách doc 20, KHÔNG tự định nghĩa nguồn threshold. Kết quả detector đổ vào flow waiver doc 22 — không nhân đôi chính sách waiver ở đây.
