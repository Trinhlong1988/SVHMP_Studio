# PROPOSAL — DEBT-035 R216 reconcile (Hướng A: EP01 = ground truth)

- **Ngày:** 2026-07-17
- **Người lập:** CMD_AUDIT (KIEM_DUYET)
- **Thẩm quyền duyệt:** Mr.Long (canon authority, R_SUPREME R1/R2)
- **Trạng thái:** CHỜ DUYỆT — chưa thực thi bất kỳ thay đổi bible/21 + regen tập nào
- **Grounded bằng:** 3 agent scope 17/7 (seat / death / generator-source) — mọi số dòng dưới đây là firsthand, không suy đoán
- **Quyết định đã chốt:** Boss chọn **Hướng A** (EP01 thắng) + "chết ở nước ngoài là bình thường" (New York KHÔNG phải world-error)

---

## 0. CANON GỐC (EP01, tập sinh sớm nhất 26/6 — bất biến theo R216)

| Fact | Giá trị canon (EP01) | Nguồn |
|---|---|---|
| Chỗ ngồi Khải Phong | **ghế số BẢY** | `output/ep_01/episode.md:100,394,474` + `bible/27_fact_db.yaml:15` (R117 IMMUTABLE, đã đúng) |
| Ghế ba (EP01) | **ông cụ ôm radio** (KHÔNG phải KP) | `ep_01:178,252,422` + `bible/27_fact_db.yaml:40` |
| Cái chết Hạ Vy | **tai nạn TAXI ở New York** (sân bay Kennedy) sau khi đi du học Hoa Kỳ | `ep_01:232,242,264,298,336` |
| Đồng hồ | dừng **7:10** | `ep_01` nhiều dòng — LƯU Ý: motif toàn series, KHÔNG phân biệt version |
| Bối cảnh xe xuất phát | Hà Nội (hợp lệ — chỉ là nơi xe chạy, KHÔNG phải nơi Hạ Vy chết) | `ep_01:98,134` |

**Nguyên tắc reconcile:** mọi bản "ghế 3 / xe máy / phố Huế / Hai Bà Trưng / Bạch Mai / 12-4 / Hải Phòng" ở EP02-50 và trong các nguồn phái sinh = **bản SAI, sửa xuôi về EP01**. KHÔNG đụng EP01.

---

## 1. BẢN ĐỒ CORRUPTION (đầy đủ — cái gì phải sửa)

### 1a. SEAT (ghế 3 → ghế 7)
- **49 tập** EP02-50: mỗi tập 1 câu chính `"Khải Phong ngồi ghế thứ ba"` + (đa số) 1 câu `"quan sát từ ghế ba"`. Danh sách dòng đầy đủ: xem báo cáo agent seat (đính kèm runtime).
- **Bible/runtime hardcode ghế-3:** `bible/03:92-94,158,168` · `bible/21:107,109` · `runtime/canon_registry.yaml:26,33-34` · `bible/00:970` (template mẫu) · `runtime/roster_backfill_draft.yaml:5479`.
- **⚠ HARDCODE TRONG PYTHON:** `tools/auto_gen_ep.py:149,151,351` + `tools/auto_gen_ep_v3.py:521` in cứng literal "ghế thứ ba" — **đây là lý do regen vẫn ra ghế-3 dù sửa bible.**
- **Đã đúng ghế-7 (giữ):** `bible/27_fact_db:15` · `bible/21b:98` · `bible/24:25` · `runtime/state.yaml:133`.

### 1b. DEATH (Hà Nội/xe máy → New York/taxi)
- **13 tập field Hà Nội:** EP20,24,25,27,28,31,32,36,37,39,40,41,50 (mạnh nhất: EP24,25,36,37,40,50). Chi tiết: văn phòng Mộc Hà phố Hai Bà Trưng, ngã tư phố Huế–Hai Bà Trưng–Trần Hưng Đạo, bệnh viện Bạch Mai, 12/4/2018, tin nhắn "Anh ơi em sắp về" + "Anh ơi em yêu" viết dở (EP41).
- **Bible field-hoá Hà Nội:** `bible/03:99,122-129,150` (core_wound) · `bible/21` M4/M7/M8/M9/M12 · roster `4248,4327-4359,4735-4766`.
- **Nguồn phái sinh:** `runtime/event_ledger_draft.yaml:2215,2804` · `governance/proposals/bible03_driver_memory_arc_proposal.yaml#bang_arc_40_tap` (source-of-truth M3-M10) · hardcode `auto_gen_ep_v3.py:521` "về Hà Nội".

