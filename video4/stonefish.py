"""Peixe-pedra e cenário de recife raso em corte lateral.

Lógica física:
- O peixe-pedra fica parado no fundo (apoiado no chão), só respira devagar.
- Os 13 espinhos ficam deitados e só levantam quando há pressão de cima.
- O bote: a boca abre e a cabeça expande em ~0,1 s; a presa é puxada para dentro pela sucção.
- A pessoa anda no fundo raso: pés sempre no chão de areia, água cobre até o joelho.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "video3"), os.path.join(HERE, "..", "video")]

import cairo  # noqa: E402

from gfx import *  # noqa: F401,F403,E402
import rig  # noqa: E402
from motion import Path  # noqa: E402

ROCK = (0.46, 0.42, 0.36)


def blob(ctx, cx, cy, rx, ry, seed, bumps=14, amp=0.10, t=0.0):
    rnd = random.Random(seed)
    phs = [rnd.uniform(0, 6.28) for _ in range(bumps)]
    N = 64
    for i in range(N + 1):
        a = i / N * 2 * math.pi
        r = 1 + sum(amp / (k + 1) * math.sin((k + 2) * a + phs[k]) for k in range(4))
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        (ctx.move_to if i == 0 else ctx.line_to)(x, y)
    ctx.close_path()


def stonefish(ctx, x, ground, L, t, facing=1, a=1.0, camo=0.0, spines=0.0, mouth=0.0, eyes=1.0, algae=0.0,
              seed=1, breathe=True):
    """Peixe-pedra apoiado no chão em (x, ground), comprimento L. camo 1 = idêntico a uma pedra."""
    rnd = random.Random(seed)
    Hh = L * 0.42
    cy = ground - Hh * 0.48
    br = 1 + (0.02 * math.sin(t * 1.3) if breathe else 0)
    base = tuple(lerp(c, r, camo) for c, r in zip((0.52, 0.40, 0.34), ROCK))
    ctx.save()
    ctx.translate(x, 0)
    ctx.scale(facing, 1)
    # nadadeiras peitorais em leque (atrás)
    for s in (0,):
        ctx.move_to(-L * 0.05, cy + Hh * 0.1)
        for k in range(7):
            ang = math.pi * 0.78 + k * 0.05
            ctx.line_to(-L * 0.05 + math.cos(ang) * L * 0.26, cy + Hh * 0.1 + math.sin(ang) * L * 0.22)
        ctx.close_path()
        ink(ctx, tuple(c * 0.85 for c in base), a, 2)
    # espinhos dorsais (13): deitados -> em pé
    for k in range(13):
        u = -0.32 + k * 0.045
        bx = u * L
        by = cy - Hh * 0.45 * math.sqrt(max(0, 1 - (u / 0.5) ** 2))
        ang = lerp(-math.pi * 0.92, -math.pi / 2 - 0.15, spines) + (k - 6) * 0.03 * spines
        Ls = L * lerp(0.05, 0.16, spines) * (0.8 + 0.2 * math.sin(k))
        ex, ey = bx + math.cos(ang) * Ls, by + math.sin(ang) * Ls
        # bolsas de veneno quando os espinhos sobem
        if spines > 0.5:
            ellipse_path(ctx, lerp(bx, ex, 0.3), lerp(by, ey, 0.3), L * 0.012, L * 0.022, ang + math.pi / 2)
            rgba(ctx, (0.55, 0.75, 0.40), a * (spines - 0.5) * 2)
            ctx.fill()
        line(ctx, bx, by, ex, ey, INK, a, 3.2)
        line(ctx, bx, by, ex, ey, (0.85, 0.80, 0.70), a, 1.6)
    # corpo: bloco irregular e verrugoso
    blob(ctx, 0, cy, L * 0.5 * br, Hh * 0.5 * br, seed, amp=0.12)
    ink(ctx, base, a, 2.4)
    # manchas e verrugas (cores somem com a camuflagem)
    cols = [(0.70, 0.45, 0.25), (0.35, 0.40, 0.30), (0.62, 0.30, 0.25), (0.30, 0.28, 0.26), (0.55, 0.52, 0.45)]
    for k in range(70):
        u, v = rnd.uniform(-0.45, 0.45), rnd.uniform(-0.40, 0.40)
        if (u / 0.5) ** 2 + (v / 0.5) ** 2 > 0.85:
            continue
        c = cols[k % len(cols)]
        c = tuple(lerp(cc, b * 0.9, camo * 0.7) for cc, b in zip(c, ROCK))
        circle(ctx, u * L, cy + v * Hh, rnd.uniform(2, L * 0.025), c, a * 0.9)
    # algas crescendo por cima
    if algae > 0:
        for k in range(16):
            u = rnd.uniform(-0.35, 0.35)
            bx, by = u * L, cy - Hh * 0.42
            hh = rnd.uniform(10, 26) * algae
            ctx.move_to(bx, by)
            ctx.curve_to(bx + 5, by - hh * 0.4, bx - 5, by - hh * 0.7, bx + math.sin(t + k) * 4, by - hh)
            rgba(ctx, (0.35, 0.50, 0.28), a * algae)
            ctx.set_line_width(3)
            ctx.stroke()
    # boca virada para cima (abre no bote)
    if mouth > 0:
        ellipse_path(ctx, L * 0.40, cy - Hh * 0.12, L * 0.075 * (1 + mouth * 0.3), Hh * 0.20 * mouth, -0.5)
        ink(ctx, (0.18, 0.08, 0.08), a, 2)
    else:
        ctx.move_to(L * 0.28, cy + Hh * 0.02)
        ctx.curve_to(L * 0.36, cy - Hh * 0.04, L * 0.42, cy - Hh * 0.12, L * 0.47, cy - Hh * 0.24)
        rgba(ctx, INK, a * 0.9)
        ctx.set_line_width(2.5)
        ctx.stroke()
    # olhos no alto da cabeça, quase escondidos
    if eyes > 0:
        ex, ey = L * 0.26, cy - Hh * 0.40
        circle(ctx, ex, ey, L * 0.035 + 2, tuple(c * 0.7 for c in base), a)
        circle(ctx, ex, ey, L * 0.020 * eyes + 0.5, (0.85, 0.65, 0.25), a)
        circle(ctx, ex + 1, ey, L * 0.010 * eyes + 0.3, INK, a)
    ctx.restore()


def rock(ctx, x, ground, w, seed, a=1.0, col=ROCK):
    blob(ctx, x, ground - w * 0.22, w * 0.5, w * 0.24, seed, amp=0.14)
    ink(ctx, col, a, 2.2)
    rnd = random.Random(seed)
    for k in range(10):
        circle(ctx, x + rnd.uniform(-w * 0.35, w * 0.35), ground - w * 0.22 + rnd.uniform(-w * 0.12, w * 0.12),
               rnd.uniform(2, 5), tuple(c * 0.8 for c in col), a)


# ------------------------------------------------------------------ recife raso em corte lateral
FLOOR = H * 0.78
SURF = FLOOR - 62


def reef_scene(ctx, t, mid=None, front=None, surf=None, floor=FLOOR, morning=1.0, xoff=0.0):
    surf = SURF if surf is None else surf
    g = cairo.LinearGradient(0, 0, 0, surf)
    g.add_color_stop_rgb(0, lerp(0.40, 0.58, morning), lerp(0.55, 0.72, morning), lerp(0.66, 0.80, morning))
    g.add_color_stop_rgb(1, lerp(0.80, 0.95, morning), lerp(0.78, 0.88, morning), lerp(0.70, 0.80, morning))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, surf)
    ctx.fill()
    circle(ctx, W * 0.18, surf - 90, 36, (1.0, 0.95, 0.80), 0.9)
    # água (fundo)
    g = cairo.LinearGradient(0, surf, 0, floor)
    g.add_color_stop_rgb(0, 0.36, 0.66, 0.66)
    g.add_color_stop_rgb(1, 0.22, 0.48, 0.48)
    ctx.set_source(g)
    ctx.rectangle(0, surf, W, floor - surf + 10)
    ctx.fill()
    # cáusticas no fundo
    for i in range(40):
        xx = ((i * 97 - xoff * 0.8) % (W + 100)) - 50 + math.sin(t * 1.2 + i) * 10
        ellipse_path(ctx, xx, floor - 4 - (i % 3) * 3, 24 + 8 * math.sin(t * 2 + i), 4)
        rgba(ctx, WHITE, 0.10)
        ctx.set_line_width(1.5)
        ctx.stroke()
    # chão: areia, coral quebrado, pedras
    ctx.rectangle(0, floor, W, H - floor)
    ink(ctx, (0.80, 0.74, 0.58), 1, 2)
    rnd = random.Random(3)
    for i in range(14):
        xx = ((rnd.uniform(0, W * 2) - xoff) % (W + 200)) - 100
        rock(ctx, xx, floor + 4, rnd.uniform(40, 90), i)
    for i in range(30):
        xx = ((rnd.uniform(0, W * 2) - xoff) % (W + 100)) - 50
        line(ctx, xx, floor + rnd.uniform(4, 30), xx + rnd.uniform(-12, 12), floor + rnd.uniform(4, 30),
             (0.92, 0.88, 0.80), 0.8, 3)
    if mid:
        mid(ctx)
    # véu de água por cima do que está submerso
    ctx.rectangle(0, surf, W, floor - surf + 30)
    rgba(ctx, (0.25, 0.55, 0.56), 0.30)
    ctx.fill()
    ctx.move_to(0, surf)
    for xx in range(0, int(W) + 20, 16):
        ctx.line_to(xx, surf + math.sin(xx * 0.03 + t * 2) * 2)
    rgba(ctx, WHITE, 0.8)
    ctx.set_line_width(2.2)
    ctx.stroke()
    if front:
        front(ctx)


def wader(ctx, x, t, outfit="swimmer", facing=1, s=1.2, pose=None, a=1.0, floor=FLOOR):
    """Pessoa em pé ou andando no raso, pés no fundo de areia."""
    p = pose if pose is not None else rig.p_stand(t)
    rig.figure(ctx, x, floor, s, p, outfit=outfit, facing=facing, a=a, t=t, shadow=False)


def walker_pose(path, t, stride_px=120.0):
    """Ciclo de passo pela distância andada (pé não desliza); parado = em pé."""
    if path.speed(t) < 3:
        return rig.p_stand(t)
    ph = path.phase(t, stride_px * 2)
    return rig.p_walk(ph / 0.85, 1.0)
