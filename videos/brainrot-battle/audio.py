#!/usr/bin/env python3
"""events.json -> audio.wav: a punchy 140 bpm beat with a catchy lead, plus cartoon sound effects. No voice. numpy only."""
import json, wave
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
SR = 48000
rng = np.random.default_rng(11)
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


# ---------------------------------------------------------------- sound effects
def tung():      # hollow wooden knock
    t = T(.35); return (np.sin(2 * np.pi * 520 * t) * np.exp(-t * 28) + .6 * np.sin(2 * np.pi * 1180 * t) * np.exp(-t * 45) + .5 * np.sin(2 * np.pi * (140 + 90 * np.exp(-t * 30)) * t) * np.exp(-t * 14)
                    + lp(noise(.35), .4) * np.exp(-t * 120) * .8) * .55
def thud(): t = T(.4); return (np.sin(fm(50 + 110 * np.exp(-T(.4) * 25), .4)) + lp(noise(.4), .1) * .8) * env(.4, .001, .1) * .8
def vineboom():
    t = T(1.4); f = 42 + 30 * np.exp(-t * 6); s = np.sin(fm(f, 1.4)) + .5 * np.sin(fm(f * 2.01, 1.4)) + .25 * saw(fm(f, 1.4))
    return np.tanh(s * 2.2 * env(1.4, .003, .45)) * .75
def whoosh(): d = .5; t = T(d); return lp(noise(d), .12) * np.sin(np.pi * t / d) ** 2 * .9
def fall(): return np.sin(fm(1500 - 1100 * T(.5) / .5, .5)) * env(.5, .01, .4) * .18
def airhorn():
    out = np.zeros(int(1.6 * SR))
    for o, d in [(0, .14), (.18, .14), (.36, .9)]:
        t = T(d); ph = fm(466 * (1 + .01 * np.sin(2 * np.pi * 6 * t)), d)
        s = (saw(ph) + .7 * saw(ph * 1.5) + .5 * saw(ph * 2.003)) * np.minimum(1, t / .01) * np.minimum(1, (d - t) / .02)
        s = np.tanh(lp(s, .35) * 2) * .25; i = int(o * SR); out[i:i + len(s)] += s
    return out
def bell():
    t = T(1.2); return sum(np.sin(2 * np.pi * f * t) * a for f, a in [(880, 1), (2210, .5), (3520, .3)]) * env(1.2, .002, .35) * .22 + np.r_[np.zeros(int(.2 * SR)), (sum(np.sin(2 * np.pi * f * T(1.0)) * a for f, a in [(880, 1), (2210, .5)]) * env(1.0, .002, .3) * .2)][:int(1.2 * SR)]
def windup(): return np.sin(fm(200 + 900 * (T(.55) / .55) ** 2, .55)) * np.minimum(1, T(.55) / .05) * .2
def slideup(): t = T(.9); return np.sin(fm(400 + 1400 * (t / .9), .9) + 2 * np.sin(2 * np.pi * 7 * t)) * np.minimum(1, t / .03) * np.minimum(1, (.9 - t) / .1) * .22
def splat(): t = T(.4); return (lp(noise(.4), .25) * env(.4, .001, .07) + np.sin(fm(300 - 200 * t / .4, .4)) * env(.4, .002, .08)) * .7
def tweet():
    out = np.zeros(int(1.0 * SR))
    for i in range(5):
        s = np.sin(fm(2600 + 900 * np.sin(np.pi * T(.12) / .12), .12)) * env(.12, .005, .05) * .14; o = int(i * .18 * SR); out[o:o + len(s)] += s
    return out
