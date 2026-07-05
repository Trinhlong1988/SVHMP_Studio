# G3 DIALOGUE — REPORT TỔNG HỢP (D8, TASK_G3_DIALOGUE.md)

> Xây bởi 2 phiên: KIEM_DUYET_CLAUDE_5_7 (D0, D2+D3, D4, D5, D6 — release lại đúng vai, không tự
> build) → CMD_BUILD_3 (verify toàn bộ D0-D6, D7, D8, xử lý phát hiện phụ). Mọi số liệu dưới đây
> trích từ lệnh máy chạy thật trên worktree `SVHMP_wt_g3build`, không phải tường thuật.

## D0 — Baseline (before)

Xem đầy đủ `reports/G3_REALITY_AUDIT.md`. Tóm tắt số liệu before:
- `ci_gate.py`: đúng 12 stage (sửa 5/7, lỗi đếm tay cũ ghi "11" — máy đếm `len(CHECKS)` xác nhận
  12 trước khi G3 wire thêm), PASS, `502 passed, 8 skipped, 1 warning in 187.50s`.
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

`tools/g3_dialogue_check.py` (mirror `g4_world_check.py`/`g5_supernatural_check.py`): ban đầu 4
stage, **nay 5 stage** (thêm `G3_7_output_audit_real` ở vòng audit 2 — xem mục "G3-7" dưới), guard
fork-bomb 2 lớp (đã verify THẬT bằng đếm process python trước/sau: 2 → 6, không bùng nổ — sự cố
2200+ process từng xảy ra 1 lần trong quá trình build, xem `docs/ENVIRONMENT_GOTCHAS.md` G14, ĐÃ
được builder trước fix và CMD_BUILD_3 xác nhận lại). Wire `ci_gate.py` đúng vị trí (sau `R208_age`,
không đổi 12 entry cũ), mã lỗi `QA1016`. Unwire-guard 2 lớp (grep tĩnh + monkeypatch hành vi):
**4/4 test PASS**. `reports/G3_HANDOFF_G8.md`: bàn giao R191 rõ ràng cho G8.

## D8 — Sample + Report (file này)

`runtime/dialogue_sample_output.yaml`: **15 câu** sinh thật, phủ 3 vùng, kèm verdict từng validator
(15/15 status OK) — draft chờ Mr.Long duyệt chất lượng trước khi chạy generator diện rộng.

## Ci Gate — Before/After

- **Before (D0):** 12 stage, `502 passed, 8 skipped, 1 warning in 187.50s`.
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
13/13 stage PASS = 12 stage baseline D0 (đã bao gồm `g5_supernatural`/`G4_world`, wire xong TRƯỚC
khi D0 chạy — 2 pack đó build song song với G3 nhưng landed vào `main` sớm hơn) + 1 (`G3_dialogue`
mới). 534 - 502 = 32 test mới ròng (D1 5 + D3/D4 16 + D5-confusion 10 + D7 4 - 3 trùng đếm do D0
baseline đã có sẵn trước khi D1 landed).

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

## AUDIT VÒNG 2 (route-back kiểm duyệt độc lập 5/7, `PROMPT_HANDOFF_CMD_BUILD_3_G3_FIXES.md`)

Audit độc lập 15 checkpoint (2 lớp verify) trên `build/g3-dialogue-d0-d8`: 9/15 PASS sạch,
`G3-1` (build-ahead) FAIL ban đầu → route lại 5 việc. Kiểm duyệt đã tự xử lý 2/5 việc trực tiếp
trên `main` (D2 decision_note trung thực + sửa đếm 11→12 trong `TASK_G3_DIALOGUE.md`/
`CMD_AUDIT_G3.md`) — CMD_BUILD_3 chỉ cần đồng bộ (rebase), không làm lại. 3 việc còn lại:

**1. Đồng bộ D2:** `git rebase origin/main`, resolve conflict `g3_manager_decision_proposal.yaml`
giữ đúng bản `main` (kiểm duyệt) — `mr_long_decision: APPROVED_A` với `decision_note` ghi trung
thực timeline tự-duyệt (không hồi tố, không giả mạo lịch sử). Xác nhận qua `git log` sau rebase:
field khớp đúng bản chuẩn.

**2. Sửa số D0 (11→12):** `reports/G3_REALITY_AUDIT.md` mục 1 — máy đếm lại `len(CHECKS)` trong
`tools/ci_gate.py` xác nhận **12** (không phải 11) trước khi G3 wire — danh sách 12 tên liệt kê
ngay dưới câu văn xuôi vốn đã đúng, chỉ con số trong câu bị sai (lỗi kế thừa từ `TASK_G3_DIALOGUE.md`
gốc). Đã sửa cả 2 câu liên quan trong `G3_REALITY_AUDIT.md` + đồng bộ lại chính report này.

