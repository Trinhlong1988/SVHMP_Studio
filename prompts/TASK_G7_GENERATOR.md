# TASK G7 — GENERATOR (KHUNG chuẩn bị trước, CHƯA build được — chờ G6a+G6b thật)

> Viết bởi kiểm duyệt 5/7, ÁP DỤNG rút kinh nghiệm toàn bộ lỗi thật đã xảy ra trong phiên G2-G6
> (liệt kê đầy đủ ở mục "RÚT KINH NGHIỆM" cuối file — đọc trước khi build, không phải đọc sau khi
> bị audit bắt lại đúng lỗi cũ). Đây là **KHUNG**, không phải lệnh "chạy ngay" — G7 hiện KHÔNG THỂ
> build thật vì vẫn còn 1/4 điều kiện chưa xong hẳn (G6b đang code, xem bảng dưới — **CẬP NHẬT
> 5/7 tối**, 3/4 điều kiện đã đổi trạng thái so với bản viết sáng 5/7).

## ĐIỀU KIỆN CHẠY — đọc TRƯỚC khi claim pack (đọc trực tiếp `blueprint_domains.yaml` dòng 594-622)

`generator` là domain có **blocking_dependency rộng nhất toàn dự án**: 14 domain phải đọc được
(`story_planner, decision_engine, dialogue, character, event, object, world, timeline,
supernatural, location, weather, culture, belief, ritual`) + 2 cổng duyệt Mr.Long riêng biệt:

| Cổng chặn | Trạng thái thật (cập nhật tối 5/7) | Lệnh xác nhận |
|---|---|---|
| `story_planner` (G6b) manager thật tồn tại | 🟡 ĐANG LÀM — CMD_BUILD đã claim `g6b_story_planner`, chưa release | `python tools/build_claim.py status` — chờ dòng `released` + `Test-Path tools/story_planner.py` |
| `decision_engine` (G6a) packet builder thật | ✅ XONG — locked v1.0, tag `g6a-decision-engine-v1.0` | `Test-Path bible/42_decision_policy.yaml` = True |
| Mr.Long duyệt `story_plan_schema.yaml` (G6b riêng) | ✅ Đã duyệt phương án A (nguyên văn), `governance/proposals/story_plan_schema_proposal.yaml` `APPROVED_A`, commit `9f5ccbd` | — |
| Mr.Long duyệt `episode_schema.yaml` (G7 riêng, KHÁC cổng trên) | ✅ Đã duyệt phương án B (có bổ sung ngoại lệ ep73/90 cho bell_count/driver_lines), `governance/proposals/episode_schema_proposal.yaml` `APPROVED_B`, commit `eef436b` | — |

**Luật cứng (mirror G6-1, REALITY ANCHOR luật 9):** BẤT KỲ dòng code nào của
`tools/episode_generator.py` xuất hiện trong diff mà thiếu 1 trong 4 điều kiện trên = build-ahead,
**100% SAI, không có mức tạm chấp nhận** — đúng lớp lỗi đã bắt G3 (dialogue_manager tự duyệt) và
suýt bắt G6b (chờ G4). G7 rủi ro build-ahead CAO HƠN mọi domain trước vì phụ thuộc nhiều nhất.
**Chỉ còn đúng 1 điều kiện chưa xong (G6b code) — khi CMD_BUILD release `g6b_story_planner` VÀ
`tools/story_planner.py` tồn tại thật, đủ cả 4/4, G7 mới được claim.**

## NỀN ĐÃ CÓ (reconcile trước — CẤM nhân đôi R211, đã verify trực tiếp 5/7)