### 1c. ⚠ XƯƠNG SỐNG MEMORY-ARC + ROUTE/MAP (hệ quả NẶNG NHẤT — vượt ngoài seat+death)
Toàn bộ nửa sau series (M4-M18, EP51-90) dựng trên cái chết xe-máy-Hà-Nội:
- **M8** (`bible/21:63-66`): "ai bên Hạ Vy lúc chết — không phải Khải Phong".
- **M13** (`bible/21:89-92`, EP61-65 chưa viết): "chính **Khải Phong CHỞ Hà** — Hạ Vy ngồi sau xe máy Khải Phong".
- **M14-M15** (`bible/21:93-102`): "tai nạn xe đêm đó — Hà rơi xuống — Khải Phong chết theo Hà".
- **ROUTE/MAP** (`bible/21:269,275`): 50 stops = "bản đồ Hà Nội", hội tụ về **ngã tư phố Huế nơi Hạ Vy va** (payoff EP40:264-284, EP50:275-283).

**Xung đột kép của M13-M15 (agent xác nhận):**
1. **vs EP01 (canon):** Hạ Vy chết trong TAXI ở New York → Khải Phong KHÔNG thể "chở" cô bằng xe máy. M13-M15 **bất khả** dưới canon EP01.
2. **vs chính các tập Hà Nội đã viết:** EP36:249 "em đi xe máy MỘT MÌNH — không phải sau xe ai"; EP39:239 "anh Hải đi sau — chứng kiến"; EP32:245 "Khải Phong tới bệnh viện sau mẹ Hạ Vy 1 giờ" (KP không ở hiện trường). → M13 "KP chở" **đã mâu thuẫn nội bộ** ngay cả trước R216.

→ **Direction A buộc REDESIGN nửa sau series**, không chỉ sửa 13 câu chết. Đây là chi phí lớn nhất, Boss cần biết trước khi duyệt.

---

## 2. GENERATOR THỰC TẾ — vì sao "regen vẫn gen sai" (agent 3)

- **2 engine tách rời:**
  1. **Template engine cũ** (`auto_gen_ep.py`/`_v3.py`) = thứ THỰC SỰ sinh 49 tập. **Hardcode ghế-3/Hà-Nội trong Python**, chỉ đọc roster + bible/11, **KHÔNG đọc bible/03/21/core_wound**. Sửa bible → engine này KHÔNG đổi.
  2. **Kiến trúc mới** (`story_planner`→`episode_generator`) đọc bible/21 nhưng **chỉ ráp packet, KHÔNG viết prose**, và **chỉ chạy đủ EP01** (EP12-50 = `pending`, thiếu scene-level + driver_reveal_cumulative).
- **Không có prose-writing tool** — viết prose vẫn là người+LLM qua `prompts/generator.md` (đọc bible/03 + canon_registry).
- **Không có gate lúc-gen** đối chiếu output vs EP01. `cross_episode_canon_check.py` (mới) là post-hoc, mới cover seat, chưa cover death, chưa wire ci_gate.

**Hệ quả:** muốn hết gen-sai phải sửa CẢ **6 nguồn** (bible/03, bible/21, canon_registry, event_ledger_draft, bang_arc_40_tap, **+ hardcode Python**) — sửa thiếu 1 chỗ là drift ngược.

---

## 3. ĐIỂM QUYẾT ĐỊNH CHO BOSS (cần chốt trước khi thực thi)

- **Q1 — Seat collision:** EP02-50 chuyển KP→ghế7. Vậy (a) ghế-3 để trống hay chuyển ông cụ radio (EP01 canon) thành hành khách cố định ghế-3? (b) 8 tập có hành khách "ghế bảy" (EP02,11,24,34,37,44,45,49) — dời họ sang ghế khác, hay đổi số ghế KP? → **Đề xuất CMD_AUDIT:** giữ KP=ghế7 (khớp EP01 tuyệt đối), dời hành-khách-ghế-7 ở 8 tập sang ghế trống khác; ghế-3 EP02-50 để mô-típ ông-cụ/để trống tuỳ tập. Chờ Boss xác nhận.
- **Q2 — Death mechanism:** reconcile 13 tập + bible về "taxi New York / du học". Nhưng chi tiết đặc sắc "Anh ơi em yêu viết dở khi lái xe máy" (EP41) mất cơ sở (không lái xe máy ở New York). → Boss quyết: bỏ chi tiết đó, hay thay bằng biến thể hợp taxi/New York?
- **Q3 — ⚠ Memory-arc M13-M15 + route/map:** đây là quyết định NẶNG. Hai lựa chọn con:
  - **A1:** Giữ route = bản đồ Hà Nội (xe khách chạy ở VN, hợp lệ), nhưng REDESIGN M8/M13-M15: bỏ "KP chở Hạ Vy chết cùng"; reveal mới khớp EP01 (Hạ Vy chết xa nhà bên Mỹ, KP tiễn ở sân bay — nỗi đau "không giữ được / không ở bên"). Route/map trỏ về **sân bay/cổng B** thay vì "ngã tư phố Huế".
  - **A2:** Giữ nguyên ý đồ "KP chở/chết cùng" → **mâu thuẫn EP01, vi phạm R216** → LOẠI (trừ khi Boss lật R216).
  - → **Đề xuất CMD_AUDIT: A1.** Chờ Boss.
