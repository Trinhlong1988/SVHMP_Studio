# KHUÔN ENGINE DESIGN — story-agnostic generation (đề xuất #6)

- **Người lập:** CMD_BUILD (builder, worktree cách ly)
- **Bối cảnh:** `governance/AUDIT_ROOT_CAUSE_SYNTHESIS_17_07.md` mục 3 #6 — Boss chốt xây "khuôn" (engine story-agnostic) để 1 engine sinh được NHIỀU truyện chỉ bằng thay config, KHÔNG hardcode literal truyện-cụ-thể vào `tools/`.
- **Trạng thái:** ĐỀ XUẤT — chưa refactor engine, chưa build enforcer. Kèm PILOT đã chạy (seat✓ + name✓, mục "Migration path").
- **Phạm vi bản này:** trả lời 5 câu hỏi Boss giao (engine-choice / config schema / migration / enforcer phác thảo / rủi ro + câu hỏi). KHÔNG tự quyết (R_SUPREME R1/R10).

---

## 0. TÓM TẮT (nếu chỉ đọc 1 mục)

- **KHÔNG chọn `auto_gen_ep.py` làm "khuôn".** Bằng chứng chạy tay (dưới): engine template này KHÔNG phải nguồn của 50 tập thật hiện có — nó là 1 nhánh **legacy/thí nghiệm**. Regen 49 tập nên đi qua đường **LLM + `prompts/generator.md`** (đường đã sinh 50 tập thật), với `story_planner.py → episode_generator.py` làm **tầng ráp DATA packet** (deterministic, testable) feed cho bước viết prose.
- **"Khuôn" thật sự cần = tách 3 tầng:** (1) **STORY CONFIG** (data thuần: canon nhân vật/địa danh/vật/setting + prompt template refs) · (2) **ENGINE LOGIC** (story-agnostic: đọc config, ráp packet, gọi LLM, chạy gate) · (3) **ENFORCER** chống literal truyện lọt ngược vào tầng (2).
- **Pilot đã chứng minh nguyên lý ở quy mô nhỏ:** seat + tên nhân vật POV giờ = DATA đọc từ `runtime/canon_registry.yaml`, mutation-proof (đổi canon → output đổi). Đây là "bước 2" của khuôn; phần còn lại là refactor lớn CHỜ DUYỆT.

---

## 1. ENGINE-CHOICE — khảo sát 3 đường sinh (đọc code + chạy tay)

### Đường A — `tools/auto_gen_ep.py` (+ `auto_gen_ep_v3.py`): template engine legacy, full hardcode
- **Bản chất:** f-string template Python thuần. 1 hàm `build_episode()` chứa TOÀN BỘ prose 6 section, chèn biến từ roster/bible. Không gọi LLM.
- **Mức hardcode:** rất cao. Tên POV "Khải Phong" xuất hiện literal ~40 lần (v3: 32 lần), `SETTING_DESCRIPTORS`/`OBJECT_DESCRIPTORS`/`STOP_LOCATIONS` = hằng SVHMP nhúng thẳng trong code, `prompt_version` hardcode chuỗi.
- **BẰNG CHỨNG NÓ KHÔNG PHẢI NGUỒN 50 TẬP THẬT (chạy tay, worktree):** chạy `python tools/auto_gen_ep.py --ep 11` GHI ĐÈ `output/ep_11/episode.md`; `git diff` cho thấy nội dung THẬT khác HOÀN TOÀN bản template sinh ra:
  - Bản thật có khối `[INTRO 4.5s — HẮC DẠ KÝ master]` + `prompt_version: SVHMP-10.0-RC3.5`, tiêu đề "TẬP 11 — VÒNG CỔ CHỊ TẶNG EM…".
  - Bản template sinh "TẬP 11 — BĂNG CASSETTE CŨ…", `prompt_version: SVHMP-10.0-RC3.4`, không có INTRO.
  → 50 tập thật KHÔNG do engine này sinh. (Đã `git checkout` khôi phục ep_11 sau kiểm chứng.)
- **Kết luận:** đây là **legacy/prototype**, KHÔNG phải production path. Dùng nó làm "khuôn" = đóng băng 1 văn phong template cứng (mọi tập cùng 1 khung câu) — trái mục tiêu chất lượng prose. **KHÔNG chọn.** (Vẫn hữu ích làm *sân tập de-hardcode* — chính là nơi chạy PILOT vì rẻ + in-process testable.)

