@echo off
chcp 65001>nul
cd /d "%~dp0.."
claude "Ban la CMD_BUILD trong pipeline SVHMP. Doc prompts/CMD_BUILD.md va prompts/PIPELINE_PROTOCOL.md roi tuan thu tuyet doi. Xac nhan vai tro va cho lenh. Builder chi ket luan READY FOR AUDIT = YES/NO, KHONG PASS/FREEZE/SHIP."
