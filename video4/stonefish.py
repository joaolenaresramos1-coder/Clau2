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


def _smooth_path(ctx, pts, closed=True):
    """Curva suave (Catmull-Rom) passando pelos pontos."""
    n = len(pts)
    ctx.move_to(*pts[0])
    rng_ = range(n) if closed else range(n - 1)
    for i in rng_:
        p0, p1 = pts[i - 1] if (closed or i > 0) else pts[i], pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        ctx.curve_to(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if closed:
        ctx.close_path()


def sf_point(x, ground, L, u, v, facing=1):
    """Ponto (u, v) do corpo do peixe-pedra em coordenadas da tela (mesma geometria de stonefish())."""
    Hh = L * 0.40
    cy = ground - Hh * 0.45
    return x + facing * u * L, cy + v * Hh


def stonefish(ctx, x, ground, L, t, facing=1, a=1.0, camo=0.0, spines=0.0, mouth=0.0, eyes=1.0, algae=0.0,
              seed=1, breathe=True, bury=0.0):
    """Peixe-pedra de perfil, modelado a partir de fotos de referência (Synanceia verrucosa):
    cabeça grande e larga com boca de lábios grossos na frente, olhos pequenos em calombos no alto da
    cabeça (dentro do contorno), corpo afinando até uma cauda arredondada, nadadeira peitoral em leque
    listrado apoiada no chão, crista dorsal com espinhos e pele verrugosa mosqueada.
    (x, ground) = ponto de apoio no chão; facing = lado do focinho."""
    rnd = random.Random(seed)
    Hh = L * 0.40
    br = 1 + (0.015 * math.sin(t * 1.3) if breathe else 0)
    cy = ground - Hh * 0.45
    base = tuple(lerp(c, r, camo) for c, r in zip((0.50, 0.42, 0.44), ROCK))
    dark = tuple(c * 0.70 for c in base)

    def P(u, v):  # u: -0.5 cauda .. +0.5 focinho; v: em múltiplos de Hh (negativo = dorso)
        return (u * L, cy + v * Hh * br)

    ctx.save()
    ctx.translate(x, 0)
    ctx.scale(facing, 1)
    # cauda arredondada (atrás do corpo)
    tail = [P(-0.39, -0.12), P(-0.50, -0.30), P(-0.58, -0.22), P(-0.60, 0.0), P(-0.58, 0.22), P(-0.50, 0.30),
            P(-0.39, 0.12)]
    _smooth_path(ctx, tail)
    ink(ctx, dark, a, 2.2)
    for k in range(6):
        v = -0.22 + k * 0.09
        line(ctx, *P(-0.40, v * 0.5), *P(-0.57, v), INK, a * 0.35, 1.2)
    # crista dorsal: membrana com espinhos (13), deitados -> em pé
    tops = []
    for k in range(13):
        u = 0.22 - k * 0.042
        top_v = -0.46 + 0.30 * max(0, (-u - 0.05) / 0.35) ** 1.3
        bx, by = P(u, top_v + 0.03)
        ang = lerp(-math.pi * 0.86, -math.pi / 2 - 0.10, spines)
        Ls = L * lerp(0.05, 0.15, spines) * (0.75 + 0.25 * math.sin(k * 1.3 + 1))
        tops.append(((bx, by), (bx + math.cos(ang) * Ls, by + math.sin(ang) * Ls)))
    ctx.move_to(*tops[0][0])
    for bpt, tp in tops:
        ctx.line_to(*tp)
    ctx.line_to(*tops[-1][0])
    ctx.close_path()
    rgba(ctx, dark, a * 0.85)
    ctx.fill()
    for (bx, by), (ex, ey) in tops:
        if spines > 0.5:
            ellipse_path(ctx, lerp(bx, ex, 0.3), lerp(by, ey, 0.3), L * 0.010, L * 0.020,
                         math.atan2(ey - by, ex - bx) + math.pi / 2)
            rgba(ctx, (0.55, 0.75, 0.40), a * (spines - 0.5) * 2)
            ctx.fill()
        line(ctx, bx, by, ex, ey, INK, a, 2.8)
        line(ctx, bx, by, ex, ey, (0.82, 0.78, 0.72), a, 1.3)
    # corpo
    body = [P(0.50, 0.04), P(0.47, -0.20), P(0.40, -0.36), P(0.30, -0.46), P(0.18, -0.48), P(0.02, -0.44),
            P(-0.15, -0.36), P(-0.30, -0.22), P(-0.39, -0.13), P(-0.40, 0.12), P(-0.30, 0.30), P(-0.12, 0.43),
            P(0.10, 0.47), P(0.30, 0.44), P(0.44, 0.34), P(0.50, 0.20)]
    _smooth_path(ctx, body)
    ctx.save()
    ctx.clip_preserve()
    rgba(ctx, base, a)
    ctx.fill()
    # mosqueado (manchas grandes e verrugas), recortado dentro do corpo
    cols = [(0.62, 0.32, 0.30), (0.36, 0.34, 0.38), (0.72, 0.66, 0.66), (0.30, 0.28, 0.26), (0.55, 0.48, 0.40)]
    for k in range(26):
        c = cols[k % len(cols)]
        c = tuple(lerp(cc, b * 0.92, camo * 0.7) for cc, b in zip(c, ROCK))
        u, v = rnd.uniform(-0.40, 0.48), rnd.uniform(-0.45, 0.45)
        blob(ctx, *P(u, v), rnd.uniform(L * 0.03, L * 0.08), rnd.uniform(L * 0.02, L * 0.05), k + seed, amp=0.3)
        rgba(ctx, c, a * 0.75)
        ctx.fill()
    for k in range(90):
        u, v = rnd.uniform(-0.40, 0.50), rnd.uniform(-0.48, 0.47)
        px, py = P(u, v)
        circle(ctx, px, py, rnd.uniform(1.2, L * 0.012), (0.85, 0.82, 0.82), a * 0.5)
        circle(ctx, px + 1, py + 1, rnd.uniform(0.8, L * 0.006), (0.15, 0.12, 0.12), a * 0.4)
    # sombra da barriga
    g = cairo.LinearGradient(0, cy, 0, cy + Hh * 0.5)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.30 * a)
    ctx.set_source(g)
    ctx.paint()
    ctx.restore()
    _smooth_path(ctx, body)
    rgba(ctx, INK, a)
    ctx.set_line_width(2.4)
    ctx.stroke()
    # opérculo (linha da guelra)
    ctx.move_to(*P(0.16, -0.30))
    ctx.curve_to(*P(0.10, -0.10), *P(0.10, 0.12), *P(0.16, 0.30))
    rgba(ctx, INK, a * 0.55)
    ctx.set_line_width(2)
    ctx.stroke()
    # nadadeira peitoral em leque, listrada, apoiada no chão (na frente do corpo)
    fb = P(0.08, 0.08)
    tips = []
    for k in range(9):
        f = k / 8
        ang = lerp(math.pi * 0.62, math.pi * 1.02, f)
        r = L * (0.30 - 0.05 * abs(f - 0.5))
        tx, ty = fb[0] + math.cos(ang) * r, fb[1] + math.sin(ang) * r * 0.75
        ty = min(ty, ground - 2)
        tips.append((tx, ty))
    ctx.move_to(*fb)
    _smooth_path(ctx, tips, closed=False)
    ctx.close_path()
    ink(ctx, tuple(lerp(c, 0.25, 0.3) for c in base), a, 2)
    for k, (tx, ty) in enumerate(tips):
        line(ctx, fb[0], fb[1], tx, ty, INK if k % 2 else (0.85, 0.82, 0.80), a * 0.5, 2.5 if k % 2 else 1.4)
    # boca: lábios grossos na frente, virada para cima
    if mouth > 0:
        mx, my = P(0.45, 0.10)
        ellipse_path(ctx, mx, my, L * 0.065 * (0.7 + 0.3 * mouth), Hh * 0.20 * mouth, -0.35)
        ink(ctx, (0.20, 0.08, 0.08), a, 2.4)
        ctx.move_to(*P(0.50, 0.02))
        ctx.curve_to(*P(0.47, -0.06 - 0.1 * mouth), *P(0.40, -0.04), *P(0.34, 0.06))
        rgba(ctx, (0.75, 0.55, 0.55), a)
        ctx.set_line_width(3)
        ctx.stroke()
    else:
        ctx.move_to(*P(0.50, 0.06))
        ctx.curve_to(*P(0.44, 0.10), *P(0.36, 0.14), *P(0.28, 0.20))
        rgba(ctx, INK, a)
        ctx.set_line_width(3.2)
        ctx.stroke()
        ctx.move_to(*P(0.50, 0.12))
        ctx.curve_to(*P(0.45, 0.17), *P(0.38, 0.20), *P(0.30, 0.22))
        rgba(ctx, (0.75, 0.55, 0.55), a * 0.7)
        ctx.set_line_width(2)
        ctx.stroke()
    # olhos: pequenos, num calombo no alto da cabeça, DENTRO do contorno
    ex, ey = P(0.31, -0.33)
    blob(ctx, ex, ey + 2, L * 0.045, L * 0.035, seed + 3, amp=0.15)
    ink(ctx, dark, a, 1.6)
    if eyes > 0:
        circle(ctx, ex, ey, L * 0.020, (0.92, 0.60, 0.25), a * eyes)
        circle(ctx, ex + L * 0.004, ey, L * 0.010, INK, a * eyes)
        circle(ctx, ex + L * 0.007, ey - L * 0.006, L * 0.004, WHITE, a * eyes)
    else:
        line(ctx, ex - L * 0.02, ey, ex + L * 0.02, ey, INK, a * 0.7, 2)
    # algas crescendo por cima
    if algae > 0:
        for k in range(18):
            u = rnd.uniform(-0.30, 0.30)
            bx, by = P(u, -0.42 + 0.25 * max(0, (-u - 0.05) / 0.35))
            hh = rnd.uniform(10, 26) * algae
            ctx.move_to(bx, by)
            ctx.curve_to(bx + 5, by - hh * 0.4, bx - 5, by - hh * 0.7, bx + math.sin(t + k) * 4, by - hh)
            rgba(ctx, (0.35, 0.50, 0.28), a * algae)
            ctx.set_line_width(3)
            ctx.stroke()
    # meio enterrado na areia: areia cobre cauda, nadadeira e a parte de baixo (fica parecendo uma pedra)
    if bury > 0:
        sand = (0.80, 0.74, 0.58)
        ctx.move_to(*P(-0.75, 0.55))
        ctx.curve_to(*P(-0.62, -0.10 * bury), *P(-0.40, -0.05 * bury), *P(-0.20, 0.20 - 0.05 * bury))
        ctx.curve_to(*P(0.10, 0.30 - 0.15 * bury), *P(0.40, 0.35 - 0.1 * bury), *P(0.62, 0.55))
        ctx.close_path()
        rgba(ctx, sand, a * bury)
        ctx.fill()
        ctx.move_to(*P(-0.66, 0.30))
        ctx.curve_to(*P(-0.62, -0.10 * bury), *P(-0.40, -0.05 * bury), *P(-0.20, 0.20 - 0.05 * bury))
        ctx.curve_to(*P(0.10, 0.30 - 0.15 * bury), *P(0.40, 0.35 - 0.1 * bury), *P(0.56, 0.45))
        rgba(ctx, INK, a * bury * 0.5)
        ctx.set_line_width(1.6)
        ctx.stroke()
        for k in range(30):
            px, py = P(rnd.uniform(-0.6, 0.55), rnd.uniform(0.25, 0.5))
            circle(ctx, px, py, rnd.uniform(1, 2.5), (0.66, 0.60, 0.45), a * bury * 0.7)
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
    ctx.rectangle(-W, -H, 3 * W, surf + H)
    ctx.fill()
    circle(ctx, W * 0.18, surf - 90, 36, (1.0, 0.95, 0.80), 0.9)
    # água (fundo)
    g = cairo.LinearGradient(0, surf, 0, floor)
    g.add_color_stop_rgb(0, 0.36, 0.66, 0.66)
    g.add_color_stop_rgb(1, 0.22, 0.48, 0.48)
    ctx.set_source(g)
    ctx.rectangle(-W, surf, 3 * W, floor - surf + 10)
    ctx.fill()
    # cáusticas no fundo
    for i in range(40):
        xx = ((i * 97 - xoff * 0.8) % (W + 100)) - 50 + math.sin(t * 1.2 + i) * 10
        ellipse_path(ctx, xx, floor - 4 - (i % 3) * 3, 24 + 8 * math.sin(t * 2 + i), 4)
        rgba(ctx, WHITE, 0.10)
        ctx.set_line_width(1.5)
        ctx.stroke()
    # chão: areia, coral quebrado, pedras
    ctx.rectangle(-W, floor, 3 * W, 2 * H)
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
    ctx.rectangle(-W, surf, 3 * W, floor - surf + 30)
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


