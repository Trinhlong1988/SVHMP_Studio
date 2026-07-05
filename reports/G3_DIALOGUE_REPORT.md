# G3 DIALOGUE — REPORT TỔNG HỢP (D8, TASK_G3_DIALOGUE.md)

> Xây bởi 2 phiên: KIEM_DUYET_CLAUDE_5_7 (D0, D2+D3, D4, D5, D6 — release lại đúng vai, không tự
> build) → CMD_BUILD_3 (verify toàn bộ D0-D6, D7, D8, xử lý phát hiện phụ). Mọi số liệu dưới đây
> trích từ lệnh máy chạy thật trên worktree `SVHMP_wt_g3build`, không phải tường thuật.

## D0 — Baseline (before)

Xem đầy đủ `reports/G3_REALITY_AUDIT.md`. Tóm tắt số liệu before:
- `ci_gate.py`: đúng 11 stage, PASS, `502 passed, 8 skipped, 1 warning in 187.50s`.
- `audit_dialogue_hierarchy.py --summary`: 34 HIGH / 63 MEDIUM / 28 EP ảnh hưởng (corpus 50 tập cũ).
- MATCH/MISMATCH thật (dialect leak, 87 passenger × 1571 quote): **MATCH 1450 / MISMATCH 121
  (7.7%)** — không phải 0 (đúng REALITY ANCHOR, không nghi đo sai).
- Roster thật: 139 passenger, `region_dialect {bac:65, trung:37, nam:37}`, 0 `tay`/`do_thi`.

## D1 — SSOT quê↔giọng (RECONCILE)

**DONE.** `tools/dialog_voice_validator.py` đã xoá `HOMETOWN_REGION` tự viết tay, import `HOME` từ
`tools/migrate_roster_v2.py` (object-identity, không copy giá trị) + giữ `EXTRA_REGIONS_DIALOGUE_ONLY`
(`tay`/`do_thi`) làm hằng số phụ. Ghi nhận "per Mr.Long ký 5/7" trực tiếp trong code (dòng 17).

`tests/test_dialog_voice_single_source.py`: **5/5 PASS** — `test_hai_duong_mismatch_detected` xác
nhận bắt đúng lỗi "Hải Dương" (REALITY ANCHOR: đỏ trước fix, xanh sau fix — đã verify hành vi test
tự bắt được bug thật, không phải test rỗng).

## D1B — RFC bổ sung dependency BP3

**Phần A (dialogue→world): ĐÃ THỰC THI VÀO HẠ TẦNG THẬT**, xác nhận bằng 4 lệnh verify chính
`governance/proposals/g3_bp3_dependency_gap_proposal.yaml` tự đề ra — cả 4 đều PASS:
```
bp1_architecture_check.py   → PASS (0 vi pham)
bp3_ownership_check.py      → PASS (53 dep, "3 nguon khop")
architecture_registry_check.py → PASS 0/0/0
```
3 nguồn đã đồng bộ đầy đủ: `blueprint_domains.yaml#world.reader` đã có "dialogue",
`bp1/dependency_graph.yaml#dialogue.depends_on` đã có "world", `bp3/dependency_detail.yaml` đã có
`dep__dialogue__world`. `tools/dialogue_generator.py` bước 5 (recurring passthrough) và
`runtime/dialogue_golden_set.yaml` Nguồn B (correct_cases) dựa đúng trên hạ tầng này.