def squeak(): t = T(.14); return np.sin(fm(1800 + 1500 * t / .14, .14)) * np.sin(np.pi * t / .14) * .2
def spin(): t = T(1.1); f = 300 + 800 * (t / 1.1); return lp(noise(1.1), .2) * (.5 + .5 * np.sin(2 * np.pi * (4 + 20 * t) * t)) * np.minimum(1, t / .2) * np.minimum(1, (1.1 - t) / .1) * .5 + np.sin(fm(f, 1.1)) * .06
def hit(): t = T(.5); return np.tanh((np.sin(fm(70 + 200 * np.exp(-t * 30), .5)) + lp(noise(.5), .35) * np.exp(-t * 18)) * 2.5) * env(.5, .001, .12) * .8
def bonk(): t = T(.5); return (np.sin(fm(900 * np.exp(-t * 4) + 200, .5)) * .8 + np.sin(fm(1800 * np.exp(-t * 4) + 400, .5)) * .3) * env(.5, .001, .12) * .45
def pop(): return np.sin(fm(500 + 9000 * T(.09), .09)) * env(.09, .001, .03) * .35
def scratch(): t = T(.5); return (lp(noise(.5), .3) * .7 + sq(fm(1600 - 1400 * t / .5, .5)) * .15) * np.minimum(1, (.5 - t) / .1) * .7
def heartbeat():
    out = np.zeros(int(.6 * SR))
    for o, a in [(0, 1), (.17, .7)]:
        s = np.sin(fm(55 + 30 * np.exp(-T(.25) * 20), .25)) * env(.25, .002, .06) * a; i = int(o * SR); out[i:i + len(s)] += s
    return out * .9
def explode(): d = 1.6; t = T(d); return np.tanh((lp(noise(d), .08) * 3 + np.sin(fm(40 + 60 * np.exp(-t * 5), d)) * 1.5) * env(d, .002, .4)) * .9
def womp():
    out = np.zeros(int(2.0 * SR))
    for i, (f, d) in enumerate([(311, .35), (294, .35), (277, .35), (262, .9)]):
        t = T(d); s = saw(fm(f * (1 + .02 * np.sin(2 * np.pi * 5 * t * (i == 3))), d)); s = lp(s, .12) * np.minimum(1, t / .02) * np.minimum(1, (d - t) / .05) * .5
        o = int(sum(x[1] for x in [(311, .35), (294, .35), (277, .35)][:i]) * SR); out[o:o + len(s)] += s
    return out
def boing(): t = T(.5); return np.sin(fm(200 + 300 * np.abs(np.sin(2 * np.pi * 6 * t)) * np.exp(-t * 3), .5)) * env(.5, .005, .25) * .45
def click(): t = T(.05); return np.sin(2 * np.pi * 2200 * t) * env(.05, .0005, .008) * .35
def confetti():
    out = np.zeros(int(1.2 * SR))
    for i in range(14):
        s = pop() * (.3 + rng.random() * .4); o = int(rng.random() * SR); out[o:o + len(s)] += s
    return out


SFX = {k: v() for k, v in dict(tung=tung, thud=thud, vineboom=vineboom, whoosh=whoosh, fall=fall, airhorn=airhorn, bell=bell, windup=windup, slideup=slideup,
                               splat=splat, tweet=tweet, squeak=squeak, spin=spin, hit=hit, bonk=bonk, pop=pop, scratch=scratch, heartbeat=heartbeat,
                               explode=explode, womp=womp, boing=boing, click=click, confetti=confetti).items()}
for e in spec['events']:
    s = SFX[e['type']] * e['gain']; i = int(e['t'] * SR)
    if e['type'] == 'whoosh': i -= len(s) // 2
    i = max(0, i); j = min(n, i + len(s)); fx[i:j] += s[:j - i]

# ---------------------------------------------------------------- music
bpm = 140; beat = 60 / bpm; st = beat / 4
def put(buf, t0, s, g=1.0):
    i = int(t0 * SR)
    if i >= n: return
    j = min(n, i + len(s)); buf[i:j] += s[:j - i] * g
