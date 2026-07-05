# G5 FIX — Possession State Machine Dedup (R211), branch fix/g5-4-possession-dup

**Ngày:** 2026-07-05 · **Vi phạm sửa:** CMD_AUDIT_G4_G5.md checkpoint **G5-4** — "Possession state
machine viết engine riêng thay vì mở rộng `bp4/state_machines.yaml`".

## Vi phạm THẬT là gì (đọc trước khi sửa)

`governance/blueprint/bp4/state_machines.yaml` khai entity `ghost` (owner_domain: supernatural)
với 5 state `[dormant, watching, manifest, attack, released]` — **không có** khái niệm
"possession" riêng.

`runtime/supernatural_state_machine.yaml` (file NGOÀI bp4) tự khai 1 block độc lập:

```yaml
possession_state_machine:
  entity: possession
  states: [none, entering, manifesting, peak, exorcising, released]
  transitions: [... 7 transition riêng ...]
```

File này tự nhận trong comment là "RECONCILE bp4 ghost" và "KHÔNG viết engine riêng", nhưng
**cấu trúc thật** là 1 state machine song song, đứng độc lập, dùng entity tên khác (`possession`
≠ `ghost`), states khác, transitions khác — chỉ *tự xưng* reconcile chứ không *thật* reconcile.
Nguồn thực thi thật xác nhận: `tools/supernatural_validator.py` dòng 25 (`STATE_MACHINE = ... /
runtime / supernatural_state_machine.yaml`) và `check_possession_state_machine()` đọc TRỰC TIẾP
từ file này, không đụng tới bp4 — đúng dạng R211 cấm (2 nguồn luật cho cùng 1 khái niệm).

## Việc đã làm (RECONCILE thật, không chỉ đổi tên)

### 1. `governance/blueprint/bp4/state_machines.yaml` — MỞ RỘNG entity `ghost`

States cũ: `[dormant, watching, manifest, attack, released]`
States mới: `[dormant, watching, entering, manifest, attack, exorcising, released]`

Thêm đúng 2 state mới (`entering`, `exorcising`) — tối thiểu cần thiết để giữ ngữ nghĩa "nhập →
biểu hiện → trục xuất/thoát" mà `runtime/` cũ mô tả, KHÔNG bịa thêm state không cần (vì
`none`~`dormant`, `manifesting`~`manifest`, `peak`~`attack`, `released`~`released` đã có sẵn
tương đương trong `ghost`).

Transitions cũ (5 cạnh) → mới (8 cạnh, thêm đúng những cạnh cần cho 2 state mới, giữ nguyên
topology 1-đối-1 với 7 transition gốc của `runtime/` — chỉ đổi nhãn state cho khớp `ghost`):

| runtime/ (đã xoá) | bp4 ghost (mới) | trigger |
|---|---|---|
| none → entering | watching → entering | ghost_appears |
| entering → manifesting | entering → manifest | regret_triggered |
| manifesting → peak | manifest → attack | regret_triggered |
| peak → exorcising | attack → exorcising | ghost_released |
| exorcising → released | exorcising → released | ghost_released |
| manifesting → exorcising | manifest → exorcising | ghost_released |
| entering → released | entering → released | ghost_released |

0 event_id mới — 4 trigger dùng lại nguyên (`passenger_boards`/`ghost_appears`/
`regret_triggered`/`ghost_released`) đã khai sẵn `bp4/event_bus.yaml`, đúng giới hạn task.

### 2. `tools/supernatural_validator.py` — đọc từ bp4

- `STATE_MACHINE` đổi từ `runtime/supernatural_state_machine.yaml` →
  `governance/blueprint/bp4/state_machines.yaml`.
- Thêm `POSSESSION_ENTITY = 'ghost'` + hàm `_find_state_machine_entity()`.
- `check_possession_state_machine()` viết lại: tìm entity `ghost` trong `state_machines` list của
  bp4, đọc `states`/`transitions` từ đó, chạy lại đúng thuật toán BFS-ngược-tới-`released` cũ
  (M3, chống treo mãi) — **hành vi validate KHÔNG đổi**, chỉ đổi nguồn đọc.

### 3. `runtime/supernatural_state_machine.yaml` — XỬ LÝ file cũ

**Quyết định: GIỮ file, XOÁ block `possession_state_machine` trùng lặp** (không xoá cả file).

