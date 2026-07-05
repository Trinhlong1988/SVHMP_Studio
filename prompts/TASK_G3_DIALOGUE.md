# TASK G3 — DIALOGUE (bản tổng hợp cuối — reconcile 4 góc nhìn + 3 skeptic review, kiểm chứng trực tiếp trên repo 5/7)

> Đọc trực tiếp code (không suy đoán): hạ tầng dialogue **đã có 5 tool + 2 test confusion** hoạt
> động thật — `tools/dialog_voice_validator.py` (dialect/xưng hô/age-slang), `tools/audit_dialogue_hierarchy.py`
> (R48 pronoun-ambiguity) + `tools/auto_fix_dialogue_hierarchy.py` (auto-fix cùng cặp),
> `tools/audit_driver_dialogue_context.py` (R174, 2 câu LOCK bác tài), `tools/qa_dialogue_identity.py`
> (R191, speaker-embedding audio) — cộng `tests/test_character_system_1000_r206.py` (R206, 1000
> case, 0 FN/0 FP, input 100% synthetic tay gõ) và `tests/test_dialogue_appropriateness_1000_r208.py`
> (R208, 1000 case tuổi-tác/tiếng lóng qua `dialog_voice_validator.validate()` + `MODERN_SLANG`,
> 0 FN/0 FP) — **R208 đã wired thật trong `CHECKS` của `tools/ci_gate.py`** (skeptic-1 phát hiện:
> 1 bản nháp trước từng bỏ sót file này khi liệt "hạ tầng đã có").
> **CÁI CHƯA CÓ THẬT SỰ**: generator (0 file), gate 1 cửa `G3_dialogue` (chưa có; `ci_gate.py` hiện
> có **12 entry** trong `CHECKS` — `registry, blueprint, R199_tail, R203_conf, R205_char, R206_voice,
> R207_canon, R208_age, project_config, G2_roster, g5_supernatural, G4_world` — KHÔNG có entry nào
> tên `dialogue`/`G3_dialogue`), domain `dialogue` như **1 block độc lập** trong
> `governance/architecture_registry.yaml` (registry đã có sẵn `dependency_map` edge
> "Character -> Dialogue" / "Dialogue -> TTS", và `test_dialogue_appropriateness_1000_r208.py` đã
> đăng ký dưới domain `character` — nhưng chưa có block `dialogue:` cấp domain riêng làm chủ 4 tool
> audit trên), và quyết định tách/giữ-chung `dialogue_manager.py` với `character_manager.py`
> (`blueprint_domains.yaml` khai `manager.status: planned` kèm `blocking_dependency` chưa gỡ).
> G3 = xây đúng phần thiếu này, **KHÔNG viết lại** bất kỳ logic dialect/pronoun/identity nào đã tồn
> tại (R211), và đóng 3 món nợ kỹ thuật/governance đã bắt được bằng đọc code: (a) 2 nguồn quê↔vùng
> đang lệch nhau, (b) 3 tool audit (`audit_dialogue_hierarchy.py`, `audit_driver_dialogue_context.py`,
> `qa_dialogue_identity.py`) đã có nhưng **không stage nào trong `ci_gate.py` gọi chúng** (named ≠
> enforced — riêng `dialog_voice_validator.py` ĐÃ được exercise gián tiếp qua R208, không nằm trong
> nhóm "chưa gọi" này), và (c) `bp3/dependency_detail.yaml` chưa khai 2 cạnh phụ thuộc đang bị dùng
> ngầm: dialogue đọc `bible/02_lore_db.yaml` (SoT domain `world`) và `bible/31_golden_samples.yaml`
> (SoT domain `audio`) mà không có `dep__dialogue__world`/`dep__dialogue__audio` nào, và `dialogue`
> không có mặt trong `reader` whitelist của 2 domain đó (skeptic-3 phát hiện).

## ĐIỀU KIỆN CHẠY

Phụ thuộc thật (`governance/blueprint/bp3/dependency_detail.yaml` dòng 28-37):
`dep__dialogue__character` và `dep__dialogue__culture`, cả hai `data_flow: read`. G3 **CẤM ghi
vào** `bible/37` hay `runtime/passenger_roster_100.yaml` (luật 1-writer, R7). `forbidden_dependencies:
[production, publisher]` (`blueprint_domains.yaml` dòng 449) — tuyệt đối không import module 2
domain đó. `dep__generator__dialogue` xác nhận domain `generator` (G7, sau này) sẽ đọc TỪ dialogue —
G3 không phải "cái sinh cả tập", chỉ là lớp luật + công cụ mà G7 gọi lại.

**Gap phụ thuộc chưa khai trong BP3 (phát hiện skeptic-3, xác nhận đọc trực tiếp toàn bộ 268 dòng
`bp3/dependency_detail.yaml` — chỉ có đúng 2 `dep_id` với `from: dialogue`):** hạ tầng đã tồn tại
(`audit_driver_dialogue_context.py` đọc 2 câu LOCK từ `bible/02_lore_db.yaml:18-20`, SoT của domain
`world`) lẫn deliverable mới D5-Nguồn-B (đọc `bible/31_golden_samples.yaml`, SoT của domain `audio`)
đang dùng dữ liệu của 2 domain mà `dialogue` **không có trong `reader` whitelist** (`world.reader`
dòng 108 và `audio.reader` dòng 685 đều không liệt `dialogue`) và **không có `dep_id` BP3 tương
ứng**. G3 KHÔNG được coi đây là hợp lệ ngầm định chỉ vì code cũ đã đọc file đó — phải xử lý bằng D1B
(RFC bổ sung dependency, cùng cơ chế RFC như D1/D2), TRƯỚC khi D3 pass-through câu LOCK hoặc D5
Nguồn B được coi là chạy chính thức (dry-run cấu trúc thì được, y hệt ràng buộc D1 áp cho D3/D4).

- **character (G2)**: đang trong quá trình audit + vá gap (chưa 100% secondary-cast), nhưng field
  `tier_1_mandatory.voice` trong `bible/37_character_schema.yaml` v2.2 đã **LOCKED** và đã được
  `roster_validator.py` enforce trên roster thật (`runtime/passenger_roster_100.yaml`, sinh bởi
  `tools/gen_100_passenger.py`). G3 không cần chờ G2 xong 100%, chỉ đọc field đã tồn tại.
- **culture**: facet `xung_ho_convention` (`bp7/cultural_spec.yaml`) vẫn `status: planned`,
  `bible/38_culture_bible.yaml` **chưa tồn tại** (đã xác nhận 0 file). G3 KHÔNG được chờ vô thời hạn,
  cũng KHÔNG được tự dựng domain `culture` mới — bảng quê↔vùng/xưng hô hiện có trong
  `migrate_roster_v2.HOME` + `dialog_voice_validator.REGIONS` CHÍNH LÀ lớp văn hoá đang tồn tại
  trên thực tế; dùng tạm, ghi rõ nợ reconcile khi `bible/38` lock.

