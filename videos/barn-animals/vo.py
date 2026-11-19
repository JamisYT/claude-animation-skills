#!/usr/bin/env python3
"""Voices (Kokoro, kit/.venv): a warm narrator and a playful animal voice. Writes vo/<id>.wav + vo/vo.json (durations)."""
import json, os
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
KIT = HERE.parents[1] / 'kit'
N, A = ('af_heart', 1.0), ('am_puck', .95)
ANIMALS = [('cow', 'Moo! Moo!'), ('pig', 'Oink! Oink!'), ('duck', 'Quack! Quack!'), ('sheep', 'Baa! Baa!'), ('dog', 'Woof! Woof!')]
LINES = {'intro': ("Who is hiding in the barn? Let's find out!", N)}
for a, snd in ANIMALS:
    name = 'puppy' if a == 'dog' else a
    LINES[f'{a}_is'] = (f"It's a {name}!", N)
    LINES[f'{a}_says'] = (f"The {name} says...", N)
    LINES[f'{a}_snd'] = (snd, A)
LINES['bye'] = ("Bye bye, friends! See you next time!", N)
k = Kokoro(str(KIT / 'models/kokoro-v1.0.onnx'), str(KIT / 'models/voices-v1.0.bin'))
os.makedirs(HERE / 'vo', exist_ok=True)
durs = {}
for key, (text, (voice, speed)) in LINES.items():
    s, sr = k.create(text, voice=voice, speed=speed, lang='en-us')
    idx = np.where(np.abs(s) > .01)[0]; s = s[max(0, idx[0] - int(.02 * sr)): idx[-1] + int(.08 * sr)]
    sf.write(HERE / 'vo' / f'{key}.wav', s, sr); durs[key] = round(len(s) / sr, 3)
    print(f'{key:10s} {durs[key]:5.2f}s  {text}')
json.dump(durs, open(HERE / 'vo' / 'vo.json', 'w'), indent=1)
