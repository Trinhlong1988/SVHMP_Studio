# CONTENT-OS MASTER ROADMAP — tiến trình chốt (Boss 2/7)
_Hoàn thiện tổng thể + tái dùng cho tiểu thuyết / podcast / tình cảm / trinh thám. Lập luận từ bằng chứng, không suy luận._

---

## 1. LẬP LUẬN TỪ HIỆN TRẠNG (evidence)
`tools/architecture_registry_check.py` (deep-audit 2/7, strict): **230 disk file · 246 declared · 0 MISSING · 0 DUP · 0 UNMAPPED**. _(G1 đã triage xong 186→0; checker giờ exit 1 nếu bất kỳ MISSING/DUP/UNMAPPED — F5.)_
- Dự án đã phình hữu cơ (nhiều thế hệ `audit_*`, `auto_fix_*`, `rewrite_ep*`, `qa_*`).
- **Rủi ro gốc:** thiếu Tier-0 → mỗi lần code thêm dễ trùng module, mất source-of-truth → loạn.
- **Đã fix gốc (G0):** `governance/architecture_registry.yaml` + checker + hiến pháp **R211** (reconcile R7/R200, không nhân đôi).

## 2. NGUYÊN LÝ CHỐT — GENERIC CORE + GENRE OVERLAY (chìa khoá tái dùng)
Để 1 engine phục vụ N dự án nội dung số:
- **CORE (content-agnostic, tái dùng):** Governance · Character Identity · Dialogue/Voice · World/Time/Event · Story Memory · Continuity/QA framework · TTS/Audio · Analytics.
- **OVERLAY (config + bible theo thể loại):** SVHMP=kinh dị/nuối tiếc/hồn · tiểu thuyết=chương/arc POV · tình cảm=nhịp quan hệ · trinh thám=manh mối/đánh lạc hướng/thời điểm lộ.
- **Cơ chế:** engine đọc `project_config` (genre, distribution target, bộ phương ngữ, beat template, taxonomy) → **cùng code, khác project**.
- **Bằng chứng đã có mầm:** Character schema `bible/37` đã tách **LÕI universal (7 chiều)** vs **PHỦ narrative (SVHMP)** — đúng nguyên lý này.

## 3. KIẾN TRÚC CHỐT (6 tầng)
| Tier | Lớp | CORE (tái dùng) | OVERLAY (SVHMP) |
|---|---|---|---|
| 0 | Governance | registry, change-gate, ownership, promotion, audit | — |
| 1 | Bible/Schema | Character, World, Time, Event, Dialogue, Story | regret, ghost, chuyến-xe |
| 2 | Managers | Character/Context/Dialogue/Story-Memory/Object manager | — |
| 3 | Validators/QA | Character/Dialogue/Timeline/Continuity/Math/Culture QA | supernatural QA |
| 4 | Production | TTS · Audio QA · Mix · Video · Publish | brand audio |
| 5 | Analytics | retention · comment · error-feedback loop | — |

## 4. TIẾN TRÌNH (phased, mỗi phase DoD-gated + test + registry + log_ping + commit)
> **PHƯƠNG ÁN MỚI — Mr.Long duyệt 3/7/2026** (thay bảng cũ; đây là source-of-truth DUY NHẤT, bảng G-số cũ hết hiệu lực). Sau Governance v1.0 (locked): Luật bản vẽ → Bản vẽ → xây từng domain. Mỗi tầng: BUILD → audit adversarial → Mr.Long ký → freeze.

