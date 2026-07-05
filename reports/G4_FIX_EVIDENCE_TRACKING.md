# G4 FIX — event_ledger_miner: evidence tracking cho object_mentions/primary_event

Task: sửa `tools/event_ledger_miner.py` để `object_mentions` và `primary_event`
(runtime/event_ledger_draft.yaml) mang field `line` (số dòng THẬT trong
`output/ep_N/episode.md`), giống hệt cơ chế đã có sẵn cho `temporal_mentions`.
KHÔNG viết parser mới — tái dùng cơ chế đếm dòng (`enumerate(lines, 1)`) đã
tồn tại trong `mine_episode`, mở rộng thêm sang `parse_header` (trước đây đọc
dòng nhưng không giữ lại số dòng).

## Nguyên nhân gốc (root cause)

- `parse_header(lines)` (dòng 91-104 bản cũ) duyệt qua header block nhưng chỉ
  trả về `dict key->value` — số dòng bị vứt bỏ ngay khi đọc xong. Mọi field
  của `primary_event` (`regret_sub`, `signature_object`, `signature_setting`,
  `passenger_main`, `stop_location`) đều lấy từ dict này → **không có cách nào**
  trace ngược lại episode.md dù dữ liệu gốc là thật.
- `object_mentions` dùng `set()` cộng 2 nguồn: (a) regex quét toàn bộ `lines`
  bắt `OBJ_[A-Z_]+` — có duyệt qua từng dòng nhưng không lưu `i` vào kết quả;
  (b) `sig_obj = header.get('signature_object')` cộng thẳng chuỗi RAW (kèm mô
  tả tiếng Việt, vd `'OBJ_AO_LEN_NAU (áo len nâu mẹ đan dở)'`) vào set — cũng
  không giữ dòng nguồn.

## Fix

1. `parse_header` nay trả về tuple `(meta, meta_lines)` — `meta_lines[key]` =
   số dòng 1-indexed thật trong chính danh sách `lines` truyền vào, nơi key đó
   được đọc. Cả 2 call site (`mine_episode`, `_add_freeform_nickname_candidates`)
   đã cập nhật để unpack tuple.
2. `primary_event`: mỗi field non-null giờ là
   `{'value': ..., 'ep': N, 'line': N}` (helper `_pe_field`) thay vì scalar
   trần. Field null vẫn giữ `None` (không có bằng chứng = không bịa entry).
3. `object_mentions`: đổi từ `set()` chuỗi phẳng sang
   `list[{'ep', 'line', 'value'}]`, dùng dict `value -> dòng đầu tiên gặp` để
   **giữ nguyên y hệt nội dung/số lượng tập hợp cũ** (chỉ bổ sung evidence,
   không đổi logic trích xuất): dòng cho mỗi OBJ_ID sạch = dòng đầu tiên quét
   regex ra nó (kể cả dòng header, vì `lines` bao gồm cả header); dòng cho
   chuỗi raw có mô tả (từ `header.get('signature_object')`) = chính dòng
   header đó (`meta_lines['signature_object']`, không suy luận).
4. `find_object_catalog_gaps` cập nhật để đọc được cả 2 dạng
   (`{'value':...}` dict từ `mine()` thật, hoặc string trần từ test synthetic
   cũ) — không đổi hợp đồng hàm, không phá test hiện có.

## Before / After

| Hạng mục | Tổng mục | Có `line` TRƯỚC fix | Có `line` SAU fix |
|---|---|---|---|
| temporal_mentions | 314 | 314 (100%) | 314 (100%) |
| object_mentions | 97 | 0 (0%) | 97 (100%) |
| primary_event (field non-null) | 206 | 0 (0%) | 206 (100%) |
| **Tổng** | **617** | **314 (50.89%)** | **617 (100%)** |
| **Thiếu evidence** | | **303 (49.11%)** | **0 (0%)** |

Trước fix (đo trực tiếp trên `mine()` tại `main` hiện tại, script đo:
`sum(len(s['object_mentions']))` + đếm field non-null của `primary_event`,
so với `temporal_mentions` vốn đã có `line` sẵn):

```
temporal_mentions total: 314
object_mentions total: 97
primary_event non-null fields total: 206
grand total: 617
missing evidence (object_mentions + primary_event): 303
missing pct: 49.11
```

Sau fix (cùng script đo, chạy lại `mine()` với code đã sửa):

```
temporal_mentions total: 314
object_mentions total: 97 with line: 97
primary_event non-null total: 206 with line: 206
grand total: 617
missing evidence: 0
missing pct: 0.0
```

