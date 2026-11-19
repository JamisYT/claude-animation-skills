#!/usr/bin/env python3
"""Narration with the free Kokoro voice (kit/.venv): vo/line_XX.wav + vo/vo.json (durations), one line per scene."""
import json, os
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
KIT = HERE.parents[1] / 'kit'
LINES = [
    "GTA 6 just scored a ninety-nine on Metacritic. But it's not perfect. Here are the worst things about it.",
    "Number six. The slow start. Reviewers say the opening takes its time before the fun kicks in.",
    "Number five. Cutscenes that interrupt the action, right in the middle of big heists.",
    "Number four. The combat. Several reviews call the gunplay clunky.",
    "Number three. The price. Seventy-nine ninety-nine for standard, and ninety-nine ninety-nine for the ultimate edition.",
    "Number two. No PC version. It's console only, and a PC release hasn't even been announced.",
    "And number one. Thirty frames per second. Every console is locked to thirty, even the PS5 Pro.",
    "Was it worth the thirteen year wait? Comment below, and subscribe for more!",
]
k = Kokoro(str(KIT / 'models/kokoro-v1.0.onnx'), str(KIT / 'models/voices-v1.0.bin'))
os.makedirs(HERE / 'vo', exist_ok=True)
durs = []
for i, line in enumerate(LINES):
    s, sr = k.create(line, voice='am_michael', speed=1.12, lang='en-us')
    idx = np.where(np.abs(s) > .01)[0]; s = s[max(0, idx[0] - int(.02 * sr)): idx[-1] + int(.06 * sr)]
    sf.write(HERE / 'vo' / f'line_{i:02d}.wav', s, sr); durs.append(round(len(s) / sr, 3))
    print(f'{i}: {durs[-1]:5.2f}s  {line}')
json.dump({'durs': durs, 'lines': LINES}, open(HERE / 'vo' / 'vo.json', 'w'), indent=1)