| Đã có | Ở đâu | Verify |
|---|---|---|
| Scaffold khung episode (hook/setup/incident/reveal/payoff/cliffhanger) | `prompts/ep_scaffold_template.md` | ✅ `Test-Path` = True |
| Ràng buộc chống lặp/mòn ý tưởng | `bible/08_novelty_constraints.yaml` | ✅ `Test-Path` = True |
| Validator có sẵn (2 file, KHÁC phạm vi nhau) | `tools/svhmp_preflight_qa.py` (BP0 khai, render-spec level) + `tools/post_render_gate.py` (12-check, episode.md level, chưa khai trong BP0) | ✅ cả 2 `Test-Path` = True — xem D3 để biết cách dùng đúng, không tự chọn 1 trong 2 |
| 14 interface contract `read__<domain>__generator` | `governance/blueprint/bp1/interface_contracts.yaml` | ✅ đếm trực tiếp đúng 14, toàn bộ `allowed_operations: [read]`, `forbidden_operations: [write, schema_change]` — generator KHÔNG được ghi ngược vào bất kỳ domain nào trong 14 |
| Domain đã khai (generator) | BP0 dòng 594-622 | writer: `[generator]` (chỉ tự ghi output của mình) — reader: `[qa_runtime, production]` |

**CẢNH BÁO MỚI (5/7 tối, từ audit G2):** KHÔNG mặc định `lifecycle: approved` của 1 domain nguồn
= dữ liệu đó chất lượng tốt. Audit độc lập G2 vừa bắt được: dữ liệu voice 139 passenger (roster đã
"approved") thực chất là công thức hóa theo vùng+tuổi (18 khuôn giọng), KHÔNG cá tính hóa thật —
đang được CMD_BUILD_2 sửa. G7 đọc `character` domain PHẢI tự kiểm tra 1 lần nữa trạng thái sửa lỗi
này đã xong chưa (`python tools/roster_validator.py`, xem cả C1-C5 lẫn nội dung thật, không chỉ tin
số 0 violation) trước khi coi dữ liệu đó là input đáng tin — "approved" chỉ đảm bảo ĐỦ FIELD, không
đảm bảo NỘI DUNG tốt.

## DELIVERABLE (khung, KHÔNG build cho tới khi đủ 4 điều kiện ở trên)

### D1 — `governance/blueprint/schemas/episode_schema.yaml` (field-hóa, ĐÃ CÓ bản duyệt — chỉ copy đúng)
Mr.Long đã duyệt phương án B (`governance/proposals/episode_schema_proposal.yaml`, `APPROVED_B`,
commit `eef436b`) — đọc đúng mục `schema_draft` trong file đó (đã có sẵn ngoại lệ `bell_count`
allowed [1,2] cho ep73, `driver_lines` allowed [2,3] cho ep73/90/milestone) → field-hóa NGUYÊN VĂN
thành `governance/blueprint/schemas/episode_schema.yaml`. KHÔNG tự thêm/bớt field so với bản đã
duyệt (nếu thấy cần đổi, dừng lại báo kiểm duyệt, không tự quyết — đúng bài học G6-5).

### D2 — `tools/episode_generator.py` (manager, CHỈ build sau khi CẢ 4 điều kiện đủ)
Đọc packet thật từ `decision_engine` (G6a, budget nhịp) + `story_planner` (G6b, kế hoạch reveal)
+ 14 domain còn lại (chỉ READ, theo đúng `interface_contracts.yaml`) → sinh `episode.md` theo
scaffold. KHÔNG tự tạo nhân vật mới (bible/03 cấm) · KHÔNG tự quyết ratio/pacing (đó là việc
decision_engine, generator chỉ THI HÀNH quyết định có sẵn) · KHÔNG tự phong PASS (qa_runtime +
auditor làm) · KHÔNG render (production làm).

