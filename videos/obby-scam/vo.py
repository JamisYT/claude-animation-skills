#!/usr/bin/env python3
"""Voices for story.json with the free Kokoro voice (kit/.venv): vo/<beat>_<n>.wav + vo/vo.json (durations)."""
import json, os
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
KIT = HERE.parents[1] / 'kit'
story = json.loads((HERE / 'story.json').read_text())
k = Kokoro(str(KIT / 'models/kokoro-v1.0.onnx'), str(KIT / 'models/voices-v1.0.bin'))
os.makedirs(HERE / 'vo', exist_ok=True)
durs = {}
for b in story['beats']:
    for i, (who, line) in enumerate(b['lines']):
        voice, speed = story['voices'][who]
        s, sr = k.create(line, voice=voice, speed=speed, lang='en-gb' if voice.startswith('b') else 'en-us')
        idx = np.where(np.abs(s) > .01)[0]
        s = s[max(0, idx[0] - int(.02 * sr)): idx[-1] + int(.06 * sr)]
        name = f"{b['id']}_{i}"
        sf.write(HERE / 'vo' / f'{name}.wav', s, sr)
        durs[name] = round(len(s) / sr, 3)
        print(f'{name:12s} {durs[name]:5.2f}s  {who}: {line}')
json.dump(durs, open(HERE / 'vo' / 'vo.json', 'w'), indent=1)