Claim pack trước khi build (luật 11 MASTER): `python tools/build_claim.py claim g3_dialogue <phiên>`.
Nếu G2 đang có claim mở và cũng sửa `bible/37_character_schema.yaml` cùng lúc — dừng, báo Boss
trọng tài trước khi merge (xem PHẢN BIỆN #10).

## MISSION

Sinh câu thoại cho nhân vật (passenger/driver) **đúng voice profile đã khai** (vùng miền, xưng hô,
tuổi, từ cấm) — không tự bịa quy tắc ngôn ngữ mới, không nói thay generator điều mà các validator
sẵn có chưa từng kiểm. ROI cao nhất theo `master_roadmap.md` §4 vì mọi domain khác (G4 event, G5
supernatural, G6 planner) đều tạo INPUT cho lời thoại, nhưng chưa ai sinh RA lời thoại. Thiết kế
theo nguyên lý CORE+OVERLAY (`master_roadmap.md` §2): generator là lớp orchestration CORE, dialect
VN là OVERLAY — để sau này đổi thể loại/ngôn ngữ chỉ cần đổi bible, không viết lại engine.

## ⚠️ PHẢN BIỆN QUAN TRỌNG (đọc trước khi build — bỏ qua sẽ vi phạm R211 hoặc sinh phantom coverage)

1. **SSOT quê↔giọng đã lệch nhau thật, không phải rủi ro lý thuyết.** `tools/dialog_voice_validator.py`
   giữ dict `HOMETOWN_REGION`/`REGIONS` tự viết tay, **5 vùng** (`bac/trung/nam/tay/do_thi`). Trong
   khi đó `tools/migrate_roster_v2.py::HOME` chỉ có **3 vùng** (`bac/trung/nam`) và **đây mới là
   bảng** `tools/roster_validator.py` đã import làm single-source cho check C2 quê↔giọng (R210).
   Bằng chứng cụ thể: "Hải Dương" có trong `HOME['bac']` nhưng **thiếu** trong `HOMETOWN_REGION` —
   hậu quả thật là `validate_profile()` chỉ raise `HOMETOWN_REGION_MISMATCH` khi quê nằm trong
   `HOMETOWN_REGION`, nên quê thiếu trong bảng = **false negative câm lặng**. G3 không được dựa vào
   1 trong 2 bảng này mà chưa reconcile (D1).
2. **`detect_pronoun_issues_in_quote()` không phải API per-line tổng quát.** Nó giả định input là
   1 quote đã viết xong trong ngữ cảnh đoạn văn REVEAL, dò tên nhân vật qua 1 set `VN_NAMES` hard-code
   ~70 tên liệt kê tay trong file. Nếu passenger do G3 sinh có tên ngoài whitelist này, nhánh dò-theo-
   tên im lặng không bắt được gì (phantom coverage). Generator phải gọi hàm này qua **adapter mỏng**
   dựng lại đúng input dạng nó cần — không coi nó là "đã handle mọi tên", không copy list tên sang chỗ khác.
3. **`audit_driver_dialogue_context.py` (R174) chỉ khoá đúng 2 câu literal** ("Con đã nhớ ra chưa?" /
   "Chưa tới lúc.") của 1 nhân vật driver cố định, match theo substring, **không nhận diện paraphrase**.
   Đây là lỗ hổng có sẵn của enforcer — generator không được vô tình khai thác nó bằng cách tạo biến
   thể đồng nghĩa; audit của builder không được lấy "tool exit 0" làm bằng chứng nếu diff cho thấy câu
   đã đổi từ. Sinh thoại driver khác 2 câu này thì tool này cho **0 coverage thật** dù chạy không lỗi.
4. **`qa_dialogue_identity.py` (R191) chạy trên WAV đã render** (librosa/MFCC, post-render) — không
   thể và không nên nằm trong vòng lặp validate-trước-khi-ghi của generator TEXT. G3 chỉ tham chiếu
   tool này như bước downstream đã tồn tại, không import `librosa` vào generator "cho đủ tool", và
   phải bàn giao rõ cho G8 QA Runtime (không tự nhận đã "enforce" R191).
5. **Domain `dialogue` chưa có block độc lập trong `governance/architecture_registry.yaml`**
   (không phải "0 hit" như một bản nháp trước từng viết — sửa theo skeptic-1: `grep -i dialogue
   governance/architecture_registry.yaml` cho ≥2 vùng khớp thật: `dependency_map` đã có cạnh
   "Character -> Dialogue" / "Dialogue -> TTS(svhmp_v13_render)", và
   `tests/test_dialogue_appropriateness_1000_r208.py` — R208, confusion-test 1000 case age-slang
   gọi `dialog_voice_validator.validate()` + `MODERN_SLANG`, đã wired thật trong `ci_gate.py` — đã
   đăng ký dưới domain `character` dòng ~265). Ý đúng duy nhất còn giữ được: **chưa có 1 block
   `dialogue:` cấp domain riêng** làm chủ `tools/dialog_voice_validator.py` +
   `audit_dialogue_hierarchy.py` + `audit_driver_dialogue_context.py` + `qa_dialogue_identity.py` —
   4 tool này hiện vẫn treo dưới domain `character` (locked, `CMD_CHARACTER`). Nếu G3 tạo file mới
   mà không đăng ký domain, `tools/architecture_registry_check.py --strict` (đang giữ 0 MISSING/0
   DUP/0 UNMAPPED) sẽ bắt UNMAPPED ngay — gate đang chạy thật, không lý thuyết. D6 khi thêm block
   `dialogue:` PHẢI cross-reference rõ `test_dialogue_appropriateness_1000_r208.py` (ghi chú "đo
   age-slang qua validator, KHÔNG trùng phạm vi D5 generator-confusion-test") để tránh 2
   confusion-test độc lập đo cùng lát cắt age-slang mà không biết nhau.
6. **`tools/dialogue_manager.py` đang bị chặn build-ahead (R211, không có mức "tạm chấp nhận").**
   `blueprint_domains.yaml` khai `manager.status: planned` với `blocking_dependency`: "quyết định
   tách/giữ chung với `character_manager.py`" — CHƯA có quyết định tường minh của Mr.Long. G3 tuyệt
   đối không tạo file này hay sửa `character_manager.py` theo hướng ngầm định trước khi có quyết định
   (D2 xử lý bằng RFC gate).
7. **Roster THẬT hiện thiếu dữ liệu Tier-1** dù schema đã khai bắt buộc. Đọc trực tiếp entry mẫu
   trong `runtime/passenger_roster_100.yaml`: chỉ có `region_dialect, hometown, pronoun_system,
   particles, register` — **KHÔNG có** `catchphrase, forbidden_words, dialogue_sample,
   speaking_speed` dù `bible/37 tier_1_mandatory.voice` khai cả 4 field này là bắt buộc. Đây là **nợ
   dữ liệu của G2**, không phải lỗi schema. G3 không được tự điền dữ liệu này để generator chạy cho
   "đẹp" rồi nhận vơ là "đã xong voice data" — generator phải SKIP field thiếu và log rõ, không bịa.
8. **50 tập `episode.md` đã render KHÔNG dùng được làm "golden set đa dạng vùng miền".** Đã grep
   `tools/auto_gen_ep.py` toàn văn: 0 hit `dialog`/`voice`/`region_dialect`. Toàn bộ thoại 50 tập là
   template hardcode theo setting/object, sinh TRƯỚC khi `voice.region_dialect` được thêm vào roster
   (migrate_roster_v2 mới chạy 2/7). Mine thẳng 50 tập này để làm "golden dialect đa vùng" sẽ cho ra
   dữ liệu giả-đa-dạng (thực chất đơn giọng) — D5 xử lý bằng cách tách bạch 2 nguồn, không trộn nhãn.
9. **Ranh giới domain dễ bị lấn.** `non_responsibility` của domain dialogue khai rõ "KHÔNG quyết
   ratio thoại/narration" — đó là việc G6 Story Planner (decision_engine). Generator chỉ NHẬN ratio
   làm input, không tự tính. `forbidden_dependencies: [production, publisher]` — không import 2
   domain đó (grep-able).
10. **Cross-domain**: G2 (character audit vá gap) và G3 cùng có thể sửa `bible/37_character_schema.yaml`
    trong cùng cửa sổ thời gian — claim pack (luật 11) chỉ chặn trùng-pack, không chặn 2 pack khác
    nhau cùng sửa 1 file. Báo Boss trọng tài trước khi merge nếu trùng.
11. **Rủi ro nhân đôi ẩn (R211 trá hình) — rủi ro cốt lõi của toàn bộ pack này.** Áp lực tiến độ dễ
    khiến người build viết thẳng logic dialect/pronoun/age-slang MỚI bên trong `dialogue_generator.py`
    vì gọi lại API cũ "lằng nhằng" hơn viết tay. Review PHẢI bác ngay nếu thấy regex/bảng-từ mới trùng
    phạm vi 5 tool đã có — không cần đợi mutation audit mới bắt (R211 tối cao).
12. **2 cạnh phụ thuộc BP3 đang bị dùng ngầm không khai báo (skeptic-3).** Bản này tự giới hạn
    "Phụ thuộc thật" của G3 ở đúng `dep__dialogue__character` + `dep__dialogue__culture` (khớp dòng
    28-37 `bp3/dependency_detail.yaml`), nhưng chính hạ tầng đã có (`audit_driver_dialogue_context.py`
    đọc `bible/02_lore_db.yaml` — SoT domain `world`, `world.reader` không liệt `dialogue`) và
    deliverable mới D5-Nguồn-B (đọc `bible/31_golden_samples.yaml` — SoT domain `audio`,
    `audio.reader` không liệt `dialogue`) đang phụ thuộc 2 domain này mà BP3 không có `dep_id` nào
    ghi nhận. Đây không phải lỗi do G3 tạo ra (2 tool đã tồn tại từ trước), nhưng G3 KHÔNG được im
    lặng kế thừa gap governance này khi build thêm D3/D5 dựa trên chính 2 nguồn đó — xử lý bằng D1B.

## NỀN ĐÃ CÓ (đọc trực tiếp, không suy đoán — CẤM nhân đôi R211)

| Đã có | Ở đâu | Trạng thái verify |
|---|---|---|
| Validator dialect/xưng hô/age-slang | `tools/dialog_voice_validator.py` (`validate_profile`, `validate_line`) | ✅ chạy được, `MANDATORY_VOICE`/`EXCLUSIVE` marker vùng, `AGE_INAPPROPRIATE_SLANG` — nhưng bảng `HOMETOWN_REGION` lệch `migrate_roster_v2.HOME` (PHẢN BIỆN #1) |
| Pronoun-ambiguity hierarchy (R48) | `tools/audit_dialogue_hierarchy.py` + `tools/auto_fix_dialogue_hierarchy.py` | ✅ quét 50 tập, ghi `runtime/audit_dialogue_hierarchy_report.json`; auto-fix có `detect_relationship()` suy quan hệ từ REVEAL |
| Driver 2-câu lock (R174) | `tools/audit_driver_dialogue_context.py` | ✅ scope hẹp đúng 2 câu literal (`bible/02_lore_db.yaml` dòng 18-20), `--episode/--file/--all` |
| Speaker identity audio (R191) | `tools/qa_dialogue_identity.py` | ✅ MFCC-embedding + cosine threshold 0.85, chạy sau render, độc lập text |
| Test confusion mẫu (validator, không phải generator) | `tests/test_character_system_1000_r206.py` (R206) | ✅ 1000/1000 (500 đúng/500 sai), 0 FN/FP — **input 100% synthetic tay gõ**, không mine từ dữ liệu thật |
| Test confusion age-slang (validator, đã wired ci_gate) | `tests/test_dialogue_appropriateness_1000_r208.py` (R208) — gọi `dialog_voice_validator.validate()` + `MODERN_SLANG` | ✅ 1000/1000 (500/500), 0 FN/FP; **đã wired trong `ci_gate.py` CHECKS** (`R208_age`) và đăng ký trong `architecture_registry.yaml` dưới domain `character` — phạm vi hẹp hơn R206 (chỉ age-slang); D5/D6/D7 phải cross-reference, không dựng test/gate mới trùng lát cắt này mà không biết (sửa theo skeptic-1) |
| Voice profile field nguồn (schema) | `bible/37_character_schema.yaml` v2.2 `tier_1_mandatory.voice` | ✅ LOCKED: `region_dialect, pronoun_style, speaking_speed, catchphrase, forbidden_words, dialogue_sample` |
| Voice profile field DỮ LIỆU thật | `runtime/passenger_roster_100.yaml` (136KB, `gen_100_passenger.py`, migration_v2 2/7) | 🔶 chỉ có `region_dialect, hometown, pronoun_system, particles, register` — thiếu 4 field tier_1 (PHẢN BIỆN #7) |
| Single-source quê↔vùng dùng cho roster | `tools/migrate_roster_v2.py` (`HOME`, 3 vùng) ← import bởi `roster_validator.py` | ✅ đang là nguồn C2 THẬT cho domain `character` (locked) |
| Bible dialect/anti-slop/giọng kể (LOCKED) | `bible/22_anti_slop_vi.yaml`, `bible/06_lexical_style.yaml`, `bible/15_voice_bible.yaml` | ✅ `status: exists`, `writer: mr_long`, `lock_type: bible` |
| Golden sample duy nhất liên quan dialogue | `bible/31_golden_samples.yaml` | 🔶 chỉ 1 dòng nhắc dialogue (bác tài), khoá EP01 tổng thể trước khi có field `region_dialect`; SoT domain `audio` — dialogue chưa có quyền đọc chính thức (PHẢN BIỆN #12) |
| 50 tập dialogue đã render | `output/ep_02..50/episode.md` | 🔶 tồn tại thật nhưng sinh bởi `tools/auto_gen_ep.py` — template hardcode, không đọc voice field (PHẢN BIỆN #8) |
| Manager (dialogue) | — | ❌ `blueprint_domains.yaml`: `status: planned`, `blocking_dependency` chưa gỡ (PHẢN BIỆN #6) |
| Generator | — | ❌ 0% — chưa file nào tên `dialogue_generator.py` |
| Gate 1 cửa | — | ❌ `ci_gate.py` hiện có **12 entry** trong `CHECKS` (`registry, blueprint, R199_tail, R203_conf, R205_char, R206_voice, R207_canon, R208_age, project_config, G2_roster, g5_supernatural, G4_world`) — KHÔNG có entry `dialogue`/`G3_dialogue` (sửa 5/7 sau audit độc lập: bản trước ghi sai "11", đúng là 12, lỗi đếm của chính kiểm duyệt) |
| Domain `dialogue` trong registry (block độc lập) | `governance/architecture_registry.yaml` | 🔶 chưa có block `dialogue:` riêng, nhưng **đã có** `dependency_map` edge Character->Dialogue/Dialogue->TTS và `test_dialogue_appropriateness_1000_r208.py` đăng ký dưới domain `character` — sửa theo skeptic-1, không phải "0 hit" |
| Dependency BP3 dialogue→world, dialogue→audio | `bp3/dependency_detail.yaml` | ❌ chưa khai (chỉ có `dep__dialogue__character`/`dep__dialogue__culture`) dù `audit_driver_dialogue_context.py` đọc `bible/02` (world) và D5-Nguồn-B sẽ đọc `bible/31` (audio) — cả 2 domain không liệt `dialogue` trong `reader` (PHẢN BIỆN #12, skeptic-3) |

## GAP THẬT (việc của G3 — đã trừ phần đã có)

1. **Generator sinh thoại** — 0% có.
2. **SSOT quê↔vùng lệch** giữa 2 validator đang sống — nợ kỹ thuật phải trả trước khi generator dựa vào 1 trong 2 bảng.
3. **Quyết định manager tách/giữ-chung** chưa chốt — chặn build-ahead.
4. **Domain `dialogue` chưa có block độc lập trong registry** (dù đã có dependency_map edge + R208 gắn dưới `character`) — generator/gate mới sẽ UNMAPPED nếu không khai block riêng.
5. **Golden set + test confusion cho hành vi GENERATOR** (khác R206/R208 vốn test thẳng validator nội bộ, không test "generator có chặn dòng sai trước khi ghi ra file không").
6. **Gate 1 cửa `tools/g3_dialogue_check.py`** chưa có, chưa wire `ci_gate`.
7. **Roster thiếu 4 field tier_1** — món nợ của G2, G3 chỉ được đọc/skip, không tự vá.
8. **2 cạnh phụ thuộc BP3 chưa khai** (`dialogue→world` qua `bible/02`, `dialogue→audio` qua
   `bible/31`) — món nợ governance có sẵn từ trước G3, nhưng G3 build D3/D5 dựa trên đúng 2 nguồn
   này nên phải đóng bằng RFC (D1B) trước khi coi là hợp lệ chính thức.

## KIẾN TRÚC (mỗi lớp audit độc lập — CORE+OVERLAY §2, để mở sang thể loại khác không viết lại engine)

| Lớp | File/tool | CORE hay OVERLAY | Audit độc lập bằng gì |
|---|---|---|---|
| 1 Schema dialect (bible) | `bible/37` voice fields (CORE) + `bible/22/06/15` (OVERLAY: anti-slop tiếng Việt, giọng kể) | mix | đọc field tồn tại trực tiếp |
| 2 Manager (dialogue context) | D2 (quyết định + code) | CORE (context "ai nói/đã nói gì/biết gì tới ep N" — tổng quát mọi thể loại) | unit test độc lập, không cần LLM |
| 3 Validator (đã có, KHÔNG đổi phạm vi) | 5 tool đã liệt ở trên | `dialog_voice_validator` = OVERLAY (3 vùng miền VN); 4 tool còn lại = CORE (pronoun/context/identity không phụ thuộc thể loại) | chạy trực tiếp trên corpus thật, exit code |
| 4 Generator (mới, mỏng) | `tools/dialogue_generator.py` | CORE (orchestration, 0 dòng dialect rule cứng) | mutation test (thiếu Tier1 → refuse; dialect leak → reject) |
| 5 Gate | `tools/g3_dialogue_check.py` (mirror `g4_world_check.py`/`g5_supernatural_check.py`) | CORE | matrix PASS/FAIL, unwire-guard |

Nguyên tắc: lớp N chỉ **import + gọi** lớp N-1, không copy logic sang lớp trên. Vi phạm = tái diễn PHẢN BIỆN #11.

## DELIVERABLES

### D0 — Baseline & Reality Check (chạy trước mọi thứ, chống claim=work lệch)
Log làm bằng chứng khởi điểm (mốc so sánh bắt buộc trong report cuối, không phải suy đoán khi báo DONE):
- Chạy và lưu: `python tools/ci_gate.py` (xác nhận đủ **12 stage** hiện có trong `CHECKS` —
  `registry, blueprint, R199_tail, R203_conf, R205_char, R206_voice, R207_canon, R208_age,
  project_config, G2_roster, g5_supernatural, G4_world`; liệt thiếu bất kỳ entry nào so với file
  thật = D0 tự sai, auditor bác theo G3-11 của `CMD_AUDIT_G3.md`), `python
  tools/dialog_voice_validator.py` (baseline demo), `python tools/audit_dialogue_hierarchy.py
  --summary` (baseline số issue trên 50 tập).
- Đo tỉ lệ MATCH/MISMATCH thật: với mỗi passenger có `assigned_ep`, trích quote gán cho họ trong
  `output/ep_{n}/episode.md` (tái dùng `extract_quotes()` có sẵn trong `audit_dialogue_hierarchy.py`,
  không viết lại regex), chạy qua `dialog_voice_validator.validate_line()` → đếm MATCH/MISMATCH.
  Dự đoán thấp (theo PHẢN BIỆN #8) nhưng PHẢI đo, không đoán.
- Xuất `reports/G3_REALITY_AUDIT.md`. 🔍 **Cách bắt lỗi:** báo cáo DONE cuối pack mà không kèm
  before/after 3 lệnh + số MATCH/MISMATCH này = vi phạm claim=work, auditor bác thẳng không cần mutation.

### D1 — Reconcile SSOT quê↔giọng (khoá TRƯỚC D3/D4, không có mức bỏ qua)
`governance/proposals/g3_dialect_region_ssot_proposal.yaml` (`meta.status:
PROPOSAL_AWAITING_MR_LONG_SIGNATURE`): trích nguyên văn 2 bảng lệch nhau + evidence "Hải Dương" thiếu
ở `HOMETOWN_REGION`. Đề xuất diff tối thiểu cho `tools/dialog_voice_validator.py`: xoá
`HOMETOWN_REGION` tự viết tay, import `HOME` từ `tools/migrate_roster_v2.py` (đúng pattern
`roster_validator.py` đã dùng) và suy ngược `{quê(lowercase): vùng}` tại chỗ. 2 vùng `tay`/`do_thi`
(chưa có trong `HOME`) giữ lại như hằng số phụ `EXTRA_REGIONS_DIALOGUE_ONLY` ngay trong file, comment
rõ "chưa có trong character roster, chỉ dùng khi generator cần dải giọng rộng hơn — KHÔNG suy luận
thêm quê mới". File này thuộc `ownership_matrix.CMD_CHARACTER` (locked) → **cần authorization RFC**
như G5 đã làm cho `entity_class`, không tự commit vào domain locked.
`tests/test_dialog_voice_single_source.py`: assert `dialog_voice_validator` sau fix resolve đúng
vùng cho MỌI quê trong `HOME` (mọi vùng) và ngược lại; assert bằng object-identity qua import (không
copy giá trị tay) để ai dán lại dict cứng sau này sẽ đỏ ngay.
🔍 **Cách bắt lỗi:** test này PHẢI bắt được đúng lỗi "Hải Dương" ĐỎ trước khi fix, XANH sau khi fix —
chứng minh test thật, không phải test rỗng (REALITY ANCHOR). D3/D4 KHÔNG được chạy thật (chỉ dry-run
cấu trúc) cho tới khi `mr_long_decision` của proposal này != `PENDING`.

### D1B — RFC bổ sung dependency BP3 (dialogue→world, dialogue→audio) (khoá TRƯỚC D3-driver-passthrough / D5-Nguồn-B — cùng cơ chế RFC như D1)
Phát hiện skeptic-3: hạ tầng đã có (`audit_driver_dialogue_context.py`) đọc `bible/02_lore_db.yaml`
(SoT domain `world`) và deliverable mới D5-Nguồn-B đọc `bible/31_golden_samples.yaml` (SoT domain
`audio`) — cả hai domain đều KHÔNG liệt `dialogue` trong `reader` whitelist
(`blueprint_domains.yaml` dòng 108 `world.reader`, dòng 685 `audio.reader`), và
`bp3/dependency_detail.yaml` không có `dep__dialogue__world`/`dep__dialogue__audio`.
`governance/proposals/g3_bp3_dependency_gap_proposal.yaml` (`meta.status:
PROPOSAL_AWAITING_MR_LONG_SIGNATURE`): trích nguyên văn 2 gap (dòng `world.reader`, `audio.reader`,
danh sách `dep_id` hiện có `from: dialogue`), đề xuất bổ sung 2 `dep_id` mới (`data_flow: read`,
đúng phạm vi hẹp hiện tại — đọc 2 câu LOCK cố định + 1 dòng golden text cố định, KHÔNG đọc rộng hơn)
và thêm `dialogue` vào `world.reader`/`audio.reader`. Cho tới khi `mr_long_decision` != `PENDING`:
D3 bước 5 (pass-through câu LOCK) và D5 Nguồn B chỉ chạy **dry-run cấu trúc** (đọc để viết
test/skeleton, KHÔNG coi là nguồn chính thức để claim DONE) — y hệt ràng buộc D1 áp cho D3/D4.
🔍 **Cách bắt lỗi:** nếu D8 report tổng hợp trích số liệu từ Nguồn B hoặc từ D3-driver-passthrough
mà `g3_bp3_dependency_gap_proposal.yaml.mr_long_decision == PENDING` → auditor bác, coi là dùng dữ
liệu domain `world`/`audio` chưa được cấp phép (governance gap chưa đóng).

### D2 — Quyết định Manager (khoá build-ahead R211, không có mức "tạm chấp nhận")
`governance/proposals/g3_manager_decision_proposal.yaml` (cùng convention): liệt 2 phương án —
- **A (tách)**: `tools/dialogue_manager.py` mới, mỏng (~100-150 dòng), API
  `get_dialogue_context(character_id, ep_n) -> {voice_profile, known_facts_upto_ep, recent_lines}`,
  đọc `voice_profile` qua `character_manager.CharacterRegistry` (không đọc YAML lần 2).
- **B (giữ chung)**: thêm method cùng chữ ký thẳng vào `tools/character_manager.py`, không tạo file mới.
`mr_long_decision: PENDING` → khi ký ghi rõ A/B + lý do. **0 dòng code của nhánh nào được viết trước
khi field này != PENDING.** 🔍 **Cách bắt lỗi:** mutation M7 bắn đúng chỗ này — bất kỳ file
`tools/dialogue_manager.py` nào xuất hiện trong diff mà không kèm quyết định = FAIL toàn bộ pack ngay,
không xét tiếp checkpoint khác.

### D3 — Generator (thin orchestration layer — DUY NHẤT phần code sinh mới thật sự)
`tools/dialogue_generator.py`. Input: `character_id` (tra roster qua manager D2) + `scene_context`
(speaker/listener, beat cảm xúc, ratio thoại/narration — **nhận từ ngoài, không tự tính**, PHẢN BIỆN
#9) + cờ driver-fixed-line. Output: 1 câu thoại ứng viên. Luồng bắt buộc theo thứ tự, grep-able:
1. **Tier1-completeness gate**: thiếu bất kỳ field `tier_1_mandatory.voice` nào → `raise
   Tier1IncompleteError`, không sinh câu rỗng/placeholder (R210).
2. Field roster THIẾU dữ liệu thật dù schema có (catchphrase/forbidden_words/dialogue_sample/
   speaking_speed, PHẢN BIỆN #7) → generator **SKIP dùng field đó**, log vào
   `reports/G3_MISSING_VOICE_FIELDS.md`, không bịa placeholder, không tự điền ngược vào roster
   (việc của G2).
3. Gọi `dialog_voice_validator.validate_line()` + `validate_profile()` (import + call thật) ngay tại
   điểm sinh — FAIL thì loại bỏ/thử lại, không emit câu vi phạm.
4. Gọi `audit_dialogue_hierarchy.detect_pronoun_issues_in_quote()` qua adapter dựng lại context tối
   thiểu nó cần (PHẢN BIỆN #2) — chặn nếu có issue `severity: HIGH`.
5. Nếu `kind == 'recurring'` (Bác tài/Nam): generator **refuse cứng**, không sinh — 2 nhân vật này
   dùng `bible/02` lock + `audit_driver_dialogue_context.py` riêng (PHẢN BIỆN #3). Nếu context khớp
   đúng trigger 3-câu-trước của 1 trong 2 câu LOCK Q1/Q2: pass-through **nguyên văn**, cấm paraphrase
   — **subject to D1B**: cho tới khi `g3_bp3_dependency_gap_proposal.yaml.mr_long_decision !=
   PENDING`, bước này chỉ chạy dry-run, không tính vào DoD "generator chạy thật".
6. Ghi output đúng convention `output/ep_*/episode.md` hiện có (để 4 tool audit cũ còn quét được).
7. Cấm import bất kỳ module thuộc domain `production`/`publisher` (grep-able, PHẢN BIỆN #9).
**Cấm tuyệt đối**: viết bảng dialect/pronoun/age-slang mới bên trong file này (PHẢN BIỆN #11).

### D4 — Wiring evidence + mở rộng validator (0 file mới trùng phạm vi 5 tool cũ)
Không tạo validator mới. Bằng chứng bắt buộc: `grep -n "dialog_voice_validator\|audit_dialogue_hierarchy"
tools/dialogue_generator.py` phải thấy **import + call thật** (không phải comment). Nếu cần check
theo batch, thêm hàm `validate_generated_batch(passenger, lines)` **vào trong**
`tools/dialog_voice_validator.py` (không phải file mới) chạy toàn bộ output D3 qua `validate_line()`
hiện có. 🔍 **Cách bắt lỗi:** review PR bắt buộc list "file đã SỬA" — nếu diff có file mới tên chứa
`dialect_validator`/`dialogue_validator` khác `dialog_voice_validator.py`, hoặc viết lại hàm trùng
chức năng `detect_pronoun_issues_in_quote`/`audit_text` → auditor bác ngay, không cần chạy mutation.

### D5 — Golden set + test confusion cho hành vi generator (2 nguồn tách bạch, không trộn nhãn)
`runtime/dialogue_golden_set.yaml` (status: draft):
- **Nguồn A — "synthetic-verified" (dialect/xưng hô/age-slang)**: import nguyên 500 câu `VALID_LINE`
  từ `tests/test_character_system_1000_r206.py` (đã 0 FN/FP) — copy nguyên văn, gắn `source:
  synthetic_r206`, không sửa nội dung. Dùng làm baseline cho lỗi loại dialect leak/age slang.
- **Nguồn B — "real-mined" (pronoun-ambiguity/driver-context)**: lấy trực tiếp từ dữ liệu THẬT đã có
  — câu "đúng" từ `bible/31_golden_samples.yaml` (`golden_text_ep01`), câu "sai" từ
  `runtime/audit_dialogue_hierarchy_report.json` (`sample_issues`, đã bị R48 chấm HIGH thật, evidence
  `ep:line` có sẵn) — không tự viết câu mẫu bịa. **Subject to D1B**: phần trích từ `bible/31` (SoT
  domain `audio`) chỉ tính là số liệu chính thức sau khi `g3_bp3_dependency_gap_proposal.yaml`
  được ký; trước đó ghi rõ trong report là "dry-run, chờ RFC".
- Do PHẢN BIỆN #8 (50 tập đơn giọng), Nguồn B **không dùng để đo dialect đa vùng**, chỉ dùng cho
  pronoun/driver-context. Nếu 1 nhánh của Nguồn B ra 0 case, ghi rõ trong report, không độn giả cho đủ số.
`tests/test_g3_dialogue_confusion.py` (mirror cấu trúc R206, in bảng confusion): chạy generator D3 +
3 validator trên ≥30 passenger thật lấy từ roster (phủ ≥3 vùng giọng có trong roster) × case sạch/case
cố ý phá (mutation: xoá field Tier1, ép `region_dialect` lệch `hometown`, chèn `forbidden_words`) —
đối chiếu Nguồn A+B làm baseline. Tiêu chuẩn PASS: 0 FN + 0 FP, không có "gần đúng".
🔍 **Cách bắt lỗi:** nếu confusion matrix ra 0 FN/0 FP ngay lần chạy đầu → không được tin ngay, phải
bắn thêm ≥1 case pronoun-ambiguity thật (không chỉ dialect/age) — nếu 0 case dạng này bắt được gì,
nghi ngờ adapter D3 bước 4 chưa nối đúng.

### D6 — Đăng ký domain `dialogue` vào Architecture Registry
Thêm block `dialogue:` vào `governance/architecture_registry.yaml` (tier 2 cho generator mới, tier 3
cho validator cũ): `tools/dialogue_generator.py` (manager của domain này) + 4 validator (cross-reference
với domain `character` đang sở hữu `dialog_voice_validator.py`, **không chuyển ownership** nếu chưa
Mr.Long duyệt) + test D5. `source_of_truth`: `bible/37#tier_1_mandatory.voice` (đọc, không sở hữu).
**Bắt buộc** ghi rõ dòng cross-reference tới `tests/test_dialogue_appropriateness_1000_r208.py`
(đã đăng ký dưới domain `character`) giải thích ranh giới: R208 = test hành vi validator (age-slang
only), D5 = test hành vi generator (đa lát cắt) — tránh 2 confusion-test độc lập đo trùng age-slang
mà không biết nhau (skeptic-1).
🔍 **Cách bắt lỗi:** `python tools/architecture_registry_check.py --strict` phải PASS 0 MISSING/0
DUP/0 UNMAPPED sau khi thêm — chạy thật, không suy đoán. Thiếu dòng cross-reference R208 = FAIL
checkpoint này dù `--strict` xanh (kiểm bằng đọc registry, không chỉ chạy máy).

### D7 — Gate 1 cửa + wire + unwire-guard 2 lớp
`tools/g3_dialogue_check.py` (mirror pattern `g4_world_check.py`/`g5_supernatural_check.py`): gọi D0
regression + D3 smoke trên batch mẫu + 3 validator hiện có + D5 confusion, in ma trận PASS/FAIL,
không short-circuit. Ghi `runtime/reports/dialogue_system_report.md` (mirror
`character_system_report.md`). Wire `ci_gate.py` `CHECKS` thêm `('G3_dialogue',
'tools/g3_dialogue_check.py')` (đặt sau `R208_age`, không xoá/đổi thứ tự 12 entry hiện có). **R191
(`qa_dialogue_identity.py`) KHÔNG wire vào ci_gate** (cần WAV đã render, ci_gate chạy trước render) —
ghi rõ trong `reports/G3_HANDOFF_G8.md` rằng đây là việc audio-runtime của G8, G3 chỉ xác nhận tool
tồn tại/chạy được.
🔍 **Cách bắt lỗi:** `tests/test_g3_dialogue.py::test_g3_dialogue_stage_wired_in_ci_gate` viết NGAY
commit đầu tiên, 2 lớp: (a) grep trực tiếp `tools/ci_gate.py` xác nhận dòng `'G3_dialogue'` có mặt
trong `CHECKS` (bắt trường hợp ai xoá dòng thật sau này); (b) monkeypatch xoá stage tạm trong bộ nhớ
rồi assert hành vi gate đổi (bắt trường hợp guard (a) bị vô hiệu bằng cách sửa cả 2 nơi cùng lúc).

### D8 — Sample YAML + Report tổng hợp (DoD "sample_yaml")
`runtime/dialogue_sample_output.yaml`: 10-15 câu do generator sinh thật cho passenger có sẵn trong
roster (đa dạng vùng miền theo `balance_targets.region_dialect_spread` của `bible/37`), kèm verdict
từng validator — để Mr.Long duyệt chất lượng trước khi chạy generator diện rộng.
`reports/G3_DIALOGUE_REPORT.md`: tổng hợp số liệu thật D0 (before/after, đủ 12 stage ci_gate) +
quyết định D1/D1B/D2 (ghi rõ `mr_long_decision` từng proposal, không phải PENDING nếu tính vào số
liệu chính thức) + đếm Nguồn A/B của D5 + kết quả confusion D5 — trích số liệu từ file/report thật,
không phải báo cáo tường thuật.

## REALITY ANCHOR (luật 9)

- `tests/test_dialog_voice_single_source.py` (D1) phải bắt được đúng lỗi "Hải Dương" ĐỎ trước fix,
  XANH sau fix.
- `dialogue_generator.py` (D3) phải chạy sinh thật cho ≥10 passenger có voice profile khác vùng
  trong roster THẬT, không chỉ dữ liệu giả lập tay; ≥1 case phải bị 1 trong 3 validator chặn thật
  (0 case nào bị bắt ở lần chạy đầu = nghi validator không thật sự chạy trên output generator).
- D5 confusion test phải có ≥1 case pronoun-ambiguity thật (không chỉ dialect/age).
- D0 baseline: 0 MISMATCH tìm được ở bước đo MATCH/MISMATCH phải kèm giải trình (nghi ngờ đo sai),
  đúng tinh thần "0 lỗi thật = nghi tool yếu, phải bắn thêm case trước khi tin".
- D1B: `g3_bp3_dependency_gap_proposal.yaml.mr_long_decision` phải != `PENDING` trước khi D8 report
  tính D5-Nguồn-B hoặc D3-driver-passthrough là số liệu chính thức — nếu vẫn PENDING mà report đã
  tính, đó là dấu hiệu claim=work lệch (dùng dữ liệu domain chưa cấp phép).

## MUTATION AUDIT SẼ BẮN (khai trước — kiểm duyệt sẽ bắn thêm không báo)

M1 generator sinh câu dùng tiểu từ/marker độc quyền vùng khác → phải bị chặn, không ghi ra file ·
M2 generator sinh 2 "em" mơ hồ cùng câu mà không tự bắt (phải nhờ validator ngoài mới thấy) → coi là
KHÔNG tự-validate, vi phạm D3 · M3 generator sinh/paraphrase câu Q1/Q2 driver không đúng nguyên văn
hoặc thiếu trigger 3-câu-trước → chặn (R174), verify bằng DIFF thật không chỉ exit-code · M4 gỡ dòng
`'G3_dialogue'` khỏi `CHECKS` trong `ci_gate.py` → unwire-guard 2 lớp phải đỏ · M5 câu sinh dùng quê
không có trong `HOME`/`EXTRA_REGIONS_DIALOGUE_ONLY` sau D1 → FAIL, coi là dữ liệu bịa (R195) · M6 tool
mới trùng chức năng 1 trong 5 tool cũ (viết lại bảng dialect/pronoun) → FAIL ngay từ review, không cần
đợi mutation (R211 tối cao) · M7 file `tools/dialogue_manager.py` xuất hiện trong diff hoặc
`character_manager.py` bị sửa theo hướng manager TRƯỚC KHI `mr_long_decision` (D2) != `PENDING` →
FAIL toàn bộ pack ngay, không xét tiếp checkpoint khác · M8 generator import module
`production`/`publisher` → FAIL ngay, không cần xét tiếp · M9 generator tự tính tỉ lệ thoại/narration
thay vì nhận input → FAIL review (cross-G3/G6) · M10 entry Nguồn B trong golden set không có
`ep:line` evidence, hoặc trộn lẫn Nguồn A/B không gắn `source` → FAIL khi merge · M11 generator bịa
giá trị cho field roster đang thiếu (in placeholder thay vì skip) → FAIL D3 self-test · M12 sửa
`bible/37/22/06/15` không kèm dòng "Mr.Long ký `<ngày>`" trong commit note → auditor bác thẳng ·
M13 D3-driver-passthrough hoặc D5-Nguồn-B được tính vào DoD/report chính thức trong khi
`g3_bp3_dependency_gap_proposal.yaml.mr_long_decision == PENDING` → FAIL, coi là dùng dữ liệu domain
`world`/`audio` chưa khai báo BP3 (skeptic-3) · M14 D6/D7 dựng test/gate mới đo age-slang mà không
cross-reference `tests/test_dialogue_appropriateness_1000_r208.py` đã có → FAIL review (skeptic-1,
đối chiếu "đã có" trước khi tính "gap"/tạo mới, R211).

## DoD

D0 baseline log lưu (before/after, đủ 12 stage ci_gate thật) + số MATCH/MISMATCH thật ✅ · D1 SSOT
reconcile: proposal ký + test regression bắt lỗi Hải Dương trước/sau fix ✅ · D1B RFC bổ sung
dependency BP3 (dialogue→world, dialogue→audio) ký trước khi D3-driver-passthrough/D5-Nguồn-B được
tính là số liệu chính thức ✅ · D2 quyết định manager A/B ghi rõ, 0 dòng code viết trước quyết định
✅ · D3 generator chạy thật ≥10 passenger đa vùng, refuse đúng Tier1-thiếu/recurring/dialect-leak,
0 field bịa cho field roster thiếu ✅ · D4 grep xác nhận generator gọi thật 3 validator, 0 file mới
trùng phạm vi 5 tool cũ ✅ · D5 golden set 2 nguồn tách bạch (không độn giả) + confusion test 0 FN/0
FP trên tập đã khai, có ≥1 case pronoun thật ✅ · D6 domain `dialogue` đăng ký registry (block độc
lập, cross-reference rõ R208 tránh đo trùng age-slang), `architecture_registry_check.py --strict`
0/0/0 ✅ · D7 gate wired + unwire-guard 2 lớp đỏ khi gỡ ✅ · D8 sample YAML Mr.Long duyệt + report
tổng hợp bằng số liệu thật ✅ · KHÔNG tạo `tools/dialogue_manager.py` trước quyết định D2 · KHÔNG sửa
bible LOCKED thiếu "Mr.Long ký" · KHÔNG tự dựng domain `culture` mới · KHÔNG đụng render/pipeline
LOCKED · KHÔNG đụng 2 câu LOCK bác tài · KHÔNG file mới nào trùng phạm vi 5 tool đã có (review R211
xác nhận) · KHÔNG tính D5-Nguồn-B/D3-driver-passthrough là số liệu chính thức khi D1B còn PENDING.

## RÀNG BUỘC

Claim pack trước khi build (`python tools/build_claim.py claim g3_dialogue <phiên>`, luật 11 MASTER) ·
sửa file `ownership_matrix.CMD_CHARACTER` (D1) cần authorization kiểu RFC như G5 đã làm, không tự
commit · gap dependency BP3 (dialogue→world qua `bible/02`, dialogue→audio qua `bible/31`) phải qua
D1B trước khi coi là chính thức, không im lặng kế thừa · số/quê/rule/field bịa = BÁC (R195) · nhân
đôi tool/manager/nguồn dữ liệu sẵn có = BÁC (R211, đặc biệt nghiêm — core lesson của pack này) · sửa
bible LOCKED không authorization = BÁC · import `production`/`publisher` = BÁC ngay · commit UTF-8
no-BOM · worktree riêng (R200) · mọi claim "DONE" phải kèm before/after log D0 (chống claim=work
lệch) · nếu G2 đang có claim mở trên `bible/37` cùng lúc → báo Boss trọng tài trước khi merge.

## THAM CHIẾU

`governance/master_roadmap.md` §2 (CORE+OVERLAY), §4/§5 · `governance/pack2/08_artifact_contract.md`
(dòng "G3 dialogue") · `governance/blueprint/blueprint_domains.yaml` dòng 428-450 (domain `dialogue`),
dòng 108 (`world.reader`), dòng 685 (`audio.reader`) · `governance/blueprint/bp3/dependency_detail.yaml`
(`dep__dialogue__character`, `dep__dialogue__culture`, `dep__generator__dialogue` — và gap
`dep__dialogue__world`/`dep__dialogue__audio` chưa khai, PHẢN BIỆN #12) ·
`governance/blueprint/bp7/cultural_spec.yaml` · `prompts/CMD_AUDIT_G3.md` (bảng rủi ro G3-1..G3-13 —
đã tích hợp phát hiện skeptic) · `prompts/TASK_G4_WORLD.md`, `prompts/TASK_G5_SUPERNATURAL.md` (mẫu
cấu trúc/văn phong) · `bible/37_character_schema.yaml` · `bible/02_lore_db.yaml` (dòng 18-20, 2 câu
LOCK, SoT domain `world`) · `bible/31_golden_samples.yaml` (SoT domain `audio`) ·
`output/ep_01/episode_golden_text.md` · `runtime/passenger_roster_100.yaml` ·
`tools/dialog_voice_validator.py`, `tools/audit_dialogue_hierarchy.py`,
`tools/auto_fix_dialogue_hierarchy.py`, `tools/audit_driver_dialogue_context.py`,
`tools/qa_dialogue_identity.py`, `tools/roster_validator.py`, `tools/migrate_roster_v2.py`,
`tools/character_manager.py`, `tools/gen_100_passenger.py`, `tools/auto_gen_ep.py`,
`tools/g4_world_check.py`/`tools/g5_supernatural_check.py` (mirror pattern), `tools/ci_gate.py`
(12 entry CHECKS thật), `tools/architecture_registry_check.py`,
`governance/architecture_registry.yaml` (`dependency_map` Character->Dialogue/Dialogue->TTS,
domain `character` dòng ~265 cho R208) · `tests/test_character_system_1000_r206.py` (R206) ·
`tests/test_dialogue_appropriateness_1000_r208.py` (R208, wired trong ci_gate) ·
`tests/test_g4_world.py`/tương đương G5 (mirror unwire-guard + reality-anchor pattern).

STATUS cuối: READY_FOR_AUDIT / FAIL_NEEDS_FIX.

---

**Ghi chú tổng hợp (nguồn từng phần và lý do loại bỏ):**

- **Khung sườn + kiến trúc 5 lớp CORE/OVERLAY + cơ chế RFC-gate cho D1/D2** lấy từ bản **architecture-clean** — đây là bản có thiết kế phòng-thủ chặt nhất cho 2 rủi ro nghiêm trọng nhất (SSOT lệch, manager build-ahead) bằng cách bắt buộc có quyết định ký trước khi cho phép code chạy thật, thay vì để builder tự quyết ngầm.
- **"🔍 Cách bắt lỗi" gắn theo từng deliverable + thiết kế unwire-guard 2 lớp (grep tĩnh + monkeypatch hành vi)** lấy từ bản **risk-hardened** — đây là cách làm DoD đo được bằng máy rõ nhất trong 4 bản, trực tiếp học đúng bài học "named ≠ enforced" của dự án.
- **Bằng chứng cụ thể "Hải Dương" thiếu trong `HOMETOWN_REGION`** và ý tưởng hằng số phụ `EXTRA_REGIONS_DIALOGUE_ONLY` cho vùng `tay`/`do_thi` lấy từ bản **reuse-first** — đây là chi tiết falsifiable nhất, biến rủi ro SSOT từ "lý thuyết" thành "test case cụ thể có thể đỏ/xanh".
- **D0 Reality Audit đo % MATCH/MISMATCH thật giữa 50 tập đã render và voice profile** + phát hiện `auto_gen_ep.py` không đọc field dialect (khiến 50 tập là "đơn giọng giả-đa-dạng") + kỷ luật tách 2 nguồn golden set (synthetic-verified vs real-mined, không trộn nhãn) lấy từ bản **golden-data-first** — đây là phần duy nhất thực sự đo lường tính khả thi trên dữ liệu thật thay vì giả định.
- **Phát hiện domain `dialogue` chưa đăng ký trong `architecture_registry.yaml`** (D6) chỉ có ở bản reuse-first — giữ lại vì đây là một gate đang chạy thật (`--strict`) mà 3 bản kia bỏ sót hoàn toàn.
- **Phát hiện roster thật thiếu 4 field tier_1** (catchphrase/forbidden_words/dialogue_sample/speaking_speed) chỉ có ở bản risk-hardened — giữ lại vì ảnh hưởng trực tiếp đến tính khả thi của generator và ranh giới trách nhiệm G2 vs G3.
- **Loại bỏ**: tên test `test_dialogue_appropriateness_1000_r208.py` từng bị loại khỏi 1 bản nháp trước vì nghi số hiệu sai (chỉ 1/4 bản gốc nhắc) — **ĐÃ SỬA sau skeptic-1**: file này thật, đang chạy thật, đã wired trong `ci_gate.py` (`R208_age`) và đăng ký trong `architecture_registry.yaml` — không phải số bịa. Đã đưa lại vào bảng "NỀN ĐÃ CÓ", sửa mọi câu claim "ci_gate chỉ có 4 stage"/"registry 0 hit dialogue" cho khớp thực tế 11-stage/dependency_map đã có, và thêm yêu cầu cross-reference ở D6/D7 để tránh 2 confusion-test đo trùng age-slang mà không biết nhau. Cũng loại bỏ chi tiết "G2 released đúng 2026-07-05 02:04" (chỉ 1 bản nêu, mâu thuẫn "G2 ~92%"/"G2 đang audit vá gap" ở 2 bản khác) — thay bằng phát biểu an toàn hơn khớp đa số. Không lặp lại riêng rẽ 4 bảng "NỀN ĐÃ CÓ" và 4 danh sách MUTATION AUDIT của từng bản — đã gộp/khử trùng thành 1 bảng và 1 danh sách duy nhất để tránh văn bản phình to vô ích mà không thêm thông tin mới.
- **Sửa sau 3 vòng skeptic review độc lập (5/7)**: (1) **skeptic-1** (R211-dup-check) phát hiện 2 claim sai theo nghĩa đen — "ci_gate.py hiện chỉ có 4 stage" và "domain dialogue 0 hit khi grep registry" — đối chiếu file thật cho thấy `ci_gate.py` có **12 entry** `CHECKS` (bao gồm `R208_age` → `test_dialogue_appropriateness_1000_r208.py`, một confusion-test dialogue-age-slang đang chạy thật) và `architecture_registry.yaml` đã có `dependency_map` edge Character->Dialogue/Dialogue->TTS cùng R208 đăng ký dưới domain `character`. Đã sửa: đoạn mở đầu, PHẢN BIỆN #5, bảng NỀN ĐÃ CÓ (2 dòng + thêm 1 dòng R208), GAP THẬT #4, D0, D6, D7, MUTATION AUDIT (thêm M14), DoD, THAM CHIẾU. (2) **skeptic-2** (bible-immutability-check) không tìm được lỗi — cơ chế RFC/proposal cho D1/D2 đã khớp tiền lệ thật (`supernatural_typology_proposal.yaml`, `ownership_matrix.CMD_CHARACTER`) — giữ nguyên, không sửa. (3) **skeptic-3** (BP3-dependency-check) phát hiện `bp3/dependency_detail.yaml` không khai `dep__dialogue__world`/`dep__dialogue__audio` dù hạ tầng có sẵn (`audit_driver_dialogue_context.py` đọc `bible/02`, SoT `world`) và deliverable mới D5-Nguồn-B (đọc `bible/31`, SoT `audio`) đang dùng đúng 2 domain đó mà `dialogue` không có trong `reader` whitelist của cả hai — thêm deliverable **D1B** (RFC bổ sung dependency, cùng cơ chế D1/D2), PHẢN BIỆN #12, GAP THẬT #8, MUTATION M13, REALITY ANCHOR bổ sung, và ràng buộc D3 bước 5 + D5 Nguồn B chỉ tính chính thức sau khi D1B ký.
