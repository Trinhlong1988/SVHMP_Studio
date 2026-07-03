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
| **BP-C** | **Blueprint Constitution** (luật xây bản vẽ) — `governance/blueprint/00-04` + checker + test; Domain Inventory khoá TRƯỚC (18 domain); mọi element khai `exists\|planned` | ⏳ **KẾ TIẾP** |
| **BP** | **SYSTEM_BLUEPRINT v1.0** (bản vẽ thật ~20 doc: domain catalog/dependency/data-flow/memory-architecture/manager specs...) — xây theo BP-C | ⏳ |
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

## 7. QUYẾT ĐỊNH CẦN BOSS (để em chạy tiếp đúng thứ tự)
- Ưu tiên **G1 (dọn 186 file)** hay **G3 (Dialogue generator — ra chất truyện nhanh)** trước?
- Mốc tái dùng G5: chọn thể loại làm project mẫu đầu tiên (podcast tình cảm / trinh thám)?