# ------------------------------------------------------------------ pé humano detalhado (vista lateral)
def foot(ctx, x, y, s, facing=1, a=1.0, swell=0.0, bruise=0.0, leg_to=None, skin=None, seed=3):
    """Pé de perfil a partir de referência anatômica: calcanhar arredondado, arco plantar, bola do pé,
    dedões com unhas e tornozelo com maléolo. (x, y) = ponto de apoio sob a bola do pé; s ≈ comprimento/240.
    swell 0..1 incha o dorso; bruise 0..1 escurece em volta da picada (na sola, sob a bola do pé).
    leg_to = (x, y) do joelho/topo para desenhar a canela até lá."""
    skin = skin or SKIN
    sw = 1 + 0.25 * swell
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing * s, s)
    # canela (até o ponto pedido, em coordenadas da tela -> converte para locais)
    if leg_to is not None:
        lx = (leg_to[0] - x) / (facing * s)
        ly = (leg_to[1] - y) / s
        limb(ctx, [(-150, -95), (lx, ly)], 70 * sw, skin, a)
    pts = [(-205, -12), (-215, -40), (-200, -80), (-170, -105), (-140, -118),  # calcanhar -> tornozelo atrás
           (-110, -125), (-80, -118), (-40, -98 * sw), (0, -78 * sw), (40, -58 * sw), (70, -44), (95, -36),
           (105, -30), (108, -18), (100, -6), (80, -2), (60, 0), (20, 0), (-20, -2), (-60, -10),  # dedos e sola
           (-100, -14), (-140, -6), (-180, 0)]
    _smooth_path(ctx, pts)
    ink(ctx, skin, a, 2.6)
    # sombra do arco plantar e volume
    ctx.save()
    _smooth_path(ctx, pts)
    ctx.clip()
    g = cairo.LinearGradient(0, -130, 0, 0)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.12 * a)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.18 * a)
    ctx.set_source(g)
    ctx.paint()
    if bruise > 0:
        for k, (bx, by, r) in enumerate(((-10, -12, 70), (20, -20, 50), (-50, -25, 55))):
            gg = cairo.RadialGradient(bx, by, 0, bx, by, r * (0.6 + 0.7 * bruise))
            gg.add_color_stop_rgba(0, 0.35, 0.12, 0.30, 0.75 * bruise * a)
            gg.add_color_stop_rgba(1, 0.35, 0.12, 0.30, 0)
            ctx.set_source(gg)
            ctx.paint()
    ctx.restore()
    # maléolo (osso do tornozelo)
    ellipse_path(ctx, -128, -98, 13, 10)
    rgba(ctx, (0.80, 0.60, 0.50), 0.6 * a)
    ctx.fill()
    # dedos: separação e unhas
    for k, (tx, ty, r) in enumerate(((100, -20, 12), (82, -16, 10), (66, -12, 9))):
        if k:
            ctx.move_to(tx + 6, ty - r)
            ctx.curve_to(tx + 2, ty - 2, tx + 4, ty + 4, tx + 8, ty + 10)
            rgba(ctx, INK, 0.45 * a)
            ctx.set_line_width(1.4)
            ctx.stroke()
    ctx.move_to(96, -34)
    ctx.curve_to(104, -36, 108, -30, 106, -24)
    ctx.curve_to(102, -24, 96, -27, 96, -34)
    rgba(ctx, (0.96, 0.86, 0.82), a)
    ctx.fill_preserve()
    rgba(ctx, INK, 0.6 * a)
    ctx.set_line_width(1.2)
    ctx.stroke()
    # tendão de Aquiles
    ctx.move_to(-190, -60)
    ctx.curve_to(-178, -90, -165, -110, -158, -125)
    rgba(ctx, INK, 0.3 * a)
    ctx.set_line_width(1.6)
    ctx.stroke()
    ctx.restore()


