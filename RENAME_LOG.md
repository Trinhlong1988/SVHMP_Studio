# RENAME LOG — mass-replace decisions

**Rule:** Mọi mass-replace (≥10 instances cùng word→word) trong repo PHẢI log đây
trước commit. Pre-commit hook SECTION C verify.

**Format:** `[YYYY-MM-DD HH:MM] OLD → NEW (N instances) | author | reason`

---

- `2026-06-29 23:45` **Hắc Vỹ Dạ** → **Hắc Dạ Ký** | author: CMD LEAD | reason: Mr.Long quyết revert mid-session 22:52 — kênh name gốc
- `2026-06-30 13:17` **CMD #2** → **CMD THỰC THI** | author: CMD LEAD | reason: Mr.Long rename 30/6 13:15 — clarify role: LEAD=coordinator, THUC THI=executor (build/fix/apply)
- `2026-07-05 01:31` **Series:** → **Loat truyen:** | author: CMD LEAD | reason: DEBT-001 brand intro retrofit R40/R41, 37 tap ep_11-49 tru 30/50 (CMD_BUILD_3)
- `2026-07-05 01:31` **chua noi loi tam biet** → **chua kip noi loi tam biet** | author: CMD LEAD | reason: DEBT-001 brand intro retrofit R40/R41, 37 tap ep_11-49 tru 30/50 (CMD_BUILD_3)
