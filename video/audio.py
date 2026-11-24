"""Gera trilha ambiente + efeitos sonoros e mixa com a narração (com ducking).

Uso: python3 audio.py  -> out/mix.wav
"""
import math
import os
import subprocess
import numpy as np
from scipy.signal import butter, sosfilt

from scenes3 import SCENES, CUTS

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


# Mi bemol menor: i – VI – III – VII  (Ebm, Cb, Gb, Db) e variações por clima
PROG = {
    "suspense": [[39, 46, 51, 54], [38, 46, 50, 53]],
    "doc": [[39, 46, 51, 54, 58], [35, 42, 51, 54, 59], [42, 49, 54, 58, 61], [37, 44, 53, 56, 61]],
    "tension": [[39, 46, 51, 54], [40, 47, 52, 55], [39, 46, 51, 54], [38, 45, 50, 54]],
    "calm": [[35, 42, 51, 54, 59], [42, 49, 54, 58, 61], [39, 46, 51, 54, 58], [37, 44, 53, 56, 61]],
    "end": [[35, 42, 51, 54, 59], [37, 44, 53, 56, 61], [39, 46, 51, 54, 58], [42, 49, 58, 61, 66]],
}


def felt_piano(freq, length=5.0, vel=1.0):
    """Piano abafado: harmônicos levemente inarmônicos, decaimento por harmônico, martelo suave."""
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    B = 0.0004
    for k in range(1, 9):
        fk = k * freq * np.sqrt(1 + B * k * k)
        if fk > 6000:
            break
        amp = (1.0 / k ** 1.6) * (0.6 + 0.4 * vel)
        s += amp * np.sin(2 * np.pi * fk * t + rng.uniform(0, 6.28)) * np.exp(-t * (0.5 + 0.45 * k))
    hammer = lp(rng.standard_normal(n), 900) * np.exp(-t * 60) * 0.05
    s = (s + hammer) * env_adsr(n, 0.006, 0.4)
    return lp(s, 2600) * vel


def warm_pad(freq, length, bright=0.3):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for det in (-0.08, 0.0, 0.07):
        f = freq * 2 ** (det / 12)
        ph = rng.uniform(0, 6.28)
        for k in range(1, 7):
            s += (1.0 / k ** (2.2 - bright)) * np.sin(2 * np.pi * f * k * t + ph * k)
    s *= env_adsr(n, min(3.5, length / 3), min(3.5, length / 3))
    # leve movimento de volume (respiração)
    s *= 0.85 + 0.15 * np.sin(2 * np.pi * t / 9.0)
    return lp(s / 3, 1400)


