# TASK — 18 completeness gap từ audit đa-agent 222-agent (9-10/7)

> Viết bởi CMD_AUDIT 10/7. Đây là output của agent "completeness critic" cuối workflow gốc (khác
> với 56 finding đã tách thành `TASK_AUDIT_CRITICAL_G3_G5.md` 2 mục + `TASK_AUDIT_HIGH_G2_G8.md` 25
> mục + `TASK_AUDIT_MEDIUM_LOW_G2_G8.md` 27 mục). Gốc: `C:/tmp/g2g8_audit_gaps.json`.
>
> **Khác biệt quan trọng với 3 task doc trước:** 3 doc kia là "bug đã xác nhận, sửa theo hướng X".
> Doc này là **"vùng/lens CHƯA được audit"** — hầu hết KHÔNG phải bug đã biết, mà là chỗ 8 domain
> audit gốc (G2-G8) chưa soi tới. Việc cần làm là **áp lại đúng 4 lens đã dùng cho 56 finding kia**
> (cross-domain-write / enforcement-gap / doc-code-drift / fabrication) vào vùng/lens này, rồi:
> - Nếu soi xong **sạch** → ghi 1 dòng xác nhận vào file này (đổi `[ ]` thành `[x] SẠCH — <bằng
>   chứng>`), KHÔNG cần sửa gì.
> - Nếu soi ra **finding thật** → xử lý đúng quy trình đã dùng (bằng chứng chạy thật, không suy
>   đoán; nếu đụng domain LOCKED thì TU CHỈNH có ủy quyền per Mr.Long 10/7, ghi rõ trong commit +
>   architecture_registry.yaml).
> Riêng **#14 đã là finding THẬT** (không phải gap thuần tuý) — xử lý như 1 bug bình thường.

## RÀNG BUỘC CHUNG
- KHÔNG cố tìm bug bằng mọi giá — nếu soi kỹ mà sạch thật, ghi nhận "SẠCH" là kết quả hợp lệ, không
  cần bịa ra vấn đề để báo cáo.
- `pytest tests/ -q` xanh, `architecture_registry_check.py` 0/0/0 sau mọi thay đổi.
- Việc này KHÔNG có deadline cứng — quy mô lớn (rà 6+ domain governance/blueprint chưa từng soi),
  có thể làm tuần tự theo nhóm dưới, báo tiến độ qua `log_ping.py` sau mỗi nhóm xong (không đợi cả
  18 mục xong mới báo 1 lần).

---

## Nhóm DOMAIN GAP (8 mục — domain/lớp file hoàn toàn chưa được 8 audit gốc quét)

- [x] **#1 `audio_render`** (tier 4, locked) — `svhmp_v13_render.py`, `svhmp_audio_qa.py`,
  `cap_peak.py` + 5 test R199-R204 — pipeline audio THẬT (R196 Golden Production), chưa ai audit độc
  lập bằng 4 lens.
- [x] **#2 `text_gate`** (R197 FULL_TEXT_GATE, tier 3, locked) — xác nhận claim "bắt buộc trước MỌI
  render, không ngoại lệ" có thật sự được gọi ở TẤT CẢ entrypoint render (`svhmp_v13_render.py`,
  `render_with_character_gate.py`, `render_chunk.py`, `render_section.py`) hay chỉ 1 số.
- [x] **#3 `publisher`/`tts`/`production`/`video`/`analytics`** (6/22 domain blueprint, layer 8-12) —
  đặc biệt `publisher` gắn `bp9/content_policy.yaml` (rủi ro PHÁP LÝ — Nghị định 38/2021 + Điều 320
  BLHS), hiện chỉ có structural schema check, KHÔNG có runtime content scanner. Rà xem có claim nào
  tự nhận "đã enforce" nhưng thực tế chưa.
