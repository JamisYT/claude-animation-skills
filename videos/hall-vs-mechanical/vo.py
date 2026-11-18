#!/usr/bin/env python3
"""Voiceover with the free Kokoro voice (kit/.venv + kit/models): writes vo/line_XX.wav and vo/vo.json (durations)."""
import json, os, sys
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
KIT = HERE.parents[1] / 'kit'
LINES = [  # one per scene; the outro gets two (the second goes with the subscribe pop-up)
    "Hall effect, versus mechanical. What's actually different?",
    "In a mechanical switch, pressing about two millimeters snaps two metal contacts together. Same point, on every key.",
    "Hall effect has no contacts. Just a magnet, and a sensor measuring how close it is. So you choose where it fires.",
    "That unlocks rapid trigger. Lift a hair, and it resets instantly. Same taps, four times the inputs.",
    "Hall wins on speed and durability. Mechanical wins on feel, and price.",
    "Competitive gaming? Go Hall effect. Typing on a budget? Mechanical.",
    "Subscribe for more!",
]
voice = sys.argv[1] if len(sys.argv) > 1 else 'am_michael'
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 1.1
k = Kokoro(str(KIT / 'models/kokoro-v1.0.onnx'), str(KIT / 'models/voices-v1.0.bin'))
os.makedirs(HERE / 'vo', exist_ok=True)
durs = []
for i, line in enumerate(LINES):
    s, sr = k.create(line, voice=voice, speed=speed, lang='en-us')
    idx = np.where(np.abs(s) > .01)[0]
    s = s[max(0, idx[0] - int(.02 * sr)): idx[-1] + int(.06 * sr)]
    sf.write(HERE / 'vo' / f'line_{i:02d}.wav', s, sr)
    durs.append(round(len(s) / sr, 3))
    print(f'{i}: {durs[-1]:5.2f}s  {line}')
json.dump({'durs': durs, 'lines': LINES}, open(HERE / 'vo' / 'vo.json', 'w'), indent=1)
