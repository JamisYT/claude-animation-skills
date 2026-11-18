#!/usr/bin/env python3
"""events.json -> audio.wav: voices, cartoon sound effects and a bouncy beat (numpy only)."""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
rng = np.random.default_rng(3)
spec = json.loads((HERE / 'events.json').read_text())
total = spec['total']; n = int((total + .3) * SR)
fx, voice, music = np.zeros(n), np.zeros(n), np.zeros(n)
T = lambda d: np.arange(int(d * SR)) / SR


def lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += a * (v - acc); y[i] = acc
    return y


def sweep(f0, f1, d, wave_='sine', curve=1.0):
    t = T(d); f = f0 + (f1 - f0) * (t / d) ** curve; ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if wave_ == 'sine' else np.sign(np.sin(ph)) * .6 if wave_ == 'square' else 2 * np.abs(2 * ((ph / (2 * np.pi)) % 1) - 1) - 1


def envd(d, a, dec): t = T(d); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)


def boing(): return sweep(180, 700, .22, curve=.6) * envd(.22, .005, .12) * .45
def land(): t = T(.15); return (np.sin(2 * np.pi * (60 + 80 * np.exp(-t * 40)) * t) * envd(.15, .002, .04) + lp(rng.standard_normal(len(t)), .15) * envd(.15, .001, .02) * .6) * .6
def slide(): t = T(1.1); f = 900 + 500 * np.sin(2 * np.pi * 2.2 * t) * (1 - t / 1.1) - 300 * t; return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / .03) * np.minimum(1, (1.1 - t) / .1) * .22
def poof(): d = .5; x = lp(rng.standard_normal(int(d * SR)), .08); return x * envd(d, .01, .12) * 1.6
def sparkle():
    out = np.zeros(int(.9 * SR))
    for i, f in enumerate([1568, 1976, 2349, 3136, 2637, 3951]):
        s = np.sin(2 * np.pi * f * T(.35)) * envd(.35, .002, .08) * .16; o = int(i * .09 * SR); out[o:o + len(s)] += s
    return out
def scratch(): t = T(.45); f = 300 + 1600 * np.abs(np.sin(2 * np.pi * 3.3 * t)); return (lp(rng.standard_normal(len(t)), .3) * .6 + sweep(1600, 200, .45, 'square') * .2) * np.minimum(1, (.45 - t) / .1) * .7
def buzzer(): t = T(.6); return (np.sign(np.sin(2 * np.pi * 110 * t)) + np.sign(np.sin(2 * np.pi * 116 * t))) * .14 * np.minimum(1, (.6 - t) / .05)
def stamp(): t = T(.3); return (np.sin(2 * np.pi * (50 + 60 * np.exp(-t * 30)) * t) + lp(rng.standard_normal(len(t)), .3) * .5 * np.exp(-t * 40)) * envd(.3, .001, .08) * .8
def click(): t = T(.05); return np.sin(2 * np.pi * 2200 * t) * envd(.05, .0005, .008) * .35
def pop(): return sweep(500, 1300, .09) * envd(.09, .001, .03) * .35
def ding(): t = T(.8); return (np.sin(2 * np.pi * 1318 * t) + .5 * np.sin(2 * np.pi * 1975 * t)) * envd(.8, .002, .25) * .25
def whoosh(): d = .45; t = T(d); return lp(rng.standard_normal(len(t)), .1) * np.sin(np.pi * t / d) ** 2 * .7
def fanfare():
    out = np.zeros(int(1.6 * SR)); notes = [(523, 0, .14), (659, .14, .14), (784, .28, .14), (1047, .42, .9)]
    for f, o, d in notes:
        t = T(d + .2); s = sum(np.sin(2 * np.pi * f * h * t) / h for h in (1, 2, 3, 4)) * np.minimum(1, t / .01) * np.exp(-t / (d * .9 + .1)) * .18
        i = int(o * SR); out[i:i + len(s)] += s
    return out
def confetti():
    out = np.zeros(int(1.2 * SR))
    for i in range(12):
        s = pop() * (.4 + rng.random() * .4); o = int(rng.random() * 1.0 * SR); out[o:o + len(s)] += s
    return out


SFX = {k: f() for k, f in dict(boing=boing, land=land, slide=slide, poof=poof, sparkle=sparkle, scratch=scratch, buzzer=buzzer, stamp=stamp,
                               click=click, pop=pop, ding=ding, whoosh=whoosh, fanfare=fanfare, confetti=confetti).items()}


def load_vo(name):
    with wave.open(str(HERE / 'vo' / f'{name}.wav')) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth(); raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype={2: np.int16, 4: np.int32}[sw]).astype(float) / (2 ** (8 * sw - 1))
    x = x.reshape(-1, ch).mean(1)
    return np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)


for e in spec['events']:
    i = int(e['t'] * SR)
    if e['type'] == 'vo':
        s = load_vo(e['id']); s = s / (np.abs(s).max() + 1e-9) * .9; buf = voice
    else:
        s = SFX[e['type']] * e['gain']; buf = fx
        if e['type'] == 'whoosh': i -= len(s) // 2
    i = max(0, i); j = min(n, i + len(s)); buf[i:j] += s[:j - i]

# bouncy music: 126 bpm, C - G - Am - F, plucked arpeggio, bass, kick and clap
bpm = 126; beat = 60 / bpm; eighth = beat / 2
chords = [[261.6, 329.6, 392.0], [196.0, 246.9, 293.7], [220.0, 261.6, 329.6], [174.6, 220.0, 261.6]]
pl = lambda f, d: (np.sin(2 * np.pi * f * T(d)) + .35 * np.sin(4 * np.pi * f * T(d))) * envd(d, .003, .09)
kick = np.sin(2 * np.pi * np.cumsum(45 + 120 * np.exp(-T(.25) * 35)) / SR) * envd(.25, .001, .07)
clap = lp(rng.standard_normal(int(.12 * SR)), .5) * envd(.12, .001, .03)
k = 0
while k * eighth < total:
    t0 = k * eighth; bar = int(t0 / (4 * beat)); ch = chords[bar % 4]
    i = int(t0 * SR)
    def put(s, g):
        j = min(n, i + len(s)); music[i:j] += s[:j - i] * g
    put(pl(ch[k % 3] * 2, .3), .07)
    if k % 2 == 0: put(pl(ch[0] / 2, .35), .12)
    if k % 4 == 0: put(kick, .35)
    if k % 4 == 2: put(clap, .18)
    k += 1
tt = np.arange(n) / SR
gate = np.ones(n)
for a, b in spec.get('music_off', []):
    gate *= 1 - np.clip((tt - a) / .05, 0, 1) * np.clip((b - tt) / .3, 0, 1)
gate *= np.clip((total - tt) / 1.0, 0, 1)
duck = 1 - .6 * np.clip(lp(np.abs(voice)[::64] * 6, .05).repeat(64)[:n], 0, 1)
mix = voice + fx * (.6 + .4 * duck) + music * gate * duck
mix = np.tanh(mix * 1.1) * .9
pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
with wave.open(str(HERE / 'audio.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'audio.wav  {total:.2f} s, {len(spec["events"])} events')