### Đường B — LLM + `prompts/generator.md`: prose thật (người + LLM)
- **Bản chất:** `prompts/generator.md` (v10.0-RC3.4, "STORY WRITER thuần — chỉ viết, KHÔNG self-score/QA", ~65KB) = prompt khổng lồ nhồi bible + runtime + content layer; con người/LLM chạy nó để viết prose. `episode_generator.py:5-8` xác nhận: "buoc viet van ban tu su (prose) van la CMD prompt-based (nguoi + LLM theo prompts/generator.md)".
- **Bằng chứng đây LÀ nguồn 50 tập thật:** `prompt_version` trong episode thật (RC3.5, lineage RC3.4) khớp `generator.md`, KHÔNG khớp chuỗi hardcode của đường A.
- **Đánh giá làm khuôn:** đây là đường tạo ra chất lượng prose thật → **giữ làm engine sinh prose**. NHƯNG hiện `generator.md` = prompt SVHMP-specific (nhồi tên/bible/canon SVHMP) → chưa story-agnostic. "Khuôn hoá" = biến prompt này thành **template có slot** nạp từ STORY CONFIG (xem §2), thay vì 1 file cứng.

### Đường C — `tools/story_planner.py` → `tools/episode_generator.py`: ráp DATA packet (mới, G6b/G7)
- **Bản chất:** KHÔNG viết prose. `story_planner` đọc bible/event_ledger → `episode_plan` + scene (deterministic, R195 "không bịa"). `episode_generator` ráp 14-domain thành `episode_packet` trung gian (theo `governance/blueprint/schemas/episode_schema.yaml`).
- **Phạm vi thật hiện tại:** CHỈ EP01 ráp đầy đủ packet; `story_planner` thêm EP02-11 pilot; EP12-50 = `pending` (chưa đọc/xác nhận format) — `PENDING_REASON_EP02_50`. Nên **chưa** dùng được cho regen 49 tập ngay.
- **Đánh giá làm khuôn:** đây là **tầng đúng để đặt DATA-driven** — deterministic, đã có schema + test, đã tách "đọc data" khỏi "viết prose". Nhưng nó mới phủ EP01-11 và không sinh prose. → **giữ làm tầng RÁP PACKET (input cho đường B)**, cần mở rộng EP12-50.

### KHUYẾN NGHỊ engine
**Kiến trúc 2 tầng cho regen + khuôn:**
1. **Tầng DATA (đường C mở rộng):** `story_planner`/`episode_generator` đọc STORY CONFIG → `episode_packet` deterministic. Đây là nơi enforcer + gate bám vào (testable, không cần LLM).
2. **Tầng PROSE (đường B khuôn-hoá):** `generator.md` biến thành **prompt-template có slot**, nhận `episode_packet` + canon từ config, LLM viết prose.
- **`auto_gen_ep.py` (đường A):** KHÔNG dùng cho production; giữ như harness de-hardcode/regression rẻ (pilot chạy ở đây). Cân nhắc đánh dấu `deprecated` sau khi đường C phủ đủ.

---

## 2. CONFIG SCHEMA KHUÔN — story config (DATA, không hardcode)

Mục tiêu: 1 engine + N file config = N truyện. Đề xuất cấu trúc `stories/<story_id>/config.yaml` (hoặc gộp `story_config.yaml` có `story_id`):

```yaml
story_id: svhmp            # định danh truyện; engine chọn config theo id (CLI --story)
meta:
  title: "Hắc Dạ Ký"
  language: vi
  genre: horror_melancholy

# --- CANON DATA (thay cho hardcode literal trong engine) ---
canon:
  recurring_chars:          # nguồn = runtime/canon_registry.yaml hôm nay (đã đọc được: display_name/seat)
    POV:
      id: CHAR_KHAI_PHONG
      display_name: "Khải Phong"     # PILOT: engine ĐÃ đọc field này (mục 3)
      seat: "ghế số bảy"             # PILOT R216: engine ĐÃ đọc field này
      immutable_fields: [id, display_name, seat, ...]
    DRIVER:
      id: CHAR_DRIVER
      display_name: "Bác tài"
  locations: { stop_locations_ref: "runtime/<story>/stop_locations.yaml" }
  objects:   { library_ref: "bible/<story>/12_object_library.yaml" }
  settings:  { library_ref: "bible/<story>/13_setting_library.yaml" }

# --- ENGINE BINDINGS (đường dẫn data, KHÔNG literal) ---
sources:
  roster:        "runtime/<story>/passenger_roster.yaml"
  regret_catalog:"bible/<story>/11_regret_catalog.yaml"
  event_ledger:  "runtime/<story>/event_ledger.yaml"

# --- PROSE TEMPLATE (khuôn-hoá generator.md) ---
prose:
  engine: "llm"                       # llm | template
  prompt_template_ref: "prompts/<story>/generator.md"   # prompt có slot, nạp canon ở trên
  section_order: [HOOK, SETUP, INCIDENT, REVEAL, PAYOFF, CLIFFHANGER]
```