- **Q4 — Bản nháp archive** `output/archive_draft_v1_ep11_41/` (40 tập, tên "Quang", ghế-3, không field death): gộp bỏ hay giữ làm lịch sử? → Đề xuất: giữ nguyên (đã là archive), không đụng.

---

## 4. KẾ HOẠCH THỰC THI THEO GIAI ĐOẠN (sau khi Boss chốt Q1-Q4)

> Theo R_SUPREME R7 (Read→Diff→Proposal→Approval→Backup→Patch→Regression→Production) + R216. KHÔNG làm bước sau khi bước trước chưa PASS + Boss chưa duyệt mốc.

- **G0 (xong 17/7):** revert EP01 v7, gỡ enforcer ngược, dựng `cross_episode_canon_check`, reframe docs, commit `fc196b5`. ✅
- **G1 — Khoá canon + enforcer đủ mặt (KHÔNG regen):**
  - Mở rộng `cross_episode_canon_check.py` thêm fact "death location/mechanism" (anchor EP01 New York/taxi), + wire vào `ci_gate` mutation-proof (R215.5) — dựng input vi phạm → xác nhận FAIL.
  - Cập nhật bible/03 core_wound + bible/21 M-arc + canon_registry + event_ledger_draft + bang_arc_40_tap về canon EP01 (theo Q1-Q3 Boss chốt). Đây là **sửa nguồn**, chưa đụng 49 tập.
  - Gỡ hardcode ghế-3/Hà-Nội trong `auto_gen_ep*.py` (thay bằng đọc canon_registry đã reconcile) HOẶC deprecate engine cũ.
- **G2 — Regen/patch 49 tập (theo lô, mỗi lô QA + FULL_TEXT_GATE R197):**
  - Quyết định đường sinh (Q sau G1): patch tại chỗ seat+death (rẻ, giữ prose) HAY regen prose (đắt, cần prose-tool/LLM).
  - Lô nhỏ (vd 5 tập/lô), mỗi lô: backup → patch → `cross_episode_canon_check` PASS + R41 + R86 broad + dialogue_ratio + full suite → mới sang lô sau.
- **G3 — Redesign nửa sau (M8/M13-M15 + route payoff)** theo Q3.A1 — proposal RIÊNG (đây là sáng tác, ngoài phạm vi reconcile cơ học).
- **G4 — Production validation** (R196): render thật ≥1 tập đại diện, Boss nghe/duyệt trước khi coi là done.

---

## 5. RỦI RO / GIỚI HẠN (minh bạch)

- Regen 49 tập là khối lượng lớn + đụng prose đã QA/ship → rủi ro tái nhiễm bug khác nếu không FULL_TEXT_GATE từng lô.
- Nếu chọn patch-tại-chỗ thay vì regen: rẻ nhưng có thể để lại vết khâu văn phong (câu quanh seat/death viết cho ghế-3/Hà-Nội).
- Redesign M13-M15 (G3) là **sáng tác lại**, không phải sửa lỗi cơ học — cần Boss định hướng cảm xúc/reveal.
- `cross_episode_canon_check` hiện chỉ 1-2 fact; canon còn nhiều fact khác (tên/quan hệ/mốc) chưa có gate — **"CHƯA CÓ ENFORCER đầy đủ — rủi ro drift"** (R215.1), mở rộng dần.

---

## 6. TÓM TẮT 1 DÒNG

EP01 (26/6) = canon; bible/21 + 49 tập (27/6) codify ngược → phải reconcile xuôi về EP01 ở **6 nguồn + 49 tập + redesign nửa sau series**; chi phí lớn nhất KHÔNG phải seat/death mà là **M13-M15 "KP chở Hạ Vy" + route crash-site** phải thiết kế lại. Chờ Boss chốt Q1-Q4.
