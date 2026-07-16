# TỔNG HỢP AUDIT GỐC RỄ + ĐỀ XUẤT SIẾT HIẾN PHÁP (17/7)

- **Người lập:** CMD_AUDIT (KIEM_DUYET)
- **Yêu cầu Mr.Long:** "tìm gốc rễ nguyên nhân TẤT CẢ bug từ đầu đến giờ, fix sạch gốc, siết hiến pháp" + "xây CÔNG THỨC/KHUÔN story-agnostic để sinh nhiều truyện".
- **Phương pháp:** 7 agent audit ĐỘC LẬP song song (reproducibility: chạy lại enforcer tại HEAD, không trích số cũ) + CMD_AUDIT **tự verify tay** các claim trọng điểm (đánh dấu ✅VERIFIED).
- **Trạng thái:** CHỜ DUYỆT — chưa codify rule/sửa nội dung nào từ bản này.

---

## 1. GỐC RỄ ĐƠN — trả lời "nguyên nhân của tất cả bug"

**CLAIM–ENFORCER GAP:** một khẳng định "đúng/PHẢI/CẤM/đã-enforce" (trong rule/bible/docstring/schema) mà đằng sau **KHÔNG có gate hành vi thật trên dữ liệu thật**. 3 biến thể = 1 gốc:
- **Class 1 — không gate** (~16 bug): rule tuyên bố, 0 checker.
- **Class 2 — gate giả** (~10 bug): kiểm token/grep/composition thay vì hành vi; gỡ logic vẫn PASS.
- **Class 3 — drift** (~11 bug): gate từng đúng rồi trôi khỏi thực tế sau LOCK/rename.

Cộng **~37/68 mục (>54%)**. R216 (backward-anchor) = ca đặc biệt cùng gốc, **tệ hơn** vì tạo *an toàn giả* (bible codify ngược → enforcer ngược → QA xanh → tin QA). Bằng chứng "cùng gốc lặp": B26→B28 (cùng session), B32→DEBT-038 (cp1252, 3 tuần), B7→B51-55 (6 lần).

