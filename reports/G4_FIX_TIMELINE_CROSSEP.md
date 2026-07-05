# G4 FIX — timeline_check.py::check_cross_episode_M1 (bug 2 lớp đã audit xác nhận)

## Bug (đã audit xác nhận, 2 lớp)

`tools/timeline_check.py::check_cross_episode_M1(mined)` (dòng ~72-82 bản gốc)
**bỏ qua tham số `mined`** — thân hàm chỉ có 1 dòng `return []` vô điều kiện.
Hệ quả: `R84_temporal_anchor_for_events` **KHÔNG BAO GIỜ** bắt được mâu thuẫn
"bao nhiêu năm trước" xuyên 2 tập, dù mâu thuẫn rõ ràng đến đâu.

Đây **không phải lỗi ngẫu nhiên** — theo `reports/G4_REPORT.md` mục "Quá trình
build" số 3, tác giả gốc **có ý** tắt việc áp `check_arithmetic_consistency_
across_episodes()` (hàm số học thuần, dòng ~51-69, **đúng thuật toán**, đã
mutation-test) lên dữ liệu F1 (nickname cross-episode candidate — fuzzy, tách
từng từ trong `char_name` ra làm ứng viên, **chưa xác nhận cùng 1 người**), vì
áp trực tiếp từng ra 16 "violation" giả (F1 gộp nhầm nhiều người khác tên vào
1 "candidate" do tần suất âm tiết). Tác giả đợi D3 (`governance/proposals/
fact_ledger_schema.yaml`, **chưa có chữ ký Mr.Long**) trước khi coi liên kết
là "confirmed" đủ để hard-fail — nhưng thay vì chỉ tắt đường dẫn "F1 → M1", đã
tắt **toàn bộ tham số `mined`**, khiến M1 mù hoàn toàn kể cả với tín hiệu KHÔNG
liên quan gì đến F1 (như exact full-name match ở fix này).

## Before evidence (chạy máy, xác nhận lại bug thật)

Tạo lại đúng test case đã audit: 2 "tập" giả (`_tmp_before_test/ep_15`,
`ep_25`), cùng 1 chuỗi tên nhân vật **VIẾT HOA CHÍNH XÁC giống hệt nhau**
("Phong Hoài Đức") xuất hiện literal trong cả 2 tập, cùng 1 mốc "mười năm
trước", nhưng tuổi hiện tại được nói khác nhau (31 vs 50 — chênh 19 năm dù
cùng mốc -10 năm — mâu thuẫn số học rõ ràng):

```
$ python -c "
mined = mine(output_root=Path('_tmp_before_test'))
print(check_cross_episode_M1(mined))
"
temporal ep15: [..., {'kind': 'years_ago', 'value': 10, ...}, {'kind': 'age', 'value': 31, ...}]
temporal ep25: [..., {'kind': 'years_ago', 'value': 10, ...}, {'kind': 'age', 'value': 50, ...}]
M1 result (BEFORE FIX): []
```

**BUG CONFIRMED**: `run()` → `M1_cross_episode_violations == []` → `exit 0
(PASS)` dù mâu thuẫn xuyên tập rành rành trong dữ liệu.

Baseline pytest TRƯỚC fix (đo bằng `git stash` riêng file `tools/timeline_
check.py` về bản gốc, chạy `python -m pytest tests/ -q`):

```
490 passed, 8 skipped in 351.13s
```

Khớp đúng baseline đã biết của TASK (490 passed, 8 skipped).

## Fix (hẹp, đúng phạm vi TASK — KHÔNG bật lại F1 làm hard-fail)

Thêm 1 lớp phát hiện MỚI trong `tools/timeline_check.py`, tách biệt hoàn toàn
khỏi F1 (không đụng `event_ledger_miner.py` — F1/F2 giữ nguyên 100% hành vi):

1. `_load_full_char_names(roster_path)` — chỉ lấy **CẢ CỤM** `char_name`
   nguyên văn từ roster (vd `"Phong Hoài Đức"`), **KHÔNG tách từng từ** như
   `_load_nickname_candidates` của F1. Loại `char_name` 1 từ (vd `"Nguyễn"`
   — họ đơn lẻ trong `spare_pool` draft, `PAS_0131`) vì không phải "full name"
   thật.
2. `_find_full_name_line_hits(output_root, full_names)` — quét thân bài mỗi
   tập tìm cụm tên đầy đủ xuất hiện **literal, case-sensitive, word-boundary
   Unicode** (mirror cách F1 dò nickname, chỉ khác ở việc không tách từ).
3. `find_exact_name_cross_episode_conflicts(mined, output_root, roster_path)`
   — **M1 mới**: chỉ hard-fail khi ĐỒNG THỜI
   - (a) cùng 1 cụm tên đầy đủ xuất hiện literal ở **≥2 tập khác nhau**, VÀ
   - (b) mỗi tập liên quan có **CẢ age VÀ years_ago** nằm gần nhau (±3 dòng,
     đồng bộ ngưỡng F2 `MAX_LINE_WINDOW_FOR_SAME_REFERENT`) quanh lần nhắc
     tên đó — nghĩa là có "temporal anchor" hợp lệ (mẫu ví dụ TASK gốc: "21
     tuổi... mười năm trước"), KHÔNG chỉ 2 tuổi rời rạc không có phép tính
     nào liên kết, VÀ
   - (c) `check_arithmetic_consistency_across_episodes()` (hàm cũ, không sửa)
     trả `False` trên các mốc đó.
4. `check_cross_episode_M1(mined, output_root=None, roster_path=None)` giờ
   **dùng** `mined` thật — gọi `find_exact_name_cross_episode_conflicts`.

Điều kiện (b) được thêm **sau khi tự bắt lỗi trên chính dữ liệu thật**: bản
đầu của fix (chỉ có điều kiện (a)+(c), không có (b)) chạy trên 50 tập thật ra
1 false-positive: `'Hạ Nhi'` (nhân vật draft trong `spare_pool`, `PAS_0151`,
`assigned_ep: None`, là em/chị gái của Hạ Vy — nhắc lại ở 9 tập) có tuổi 16 ở
ep_33 và 24 ở ep_50 nhưng **không có mốc "X năm trước" nào đi kèm** ở tập nào
— tức không có phép tính nào thật sự liên kết 2 con số, chỉ là 2 bối cảnh
khác nhau nhắc tuổi khác nhau (đúng loại lỗi F2 cũ: "gộp tuổi nhiều người/bối
cảnh khác nhau" — không phải mâu thuẫn số học xác nhận được). Thêm điều kiện
(b) loại bỏ case này, khớp đúng bài học đã ghi trong `G4_REPORT.md`.

## After evidence (chạy máy, xác nhận fix đúng)

Case bug thật ở trên (`_tmp_after_test`, roster giả có `char_name: "Phong Hoài
Đức"`):

