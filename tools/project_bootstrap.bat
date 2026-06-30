@echo off
chcp 65001 >nul
title SVHMP Project Bootstrap — Mr.Long 1-click setup

cd /d "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio"

set PYTHONIOENCODING=utf-8
python tools\project_bootstrap.py

pause
