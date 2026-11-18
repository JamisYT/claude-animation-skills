#!/usr/bin/env python3
"""events.json -> audio.wav: a beat that builds with every bigger brainrot, a character sound for each, and a giant finale. numpy only."""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
rng = np.random.default_rng(9)
spec = json.loads((HERE / 'events.json').read_text())
total = spec['total']; S = spec['sections']; n = int((total + .3) * SR)
fx, music = np.zeros(n), np.zeros(n)
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
def cat(*parts): return np.concatenate(parts)


def whoosh(): d = .5; t = T(d); return lp(noise(d), .12) * np.sin(np.pi * t / d) ** 2 * .8
def zoom(): d = .8; t = T(d); return lp(noise(d), .1) * np.sin(np.pi * t / d) ** 2 * .6 + np.sin(fm(200 + 500 * t / d, d)) * np.sin(np.pi * t / d) ** 2 * .08
def vineboom(): t = T(1.4); f = 42 + 30 * np.exp(-t * 6); return np.tanh((np.sin(fm(f, 1.4)) + .5 * np.sin(fm(f * 2.01, 1.4)) + .25 * saw(fm(f, 1.4))) * 2.2 * env(1.4, .003, .45)) * .75
def ding(i): f = 523.25 * 2 ** ([0, 2, 4, 5, 7, 9, 11, 12, 14][int(i) % 9] / 12); t = T(.8); return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * 2 * f * t)) * env(.8, .002, .2) * .22
def pop(): return np.sin(fm(500 + 9000 * T(.09), .09)) * env(.09, .001, .03) * .35
def click(): t = T(.05); return np.sin(2 * np.pi * 2200 * t) * env(.05, .0005, .008) * .35
def chimp():      # "ooh ooh aah!"
    out = []
    for f0, d in [(500, .14), (520, .14), (700, .32)]:
        t = T(d); f = f0 * (1 + .3 * np.sin(np.pi * t / d)); s = saw(fm(f, d)); s = lp(s, .25) * np.sin(np.pi * t / d) ** .6; out += [s * .3, np.zeros(int(.04 * SR))]
    return cat(*out)
def musicbox():
    out = np.zeros(int(1.4 * SR))
    for i, m in enumerate([84, 88, 91, 96, 91, 88]):
        f = 440 * 2 ** ((m - 69) / 12); s = (np.sin(2 * np.pi * f * T(.5)) + .3 * np.sin(2 * np.pi * 3 * f * T(.5))) * env(.5, .001, .15) * .15; o = int(i * .14 * SR); out[o:o + len(s)] += s
    return out
def tung():
    one = lambda: (np.sin(2 * np.pi * 520 * T(.3)) * np.exp(-T(.3) * 28) + .5 * np.sin(2 * np.pi * 1180 * T(.3)) * np.exp(-T(.3) * 45) + lp(noise(.3), .4) * np.exp(-T(.3) * 120) * .8) * .5
    out = np.zeros(int(1.0 * SR))
    for i in range(3): s = one(); o = int(i * .22 * SR); out[o:o + len(s)] += s
    return out
def honk(): t = T(.5); return np.tanh(lp(sq(fm(415, .5)) + sq(fm(494, .5)), .3) * 2) * np.minimum(1, t / .01) * np.minimum(1, (.5 - t) / .03) * .18
def trumpet():    # elephant
    d = .9; t = T(d); f = 300 + 500 * np.sin(np.pi * np.minimum(1, t / .5)) ** 2 * (t < .5) + 800 * (t >= .5) - 300 * np.clip((t - .5) / .4, 0, 1)
    s = saw(fm(f * (1 + .02 * np.sin(2 * np.pi * 9 * t)), d)) + .3 * noise(d); s = lp(s, .3) - lp(s, .03)
    return np.tanh(s * 2) * np.minimum(1, t / .05) * np.minimum(1, (d - t) / .2) * .3
