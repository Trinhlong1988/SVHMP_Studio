# DEPRECATION REPORT (G1 — Boss 2/7)

**Policy:** `keep`=active đang dùng · `deprecated`=one-off/backup/v1 → archive, KHÔNG xoá vội · `forbidden`=CẤM sửa.

## KEEP (active): 195
## DEPRECATED (archive candidate): 21

- `tools/ab_test_tail_trim_v1_vs_v2.py`
- `tools/assignment_planner_v1_backup.py`
- `tools/auto_fix_r61_aggressive.py`
- `tools/fix_anaphora_aggressive.py`
- `tools/fix_anaphora_chains_mixed.py`
- `tools/fix_anaphora_vary_subject.py`
- `tools/fix_chains_zero_tolerance.py`
- `tools/rewrite_batch_r61.py`
- `tools/rewrite_ep01_final.py`
- `tools/rewrite_ep01_r61.py`
- `tools/rewrite_ep02_05.py`
- `tools/rewrite_ep06_10.py`
- `tools/rewrite_ep11_15.py`
- `tools/rewrite_ep16_20.py`
- `tools/rewrite_ep21_25.py`
- `tools/rewrite_ep26_30.py`
- `tools/rewrite_ep31_35.py`
- `tools/rewrite_ep36_40.py`
- `tools/rewrite_ep41_45.py`
- `tools/rewrite_ep46_50.py`
- `tools/rewrite_pov.py`

## FORBIDDEN: 1
- thư mục ZIP `*-6d16ecda` (stale copy — R200 CẤM sửa)

## KHAI TỬ / DELETED (G8-D6 — Mr.Long authorization 9/7, commit quyết định `717342a`): 4

Khác `deprecated` (archive, giữ file): 4 file batch legacy dưới đây **xoá hẳn** — đã xác nhận
**0 live caller thật** (grep toàn repo: không `.py` nào import/gọi, chỉ xuất hiện trong doc/manifest).
Chuỗi audit chúng từng gọi (`audit_short_*`, `audit_style_stats`, `audit_phrase_repetition`,
`audit_pronoun_pov`…) nay chạy qua luồng G-pipeline hiện hành (auto_watch → qa_skeptic_orchestrator).

- `tools/deep_200_rounds.py` (governance_audit tier0) — đã stale-mark từ `bdc36e8`; report `runtime/deep_200_rounds_report.json` giữ lại với cờ `_STALE` làm chứng lịch sử.
- `tools/deep_200_rounds_all_rules.py` (governance_audit tier0)
- `tools/verify_50_rounds.py` (governance_audit tier0)
- `tools/sequential_full_auto.py` (generation tier2)

**Dọn kèm:** gỡ 4 entry `governance/file_index.yaml` (total 370→366) · gỡ khỏi 2 manifest
(`governance_audit_manifest.yaml` 27→24, `generation_manifest.yaml` 13→12) · `architecture_registry_check.py`
xác nhận 0/0/0 sau xoá (không MISSING). Tham chiếu doc lịch sử còn lại (KHÔNG sửa vì append-only /
immutable): `BUGS_FIXED.md` (bản ghi bug misleading-artifact), `bible/26` (ghi chú "orchestrator only,
no fix" — bible immutable, writer=mr_long), `docs/journal/NOTICE_ACTIVE_SESSION.md:135` (ví dụ lệnh cũ),
`reports/G8_QA_REALITY_MAP.md` (bản đồ D1). File `.bak.stale_mark_09_07` (CMD TỔNG TRỢ LÝ, untracked)
trở thành mồ côi sau xoá — vô hại, không thuộc git.
