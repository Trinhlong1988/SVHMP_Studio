# TASK — 25 finding mức CAO từ audit đa-agent 9-10/7 (workflow 222 agent, G2-G8)

> Viết bởi CMD_AUDIT 10/7. Nguồn: artifact báo cáo audit đa-agent (32 finder × 4 lens, 3-skeptic
> phản biện độc lập mỗi finding — đã qua ≥2/3 skeptic không bác được mới xếp vào đây). KHÔNG re-verify
> lại từng cái bằng tay lần 2 (workflow đã làm đủ nghiêm — mỗi finding có ít nhất 1 skeptic đọc lại
> source thật + chạy repro) — CMD_BUILD tiếp nhận vẫn PHẢI tự đọc lại code trước khi sửa (không tin
> mù task doc này, đúng tinh thần dự án). **1 finding (G3 cross_domain_write, `write_episode_line`)
> ĐÃ gộp vào `TASK_AUDIT_CRITICAL_G3_G5.md` — không lặp lại ở đây, fix guard đó tự động đóng luôn
> finding này.**

## NHÓM A — Sửa được ngay (thêm test/guard, không cần quyết định kiến trúc)

### G2-1. `tools/render_with_character_gate.py::run_character_gate()` không có test hành vi thật
Test hiện có chỉ text-grep tên biến (`WIRE_MARKERS`), không gọi hàm. Nếu ai đổi `return False` →
`return True` (vô hiệu hoá BLOCK), 6/6 test vẫn xanh. **Fix:** thêm test gọi thật
`run_character_gate()` với input cố ý thiếu Tier1/voice, assert `False`; test `main()` với case đó
assert `sys.exit(2)`.

### G2-2. `tools/story_consistency_validator.py::validate_against_registry()` không bao giờ được gọi
Hàm DUY NHẤT nối `CharacterRegistry` (dữ liệu roster thật) với so sánh baseline — 0 caller ngoài
định nghĩa. `__main__` chỉ `print()`, không `assert`/`sys.exit` theo kết quả → gate D4 luôn "sạch"
dù logic có chạy hay không. **Fix:** wire `validate_against_registry()` vào `g4_world_check.py`
D4 stage thật (không chỉ smoke-test `python tools/story_consistency_validator.py`), có test gọi
thật với dữ liệu cố ý vi phạm field khóa.

### G2-3. `tools/story_consistency_validator.py` self-test dùng sai key có dấu (`nguyên_nhân` vs `nguyen_nhan`)
Nhánh kiểm khóa `nguyen_nhan` (1/3 `EVENT_LOCKED_FIELDS`) chưa từng thực sự chạy trong self-test vì
lệch chính tả có dấu/không dấu — vẫn in "sạch" như đã PASS. **Fix:** sửa key đúng chính tả trong
self-test dòng 117, xác nhận lại self-test bắt được thay đổi `nguyen_nhan` thật.

### G4-1. `tools/event_ledger_miner.py` evidence-tracking fix (commit 2869553) không có regression test
Code tự viết tương thích ngược cả 2 định dạng cũ/mới (`isinstance(entry, dict)` fallback) — nếu
revert về định dạng cũ, pipeline vẫn chạy, gate vẫn PASS, 616+ pytest vẫn xanh. **Fix:** thêm test
xác nhận `object_mentions`/`primary_event` field `line` tồn tại thật (không phải fallback rỗng) trên
dữ liệu mine thật.

### G5-1. R211 dedup fix (`possession_state_machine` xóa khỏi `runtime/supernatural_state_machine.yaml`) không có guard chặn tái diễn
`check_no_duplicate_compliance_files()` chỉ chặn 2 file không liên quan, không kiểm tra file này còn
key trùng hay không. **Fix:** thêm check trong `supernatural_validator.py` xác nhận
`runtime/supernatural_state_machine.yaml` KHÔNG chứa lại key `possession_state_machine`.