- [x] **#4 `naming`** (bible/23, `build_name_pool.py`, `gen_100_passenger.py`) — xác nhận
  `forbidden_edit: rule_02 word-uniqueness` còn đúng trên tập 139 passenger (đã tăng từ 100 LOCK gốc,
  xem G2 finding #2/#4 trong `TASK_AUDIT_HIGH_G2_G8.md`).
- [x] **#5 `regret`** (bible/11, distribution 32/24/20/14/10, 27 sub-archetype) — tính lại tỷ lệ phân
  bố thật trên 139 passenger, xác nhận còn khớp 32/24/20/14/10 hay đã lệch sau khi tăng từ 100→139.
- [x] **#6 `audit_ping`** (R200, `log_ping.py`, PING_CMD_LEAD_29_06.md) — cơ chế bắt buộc mọi CMD
  dùng để báo cáo, nhưng chưa ai kiểm tra chính nó có chống giả mạo/bỏ sót hay không (vd: CMD tự ý
  không gọi `log_ping.py` sau khi fix — có gì phát hiện được không).
- [x] **#7 `bp1-bp9`** (toàn bộ 9 pack blueprint đã "locked", Tier-0 nền tảng của
  `architecture_registry.yaml`) — áp 4 lens cho chính các file bp1/bp2/bp3/bp5/bp7/bp8/bp9 (bp4/bp6
  đã bị audit bắt sửa-sau-lock-không-xin-phép, đã TU CHỈNH — kiểm xem 7 pack còn lại có case tương tự
  chưa bị phát hiện không).
- [x] **#8 `object`/`location`/`weather`/`culture`/`belief`/`ritual`** (6/22 domain, khai "planned")
  — kiểm "planned honesty": có file manager/validator nào đã âm thầm tồn tại trên đĩa mà
  `blueprint_domains.yaml` vẫn khai "planned" không (đúng loại lỗi G5 đã bắt với `entity_class`).

## Nhóm FILE GAP (5 mục — file cụ thể trong domain ĐÃ quét nhưng bản thân file đó bị bỏ sót)

- [x] **#9** `tools/character_manager.py` (domain G2, nguồn thật của `CharacterRegistry` mà dialogue
  domain claim "đọc qua") — chưa finding G2 nào soi logic MANAGER gốc này, chỉ soi validator/roster/
  schema hạ lưu.
- [x] **#10** `bible/03_character_bible.yaml` (CHAR_DRIVER + CHAR_NAM, "CẤM tạo mới") — kiểm 2 nhân
  vật lặp lại này có bị ảnh hưởng bởi drift 100→139 passenger không.
- [x] **#11** `tools/auto_watch.py` + `runtime/auto_watch_state.yaml`/`auto_watch_log.jsonl` +
  `tools/qa_watch_supervisor.py` (domain G8, daemon THẬT gọi `qa_skeptic_orchestrator.py` production,
  không phải test/mock) — chưa finding G8 nào chạm tới.
- [x] **#12** `tools/calibrate_decision_policy.py` (domain G6a, công cụ tạo `bible/42_decision_policy.yaml`,
  căn cứ cho claim "tái lập 100%" trong `architecture_registry.yaml:246`) — chưa finding G6a nào xác
  nhận/bác bỏ tính tái lập 100% này.
- [x] **#13** `prompts/ep_scaffold_template.md` + `bible/08_novelty_constraints.yaml` (domain G7,
  source_of_truth chính thức nhưng chưa finding G7 nào chạm tới — 7 finding G7 chỉ xoay quanh
  `episode_schema.yaml`/`no_write_domain`/`decision_engine`).

## Nhóm META GAP (1 mục — đã là finding THẬT, không phải gap thuần)

- [x] **#14 (đã CONFIRMED, xử lý như bug)** `governance/manifests/unclassified_manifest.yaml` (sinh
  bởi `tools/gen_domain_manifests.py`) vẫn liệt kê `character_manager.py`, `dialog_voice_validator.py`,
  `story_consistency_validator.py`, `svhmp_v13_render.py`, `svhmp_preflight_qa.py`,
  `svhmp_audio_qa.py` dưới domain `unclassified`/owner `UNASSIGNED` — dù cả 6 file đã có domain rõ
  ràng trong `architecture_registry.yaml` (character/audio_render/text_gate). Đây là doc-code(data)-
  drift thật vì chưa ai đọc thư mục `governance/manifests/`.
  **Đề xuất fix:** chạy lại `tools/gen_domain_manifests.py` (nếu nó tự đọc registry để sinh manifest
  thì chỉ cần re-run là hết drift) — nếu KHÔNG tự động re-sync, cần sửa script để đọc đúng domain từ
  `architecture_registry.yaml`/`file_index.yaml` thay vì để `unclassified` cứng. Xác nhận sau khi sửa
  6 file trên không còn nằm trong `unclassified_manifest.yaml`.

## Nhóm METHOD GAP (4 mục — lens/phương pháp chưa từng áp dụng xuyên toàn bộ 56 finding)

