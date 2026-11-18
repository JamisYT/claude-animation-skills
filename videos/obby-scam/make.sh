#!/usr/bin/env bash
# Renders obby-scam.mp4 (1080x1920, 30 fps, with voices). Needs node + playwright, ffmpeg, python3 + numpy,
# three.js in kit/node_modules (bash kit/setup.sh) and, for new voices, the Kokoro voice (bash kit/setup.sh --voice).
set -euo pipefail
cd "$(dirname "$0")"
[ -s vo/vo.json ] || ../../kit/.venv/bin/python vo.py
node render.js
python3 audio.py
ffmpeg -v error -y -i video.mp4 -i audio.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart obby-scam.mp4
rm -f video.mp4 audio.wav
echo "done: $(pwd)/obby-scam.mp4"