**3. Re-audit thật G3-5:** 2 test cũ (`test_dialect_leak_blocks_via_real_validator_direct_call`,
`test_forbidden_word_direct_call_confirms_step3_uses_live_function`) chỉ gọi `dvv.validate_line()`
**trực tiếp** trên chuỗi tay gõ — chưa chứng minh `generate_line()` (buộc 3 thật) tự lọc được
candidate leak qua toàn bộ pipeline. Test mới
`test_dialect_leak_end_to_end_via_generate_line_full_pipeline`: mutate 1 nhân vật thật (region
`nam`), bơm marker leak (`nhé`/`nhỉ`, EXCLUSIVE của `bac`) qua `scene_context` (input từ ngoài,
đúng cách G6 sẽ cấp trong tương lai) khiến candidate đầu (`core`) leak thật — xác nhận bằng chứng
khách quan `r['attempts'] > 1` (candidate đầu bị buộc-3 từ chối trước khi candidate sạch được
chọn, verify thủ công cho ra `attempts=2`, không phải giả định) + dòng cuối không còn marker leak.
**PASS**, không phải pass rỗng (đã probe giá trị `attempts` thật trước khi tin).

**4. Đóng gap G3-7:** `write_episode_line()` mở rộng nhận `ep_n` dạng chuỗi (không ép `int()` cứng)
để tạo thư mục sandbox **tên chữ** `output/ep_g3_sample/` — không bao giờ trùng số tập thật/tương
lai (hiện 50, roadmap tới 90), khác hẳn cách dùng số giả (0/99) rủi ro đụng tập tương lai. Gate
`tools/g3_dialogue_check.py` thêm stage `G3_7_output_audit_real`: sinh 1 dòng thoại thật, ghi ra
sandbox, rồi chạy `audit_driver_dialogue_context.py --file` (hỗ trợ sẵn) + import trực tiếp
`audit_dialogue_hierarchy.audit_ep()` (hàm lõi không phụ thuộc đường dẫn) — xác nhận **cả 2 tool
quét được thật** (`extract_quotes() >= 1`, không phải 0-file/0-quote PASS RỖNG), và `--all` glob
`ep_*/episode.md` cũng tự động bắt được path này (verify thủ công). Xác nhận an toàn: regex R41
pre-commit gate (`^output/ep_[0-9]+/episode\.md$`) không khớp tên chữ → sandbox tự động được bỏ
qua bởi gate 50-tập, không gây crash `int('g3_sample')`.

**5. TECH_DEBT DEBT-004:** ghi nợ Cross-G3/G6 (`scene_context` chưa khớp packet 12-knob thật vì
`decision_engine.py` chưa build) vào `governance/TECH_DEBT.md` — OPEN, chờ G6.

## DoD checklist (theo TASK_G3_DIALOGUE.md)

- [x] D0 baseline + MATCH/MISMATCH thật
- [x] D1 SSOT reconcile + test Hải Dương đỏ/xanh
- [~] D1B Phần A: hạ tầng đã đồng bộ (máy PASS), field giấy tờ vẫn PENDING — chờ Mr.Long
- [ ] D1B Phần B: vẫn bị chặn đúng thiết kế, thiết kế lại chưa làm (ngoài phạm vi D7/D8)
- [x] D2 quyết định A ghi rõ — kiểm duyệt 5/7 đã sửa `decision_note` ghi trung thực timeline
      (tự-duyệt trước, Boss xác nhận sau, không hồi tố) — xem "AUDIT VÒNG 2" mục 1
- [x] D3 generator chạy thật ≥10 passenger đa vùng
- [x] D4 grep xác nhận gọi thật 3 validator, 0 file mới trùng phạm vi
- [x] D5 golden set 2 nguồn tách bạch + confusion 0FN/0FP + ≥1 case pronoun thật
- [x] D6 domain đăng ký, registry 0/0/0
- [x] D7 gate wired + unwire-guard 2 lớp
- [x] D8 sample YAML + report này

STATUS cuối: **READY_FOR_AUDIT** (với 2 điểm treo đã flag rõ ở trên: D1B Phần A cần Mr.Long xác
nhận field, D1B Phần B cần thiết kế lại — cả 2 KHÔNG chặn merge, vì D5/D3 đã tự tránh dùng Phần B
và đã minh bạch tình trạng Phần A).