def spine_detail(ctx, t, cx, base_y, length, press, a=1.0, venom_flow=0.0):
    """Espinho dorsal em corte, modelado a partir de ilustrações anatômicas de Synanceia:
    espinho afilado e levemente curvo, com um sulco de cada lado; uma glândula de veneno em forma de gota
    presa a cada lado, na metade de baixo; bainha de pele (tegumento) envolvendo tudo.
    press 0..1: a bainha é empurrada para baixo e espreme as glândulas."""
    L = length
    tipx, tipy = cx + L * 0.06, base_y - L
    # espinho (afilado, curvo)
    ctx.move_to(cx - L * 0.035, base_y)
    ctx.curve_to(cx - L * 0.03, base_y - L * 0.5, cx - L * 0.005, base_y - L * 0.85, tipx, tipy)
    ctx.curve_to(cx + L * 0.02, base_y - L * 0.85, cx + L * 0.035, base_y - L * 0.5, cx + L * 0.035, base_y)
    ctx.close_path()
    ink(ctx, (0.93, 0.90, 0.84), a, 2.2)
    # sulcos
    for sgn in (-1, 1):
        ctx.move_to(cx + sgn * L * 0.012, base_y - L * 0.10)
        ctx.curve_to(cx + sgn * L * 0.012, base_y - L * 0.5, cx + sgn * L * 0.006 + L * 0.02, base_y - L * 0.80,
                     tipx - L * 0.004, tipy + L * 0.06)
        rgba(ctx, (0.55, 0.50, 0.45), a)
        ctx.set_line_width(2)
        ctx.stroke()
    # glândulas de veneno (gotas), espremidas pela bainha
    sq = 1 - 0.55 * press
    gy = base_y - L * (0.32 - 0.10 * press)
    for sgn in (-1, 1):
        gx = cx + sgn * (L * 0.035 + L * 0.045 * sq)
        ctx.move_to(gx, gy - L * 0.16)
        ctx.curve_to(gx + sgn * L * 0.06 * sq, gy - L * 0.10, gx + sgn * L * 0.06 * sq, gy + L * 0.06, gx, gy + L * 0.08)
        ctx.curve_to(gx - sgn * L * 0.03 * sq, gy + L * 0.04, gx - sgn * L * 0.03 * sq, gy - L * 0.10,
                     gx, gy - L * 0.16)
        g = cairo.RadialGradient(gx, gy, 2, gx, gy, L * 0.12)
        g.add_color_stop_rgba(0, 0.70, 0.92, 0.45, a)
        g.add_color_stop_rgba(1, 0.35, 0.60, 0.25, a)
        ctx.set_source(g)
        ctx.fill_preserve()
        rgba(ctx, INK, a)
        ctx.set_line_width(2)
        ctx.stroke()
    # bainha de pele (desce com a pressão)
    top = base_y - L * lerp(0.80, 0.30, press)
    ctx.move_to(cx - L * 0.14, base_y + 4)
    ctx.curve_to(cx - L * 0.13, base_y - L * 0.3, cx - L * 0.06, top + L * 0.05, cx, top)
    ctx.curve_to(cx + L * 0.06, top + L * 0.05, cx + L * 0.13, base_y - L * 0.3, cx + L * 0.14, base_y + 4)
    ctx.close_path()
    g = cairo.LinearGradient(cx - L * 0.14, 0, cx + L * 0.14, 0)
    g.add_color_stop_rgba(0, 0.45, 0.36, 0.38, 0.55 * a)
    g.add_color_stop_rgba(0.5, 0.62, 0.52, 0.52, 0.35 * a)
    g.add_color_stop_rgba(1, 0.45, 0.36, 0.38, 0.55 * a)
    ctx.set_source(g)
    ctx.fill_preserve()
    rgba(ctx, INK, 0.8 * a)
    ctx.set_line_width(2)
    ctx.stroke()
    # dobras da bainha amontoada
    for k in range(int(press * 4)):
        yy = top + L * 0.05 + k * L * 0.05
        line(ctx, cx - L * 0.07, yy, cx + L * 0.07, yy + 3, INK, 0.35 * a, 1.5)
    # veneno subindo pelos sulcos até a ponta
    if venom_flow > 0:
        for k in range(10):
            ph = (t * 1.1 + k / 10) % 1
            for sgn in (-1, 1):
                yy = lerp(gy - L * 0.1, tipy + L * 0.05, ph)
                f = (base_y - yy) / L
                xx = cx + sgn * L * 0.012 * (1 - f) + (tipx - cx) * f ** 2
                circle(ctx, xx, yy, 3.5, (0.55, 0.95, 0.35), a * venom_flow * (0.4 + 0.6 * (1 - ph)))
