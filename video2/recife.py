"""Praia de Boa Viagem em corte lateral: calçadão e prédios, areia, piscina rasa protegida, linha de
arrecifes e o canal fundo logo depois. Maré e turbidez ajustáveis. Chão consultável para a física."""
import math
import random

import cairo

from shark import *  # noqa: F401,F403

DRY = H * 0.50
REEF_X = W * 0.62
TIDE_HIGH = H * 0.505
TIDE_LOW = H * 0.565


def ground_y(x):
    if x < W * 0.30:
        return DRY
    if x < W * 0.38:                       # praia descendo
        return DRY + (x - W * 0.30) / (W * 0.08) * 70
    if x < REEF_X - 40:                    # fundo da piscina (rasa)
        return DRY + 70 + math.sin(x * 0.03) * 3
    if x < REEF_X + 30:                    # crista do arrecife
        k = (x - (REEF_X - 40)) / 70
        return DRY + 70 - 55 * math.sin(k * math.pi) + 4 * math.sin(x * 0.4)
    k = clamp((x - (REEF_X + 30)) / 120)   # queda para o canal fundo
    return DRY + 70 + k * (H * 0.40)


def sea_level(tide):
    return lerp(TIDE_LOW, TIDE_HIGH, tide)


def depth(x, tide=1.0):
    return max(0.0, ground_y(x) - sea_level(tide))


def sky(ctx, t, dusk=0.6, rain=0.0):
    g = cairo.LinearGradient(0, 0, 0, DRY)
    g.add_color_stop_rgb(0, lerp(0.50, 0.36, dusk) - 0.1 * rain, lerp(0.66, 0.44, dusk) - 0.1 * rain,
                         lerp(0.80, 0.56, dusk) - 0.08 * rain)
    g.add_color_stop_rgb(1, lerp(0.88, 0.98, dusk), lerp(0.88, 0.74, dusk), lerp(0.86, 0.58, dusk))
    ctx.set_source(g)
    ctx.paint()
    sx = W * 0.86
    circle(ctx, sx, DRY - 150, 70, (1.0, 0.85, 0.6), 0.18)
    circle(ctx, sx, DRY - 150, 34, (1.0, 0.86, 0.62), 0.95)
    for i in range(5):
        cx = (W * (0.1 + i * 0.22) + t * 3) % (W + 300) - 150
        for dx, r in ((-40, 24), (0, 34), (40, 25)):
            circle(ctx, cx + dx, H * (0.08 + 0.05 * (i % 2)), r, (0.82, 0.82, 0.84), 0.45 + 0.3 * rain)


def land(ctx, t, lit=0.3):
    skyline(ctx, DRY - 26, t, 1.0, -20, W * 0.34, seed=5, col=(0.70, 0.71, 0.74), lit=lit)
    # calçadão
    ctx.rectangle(-10, DRY - 26, W * 0.34, 26)
    ink(ctx, (0.80, 0.76, 0.70), 1, 2)
    for i in range(12):
        line(ctx, i * 40, DRY - 26, i * 40 + 20, DRY - 2, (0.55, 0.50, 0.45), 0.5, 2)
    # coqueiros
    for x in (W * 0.05, W * 0.19):
        palm(ctx, x, DRY - 24, 0.75, t)


def sand_and_reef(ctx, t, tide=1.0):
    ctx.move_to(-10, DRY)
    x = -10
    while x <= W + 12:
        ctx.line_to(x, ground_y(x))
        x += 6
    ctx.line_to(W + 12, H + 10)
    ctx.line_to(-10, H + 10)
    ctx.close_path()
    ink(ctx, SAND, 1, 2.5)
    # rochas do arrecife
    rnd = random.Random(2)
    for i in range(10):
        xx = REEF_X - 50 + i * 9 + rnd.uniform(-4, 4)
        ellipse_path(ctx, xx, ground_y(xx) + 8, rnd.uniform(14, 22), rnd.uniform(10, 16))
        ink(ctx, (0.45, 0.42, 0.36), 1, 2)
    for i in range(30):
        xx = rnd.uniform(W * 0.40, W)
        circle(ctx, xx, ground_y(xx) + rnd.uniform(4, 40), rnd.uniform(1.5, 3), (0.65, 0.58, 0.42), 0.6)


def _water_path(ctx, t, tide):
    lvl = sea_level(tide)
    x = W * 0.30
    while ground_y(x) < lvl and x < W:
        x += 2
    xs = x
    ctx.move_to(xs, lvl)
    x = xs
    while x <= W + 20:
        yy = lvl + math.sin(x * 0.03 + t * 2) * 2
        ctx.line_to(x, yy)
        x += 10
    x = W + 20
    while x >= xs:
        ctx.line_to(x, max(ground_y(x), lvl) + 1)
        x -= 8
    ctx.close_path()


def water_back(ctx, t, tide=1.0, murk=1.0):
    _water_path(ctx, t, tide)
    g = cairo.LinearGradient(0, sea_level(tide), 0, H)
    c0 = (lerp(0.30, 0.42, murk), lerp(0.66, 0.50, murk), lerp(0.70, 0.36, murk))
    c1 = (lerp(0.08, 0.14, murk), lerp(0.30, 0.16, murk), lerp(0.38, 0.10, murk))
    g.add_color_stop_rgb(0, *c0)
    g.add_color_stop_rgb(1, *c1)
    ctx.set_source(g)
    ctx.fill()


def water_front(ctx, t, tide=1.0, murk=1.0):
    """Véu de água por cima do que está submerso; turva = mais opaco."""
    _water_path(ctx, t, tide)
    rgba(ctx, (lerp(0.22, 0.36, murk), lerp(0.56, 0.42, murk), lerp(0.62, 0.28, murk)), lerp(0.40, 0.72, murk))
    ctx.fill()
    lvl = sea_level(tide)
    x = W * 0.30
    while ground_y(x) < lvl and x < W:
        x += 2
    ctx.move_to(x, lvl)
    while x <= W + 20:
        ctx.line_to(x, lvl + math.sin(x * 0.03 + t * 2) * 2)
        x += 10
    rgba(ctx, WHITE, 0.85)
    ctx.set_line_width(2.5)
    ctx.stroke()
    # quebra da onda no arrecife
    for i in range(6):
        xx = REEF_X + 10 + i * 9 + math.sin(t * 3 + i) * 4
        circle(ctx, xx, lvl - 2 - abs(math.sin(t * 2 + i)) * 6, 5, WHITE, 0.7)


def scene(ctx, t, tide=1.0, murk=1.0, dusk=0.6, rain=0.0, mid=None, lit=0.3, sign=True):
    """Monta o cenário completo; 'mid' desenha personagens/animais entre o fundo e a água."""
    sky(ctx, t, dusk, rain)
    land(ctx, t, lit)
    sand_and_reef(ctx, t, tide)
    water_back(ctx, t, tide, murk)
    if sign:
        shark_sign(ctx, W * 0.27, DRY, 0.55)
    if mid:
        mid(ctx)
    water_front(ctx, t, tide, murk)