| Phase | Nội dung | Trạng thái |
|---|---|---|
| **G0** | Tier-0 Governance (registry+checker+R211+ownership+change-gate) | ✅ DONE |
| **G1** | Triage 186 unmapped → 0 | ✅ DONE |
| **GOV** | Enterprise Governance v1.0 — 5 pack locked + tag `governance-v1.0` + promotion_status locked | ✅ **DONE 2/7** |
| **BP-C** | **Blueprint Constitution v2.0** — 22+1 domain ĐÓNG · decision layer · lifecycle+versioning · dup-key loader; tag `blueprint-constitution-v2.0` | ✅ **DONE 3/7** |
| **BP** | **SYSTEM_BLUEPRINT v1.0** — BP1 Core · BP2 Domain · BP3 Ownership · BP4 Runtime ✅ locked+tag 3/7 · **BP5 Validation + G2-B1/B2 miner 🔄 đang build** (song song per TASK_G2 đã duyệt) · BP6-8 **THIN+TIMEBOX** (luật 10 MASTER) → FINAL AUDIT (+implementability) → tag `system-blueprint-v1.0` | 🔄 |
| **G2** | **Character** — ĐÃ CÓ LÕI (bible/37 + character_manager wired render L339/344 + R205/R206; ~92%): **AUDIT theo blueprint + vá gap** (fill roster, secondary-cast, sample YAML) — KHÔNG rebuild (cấm nhân đôi) | ⏳ |
| **G3** | **Dialogue** — generator sinh thoại dùng voice profile (ROI cao nhất) | ⏳ |
| **G4** | **World + Timeline + Event** + Story Memory + Continuity QA | ⏳ |
| **G5** | **Supernatural** (domain độc lập — Ghost/Spirit/Curse/Ritual/Omen/SacredObject/Belief/Karma/Possession; KHÔNG giấu trong World/Event) | ⏳ |
| **G6** | **Story Planner** — Dialogue/Narration Ratio · Pacing · Emotion/Suspense/Reveal Curve · Cliffhanger · Scene Budget | ⏳ |
| **G7** | **Generator** — sinh episode theo planner + domain managers | ⏳ |
| **G8** | **QA Runtime** — ĐÃ CÓ LÕI (pack5: detector R188-191, waiver R204, watch): AUDIT theo blueprint + vá gap (F2 harness, F8 real-audio calibrate) — KHÔNG rebuild | ⏳ |
| **EP01** | Prototype: re-render EP01 bằng pipeline mới = acceptance test toàn hệ | ⏳ |
| _(sau)_ | Generic-core đa dự án (`project_config` — validator P4 sẵn) · Analytics · Video · Publisher | backlog |

## 5. DEFINITION OF DONE (mỗi domain mới ship)
`schema · manager · validator · report · test PASS · md doc · sample YAML · regression chống trùng` — thiếu 1 = chưa DONE.

## 6. RÚT KINH NGHIỆM (đã note vào memory)
1. **Governance trước feature** — 186 file unmapped = hậu quả code trước, quản sau.
2. **Generic-core vs genre-overlay tách ngay từ schema** — không thì mỗi genre viết lại từ đầu.
3. **Mọi claim = confusion-test + evidence** (R203/206/207/208 mỗi cái 1000/1000; balance 7→0 flag).
4. **Reconcile hiến pháp sẵn có, không nhân đôi** (Change-Gate=R7, Audit=R200/log_ping, Promotion=bible lock).
5. **Calibrate/kiểm chứng từ dữ liệu thật (Golden/roster), không suy luận, không bịa field.**
6. **50 tập hiện có = THỬ NGHIỆM TURN 1, không phải nội dung cố định phải giữ nguyên** (Boss chốt
   5/7, xem §7 mục mới). Bằng chứng: `runtime/lifecycle.yaml` (state machine chính thức) cho thấy
   **chưa tập nào từng PUBLISHED** — kể cả EP01 chỉ mới `QA_PASS (tentative)`, ep_2 còn ghi
   `not_yet_generated` dù `output/ep_02..50/` đã có file (nghĩa là 49 tập đó viết ngoài pipeline
   chính thức, không qua Director/QA Lock tracking). Bài học: không cần sợ "phá nội dung đã lên
   sóng" khi sửa/patch/regen — 0 khán giả thật đã xem. Tránh lặp lỗi: đổ công vá tay từng lỗi nhỏ
   (DEBT-001 intro drift, G2-4 tên chưa đồng bộ vào episode.md) như thể đó là sản phẩm cuối cùng —
   những patch đó chỉ TẠM THỜI, giá trị thật nằm ở việc rút kinh nghiệm để G6-G8 (pipeline chuẩn)
   đủ tốt rồi regen lại toàn bộ, không phải giữ nguyên 50 tập nháp bằng mọi giá.

