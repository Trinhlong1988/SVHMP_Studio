# TASK G4 — WORLD / TIMELINE / EVENT (finalize từ Desktop draft 4/7, kiểm chứng + phản biện 4/7)

> Reconciled từ kiểm thử THẬT trên repo: khung ~80% có sẵn (BP4 event_bus/state_machines,
> bible/02 lore, R84 khai trong bible/00), máy canh ~25%, **ruột dữ liệu ~5%**. G4 = đổ ruột
> + vá 2 enforcer thiếu, KHÔNG xây lại khung. Nuôi trực tiếp BP7 cultural_spec + G5 supernatural
> typology (dependency thật, xem `governance/blueprint/bp3/dependency_detail.yaml`: `world` là
> domain KHÔNG phụ thuộc character/dialogue — character mới đọc từ world, không ngược lại).

## ĐIỀU KIỆN CHẠY
Không phụ thuộc G2/G3 (đã kiểm BP3: 0 dependency `world`→`character`/`dialogue`). Chạy song
song với G2 và G5 được ngay. Claim pack trước khi build (luật 11 MASTER):
`python tools/build_claim.py claim g4_world <phiên>`.

## MISSION
Bộ nhớ thế giới truyện: chuyện gì xảy ra, ở đâu, lúc nào, ai biết — để tập 80 không cãi tập 8.
KHÔNG suy luận, KHÔNG bịa — mọi entry có evidence ep:line (nguyên tắc miner đã thắng ở G2).

## NỀN ĐÃ CÓ (reconcile — CẤM nhân đôi R211; đã re-verify trực tiếp 4/7, KHÔNG suy đoán)
| Đã có | Ở đâu | Trạng thái verify lại (4/7, phiên kiểm duyệt) |
|---|---|---|
| Chuỗi sự kiện (khung) | `governance/blueprint/bp4/event_bus.yaml` | ✅ **8 event_id** khai báo (đính chính: KHÔNG phải "3 chain mẫu" như draft gốc — đã grep trực tiếp): `passenger_boards, ghost_appears, regret_triggered, passenger_dies, secret_revealed, ghost_released, qa_violation_found, episode_rendered`. Khung tốt, chain hợp lý — **0 dữ liệu 90 tập thật** |
| State machine | `bp4/state_machines.yaml` | ✅ **4 entity xác nhận đúng**: `ghost, character_fear, character_life, voice_state`, 0 orphan. Khung, chưa gắn dữ liệu |
| Lore/World | `bible/02_lore_db.yaml` + `bible/12_object_library.yaml` | 🔶 quá mỏng cho 90 tập (chưa re-đếm chính xác dòng, giữ nguyên đánh giá draft gốc "mỏng") |
| Fact checking | `tools/qa_fact_check.py` | ✅ tồn tại, chạy trong QA thật — fact rải rác nhiều file bible, không sổ cái, không nguồn/cấp-độ-tin |
| Continuity | `tools/story_consistency_validator.py` | ✅ xác nhận có `LOCKED_FIELDS` (character_id, full_name, gender, date_of_birth, …) — nhưng **chỉ phủ nhân vật**, không phủ sự kiện/đồ vật/thời gian |
| Timeline (luật) | `R84_temporal_anchor_for_events` trong `bible/00_constitution.yaml` dòng 321 | ❌ **NAMED KHÔNG ENFORCED — đã xác nhận lại, có ĐÍNH CHÍNH quan trọng**: grep `tools/*.py` cho "R84" CÓ 1 hit (`tools/pre_render_audit.py` dòng 3 "Check R84 mandatory") nhưng đọc kỹ nội dung — đây là **R84 KHÁC HOÀN TOÀN** (checklist 8 bước audio/text pre-render: word-audit/tail-check/pause/tempo/emo_vector), KHÔNG liên quan temporal_anchor. Đây là 1 vụ **trùng số hiệu luật giữa 2 ngữ cảnh** (bug class tương tự R141/142/143 dup-key đã fix ở bible/00, nhưng khác file/namespace) — ghi nhận riêng, KHÔNG thuộc scope G4 sửa, chỉ flag cho Boss biết. Kết luận cho G4: `R84_temporal_anchor_for_events` (bible/00) **enforcement thật = 0**, claim gốc của draft vẫn ĐÚNG bản chất dù lý do trích dẫn cần sửa. |
| Story memory (per-nhân vật) | facet `knowledge` (bible/37 v2.1) | ✅ mới bật, chưa có dữ liệu |
| Lịch âm/văn hóa vùng miền | Cultural KB | ✅ **ĐÃ QUA deep-research + adversarial-verify + Evidence Schema** (CMD_BUILD_3 SVAF pattern 4/5, `governance/evidence_schema_cultural_kb.yaml`, done 4/7) — KHÔNG còn "chờ Boss ký nguồn" như draft gốc ghi, nguồn đã verify xong, chỉ còn chờ BP7/G4 tự đưa vào bible chính thức |

