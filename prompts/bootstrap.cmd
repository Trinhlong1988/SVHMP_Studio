@echo off
chcp 65001>nul
rem bootstrap.cmd — DONG BO + SHIP DESKTOP (chay 1 lan tren MOI may). KHONG PowerShell.
cd /d "%~dp0.."
echo Repo: %CD%
git pull --rebase origin main
cscript //nologo "%~dp0mk_shortcuts.vbs"
echo.
echo XONG. Desktop co icon "SVHMP PIPELINE (control)" -^> 1-click chay controller.
pause
