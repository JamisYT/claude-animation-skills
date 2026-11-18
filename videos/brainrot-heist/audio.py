#!/usr/bin/env python3
"""events.json + vo/ -> audio.wav: loud voice chat, a synthesized scream, chat blips, typing, siren and changing music. numpy only."""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
rng = np.random.default_rng(5)
spec = json.loads((HERE / 'events.json').read_text())
total = spec['total']; S = spec['sections']; n = int((total + .3) * SR)
fx, voice, music = np.zeros(n), np.zeros(n), np.zeros(n)
T = lambda d: np.arange(int(d * SR)) / SR


def lp(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += a * (v - acc); y[i] = acc
    return y


def bp(x, f, q):                 # biquad band-pass
    w = 2 * np.pi * f / SR; al = np.sin(w) / (2 * q); b0, b2, a0, a1, a2 = al, -al, 1 + al, -2 * np.cos(w), 1 - al
    y = np.zeros_like(x); x1 = x2 = y1 = y2 = 0.0
    for i, v in enumerate(x):
        o = (b0 * v + b2 * x2 - a1 * y1 - a2 * y2) / a0; x2, x1, y2, y1 = x1, v, y1, o; y[i] = o
    return y


def env(d, a, dec): t = T(d); return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / dec)
def fm(f, d): return 2 * np.pi * np.cumsum(np.broadcast_to(f, (int(d * SR),))) / SR
def saw(ph): return 2 * ((ph / (2 * np.pi)) % 1) - 1
def sq(ph): return np.sign(np.sin(ph))
def noise(d): return rng.standard_normal(int(d * SR))


def scream():                    # high-pitched "AAAAAH!"
    d = 1.5; t = T(d)
    f0 = 1050 + 450 * np.sin(np.pi * np.minimum(1, t / .5)) * (t < .5) + 450 * (t >= .5) - 250 * np.clip((t - .6) / .9, 0, 1)
    f0 = f0 * (1 + .035 * np.sin(2 * np.pi * 8.5 * t) + .01 * lp(noise(d), .01) * 20)
    src = saw(fm(f0, d)) + .25 * noise(d)
    s = bp(src, 1100, 3) * 1.0 + bp(src, 2700, 4) * .8 + bp(src, 3800, 5) * .4
    s = np.tanh(s * 2.5) * np.minimum(1, t / .04) * np.minimum(1, (d - t) / .25)
    return s * .55
def blip(): return (np.sin(fm(880, .08)) + .5 * np.sin(fm(1320, .08))) * env(.08, .002, .03) * .3
def typing():
    out = np.zeros(int(.45 * SR))
    for i in range(9):
        c = (lp(noise(.03), .6) * .6 + np.sin(fm(1800 + rng.random() * 900, .03)) * .3) * env(.03, .0005, .006); o = int((i * .045 + rng.random() * .015) * SR); out[o:o + len(c)] += c
    return out * .5
def tiptoe(): t = T(.18); return (np.sin(fm(196 * 2 ** (rng.integers(0, 5) / 12), .18)) * np.exp(-t * 30) + .4 * np.sin(fm(392, .18)) * np.exp(-t * 40)) * .35
def charge():
    out = np.zeros(int(1.3 * SR))
    for i in range(10):
        s = np.sin(fm(600 + i * 90, .06)) * env(.06, .002, .03) * .25; o = int(i * .12 * SR); out[o:o + len(s)] += s
    return out
