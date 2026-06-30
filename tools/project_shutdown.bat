@echo off
chcp 65001 >nul
title SVHMP Project Shutdown — TAT all

cd /d "C:\tmp\svhmp_review"

set PYTHONIOENCODING=utf-8
python tools\project_shutdown.py

pause
