"""Gera trilha ambiente + efeitos sonoros e mixa com a narração (com ducking).

Uso: python3 audio.py  -> out/mix.wav
"""
import os
import subprocess
import numpy as np
from scipy.signal import butter, sosfilt

from scenes import SCENES, CUTS

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
rng = np.random.default_rng(42)


def dur():
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                        os.path.join(HERE, "narracao.wav")], capture_output=True, text=True)
    return float(r.stdout)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x, axis=0)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x, axis=0)


def bp(x, f1, f2, order=2):
    return sosfilt(butter(order, [f1, f2], "band", fs=SR, output="sos"), x, axis=0)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def env_adsr(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def add(buf, sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= len(buf):
        return
    sig = sig[: len(buf) - i]
    l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    buf[i:i + len(sig), 0] += sig * gain * l * 1.414
    buf[i:i + len(sig), 1] += sig * gain * r * 1.414


def pad_note(freq, length, bright=0.3):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for det in (-0.12, 0.0, 0.11):
        f = freq * 2 ** (det / 12)
        ph = rng.uniform(0, 6.28)
        s += np.sin(2 * np.pi * f * t + ph) + bright * 0.5 * np.sin(4 * np.pi * f * t + ph) \
            + bright * 0.25 * np.sin(6 * np.pi * f * t + ph)
    s *= env_adsr(n, min(2.5, length / 3), min(3.0, length / 3))
    return s / 3


def pluck(freq, length=2.5):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t) + 0.1 * np.sin(6 * np.pi * freq * t))
    return s * np.exp(-t * 2.2) * env_adsr(n, 0.005, 0.2)


def section(t):
    if t < 62:
        return "suspense"
    if t < 575:
        return "doc"
    if t < 781:
        return "tension"
    if t < 878:
        return "calm"
    return "end"


# Progressões (graus em Lá menor)
PROG = {
    "suspense": [[45, 52, 57, 60], [44, 52, 56, 59]],          # Am, E/G#
    "doc": [[45, 52, 57, 60, 64], [41, 48, 57, 60, 65], [48, 55, 60, 64, 67], [43, 50, 59, 62, 67]],  # Am F C G
    "tension": [[45, 52, 57, 60], [46, 53, 58, 62], [45, 52, 57, 60], [44, 52, 56, 59]],
    "calm": [[41, 48, 57, 60, 65], [48, 55, 60, 64, 67], [45, 52, 57, 60, 64], [43, 50, 59, 62, 67]],
    "end": [[41, 48, 57, 60, 69], [43, 50, 59, 62, 67], [45, 52, 57, 60, 64], [48, 55, 64, 67, 72]],
}


def music(D):
    buf = np.zeros((int(D * SR) + SR, 2))
    bar = 8.0
    t = 0.0
    k = 0
    while t < D:
        sec = section(t)
        chord = PROG[sec][k % len(PROG[sec])]
        bright = {"suspense": 0.1, "doc": 0.35, "tension": 0.25, "calm": 0.4, "end": 0.5}[sec]
        g = {"suspense": 0.5, "doc": 0.55, "tension": 0.5, "calm": 0.6, "end": 0.7}[sec]
        for j, n in enumerate(chord):
            add(buf, pad_note(midi(n), bar + 3, bright), t, g * (0.6 if j == 0 else 0.35), pan=(j - 2) * 0.25)
        # baixo
        add(buf, pad_note(midi(chord[0] - 12), bar + 2, 0.05), t, g * 0.5)
        # arpejo
        if sec in ("doc", "calm", "end"):
            notes = chord[1:] + [chord[1] + 12]
            step = 0.5 if sec == "doc" else 0.75
            for i in range(int(bar / step)):
                n = notes[(i * 2 + k) % len(notes)] + 12
                add(buf, pluck(midi(n)), t + i * step, 0.10 * g, pan=np.sin(i) * 0.6)
        if sec == "tension":
            for i in range(int(bar / 0.333)):
                n = chord[0] + (12 if i % 2 else 0)
                add(buf, pluck(midi(n), 0.6), t + i * 0.333, 0.16, pan=0.3 if i % 2 else -0.3)
        t += bar
        k += 1
    buf = lp(buf, 5000)
    # reverb simples (atrasos múltiplos)
    rev = np.zeros_like(buf)
    for d, gg in ((0.031, 0.5), (0.047, 0.45), (0.071, 0.4), (0.113, 0.35), (0.173, 0.3), (0.257, 0.25)):
        i = int(d * SR)
        rev[i:] += buf[:-i] * gg
    rev = lp(rev, 3000)
    return buf + rev * 0.6


def ambience(D):
    n = int(D * SR) + SR
    w = rng.standard_normal((n, 2))
    brown = np.cumsum(w, axis=0)
    brown -= lp(brown, 20)
    brown = lp(brown, 400)
    brown /= np.max(np.abs(brown)) + 1e-9
    buf = brown * 0.25
    # bolhas
    for _ in range(int(D * 0.6)):
        t0 = rng.uniform(0, D)
        L = rng.uniform(0.03, 0.08)
        tt = np.arange(int(L * SR)) / SR
        f0 = rng.uniform(500, 1400)
        s = np.sin(2 * np.pi * (f0 * tt + 4000 * tt ** 2)) * np.exp(-tt * 60)
        add(buf, s, t0, rng.uniform(0.02, 0.06), rng.uniform(-0.8, 0.8))
    return buf