```
$ python -c "
mined = mine(output_root=Path('_tmp_after_test'), roster_path=Path('_tmp_after_test/roster.yaml'))
m1 = check_cross_episode_M1(mined, output_root=Path('_tmp_after_test'), roster_path=Path('_tmp_after_test/roster.yaml'))
print(m1)
"
[{'exact_name': 'Phong Hoài Đức', 'episodes': [15, 25],
  'ages_by_ep': {15: [31], 25: [50]}, 'years_ago_by_ep': {15: [10], 25: [10]},
  'evidence': \"'Phong Hoài Đức' xuat hien literal (exact, case-sensitive) o
  ['ep_15', 'ep_25'] — tuoi/moc gan ten do khong khop qua years_ago\"}]
```

→ FAIL đúng (đỏ thật), khác hoàn toàn `[]` trước fix.

Dữ liệu thật 50 tập (`mine()` + `check_cross_episode_M1()` không tham số
override) vẫn `[]` sau fix — **không** bắt lại 'Hạ Nhi' hay bất kỳ case nào
trong F1 (57 nickname candidate hiện có) làm hard-fail:

```
$ python -c "print(check_cross_episode_M1(mine()))"
[]
```

## Test mutation mới (`tests/test_g4_world.py`)

4 test mới, nhóm "M1 WIRING FIX":

- `test_m1_exact_name_match_arithmetic_conflict_bites` — mirror đúng case bug
  thật ở trên (2 tập, cùng tên đầy đủ, mâu thuẫn 31 vs 50 cùng mốc -10 năm)
  → PHẢI FAIL (đỏ trước fix, xanh sau fix — đã verify bằng `git stash` file
  gốc trước khi viết fix).
