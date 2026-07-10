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

## NHÓM B — ĐÃ CÓ QUYẾT ĐỊNH (Mr.Long duyệt theo khuyến nghị CMD_AUDIT, 10/7 — thực thi thẳng, không hỏi lại)

### G2-4. CLAUDE.md ghi "100 passenger LOCK, 50 NAM+50 NU" nhưng thực tế 139 (70 nam/69 nữ)
**QUYẾT ĐỊNH:** cập nhật CLAUDE.md khớp số liệu thật (139, 70 nam/69 nữ, ghi rõ backfill per
Mr.Long 5/7). An toàn, không đổi hành vi code.

### G2-5. `roster_validator.py` docstring "0/139 đã fill" nhưng data thật 139/139 đã điền đủ
**QUYẾT ĐỊNH:** cập nhật docstring khớp thực tế 139/139.

### G2-6. `bible/37` claim "BỊ CHẶN" (blocked) nhưng code mặc định chỉ WARN
**QUYẾT ĐỊNH: sửa bible/37 khớp thực tế WARN-default** — KHÔNG bật `--strict-characters` (roster
completeness ~23%, bật strict sẽ chặn mọi episode, đúng tinh thần GOV-2 `master_roadmap.md` — không
bật khi dữ liệu voice còn đang sửa).

### G2-7. `tools/migrate_roster_v2.py` — `pronoun_system`/`particles` vẫn công thức hóa
**QUYẾT ĐỊNH: mở rộng đúng batch fix G2-1** (mirror kỹ thuật đã dùng cho 4 field kia, commit
`e079d10`) sang 2 field `pronoun_system`/`particles` — cùng CMD_CHARACTER, cùng domain.

### G4-2. `blueprint_domains.yaml` domain timeline/event vẫn ghi "planned" lỗi thời
**QUYẾT ĐỊNH:** cập nhật status → exists, xóa lý do lỗi thời, note rõ trong commit chỉ đồng bộ
trạng thái không đổi field khác.

### G5-2. `blueprint_domains.yaml` domain supernatural validator vẫn "planned" dù đã LOCK
**QUYẾT ĐỊNH:** cập nhật đồng bộ trạng thái, tương tự G4-2.

### G5-3. `character_ext_schema.yaml` (đã SIGNED) claim enforcement giả (`entity_class<->alive_status`)
**QUYẾT ĐỊNH: thêm check thật vào `story_consistency_validator.py`** — giữ đúng cam kết đã ký
(không hạ cấp schema xuống roadmap). Đây là claim TRONG FILE ĐÃ KÝ, ưu tiên làm đúng lời hứa hơn là
rút lại.

### G6a-2 / G7-2. `decision_engine.build_packet()` tự nhận `status="full"` không kiểm field bắt buộc
**QUYẾT ĐỊNH: siết `status="full"` chỉ khi đủ field bắt buộc thật** (`cast_per_scene`,
`reveals_allowed` theo `decision_io.yaml`, `scene_id` khớp plan) — chấp nhận rủi ro nhiều packet
rơi về `"partial"` (an toàn hơn tự nhận đủ khi chưa đủ, đúng tinh thần R195 không bịa). Xử lý G6a-2
và G7-2 CHUNG 1 lần (cùng gốc, cùng file).

### G6b-1. `blueprint_domains.yaml` dependencies không khớp code thật
**QUYẾT ĐỊNH:** cập nhật đồng bộ đơn giản.

### G6b-2. `location_ref` gán cứng "Cầu Long Biên" cho cả 6 scene
**ĐÃ ĐIỀU TRA — KHÔNG PHẢI bug bịa dữ liệu, chỉ là code không đọc biến đã load:** tự kiểm
`runtime/event_ledger_draft.yaml` xác nhận `events.ep_01.primary_event.stop_location.value` =
**"Cầu Long Biên"** — khớp CHÍNH XÁC chuỗi hardcode. Nguồn dữ liệu thật CHỈ có 1 giá trị
location/episode (không có location riêng từng scene — đúng thiết kế dữ liệu, EP01 toàn bộ diễn ra
1 địa điểm). **QUYẾT ĐỊNH: sửa code đọc ĐỘNG từ `event_ledger['primary_event']['stop_location']['value']`**
thay vì hardcode literal (biến `event_ledger` đã load sẵn ở dòng 100-101, chỉ cần dùng đúng) — để
episode tương lai có location khác nhau tự động đúng, không phải sửa tay mỗi lần.

### G6b-3. `scene_function` chưa được enforce quyền sở hữu
**QUYẾT ĐỊNH: hoãn** — đúng khuyến nghị ban đầu, gộp vào đợt build generator EP02+ (hiện D2 mới có
EP01, chưa cấp thiết). Ghi vào `governance/TECH_DEBT.md` để không trôi mất.

### G7-1. Gate `no_write_domain` tự-skip do thời điểm chạy (pre-push, sau khi đã commit)
**QUYẾT ĐỊNH: thiết kế lại cách kiểm** — đổi từ `git diff --name-only HEAD` (working-tree vs HEAD,
luôn rỗng lúc pre-push) sang so sánh diff giữa commit đang push và `origin/main` hiện tại (hoặc
merge-base), tức kiểm ĐÚNG nội dung sắp lên remote thay vì trạng thái working-tree đã lỗi thời. CMD
thực thi tự thiết kế chi tiết kỹ thuật, chỉ cần đảm bảo không phá cơ chế push hiện có — bắt buộc có
mutation test xác nhận gate bắt được commit thật sự ghi domain khác.

### G8-1. AUTO_FIX (`vnqa/auto_fix.py --apply`) ghi trực tiếp `episode.md`
**ĐÃ ĐIỀU TRA — ĐÂY LÀ NGOẠI LỆ ĐÃ DUYỆT, KHÔNG PHẢI DRIFT:** `governance/pack5/19_qa_pipeline.md`
dòng 26 ghi rõ nguyên văn: *"AUTO_FIX (Phase H4): vnqa/auto_fix.py --apply (**registry literal map
Mr.Long duyệt**, atomic ghi + backup)"* — cơ chế này đã được Mr.Long duyệt từ trước, có phạm vi hẹp
(chỉ literal-map đã duyệt, không phải sửa content tự do) + an toàn (atomic write + backup). **QUYẾT
ĐỊNH: KHÔNG đổi hành vi code** — chỉ cập nhật `non_responsibility` của domain `qa_runtime` trong
`blueprint_domains.yaml` ghi rõ AUTO_FIX là ngoại lệ đã duyệt (tránh đọc nhầm là vi phạm hợp đồng
domain lần sau). **Lưu ý phụ (không chặn quyết định trên):** `bible/26_pipeline_discipline_kentjuno.yaml`
dòng 97 ghi quy ước chung *"auto_fix_*.py: REQUIRE --apply flag, default dry-run"* — nhưng
`qa_skeptic_orchestrator.py` gọi với `autofix_mode` mặc định = `'apply'` (không phải dry-run mặc
định). CMD thực thi kiểm lại xem đây có phải sai lệch quy ước chung cần báo riêng không (không tự
đổi default khi chưa rõ).

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