kick = np.tanh(np.sin(fm(48 + 140 * np.exp(-T(.3) * 32), .3)) * 1.8) * env(.3, .001, .09)
snare = (lp(noise(.2), .6) * .8 + np.sin(fm(190, .2)) * .5) * env(.2, .001, .05)
hat = (noise(.05) - lp(noise(.05), .4)) * env(.05, .0005, .012)
wood = lambda f: np.sin(2 * np.pi * f * T(.12)) * env(.12, .001, .025)
def bassnote(f, d): t = T(d); return lp(saw(fm(f, d)), .18) * np.minimum(1, t / .005) * np.exp(-t * 3) * np.minimum(1, (d - t) / .01)
def lead(f, d, kind):
    t = T(d)
    if kind == 'sq': s = lp(sq(fm(f, d)) * .6 + saw(fm(f * 1.005, d)) * .4, .35)
    else: s = np.sin(fm(f * (1 + .012 * np.sin(2 * np.pi * 6 * t)), d)) + .25 * np.sin(fm(2 * f, d))      # flute-ish for the shark
    return s * np.minimum(1, t / .01) * np.minimum(1, (d - t) / .03)
NOTE = lambda m: 440 * 2 ** ((m - 69) / 12)
prog = [57, 53, 48, 55]                        # A minor, F, C, G (bass roots, midi)
# 2-bar hook in 16ths: (step, midi, length in steps)
HOOK_A = [(0, 69, 2), (2, 72, 2), (4, 76, 2), (6, 74, 1), (7, 72, 1), (8, 74, 2), (10, 72, 2), (12, 69, 4),
          (16, 69, 2), (18, 72, 2), (20, 76, 2), (22, 79, 2), (24, 77, 2), (26, 76, 2), (28, 74, 4)]
HOOK_B = [(0, 76, 1), (1, 77, 1), (2, 79, 2), (4, 76, 2), (6, 72, 2), (8, 76, 1), (9, 77, 1), (10, 79, 2), (12, 76, 4),       # "tra-la-le-ro, tra-la-la"
          (16, 76, 1), (17, 77, 1), (18, 79, 2), (20, 81, 2), (22, 79, 2), (24, 77, 2), (26, 76, 2), (28, 72, 4)]
steps = int(total / st) + 1
for k in range(steps):
    t0 = k * st
    if t0 >= total - .2: break
    quiet = S['quiet0'] <= t0 < S['who']
    sec = 'intro' if t0 < S['r1'] else 'r1' if t0 < S['r2'] else 'r2' if t0 < S['fin'] else 'fin' if t0 < S['who'] else 'who'
    bar = int(t0 / (4 * beat)); root = prog[bar % 4]; s16 = k % 16
    if quiet: continue
    if sec == 'fin' and t0 >= S['fin'] + 1.2:          # drum roll building into the charge
        put(music, t0, snare, .15 + .35 * (t0 - S['fin']) / (S['quiet0'] - S['fin'])); continue
    if s16 % 4 == 0: put(music, t0, kick, .55)
    if s16 in (4, 12): put(music, t0, snare, .35)
    if sec != 'intro' or t0 > 1.0: put(music, t0, hat, .18 if s16 % 2 == 0 else .1)
    if t0 > 1.0 and s16 in (0, 3, 6, 8, 10, 14): put(music, t0, bassnote(NOTE(root - 12), st * 2), .35)
    if sec == 'r1' and s16 in (0, 3, 6, 10, 12): put(music, t0, wood(900 if s16 % 4 else 700), .25)
    if sec in ('r1', 'r2', 'who') or (sec == 'intro' and t0 > 1.5):
        hook, kind = (HOOK_B, 'flute') if sec == 'r2' else (HOOK_A, 'sq')
        pos = k % 32
        for stp, m, ln in hook:
            if stp == pos: put(music, t0, lead(NOTE(m), ln * st, kind), .11 if kind == 'sq' else .14)
tt = np.arange(n) / SR
music *= np.clip((total - tt) / 1.0, 0, 1)
duck = 1 - .45 * np.clip(lp(np.abs(fx)[::64] * 3, .08).repeat(64)[:n], 0, 1)
mix = fx + music * duck
mix = np.tanh(mix * 1.15) * .9
pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
with wave.open(str(HERE / 'audio.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print(f'audio.wav  {total:.2f} s, {len(spec["events"])} sfx')