def squeak(): t = T(.16); return np.sin(fm(1800 + 1500 * t / .16, .16)) * np.sin(np.pi * t / .16) * .22
def plane():
    d = 1.6; t = T(d); eng = lp(saw(fm(70 + 6 * np.sin(2 * np.pi * 9 * t), d)), .2) * (.6 + .4 * np.sin(2 * np.pi * 18 * t)) * .35
    whistle = np.sin(fm(1800 - 1000 * t / d, d)) * .08 * np.clip((t - .4) / .3, 0, 1)
    return (eng + whistle) * np.minimum(1, t / .1) * np.minimum(1, (d - t) / .3)
def rumble(): d = 2.6; t = T(d); return lp(noise(d), .02) * 3 * (t / d) ** 1.5 * np.minimum(1, (d - t) / .05) + np.sin(fm(30 + 10 * t / d, d)) * .3 * (t / d)
def horn():       # the giant "BWAAAM"
    d = 2.6; t = T(d); s = sum(saw(fm(f * (1 + .003 * np.sin(2 * np.pi * 3 * t)), d)) for f in (55, 55.4, 82.4, 110.3))
    return np.tanh(lp(s, .06) * 3) * np.minimum(1, t / .04) * np.exp(-t / 1.6) * .6


SFX = dict(whoosh=whoosh, zoom=zoom, vineboom=vineboom, pop=pop, click=click, chimp=chimp, musicbox=musicbox, tung=tung, honk=honk,
           trumpet=trumpet, squeak=squeak, plane=plane, rumble=rumble, horn=horn)
for e in spec['events']:
    s = (ding(e['id']) if e['type'] == 'ding' else SFX[e['type']]()) * e['gain']
    i = int(e['t'] * SR)
    if e['type'] in ('whoosh', 'zoom'): i -= len(s) // 3
    i = max(0, i); j = min(n, i + len(s)); fx[i:j] += s[:j - i]

# music: 120 bpm, layers come in as the sizes grow; silence for the rise; full power after the giant
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
def put(t0, s, g):
    i = int(t0 * SR); j = min(n, i + len(s))
    if 0 <= i < n: music[i:j] += s[:j - i] * g
kick = np.tanh(np.sin(fm(48 + 140 * np.exp(-T(.3) * 32), .3)) * 1.8) * env(.3, .001, .09)
snare = (lp(noise(.2), .6) * .8 + np.sin(fm(190, .2)) * .5) * env(.2, .001, .05)
hat = (noise(.05) - lp(noise(.05), .4)) * env(.05, .0005, .012)
pluck = lambda f, d=.3: (np.sin(fm(f, d)) + .3 * np.sin(fm(2 * f, d))) * env(d, .002, .08)
lead = lambda f, d: lp(sq(fm(f, d)), .3) * np.minimum(1, T(d) / .01) * np.minimum(1, (d - T(d)) / .02)
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
melody = [76, 0, 76, 79, 76, 74, 72, 0, 74, 0, 74, 76, 74, 72, 71, 0]
items = S['items']
bt = 60 / 120; k = 0; t0 = 0.0
while t0 < total - .4:
    quiet = S['reveal'] <= t0 < S['boom']
    level = sum(1 for x in items if t0 >= x) + (6 if t0 >= S['boom'] else 0)
    s16 = k % 16; ch = chords[(k // 16) % 4]
    if not quiet:
        if s16 % 2 == 0: put(t0, pluck(NOTE(ch[(k // 2) % 3] + 12)), .09)
        if level >= 2 and s16 % 4 == 0: put(t0, kick, .45)
        if level >= 3: put(t0, hat, .1 if s16 % 2 == 0 else .05)
        if level >= 4 and s16 % 4 == 0: put(t0, pluck(NOTE(ch[0] - 12), .4), .35)
        if level >= 5 and s16 in (4, 12): put(t0, snare, .3)
        if level >= 7 and s16 % 2 == 0 and melody[(k // 2) % 16]: put(t0, lead(NOTE(melody[(k // 2) % 16]), bt / 2 * .9), .05)
    t0 += bt / 4; k += 1
ta = np.arange(n) / SR
music *= np.clip((total - ta) / 1.0, 0, 1)
mix = fx + music
mix = np.tanh(mix * 1.1) * .9
pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
with wave.open(str(HERE / 'audio.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'audio.wav  {total:.2f} s, {len(spec["events"])} sfx')