def music(D):
    buf = np.zeros((int(D * SR) + 8 * SR, 2))
    bar = 8.0
    t = 0.0
    k = 0
    while t < D:
        sec = section(t)
        chord = PROG[sec][k % len(PROG[sec])]
        g = {"suspense": 0.45, "doc": 0.5, "tension": 0.5, "calm": 0.55, "end": 0.65}[sec]
        bright = {"suspense": 0.0, "doc": 0.3, "tension": 0.15, "calm": 0.35, "end": 0.45}[sec]
        for j, n in enumerate(chord[:4]):
            add(buf, warm_pad(midi(n), bar + 4, bright), t, g * (0.55 if j == 0 else 0.28), pan=(j - 1.5) * 0.3)
        add(buf, warm_pad(midi(chord[0] - 12), bar + 3, 0.0), t, g * 0.45)
        # piano esparso (motivo)
        if sec != "suspense":
            upper = [n + 12 for n in chord[1:]] + [chord[1] + 24]
            r = np.random.default_rng(int(t) + 7)
            if sec == "tension":
                times = np.arange(0, bar, 1.0)
                for i, tt in enumerate(times):
                    note = chord[0] + (12 if i % 2 else 0)
                    add(buf, felt_piano(midi(note), 2.5, 0.55), t + tt, 0.22, pan=-0.2 if i % 2 else 0.2)
            else:
                times = [0.0, 1.5, 3.0, 5.0, 6.0] if sec in ("doc", "end") else [0.0, 2.0, 4.0, 6.0]
                for i, tt in enumerate(times):
                    if r.random() < (0.85 if i == 0 else 0.6):
                        note = upper[(i * 2 + k) % len(upper)]
                        add(buf, felt_piano(midi(note), 5.0, r.uniform(0.5, 0.9)), t + tt + r.uniform(-0.05, 0.05),
                            0.30, pan=r.uniform(-0.5, 0.5))
        else:
            # suspense: notas graves isoladas e um sino distante
            add(buf, felt_piano(midi(chord[0] + 12), 6.0, 0.5), t + 0.5, 0.22)
            add(buf, felt_piano(midi(chord[3] + 24), 6.0, 0.35), t + 4.5, 0.12, pan=0.4)
        t += bar
        k += 1
    # reverberação de sala (convolução com resposta impulsiva sintética de ~3 s)
    from scipy.signal import fftconvolve
    L = int(3.0 * SR)
    tt = np.arange(L) / SR
    ir = np.stack([rng.standard_normal(L), rng.standard_normal(L)], 1) * np.exp(-tt * 2.3)[:, None]
    ir = lp(ir, 5000)
    ir[: int(0.02 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum(axis=0))
    wet = np.stack([fftconvolve(buf[:, c], ir[:, c])[: len(buf)] for c in (0, 1)], 1)
    out = buf * 0.65 + wet * 0.55
    return hp(out, 40)


# ------------------------------------------------------------------ estilo eletrônica submarina
BPM = 84.0
BEAT = 60.0 / BPM


def saw_pad(freq, length, cutoff=900.0, lfo=0.07):
    """Supersaw filtrado com varredura lenta de filtro (respira como a água)."""
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for det in (-0.14, -0.05, 0.0, 0.06, 0.15):
        f = freq * 2 ** (det / 12)
        ph = rng.uniform(0, 1)
        s += 2 * (((f * t + ph) % 1.0) - 0.5)
    s /= 5
    # filtro: média de dois cortes, misturados pela LFO
    lo, hi = lp(s, cutoff * 0.5), lp(s, cutoff * 1.6)
    m = 0.5 + 0.5 * np.sin(2 * np.pi * lfo * t + rng.uniform(0, 6))
    s = lo * (1 - m) + hi * m
    return s * env_adsr(n, min(2.5, length / 3), min(3.0, length / 3))


def sub_bass(freq, length):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.25 * np.sin(4 * np.pi * freq * t)
    return s * env_adsr(n, 0.01, 0.15) * np.exp(-t * 1.2)


def kick():
    n = int(0.5 * SR)
    t = np.arange(n) / SR
    f = 45 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)


def soft_hat():
    n = int(0.08 * SR)
    t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 6000) * np.exp(-t * 60) * 0.5


def rim():
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    return (bp(rng.standard_normal(n), 1500, 3500) * np.exp(-t * 40) + np.sin(2 * np.pi * 820 * t) * np.exp(-t * 50))


def pluck_syn(freq, length=1.2):
    n = int(length * SR)
    t = np.arange(n) / SR
    s = 2 * (((freq * t) % 1.0) - 0.5) * 0.6 + np.sin(2 * np.pi * freq * t)
    s = lp(s, 2200) * np.exp(-t * 4.5)
    return s * env_adsr(n, 0.003, 0.1)


def sonar():
    n = int(2.5 * SR)
    t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 3.2) * env_adsr(n, 0.002, 0.3)


