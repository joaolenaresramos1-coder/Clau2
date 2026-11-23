"""Praia em corte lateral (como as cenas de gelo/praia do canal): areia em declive entrando no mar,
linha d'água e parte submersa visível. Inclui a função do chão para apoiar os personagens."""
import math
import random

import cairo

from gfx import W, H, INK, WHITE, SAND, ORANGE, rgba, ink, line, circle, palm, post_bottle, rrect, lerp, clamp

SURF = H * 0.60          # nível do mar
DRY = H * 0.555          # altura da areia seca
SHORE_X = W * 0.42       # onde a areia começa a descer
SLOPE = 0.30


def ground_y(x):
    if x <= SHORE_X:
        return DRY + math.sin(x * 0.01) * 2
    return min(H * 1.05, DRY + (x - SHORE_X) * SLOPE + ((x - SHORE_X) ** 2) * 0.00012)


def water_depth(x):
    return max(0.0, ground_y(x) - SURF)


def sky(ctx, t, sunset=0.3):
    g = cairo.LinearGradient(0, 0, 0, SURF)
    g.add_color_stop_rgb(0, lerp(0.52, 0.40, sunset), lerp(0.72, 0.58, sunset), lerp(0.85, 0.76, sunset))
    g.add_color_stop_rgb(1, lerp(0.88, 0.97, sunset), lerp(0.93, 0.82, sunset), lerp(0.94, 0.66, sunset))
    ctx.set_source(g)
    ctx.paint()
    sx = W * 0.80
    circle(ctx, sx, SURF - 120, 80, (1.0, 0.93, 0.74), 0.15)
    circle(ctx, sx, SURF - 120, 40, (1.0, 0.94, 0.76), 0.95)
    for i in range(4):
        cx = (W * (0.1 + i * 0.27) + t * 4) % (W + 300) - 150
        for dx, r in ((-36, 20), (0, 28), (36, 21)):
            circle(ctx, cx + dx, H * (0.10 + 0.05 * (i % 2)), r, WHITE, 0.35)


def sand(ctx, t):
    ctx.move_to(-10, DRY)
    for x in range(0, int(W) + 20, 10):
        ctx.line_to(x, ground_y(x))
    ctx.line_to(W + 10, H + 10)
    ctx.line_to(-10, H + 10)
    ctx.close_path()
    ink(ctx, SAND, 1, 2.5)
    water_back(ctx, t)
    rnd = random.Random(8)
    for i in range(60):
        x = rnd.uniform(0, W)
        y = ground_y(x) + rnd.uniform(8, 120)
        circle(ctx, x, y, rnd.uniform(1, 2.6), (0.70, 0.62, 0.45), 0.6)
    # conchas e pedrinhas submersas
    for i in range(7):
        x = rnd.uniform(SHORE_X + 60, W)
        circle(ctx, x, ground_y(x) + 2, rnd.uniform(4, 8), (0.62, 0.60, 0.56), 0.9)


def _water_path(ctx, t):
    xs = SHORE_X
    while ground_y(xs) < SURF:
        xs += 2
    ctx.move_to(xs, SURF)
    x = xs
    while x <= W + 20:
        ctx.line_to(x, SURF + math.sin(x * 0.03 + t * 2) * 2)
        x += 12
    x = W + 20
    while x >= xs:
        ctx.line_to(x, ground_y(x) + 1)
        x -= 10
    ctx.close_path()


def water_back(ctx, t):
    """Corpo de água opaco (desenhado antes dos personagens)."""
    _water_path(ctx, t)
    g = cairo.LinearGradient(0, SURF, 0, H)
    g.add_color_stop_rgb(0, 0.30, 0.66, 0.70)
    g.add_color_stop_rgb(1, 0.10, 0.34, 0.42)
    ctx.set_source(g)
    ctx.fill()
    ctx.save()
    _water_path(ctx, t)
    ctx.clip()
    for i in range(5):
        x0 = W * (0.5 + i * 0.12) + math.sin(t * 0.3 + i) * 20
        g = cairo.LinearGradient(0, SURF, 0, H)
        g.add_color_stop_rgba(0, 0.8, 0.95, 0.95, 0.12)
        g.add_color_stop_rgba(1, 0.8, 0.95, 0.95, 0)
        ctx.move_to(x0, SURF)
        ctx.line_to(x0 + 30, SURF)
        ctx.line_to(x0 + 110, H)
        ctx.line_to(x0 + 50, H)
        ctx.close_path()
        ctx.set_source(g)
        ctx.fill()
    ctx.restore()


def water(ctx, t):
    """Véu de água translúcido por cima do que está submerso (desenhado depois dos personagens)."""
    _water_path(ctx, t)
    rgba(ctx, (0.22, 0.58, 0.64), 0.45)
    ctx.fill()
    # linha da superfície
    ctx.move_to(SHORE_X + 95, SURF)
    for x in range(int(SHORE_X) + 95, int(W) + 20, 12):
        ctx.line_to(x, SURF + math.sin(x * 0.03 + t * 2) * 2)
    rgba(ctx, WHITE, 0.9)
    ctx.set_line_width(2.5)
    ctx.stroke()
    # espuma na beira
    for i in range(3):
        xx = SHORE_X + 20 + i * 14 + math.sin(t * 1.5 + i) * 8
        circle(ctx, xx, ground_y(xx) - 2, 4, WHITE, 0.6)


def net_background(ctx, t, x0=W * 0.55, x1=W * 0.80, a=0.55):
    """Cercado com rede ao fundo (em outro trecho da praia), mais claro e menor, para dar profundidade."""
    yb = SURF + 50
    for i in range(int((x1 - x0) / 18) + 1):
        x = x0 + i * 18
        line(ctx, x, SURF - 2, x, yb, WHITE, a * 0.6, 1.2)
    line(ctx, x0, yb, x1, yb, WHITE, a * 0.5, 1.2)
    for i in range(int((x1 - x0) / 36) + 1):
        circle(ctx, x0 + i * 36, SURF - 3, 4, ORANGE, a)


def props(ctx, t, post_x=W * 0.10, towel_x=W * 0.18, cooler_x=W * 0.26, glow=0.0):
    palm(ctx, W * 0.03, DRY + 4, 0.9, t)
    post_bottle(ctx, post_x, ground_y(post_x) + 2, 0.62, glow=glow)
    # toalha
    gy = ground_y(towel_x)
    ctx.move_to(towel_x - 55, gy + 1)
    ctx.line_to(towel_x + 55, gy + 1)
    ctx.line_to(towel_x + 52, gy - 4)
    ctx.line_to(towel_x - 52, gy - 4)
    ctx.close_path()
    ink(ctx, (0.95, 0.45, 0.40), 1, 2)
    for i in range(3):
        line(ctx, towel_x - 40 + i * 30, gy - 3, towel_x - 30 + i * 30, gy - 3, WHITE, 0.8, 2)
    # isopor
    gy = ground_y(cooler_x)
    rrect(ctx, cooler_x - 26, gy - 34, 52, 34, 5)
    ink(ctx, (0.25, 0.55, 0.85), 1, 2)
    rrect(ctx, cooler_x - 28, gy - 40, 56, 9, 3)
    ink(ctx, WHITE, 1, 2)