## 7. QUYẾT ĐỊNH CẦN BOSS (cập nhật 3/7 tối — câu G1/G3 cũ hết hiệu lực, G1 đã DONE)
- ✅ **GPU máy render = RTX 5060 Ti 16GB** (Mr.Long cấp specs 3/7 tối) → máy render = máy TRAIN chính (LoRA FLUX); máy Admin 3060 12GB = inference phụ/QA. S3-0 chỉ còn benchmark tốc độ, không còn câu hỏi khả thi.
- ✅ **Phong cách video HDK = ĐỘNG-TĨNH 2D · stack FLUX + LoRA** (Mr.Long chốt 3/7 tối): FLUX.1-dev fp8 trên 16GB cho still cinematic + parallax/hiệu ứng + lip-sync (LivePortrait) — không cần full animation, hợp horror.
- Cloud-GPU fallback: **tạm đóng** — 5060 Ti 16GB đủ train local; chỉ mở lại nếu benchmark S3-0 fail.
- ✅ **IP2 = HUYỀN SỬ VIỆT** (Mr.Long chốt 3/7 tối): visual **anime/chibi** (ảnh + video), cách kể **trẻ trung hoạt náo** — đối cực HDK (horror trầm) → test overlay platform chuẩn nhất: cùng engine, khác bible/LoRA/tone. LoRA chibi train dễ trên 5060 Ti, dung sai consistency cao.
→ **§7 ĐÓNG — cả 4 quyết định đã chốt 3/7 tối.**

- ✅ **50 tập hiện có (ep_01-50) = thử nghiệm turn 1, sẽ REGEN lại qua pipeline chuẩn G6-G8 khi
  xong** (Mr.Long chốt 5/7, xem §6 mục 6 bằng chứng lifecycle.yaml). Không giữ nội dung cũ bằng
  mọi giá — mục tiêu turn 1 là rút kinh nghiệm/phản biện/bắt lỗi để chuẩn hoá, không phải bản
  chốt cuối cùng. Tiền lệ tái dùng: `output/archive_draft_v1_ep11_41/` (đã archive 1 bản nháp cũ
  khi có bản mới hơn) — làm lại đúng cách đó ở quy mô lớn hơn khi G7/G8 sẵn sàng.

## 8. AI STUDIO EXPANSION — Mr.Long CHỐT 3/7/2026
> Bản đầy đủ (kiến trúc 4 tầng · phân xử AUDIT.md · hạ tầng đo thật · rủi ro): `AI_STUDIO_PLAN.md`
> — hiện ở Desktop, nhập vào `governance/` kèm mapping file_index sau khi builder lands BP5.

Hắc Dạ Ký → **AI Studio đa IP** (video 2D animation, train local). Nguyên tắc bất biến:
Governance hiện tại = móng, KHÔNG xây lại · mỗi Factory mới = pack ceremony đầy đủ ·
**REALITY ANCHOR** (luật 9 MASTER): pack lock cần ≥1 artifact chạy dữ liệu thật ·
Studio Core = **EXTRACT từ dây chuyền đã chạy** (sau S1), cấm build-ahead.

| Phase | Nội dung | Acceptance đo được |
|---|---|---|
| **S0** 🔄 | BP5+G2-B1/B2 (đang build) → BP6-8 thin → `system-blueprint-v1.0` | freeze_gate 5/5 mỗi pack; blueprint_suite 1 lệnh xanh |
| **S1** | Vertical slice AUDIO: fix 4 vi phạm content ep_01 → re-render EP01 → đo KPI thật | EP01 PASS golden + bảng KPI per-episode đầu tiên |
| **S2** | Studio Core v0 (extract từ S1): Asset Registry mở rộng · Prompt Registry · Cost Dashboard · dep-matrix generator (máy-sinh từ BP yaml) · ADR retro mỏng | dashboard trả lời "1 tập = bao lâu/token/$" bằng số thật |
| **S3** | Visual Foundation: S3-0 benchmark tốc độ (timebox 3 ngày) → Art/Character Visual Bible (từ bible/37) → **LoRA FLUX** style + nhân vật, train trên **máy render 5060 Ti 16GB**, inference phụ/QA trên 3060 12GB | consistency 20 ảnh/nhân vật, người duyệt ≥90% |
| **S4** | Animation 2D + lip-sync + compose → **EP01 VIDEO** publish YouTube | EP01 video lên kênh + KPI video vào dashboard |
| **S5** | Multi-IP: **Huyền Sử Việt** (anime/chibi, kể trẻ trung hoạt náo) onboard CHỈ bằng `project_config` + bible + LoRA riêng (P4 validator sẵn) | 1 tập HSV end-to-end; đo thời-gian-onboard = KPI platform #1 |
| **S6** | Scale 90 tập HDK · cost optimize · analytics feedback loop | tập/tuần ổn định; $/tập giảm theo đường cong |

