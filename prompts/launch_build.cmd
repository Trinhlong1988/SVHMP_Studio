@echo off
chcp 65001>nul
cd /d "%~dp0.."
rem Nap venv (co deps: yaml/pytest) vao PATH — dung TRUOC python312 bare
set "VENV=C:\Users\Admin\index-tts\.venv\Scripts"
if exist "%VENV%\python.exe" set "PATH=%VENV%;%PATH%"
claude "Ban la CMD_BUILD trong pipeline SVHMP. Doc prompts/CMD_BUILD.md va prompts/PIPELINE_PROTOCOL.md roi tuan thu tuyet doi. Xac nhan vai tro va cho lenh. Builder chi ket luan READY FOR AUDIT = YES/NO, KHONG PASS/FREEZE/SHIP."
