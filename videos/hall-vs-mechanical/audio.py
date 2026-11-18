#!/usr/bin/env python3
"""events.json -> audio.wav: synthesized switch sounds, whooshes and a quiet beat. numpy only."""
import json
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
rng = np.random.default_rng(7)
spec = json.loads((HERE / 'events.json').read_text())
total = spec['total']
n = int((total + 0.5) * SR)
fx = np.zeros(n)
music = np.zeros(n)


def env(length, attack, decay):
    t = np.arange(int(length * SR)) / SR
    return np.minimum(1, t / max(attack, 1e-4)) * np.exp(-t / decay), t


def lowpass(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc); y[i] = acc
    return y


def click():          # clicky mechanical: two bright transients
    e, t = env(.06, .0005, .006)
    s = (rng.standard_normal(len(t)) * .6 + np.sin(2 * np.pi * 3800 * t)) * e
    e2, t2 = env(.05, .0005, .009)
    s2 = (np.sin(2 * np.pi * 2400 * t2) * .8 + rng.standard_normal(len(t2)) * .3) * e2
    out = np.zeros(int(.09 * SR)); out[:len(s)] += s; o = int(.016 * SR); out[o:o + len(s2)] += .7 * s2
    return out * .55


def clack():          # bottom-out
    e, t = env(.12, .001, .025)
    return (np.sin(2 * np.pi * 190 * t) + .4 * lowpass(rng.standard_normal(len(t)), .2)) * e * .5


def hall():           # smooth magnetic thock + a soft rising zip
    e, t = env(.16, .001, .035)
    thock = np.sin(2 * np.pi * (140 + 60 * np.exp(-t * 40)) * t) * e
    e2, t2 = env(.12, .01, .04)
    zip_ = np.sin(2 * np.pi * (700 * t2 + 2500 * t2 ** 2)) * e2 * .25
    out = np.zeros(len(t)); out += thock; out[:len(zip_)] += zip_
    return out * .6


def whoosh():
    L = .4; t = np.arange(int(L * SR)) / SR
    shape = np.sin(np.pi * (t / L) ** .7) ** 2
    return lowpass(rng.standard_normal(len(t)), .12) * shape * .7


def boom():
    e, t = env(.9, .002, .25)
    f = 45 + 80 * np.exp(-t * 9)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + .3 * lowpass(rng.standard_normal(len(t)), .05) * np.exp(-t * 12)) * e * .9


def drop():
    e, t = env(.2, .001, .05)
    return np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 30)) * t) * e * .6


def pop():
    e, t = env(.08, .001, .025)
    return np.sin(2 * np.pi * np.cumsum(950 - 3000 * t) / SR) * e * .35


def tick():
    e, t = env(.04, .0005, .006)
    return np.sin(2 * np.pi * 1800 * t) * e * .3


SOUNDS = {k: v() for k, v in dict(click=click, clack=clack, hall=hall, whoosh=whoosh, boom=boom, drop=drop, pop=pop, tick=tick).items()}
for e in spec['events']:
    s = SOUNDS[e['type']] * e['gain']
    i = int(e['t'] * SR)
    if e['type'] == 'whoosh':
        i -= len(s) // 2
    i = max(0, i); j = min(n, i + len(s)); fx[i:j] += s[:j - i]

# quiet beat: 112 bpm, Am - F - C - G pad, kick on beats, hats on off-beats
bpm = 112; beat = 60 / bpm
t_all = np.arange(n) / SR
chords = [[220, 261.63, 329.63], [174.61, 220, 261.63], [196 * 2 / 1.5 * .75 * 2, 261.63, 329.63], [196, 246.94, 293.66]]
chords[2] = [130.81 * 2, 329.63, 392]
bar = 4 * beat
for ci in range(int(total / bar) + 1):
    a = int(ci * bar * SR); b = min(n, int((ci + 1) * bar * SR))
    if a >= n: break
    tt = t_all[a:b] - ci * bar
    shape = np.minimum(1, tt / .3) * np.minimum(1, (bar - tt) / .3)
    for f in chords[ci % 4]:
        music[a:b] += (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2.003 * tt)) * shape * .05
kick_e, kt = env(.3, .001, .08)
kick = np.sin(2 * np.pi * np.cumsum(50 + 110 * np.exp(-kt * 30)) / SR) * kick_e * .55
hat_e, ht = env(.04, .0005, .008)
hat = (rng.standard_normal(len(ht)) - lowpass(rng.standard_normal(len(ht)), .3)) * hat_e * .08
k = 0
while k * beat < total - .5:
    i = int(k * beat * SR)
    if k * beat > 1.0:                      # drums come in on the VS hit
        music[i:i + len(kick)] += kick[:max(0, min(len(kick), n - i))]
        h = int((k + .5) * beat * SR); music[h:h + len(hat)] += hat[:max(0, min(len(hat), n - h))]
    k += 1
fade = np.clip((total - t_all) / 1.2, 0, 1)
mix = fx + music * fade
mix = np.tanh(mix * 1.1) * .9
st = np.stack([mix, mix], 1)
pcm = (st * 32767).astype(np.int16)
with wave.open(str(HERE / 'audio.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'audio.wav  {total:.2f} s, {len(spec["events"])} sound events')