- [x] **#15 reproducibility/evidence-freshness** — 56 finding đều trích số liệu quá khứ ("pytest 596
  passed", "registry 0/0/0"...) nhưng không finding nào tự chạy lại TẠI THỜI ĐIỂM ĐỌC để xác nhận số
  liệu còn đúng. Việc cần làm: chọn mẫu (không cần cả 56) các claim số liệu quan trọng nhất trong 3
  task doc đã giao, chạy lại xác nhận còn đúng — nếu lệch, ghi rõ lệch bao nhiêu (không phải lỗi audit,
  vì baseline đổi theo thời gian là bình thường — chỉ cần biết còn đúng hay không).
- [x] **#16 concurrency/race-condition** — nhiều CMD chạy song song ghi chung file
  (`runtime/*.yaml`, `output/ep_*`, `qa_waivers.json`) — DEBT-005 đã xử lý riêng cho
  `output/ep_01/`, nhưng các file `runtime/*.yaml` khác (vd `build_claim.yaml`,
  `event_ledger_draft.yaml`) có cơ chế khoá/atomic-write không? Rà các writer của những file này,
  xác nhận có/không có lock — nếu thiếu và có rủi ro thật (nhiều CMD ghi đồng thời), áp dụng
  `golden_lock`/`atomic_write_json` pattern đã có sẵn trong repo (không viết cơ chế mới).
- [x] **#17 content-instance compliance/legal** — `bp9_compliance_check.py` (HB01/HB02, Nghị định
  38/2021 + Điều 320 BLHS) chỉ kiểm cấu trúc schema, chưa ai quét NỘI DUNG THẬT của 50 tập đã render
  xem có vi phạm HB01/HB02 không. Đây là rủi ro pháp lý thật — **KHÔNG tự triển khai runtime content
  scanner mới** (việc lớn, ngoài phạm vi 1 CMD tự quyết) — chỉ xác nhận hiện trạng (có/không có gì
  quét nội dung thật) và ghi vào `TECH_DEBT.md`, đề xuất Mr.Long quyết có cần xây scanner riêng
  không.
- [x] **#18 security/path-traversal/injection** — các finding ghi-sai-domain (G3
  `write_episode_line`, G7 `forbidden_operations` text-grep) mới xét góc độ ownership, chưa xét góc độ
  path-traversal/injection (tham số như `ep_n` có thể chứa ký tự đường dẫn độc hại đưa thẳng vào
  `Path()`/`subprocess` không). Rà nhanh các entrypoint nhận `ep_n`/tham số string từ bên ngoài
  (`episode_generator.py`, `dialogue_generator.py`, render pipeline) — xác nhận có validate kiểu/dải
  giá trị trước khi ghép path không. Đây là rà soát phòng ngừa (không có bằng chứng khai thác thật
  tại thời điểm audit) — nếu tìm thấy lỗ hổng thật, ưu tiên báo ngay qua `log_ping.py VIOLATION`
  trước khi tự fix.

---

## DoD
Mỗi mục 1 trong 2 kết quả: **[x] SẠCH** (kèm bằng chứng đã soi — lệnh chạy, file đã đọc) hoặc
**finding thật** (kèm fix + bằng chứng + cập nhật `TECH_DEBT.md`/registry nếu cần). Không bắt buộc
làm hết 18 mục trong 1 lần — báo tiến độ theo nhóm qua `log_ping.py`. Registry 0/0/0, pytest xanh sau
mọi thay đổi.

## THAM CHIẾU
Gốc: `C:/tmp/g2g8_audit_gaps.json` (18 gap, agent "completeness critic" cuối workflow 222-agent
9-10/7). Cùng đợt: `TASK_AUDIT_CRITICAL_G3_G5.md`, `TASK_AUDIT_HIGH_G2_G8.md`,
`TASK_AUDIT_MEDIUM_LOW_G2_G8.md`.

---

# KẾT QUẢ AUDIT — CMD_BUILD_2, 2026-07-11 (claim debt_completeness_gaps)

> Phương pháp: 5 subagent điều tra READ-ONLY song song (4 lens) + CMD_BUILD_2 tự verify tận tay
> mọi finding trước khi hành động/escalate (R215 điều 4 — subagent report KHÔNG phải bằng chứng
> độc lập). Baseline tươi tại thời điểm audit (R215 điều 3 reproducibility): **pytest 725 passed /
> 0 fail** (chạy lại thật, 656s), **registry 0/0/0**. Số cũ trong 3 task doc trước (596/616/720)
> tăng theo thời gian do thêm test — không lệch, không regression.

