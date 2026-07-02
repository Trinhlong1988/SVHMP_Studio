@echo off
chcp 65001>nul
cd /d "%~dp0.."
claude "Ban la CMD_QA_AUDIT trong pipeline SVHMP. Doc prompts/CMD_QA_AUDIT.md va prompts/PIPELINE_PROTOCOL.md roi tuan thu tuyet doi. Self-test bang python tools/cmd_pipeline_gate.py --ref origin/main, lay verdict gate QA. Xac nhan vai tro va cho lenh."
