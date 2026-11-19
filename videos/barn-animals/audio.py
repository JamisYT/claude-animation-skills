#!/usr/bin/env python3
"""events.json + vo/ -> audio.wav: narrator and animal voices over a soft ukulele-and-xylophone tune, with gentle sfx. numpy only."""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
rng = np.random.default_rng(21)
spec = json.loads((HERE / 'events.json').read_text())
total = spec['total']; S = spec['sections']; n = int((total + .3) * SR)
fx, voice, music = np.zeros(n), np.zeros(n), np.zeros(n)
T = lambda d: np.arange(int(d * SR)) / SR


def lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += a * (v - acc); y[i] = acc
    return y


def env(d, a, dec): t = T(d); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def fm(f, d): return 2 * np.pi * np.cumsum(np.broadcast_to(f, (int(d * SR),))) / SR
def noise(d): return rng.standard_normal(int(d * SR))
def pad(s, d): return np.r_[s, np.zeros(max(0, int(d * SR) - len(s)))][:int(d * SR)]


def knock(): t = T(.18); return (np.sin(2 * np.pi * 180 * t) * np.exp(-t * 40) + lp(noise(.18), .3) * np.exp(-t * 80) * .6) * .5
def creak(): d = .6; t = T(d); return lp(np.sign(np.sin(fm(90 + 60 * np.sin(np.pi * t / d), d))) * (rng.random(len(t)) > .5), .2) * np.sin(np.pi * t / d) * .12
def sparkle():
    out = np.zeros(int(1.0 * SR))
    for i, f in enumerate([1568, 1976, 2349, 3136, 2637]): s = np.sin(2 * np.pi * f * T(.4)) * env(.4, .002, .1) * .12; o = int(i * .08 * SR); out[o:o + len(s)] += s
    return out
def hop(): return np.sin(fm(220 + 380 * (T(.16) / .16) ** .6, .16)) * env(.16, .004, .07) * .3
def pop(): return np.sin(fm(500 + 5000 * T(.09), .09)) * env(.09, .001, .03) * .3
def patter():
    out = np.zeros(int(1.1 * SR))
    for i in range(7): s = lp(noise(.05), .4) * env(.05, .001, .012) * .25; o = int(i * .15 * SR); out[o:o + len(s)] += s
    return out
def chimes():
    out = np.zeros(int(2.0 * SR))
    for i, m in enumerate([72, 76, 79, 84, 88, 91]): f = 440 * 2 ** ((m - 69) / 12); s = (np.sin(2 * np.pi * f * T(1.0)) + .3 * np.sin(2 * np.pi * 2 * f * T(1.0))) * env(1.0, .002, .3) * .13; o = int(i * .1 * SR); out[o:o + len(s)] += s
    return out
def confetti():
    out = np.zeros(int(1.2 * SR))
    for i in range(10): s = pop() * (.3 + rng.random() * .4); o = int(rng.random() * SR); out[o:o + len(s)] += s
    return out
def click(): t = T(.05); return np.sin(2 * np.pi * 2200 * t) * env(.05, .0005, .008) * .3


SFX = {k: v for k, v in globals().items() if k in 'knock creak sparkle hop pop patter chimes confetti click'.split()}


def load_vo(name):
    with wave.open(str(HERE / 'vo' / f'{name}.wav')) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth(); raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype={2: np.int16, 4: np.int32}[sw]).astype(float) / (2 ** (8 * sw - 1)); x = x.reshape(-1, ch).mean(1)
    pitch = 1.12 if name.endswith('_snd') else 1.0                     # animal voice a little higher and cuter
    y = np.interp(np.arange(int(len(x) * SR / sr / pitch)) * sr * pitch / SR, np.arange(len(x)), x)
    return y / (np.abs(y).max() + 1e-9) * .85


for e in spec['events']:
    i = int(e['t'] * SR)
    if e['type'] == 'vo': s = load_vo(e['id']); buf = voice
    else: s = SFX[e['type']]() * e['gain']; buf = fx
    i = max(0, i); j = min(n, i + len(s)); buf[i:j] += s[:j - i]

# soft tune: 108 bpm, ukulele strums, xylophone melody, a gentle shaker
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
def put(t0, s, g):
    i = int(t0 * SR); j = min(n, i + len(s))
    if 0 <= i < n: music[i:j] += s[:j - i] * g
uke = lambda f, d=.5: sum((np.sin(fm(f * h, d)) / h) for h in (1, 2, 3)) * env(d, .003, .18)
xylo = lambda f, d=.45: (np.sin(fm(f, d)) + .25 * np.sin(fm(f * 3.9, d))) * env(d, .002, .12)
shaker = lp(noise(.06), .7) - lp(noise(.06), .2)
chords = [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]]
mel = [76, 79, 81, 79, 76, 74, 72, 74, 76, 76, 74, 74, 72, 0, 0, 0]
bt = 60 / 108; k = 0; t0 = 0.0
while t0 < total - .6:
    s8 = k % 8; ch = chords[(k // 8) % 4]
    if s8 in (0, 3, 4, 6):
        for j, m in enumerate(ch): put(t0 + j * .012, uke(NOTE(m - 12 * (j == 0))), .05)
    put(t0, shaker * env(.06, .001, .02), .05)
    m = mel[k % 16]
    if m: put(t0, xylo(NOTE(m)), .08)
    t0 += bt / 2; k += 1
ta = np.arange(n) / SR
music *= np.clip((total - ta) / 1.5, 0, 1) * np.clip(ta / .8, 0, 1)
duck = 1 - .55 * np.clip(lp(np.abs(voice)[::64] * 5, .05).repeat(64)[:n], 0, 1)
mix = voice + fx * (.7 + .3 * duck) + music * duck
mix = np.tanh(mix * 1.05) * .85
pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
with wave.open(str(HERE / 'audio.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'audio.wav  {total:.2f} s, {len(spec["events"])} events')