## ĐÃ FIX (committed, in-scope + authorized)
- **#14 META** — FIXED (commit reconcile file_index + regen manifest). Root cause: `file_index.yaml`
  gán `domain: unclassified` cho 5 file mâu thuẫn registry (SoT): character_manager +
  dialog_voice_validator→character, svhmp_v13_render + svhmp_audio_qa→audio_render,
  svhmp_preflight_qa→text_gate (story_consistency_validator đã đúng, chỉ manifest stale). 6 file
  rời unclassified (17→10). Phát hiện phụ: thư mục `manifests/` thiếu nhiều domain manifest chưa
  từng commit (không có freshness gate) → đã regen đủ 34. registry 0/0/0, test_file_index_total PASS.
- **#16 METHOD concurrency** — FIXED (commit build_claim atomic). `build_claim._save()` dùng plain
  `write_text` → corrupt `runtime/build_claim.yaml` nếu ghi bị kill/nhiều CMD ghi (mỉa mai: chính là
  công cụ chống-đụng-độ). Áp pattern atomic (tmp+os.replace) có sẵn. +1 test regression. 8/8 pass.
  Residual TOCTOU (2 session cùng claim) cần lock riêng = cơ chế mới → DEBT-017.
- **#7 DOMAIN bp1-bp9** — gate 7 pack đều DEEP (0 gate nông — SẠCH). bp1/bp2/bp3/bp7 bị edit
  post-lock (ĐÃ có Mr.Long auth trong commit) nhưng lock line thiếu addendum như bp4/bp6 →
  FIXED (commit thêm addendum doc-parity, verify tận tay 4 commit d67998b/6591d72/811d3ce/ae706e5).
  bp5/bp8/bp9 SẠCH (0 post-lock edit).

## SẠCH (soi kỹ + bằng chứng, không cần sửa)
- **#3 publisher/tts/production/video/analytics** — mọi manager/validator/schema khai đúng
  exists/planned vs đĩa (11 slot khớp 100%). Publisher chỉ có structural check, KHÔNG có runtime
  content scanner — khai TRUNG THỰC ở 3 nơi (blueprint_domains:740, bp9_compliance_check docstring,
  bp9/00_compliance.md:27). Không claim "enforced" quá lời. (→ #17 legal bên dưới.)
- **#8 object/location/weather/culture/belief/ritual** — 13/13 tool+schema path + 4/4 bible path
  đều ABSENT thật; grep 0 implementation ẩn. Chỉ có proposal (planning). KHÔNG dính lỗi G5
  entity_class (file ẩn khai planned). Planned honesty PASS.
- **#9 character_manager.py** — đọc full: 0 fabrication (chỉ consume roster+bible/03), docstring
  khớp behavior, by_ep/completeness/missing_ext/_group_nonempty đúng, chỉ ghi qua save_enriched ra
  file riêng (không đè skeleton). Cross-domain write: sạch.
- **#10 bible/03 CHAR_DRIVER/CHAR_NAM** — 0 ID/name collision với 139 roster; "Kỳ Bách" là
  false-positive substring; rule_04 (loại 'Nam') giữ. Drift 100→139 không rò rỉ recurring char.
- **#12 calibrate_decision_policy.py** — determinism CONFIRMED (0 random/time/env/net, pure over
  golden LOCKED). "Tái lập 100%" hợp lệ. Caveat: 2/11 knob (reveal_curve/information_budget) là hằng
  đếm-tay có trích dẫn dòng golden (R195-compliant) — tái lập trivial, KHÔNG tự phát hiện golden
  drift; đã ghi caveat, không refute claim.
- **#13 ep_scaffold_template.md + bible/08** — word budget 6 section, distance_constraints
  (15/10/8), word_count range [2000,2700] đều KHỚP CHÍNH XÁC code trích. 2 conflict đã biết
  (bell_count bible/00 vs 09; phase enum) đã self-flag trong schema, không phải drift mới.
- **#15 reproducibility** — đã chạy lại thật: pytest 725 passed/0 fail, registry 0/0/0 (xem trên).
- **#18 security/path-traversal** — 3 entrypoint nhận CLI arg (biên trusted-operator), int-validate
  ep_n trước khi ghép path, 0 `shell=True`, subprocess list-form. Không lỗ hổng khai thác từ input
  untrusted. LATENT thấp: `dialogue_generator.write_episode_line()` non-numeric ep_n chưa sanitize
  (KHÔNG reachable từ untrusted, đã có guard production-overwrite) → ghi chú DEBT-019, không fix gấp.