def siren(): t = T(1.6); f = 700 + 300 * np.sin(2 * np.pi * 2.5 * t); return lp(sq(fm(f, 1.6)), .3) * np.minimum(1, t / .05) * np.minimum(1, (1.6 - t) / .2) * .18
def step(): t = T(.08); return lp(noise(.08), .3) * np.exp(-t * 60) * .35 + np.sin(fm(90, .08)) * np.exp(-t * 40) * .3
def pop(): return np.sin(fm(500 + 9000 * T(.09), .09)) * env(.09, .001, .03) * .35
def thud(): return (np.sin(fm(50 + 110 * np.exp(-T(.4) * 25), .4)) + lp(noise(.4), .1) * .8) * env(.4, .001, .1) * .8
def scratch(): t = T(.5); return (lp(noise(.5), .3) * .7 + sq(fm(1600 - 1400 * t / .5, .5)) * .15) * np.minimum(1, (.5 - t) / .1) * .7
def stomp(): t = T(1.0); return np.tanh((np.sin(fm(38 + 50 * np.exp(-t * 8), 1.0)) * 1.6 + lp(noise(1.0), .05) * 1.5 * np.exp(-t * 6)) * 2) * env(1.0, .002, .3) * .8 + np.r_[(np.sin(2 * np.pi * 520 * T(.3)) * np.exp(-T(.3) * 28) * .4), np.zeros(int(.7 * SR))][:int(1.0 * SR)]
def gasp(): t = T(.35); return bp(noise(.35), 1800, 2) * np.sin(np.pi * t / .35) * .5
def windup(): return np.sin(fm(200 + 900 * (T(.3) / .3) ** 2, .3)) * np.minimum(1, T(.3) / .03) * .2
def bonk(): t = T(.6); return np.tanh((np.sin(fm(900 * np.exp(-t * 4) + 200, .6)) * .9 + np.sin(fm(70 + 200 * np.exp(-t * 30), .6)) * 1.2 + lp(noise(.6), .3) * np.exp(-t * 25)) * 1.8) * env(.6, .001, .15) * .7
def slideup(): t = T(.9); return np.sin(fm(400 + 1400 * (t / .9), .9) + 2 * np.sin(2 * np.pi * 7 * t)) * np.minimum(1, t / .03) * np.minimum(1, (.9 - t) / .1) * .22
def ding(): t = T(.9); return (np.sin(2 * np.pi * 2093 * t) + .5 * np.sin(2 * np.pi * 3136 * t)) * env(.9, .002, .25) * .22
def airhorn():
    out = np.zeros(int(1.6 * SR))
    for o, d in [(0, .14), (.18, .14), (.36, .9)]:
        t = T(d); ph = fm(466 * (1 + .01 * np.sin(2 * np.pi * 6 * t)), d)
        s = np.tanh(lp((saw(ph) + .7 * saw(ph * 1.5) + .5 * saw(ph * 2.003)) * np.minimum(1, t / .01) * np.minimum(1, (d - t) / .02), .35) * 2) * .25; i = int(o * SR); out[i:i + len(s)] += s
    return out
def confetti():
    out = np.zeros(int(1.2 * SR))
    for i in range(14): s = pop() * (.3 + rng.random() * .4); o = int(rng.random() * SR); out[o:o + len(s)] += s
    return out
def whoosh(): d = .5; t = T(d); return lp(noise(d), .12) * np.sin(np.pi * t / d) ** 2 * .9
def vineboom(): t = T(1.4); f = 42 + 30 * np.exp(-t * 6); return np.tanh((np.sin(fm(f, 1.4)) + .5 * np.sin(fm(f * 2.01, 1.4)) + .25 * saw(fm(f, 1.4))) * 2.2 * env(1.4, .003, .45)) * .75
def click(): t = T(.05); return np.sin(2 * np.pi * 2200 * t) * env(.05, .0005, .008) * .35


SFX = {k: v for k, v in globals().items() if k in 'scream blip typing tiptoe charge siren step pop thud scratch stomp gasp windup bonk slideup ding airhorn confetti whoosh vineboom click'.split()}


def load_vc(name):
    with wave.open(str(HERE / 'vo' / f'{name}.wav')) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth(); raw = w.readframes(w.getnframes())
    x = np.frombuffer(raw, dtype={2: np.int16, 4: np.int32}[sw]).astype(float) / (2 ** (8 * sw - 1)); x = x.reshape(-1, ch).mean(1)
    pitch = 1.22 if name != 'tung' else 1.12                      # higher, younger, more panicked
    y = np.interp(np.arange(int(len(x) * SR / sr / pitch)) * sr * pitch / SR, np.arange(len(x)), x)
    y = y / (np.abs(y).max() + 1e-9)
    if name in ('tung',): return y * .8
    y = y - lp(y, .04)                                             # thin "headset mic"
    y = np.tanh(y * 5) * .75                                       # clipping from yelling into the mic
    return y


for e in spec['events']:
    i = int(e['t'] * SR)
    if e['type'] == 'vc': s = load_vc(e['id']); buf = voice
    else: s = SFX[e['type']]() * e['gain']; buf = fx
    if e['type'] == 'whoosh': i -= len(s) // 2
    i = max(0, i); j = min(n, i + len(s)); buf[i:j] += s[:j - i]

