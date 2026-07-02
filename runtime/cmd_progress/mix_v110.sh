#!/bin/bash
# v110 — Fix C13 click/pop regression từ v109 (loudnorm caused 13429 clicks)
# Strategy: highpass 30Hz + alimiter 0.7 (tighter than v108 0.8) + NO loudnorm
# CMD THUC THI 30/6 17:24
set -e
cd "D:\DỰ ÁN AI\GIỌNG ĐỌC\DỰ ÁN TRUYỆN MA\SVHMP_Studio"

echo "=== CONCAT v110 với R94b silence bridge 1500ms ==="
ffmpeg -y -hide_banner -loglevel error \
  -i "output/ep_01/sections/hook.wav" \
  -i "output/ep_01/sections/setup.wav" \
  -i "output/ep_01/sections/incident.wav" \
  -i "output/ep_01/sections/reveal.wav" \
  -i "output/ep_01/sections/payoff.wav" \
  -i "output/ep_01/sections/cliffhanger.wav" \
  -f lavfi -i "anullsrc=r=22050:cl=mono:duration=1.5" \
  -filter_complex "[0:a][6:a][1:a][6:a][2:a][6:a][3:a][6:a][4:a][6:a][5:a]concat=n=11:v=0:a=1[v]" \
  -map "[v]" -c:a pcm_s16le -ar 22050 "output/ep_01/EP01_VOICE_v110.wav"

echo "=== MIX v110 (highpass 30Hz + alimiter 0.7 + NO loudnorm) ==="
ffmpeg -y -hide_banner -loglevel error \
  -i "output/ep_01/EP01_VOICE_v110.wav" \
  -i "D:/hdk_music_library/_episodes/ep_001/ep_001_full.mp3" \
  -filter_complex "[0:a]highpass=f=30,volume=0.92,alimiter=limit=0.7:attack=10:release=80,adelay=6000|6000[voice];[1:a]highpass=f=30,volume=0.282,afade=t=in:st=0:d=2.0[music];[voice][music]amix=inputs=2:duration=first:normalize=0[out]" \
  -map "[out]" -c:a libmp3lame -q:a 2 -ar 44100 "output/ep_01/EP01_FULL_v110.mp3"

echo "=== DONE v110 ==="
