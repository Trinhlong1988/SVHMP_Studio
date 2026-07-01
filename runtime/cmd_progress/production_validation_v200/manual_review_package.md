# Manual Review Package — EP01 v200

**Generated:** 2026-06-30T23:10
**Purpose:** Help Mr.Long listen efficiently + record verdict per section.

## Audio file

**Path:** `output/ep_01/EP01_FULL_v200.mp3`
**Size:** 13 MB
**Duration:** 20:39
**LUFS:** -16 range (target met)
**Peak:** -16.14 dB (safe)

## Open command (Windows)

```
Start-Process "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio\output\ep_01\EP01_FULL_v200.mp3"
```

## Section timeline (for Mr.Long to mark verdict)

| # | Section | Start time | End time | Duration | Key text | Mr.Long verdict |
|---|---|---|---|---|---|---|
| 1 | hook | 0:06 (after 6s intro) | ~1:30 | ~1:24 | "Đêm đã buông xuống lặng lẽ trên thành phố..." | ⏸️ TBD |
| 2 | setup | ~1:32 | ~5:00 | ~3:28 | "Anh nhíu mắt khẽ một thoáng..." + Bỗng nhiên... | ⏸️ TBD |
| 3 | incident | ~5:02 | ~8:24 | ~3:22 | "Anh cứng cả bàn tay..." | ⏸️ TBD |
| 4 | reveal | ~8:26 | ~14:54 | ~6:28 | "Tôi nhớ ra rồi đấy cháu ạ" + REVEAL Hạ-Vy | ⏸️ TBD |
| 5 | payoff | ~14:56 | ~17:48 | ~2:52 | "Anh ngừng nói. [pause] Cô gái ghế tám..." | ⏸️ TBD |
| 6 | cliffhanger | ~17:50 | ~20:39 | ~2:49 | "Bác tài: — Con đã nhớ ra chưa?" + outro Option D | ⏸️ TBD |

## Items to listen for (Mr.Long-flagged historical bugs)

| Time | Item | Expected after fix |
|---|---|---|
| ~1:32 setup | "Anh nhíu mắt" — was cụt | Should be "Anh nhíu mắt khẽ một thoáng" — đủ hơi |
| ~1:50 setup | "Sương ngoài cửa kính" + "Anh ngước nhìn" | Should NOT have "kính" lặp 2 dòng (R177 fix) |
| ~2:20 setup | "[pause:1200ms] Bỗng nhiên... chiếc đồng hồ" | Should have ellipsis + extended pause |
| ~5:10 incident | "Anh khựng người — Hạ-Vy từng hát..." | Should be merged via em-dash, no cụt |
| ~6:00 incident | "kẹt xe vì đường ngập nước" | Should be "vì đường ngập" (semantic clear) |
| ~10:30 reveal | "— Tôi nhớ ra rồi đấy cháu ạ" | LISTEN FOR voice character drift "ẹ ẹ như dê" — Mr.Long historical flag |
| ~12:00 reveal | "— Tôi mua đồng hồ để cô ấy nhớ giờ về" | LISTEN FOR voice drift Khải-Phong |
| ~13:30 reveal | "— Tôi vẫn còn sợ... ám ảnh đến tận hôm nay" | Should be vary "sợ" (R66 chain fix) |
| ~15:00 payoff | "Anh ngừng nói. [pause:1500ms]" | LISTEN FOR pause length adequate |
| ~17:20 payoff | "Bác tài buông một cái nhìn thoáng qua" | Should be "thoáng qua" not "rất ngắn" (R180b) |
| ~18:30 cliffhanger | "ông già nhẹ giọng thì thầm" | LISTEN FOR tạp âm xì xì breath artifact |
| ~19:00 cliffhanger | "sao tôi không nhớ ra điều gì..." | LISTEN FOR ù ù pause boundary artifact |
| ~19:30 cliffhanger | "chưa ai từng kể ra" | LISTEN FOR tạp âm onset artifact |
| ~19:50 cliffhanger | "— Con đã nhớ ra chưa?" (Q1 instead of Q2) | Bác tài Q1 cho cô gái mới (B60 fix) |
| ~20:20 cliffhanger | "Hãy nhớ rằng... có thể chính bạn cũng đang ngồi..." | Option D outro (B62 fix) |

## R190 prosody catalog — for cross-reference if Mr.Long flags pitch drops

Reveal section has highest R190 detection (183 HIGH + 299 MED). If Mr.Long hears pitch drops/rung lẹm in reveal, cross-reference `r190_timestamp_catalog.json` for section-time-text-severity.

## Mr.Long verdict template (please fill after listen)

```
Overall: [ACCEPT / REJECT / PARTIAL]

Per section verdicts:
  hook:        [OK / FIX_NEEDED: ___________]
  setup:       [OK / FIX_NEEDED: ___________]
  incident:    [OK / FIX_NEEDED: ___________]
  reveal:      [OK / FIX_NEEDED: ___________]
  payoff:      [OK / FIX_NEEDED: ___________]
  cliffhanger: [OK / FIX_NEEDED: ___________]

R190 prosody audibility:
  [ ] AUDIBLE — bug confirmed → calibrate threshold or fix render
  [ ] NOT AUDIBLE — detector too sensitive, lower threshold post Golden cert

Audio mix balance:
  music volume:  [OK / too_loud / too_quiet]
  voice clarity: [OK / muddy / boomy / harsh]
  silence bridge length: [OK / too_long / too_short]

Specific items Mr.Long flags:
  __________________________________
  __________________________________
```

## After Mr.Long verdict

- ACCEPT → CMD THỰC THI proceeds: Golden Audio cert workflow (per R195) → calibrate → freeze → Git tag v2.1.0
- REJECT → CMD THỰC THI catalog bugs → iterate v201
- PARTIAL → fix specific items → re-render affected sections → v201

Em STOP for Mr.Long review.