### G6a-1. DEBT-007 fix (`plan_ref`) claimed CLOSED nhưng 30/30 test không có assertion nào kiểm giá trị field
Nếu ai revert dòng 56 `decision_engine.py` về bug cũ, toàn bộ pytest suite (kể cả 2 file test được
cite làm bằng chứng "đã fix") vẫn PASS 100%. **Fix:** thêm assertion trực tiếp
`decision_packet.plan_ref == f"ep{episode_number}_{season_ref}"` (không chỉ `is not None`) vào 1
trong 2 test file đã cite.

### G8-1. `tools/vnqa/auto_fix.py` (AUTO_FIX, mặc định `apply`) ghi trực tiếp `episode.md` — vi phạm hợp đồng `qa_runtime` tự khai "KHÔNG sửa content"
`qa_skeptic_orchestrator.orchestrate()` gọi AUTO_FIX với `autofix_mode` mặc định = `'apply'`.
**Cần Mr.Long xác nhận:** đây là hành vi ĐÃ BIẾT/CHỦ Ý (AUTO_FIX literal-map registry Mr.Long đã
duyệt, ghi trong `feedback_svhmp_*`?) hay là drift thật? Nếu chủ ý, chỉ cần cập nhật
`non_responsibility` trong `blueprint_domains.yaml` cho chính xác (AUTO_FIX là ngoại lệ đã duyệt).
Nếu không, cần đổi mặc định `autofix_mode` sang `'dry_run'` + xác nhận riêng khi cần `apply`.
**→ KHÔNG tự sửa code, hỏi Mr.Long hướng trước.**

### G8-2 đến G8-5. 4 lỗ hổng enforcement cùng lớp `qa_post_render.py`/`qa_skeptic_orchestrator.py`/`qa_pause_silence.py`
- `qa_pause_silence.py::audit_array()` — ngưỡng `noisy<=1` (R96 v3.3) chưa có test boundary thật.
- `qa_post_render.py::audit_spectrum()`/`audit_boundary()`/`audit_head_onset()` — 3/4 check STAGE 3
  hoàn toàn 0 test (khác `audit_pause()` đã có 3-lớp bảo vệ sau D3).
- `qa_skeptic_orchestrator.py::orchestrate()` — decision tree (Claude-QA + Skeptic + VNQA-escalation)
  chưa từng được import/gọi trong bất kỳ test nào.
**Fix:** mirror đúng mẫu D3 (`tests/test_qa_post_render_pause_delegation.py`) — thêm test hành vi
thật (không chỉ text-grep) cho từng hàm, có mutation-proof. Đây là khối lớn — có thể chia nhỏ theo
từng hàm, ưu tiên `orchestrate()` trước (quan trọng nhất, verdict cuối của toàn hệ QA).

### G8-6, G8-7. 2 giá trị enum chết trong `qa_skeptic_orchestrator.py`
`PASS_WITH_NOTE` (docstring) và `PASS_WITH_WARNING` (code 4 chỗ, kể cả `next_action`/`exit_code`
map) đều không bao giờ được gán bởi decision tree thật — dead code/docstring. **Fix:** dọn
`PASS_WITH_NOTE` khỏi docstring (không tồn tại thật). Với `PASS_WITH_WARNING` — **cần Mr.Long xác
nhận:** có ý định dùng trong tương lai (giữ, thêm nhánh decision tree gán nó) hay bỏ hẳn (xóa khỏi
enum + 4 chỗ tham chiếu)? Lưu ý: D5 (G8, đã lock) đã quyết định GIỮ `PASS_WITH_WARNING` trong
canonical enum của `qa_verdict_adapter.py` map từ VNQA `WARN` — 2 việc khác nhau, không tự gộp.

### G8-8. `qa_post_render.py` banner in nhầm quy tắc (R87b "-20dB/50ms") nhưng hàm chạy thật là R88 ("-28dB/120ms")
**Fix:** sửa dòng print banner khớp đúng rule thật đang chạy (R88), hoặc nếu ý định ban đầu là R87b
thật thì đổi default params của `audit_head_onset()` — cần đọc `bible/00_constitution.yaml` dòng
3331-3336 xác nhận rule nào là ý định gốc trước khi chọn hướng sửa (không tự đoán).

