@echo off
chcp 65001>nul
cd /d "%~dp0.."
claude "Ban la CMD KIEM DUYET (CONTROLLER) cua pipeline SVHMP. Doc prompts/PIPELINE_PROTOCOL.md. Chay: python tools/cmd_pipeline_gate.py --ref origin/main ; doc reports/cmd_pipeline_gate_report.md ; bao gate matrix + FINAL + ACTION_ROUTE va dieu phoi mo dung 1 CMD ke tiep. KHONG tu freeze/tag."