def whoosh(L=1.2):
    n = int(L * SR)
    x = rng.standard_normal(n)
    t = np.linspace(0, 1, n)
    out = np.zeros(n)
    # varredura por blocos
    blocks = 24
    for b in range(blocks):
        a, z = b * n // blocks, (b + 1) * n // blocks
        f = 300 + 2500 * np.sin(np.pi * (b + 0.5) / blocks)
        out[a:z] = bp(x, f * 0.7, f * 1.3)[a:z]
    return out * np.sin(np.pi * t) ** 2


def hit(L=2.5, f=55):
    n = int(L * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t * (1 + 0.5 * np.exp(-t * 8))) * np.exp(-t * 1.8)
    s += lp(rng.standard_normal(n), 800) * np.exp(-t * 12) * 0.5
    return s


def heartbeat():
    out = np.zeros(int(0.9 * SR))
    for t0, g in ((0, 1.0), (0.22, 0.7)):
        n = int(0.15 * SR)
        t = np.arange(n) / SR
        s = np.sin(2 * np.pi * 50 * t) * np.exp(-t * 30) * g
        i = int(t0 * SR)
        out[i:i + n] += s
    return out


def tick():
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 2000) * np.exp(-t * 200)


def sting():
    n = int(1.5 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 1200 * t * (1 - 0.3 * t)) * np.exp(-t * 6) * 0.4
    s += hp(rng.standard_normal(n), 3000) * np.exp(-t * 20) * 0.6
    return s


def waves(L):
    n = int(L * SR)
    x = lp(rng.standard_normal((n, 2)), 1200)
    t = np.arange(n) / SR
    e = 0.5 + 0.5 * np.sin(2 * np.pi * t / 6.0) ** 2
    return x * e[:, None] * 0.6


def sfx(D):
    buf = np.zeros((int(D * SR) + SR, 2))
    w = waves(37.5)
    buf[: len(w)] += w * np.linspace(1, 0.2, len(w))[:, None]
    w = waves(D - 878)  # final na praia
    i = int(910 * SR)
    buf[i:i + len(w[: len(buf) - i])] += w[: len(buf) - i] * 0.5
    w = waves(62)
    i = int(575 * SR)
    buf[i:i + len(w)] += w * 0.35
    for c in CUTS:
        if 1 < c < D - 1:
            add(buf, whoosh(), c - 0.6, 0.10, rng.uniform(-0.4, 0.4))
    for t0 in (43.0, 595.0):
        add(buf, sting(), t0, 0.25)
        add(buf, hit(), t0, 0.35)
    for t0 in (71.2, 117.4, 252.0, 269.5, 430.5, 534.3, 696.5, 727.5):
        add(buf, hit(2.0, 45), t0, 0.28)
    for i in range(12):
        add(buf, heartbeat(), 224 + i * 0.85 * (1 + max(0, i - 5) * 0.15), 0.5 * (1 if i < 6 else 0.7 ** (i - 5)))
    for a, b in ((414.5, 418.5), (506.5, 509.5), (795, 798), (634.2, 637)):
        t0 = a
        while t0 < b:
            add(buf, tick(), t0, 0.25)
            t0 += 0.25
    return buf


def main():
    D = dur()
    print("duração", D)
    mus = music(D)
    amb = ambience(D)
    fx = sfx(D)
    n = int(D * SR)
    mus, amb, fx = mus[:n], amb[:n], fx[:n]
    for x in (mus, amb, fx):
        x /= np.max(np.abs(x)) + 1e-9
    # cena na praia: menos ambiência submarina
    tt = np.arange(n) / SR
    under = np.ones(n)
    under[(tt < 37) | ((tt > 575) & (tt < 622)) | (tt > 910)] = 0.25
    under = lp(under, 1)
    bed = mus * 0.55 + amb * (0.22 * under)[:, None] + fx * 0.5
    bed /= np.max(np.abs(bed)) + 1e-9
    import wave
    pcm = (np.clip(bed, -1, 1) * 32000).astype(np.int16)
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "bed.wav")
    with wave.open(p, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    # mix: voz em destaque + trilha com ducking por sidechain + loudness para YouTube
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", os.path.join(HERE, "narracao.wav"), "-i", p, "-filter_complex",
        "[0:a]aresample=48000,pan=stereo|c0=c0|c1=c0,highpass=f=70,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,"
        "asplit=2[v][sc];"
        "[1:a]volume=-15dB[b];"
        "[b][sc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=600[bd];"
        "[v][bd]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
        "-map", "[out]", "-ar", "48000", os.path.join(OUT, "mix.wav")], check=True)
    print("ok", os.path.join(OUT, "mix.wav"))


if __name__ == "__main__":
    main()