## NHÓM B — Cần Mr.Long quyết định trước khi sửa (drift do 2 nguồn tài liệu mâu thuẫn thật)

### G2-4. CLAUDE.md ghi "100 passenger LOCK, 50 NAM+50 NU" nhưng thực tế 139 (70 nam/69 nữ)
Đã có backfill 39 người per Mr.Long 5/7 (ghi trong code) — chỉ là **CLAUDE.md quên cập nhật con số**
sau quyết định đó. Sửa an toàn: cập nhật CLAUDE.md khớp số liệu thật, không cần hỏi lại.

### G2-5. `roster_validator.py` docstring "0/139 đã fill" nhưng data thật 139/139 đã điền đủ
Tương tự — chỉ là comment lỗi thời sau khi dữ liệu đã điền xong. Sửa an toàn: cập nhật docstring.

### G2-6. `bible/37` claim "BỊ CHẶN" (blocked) nhưng code mặc định chỉ WARN, `--strict-characters` không được gọi ở đâu trong pipeline tự động
**Cần Mr.Long quyết:** có muốn BẬT strict thật trong pipeline tự động (rủi ro: completeness roster
hiện ~23%, sẽ chặn MỌI episode) hay chỉ sửa lại bible/37 cho khớp thực tế WARN-default (an toàn
hơn, đúng lý do code đã ghi rõ)? Đây đúng tinh thần GOV-2 đã ghi trong `master_roadmap.md` — không
tự bật khi dữ liệu voice còn đang sửa.

### G2-7. `tools/migrate_roster_v2.py` — `pronoun_system`/`particles` vẫn công thức hóa theo vùng miền (3 giá trị cho 100 người)
Cùng lớp lỗi G2-1 đã bắt và sửa cho 4 field khác (`speaking_speed`/`catchphrase`/`dialogue_sample`/
`forbidden_words`, commit `e079d10`) nhưng 2 field này CHƯA sửa. **Cần Mr.Long xác nhận phạm vi:**
mở rộng đúng batch fix G2-1 sang 2 field này (cùng CMD_CHARACTER, cùng kỹ thuật) hay để riêng?

### G4-2. `blueprint_domains.yaml` domain timeline/event vẫn ghi "planned" với lý do lỗi thời ("100 tập chưa render đủ", "chưa có tập nào ghi ledger") dù `g4_world` đã LOCKED
Cập nhật đơn giản (status → exists, xóa lý do lỗi thời) — an toàn, không cần hỏi, nhưng đụng file
governance dùng chung nên **note rõ trong commit** đây chỉ là đồng bộ trạng thái, không đổi field
nào khác.

### G5-2. `blueprint_domains.yaml` domain supernatural validator vẫn "planned" (`tools/supernatural_rule_validator.py`, không tồn tại) dù validator thật (`supernatural_validator.py`) đã LOCK
Tương tự G4-2 — cập nhật đồng bộ trạng thái, an toàn.

### G5-3. `character_ext_schema.yaml` (đã "SIGNED" bởi Mr.Long) claim `story_consistency_validator.py` đối chiếu 2 chiều `entity_class<->alive_status` nhưng code KHÔNG có check này
Đây là **claim enforcement giả trong 1 file đã ký** — nghiêm trọng hơn drift thường vì đã có chữ ký.
**Cần Mr.Long quyết:** thêm check thật vào `story_consistency_validator.py` (đúng như đã ký) hay
sửa lại schema cho khớp thực tế chưa làm (hạ cấp thành roadmap)?

