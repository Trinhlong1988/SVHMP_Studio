# BUGS_FIXED — HDK Channel (assets/hdk_channel/)

**Rule cứng:** memory `feedback_fix_registry_rule.md` (Mr.Long 26/6)
**Audit script:** `C:\tmp\hdk_audit_20rounds.py` — re-run cover ALL bugs dưới
**Session start protocol:** đọc file này + README.md + _AUDIT_TENTATIVE_LOG.md trước touch code

---

## Bugs

### B1 — YAML colon parse error bible/04 line 375
- **Ngày catch:** 2026-06-26
- **Phát hiện qua:** Audit script round R07
- **Triệu chứng:** `yaml.safe_load(bible/04_asset_bible.yaml)` raises "mapping values are not allowed here"
- **Root cause:** Unquoted YAML string chứa colon `:` trong `(5 SFX: gió + chuông xa...)` — YAML parser interpret colon là mapping separator
- **Fix:** `bible/04_asset_bible.yaml` line 375 — quote string: `audio: "stereo 48kHz (5 SFX: gió + chuông xa + đèn dầu + piano + còi tàu)"`
- **Regression test:** `C:\tmp\hdk_audit_20rounds.py` R07 — `yaml.safe_load()` bible/04 + bible/19
- **Cross-ref:** session 26/6 HDK 22-round audit final report

### B2 — Audit script case-sensitive miss "KHÔNG"
- **Ngày catch:** 2026-06-26
- **Phát hiện qua:** Audit script round R16 (false negative)
- **Triệu chứng:** Audit báo "không tiếng hét" missing trong storyboard, thực tế có "KHÔNG tiếng hét/quỷ" (uppercase + suffix)
- **Root cause:** Script Python check `string in content` case-sensitive, không match "KHÔNG" vs "không"
- **Fix:** `C:\tmp\hdk_audit_20rounds.py` R16 — `sb_lower = sb.lower()`, check `f.lower() in sb_lower`
- **Regression test:** R16 case-insensitive check 3 docx facts: "không phát sáng mạnh" + "cắt thẳng" + "không tiếng hét"
- **Cross-ref:** docx Mr.Long 25/6 23:56 LOCK

### B3 — BOM ﻿ phá regex banner detection
- **Ngày catch:** 2026-06-26
- **Phát hiện qua:** Approve banner script (post-audit phase)
- **Triệu chứng:** PowerShell regex `^>\s*⚠️` không match line 0 dù banner có format đúng; script "TENTATIVE found but block not matched" cho 17 file
- **Root cause:** PowerShell `Set-Content -Encoding UTF8 -NoNewline` thêm BOM `﻿` (U+FEFF) đầu file. Line 0 thực tế là `﻿> ⚠️ **TENTATIVE...` → `line.startswith('>')` returns False vì BOM trước `>`.
- **Fix:** `C:\tmp\hdk_fix_paths_approve.py` — Python script strip BOM: `line.lstrip('﻿')`, write back `Set-Content -Value $cleaned -Encoding UTF8 -NoNewline` standardize bỏ BOM
- **Regression test:** R22 audit check `no leading > banner with TENTATIVE_SUY_LUẬN` regex multiline
- **Cross-ref:** Hỏi Python repr line debug → phát hiện `﻿` prefix

### B4 — Path bug hdk_brand/ folder rename không sync trong content
- **Ngày catch:** 2026-06-26
- **Phát hiện qua:** Debug round 2 (sau approve)
- **Triệu chứng:** 4 files (SETUP_CHECKLIST + 01_brand_logo + 02_brand_typography + storyboard) ref `assets/hdk_channel/hdk_brand/logo/...` nhưng folder thực tế đã rename `brand/` khi move D:\HDK_Assets → SVHMP_Studio\assets\hdk_channel\
- **Root cause:** PowerShell move script rename folder root nhưng KHÔNG sweep update path content trong markdown files. Path replace pass trước chỉ thay `D:\HDK_Assets\` → `assets/hdk_channel/`, KHÔNG thay `hdk_brand` → `brand`.
- **Fix:** `C:\tmp\hdk_fix_paths_approve.py` regex 3 patterns: `r'(hdk_channel[\\/])hdk_brand([\\/])' → r'\1brand\2'` + 2 variants for bare references
- **Regression test:** R21 audit — `re.search(r'hdk_channel[\\/]hdk_brand[\\/]', c)` phải = 0 hits across all .md + .yaml files
- **Cross-ref:** Rename precedent SVTK foundation v2.10.0 (refactor folder cần sweep references)

### B6 — Audit false positive: BUGS_FIXED.md document ref bug history
- **Ngày catch:** 2026-06-26
- **Phát hiện qua:** Ngay khi tạo BUGS_FIXED.md → audit re-run R02 + R21 FAIL
- **Triệu chứng:** Audit báo "old D:\HDK_Assets reference" + "bad path hdk_channel/hdk_brand/" trong BUGS_FIXED.md, dù file này chỉ DOCUMENT bug fix history (không phải active code path)
- **Root cause:** Audit script không phân biệt documentation context vs production state. BUGS_FIXED + _AUDIT_TENTATIVE_LOG file MENTION bug pattern để record, không phải sử dụng path đó thực sự.
- **Fix:** `C:\tmp\hdk_audit_20rounds.py` R02 + R21 — add `DOC_EXCLUDE = {'BUGS_FIXED.md', '_AUDIT_TENTATIVE_LOG.md'}` skip documentation files
- **Regression test:** R02 + R21 audit run pass 22/22 sau exclude docs (verify command: `python C:/tmp/hdk_audit_20rounds.py | grep SUMMARY`)
- **Cross-ref:** Rule meta — audit phải distinguish "current state" vs "historical documentation". General lesson cho mọi audit script tương lai.

### B5 — Audit check R19 outdated sau approve flow
- **Ngày catch:** 2026-06-26
- **Phát hiện qua:** Re-run audit sau approve
- **Triệu chứng:** R19 fail "13 prompts missing T4.{N}" sau khi approve banner replace TENTATIVE → APPROVED (lost T4.N reference)
- **Root cause:** Banner cũ chứa `T4.1`..`T4.13` per file. Banner mới (post-approve) generic "T1-T8". R19 check banner = pattern outdated, không reflect post-approve state.
- **Fix:** `C:\tmp\hdk_audit_20rounds.py` R19 — change check from "T4.{N} in 13 prompt files" → "T4.1..T4.13 in audit log historical" (audit trail luôn keep mapping)
- **Regression test:** R19 check `T4.{i}` in `_AUDIT_TENTATIVE_LOG.md` for i in 1..13
- **Cross-ref:** Audit lifecycle: pre-approve check banner, post-approve check audit log

---

## Audit regression coverage

Audit script: `C:\tmp\hdk_audit_20rounds.py` (22 rounds total)

| Bug | Audit round | Coverage status |
|---|---|---|
| B1 YAML colon | R07 | ✓ permanent |
| B2 case-sensitive | R16 | ✓ permanent |
| B3 BOM banner | R22 (post-approve) | ✓ permanent |
| B4 path rename | R21 | ✓ permanent |
| B5 R19 legacy | R19 (refactored) | ✓ permanent |

Re-run command: `python C:/tmp/hdk_audit_20rounds.py` — must PASS 22/22.

---

## Stats

- Total bugs caught: 6 (B1-B6)
- Total regression tests: 6
- Last audit run: 2026-06-26 (post-B6 fix)
- Last audit PASS: 22/22 (2026-06-26)
- Notable: B6 caught NGAY khi tạo BUGS_FIXED.md — process work end-to-end
