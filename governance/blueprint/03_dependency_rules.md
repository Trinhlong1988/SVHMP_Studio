# BLUEPRINT — 03_dependency_rules.md — Luật layer + hướng phụ thuộc
> Enforce: `tools/blueprint_constitution_check.py` C4–C5 (layer map + dependency direction + supernatural độc lập) · chứng thực: `tests/test_blueprint_constitution.py` (neg5 sai hướng, neg6 gộp supernatural).

**Mission:** Kiến trúc chảy MỘT chiều: canon → nhân vật → kế hoạch → sinh → QA → render → phân phối. Không bao giờ ngược.
**Purpose:** Chặn lớp bug kiến trúc đắt nhất: phụ thuộc vòng/ngược (canon import generator, QA import thứ nó chấm) — thứ không thể sửa rẻ khi đã lan.
**Scope:** `layers` map + `dependencies` + `forbidden_dependencies` của 14 domain trong `blueprint_domains.yaml`. KHÔNG quản nội dung field (doc 02).
**Authority:** Đổi layer của domain = đổi kiến trúc = Mr.Long duyệt qua Change Request Gate (R211).
**Responsibilities — bảng layer v2 (số nhỏ = nền móng; bảng E 3/7):**
| L | Domain | Ghi chú |
|---|---|---|
| 1 | world · timeline · location · weather · culture · belief · ritual · supernatural | canon gốc — **dependencies RỖNG TUYỆT ĐỐI; tham chiếu ngang CHỈ qua reader (điều kiện 1 kiểm duyệt); dep L1↔L1 = VIOLATION L1-CROSS-DEP** |
| 2 | character · object | đứng trên canon |
| 3 | dialogue · event | đứng trên character/object |
| 4 | story_planner · quest (RESERVED) | kế hoạch từ canon+nhân vật+sự kiện |
| 5 | decision_engine | AI Decision Layer — quyết nhịp TRƯỚC khi viết |
| 6 | generator | sinh theo budget sheet của decision_engine |
| 7 | qa_runtime | chấm output — ĐỘC LẬP với generator (forbidden) |
| 8–10 | tts → audio → production | chuỗi render |
| 11–12 | video → publisher · analytics | phân phối + đo lường |

**layer_groups (4 nhãn — nhãn trên layer-số, KHÔNG thay DAG):** narrative (L1–L5) · runtime (generator/qa_runtime/production) · presentation (tts/audio/video) · business (publisher/analytics). Checker bắt: mỗi domain thuộc ĐÚNG 1 nhóm.
**Workflow:** khai dep → checker C4: dep phải là domain đã khai + layer THẤP HƠN strictly + không nằm trong forbidden_dependencies → vi phạm = exit 1.
**Mandatory Rules:** (1) Chỉ được depend layer thấp hơn STRICTLY — cùng layer cũng cấm (dialogue không depend event). (2) `qa_runtime` CẤM depend `generator` — người chấm không dùng logic người làm bài (mirror nguyên tắc auditor độc lập Builder). (3) **Supernatural ĐỘC LẬP**: là domain top-level, CẤM `sub_of`, CẤM domain khác `contains` nó, CẤM nó depend world/event/story_planner — luật siêu nhiên đứng riêng để không bị "tiện tay" nhét vào lore. (4) Canon L1 dependencies rỗng tuyệt đối — 8 domain canon tham chiếu nhau CHỈ qua `reader` (vd location đọc world); checker in `L1-CROSS-DEP` khi vi phạm. (5) CẤM dep/reader/writer trỏ domain `lifecycle=archived`; dep vào `deprecated` = WARN di cư. (6) Cross-domain event (FORMAT tại contract, data ở BP4): mỗi hop kế tiếp trong chain PHẢI nằm trong `reader` của hop trước — chuỗi Ghost Appears → World → Character → ... không được nhảy cóc qua quyền đọc.
**PASS Criteria:** checker C4+C5 exit 0: mọi dep đúng hướng, 0 forbidden dep bị dùng, supernatural độc lập (ENFORCED).
**FAIL Criteria:** dep ngược/ngang hướng → `[VIOLATION] SAI HUONG`; dep nằm trong forbidden list → FAIL; supernatural bị gộp → `[VIOLATION] contains supernatural` / mất độc lập → FAIL.
**Examples:** `character.dependencies: [generator]` → FAIL `character(L2) depend generator(L5) — SAI HUONG`; `world.contains: [supernatural]` → FAIL; `production.dependencies: [generator, qa_runtime, tts, audio]` (L9 ← L5/6/7/8) → hợp lệ.
**Promotion Rules:** theo `governance/constitution/00_constitution.md` — reconcile, KHÔNG nhân đôi.