- `test_m1_exact_name_match_consistent_case_clean` — mirror case NHẤT QUÁN
  gốc trong TASK (21+10=31 khớp cả 2 tập) → không được FAIL.
- `test_m1_exact_name_match_requires_paired_temporal_anchor_not_bare_age_diff`
  — neo lại chính giới hạn (b) vừa thêm: 2 tuổi khác nhau KHÔNG có "X năm
  trước" đi kèm → không đủ tin cậy để hard-fail (case thật 'Hạ Nhi' phát hiện
  khi build fix).
- `test_m1_single_word_nickname_not_promoted_to_exact_name_layer` — char_name
  1 từ (họ đơn lẻ kiểu `PAS_0131` 'Nguyễn') không được vào lớp mới, dù trùng
  nhiều tập và có vẻ mâu thuẫn tuổi.

Test cũ `test_timeline_check_pass_on_real_data` (đã có sẵn, không sửa) tiếp
tục là hàng rào chống tái diễn 16 false-positive lịch sử: vẫn assert
`M1_cross_episode_violations == []` trên 50 tập thật, và **đã pass** sau fix
— chứng minh lớp mới không lặp lại lỗi cũ.

## Kết quả test suite

| | passed | skipped |
|---|---|---|
| TRƯỚC fix (file gốc, `git stash`) | 490 | 8 |
| SAU fix | 494 | 8 |

+4 = đúng bằng 4 test mutation mới thêm vào, 0 test cũ đổi trạng thái
(không có test nào chuyển pass→fail), 0 regression.

## Vì sao KHÔNG mở rộng sang F1 (fuzzy nickname)

F1 (`event_ledger_miner.find_cross_episode_name_recurrence`) tách **từng từ
đơn** trong `char_name` (vd "Phong" từ "Phong Hoài Đức") làm ứng viên nickname
— đây chính là cơ chế đã gây ra 16 "violation" giả khi tác giả gốc thử áp M1
lên F1 (xem `G4_REPORT.md` mục 3): 1 âm tiết trùng ngẫu nhiên giữa nhiều nhân
vật khác nhau bị coi là "cùng 1 người". Liên kết đó **chưa được xác nhận** —
cần D3 (`fact_ledger_schema.yaml`) có chữ ký Mr.Long mới đủ tin cậy. Fix này
**giữ nguyên quyết định gốc đó**: F1 vẫn chỉ là ứng viên in trong
`G4_EVENT_FINDINGS.md` cho người xem lại, không đưa vào đường dẫn hard-fail
của M1. Lớp mới **không dùng chung dữ liệu/hàm với F1** — nó tự nạp `char_name`
CẢ CỤM (không tách từ) và tự quét literal match riêng, nên rủi ro trùng lặp
lỗi cũ gần như không có (đã verify bằng test suite thật + case 'Hạ Nhi').

## Honest caveat (giới hạn còn lại — CHƯA giải quyết bằng fix này)

- Lớp mới chỉ bắt được mâu thuẫn khi 2 tập dùng **CHÍNH XÁC cùng 1 chuỗi ký
  tự** cho tên nhân vật (case-sensitive, full string). Mọi biến thể — biệt
  danh, đại từ, tên rút gọn, đồng tham chiếu (coreference), hoặc chỉ lệch 1
  dấu câu/khoảng trắng — **vẫn không bắt được**, và **vẫn cần D3
  (`fact_ledger_schema.yaml`) được Mr.Long ký** để xử lý đúng cách (đúng như
  quyết định gốc của tác giả, không đổi).
- Trên 50 tập thật hiện tại, lớp mới trả `[]` — do dữ liệu thật (one-shot-only
  theo bible/03) chưa có case nào đủ 2 điều kiện (a)+(b) cùng lúc với mâu
  thuẫn thật. Đây có thể là "chưa có bug thật để bắt" (đúng — one-shot
  passenger hiếm khi được nhắc lại bằng CHÍNH XÁC tên đầy đủ ở tập khác), chứ
  không phải bằng chứng lớp mới hoạt động — bằng chứng thật nằm ở test
  mutation + before/after evidence phía trên.
- Route xử lý F1 (57 candidate hiện có) và F2 (4 candidate) **không đổi** —
  vẫn chờ executor/Mr.Long xem lại thủ công, không tự động hard-fail.
