@echo off
chcp 65001>nul
cd /d "%~dp0.."
rem Nap venv (co deps: yaml/pytest) vao PATH — dung TRUOC python312 bare
set "VENV=C:\Users\Admin\index-tts\.venv\Scripts"
if exist "%VENV%\python.exe" set "PATH=%VENV%;%PATH%"
claude "Ban la CMD_ARCH_AUDIT trong pipeline SVHMP. Doc prompts/CMD_ARCH_AUDIT.md va prompts/PIPELINE_PROTOCOL.md roi tuan thu tuyet doi. Self-test bang python tools/cmd_pipeline_gate.py --ref origin/main, lay verdict gate ARCH. Xac nhan vai tro va cho lenh."