**Gốc rễ THỨ HAI (cho mục tiêu KHUÔN):** thiếu **tầng extractor prose→structured-fact**. Mọi lock generic (`validate_consistency`, event lock) **inert** vì không ai trích fact từ prose để so. Và các extractor đang có (R216) là **regex hardcode cho truyện này** → zero generality. ✅VERIFIED (agent #3 + đọc code).

---

## 2. BẢN ĐỒ ENFORCED vs GAP (7 dimension)

### ✅ Enforced THẬT + mutation-proof (giữ, nhân rộng làm mẫu)
| Cơ chế | Bằng chứng |
|---|---|
| Architecture registry | 0/0/0, wired ci_gate |
| Character Tier1 + quê↔giọng (R210) | `roster_validator` C1-C5 blocking + mutation test 69 pass ✅ |
| Field-lock cross-episode CHARACTER (R207) | `story_consistency_validator` self-check mutate gender real-roster → sys.exit; 500-case R207 0FN/0FP ✅ |
| Siêu nhiên CẤU TRÚC (g5) | typology+possession SM, 16 test mutation-proof |
| Text QA: R86/FULL_TEXT_GATE, VNQA H1-H10, anti-slop bible/22, regret-variety | wired preflight+G8 |
| R208 dialogue age-appropriate | 1000-case (nhưng shallow, xem gap) |
| R216 cross-episode canon (seat) | ratchet wired ci_gate, 10 test mutation-proof ✅VERIFIED (tự dựng+fix) |
| Meta-enforcer R215.5/R215.6 | `test_no_greponly_wiring_guards` + `test_no_text_true_without_encoding` 6 pass |

### ❌ GAP — claim-without-enforcer / neutered / synthetic-only (cần siết)
| # | Claim (ngôn từ khẳng định) | Thực tế | Verify |
|---|---|---|---|
| G1 | R65 8-chiều logic `ABSOLUTE_HARDLOCK` (thời tiết/địa lý/vật lý/tâm linh) | enforcer `audit_logic_total.py` **KHÔNG tồn tại** | ✅VERIFIED |
| G2 | Event lock `thoi_diem/nguyen_nhan KHÔNG đổi giữa tập` | **synthetic-only**, 0 field thật trong event_ledger, 0 caller production, không có extractor | ✅VERIFIED |
| G3 | `post_render_gate` check "bác tài 2 câu" | **hardcode `results.append((True,...))`** — luôn PASS | ✅VERIFIED (đọc L85) |
| G4 | `ghost_visual max=1` "QA HARD-FAIL nếu explicit" | gate đếm `>=1` (cận DƯỚI), **không kiểm MAX** | ✅VERIFIED (đọc L101) |
| G5 | GHOST_RULES_3 (never_attack/chase/speak) "cứng" | chỉ trong **prompt LLM** (`auto_gen_ep.py:391`), 0 hậu kiểm content | agent-report |
| G6 | ENDING_RULES.unresolved_memory "QA HARD-FAIL" | 0 tool | agent-report |
| G7 | ALWAYS_5/NEVER_7/GHOST/SERIES_ARC `enforced_by: QA PHASE 12.x` | chỉ trong `prompts/qa.md` (LLM-judge), 0 gate máy/mutation-test | agent-report |
| G8 | ≥18 enforcement ref trỏ file KHÔNG tồn tại (5 cái mask như active: R61/R68/R69/R71/R72) + `.githooks/pre-render`, `pre-publish` không có | | agent-report (đã verify 1: audit_logic_total ✅) |
| G9 | R110 narrative continuity | `qa_continuity.py` **hardcode chỉ ep_01**, không wired | agent-report |
| G10 | "Relationship Graph BẮT BUỘC" (R210) | 0/139 data, 0 checker | agent-report |
| G11 | dialogue_ratio "phù hợp từng tập" | chỉ là **hint sinh** (knob), 0 gate hậu-sinh so ratio output; target = 1 hằng EP01 | agent-report |
| G12 | right-speaker attribution; child-register voice | 0 gate (chỉ driver 2 câu); child→giọng-già **không cả rule** | agent-report |
| G13 | weather/light/folklore/phong thủy (R121/R133-137) | `status:TBD`; bible/38-41 chưa tồn tại; phong thủy MISSING | agent-report |
| G14 | publish_score R140 "CRITICAL gate" | built nhưng **0 wiring** vào render/QA | agent-report |
| G15 | regression_report.json làm "test_evidence" cho ~7 rule | artifact **tĩnh 30/6** (số cũ đóng băng) | agent-report |

### ⚠ KHUÔN (generality) — hiện single-tenant SVHMP
- ~20 tool hardcode `runtime/passenger_roster_100.yaml`; region map/15 tên cấm/regret/bible paths = hằng SVHMP.
- extractor R216 = regex "Khải Phong/Hạ Vy" → 0 generality.
- **Thiếu config-surface story-id** + **thiếu tầng prose→fact extractor** → locks generic nhưng inert cho MỌI truyện.

---

## 3. ĐỀ XUẤT SIẾT HIẾN PHÁP (mỗi cái KÈM enforcer — không khẩu hiệu)

> Nguyên tắc: KHÔNG thêm luật khẩu hiệu. Mỗi đề xuất = 1 enforcer máy + mutation-proof, hoặc nhãn tường minh "CHƯA CÓ ENFORCER — DEBT-xxx".

1. **Claim registry + coverage gate** — `governance/claim_enforcer_map.yaml`: mọi khẳng định (PHẢI/CẤM/HARD-FAIL) trong CLAUDE.md/bible/docstring gắn `enforcer: <path::node>` HOẶC `NO_ENFORCER(DEBT-xxx)`. `tools/claim_registry_check.py` (ratchet): claim mới chưa đăng ký → FAIL; claim có enforcer → xác nhận test node **được pytest collect thật**. Đánh vào BACKLOG (không chỉ claim mới như R215.1).
2. **Meta-gate "mỗi gate phải có mutation-proof test"** — `tests/test_every_gate_has_mutation_test.py`: mọi entry `ci_gate.CHECKS` phải map 1 test mutation. Cấm wire gate nếu chưa có. (Đóng G3 hardcode-True, DEBT-009/037 như 1 CLASS.)
3. **Canon anchor provenance** — mọi field-hoá bible PHẢI có `anchor_ep`+`anchor_commit` (tập git sớm nhất). `tools/bible_canon_anchor_check.py` từ chối entry canon thiếu provenance (R216 hoá máy).
4. **Nhãn enforcement cho MỌI rule** — mỗi rule bible + khối TỐI THƯỢNG kết bằng `[ENFORCER:<test> | NO_ENFORCER:DEBT-xxx | HONOR_SYSTEM:approved-date | LLM_JUDGE_ONLY]`. `tools/rule_enforcer_label_check.py` FAIL nếu thiếu tag/trỏ file không tồn tại. **Làm honor-system + LLM-judge-only HIỆN HÌNH + đếm được** (đánh G7/G8/10 rule "Manual review").
5. **Advisory→gate** (R215.6 hoá máy) + ratchet cp1252 backlog về 0 + **fix 5 enforcer mask-as-active** (R61/R68/R69/R71/R72: build hoặc relabel "CHƯA CÓ ENFORCER").
6. **[KHUÔN] Tách STORY-DATA vs ENGINE-LOGIC** — CẤM hardcode literal truyện-cụ-thể (tên/địa danh/số) vào `tools/` engine. `tools/no_story_literal_in_engine_check.py` (ratchet allowlist) quét engine tìm story-literal. + Dựng **tầng extractor prose→fact** để lock generic chạy được trên MỌI truyện (đây là hạ tầng còn thiếu của "khuôn").

---

## 4. ĐÃ FIX TRONG PHIÊN NÀY (bằng chứng, đã/đang push)
- `fc196b5` (remote ✅): revert EP01 v8→v7 (R216, EP01=ground truth), gỡ enforcer build-ngược.
- `4a9f0ad` + `a06dcd6` (đang push): wire R216 ratchet gate vào ci_gate + codify `rule_R216_` + 10 test mutation-proof; **fix G3 frozen-list guard** (chính là 1 instance Class 2 tự phát hiện khi push bị hook từ chối — de-brittle thành subset, mutation-proof).

---

## 5. ĐỀ XUẤT THỨ TỰ (chờ Boss chốt)
1. **Duyệt 6 đề xuất siết hiến pháp** (mục 3) — cái nào làm, thứ tự.
2. **Phase 1 khoá canon nguồn về EP01** + rút story-literal khỏi engine + dựng extractor prose→fact (hạ tầng khuôn).
3. **Phase 2 regen 49 tập** sạch (chỉ sau khi canon nguồn khoá + gate đủ) — pipeline agent cuốn chiếu, verify độc lập từng tập.
4. **Phase 3 production validation** (R196).

CMD_AUDIT giữ kỷ luật: không codify/sửa nội dung khi Boss chưa duyệt mục 3-5.
