#!/usr/bin/env bash
# Renders hall-vs-mechanical.mp4 (1080x1920, 30 fps, with sound). Needs node + playwright, ffmpeg, python3 + numpy.
set -euo pipefail
cd "$(dirname "$0")"
node render.js
python3 audio.py
ffmpeg -v error -y -i video.mp4 -i audio.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart hall-vs-mechanical.mp4
rm -f video.mp4 audio.wav
echo "done: $(pwd)/hall-vs-mechanical.mp4"