### G6a-2. `decision_engine.build_packet()` tự nhận `status="full"` chỉ vì `plan is not None`, không kiểm 2 field bắt buộc (`cast_per_scene`, `reveals_allowed`) theo `decision_io.yaml`
**Cần Mr.Long quyết:** siết `status="full"` chỉ khi đủ field bắt buộc thật (an toàn hơn, có thể làm
nhiều packet rơi về `"partial"`) hay giữ nguyên logic hiện tại (chỉ cần `plan` khác `None`)? Đụng
domain đã LOCKED, cùng lớp với DEBT-007 — nên gộp xử lý cùng đợt TU CHỈNH nếu Mr.Long đồng ý.

### G6b-1. `blueprint_domains.yaml` khai `dependencies: [character, event, timeline, world, supernatural]` nhưng code thật dùng `decision_engine` + đọc bible domain audio — không khớp
Cập nhật đồng bộ đơn giản — an toàn, không cần hỏi.

### G6b-2. `story_planner.py::build_episode_plan_ep01()` — `location_ref` của cả 6 scene bị gán cứng cùng 1 chuỗi `"Cầu Long Biên"` (đúng lớp lỗi công thức hóa đã bắt trước đó)
Comment nói "đọc từ event_ledger" nhưng code không hề đọc file đó cho field này. **Cần Mr.Long xác
nhận:** có dữ liệu location thật riêng cho từng scene để đọc không (nếu có nguồn thật, sửa đọc đúng
nguồn — không bịa thêm), hay EP01 chỉ có 1 location duy nhất thật (thì sửa lại comment cho khớp,
không phải bug)?

### G6b-3. `scene_function` (schema `required:true`) không có generator/validator nào enforce quyền sở hữu đã khai ("SCENE sở hữu, character CHỈ tham chiếu")
Cần thiết kế enforcement — không đơn giản, nên gộp cùng đợt khi có generator EP02+ (hiện D2
`episode_generator.py` mới build EP01).

### G7-1. `g7_generator_check.py::_stage_no_write_domain()` tự-skip vì `git diff --name-only HEAD` luôn rỗng tại thời điểm pre-push chạy (đã commit xong)
**Lỗ hổng thiết kế thời điểm-chạy** — gate hiệu quả bằng 0 trong thực tế dù logic đúng. **Cần
Mr.Long/CMD_BUILD thiết kế lại cách kiểm** (vd so sánh diff giữa 2 commit gần nhất thay vì
working-tree vs HEAD, hoặc chạy gate ở pre-commit thay vì pre-push) — không phải sửa 1 dòng đơn
giản, cần suy nghĩ kỹ tránh phá cơ chế push hiện có.

### G7-2. `decision_engine.build_packet()` tự nhận `status='full'` cho EP01 nhưng không đọc field bắt buộc theo `bp6/decision_io.yaml`, `scene_id` không khớp plan thật
Cùng gốc với G6a-2 ở trên — xử lý chung 1 lần.

## RÀNG BUỘC CHUNG
- KHÔNG tự sửa các mục NHÓM B mà chưa có xác nhận hướng từ Mr.Long — chỉ NHÓM A được làm ngay.
- Domain đã LOCKED bị chạm (G2/G3/G4/G5/G6a/G6b/G7/G8) đều cần ghi "per Mr.Long authorization
  10/7" + cập nhật dòng lock tương ứng trong `architecture_registry.yaml` (mẫu TU CHỈNH đã dùng
  nhiều lần).
- Registry 0/0/0 + pytest full suite xanh sau mỗi batch fix, không gộp NHÓM A và B vào 1 commit
  (A an toàn ngay, B cần chờ quyết định — tách để không block nhau).
- Ghi `governance/TECH_DEBT.md` cho các mục cần nhiều thời gian (G7-1, G6b-3) nếu không xong trong
  1 phiên — không để trôi mất.

## THAM CHIẾU
Artifact báo cáo audit đa-agent 222 agent (32 finder × 4 lens, 3-skeptic phản biện) 9-10/7 ·
`TASK_AUDIT_CRITICAL_G3_G5.md` (2 bug CRITICAL, xử lý trước/song song) · mẫu mutation-proof:
`tests/test_qa_post_render_pause_delegation.py` · `governance/master_roadmap.md` §9 (GOV-2 note).