Tổng số mục (617) và số lượng object_mentions (97)/primary_event non-null
(206) **giữ nguyên y hệt trước/sau** — fix chỉ bổ sung field `line`, không đổi
tập hợp dữ liệu được trích.

## Spot-check tay (đối chiếu `Get-Content` dòng thật trong episode.md)

### 1. temporal_mentions — ep_25 dòng 63
Draft: `{'ep': 25, 'line': 63, 'kind': 'lived_years', 'value': 10, 'text': 'sống mười năm'}`
`Get-Content output\ep_25\episode.md | Select-Object -Index 62` (dòng 63, 0-index 62):
```
Người khách gật. người đàn ông nhớ Phong — đập gương đêm anh hai mốt — sống mười năm — bây giờ ba mươi mốt — ném gương xuống hồ Đồng Mô như kết thúc thời nhớ.
```
Khớp — cụm "sống mười năm" thật sự nằm ở dòng 63.

### 2. object_mentions — ep_15 dòng 39
Draft: `[{'ep':15,'line':39,'value':'OBJ_GUONG_VO'}, {'ep':15,'line':39,'value':'OBJ_GUONG_VO (mảnh gương vỡ đêm Phong định không sống)'}]`
`Get-Content output\ep_15\episode.md | Select-Object -Index 38` (dòng 39):
```
signature_object: OBJ_GUONG_VO (mảnh gương vỡ đêm Phong định không sống)
```
Khớp — cả entry OBJ_ID sạch và entry raw-kèm-mô-tả đều đúng dòng 39 (đây
chính là dòng nguồn của cả 2, không phải bịa).

### 3. primary_event — ep_30 (4 field, 4 dòng)
Draft:
```
passenger_main:     {'line': 38}
signature_object:   {'line': 39}
signature_setting:  {'line': 40}
stop_location:      {'line': 41}
```
`Get-Content output\ep_30\episode.md | Select-Object -Index 37,38,39,40`:
```
38: passenger_main: nam 30 anh Nguyễn (người khách cùng tên!) — anh thầy giáo cứu khỏi bỏ học
39: signature_object: OBJ_BANG_TOT_NGHIEP (bằng tốt nghiệp THPT năm 2017)
40: signature_setting: setting_dem_thang_tu_HN
41: stop_location: ngã ba Hải Dương
```
Khớp cả 4 dòng.

### 4. (bonus) primary_event — ep_02 (5 field, 5 dòng, đối chiếu ban đầu khi debug)
Draft: `regret_sub`→39, `signature_object`→40, `signature_setting`→41,
`passenger_main`→37, `stop_location`→42.
`Get-Content output\ep_02\episode.md` dòng 37-42:
```
37: passenger_main : PAS_0013 (Hạ Diệu, nu 18-25)
38: regret_pillar  : family_regret
39: regret_sub     : REG_FAM_001 — Mẹ đợi con về Tết — con không về kịp
40: signature_object: OBJ_AO_LEN_NAU (áo len nâu mẹ đan dở)
41: signature_setting: setting_can_tet
42: stop_location  : ngã ba Phú Yên (quê Hạ Diệu, vùng đồng bằng)
```
Khớp toàn bộ — đây cũng là case spot-check thật đã nêu trong task (ep_02
dòng 40 `OBJ_AO_LEN_NAU`).

## Test suite (trước / sau fix)

- `tests/test_g4_world.py`: **20/20 PASS** trước fix, **20/20 PASS** sau fix
  (không đổi).
- Toàn bộ `tests/` (pytest): **490 passed, 8 skipped** trước fix, **490
  passed, 8 skipped** sau fix — 0 regression.

## Phạm vi / giới hạn đã biết

- `find_object_catalog_gaps` được cập nhật tối thiểu để đọc được cả dạng
  dict mới (`mine()` thật) lẫn dạng string trần (test cũ truyền tay) — không
  đổi hợp đồng hàm, không phá test hiện có.
- KHÔNG động vào F1/F2/F3 (logic phát hiện mâu thuẫn) — chạy lại xác nhận
  đếm y hệt trước fix (F1=57, F2=4, F3=36).
- `reports/G4_EVENT_FINDINGS.md` có 1 dòng đổi không liên quan tới fix này
  (`'Duy' (freeform_ep48...)` → `'Duy' (PAS_0116/freeform_ep48...)`) — đã xác
  minh bằng `git stash` chạy lại **code CŨ chưa sửa** vẫn cho ra đúng dòng
  mới này → là do roster (`runtime/passenger_roster_100.yaml`) đã có PAS_0116
  từ trước nhưng report cũ trong git chưa được regen lại, KHÔNG phải do fix
  của task này gây ra. Giữ nguyên vì đây là dữ liệu đúng-hơn (thật).
