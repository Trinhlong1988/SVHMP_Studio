# SVHMP Mini Dashboard

300×300 Catppuccin Mocha widget + full audio player. Round 14 ship 2026-06-26.

## Files

| File | Mục đích |
|---|---|
| `index.html` | Widget 300×300 — current ep, progress 90, pipeline state, arcs, bugs, cost, git tags |
| `player.html` | Full UI — danh sách audio files (final + backup) + play + open Explorer + delete + regen-stage |
| `server.py` | HTTP server port 57910 + API endpoints |
| `launch.vbs` | Silent launcher (Desktop shortcut) |

## URLs

- Widget: http://127.0.0.1:57910/
- Player: http://127.0.0.1:57910/player

## API endpoints

| Method | Route | Mục đích |
|---|---|---|
| GET | `/api/status` | Real data từ state.yaml + lifecycle + analytics + cost_ledger + BUGS_FIXED + git |
| GET | `/api/files` | List audio output/ep_*/*.wav (final + .bak* backup) + duration + size |
| GET | `/api/audio?path=...` | Stream audio file (HTML5 audio player) |
| GET | `/api/open?path=...` | Mở Explorer + select file |
| POST | `/api/delete?path=...` | Move → `.trash/YYYYMMDD/` (safe, KHÔNG xóa permanent) |
| POST | `/api/regen?path=...` | Safe-mode: backup final → `.bak_pre_regen_<ts>` + return manual command (KHÔNG auto-trigger pipeline vì 32 hiến pháp + 100-check gate) |

## Cách chạy

```bash
# Manual:
cd "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\tools\dashboard"
python server.py

# Hoặc double-click:
launch.vbs   # silent background + auto-open browser
```

## Desktop shortcut

Tạo shortcut → target: `wscript "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\tools\dashboard\launch.vbs"`

## Security

- Path traversal blocked (`safe_resolve` check path within SVHMP root)
- Delete → trash (NEVER permanent)
- Regen → backup + return manual command (NEVER auto-call pipeline)
- 127.0.0.1 only (no external access)

## Apply rule cứng

- Read-only data từ YAML files (rule "cấm suy luận" — không bịa data)
- Cost rates TENTATIVE (Mr.Long fill `tools/cost_tracker.py` COST_RATES_TENTATIVE)
- Regen UI button KHÔNG bypass 100-check gate (Rule 31 from 32 hiến pháp)