## DELIVERABLES

### D1 — Timeline Engine (đóng nợ R84_temporal_anchor_for_events named-not-enforced)
`tools/timeline_check.py`: đọc mốc thời gian mỗi tập (tuyệt đối "8 năm trước" / tương đối "hôm qua") →
đối chiếu xuyên tập (2 tập cùng nhắc 1 sự kiện phải khớp mốc) + **hiểu lịch âm** (rằm tháng 7, Tết...) để
đối chiếu không khí/hành vi nhân vật có khớp mùa không (nạp bảng lịch âm từ Cultural KB, đã verify).
Reconcile: KHÔNG viết lại `qa_fact_check.py` — timeline_check gọi nó cho phần fact-date.

### D2 — Sổ cái sự kiện (miner pattern — nhân bản G2 đã thắng)
`tools/event_ledger_miner.py`: quét `output/ep_*/episode.md` ĐÃ CÓ (50 tập) → trích: sự kiện gì, tập nào,
liên quan nhân vật/đồ vật nào, mốc thời gian → `runtime/event_ledger_draft.yaml` (status: draft, evidence
ep:line bắt buộc, KHÔNG tự ghi vào sổ chính). Bonus: report mâu thuẫn sự kiện tự phát hiện được
(2 tập kể khác nhau về cùng 1 biến cố) → `reports/G4_EVENT_FINDINGS.md`.

### D3 — World/Fact Ledger
`bible/fact_ledger_schema.yaml` (đề xuất, đường proposals/ — writer mr_long, bible LOCKED cần authorization):
mỗi fact = `fact_id · nguồn (ep:line) · cấp_độ_tin (canon/dẫn_lời_nhân_vật/tin_đồn) · trạng_thái_theo_thời_gian`
(đồng hồ vỏ xà cừ đang ở tay ai tại tập N). Mở rộng `qa_fact_check.py` đọc sổ cái này thay vì suy luận rải
rác — diff tối thiểu, KHÔNG viết lại.

### D4 — Continuity mở rộng (khỏi chỉ-nhân-vật)
Mở rộng R207 sang 2 field-lock mới: **sự kiện** (thời điểm/nguyên nhân không đổi giữa các tập nhắc lại) +
**đồ vật** (vị trí/tình trạng không tự nhảy vô lý — "áo rách" không tự lành 5 phút sau) — KHÔNG tách pack
riêng, gộp vào D4 vì đã có R207 làm nền.

### D5 — Gate 1 cửa + wire
`tools/g4_world_check.py` (mirror pattern blueprint_suite/g3_dialogue_gate): gọi D1-D4, matrix PASS/FAIL,
KHÔNG short-circuit. Wire ci_gate stage `G4_world` + **unwire-guard test NGAY commit đầu** (bài học G2_roster).

## REALITY ANCHOR (luật 9)
- `event_ledger_miner` chạy thật trên 50 tập, số liệu findings ghi vào report (không chỉ khung rỗng).
- `timeline_check` bắt được ít nhất 1 mâu thuẫn thời gian thật trong 50 tập hiện có (nếu 0 = nghi ngờ tool
  yếu, phải bắn mutation trước khi tin).

## MUTATION AUDIT SẼ BẮN (khai trước — kiểm duyệt sẽ bắn thêm không báo)
M1 2 tập nhắc cùng sự kiện lệch mốc thời gian → FAIL · M2 đồ vật đổi trạng thái vô lý giữa 2 dòng liền kề
→ FAIL · M3 fact không nguồn (thiếu ep:line) → FAIL khi merge vào sổ chính · M4 sự kiện tập rơi đúng rằm
tháng 7 nhưng hành vi/không khí không khớp mùa → WARN (calibrate ngưỡng từ golden) · M5 gỡ stage G4_world
→ unwire test đỏ · M6 event chain dùng domain/facet không có trong BP2/BP4 đã khai → FAIL (mirror luật BP4
"hộp phải map facet đã khai").

## DoD
timeline_check bắt ≥1 lỗi thật ✅ · event ledger draft sinh từ 50 tập kèm evidence ✅ · fact ledger schema
Mr.Long ký ✅ · continuity mở rộng 2 field-lock mới có test ✅ · gate wired + unwire-guard ✅ · registry
0/0/0 · KHÔNG đụng render/pipeline LOCKED.

## RÀNG BUỘC
Claim pack trước khi build (`tools/build_claim.py claim g4_world <phiên>` — luật 11 MASTER) ·
số bịa = BÁC (R195) · nhân đôi tool sẵn = BÁC (R211) · commit UTF-8 no-BOM · worktree riêng (R200).

STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.