def music(D):
    buf = np.zeros((int(D * SR) + 8 * SR, 2))
    drums = np.zeros_like(buf)
    bar = 4 * BEAT * 2  # 2 compassos por acorde
    t = 0.0
    k = 0
    while t < D:
        sec = section(t)
        chord = PROG[sec][k % len(PROG[sec])]
        pad_cut = {"suspense": 500, "doc": 900, "tension": 700, "calm": 1100, "end": 1400}[sec]
        for j, n in enumerate(chord[:4]):
            add(buf, saw_pad(midi(n), bar + 3, pad_cut), t, 0.30 if j else 0.42, pan=(j - 1.5) * 0.35)
        nbeats = int(bar / BEAT)
        # baixo sub pulsando
        if sec != "suspense":
            for i in range(nbeats):
                if sec == "tension" or i % 2 == 0:
                    sub = 4 if sec == "tension" else 1
                    for q in range(sub):
                        add(buf, sub_bass(midi(chord[0] - 12), BEAT / sub * 0.95), t + i * BEAT + q * BEAT / sub,
                            0.55 if q == 0 else 0.35)
        # bateria eletrônica suave
        if sec in ("doc", "tension", "end"):
            for i in range(nbeats):
                tb = t + i * BEAT
                if i % 4 in (0, 2) or (sec == "tension" and i % 2 == 1):
                    add(drums, kick(), tb, 0.55)
                if i % 4 == 2:
                    add(drums, rim(), tb, 0.18, pan=0.2)
                for h in range(2):
                    add(drums, soft_hat(), tb + h * BEAT / 2, 0.12 if h else 0.07, pan=-0.3)
        # arpejo com delay
        if sec in ("doc", "calm", "end", "tension"):
            notes = [n + 12 for n in chord[1:4]] + [chord[1] + 24]
            step = BEAT / 2 if sec != "calm" else BEAT
            for i in range(int(bar / step)):
                if sec == "doc" and i % 4 == 3:
                    continue
                add(buf, pluck_syn(midi(notes[(i + k) % len(notes)])), t + i * step, 0.10, pan=math.sin(i) * 0.6)
        # sonar
        if sec in ("suspense", "calm") or k % 2 == 0:
            add(buf, sonar(), t + 0.5, 0.05, pan=-0.5)
        t += bar
        k += 1
    # delay estéreo ping-pong (eco submarino) no instrumental
    d = int(BEAT * 0.75 * SR)
    echo = np.zeros_like(buf)
    echo[d:, 0] += buf[:-d, 1] * 0.38
    echo[d:, 1] += buf[:-d, 0] * 0.38
    echo[2 * d:, 0] += buf[:-2 * d, 0] * 0.18
    echo[2 * d:, 1] += buf[:-2 * d, 1] * 0.18
    from scipy.signal import fftconvolve
    L = int(2.2 * SR)
    tt = np.arange(L) / SR
    ir = np.stack([rng.standard_normal(L), rng.standard_normal(L)], 1) * np.exp(-tt * 3.0)[:, None]
    ir = lp(ir, 4000)
    ir /= np.sqrt((ir ** 2).sum(axis=0))
    mixd = buf + lp(echo, 3000)
    wet = np.stack([fftconvolve(mixd[:, c], ir[:, c])[: len(mixd)] for c in (0, 1)], 1)
    out = mixd * 0.7 + wet * 0.45 + lp(drums, 9000) * 0.9
    return hp(out, 30)


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
    for c in (122.0, 350.0, 401.0, 435.0, 542.0, 575.0, 637.0, 738.0, 813.0, 878.0):
        add(buf, whoosh(1.4), c - 0.7, 0.05, rng.uniform(-0.3, 0.3))
    for t0 in (43.0, 595.0):
        add(buf, sting(), t0, 0.25)
        add(buf, hit(), t0, 0.35)
    for t0 in (117.4, 252.0, 430.5, 534.3, 697.5):
        add(buf, hit(2.5, 41), t0, 0.18)
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
    bed = mus * 0.62 + amb * (0.16 * under)[:, None] + fx * 0.45
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
        "[1:a]volume=-17dB[b];"
        "[b][sc]sidechaincompress=threshold=0.03:ratio=6:attack=40:release=600[bd];"
        "[v][bd]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]",
        "-map", "[out]", "-ar", "48000", os.path.join(OUT, "mix.wav")], check=True)
    print("ok", os.path.join(OUT, "mix.wav"))


if __name__ == "__main__":
    main()