**Nguyên tắc schema:**
- Mọi **proper-noun canon** (tên nhân vật, địa danh, tên truyện) = field trong `config.canon`, KHÔNG literal trong `tools/`.
- Engine nhận `story_id` (CLI/env) → load đúng config → mọi path/tên đọc từ config. Không truyện nào là "mặc định cứng".
- `bible/`, `runtime/`, `prompts/` được **story-namespaced** (vd `bible/svhmp/…`) để engine story-agnostic; hoặc để config trỏ path tuyệt đối cho từng story.
- Tương thích tại chỗ: `runtime/canon_registry.yaml` HÔM NAY đã đủ dùng cho pilot (đã có `display_name` + `seat`) → config có thể **trỏ vào** file này thay vì nhân đôi.

---

## 3. MIGRATION PATH — hardcode → data-driven (theo bước)

| Bước | Trạng thái | Mô tả | Bằng chứng |
|---|---|---|---|
| 1. seat = data | ✓ ĐÃ LÀM (trước phiên) | `load_khai_phong_seat()` đọc `CANON_CHAR_KHAI_PHONG.seat` | commit e0318ff |
| 2. name = data (PILOT) | ✓ PHIÊN NÀY | `load_kp_canon()` đọc `display_name`+`seat`; 2 template chính (HOOK+CLIFFHANGER) dùng `{kp_name}`; mutation-proof | xem §pilot dưới |
| 3. Quét sạch mọi literal POV/DRIVER trong đường A | CHỜ DUYỆT | thay ~31 `Khải Phong` còn lại + `Bác tài` → biến từ config (refactor lớn, KHÔNG làm trong pilot) | — |
| 4. Externalize descriptor tables | CHỜ DUYỆT | `SETTING_/OBJECT_DESCRIPTORS`, `STOP_LOCATIONS` → file config story-namespaced | — |
| 5. Story config + `--story` resolver | CHỜ DUYỆT | thêm loader chọn config theo `story_id`; engine đọc mọi path từ config | — |
| 6. Khuôn-hoá `generator.md` (đường B) | CHỜ DUYỆT | prompt → template có slot nạp canon từ config | — |
| 7. Mở rộng đường C EP12-50 | CHỜ DUYỆT | gỡ `pending`, phủ packet đủ 49 tập | phụ thuộc format episode |
| 8. Enforcer no-story-literal (§4) | CHỜ DUYỆT | ratchet guard chống literal mới lọt lại | — |

**Thứ tự khuyến nghị:** làm §4 enforcer SỚM (ngay sau bước 3) để refactor bước 3-6 có ratchet chống tái nhiễm — nếu không, gỡ literal xong lại có người thêm literal mới, y hệt lớp "đề xuất không gate" (R215 điểm 6).

---

## 4. ENFORCER "no-story-literal-in-engine" — PHÁC THẢO (CHƯA BUILD)

> **CHƯA CÓ ENFORCER — mới là ĐỀ XUẤT** (R215 điểm 6: đề xuất quy trình không kèm gate = cùng lớp rule-without-enforcer). Ghi rõ để KHÔNG đọc nhầm là đã phòng thủ. Nên mở DEBT-xxx track khi Boss duyệt.

**Ý tưởng:** ratchet checker giống `tests/test_no_text_true_without_encoding.py` (AST-scan + allowlist file+count), quét `tools/` (engine layer) tìm **proper-noun canon truyện-cụ-thể** hardcode (tên nhân vật "Khải Phong"/"Hạ Vy", địa danh canon…). FAIL nếu THÊM occurrence mới ngoài allowlist; allowlist chốt backlog legacy hiện tại (auto_gen_ep.py ~31, v3 ~32) kèm ref DEBT.

**Phác thảo `tools/no_story_literal_in_engine_check.py`:**
- Nguồn danh sách proper-noun: đọc `config.canon.recurring_chars[*].display_name` + location/object canon names từ STORY CONFIG (KHÔNG hardcode danh sách trong checker — nếu không, checker tự vi phạm nguyên tắc nó bảo vệ).
- Quét file `tools/*.py` (trừ chính checker + loader hợp lệ như `load_kp_canon`): tìm literal string chứa proper-noun canon.
- **Allowlist ratchet:** `{path: max_count}` — vd `auto_gen_ep.py: 31`, `auto_gen_ep_v3.py: 32`. Thêm literal mới → count vượt → FAIL. Gỡ literal → cập nhật allowlist xuống (ratchet 1 chiều, chỉ giảm).
- **Mutation-proof BẮT BUỘC (khi build thật):** (a) thêm 1 literal canon giả vào engine → checker FAIL; (b) gỡ → PASS; (c) đảo loader `load_kp_canon` thành literal → FAIL. Chỉ static-scan KHÔNG đủ nếu chưa có mutation-proof (R215 điểm 5).
- **KHÔNG wire ci_gate** cho tới khi backlog allowlist ổn định + mutation-proof xong (tránh chặn nhầm refactor đang dở).