## FINDING THẬT → ESCALATE Mr.Long (thẩm quyền R_SUPREME R1, KHÔNG tự sửa — đã ghi TECH_DEBT)
- **#2 text_gate R197 (HIGH, constitutional)** — R197 (TỐI THƯỢNG) khẳng định FULL_TEXT_GATE
  (svhmp_preflight_qa.py) chạy TRƯỚC MỌI render "không ngoại lệ, FULL stack không 1 tool". VERIFY
  TẬN TAY: **0 render entrypoint gọi svhmp_preflight_qa** (svhmp_v13_render/render_with_character_gate/
  render_chunk/render_section); render thật chỉ gọi 1 tool `qa_eol_diacritic.py` (đúng thứ R197 CẤM),
  còn 2 bypass (missing-md skip; cờ `--skip-r86`). Chính `pack5/19_qa_pipeline.md:10` +
  `TASK_PACK5_BUILD.md:14` đã ghi "render KHÔNG gọi nó" → R197 là văn bản chưa reconcile, machine-false.
  Đúng lớp R215. → DEBT-018. Mr.Long quyết: (a) wire preflight vào render để R197 thành thật, hay
  (b) sửa lời R197 khớp thực tế pack5/19.
- **#1 audio_render** — tests R199-R204 là behavior-test THẬT (SẠCH). Nhưng: (1a) `svhmp_audio_qa.py`
  docstring "POST-RENDER mandatory/Block ship" trong khi 0 caller tự động (bp8/render_chain.yaml:73
  đã ghi `enforcement_mode: manual`) — drift; (1b) R199 guard `aggressive_trim_tail` đã chết (render
  dùng `qa_clean_tail`), docstring còn ghi "hardlock active"; (1c) "LOCKED v1.3" không có checksum
  enforcer. Gắn với #2 (cùng câu chuyện gate audio/text) → ghi DEBT-018, KHÔNG tự reconcile docstring
  theo 1 hướng vì Mr.Long có thể chọn wire-mandatory (đảo hướng).
- **#4 naming** — forbidden-15 sạch (0 hit), word-uniqueness enforce THẬT (validator word_owner map).
  Drift: bible/23 (immutable) khẳng định uniqueness tuyệt đối + hook "100/100 unique / 200/200
  syllable" nhưng ở 139 có 3 ngoại lệ canon (PAS_0151 Hạ Nhi chia syllable Hạ/Nhi; PAS_0131 Nguyễn
  1-syllable) — waiver CHỈ nằm trong code validator, bible chưa ghi. → DEBT-020 (sửa bible cần Mr.Long).
- **#5 regret** — `passenger_roster_100.yaml` header `distribution_actual: 32/24/20/14/10` là số
  CŨ per-100; thật ở 139 = 40/31/29/23/15 + 1 RFC_PENDING (PAS_0151 pillar chưa gán). `distribution_
  lock_bible_11: true` KHÔNG có enforcer nào recompute. 27 sub-archetype phủ đủ, 0 ID bịa. bible/11
  distribution là forbidden_edit (Mr.Long lock) → DEBT-021 (Mr.Long quyết: rebalance hay cập nhật
  metadata + gắn enforcer).
- **#6 audit_ping (R200)** — honor-system: `log_ping.py` thuần append, KHÔNG check fact→claim (fix+push
  mà quên log = 0 gate bắt); `verify_ping_claim.py` chỉ check claim→fact (chống bịa), git hooks chỉ
  `.sample`. Đúng lớp R215 "CHƯA CÓ ENFORCER — rủi ro drift". → DEBT-022 (xây anti-omission gate =
  cơ chế mới, Mr.Long quyết).
- **#17 content-instance legal** — xác nhận hiện trạng: `bp9_compliance_check.py` chỉ kiểm cấu trúc
  schema HB01/HB02, KHÔNG có tool nào quét NỘI DUNG THẬT 50 tập đã render. Rủi ro pháp lý thật
  (Nghị định 38/2021 + Điều 320 BLHS). KHÔNG tự xây scanner (việc lớn) → DEBT-023 đề xuất Mr.Long.
- **#11 auto_watch (phụ)** — SẠCH phần enforcement (thật sự spawn orchestrator, circuit-breaker,
  supervisor có single-instance lock). Gap phụ: auto_watch.py KHÔNG có single-instance guard +
  save_state non-atomic → gộp vào DEBT-017 (concurrency).
