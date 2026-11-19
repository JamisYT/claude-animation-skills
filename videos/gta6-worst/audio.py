#!/usr/bin/env python3
"""events.json + vo/ -> audio.wav: narration over a synthwave beat, with punchy sound effects. numpy only."""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
rng = np.random.default_rng(13)
spec = json.loads((HERE / 'events.json').read_text())
total = spec['total']; n = int((total + .3) * SR)
fx, voice, music = np.zeros(n), np.zeros(n), np.zeros(n)
T = lambda d: np.arange(int(d * SR)) / SR


def lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += a * (v - acc); y[i] = acc
    return y


def env(d, a, dec): t = T(d); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def fm(f, d): return 2 * np.pi * np.cumsum(np.broadcast_to(f, (int(d * SR),))) / SR
def saw(ph): return 2 * ((ph / (2 * np.pi)) % 1) - 1
def sq(ph): return np.sign(np.sin(ph))
def noise(d): return rng.standard_normal(int(d * SR))


def impact(): t = T(.7); return np.tanh((np.sin(fm(45 + 120 * np.exp(-t * 25), .7)) * 1.5 + lp(noise(.7), .2) * np.exp(-t * 20)) * 2) * env(.7, .001, .18) * .55
def glitch():
    d = .25; t = T(d); s = sq(fm(200 + 1800 * (rng.random(len(t)) > .97).cumsum() % 7 * 150, d)) * .15 + (noise(d) * (np.sin(2 * np.pi * 40 * t) > 0)) * .2
    return s * np.minimum(1, (d - t) / .05)
def ding(): t = T(1.0); return (np.sin(2 * np.pi * 1046 * t) + .5 * np.sin(2 * np.pi * 1568 * t)) * env(1.0, .002, .3) * .25
def scratch(): t = T(.5); return (lp(noise(.5), .3) * .7 + sq(fm(1600 - 1400 * t / .5, .5)) * .15) * np.minimum(1, (.5 - t) / .1) * .7
def boom(): t = T(1.4); f = 42 + 30 * np.exp(-t * 6); return np.tanh((np.sin(fm(f, 1.4)) + .5 * np.sin(fm(f * 2.01, 1.4)) + .25 * saw(fm(f, 1.4))) * 2.2 * env(1.4, .003, .45)) * .7
def tick():
    out = np.zeros(int(2.0 * SR))
    for i in range(8): s = np.sin(2 * np.pi * (2000 if i % 2 else 1500) * T(.03)) * env(.03, .0005, .006) * .25; o = int(i * .25 * SR); out[o:o + len(s)] += s
    return out
def slam(): t = T(.5); return (lp(noise(.5), .15) * np.exp(-t * 14) + np.sin(fm(60, .5)) * np.exp(-t * 10)) * .6
def stamp(): t = T(.3); return (np.sin(fm(50 + 60 * np.exp(-T(.3) * 30), .3)) + lp(noise(.3), .3) * .5 * np.exp(-t * 40)) * env(.3, .001, .08) * .8
def gunmiss():
    t = T(.6); shot = (lp(noise(.6), .5) * np.exp(-t * 30) + np.sin(fm(120 * np.exp(-t * 20) + 60, .6)) * np.exp(-t * 18)) * .45
    ric = np.r_[np.zeros(int(.12 * SR)), np.sin(fm(2400 - 1400 * T(.45) / .45, .45)) * env(.45, .005, .15) * .15, np.zeros(len(t))][:len(t)]
    return shot + ric
def register():
    out = np.zeros(int(1.0 * SR)); out[:int(.06 * SR)] += lp(noise(.06), .5) * .4
    for i, f in enumerate([2093, 2637]): s = np.sin(2 * np.pi * f * T(.7)) * env(.7, .002, .2) * .22; o = int((.08 + i * .08) * SR); out[o:o + len(s)] += s
    return out
