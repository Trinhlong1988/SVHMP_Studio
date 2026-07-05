# G3 → G8 HANDOFF — R191 speaker-identity (qa_dialogue_identity.py)

> TASK_G3_DIALOGUE.md D7. `tools/qa_dialogue_identity.py` (R191) chạy trên WAV **đã render**
> (MFCC-embedding, cosine threshold 0.85) — không thể và không nên nằm trong vòng lặp
> validate-trước-khi-ghi của `dialogue_generator.py` (text-only), và `ci_gate.py` chạy TRƯỚC
> render nên không có WAV để kiểm.

## G3 đã làm gì với R191
- KHÔNG import `librosa`/`qa_dialogue_identity` vào `tools/dialogue_generator.py`.
- KHÔNG wire `qa_dialogue_identity.py` vào `tools/ci_gate.py` CHECKS (xác nhận bằng
  `tests/test_g3_dialogue.py::test_r191_qa_dialogue_identity_not_wired_in_ci_gate`).
- Chỉ xác nhận tool **tồn tại và chạy được** (`python tools/qa_dialogue_identity.py --wav <path>`),
  không tự nhận đã "enforce" R191 ở lớp text.

## Việc của G8 (QA Runtime, audio đã render)
1. Sau khi TTS render xong 1 tập (`svhmp_v13_render.py`), gọi
   `python tools/qa_dialogue_identity.py --wav output/ep_XX/*.wav` cho từng file audio.
2. Nếu `verdict == FAIL` (cosine < 0.85 ở ≥1 segment severity HIGH) → route lại render hoặc
   flag cho QA thủ công — KHÔNG phải việc của dialogue_generator.py (đã sinh xong TEXT trước
   khi render).
3. G8 cần tự quyết định ngưỡng retry/escalation — G3 không đề xuất chính sách này (ngoài
   phạm vi domain `dialogue`).

## Tham chiếu
`tools/qa_dialogue_identity.py`, `bible/37#tier_1_mandatory.voice`, TASK_G3_DIALOGUE.md D7,
`governance/architecture_registry.yaml` (domain `dialogue`, cross-reference validators).