### D3 — Wire validator có sẵn — ĐỌC HẾT CẢ 2 FILE TRƯỚC KHI CODE (bài học từ episode_schema_proposal PHẢN BIỆN #2)
BP0 khai `tools/svhmp_preflight_qa.py` là validator của domain generator (FULL_TEXT_GATE, kiểm
trên spec.json — R86 dấu thanh...), nhưng `tools/post_render_gate.py` (12-check, đang chạy thật
cho 50 tập) mới là cái khớp sát nhất với cấu trúc episode_schema (word_count/bell_count/
ghost_manifest/driver_lines/pillar-match/memory-match/callback-match). **BẮT BUỘC đọc hết CẢ 2
file này trước khi code `tools/g7_generator_check.py`** — xác định rõ ranh giới (1 kiểm render-spec
level, 1 kiểm episode.md level), TÁI SỬ DỤNG hàm đã có (import, không copy-paste logic) để tránh
nhân đôi R211. Không tự coi 1 trong 2 file là "đủ", không tự coi cả 2 là "trùng nhau nên bỏ 1".

### D4 — Gate 1 cửa + wire (mirror pattern `g4_world_check.py`/`g6_story_planner_check.py`)
`tools/g7_generator_check.py`: xác nhận output chỉ dùng domain `lifecycle=approved` (Promotion
Gate R211) + budget sheet luôn đi kèm mỗi cảnh + KHÔNG ghi ngược vào 14 domain nguồn (`git diff`
14 file/thư mục domain nguồn phải rỗng trong mọi commit generator). Wire ci_gate + unwire-guard
test NGAY commit đầu (bài học G2_roster).

### D5 — Test dry-run trên EP01 (SAU khi D1-D4 xong)
Chạy generator thật trên dữ liệu EP01 đã có (world/timeline/character/supernatural/dialogue đã
locked hoặc gần xong) → so sánh output với `EP01_FULL_v103.mp3`/text gốc — đây là bước đầu tiên
của "bằng chứng cuối" (end-to-end EP01) mà kiểm duyệt đã báo Boss là CHƯA CÓ.

## MUTATION AUDIT SẼ BẮN (khai trước, mirror G6-1..G6-6 + Cross-G4/G6)
M1 code `episode_generator.py` xuất hiện khi 1/4 điều kiện chặn chưa đủ → FAIL (build-ahead,
không mức giữa) · M2 generator ghi vào bất kỳ 1/14 domain nguồn → FAIL (vi phạm 1-writer +
`forbidden_operations: write`) · M3 `episode_schema.yaml` field-hóa LỆCH so với nội dung đã duyệt
trong `episode_schema_proposal.yaml` (vd thiếu field ngoại lệ `bell_count`/`driver_lines` ep73/90
đã có sẵn trong bản duyệt B) → FAIL · M4 cảnh sinh ra thiếu budget sheet đính kèm → FAIL
(audit_rule BP0) · M5 gỡ stage `G7_generator` khỏi ci_gate → unwire test phải đỏ · M6 generator tự
tạo nhân vật/vật phẩm mới không có trong canon → FAIL (bible/03/12 CẤM) · M7 `bell_count=2` hoặc
`driver_lines=3` tại 1 tập KHÔNG phải ep73/90/milestone → FAIL (ngoại lệ chỉ áp đúng phạm vi đã
duyệt, không được mở rộng tùy tiện) · M8 generator dùng dữ liệu `character` (voice fields) mà
không kiểm lại tình trạng sửa lỗi G2-1 (công thức hóa) → ghi nợ kỹ thuật, không tự coi là an toàn.

## RÚT KINH NGHIỆM TOÀN BỘ LỖI THẬT ĐÃ XẢY RA (phiên G2-G6, 2/7-5/7) — ÁP DỤNG BẮT BUỘC CHO G7

1. **Build-ahead tự-duyệt (vụ D2 dialogue_manager, G3):** CMD build code + tự ghi
   `mr_long_decision: APPROVED` trong CÙNG 1 commit — không có bản ghi độc lập trước. G7 có 2
   cổng duyệt riêng (story_plan_schema + episode_schema) — PHẢI thấy bằng chứng duyệt tồn tại
   TRƯỚC commit code, không ghi kèm.
2. **Đếm tay sai (vụ "11 vs 12" CHECKS, G3):** đừng tự đếm bằng mắt số lượng domain/interface/knob
   trong văn xuôi — LUÔN grep/đếm bằng lệnh máy trước khi ghi số vào task/report (bài học này áp
   dụng ngay ở task doc này: 14 dependency + 14 interface contract đã đếm bằng `Grep` thật, không
   phải đếm tay).
