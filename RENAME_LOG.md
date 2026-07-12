# RENAME LOG — mass-replace decisions

**Rule:** Mọi mass-replace (≥10 instances cùng word→word) trong repo PHẢI log đây
trước commit. Pre-commit hook SECTION C verify.

**Format:** `[YYYY-MM-DD HH:MM] OLD → NEW (N instances) | author | reason`

---

- `2026-06-29 23:45` **Hắc Vỹ Dạ** → **Hắc Dạ Ký** | author: CMD LEAD | reason: Mr.Long quyết revert mid-session 22:52 — kênh name gốc
- `2026-06-30 13:17` **CMD #2** → **CMD THỰC THI** | author: CMD LEAD | reason: Mr.Long rename 30/6 13:15 — clarify role: LEAD=coordinator, THUC THI=executor (build/fix/apply)
- `2026-07-05 01:31` **Series:** → **Loat truyen:** | author: CMD LEAD | reason: DEBT-001 brand intro retrofit R40/R41, 37 tap ep_11-49 tru 30/50 (CMD_BUILD_3)
- `2026-07-05 01:31` **chua noi loi tam biet** → **chua kip noi loi tam biet** | author: CMD LEAD | reason: DEBT-001 brand intro retrofit R40/R41, 37 tap ep_11-49 tru 30/50 (CMD_BUILD_3)
- `2026-07-12 00:00` **(khong phai word→word rename)** — mass-line-removal that trong hook la do VIẾT LẠI NỘI DUNG THẬT (khong phai find-replace) o output/ep_0{3,4,6,7,9,10}/episode.md, doi pillar hoi tiec family_regret→promise/love/kindness/self_regret theo bang da duyet | author: CMD_BUILD | reason: DEBT-031, TASK_DEBT030_031_CONTENT_FIX.md Buoc 2, per Mr.Long "fix triet de vi day coi nhu lam that" (12/7). Ghi log de xoa WARN cua git_hook_pre_commit.py SECTION C — day KHONG phai 1 cap tu OLD→NEW dong nhat nen khong dien dung format bang tren, chi ghi nhan ngay+ly do theo dung muc dich cua rule (giai thich mass-removal, khong phai bia 1 cap tu gia).