# music by section: chill -> sneaky pizzicato -> frantic chase -> silence with stomps -> happy
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
def put(t0, s, g):
    i = int(t0 * SR); j = min(n, i + len(s))
    if i < n: music[i:j] += s[:j - i] * g
kick = np.tanh(np.sin(fm(48 + 140 * np.exp(-T(.3) * 32), .3)) * 1.8) * env(.3, .001, .09)
snare = (lp(noise(.2), .6) * .8 + np.sin(fm(190, .2)) * .5) * env(.2, .001, .05)
hat = (noise(.05) - lp(noise(.05), .4)) * env(.05, .0005, .012)
pluck = lambda f, d=.25: (np.sin(fm(f, d)) + .3 * np.sin(fm(2 * f, d))) * env(d, .002, .07)
sqlead = lambda f, d: lp(sq(fm(f, d)), .3) * np.minimum(1, T(d) / .01) * np.minimum(1, (d - T(d)) / .02)
t0 = 0.0
# chill (0 -> sneak): soft plucks
bt = 60 / 110
while t0 < S['sneak']:
    put(t0, pluck(NOTE([64, 67, 71, 67][int(t0 / bt * 2) % 4]), .4), .1); t0 += bt / 2
# sneaky (tiptoe) 110 bpm minor staccato bass
seq = [45, 0, 48, 0, 50, 0, 51, 50, 45, 0, 48, 0, 43, 0, 44, 0]
t0 = S['sneak']; k = 0
while t0 < S['chase']:
    m = seq[k % 16]
    if m: put(t0, pluck(NOTE(m), .2), .35)
    if k % 4 == 2: put(t0, hat, .1)
    t0 += bt / 4; k += 1
# chase 155 bpm
bt = 60 / 155; t0 = S['chase']; k = 0
hook = [76, 76, 74, 76, 79, 76, 74, 72, 74, 74, 72, 74, 76, 74, 72, 71]
while t0 < S['tension'] - .1:
    s16 = k % 16
    if s16 % 4 == 0: put(t0, kick, .5)
    if s16 in (4, 12): put(t0, snare, .35)
    put(t0, hat, .12)
    if s16 % 2 == 0: put(t0, pluck(NOTE([45, 45, 41, 43][(k // 16) % 4]), .2), .4)
    if s16 % 2 == 0: put(t0, sqlead(NOTE(hook[(k // 2) % 16]), bt / 2 * .9), .06)
    t0 += bt / 4; k += 1
# tension: low drone
tt = T(S['win'] - S['tension']); drone = (np.sin(2 * np.pi * 55 * tt) + .5 * np.sin(2 * np.pi * 82.4 * tt)) * np.minimum(1, tt / .5) * .25
put(S['tension'], drone, 1)
# win: happy 128 bpm
bt = 60 / 128; t0 = S['win'] + .1; k = 0
chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]
melody = [72, 74, 76, 79, 76, 74, 72, 74, 76, 76, 74, 72, 74, 0, 79, 0]
while t0 < total - .3:
    s16 = k % 16; ch = chords[(k // 16) % 4]
    if s16 % 4 == 0: put(t0, kick, .5)
    if s16 in (4, 12): put(t0, snare, .3)
    if s16 % 2 == 0: put(t0, hat, .1); put(t0, pluck(NOTE(ch[(k // 2) % 3] + 12), .3), .1)
    if s16 % 2 == 0 and melody[(k // 2) % 16]: put(t0, sqlead(NOTE(melody[(k // 2) % 16]), bt / 2 * .9), .06)
    if s16 % 4 == 0: put(t0, pluck(NOTE(ch[0] - 12), .35), .35)
    t0 += bt / 4; k += 1
ta = np.arange(n) / SR
music *= np.clip((total - ta) / 1.0, 0, 1)
duck = 1 - .6 * np.clip(lp(np.abs(voice)[::64] * 5, .05).repeat(64)[:n], 0, 1)
mix = voice * 1.0 + fx * (.7 + .3 * duck) + music * duck
mix = np.tanh(mix * 1.1) * .9
pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
with wave.open(str(HERE / 'audio.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'audio.wav  {total:.2f} s, {len(spec["events"])} events')