Lý do giữ: file còn chứa block `power_level_by_lunar_date` — đây **không phải** state machine,
không trùng BP4/BP9, là schema handoff hợp lệ cho G4 (World/Timeline/Event) đã dẫn trong
`reports/G5_HANDOFF_G8.md` dòng 38 ("Việc CỦA G4 — xem thêm `runtime/supernatural_state_machine.yaml`").
Xoá cả file sẽ làm mất nội dung THẬT không vi phạm R211, quá tay so với phạm vi vi phạm (chỉ
`possession_state_machine` mới là bản sao trái phép, `power_level_by_lunar_date` không phải).

Đã làm: xoá nguyên block `possession_state_machine` (dòng 20-43 bản cũ), viết lại header comment
từ đầu ghi rõ đây KHÔNG còn là state machine (trỏ sang bp4 + report này), version bump 1.0→1.1,
xoá field `reconciles`/`trigger_source_of_truth` (không còn ý nghĩa vì không còn state machine ở
đây để "reconcile" nữa), sửa `notes` cuối file cho khớp thực tế mới.

### 4. Test — `tests/test_supernatural_validator.py`

- `REAL_SM_YAML` trỏ sang `governance/blueprint/bp4/state_machines.yaml`.
- `test_m3_possession_stuck_state_fails`: đổi input giả từ format cũ
  (`{'possession_state_machine': {...}}`) sang format bp4 thật
  (`{'state_machines': [{'entity': 'ghost', ...}]}`) — khớp cấu trúc hàm mới đọc.
- Thêm `test_m3_missing_ghost_entity_fails` — bắt trường hợp entity `ghost` biến mất khỏi bp4.
- Thêm `test_real_state_machine_reads_from_bp4_ghost_entity` — pin cứng `sv.STATE_MACHINE ==
  bp4/state_machines.yaml` + xác nhận `entering`/`exorcising` có trong `ghost.states` (chống
  unwire ngược lại `runtime/` trong tương lai).

## Grep xác nhận 0 tham chiếu còn sót (cấu trúc trùng, không phải tên hàm)

```
$ grep -rn "possession_state_machine" .
governance/blueprint/bp4/state_machines.yaml:24:  (comment lịch sử, trỏ về report này)
tests/test_supernatural_validator.py: check_possession_state_machine (TÊN HÀM, không phải data key)
tools/supernatural_validator.py: check_possession_state_machine (TÊN HÀM + docstring giải thích)
runtime/supernatural_state_machine.yaml:5,12,48: comment lịch sử giải thích ĐÃ XOÁ, trỏ report này
```

Không còn key YAML `possession_state_machine:` nào tồn tại trong `runtime/
supernatural_state_machine.yaml` (đã xoá khối đó) — mọi hit còn lại là (a) tên hàm Python
`check_possession_state_machine` (giữ nguyên tên vì vẫn đúng chức năng — kiểm tra possession, chỉ
đổi NGUỒN đọc, không phải data structure trùng), hoặc (b) comment lịch sử giải thích đã xoá gì và
tại sao.

## Before / After — bằng chứng chạy máy thật

### Trước khi sửa (baseline, code cũ)

```
$ python tools/g5_supernatural_check.py
=== G5 SUPERNATURAL CHECK (typology + possession state machine) ===
=== PASS — typology + possession state machine hop le ===
EXIT=0

$ python -m pytest tests/test_supernatural_validator.py -q
15 passed in 0.31s

$ python -m pytest tests/ -q
490 passed, 8 skipped in 372.40s
```

### Sau khi sửa

```
$ python tools/g5_supernatural_check.py
=== G5 SUPERNATURAL CHECK (typology + possession state machine) ===
=== PASS — typology + possession state machine hop le ===
EXIT=0

$ python -m pytest tests/test_supernatural_validator.py -v
17 passed in 0.53s   (15 cũ + 2 test mới)

$ python tools/bp4_runtime_check.py
=== BP4 RUNTIME+EVENT CHECK v1.0.0 ===
  flow: 9 hop layer-tang · events: 8 · state machines: 4 (0 orphan) · memory: 6 scope khop BP0/BP3
=== PASS — BP4 runtime+event hop le (0 vi pham) ===
EXIT=0

$ python -m pytest tests/ -q
492 passed, 8 skipped in 350.98s
```

