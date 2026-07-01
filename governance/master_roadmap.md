# CONTENT-OS MASTER ROADMAP — tiến trình chốt (Boss 2/7)
_Hoàn thiện tổng thể + tái dùng cho tiểu thuyết / podcast / tình cảm / trinh thám. Lập luận từ bằng chứng, không suy luận._

---

## 1. LẬP LUẬN TỪ HIỆN TRẠNG (evidence)
`tools/architecture_registry_check.py` (chạy 2/7): **213 file · 30 mapped · 0 MISSING · 0 DUP · 186 UNMAPPED**.
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
| Phase | Nội dung | Trạng thái |
|---|---|---|
| **G0** | Tier-0 Governance (registry+checker+R211+ownership+change-gate) | ✅ **DONE** (evidence trên) |
| **G1** | Triage 186 unmapped → gán domain / dedupe / mark deprecated | ⏳ tiếp theo |
| **G2** | Character domain DoD-complete: +sample YAML, secondary-cast, fill occupation/role, **WIRE completeness-gate** vào render | ~80% (schema/manager/4 validator/report/test done) |
| **G3** | **Dialogue domain** — generator sinh thoại DÙNG voice profile (ROI cao nhất cho chất truyện) | ⏳ |
| **G4** | World/Time/Event + Story Memory + Continuity/Timeline QA | ⏳ |
| **G5** | Trích **generic-core** + `project_config` → chạy thử 1 project mẫu (romance-podcast) không sửa code | ⏳ (mốc tái dùng) |
| **G6** | Analytics Tier-5 (retention/comment feedback → cải tiến) | ⏳ |

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