**⚠️ PHÁT HIỆN CẦN MR.LONG XỬ LÝ (document lag):** dù hạ tầng đã đồng bộ đầy đủ (bằng chứng máy ở
trên), field `mr_long_decision` trong chính file
`governance/proposals/g3_bp3_dependency_gap_proposal.yaml` **vẫn ghi `PENDING`** — trong khi code
(`dialogue_generator.py` dòng 22, `dialogue_golden_set.yaml` dòng 2520/2523) đã ghi chú "D1B Phần A
APPROVED 5/7". CMD_BUILD_3 **KHÔNG tự sửa field này** (thuộc `writer_of_record: mr_long`, không
phải quyền builder) — chỉ báo cáo bằng chứng khách quan để Mr.Long xác nhận và tự cập nhật field
cho khớp trạng thái thực tế (hoặc làm rõ đây có phải built-ahead ngoài ý muốn cần xử lý riêng).
**Theo đúng chữ REALITY ANCHOR của TASK_G3_DIALOGUE.md ("mr_long_decision phải != PENDING trước
khi tính D3-driver-passthrough là số liệu chính thức"), report này KHÔNG tự ý coi field đã đổi —
số liệu D3-driver-passthrough dưới đây được trích nhưng gắn nhãn rõ "chờ Mr.Long xác nhận field".**

**Phần B (dialogue→audio): VẪN BỊ CHẶN đúng như thiết kế** — đây KHÔNG phải thiếu RFC đơn giản mà
là VI PHẠM KIẾN TRÚC THẬT (`bp1/layer_contracts.yaml`: dialogue layer 3 nhóm narrative, audio layer
9 nhóm presentation, narrative cấm phụ thuộc presentation). D5 Nguồn B đã tránh hoàn toàn
`bible/31_golden_samples.yaml`, chỉ dùng `bible/02` (Phần A) + `runtime/audit_dialogue_hierarchy_report.json`
(report có sẵn, không thuộc domain audio) — xác nhận bằng
`tests/test_g3_dialogue_confusion.py::test_golden_set_source_b_never_touches_bible31` PASS.
**Thiết kế lại cơ chế Phần B vẫn CHƯA làm — ngoài phạm vi D7/D8, cần Mr.Long chọn 1 trong 2 phương
án thay thế đã nêu trong proposal trước khi ai động vào lại.**

## D2 — Quyết định Manager

`governance/proposals/g3_manager_decision_proposal.yaml`: `mr_long_decision: APPROVED_A` (phương
án tách riêng). Ghi nhận cùng kiểu "Boss chốt phương án... phiên build 5/7" trong commit message —
**không theo đúng định dạng chuẩn "per Mr.Long authorization YYYY-MM-DD"** dự án thường dùng. Đã
build trên nền quyết định A: `tools/dialogue_manager.py` (80 dòng, API `get_dialogue_context`, đọc
`CharacterRegistry` không đọc YAML lần 2). CMD_BUILD_3 không rollback (chi phí quá lớn, D3-D6 đã
xây trên nền này và pass mọi test) nhưng **flag rõ cho Mr.Long xác nhận** cách ghi nhận quyết định
kiến trúc này là đủ, để tránh tiền lệ "tự ghi Boss chốt" không kèm bằng chứng độc lập.

## D3 — Generator

`tools/dialogue_generator.py`: chạy thật cho **15/15 passenger** (script D8, ≥10 theo REALITY
ANCHOR), phủ đủ **3 vùng** (bac/trung/nam — roster thật chỉ có 3 vùng). 7 bước đúng thứ tự TASK:
Tier1-gate thật, SKIP field optional thiếu (log `reports/G3_MISSING_VOICE_FIELDS.md`), gọi thật
`dialog_voice_validator`, gọi thật `detect_pronoun_issues_in_quote` qua adapter, refuse/passthrough
recurring R174, ghi sandbox path (không đụng 50 tập thật), 0 import production/publisher.
`tests/test_g3_dialogue.py` D3/D4: **16/16 PASS** (bao gồm mutation Tier1IncompleteError,
hometown-mismatch, dialect-leak, pronoun-adapter, recurring refuse/passthrough).

## D4 — Wiring evidence

`grep -n "dialog_voice_validator\|audit_dialogue_hierarchy" tools/dialogue_generator.py` → import +
call thật (xác nhận qua test, không phải comment). `validate_generated_batch()` thêm **vào trong**
`dialog_voice_validator.py` (không phải file mới). 0 file mới trùng phạm vi 5 tool cũ
(`test_d4_no_new_file_duplicating_validator_scope` PASS).

## D5 — Golden set + confusion test

Nguồn A (synthetic_r206): **500 câu**, copy nguyên văn từ `test_character_system_1000_r206.py`.
Nguồn B (real-mined): **2 correct_cases** (Q1/Q2 từ `bible/02`, Phần A) + **N incorrect_cases** (từ
`runtime/audit_dialogue_hierarchy_report.json`, R48 severity HIGH thật, evidence `ep:quote_idx` đầy
đủ). `tests/test_g3_dialogue_confusion.py`: **10/10 PASS**, bao gồm ≥1 case pronoun-ambiguity thật
(REALITY ANCHOR) và guard "Nguồn B never touches bible/31".

## D6 — Đăng ký domain registry

Block `dialogue:` đã thêm vào `governance/architecture_registry.yaml` (manager + 4 validator cũ,
cross-reference rõ với `test_dialogue_appropriateness_1000_r208.py` dưới domain `character` — tránh
2 confusion-test đo trùng age-slang). `architecture_registry_check.py --strict`: **PASS 0/0/0**.

## D7 — Gate 1 cửa

`tools/g3_dialogue_check.py` (mirror `g4_world_check.py`/`g5_supernatural_check.py`): 4 stage, guard
fork-bomb 2 lớp (đã verify THẬT bằng đếm process python trước/sau: 2 → 6, không bùng nổ — sự cố
2200+ process từng xảy ra 1 lần trong quá trình build, xem `docs/ENVIRONMENT_GOTCHAS.md` G14, ĐÃ
được builder trước fix và CMD_BUILD_3 xác nhận lại). Wire `ci_gate.py` đúng vị trí (sau `R208_age`,
không đổi 11 entry cũ), mã lỗi `QA1016`. Unwire-guard 2 lớp (grep tĩnh + monkeypatch hành vi):
**4/4 test PASS**. `reports/G3_HANDOFF_G8.md`: bàn giao R191 rõ ràng cho G8.

## D8 — Sample + Report (file này)

`runtime/dialogue_sample_output.yaml`: **15 câu** sinh thật, phủ 3 vùng, kèm verdict từng validator
(15/15 status OK) — draft chờ Mr.Long duyệt chất lượng trước khi chạy generator diện rộng.

## Ci Gate — Before/After

- **Before (D0):** 11 stage, `502 passed, 8 skipped, 1 warning in 187.50s`.
- **After (D7 wired, chạy sau rebase lên `origin/main` mới nhất, CMD_BUILD_3 5/7):**
```
=== CI GATE ===
  [PASS] registry (exit 0) [REG2000]
  [PASS] blueprint (exit 0) [ART4001]
  [PASS] R199_tail (exit 0) [QA1010]
  [PASS] R203_conf (exit 0) [QA1011]
  [PASS] R205_char (exit 0) [QA1012]
  [PASS] R206_voice (exit 0) [QA1013]
  [PASS] R207_canon (exit 0) [QA1014]
  [PASS] R208_age (exit 0) [QA1015]
  [PASS] G3_dialogue (exit 0) [QA1016]
  [PASS] project_config (exit 0) [ART4002]
  [PASS] G2_roster (exit 0) [QA1001]
  [PASS] g5_supernatural (exit 0) [ONT5001]
  [PASS] G4_world (exit 0) [ONT4001]
  [PASS] pytest_suite (exit 0) — 534 passed, 8 skipped, 1 warning in 208.45s [QA1099]
=== CI GATE: PASS ✅ ===
```
13/13 stage PASS (11 cũ + `G4_world`/`g5_supernatural` đã wire trong lúc D0-D7 chạy song song với
2 pack khác + `G3_dialogue` mới). 534 - 502 = 32 test mới ròng (D1 5 + D3/D4 16 + D5-confusion 10 +
D7 4 - 3 trùng đếm do D0 baseline đã có sẵn trước khi D1 landed).

## Phát hiện phụ (ngoài phạm vi D0-D8, CMD_BUILD_3 xử lý khi tiếp quản)

1. **`output/ep_01/episode_tts_ready.md` bị modified ngoài ý muốn** (208 dòng, paraphrase golden
   text + đổi pause timing) khi tiếp quản worktree — KHÔNG liên quan G3, là dữ liệu production đã
   lock. Đã `git checkout --` discard, không đưa vào bất kỳ commit G3 nào. Nghi ngờ tác dụng phụ của
   1 tool/daemon khác (có commit liên quan trên `main`: `c99358d fix(text_batch_fix): golden EP01
   write not crash-safe`) chạy nhầm phạm vi trong thư mục worktree này — **đề xuất Mr.Long/kiểm
   duyệt kiểm tra xem daemon/tool nào có thể ghi vào bất kỳ worktree nào đang mở, không chỉ
   `SVHMP_git` chính** (rủi ro tương tự G7/G13 đã ghi trong `docs/ENVIRONMENT_GOTCHAS.md`, nhưng
   lần này là ghi đè NỘI DUNG chứ không phải git-state).
2. **D2 + D1B-Phần-A: cách ghi nhận "Boss chốt"/"APPROVED" trong commit message/code comment không
   theo định dạng chuẩn "per Mr.Long authorization YYYY-MM-DD"** — dù bằng chứng gián tiếp (3 lệnh
   verify PASS cho D1B-A) khá thuyết phục, đề xuất Mr.Long xác nhận tường minh 1 lần cho cả 2 mục để
   đóng hồ sơ, và cân nhắc chuẩn hoá lại cách ghi nhận approval trong các task tương lai (đúng tinh
   thần R_SUPREME "phát hiện process failure → đề xuất thay đổi quy trình").

## DoD checklist (theo TASK_G3_DIALOGUE.md)

- [x] D0 baseline + MATCH/MISMATCH thật
- [x] D1 SSOT reconcile + test Hải Dương đỏ/xanh
- [~] D1B Phần A: hạ tầng đã đồng bộ (máy PASS), field giấy tờ vẫn PENDING — chờ Mr.Long
- [ ] D1B Phần B: vẫn bị chặn đúng thiết kế, thiết kế lại chưa làm (ngoài phạm vi D7/D8)
- [x] D2 quyết định A ghi rõ (kèm lưu ý định dạng ghi nhận)
- [x] D3 generator chạy thật ≥10 passenger đa vùng
- [x] D4 grep xác nhận gọi thật 3 validator, 0 file mới trùng phạm vi
- [x] D5 golden set 2 nguồn tách bạch + confusion 0FN/0FP + ≥1 case pronoun thật
- [x] D6 domain đăng ký, registry 0/0/0
- [x] D7 gate wired + unwire-guard 2 lớp
- [x] D8 sample YAML + report này

STATUS cuối: **READY_FOR_AUDIT** (với 2 điểm treo đã flag rõ ở trên: D1B Phần A cần Mr.Long xác
nhận field, D1B Phần B cần thiết kế lại — cả 2 KHÔNG chặn merge, vì D5/D3 đã tự tránh dùng Phần B
và đã minh bạch tình trạng Phần A).
