#!/usr/bin/env bash
# Renders gta6-worst.mp4 (1080x1920, 30 fps, narrated). Needs node + playwright, ffmpeg, python3 + numpy, and for new narration the Kokoro voice (bash kit/setup.sh --voice).
set -euo pipefail
cd "$(dirname "$0")"
[ -s vo/vo.json ] || ../../kit/.venv/bin/python vo.py
node render.js
python3 audio.py
ffmpeg -v error -y -i video.mp4 -i audio.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart gta6-worst.mp4
rm -f video.mp4 audio.wav
echo "done: $(pwd)/gta6-worst.mp4"
