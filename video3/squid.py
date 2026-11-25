"""Lula-de-humboldt e barco de pesca noturno.

Lógica física da lula: ela nada a jato, com a PONTA DO MANTO (nadadeiras) na frente e os braços
atrás, arrastados. Quando caça, vira e ataca com os braços para a frente. A direção vem sempre da
velocidade (motion.Path), nunca é escolhida à mão.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "video")]

import cairo  # noqa: E402

from gfx import *  # noqa: F401,F403,E402

SQ_RED = (0.78, 0.22, 0.20)
SQ_WHITE = (0.93, 0.88, 0.84)


def squid(ctx, x, y, L, t, head_dir=1, a=1.0, flash=0.0, arms_fwd=0.0, seed=0, ink_k=0.0, pulse=1.0):
    """Lula de comprimento L. head_dir = lado para onde ficam os braços (+1 direita).
    flash 0..1 = intensidade do pisca vermelho/branco. arms_fwd 1 = braços abertos para atacar."""
    rnd = random.Random(seed)
    ph = rnd.uniform(0, 6.28)
    # cor: pisca entre vermelho e branco algumas vezes por segundo quando flash > 0
    fl = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 3.0 + ph)
    base = (0.62, 0.30, 0.26)
    col = tuple(lerp(base[i], lerp(SQ_RED[i], SQ_WHITE[i], fl), flash) for i in range(3))
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(head_dir, 1)
    squeeze = 1 + 0.06 * math.sin(t * 5 * pulse + ph)  # contração do manto (jato)
    ML = L * 0.62
    MW = L * 0.10 / squeeze
    # braços (atrás do corpo quando nada; abrem para a frente quando ataca)
    n = 8
    for i in range(n + 2):
        long = i >= n
        aL = L * (0.48 if long else 0.34)
        spread = (i - (n + 1) / 2) / (n + 1)
        ang0 = spread * lerp(0.35, 1.3, arms_fwd)
        ctx.move_to(L * 0.10, spread * MW * 0.8)
        segs = 10
        px, py = L * 0.10, spread * MW * 0.8
        for k in range(1, segs + 1):
            f = k / segs
            wav = math.sin(t * 4 + i + f * 4 + ph) * L * 0.025 * f * (1 - arms_fwd * 0.6)
            px = L * 0.10 + f * aL * math.cos(ang0)
            py = spread * MW * 0.8 + f * aL * math.sin(ang0) + wav
            ctx.line_to(px, py)
        rgba(ctx, INK, a * 0.9)
        ctx.set_line_width(L * (0.020 if not long else 0.012) + 2.2)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.stroke_preserve() if False else None
        ctx.move_to(L * 0.10, spread * MW * 0.8)
        for k in range(1, segs + 1):
            f = k / segs
            wav = math.sin(t * 4 + i + f * 4 + ph) * L * 0.025 * f * (1 - arms_fwd * 0.6)
            ctx.line_to(L * 0.10 + f * aL * math.cos(ang0), spread * MW * 0.8 + f * aL * math.sin(ang0) + wav)
        ctx.set_line_width(L * (0.024 if not long else 0.014) + 2.6)
        rgba(ctx, INK, a * 0.9)
        ctx.stroke()
        ctx.move_to(L * 0.10, spread * MW * 0.8)
        for k in range(1, segs + 1):
            f = k / segs
            wav = math.sin(t * 4 + i + f * 4 + ph) * L * 0.025 * f * (1 - arms_fwd * 0.6)
            ctx.line_to(L * 0.10 + f * aL * math.cos(ang0), spread * MW * 0.8 + f * aL * math.sin(ang0) + wav)
        ctx.set_line_width(L * (0.024 if not long else 0.014))
        rgba(ctx, tuple(c * 0.92 for c in col), a)
        ctx.stroke()
        if long:  # clava (ponta alargada do tentáculo)
            ellipse_path(ctx, px, py, L * 0.035, L * 0.014, ang0)
            ink(ctx, col, a, 1.6)
    # cabeça com olho
    ellipse_path(ctx, L * 0.06, 0, L * 0.08, MW * 0.85)
    ink(ctx, col, a, 2.2)
    circle(ctx, L * 0.07, -MW * 0.15, L * 0.028 + 1.5, INK, a)
    circle(ctx, L * 0.075, -MW * 0.22, L * 0.009, WHITE, a * 0.8)
    # manto (aponta para trás, para -x) e nadadeiras na ponta
    tip = -ML
    ctx.move_to(0, -MW)
    ctx.curve_to(-ML * 0.4, -MW * 1.05, -ML * 0.85, -MW * 0.55, tip, 0)
    ctx.curve_to(-ML * 0.85, MW * 0.55, -ML * 0.4, MW * 1.05, 0, MW)
    ctx.close_path()
    ink(ctx, col, a, 2.4)
    # manchas de cromatóforos
    for k in range(18):
        u = rnd.uniform(0.05, 0.9)
        v = rnd.uniform(-0.7, 0.7)
        circle(ctx, -ML * u, MW * v * (1 - u * 0.6), L * 0.006 + 0.8, tuple(c * 0.75 for c in col), a * 0.8)
    fw = L * 0.10 * (1 + 0.15 * math.sin(t * 6 + ph))
    for s in (-1, 1):
        ctx.move_to(tip + ML * 0.02, 0)
        ctx.line_to(tip + ML * 0.30, s * MW * 0.55)
        ctx.line_to(tip + ML * 0.12, s * (MW * 0.55 + fw))
        ctx.close_path()
        ink(ctx, col, a, 2)
    # sifão e jato de água (sai para a frente, empurrando a lula para trás)
    ctx.restore()
    if ink_k > 0:
        rnd2 = random.Random(seed + 9)
        for k in range(10):
            dx = head_dir * (L * 0.15 + rnd2.uniform(0, L * 0.6) * ink_k)
            circle(ctx, x + dx, y + rnd2.uniform(-L * 0.2, L * 0.2) * ink_k, L * 0.08 * ink_k + 4, (0.04, 0.04, 0.05),
                   0.55 * a * ink_k)


def swim_squid(ctx, path, t, L, a=1.0, flash=0.0, seed=0, attack=0.0):
    """Lula seguindo uma trajetória: nada com a ponta do manto na frente (braços para trás)."""
    x, y = path.pos(t)
    mv = path.facing(t)
    head_dir = -mv if attack < 0.5 else mv  # ataque: vira e vai com os braços na frente
    pitch = path.pitch(t, 0.5, 0.5)
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(pitch * (mv))
    squid(ctx, 0, 0, L, t, head_dir, a, flash, attack, seed, pulse=1 + path.speed(t) / 200)
    ctx.restore()


# ------------------------------------------------------------------ barco e frota
def panga(ctx, x, y, L, t, a=1.0, lamp=1.0, lit_water=True, rock=True):
    """Barco de pesca de madeira visto de lado, com poste de lâmpada. (x,y) = linha d'água no meio."""
    tilt = math.sin(t * 0.9) * 0.025 if rock else 0
    dy = math.sin(t * 0.9 + 1) * 3 if rock else 0
    if lit_water and lamp > 0:
        g = cairo.RadialGradient(x, y + 40, 10, x, y + 40, L * 1.4)
        g.add_color_stop_rgba(0, 0.55, 0.95, 0.70, 0.45 * lamp * a)
        g.add_color_stop_rgba(1, 0.20, 0.60, 0.45, 0)
        ctx.save()
        ctx.rectangle(x - L * 1.5, y, L * 3, L * 1.6)
        ctx.clip()
        ctx.set_source(g)
        ctx.paint()
        ctx.restore()
    ctx.save()
    ctx.translate(x, y + dy)
    ctx.rotate(tilt)
    ctx.move_to(-L / 2, -L * 0.10)
    ctx.line_to(L / 2 + L * 0.06, -L * 0.14)
    ctx.curve_to(L / 2, L * 0.04, L * 0.25, L * 0.08, 0, L * 0.08)
    ctx.curve_to(-L * 0.3, L * 0.08, -L * 0.48, L * 0.03, -L / 2, -L * 0.10)
    ctx.close_path()
    ink(ctx, (0.70, 0.66, 0.58), a, 2.4)
    line(ctx, -L / 2 + 4, -L * 0.07, L / 2, -L * 0.11, (0.30, 0.45, 0.55), a, 4)
    # poste e lâmpadas
    line(ctx, -L * 0.15, -L * 0.10, -L * 0.15, -L * 0.42, (0.35, 0.33, 0.30), a, 4)
    line(ctx, -L * 0.15, -L * 0.42, L * 0.25, -L * 0.42, (0.35, 0.33, 0.30), a, 3)
    for k in range(3):
        lx = -L * 0.05 + k * L * 0.12
        line(ctx, lx, -L * 0.42, lx, -L * 0.36, (0.35, 0.33, 0.30), a, 2)
        if lamp > 0:
            g = cairo.RadialGradient(lx, -L * 0.34, 1, lx, -L * 0.34, L * 0.25)
            g.add_color_stop_rgba(0, 1.0, 1.0, 0.92, 0.6 * lamp * a)
            g.add_color_stop_rgba(1, 1.0, 1.0, 0.92, 0)
            ctx.set_source(g)
            ctx.arc(lx, -L * 0.34, L * 0.25, 0, 2 * math.pi)
            ctx.fill()
        circle(ctx, lx, -L * 0.34, 5, (1.0, 1.0, 0.92) if lamp > 0 else (0.4, 0.4, 0.4), a)
    ctx.restore()


