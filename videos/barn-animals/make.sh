#!/usr/bin/env bash
# Renders barn-animals.mp4 (1080x1920, 30 fps). Needs node + playwright, ffmpeg, python3 + numpy,
# three.js in kit/node_modules (bash kit/setup.sh) and, for new voices, the Kokoro voice (bash kit/setup.sh --voice).
set -euo pipefail
cd "$(dirname "$0")"
[ -s vo/vo.json ] || ../../kit/.venv/bin/python vo.py
node render.js
python3 audio.py
ffmpeg -v error -y -i video.mp4 -i audio.wav -c:v copy -af loudnorm=I=-15:TP=-1.5:LRA=11 -c:a aac -b:a 192k -shortest -movflags +faststart barn-animals.mp4
rm -f video.mp4 audio.wav
echo "done: $(pwd)/barn-animals.mp4"
