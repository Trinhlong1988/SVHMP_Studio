@echo off
chcp 65001>nul
cd /d "%~dp0.."
rem Nap venv vao PATH de `python` trong phien claude chay duoc (may nay python KHONG tren PATH)
set "VENV=C:\Users\Admin\index-tts\.venv\Scripts"
if exist "%VENV%\python.exe" set "PATH=%VENV%;%PATH%"
claude "Ban la CMD KIEM DUYET (CONTROLLER) cua pipeline SVHMP. Doc prompts/PIPELINE_PROTOCOL.md. Chay: python tools/cmd_pipeline_gate.py --ref origin/main ; doc reports/cmd_pipeline_gate_report.md ; bao gate matrix + FINAL + ACTION_ROUTE va dieu phoi mo dung 1 CMD ke tiep. KHONG tu freeze/tag."