def night_sky(ctx, t, horizon):
    g = cairo.LinearGradient(0, 0, 0, horizon)
    g.add_color_stop_rgb(0, 0.02, 0.03, 0.06)
    g.add_color_stop_rgb(1, 0.06, 0.09, 0.13)
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, horizon)
    ctx.fill()
    rnd = random.Random(4)
    for i in range(140):
        circle(ctx, rnd.uniform(0, W), rnd.uniform(0, horizon * 0.9), rnd.uniform(0.6, 1.6), WHITE,
               rnd.uniform(0.2, 0.7) * (0.7 + 0.3 * math.sin(t * 2 + i)))
    circle(ctx, W * 0.82, horizon * 0.25, 26, (0.92, 0.92, 0.86), 0.9)
    circle(ctx, W * 0.82, horizon * 0.25, 60, (0.92, 0.92, 0.86), 0.08)


def fleet_horizon(ctx, t, horizon, n=40, a=1.0, seed=2):
    """Luzes de outros barcos até o horizonte (mais próximos = maiores)."""
    rnd = random.Random(seed)
    for i in range(n):
        d = rnd.random() ** 1.5
        x = rnd.uniform(-50, W + 50)
        y = horizon + 3 + d * 50
        r = 2 + d * 7
        g = cairo.RadialGradient(x, y, 0, x, y, r * 6)
        g.add_color_stop_rgba(0, 1.0, 0.98, 0.85, 0.55 * a)
        g.add_color_stop_rgba(1, 1.0, 0.98, 0.85, 0)
        ctx.set_source(g)
        ctx.arc(x, y, r * 6, 0, 2 * math.pi)
        ctx.fill()
        circle(ctx, x, y, r * 0.5, (1, 1, 0.95), a)
        # reflexo na água
        line(ctx, x, y + r, x, y + r * 6, (1, 1, 0.9), 0.25 * a, r * 0.6)


