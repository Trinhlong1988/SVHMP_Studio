# PHƯƠNG ÁN PHASE BP — v2 (sau audit CMD_ARCH_AUDIT 3/7) — Builder đề xuất, Mr.Long quyết
_CMD_BUILD 3/7 · v1 đã tích hợp thêm: phản hồi CMD_ARCH_AUDIT ("promt CMD_ARCH_AUDIT.txt": điểm Decision 5/10 · Lifecycle 6/10 · Versioning 6/10; kết luận KHÔNG mở BP1 vội — thêm 1 vòng khóa hẳn BP-C). File local — KHÔNG commit khi chưa duyệt._

## A. ĐỒNG THUẬN VỚI AUDITOR (Builder xác nhận đúng, nhận làm)
1. **KHÔNG mở BP1 khi BP-C chưa khóa hẳn** — khớp phản biện D5 của v1. BP-C 912786f đang candidate, amendment còn mở.
2. **Decision Architecture (finding #6 — nặng nhất, 5/10):** ĐÚNG và quan trọng nhất. Không có Decision Engine giữa Story Planner và Generator thì generator tự quyết ratio/pacing/POV = hallucination có hệ thống. Nhận: thêm domain `decision_engine` (quản dialogue/narration ratio, emotion/fear/reveal curve, pacing, scene/information/silence budget, character focus, POV). Số liệu curve vẫn theo R195 — calibrate từ EP01 golden, KHÔNG bịa.
3. **Lifecycle (finding #3):** Nhận 2 tầng: (a) status ref mở rộng `exists|planned|deprecated|archived` (giữ PLANNED HONESTY 5-metadata; thêm rule: cấm dependency/reader/writer trỏ domain `archived`); (b) vòng đời contract per-domain: `draft→candidate→approved→deprecated→archived` (field `lifecycle` hiện tại đang trộn khái niệm — tách thành `lifecycle` mới + `lock_type: bible|tool|none`). (c) State machine ENTITY (Ghost Dormant→Watching→Manifest...) = NỘI DUNG của pack Runtime+Event, BP-C chỉ chuẩn hóa FORMAT khai state machine.
4. **Versioning (finding #4):** Nhận: `meta.schema_version` (format YAML) + `meta.contract_version` (nội dung) + `meta.validator_version` (phải khớp `__version__` của checker — cross-check máy); semver, thiếu/lệch = FAIL.
5. **Layer đặt tên (finding #2):** Nhận dạng `layer_groups`: **Narrative** (canon+character+dialogue+event+story+decision) · **Runtime** (generator+qa_runtime+production) · **Presentation** (tts+audio+video) · **Business** (publisher+analytics). Nhóm là NHÃN trên layer-số hiện có — KHÔNG phá DAG "chỉ depend layer thấp hơn". Ví dụ auditor giữ nguyên giá trị: Character không đi thẳng Audio (đã bị chặn sẵn bởi forbidden_dependencies + layer).
6. **Cross-domain event (finding #5):** Nhận FORMAT tại BP-C (event = name + emitter + chain có thứ tự, mỗi hop phải là reader hợp lệ của hop trước); CHUỖI cụ thể (Ghost Appears → World → ... → Analytics) thuộc pack Runtime+Event.

## B. PHẢN BIỆN CỦA BUILDER với list 30 domain (finding #1) — domain ≠ facet
List auditor có giá trị "khóa một lần" nhưng **trộn 3 tầng khái niệm** và **tự thiếu 3 mục đang có tool thật** (TTS · Production · Story Planner — chính list này quên, chứng minh: chốt bằng list chat sẽ sót; phải chốt bằng BẢNG PHÂN TẦNG ký một lần). Nguyên tắc phân tầng: **DOMAIN = có owner/manager/schema/validator riêng · FACET = trường dữ liệu THUỘC domain, vào Ownership Matrix · STRUCTURE = cấp tổ chức nội bộ 1 domain.**

| Mục auditor nêu | Đề xuất tầng | Căn cứ |
|---|---|---|
| Character, Dialogue, World, Timeline, Event, Supernatural, Culture, Belief, Ritual, Location, Weather | **DOMAIN** | khớp inventory TASK_BP-C |
| Generator, QA Runtime, Audio, Video, Publisher | **DOMAIN** | khớp TASK + tool thật |
| Analytics | **DOMAIN** (mới, nhận) | manifest + tools/analytics_populate.py TỒN TẠI thật |
| Story | **DOMAIN** = `story_planner` (giữ tên) | tránh 2 tên 1 domain |
| Scene, Episode, Series, Ending | **STRUCTURE** trong story_planner | cấp tổ chức truyện, không có manager riêng |
| Relationship | **FACET** của character | R210: Relationship Graph BẮT BUỘC nằm trong bible/37 |
| Inventory (nhân vật cầm gì), Skill | **FACET** của character | thuộc hồ sơ nhân vật |
| Item | **DOMAIN** = `object` | bible/12 Object library (71+ OBJ_) = source-of-truth THẬT đang tồn tại |
| Knowledge | **FACET** character (nhân vật biết gì) + phần "manh mối" = RESERVED overlay trinh thám | generic-core vs overlay (roadmap §2) |
| Quest | **RESERVED domain** (khai chỗ, planned toàn phần, cho thể loại phiêu lưu/trinh thám) | chưa có consumer SVHMP; khóa chỗ để "sau này dễ bổ sung" đúng ý auditor mà không phình core |
| Narration | **FACET** của dialogue (voice/narrator rules bible/15) | tách domain riêng = 2 owner cho 1 dòng text |
| Memory | **RULE xuyên suốt** (mỗi scope có owner) — như v1/Q1 | Memory là domain thì owner của scope tự mâu thuẫn |
| (auditor thiếu) TTS, Production | **DOMAIN** (giữ) | svhmp_v13_render LOCKED = manager thật |
| (mới #6) Decision Engine | **DOMAIN** `decision_engine` | chống hallucination |

→ **Inventory đề xuất chốt: 24 domain** = world · timeline · location · weather · culture · belief · ritual · supernatural (8 canon, L1) → character · object (L2) → dialogue · event (L3) → story_planner (L4) → decision_engine (L5) → generator (L6) → qa_runtime (L7) → tts (L8) → audio (L9) → production (L10) → video (L11) → publisher (L12) · analytics (L12) + **RESERVED:** quest (+ knowledge-overlay ghi trong object/character facet). FACET đầy đủ từng domain = pack Ownership (BP3) — BP-C chỉ khóa FORMAT facet.

## C. ROADMAP CHỐT — theo cấu trúc 9 pack của auditor (ARCH_AUDIT có thẩm quyền kiến trúc)
| Pack | Nội dung | Ghi chú Builder |
|---|---|---|
| **BP0** | Blueprint Constitution — **AMENDMENT v2** rồi Mr.Long lock | 4 bổ sung mục D dưới |
| BP1 | Core Architecture (5 doc: system_blueprint/domain_catalog/dependency_rules/runtime_boundary/glossary) | + test drift catalog↔contract |
| BP2 | Domain Architecture (contract chi tiết canon+character+object+dialogue+event) | reconcile tool thật, cấm rebuild |
| BP3 | Ownership + Dependency (facet matrix: **1 facet = 1 writer**, machine-checkable) | trả lời "Emotion ai own" bằng máy |
| BP4 | Runtime + Event (runtime flow, state machine entity, event bus chains, memory architecture mở rộng) | |
| BP5 | Validation (checker suite: schema/dependency/ownership + review flow) | |
| BP6 | Decision Architecture (decision_engine spec: ratio/curve/budget contract + nguồn calibrate R195) | |
| BP7 | Narrative Architecture (story structure Scene→Series, pacing format, cultural engine spec) | |
| BP8 | Production Architecture (render chain, golden output R196, video/publisher gates) | |
Mỗi pack: BUILD → self-test 4 lệnh → audit adversarial → Mr.Long ký lock → pack sau. Tier-2 Engines (Fear/Foreshadow/Probability...) vẫn để SAU SYSTEM_BLUEPRINT v1.0 lock (giữ phản biện v1 — auditor không phản đối điểm này).

## D. AMENDMENT v2 CHO BP-C (scope cụ thể, 1 phiên build khi được ký)
A1. Inventory 14→24+RESERVED theo bảng B (layers đánh lại số 1-12, forbidden_dependencies rà lại từng domain mới).
A2. Status enum: `exists|planned|deprecated|archived` (+rule cấm trỏ archived; deprecated cấm làm dependency MỚI).
A3. `lifecycle: draft|candidate|approved|deprecated|archived` + `lock_type: bible|tool|none` (thay enum cũ trộn khái niệm).
A4. Versioning meta 3 trường + cross-check `validator_version` == checker `__version__` (semver, máy so).
A5. Domain `decision_engine` đủ 12 mục (manager/schema/validator planned + 5 metadata trung thực).
A6. `layer_groups` 4 nhãn (Narrative/Runtime/Presentation/Business) — checker: mỗi domain thuộc đúng 1 nhóm.
A7. FORMAT spec: facet+ownership (data ở BP3) · event contract (data ở BP4) · state machine (data ở BP4).
A8. Cập nhật 5 doc + checker + negative test mới (archived-dep FAIL · version lệch FAIL · facet 2 writer FAIL-format) + registry/file_index/manifest → 4 lệnh verification xanh → READY FOR AUDIT.

## E. CẦN MR.LONG KÝ (1 lần, đủ để chạy A1-A8)
1. **Bảng phân tầng mục B** — đặc biệt: Item→`object` (bible/12)? Relationship/Inventory/Skill/Narration = facet? Quest = RESERVED? Memory = rule? Analytics vào core?
2. Inventory chốt **24 domain + RESERVED** (hay Mr.Long thêm/bớt dòng nào — sau lock BP0 là ĐÓNG).
3. Roadmap **9 pack BP0-BP8** (mục C) thay khung 5 pack v1.
4. Spec lifecycle/versioning/decision_engine (mục D: A2-A5).
5. Lệnh cho Builder chạy AMENDMENT v2 (A1-A8) → audit → lock BP0.