3. **Fabricate narrative để giảm nhẹ vi phạm (vụ D2 "Boss đã nói miệng trước"):** không tự thêm
   tình tiết chưa xác minh để giải thích lý do 1 vi phạm quy trình. Nếu G7 build-ahead xảy ra,
   ghi ĐÚNG timeline thật, không suy diễn "chắc Boss đã đồng ý ngầm".
4. **Gate mới gọi lại pytest tự đệ quy (G14, vụ 2200 process, G3 D7):** nếu `g7_generator_check.py`
   có stage gọi `subprocess.run(pytest ...)`, PHẢI tự hỏi test đó có gọi ngược lại chính gate
   không — nếu có, bắt buộc `_PYTEST_GUARD` theo đúng pattern `ci_gate.py`.
5. **Debt logging trễ/quên (vụ DEBT-004 chưa được ghi dù đã giao):** nợ kỹ thuật cross-domain phát
   hiện lúc build G7 (nếu có, vd interface thật lệch so với contract khai) phải ghi TECH_DEBT.md
   NGAY trong batch fix đó, không để "giao việc" rồi trôi — nếu phát hiện mà chưa kịp ghi, báo
   kiểm duyệt ghi trực tiếp (không gắn 1 pack cụ thể, đúng tinh thần file).
6. **Kết luận "thiếu dữ liệu" khi thật ra kỹ thuật/tài nguyên đã có sẵn nơi khác (vụ DEBT-002
   audio "tưởng mất", thật ra pipeline làm sạch đã proven, chỉ cần render lại):** trước khi báo
   "X chưa có, cần Boss cung cấp", tìm kỹ trên MÁY THẬT (kể cả ổ đĩa khác, worktree cũ, memory
   phiên trước) — đừng kết luận thiếu chỉ vì 1 thư mục cụ thể trống.
7. **Push bị reject do phiên khác vừa commit (nhiều lần, G4/G5/DEBT-004):** LUÔN `git fetch` +
   kiểm `git log HEAD..origin/main` trước khi push, rebase sạch nếu lệch — đừng giả định
   `origin/main` đứng yên trong lúc mình build (nhiều CMD_BUILD chạy song song thật).
8. **Vai trò kiểm duyệt tự build (đầu phiên 5/7):** kiểm duyệt viết task/audit doc (như file này)
   nhưng KHÔNG tự code `tools/episode_generator.py` — giao đúng CMD_BUILD rảnh, kiểm duyệt chỉ
   audit độc lập sau.

## DoD
D1 (episode_schema) field-hóa khớp đúng bản đã duyệt B, không tự thêm/bớt ✅ · D2
(episode_generator.py) chỉ tồn tại khi đủ 4 điều kiện chặn ✅ · D3 đã đọc hết + tái dùng cả 2
validator có sẵn, không viết lại logic, không nhân đôi ✅ · D4 gate 1 cửa + unwire-guard ✅ · D5
dry-run EP01 có so sánh số liệu thật (không phải "chạy được là xong") ✅ · registry 0/0/0 · pytest
xanh, không giảm baseline hiện tại.

## RÀNG BUỘC
Claim pack `python tools/build_claim.py claim g7_generator <phiên>` — nhưng CHỈ claim khi đã tự
tay chạy đủ bảng "ĐIỀU KIỆN CHẠY" ở trên và cả 4 dòng đều xanh, không claim "để giữ chỗ" rồi chờ
sau (giữ chỗ khi chưa đủ điều kiện = tự tạo áp lực build-ahead cho chính mình).

STATUS cuối: KHUNG_CHUAN_BI (chưa phải READY_FOR_AUDIT — file này chỉ có giá trị khi G6a+G6b thật
xong, đọc lại bảng điều kiện chạy để tự xác nhận trước khi bắt đầu bất kỳ dòng code nào).
