@echo off
chcp 65001>nul
cd /d "%~dp0.."
rem Nap venv (co deps: yaml/pytest) vao PATH — dung TRUOC python312 bare
set "VENV=C:\Users\Admin\index-tts\.venv\Scripts"
if exist "%VENV%\python.exe" set "PATH=%VENV%;%PATH%"
claude "Ban la CMD_BUILD_3 - phien BUILD THU 3, doc lap voi CMD_BUILD (dang giu bp8_production/bp9_compliance) va G2_EXECUTOR (dang giu g2_character). Doc prompts/PIPELINE_PROTOCOL.md + docs/ENVIRONMENT_GOTCHAS.md (bai hoc G1-G10, dac biet G6 PACK CLAIM chi chan trung-pack chua chan build-truoc-khi-pack-truoc-lock, va G7/G9/G10 ve archive/relay/loi kiem duyet) truoc khi lam gi. NHIEM VU DUY NHAT: doc C:\Users\Admin\Desktop\TASK_BACKLOG_SVAF_PATTERNS.md (5 viec doc lap: Event Log, Error Code Standard, Policy Gates, Evidence Schema cho Cultural KB, ADR retro) - claim pack rieng TRUOC khi dong bat ky file nao: python tools/build_claim.py claim svaf_patterns_backlog CMD_BUILD_3 (PHAI exit 0 moi duoc lam). TUYET DOI KHONG DUNG: governance/blueprint/bp6-bp9/* , bible/* (tru khi Mr.Long uy quyen ro rang), runtime/passenger_roster_100.yaml, runtime/roster_backfill_draft.yaml, bat ky file nao 2 phien kia dang claim (check bang python tools/build_claim.py status truoc). Lam tung viec 1, worktree rieng (R200), self-test + log_ping + push sau moi viec, release claim khi xong. Xac nhan vai tro va cho lenh."
