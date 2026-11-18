#!/usr/bin/env python3
"""Voice-chat lines for the owner (Kokoro, kit/.venv): vo/<id>.wav + vo/vo.json. audio.py makes them sound like a loud mic."""
import json, os
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

HERE = Path(__file__).resolve().parent
KIT = HERE.parents[1] / 'kit'
LINES = {
    'where': ("Wait. Where's my Tralalero?!", 'am_puck', 1.15),
    'nono': ("No no no no no! Give it back! GIVE IT BACK!", 'am_puck', 1.35),
    'second': ("Bro! I was gone for ONE second!", 'am_puck', 1.3),
    'tung': ("Wait... is that Tung Tung?", 'am_puck', 1.1),
    'lets': ("LET'S GOOOOO!", 'am_puck', 1.0),
}
k = Kokoro(str(KIT / 'models/kokoro-v1.0.onnx'), str(KIT / 'models/voices-v1.0.bin'))
os.makedirs(HERE / 'vo', exist_ok=True)
durs = {}
for key, (text, voice, speed) in LINES.items():
    s, sr = k.create(text, voice=voice, speed=speed, lang='en-us')
    idx = np.where(np.abs(s) > .01)[0]; s = s[max(0, idx[0] - int(.02 * sr)): idx[-1] + int(.06 * sr)]
    sf.write(HERE / 'vo' / f'{key}.wav', s, sr); durs[key] = round(len(s) / sr, 3)
    print(f'{key:7s} {durs[key]:5.2f}s  {text}')
json.dump(durs, open(HERE / 'vo' / 'vo.json', 'w'), indent=1)
