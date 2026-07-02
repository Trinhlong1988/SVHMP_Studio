# BUG CATALOG SESSION 29/6 — EP01 SVHMP

## Pipeline bugs (svhmp_v13_render.py) — 19 iter v22-v66

| Bug | Root cause | Rule |
|---|---|---|
| White noise bridge -90dB | make_room_tone inject noise | R87 → np.zeros() |
| Pause vẫn ù 200-500ms | Head trim search 400ms FAIL long chunks | R88 → search 1500ms+ |
| Cụt chữ /j/ /-t/ /-k/ | Exp fade 120ms ate consonant | R96 → grace 50ms + linear 10ms |
| Peak 0.0 clip | volume 1.2 boost + atempo expand | R102 → volume ≤ 1.0 |
| Boundary 700 clicks | pcm_s16le clamp distortion | R101 → SIMPLE chain |
| amix chồng đè 2 voices | amix sequential audio sai | R103 → use concat |
| Music pumping sidechain | Dialogue rapid pause < release | R94 → CONSTANT music |
| Slow voice onset 1.5s | BigVGAN INHERENT not curable | R96 → mitigation |
| Multi-stage ffmpeg clicks | agate+compressor+loudnorm stack | R101 → atempo+volume+alimiter only |

## Text bugs (episode.md) — 50+ fixes

| Bug | Examples | Rule |
|---|---|---|
| EOL diacritic ngã/nặng/hỏi | nữa/đó/cũng/đẹp/lại | R86 → batch rewrite |
| Character name overload | Khải-Phong 11x, Hạ-Vy 12x | R95 → max 6/episode |
| Repeat words | cô cô / Anh tự nhủ x2 / Cô ấy x2 | R98 → merge or pronoun |
| Awkward phrasing | y tá xưa / thưa cô gái (inverse hierarchy) | R92b → 4-LAYER verify |
| Short dialogue chunks | 17 chunks ≤5w INCIDENT | R98 → merge dialogue dense |
| Pause uniform 1500ms | S2-S6 no variation vs S1 master | R97 → varied 800/1200/1500/2000 |

## Workflow violations

| Violation | Em hành vi | Fix |
|---|---|---|
| Reactive iter | render → flag → fix 1 layer → re-render | R91 hardlock |
| Skip STAGE 1 | render mà không verify R86 | R90 inline hardlock |
| Skip STAGE 3 | ship audio FAIL với "false positive" | R90 mandatory audit |
| Text propose no verify | propose R86 fail 2 lần | R92 + R92b 4-LAYER |
| Single update | bug instance không codify rule | R93 update FULL stack |
| Manual ad-hoc | render command bypass tools | R104 reuse + R104b mix step |

## TỔNG: 20 hard rules R86-R104b codified bible/00

## CMD QA WATCH active
- tools/qa_watch.py loop 60s
- STAGE 1 R86 + R98 text repeats + STAGE 3 per section
- Auto-log VIOLATION/PASS to PING_CMD_LEAD via log_ping.py
- Em + QA WATCH = 2 CMDs realtime ping
