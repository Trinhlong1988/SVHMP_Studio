# G3 DIALOGUE — D0 REALITY AUDIT (Baseline & Reality Check)

> TASK_G3_DIALOGUE.md D0. Mọi số liệu dưới đây từ lệnh máy chạy thật trên worktree
> `SVHMP_wt_g3build` (branch `build/g3-dialogue-d0-d8`), ngày 2026-07-05, TRƯỚC khi viết
> bất kỳ dòng code D3-D8 nào. Không suy đoán.

## 1) `python tools/ci_gate.py` — xác nhận đủ 11 stage hiện có

```
=== CI GATE ===
  [PASS] registry (exit 0) [REG2000]
  [PASS] blueprint (exit 0) [ART4001]
  [PASS] R199_tail (exit 0) [QA1010]
  [PASS] R203_conf (exit 0) [QA1011]
  [PASS] R205_char (exit 0) [QA1012]
  [PASS] R206_voice (exit 0) [QA1013]
  [PASS] R207_canon (exit 0) [QA1014]
  [PASS] R208_age (exit 0) [QA1015]
  [PASS] project_config (exit 0) [ART4002]
  [PASS] G2_roster (exit 0) [QA1001]
  [PASS] g5_supernatural (exit 0) [ONT5001]
  [PASS] G4_world (exit 0) [ONT4001]
  [PASS] pytest_suite (exit 0) — 502 passed, 8 skipped, 1 warning in 187.50s [QA1099]
=== CI GATE: PASS ✅ ===
```

**Đếm trực tiếp `CHECKS` trong `tools/ci_gate.py`: đúng 11 entry** —
`registry, blueprint, R199_tail, R203_conf, R205_char, R206_voice, R207_canon, R208_age,
project_config, G2_roster, g5_supernatural, G4_world`. KHÔNG có entry `dialogue`/`G3_dialogue`
(khớp TASK_G3_DIALOGUE.md dòng 199-204, không phải "4 stage" như 1 bản nháp cũ từng liệt sai).

`grep -i dialogue governance/architecture_registry.yaml` — **4 vùng khớp thật** (không phải
"0 hit"): `dependency_map` có 2 cạnh "Character -> Dialogue" / "Dialogue -> TTS", và
`tests/test_dialogue_appropriateness_1000_r208.py` + `tests/test_dialog_voice_single_source.py`
(D1, mới thêm 5/7) đăng ký dưới domain `character`. Domain `dialogue` **chưa có block độc lập**
— đúng gap D6 cần đóng.

## 2) `python tools/dialog_voice_validator.py` — baseline demo

```
profile issues: [{'code': 'HOMETOWN_REGION_MISMATCH', 'hometown': 'bến tre', 'expected': 'tay', 'got': 'nam'}]
line OK: []
line LEAK (bac 'nhé'): [{'code': 'DIALECT_LEAK', 'marker': 'nhé', 'belongs': 'bac', 'char_region': 'nam'}]
```

Lưu ý: demo tool tự chọn hometown "Bến Tre" (vùng `tay`, `EXTRA_REGIONS_DIALOGUE_ONLY`, D1) nhưng
gán `region_dialect='nam'` trong demo profile → tự sinh HOMETOWN_REGION_MISMATCH đúng như thiết kế
demo (không phải bug). Xác nhận sau fix D1: `HOME`/`EXTRA_REGIONS_DIALOGUE_ONLY` đang hoạt động
thật.

## 3) `python tools/audit_dialogue_hierarchy.py --summary` — baseline số issue 50 tập

```
=== GLOBAL ===
  Total HIGH dialogue issues: 34
  Total MEDIUM: 63
  EPs affected: 28
```
(exit code 1 vì `high_total != 0` — đúng hành vi thiết kế của tool, không phải lỗi chạy.)

## 4) Đo tỉ lệ MATCH/MISMATCH thật (dialect leak) trên 50 tập đã render

Phương pháp: với mỗi passenger có `assigned_ep` (đọc qua `CharacterRegistry`, KHÔNG đọc YAML lần
2), trích quote gán cho họ trong `output/ep_{n}/episode.md` bằng `extract_quotes()` **tái dùng
nguyên hàm** từ `tools/audit_dialogue_hierarchy.py` (không viết lại regex), chấm từng quote qua
`dialog_voice_validator.validate_line()` (không viết lại validator) — MISMATCH = có ít nhất 1
`DIALECT_LEAK` trong quote đó.

```json
{
  "total_passenger_with_ep": 87,
  "passenger_no_quote_extracted": 0,
  "total_quote_lines_checked": 1571,
  "MATCH": 1450,
  "MISMATCH": 121,
  "mismatch_rate_pct": 7.7
}
```

**Không phải 0** (nếu ra 0 sẽ phải nghi đo sai theo REALITY ANCHOR) — 7.7% mismatch rate là số
thật, thấp hơn kỳ vọng nếu 50 tập được thiết kế đa vùng có chủ đích (khớp PHẢN BIỆN #8: 50 tập
render TRƯỚC khi `region_dialect` tồn tại trong roster, `auto_gen_ep.py` không đọc field này — nên
phần lớn dialogue "khớp" chỉ vì template trung tính không chứa marker vùng nào, không phải vì được
sinh có chủ đích theo vùng miền). 10 case MISMATCH đầu (mẫu): PAS_0014(trung,ep3,5 leak),
PAS_0017(trung,ep6,4), PAS_0018(nam,ep7,2), PAS_0019(bac,ep8,3), PAS_0020(trung,ep9,2),
PAS_0021(nam,ep10,1), PAS_0022(bac,ep11,3), PAS_0023(trung,ep12,1), PAS_0025(bac,ep14,5),
PAS_0026(trung,ep15,4).

**Kết luận D0**: hạ tầng validate 100% chạy thật, generator 0% (đúng GAP THẬT đã liệt), 50 tập cũ
KHÔNG dùng được làm "golden đa vùng" (khớp PHẢN BIỆN #8) — D5 phải tách 2 nguồn, không mine trực
tiếp từ đây làm golden set chính.

## 5) Roster thật (đọc qua CharacterRegistry, không suy đoán)

`runtime/passenger_roster_100.yaml` hiện có **139 passenger** (không phải đúng 100 — tên file giữ
nguyên lịch sử). Phân bố `region_dialect` thật: `{'bac': 65, 'trung': 37, 'nam': 37}` — 0 `tay`/0
`do_thi` (đúng dự đoán: `HOME`/roster chỉ có 3 vùng, `tay`/`do_thi` là `EXTRA_REGIONS_DIALOGUE_ONLY`
chỉ dùng khi generator cần, D1). Field `voice` mỗi passenger mẫu thật CHỈ có `region_dialect,
hometown, pronoun_system, particles, register` — **KHÔNG có** `catchphrase, forbidden_words,
dialogue_sample, speaking_speed` dù `bible/37#tier_1_mandatory.voice` khai cả 6 field bắt buộc
(3 field đầu MOI thật đủ dữ liệu: `region_dialect, hometown, pronoun_system` — trùng đúng
`dialog_voice_validator.MANDATORY_VOICE`; `pronoun_style` trong schema bible/37 SAI TÊN so với
`pronoun_system` roster thật dùng — ghi nhận là gap đặt tên có sẵn của G2, G3 không tự sửa).

## STATUS D0
Baseline log đầy đủ, có before-số cho mọi phần D1-D8 sẽ so sánh. D0 = DONE, bằng chứng ở trên là
before-state chính thức của toàn bộ pack G3.