**0 regression**: 490→492 (đúng +2 = 2 test mới thêm ở bước 4), 8 skipped không đổi, không có
test nào baseline PASS mà sau sửa FAIL. Hành vi validate possession trên dữ liệu hợp lệ hiện có
KHÔNG đổi kết quả (vẫn PASS, `check_possession_state_machine() == []`) — chỉ đổi nguồn đọc, đúng
yêu cầu.

## Có thật là RECONCILE (không phải chỉ đổi tên)?

Có — khác với chỉ "đổi tên file/field", lần sửa này:
- Xoá hẳn 1 khối dữ liệu độc lập (`possession_state_machine`, entity riêng `possession`, 6 state
  riêng, 7 transition riêng) khỏi `runtime/`.
- Chuyển ngữ nghĩa của khối đó VÀO NGAY bên trong entity `ghost` đã tồn tại trong bp4 (không tạo
  entity mới `possession` trong bp4 — nếu làm vậy vẫn là "2 entity cho cùng 1 khái niệm", vẫn vi
  phạm tinh thần R211).
- `tools/supernatural_validator.py` giờ CHỈ có 1 nguồn đọc duy nhất cho possession: bp4.
- Từ nay, bất kỳ ai muốn sửa possession logic (thêm state, đổi trigger) BẮT BUỘC sửa bp4 — không
  còn cách "lách" qua file `runtime/` riêng.

## Honest caveats

- Việc ánh xạ `none~dormant`, `manifesting~manifest`, `peak~attack`, `released~released` là suy
  luận ngữ nghĩa (không có tài liệu nào định nghĩa cứng tương đương 1-1 giữa 2 bộ tên) — dựa trên
  đọc kỹ note gốc của `runtime/` cũ ("Mirror bp4 ghost.manifest/attack -> released, chi tiet hoa 2
  buoc trung gian 'entering'/'peak'"). Nếu Mr.Long có ý định khác về ngữ nghĩa 2 state
  `entering`/`exorcising`, cần review lại — đã ghi rõ lý luận trong note tại
  `bp4/state_machines.yaml#entity=ghost` để dễ đối chiếu.
- Giữ lại `runtime/supernatural_state_machine.yaml` (không xoá cả file) vì
  `power_level_by_lunar_date` là nội dung KHÁC, hợp lệ, không phải bản sao — đây là quyết định kỹ
  thuật có chủ đích, không phải "để đó cho chắc". Nếu audit muốn xoá luôn cả file, cần tách
  `power_level_by_lunar_date` sang vị trí khác trước (vd `governance/proposals/`) — ngoài phạm vi
  fix R211 lần này (chỉ có `possession_state_machine` mới là vi phạm).
- Phát hiện thêm (KHÔNG liên quan G5-4, KHÔNG sửa trong phiên này): worktree có 2 file thay đổi
  không phải do phiên này tạo ra trong lúc chạy test (`output/ep_01/episode_tts_ready.md`,
  `reports/G4_EVENT_FINDINGS.md`) — có vẻ do 1 tiến trình khác (render/miner) chạy song song trên
  cùng máy/worktree. Đã KHÔNG `git add`/commit 2 file này (ngoài phạm vi task, không phải của
  phiên fix G5-4) — cần Boss/phiên khác tự kiểm tra riêng nếu là thay đổi ngoài ý muốn.
- Không sửa `prompts/TASK_G5_SUPERNATURAL.md` / `reports/G5_HANDOFF_G8.md` (mô tả lịch sử D3 nhắc
  `runtime/supernatural_state_machine.yaml` như nơi chứa "chuỗi possession") — đây là tài liệu ghi
  lại YÊU CẦU/BÀN GIAO gốc tại thời điểm build, giữ nguyên làm lịch sử; phần mô tả possession ở đó
  nay đã lỗi thời so với thực tế code (đã reconcile vào bp4) nhưng sửa lại prompt gốc nằm ngoài
  phạm vi "sửa 1 vi phạm R211" được giao.

## Files thay đổi

- `governance/blueprint/bp4/state_machines.yaml` (mở rộng entity `ghost`)
- `tools/supernatural_validator.py` (đổi nguồn đọc `STATE_MACHINE`, viết lại
  `check_possession_state_machine()`)
- `runtime/supernatural_state_machine.yaml` (xoá block `possession_state_machine`, giữ
  `power_level_by_lunar_date`)
- `tests/test_supernatural_validator.py` (cập nhật format test M3 khớp bp4, thêm 2 test mới)
- `reports/G5_FIX_POSSESSION_DEDUP.md` (report này)
