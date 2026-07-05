# TASK G7 — GENERATOR (KHUNG chuẩn bị trước, CHƯA build được — chờ G6a+G6b thật)

> Viết bởi kiểm duyệt 5/7, ÁP DỤNG rút kinh nghiệm toàn bộ lỗi thật đã xảy ra trong phiên G2-G6
> (liệt kê đầy đủ ở mục "RÚT KINH NGHIỆM" cuối file — đọc trước khi build, không phải đọc sau khi
> bị audit bắt lại đúng lỗi cũ). Đây là **KHUNG**, không phải lệnh "chạy ngay" — G7 hiện KHÔNG THỂ
> build thật vì phụ thuộc trực tiếp G6a (decision_engine, 0% code) + G6b (story_planner, chặn cứng
> chờ Mr.Long duyệt schema) + 1 cổng duyệt riêng của chính G7 (episode_schema).

## ĐIỀU KIỆN CHẠY — đọc TRƯỚC khi claim pack (đọc trực tiếp `blueprint_domains.yaml` dòng 594-622)

`generator` là domain có **blocking_dependency rộng nhất toàn dự án**: 14 domain phải đọc được
(`story_planner, decision_engine, dialogue, character, event, object, world, timeline,
supernatural, location, weather, culture, belief, ritual`) + 2 cổng duyệt Mr.Long riêng biệt:

| Cổng chặn | Trạng thái thật (kiểm tra 5/7, không suy đoán) | Lệnh xác nhận |
|---|---|---|
| `story_planner` (G6b) manager thật tồn tại | ❌ CHƯA — `tools/story_planner.py` chưa có | `Test-Path tools/story_planner.py` |
| `decision_engine` (G6a) packet builder thật | ❌ CHƯA — `bible/42_decision_policy.yaml`, `tools/decision_engine.py` chưa có | `Test-Path bible/42_decision_policy.yaml` |
| Mr.Long duyệt `story_plan_schema.yaml` (G6b riêng) | ❌ CHƯA có bằng chứng | grep PING/commit trích rõ duyệt ĐÚNG format này |
| Mr.Long duyệt `episode_schema.yaml` (G7 riêng, KHÁC cổng trên) | ❌ CHƯA có bằng chứng | grep PING/commit trích rõ duyệt ĐÚNG field episode spec |

**Luật cứng (mirror G6-1, REALITY ANCHOR luật 9):** BẤT KỲ dòng code nào của
`tools/episode_generator.py` xuất hiện trong diff mà thiếu 1 trong 4 điều kiện trên = build-ahead,
**100% SAI, không có mức tạm chấp nhận** — đúng lớp lỗi đã bắt G3 (dialogue_manager tự duyệt) và
suýt bắt G6b (chờ G4). G7 rủi ro build-ahead CAO HƠN mọi domain trước vì phụ thuộc nhiều nhất.

## NỀN ĐÃ CÓ (reconcile trước — CẤM nhân đôi R211, đã verify trực tiếp 5/7)

| Đã có | Ở đâu | Verify |
|---|---|---|
| Scaffold khung episode (hook/setup/incident/reveal/payoff/cliffhanger) | `prompts/ep_scaffold_template.md` | ✅ `Test-Path` = True |
| Ràng buộc chống lặp/mòn ý tưởng | `bible/08_novelty_constraints.yaml` | ✅ `Test-Path` = True |
| Validator preflight (CÓ SẴN, không phải build mới) | `tools/svhmp_preflight_qa.py` (status: exists trong BP0) | ✅ `Test-Path` = True — D-nào-đó của G7 chỉ cần WIRE vào, không viết lại logic preflight |
| 14 interface contract `read__<domain>__generator` | `governance/blueprint/bp1/interface_contracts.yaml` | ✅ đếm trực tiếp đúng 14, toàn bộ `allowed_operations: [read]`, `forbidden_operations: [write, schema_change]` — generator KHÔNG được ghi ngược vào bất kỳ domain nào trong 14 |
| Domain đã khai (generator) | BP0 dòng 594-622 | writer: `[generator]` (chỉ tự ghi output của mình) — reader: `[qa_runtime, production]` |

## DELIVERABLE (khung, KHÔNG build cho tới khi đủ 4 điều kiện ở trên)

### D1 — `governance/blueprint/schemas/episode_schema.yaml` (field-hóa, CẦN Mr.Long duyệt TRƯỚC)
Field-hóa cấu trúc `episode.md` hiện có (prose, `ep_scaffold_template.md`) thành schema máy-đọc-được
CHỈ SAU KHI có bằng chứng Mr.Long duyệt field cụ thể (không phải "làm G7 đi" chung chung — bài học
G6-5). Không tự suy đoán field nào chưa có precedent prose.

### D2 — `tools/episode_generator.py` (manager, CHỈ build sau khi CẢ 4 điều kiện đủ)
Đọc packet thật từ `decision_engine` (G6a, budget nhịp) + `story_planner` (G6b, kế hoạch reveal)
+ 14 domain còn lại (chỉ READ, theo đúng `interface_contracts.yaml`) → sinh `episode.md` theo
scaffold. KHÔNG tự tạo nhân vật mới (bible/03 cấm) · KHÔNG tự quyết ratio/pacing (đó là việc
decision_engine, generator chỉ THI HÀNH quyết định có sẵn) · KHÔNG tự phong PASS (qa_runtime +
auditor làm) · KHÔNG render (production làm).

### D3 — Wire `tools/svhmp_preflight_qa.py` vào luồng generator mới
Validator đã EXISTS — không viết lại, chỉ xác nhận generator mới gọi đúng nó trước khi coi 1
episode.md là hoàn tất, khớp `audit_rule` BP0: "episode.md qua FULL_TEXT_GATE trước render (R197);
viết cảnh không có budget sheet = VIOLATION".

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
`forbidden_operations: write`) · M3 field episode_schema field-hóa không có bằng chứng Mr.Long
duyệt ĐÚNG field đó → FAIL · M4 cảnh sinh ra thiếu budget sheet đính kèm → FAIL (audit_rule BP0) ·
M5 gỡ stage `G7_generator` khỏi ci_gate → unwire test phải đỏ · M6 generator tự tạo nhân vật/vật
phẩm mới không có trong canon → FAIL (bible/03/12 CẤM).

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
D1 (episode_schema) chỉ tồn tại kèm bằng chứng Mr.Long duyệt field ✅ · D2 (episode_generator.py)
chỉ tồn tại khi đủ 4 điều kiện chặn ✅ · D3 wire preflight thật, không viết lại logic ✅ · D4 gate
1 cửa + unwire-guard ✅ · D5 dry-run EP01 có so sánh số liệu thật (không phải "chạy được là xong")
✅ · registry 0/0/0 · pytest xanh, không giảm baseline hiện tại.

## RÀNG BUỘC
Claim pack `python tools/build_claim.py claim g7_generator <phiên>` — nhưng CHỈ claim khi đã tự
tay chạy đủ bảng "ĐIỀU KIỆN CHẠY" ở trên và cả 4 dòng đều xanh, không claim "để giữ chỗ" rồi chờ
sau (giữ chỗ khi chưa đủ điều kiện = tự tạo áp lực build-ahead cho chính mình).

STATUS cuối: KHUNG_CHUAN_BI (chưa phải READY_FOR_AUDIT — file này chỉ có giá trị khi G6a+G6b thật
xong, đọc lại bảng điều kiện chạy để tự xác nhận trước khi bắt đầu bất kỳ dòng code nào).