def night_sea(ctx, t, horizon, a=1.0):
    g = cairo.LinearGradient(0, horizon, 0, H)
    g.add_color_stop_rgb(0, 0.04, 0.10, 0.13)
    g.add_color_stop_rgb(1, 0.01, 0.03, 0.05)
    ctx.set_source(g)
    ctx.rectangle(0, horizon, W, H)
    ctx.fill()
    for i in range(14):
        yy = horizon + 20 + i * 18 + math.sin(t + i) * 3
        line(ctx, 0, yy, W, yy + math.sin(i) * 4, (0.4, 0.55, 0.6), 0.05, 1)


def jig(ctx, x, y, s, a=1.0, glow=1.0):
    """Isca luminosa com coroa de pontas (sem farpa)."""
    if glow > 0:
        g = cairo.RadialGradient(x, y, 1, x, y, 40 * s)
        g.add_color_stop_rgba(0, 0.6, 1.0, 0.6, 0.5 * glow * a)
        g.add_color_stop_rgba(1, 0.6, 1.0, 0.6, 0)
        ctx.set_source(g)
        ctx.arc(x, y, 40 * s, 0, 2 * math.pi)
        ctx.fill()
    rrect(ctx, x - 5 * s, y - 22 * s, 10 * s, 34 * s, 5 * s)
    ink(ctx, (0.75, 0.95, 0.70), a, 1.5)
    for k in range(8):
        ang = math.pi / 2 + (k - 3.5) * 0.25
        line(ctx, x, y + 12 * s, x + math.cos(ang) * 14 * s, y + 12 * s + math.sin(ang) * 14 * s, (0.8, 0.8, 0.8),
             a, 1.4)