**KPI tách:** _Platform_ = thời gian onboard IP mới · % tool tái dùng · $/phút content ‖ _Product_ = tập/tuần · lỗi QA/tập · retention/comment · $/tập.
**Track song song:** G3-G8 (bảng §4) = Story Factory buildout; EP01-pipeline-mới vẫn là acceptance của track đó.
**Backlog trả trong S0-S1:** dup-key loader cho `architecture_registry_check` (bug class H6) · `verify_ping_claim` 24 UNKNOWN · bảng rule↔enforcer máy-sinh · ADR retro (`docs/adr/`) · xác nhận revoke PAT.

## 9. TRẠNG THÁI REAL-TIME (đồng bộ 5/7 tối — MỌI CMD đọc mục này trước khi claim pack mới,
tránh hỏi lại thông tin đã có sẵn ở đây; nguồn: `python tools/build_claim.py status` + `git tag`)

**Đã LOCK (có tag, xem `governance/architecture_registry.yaml`):**
`bp1..bp9` + `blueprint_constitution` + `system_blueprint` + `governance-v1.0` (locked từ 2/7-4/7)
· `g4_world` (tag `g4-world-v1.0`) · `g5_supernatural` (tag `g5-supernatural-v1.0`) ·
`decision_engine`/G6a (tag `g6a-decision-engine-v1.0`) — cả 3 lock 5/7.

**Đang hoạt động (claim `active`, xem `build_claim.yaml` để biết ai/lúc nào):**
- `g6b_story_planner` — CMD_BUILD, code `tools/story_planner.py` (schema đã Mr.Long duyệt A).
- `g2_audit_fix` — CMD_BUILD_2, sửa 3 lỗi audit G2 (voice cá tính hóa thật, đồng bộ tên vào
  episode.md ep_12-49, gỡ CHARACTER_GATE khỏi file LOCKED) — 2/3 gần xong tại thời điểm ghi.
- `debt005_006_fix` — CMD_BUILD_3, fix khẩn 2 lỗi hạ tầng CHẶN CI GATE MỌI PHIÊN (race-condition
  corrupt `output/ep_01/` khi 2 phiên chạy pytest đồng thời + regression rule R86) — xem
  `governance/TECH_DEBT.md` DEBT-005/DEBT-006. **KHÔNG push gì cho tới khi pack này release**,
  CI gate sẽ FAIL hợp lệ (không phải lỗi của bạn) cho tới lúc đó.

**Sẵn sàng lock, CHỜ Boss xác nhận:**
- `g3_dialogue` — audit vòng 2 PASS toàn phần (4/4 điểm route-back), chưa có tag/registry entry.

**Đã duyệt, CHƯA build xong (không phải build-ahead nếu build ĐÚNG bản đã duyệt):**
- `story_plan_schema.yaml` — Mr.Long duyệt A, `governance/proposals/story_plan_schema_proposal.yaml`.
- `episode_schema.yaml` — Mr.Long duyệt B (có ngoại lệ ep73/90 cho bell_count/driver_lines),
  `governance/proposals/episode_schema_proposal.yaml`.

**Khung chuẩn bị (chưa claim được, còn thiếu điều kiện — đọc file trước khi claim):**
- `g7_generator` — xem `prompts/TASK_G7_GENERATOR.md`, còn thiếu G6b code xong (3/4 điều kiện
  khác đã đủ: G6a lock, cả 2 schema đã duyệt).
- `g8_qa_runtime` — chưa có khung chuẩn bị, chưa ai claim.

**Quyết định chiến lược 5/7 (xem §6 mục 6 + §7 phía trên):** 50 tập hiện có = thử nghiệm turn 1,
sẽ regen qua pipeline G6-G8 khi xong — đừng đầu tư sâu vá tay nội dung cũ ngoài mức cần thiết.

**Nợ kỹ thuật mở:** DEBT-002 (audio hook/cliffhanger, pipeline làm sạch có sẵn) · DEBT-003 (sfx
ACE-Step, chờ API) · DEBT-004 (scene_context G3↔G6, chờ G6b) · DEBT-005/006 (xem trên, đang fix)
· GOV-1 (bible/00 changelog, đang điều tra lại) · GOV-2 (roster --strict, chờ G2 audit fix xong
mới bật — KHÔNG tự bật khi dữ liệu voice còn đang sửa).