**Lưu ý cạm bẫy (rút từ R215):** checker phải đọc danh-sách-tên từ config chứ không grep tên cứng; nếu grep tên cứng thì chính checker lại hardcode story-literal — tái phạm đúng thứ nó cấm.

---

## 5. RỦI RO + CÂU HỎI CẦN BOSS QUYẾT

**Rủi ro:**
1. **Refactor bước 3-6 đụng nội dung 50 tập.** Externalize + khuôn-hoá generator.md dễ làm đổi văn phong output → PHẢI regen + QA lại, không được "sửa engine rồi coi như xong" (R196 Production PASS).
2. **Story-namespacing path** (`bible/svhmp/…`) là thay đổi cấu trúc thư mục lớn → chạm architecture_registry + rất nhiều tool hardcode `runtime/passenger_roster_100.yaml` (audit đếm ~20 tool). Migration path phải kèm cập nhật registry + file_index đồng bộ, không sẽ vỡ 0/0/0.
3. **Đường C (packet) mới phủ EP01-11**; ép dùng cho 49 tập trước khi gỡ `pending` = bịa data (vi phạm R195).
4. **Hai engine song song** (đường A template vs đường B LLM) dễ gây nhầm "engine nào là thật" — chính là gốc rễ #2 của audit. Cần Boss chốt 1 đường chính + deprecate rõ đường kia.

**Câu hỏi cần Boss quyết:**
1. **Engine chính cho regen 49 tập** = đường B (LLM + generator.md) + đường C (packet) như khuyến nghị? Hay giữ đường A template cho tốc độ?
2. **Có story-namespace** thư mục (`bible/<story>/…`) không, hay giữ path phẳng + config trỏ tuyệt đối? (ảnh hưởng registry lớn.)
3. **Deprecate `auto_gen_ep.py`/`v3`** sau khi đường C phủ đủ, hay giữ làm regression harness?
4. **Thứ tự:** làm enforcer §4 TRƯỚC hay SAU khi gỡ hết literal đường A? (khuyến nghị: build enforcer + allowlist backlog trước, rồi ratchet giảm dần khi refactor.)
5. **STORY CONFIG** đặt ở đâu (`stories/<id>/config.yaml` mới, hay mở rộng `project_config.yaml` hiện có)?

---

## PHỤ LỤC — PILOT đã chạy (bằng chứng phiên này, worktree cách ly)

**Sửa (`tools/auto_gen_ep.py`):**
- Thêm `load_kp_canon()` → đọc `CANON_CHAR_KHAI_PHONG.display_name` + `.seat` từ `runtime/canon_registry.yaml`, fallback EP01 ground truth ("Khải Phong"/"ghế số bảy"). `load_khai_phong_seat()` delegate sang nó (DRY).
- `build_episode()`: thêm `kp = load_kp_canon(); kp_name = kp['name']; kp_seat = kp['seat']`.
- Thay literal "Khải Phong" → `{kp_name}` trong **2 template chính**: HOOK (đoạn mở "…ngồi {kp_seat}. Đêm thứ N…") + CLIFFHANGER (đoạn "…nhớ — đêm thứ N đã ngồi {kp_seat}…"). Các occurrence khác GIỮ literal (thuộc scope refactor bước 3, không quét sạch trong pilot). "Hà Nội" GIỮ literal (bối cảnh hợp lệ, không đụng).

**Verify (in-process `build_episode`, EP11):**
- Bình thường: `load_kp_canon() -> {'name': 'Khải Phong', 'seat': 'ghế số bảy'}`; output chứa `Khải Phong ngồi ghế số bảy` (đọc từ canon).
- **Mutation** (đổi `display_name: "Khải Phong"` → `"Lâm Tuyền"` trong canon, chạy lại, rồi khôi phục): output chứa `Lâm Tuyền ngồi` + `Lâm Tuyền nhớ — đêm` = True → CHỨNG đọc thật từ canon, không phải literal cứng.
- Engine ship end-to-end: `python tools/auto_gen_ep.py --ep 11` → PASS (2473w).

**Gate (chạy tại HEAD worktree):**
- `tools/architecture_registry_check.py` → PASS 0/0/0 (MISSING=0 DUP=0 UNMAPPED=0). File `.md` này nằm `governance/proposals/` — checker không quét (glob chỉ `governance/*.yaml`), cùng convention với `DEBT035_R216_reconcile_proposal.md` (không đăng ký file_index).
- `pytest tests/test_no_greponly_wiring_guards.py tests/test_no_text_true_without_encoding.py -q` → 6 passed.