def buzzer(): t = T(.6); return (sq(fm(110, .6)) + sq(fm(116, .6))) * .13 * np.minimum(1, (.6 - t) / .05)
def pop(): return np.sin(fm(500 + 9000 * T(.09), .09)) * env(.09, .001, .03) * .35
def powerdown(): t = T(1.0); return saw(fm(800 * np.exp(-t * 3) + 40, 1.0)) * np.minimum(1, (1 - t) / .2) * .18
def lock(): t = T(.15); return (np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 80) + lp(noise(.15), .5) * np.exp(-t * 60) * .5) * .4
def riser(): d = 1.5; t = T(d); return lp(noise(d), .2) * (t / d) ** 2 * .5 + np.sin(fm(200 + 800 * (t / d) ** 2, d)) * (t / d) * .06
def click(): t = T(.05); return np.sin(2 * np.pi * 2200 * t) * env(.05, .0005, .008) * .35


SFX = {k: v for k, v in globals().items() if k in 'impact glitch ding scratch boom tick slam stamp gunmiss register buzzer pop powerdown lock riser click'.split()}


def load_vo(i):
    with wave.open(str(HERE / 'vo' / f'line_{i:02d}.wav')) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth(); raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype={2: np.int16, 4: np.int32}[sw]).astype(float) / (2 ** (8 * sw - 1)); x = x.reshape(-1, ch).mean(1)
    y = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    return y / (np.abs(y).max() + 1e-9) * .9


for e in spec['events']:
    i = int(e['t'] * SR)
    if e['type'] == 'vo': s = load_vo(e['idx']); buf = voice
    else: s = SFX[e['type']]() * e['gain']; buf = fx
    i = max(0, i); j = min(n, i + len(s)); buf[i:j] += s[:j - i]

# synthwave: 100 bpm, gated snare, arpeggio, warm pad, octave bass
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
def put(t0, s, g):
    i = int(t0 * SR); j = min(n, i + len(s))
    if 0 <= i < n: music[i:j] += s[:j - i] * g
bt = 60 / 100
kick = np.tanh(np.sin(fm(45 + 130 * np.exp(-T(.35) * 28), .35)) * 2) * env(.35, .001, .12)
snare = (lp(noise(.25), .5) * 1.0 + np.sin(fm(180, .25)) * .4) * (T(.25) < .18) * env(.25, .001, .12)
hat = (noise(.05) - lp(noise(.05), .4)) * env(.05, .0005, .015)
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
k = 0; t0 = 0.0
while t0 < total - .5:
    s16 = k % 16; ch = chords[(k // 16) % 4]
    if s16 % 4 == 0: put(t0, kick, .5)
    if s16 in (4, 12): put(t0, snare, .3)
    if s16 % 2 == 1: put(t0, hat, .1)
    arp = ch[[0, 1, 2, 1][s16 % 4]] + 12; put(t0, lp(saw(fm(NOTE(arp), bt / 4 * .9)), .2) * env(bt / 4 * .9, .002, .08), .07)
    if s16 % 2 == 0: put(t0, lp(saw(fm(NOTE(ch[0] - 24 + (12 if s16 % 4 == 2 else 0)), bt / 2 * .9)), .1) * env(bt / 2 * .9, .003, .15), .3)
    if s16 == 0:
        d = bt * 4; tt = T(d); pad = sum(lp(saw(fm(NOTE(m) * (1 + .003 * j), d)), .05) for j, m in enumerate(ch)) * np.minimum(1, tt / .3) * np.minimum(1, (d - tt) / .3)
        put(t0, pad, .05)
    t0 += bt / 4; k += 1
ta = np.arange(n) / SR
music *= np.clip((total - ta) / 1.2, 0, 1)
duck = 1 - .6 * np.clip(lp(np.abs(voice)[::64] * 5, .05).repeat(64)[:n], 0, 1)
mix = voice + fx * (.6 + .4 * duck) + music * duck
mix = np.tanh(mix * 1.1) * .9
pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
with wave.open(str(HERE / 'audio.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'audio.wav  {total:.2f} s, {len(spec["events"])} events')
