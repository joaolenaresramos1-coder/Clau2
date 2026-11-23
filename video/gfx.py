"""Primitivas de desenho 2D no estilo dos vídeos de referência:
ilustração flat com contorno escuro, oceano azul-petróleo, tipografia Raleway em caixa alta espaçada."""
import math
import random
import cairo

W, H = 1280, 720
FPS = 24

# Paleta
DEEP_TOP = (0.05, 0.22, 0.27)
DEEP_BOT = (0.01, 0.05, 0.08)
TEAL = (0.20, 0.55, 0.58)
ORANGE = (0.95, 0.62, 0.24)
YELLOW = (0.96, 0.80, 0.30)
RED = (0.86, 0.27, 0.24)
GREEN = (0.32, 0.72, 0.62)
WHITE = (0.95, 0.96, 0.96)
SOFT = (0.72, 0.84, 0.86)
SAND = (0.84, 0.77, 0.60)
MAPLAND = (0.80, 0.71, 0.52)
JELLY = (0.74, 0.89, 0.96)
SKIN = (0.93, 0.74, 0.60)
SUIT = (0.13, 0.14, 0.16)
INK = (0.07, 0.08, 0.10)
BLUE_SUIT = (0.20, 0.42, 0.62)


# ---------------------------------------------------------------- tempo
def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def ease(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def appear(t, t0, d=0.5):
    return ease((t - t0) / d)


def lerp(a, b, k):
    return a + (b - a) * k


def window(t, t0, t1, d=0.4):
    return min(appear(t, t0, d), 1 - appear(t, t1 - d, d))


# ---------------------------------------------------------------- básicos
def rgba(ctx, c, a=1.0):
    ctx.set_source_rgba(c[0], c[1], c[2], a)


def ink(ctx, fill, a=1.0, lw=2.5):
    """Preenche o caminho atual e contorna com tinta escura (traço de ilustração)."""
    rgba(ctx, fill, a)
    ctx.fill_preserve()
    rgba(ctx, INK, a * 0.9)
    ctx.set_line_width(lw)
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.stroke()


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.close_path()


def circle(ctx, x, y, r, c, a=1.0):
    ctx.new_sub_path()
    ctx.arc(x, y, max(r, 0.01), 0, 2 * math.pi)
    rgba(ctx, c, a)
    ctx.fill()


def ellipse_path(ctx, x, y, rx, ry, rot=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(rx, ry)
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def line(ctx, x1, y1, x2, y2, c, a=1.0, w=3):
    ctx.move_to(x1, y1)
    ctx.line_to(x2, y2)
    rgba(ctx, c, a)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def limb(ctx, pts, w, c, a=1.0, outline=True):
    """Membro grosso com contorno: desenha o traço escuro e depois o preenchimento."""
    for pass_w, col in (((w + 4.5), INK), (w, c)) if outline else ((w, c),):
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        rgba(ctx, col, a * (0.9 if col is INK else 1))
        ctx.set_line_width(pass_w)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        ctx.stroke()


# ---------------------------------------------------------------- tipografia
FONTS = {"bold": "RalewayXB", "black": "RalewayBlack", "semi": "RalewaySemi", "light": "RalewayLight",
         "normal": "RalewaySemi"}


def font(ctx, size, weight="bold"):
    ctx.select_font_face(FONTS.get(weight, "RalewayXB"), cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)


def measure(ctx, s, size, weight="bold", sp=None):
    font(ctx, size, weight)
    sp = size * 0.06 if sp is None else sp
    w = 0
    for ch in s:
        w += ctx.text_extents(ch).x_advance + sp
    return w - sp


def _draw_spaced(ctx, s, x, y, sp):
    for ch in s:
        ctx.move_to(x, y)
        ctx.show_text(ch)
        x += ctx.text_extents(ch).x_advance + sp
    return x


def text(ctx, s, x, y, size=40, c=WHITE, a=1.0, align="c", weight="bold", rise=0.0, sp=None):
    if a <= 0.001 or not s:
        return 0
    sp = size * 0.06 if sp is None else sp
    w = measure(ctx, s, size, weight, sp)
    tx = x - w / 2 if align == "c" else x - w if align == "r" else x
    ty = y + (1 - rise) * 10 if rise else y
    rgba(ctx, (0, 0, 0), 0.45 * a)
    _draw_spaced(ctx, s, tx + 1.5, ty + 2, sp)
    rgba(ctx, c, a)
    _draw_spaced(ctx, s, tx, ty, sp)
    return w


def label(ctx, s, x, y, t, t0, t1=None, size=40, c=WHITE, align="c", weight="bold"):
    a = appear(t, t0) if t1 is None else window(t, t0, t1)
    if size <= 24 and weight == "bold":
        weight, sp = "semi", size * 0.16  # legendas pequenas: semi, bem espaçadas
    else:
        sp = None
    text(ctx, s, x, y, size, c, a, align, weight, rise=a, sp=sp)


def big_title(ctx, parts, x, y, t, t0, t1=None, size=46):
    """parts = [(texto, cor) | (texto, cor, peso)] na mesma linha, centralizado."""
    a = appear(t, t0) if t1 is None else window(t, t0, t1)
    if a <= 0:
        return
    parts = [p if len(p) == 3 else (p[0], p[1], "bold") for p in parts]
    widths = [measure(ctx, s + " ", size, wt) if s.endswith(" ") else measure(ctx, s, size, wt) for s, _, wt in parts]
    cx = x - sum(widths) / 2
    for (s, c, wt), w in zip(parts, widths):
        text(ctx, s, cx, y, size, c, a, "l", wt, rise=a)
        cx += w


def kicker(ctx, s, x, y, t, t0, t1=None, size=17, c=SOFT, align="c"):
    """Sobretítulo pequeno muito espaçado (ex.: '370 MILLION YEARS AGO')."""
    a = appear(t, t0) if t1 is None else window(t, t0, t1)
    text(ctx, s, x, y, size, c, a, align, "semi", rise=a, sp=size * 0.35)


def chapter(ctx, small, big1, big2, x, y, t, t0, t1=None, size=60, emblem=None):
    """Cartela de capítulo no estilo das referências: sobretítulo + título em dois pesos."""
    kicker(ctx, small, x, y - size * 0.95, t, t0, t1)
    a = appear(t, t0 + 0.2) if t1 is None else window(t, t0 + 0.2, t1)
    w1 = measure(ctx, big1 + " ", size, "black")
    w2 = measure(ctx, big2, size, "light")
    ex = 0
    if emblem and a > 0:
        ex = size * 0.9
        cx0 = x - (w1 + w2 + ex) / 2 + size * 0.32
        circle(ctx, cx0, y - size * 0.33, size * 0.38, (0.05, 0.1, 0.12), a)
        ctx.arc(cx0, y - size * 0.33, size * 0.38, 0, 2 * math.pi)
        rgba(ctx, ORANGE, a)
        ctx.set_line_width(2)
        ctx.stroke()
        emblem(ctx, cx0, y - size * 0.33, size * 0.2, a)
    sx = x - (w1 + w2 + ex) / 2 + ex
    text(ctx, big1 + " ", sx, y, size, WHITE, a, "l", "black", rise=a)
    text(ctx, big2, sx + w1, y, size, ORANGE, a, "l", "light", rise=a)


def name_tag(ctx, s, x, y, t, t0, t1=None, size=26):
    """Nome de espécie no canto, com sublinhado laranja (como 'Thalattoarchon')."""
    a = appear(t, t0) if t1 is None else window(t, t0, t1)
    if a <= 0:
        return
    w = text(ctx, s, x, y, size, WHITE, a, "l", "semi", sp=0.5)
    line(ctx, x, y + 9, x + w * ease((t - t0) / 0.8), y + 9, ORANGE, a, 2.5)


def callout(ctx, px, py, r, tx, ty, s, k, size=16):
    """Círculo tracejado amarelo + linha-guia + rótulo (como 'END OF THE CABLE')."""
    if k <= 0:
        return
    ctx.set_dash([5, 4])
    ctx.new_sub_path()
    ctx.arc(px, py, r * (0.7 + 0.3 * k), 0, 2 * math.pi)
    rgba(ctx, YELLOW, k)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.set_dash([])
    ang = math.atan2(ty - py, tx - px)
    sx, sy = px + math.cos(ang) * r, py + math.sin(ang) * r
    ex, ey = lerp(sx, tx, k), lerp(sy, ty, k)
    line(ctx, sx, sy, ex, ey, WHITE, 0.85 * k, 1.3)
    if k > 0.6:
        al = "l" if tx >= px else "r"
        text(ctx, s, tx + (8 if al == "l" else -8), ty + 5, size, WHITE, appear(k, 0.6, 0.4), al, "bold", sp=0.5)


# ---------------------------------------------------------------- fundos
_rng = random.Random(7)
PARTS = [(_rng.random(), _rng.random(), _rng.uniform(0.6, 2.0), _rng.uniform(0.2, 0.6), _rng.random())
         for _ in range(110)]
BOKEH = [(_rng.random(), _rng.random(), _rng.uniform(8, 22), _rng.uniform(0.05, 0.2), _rng.random())
         for _ in range(14)]

_GRAIN = None


def grain(ctx, a=0.06, t=0.0):
    global _GRAIN
    if _GRAIN is None:
        import numpy as np
        rnd = np.random.default_rng(3)
        v = rnd.integers(0, 256, (512, 512), dtype=np.uint8)
        global _GRAIN_DATA
        _GRAIN_DATA = np.dstack([v, v, v, np.full_like(v, 255)]).copy()
        _GRAIN = cairo.ImageSurface.create_for_data(memoryview(_GRAIN_DATA), cairo.FORMAT_ARGB32, 512, 512)
    ctx.save()
    pat = cairo.SurfacePattern(_GRAIN)
    pat.set_extend(cairo.EXTEND_REPEAT)
    m = cairo.Matrix()
    off = int(t * 24) % 7
    m.translate(off * 37, off * 53)
    pat.set_matrix(m)
    ctx.set_source(pat)
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
    ctx.paint_with_alpha(a)
    ctx.restore()


DISTANT = [(_rng.random(), _rng.uniform(0.15, 0.75), _rng.uniform(0.18, 0.32), _rng.uniform(4, 9), _rng.random())
           for _ in range(4)]


def ocean(ctx, t, top=DEEP_TOP, bot=DEEP_BOT, rays=True, particles=True, light=1.0, distant=True):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(1, *bot)
    ctx.set_source(g)
    ctx.paint()
    if rays:
        for i in range(7):
            x0 = W * (0.05 + i * 0.15) + math.sin(t * 0.25 + i * 1.3) * 35
            wdt = 30 + 25 * abs(math.sin(i * 1.7))
            g = cairo.LinearGradient(0, 0, 0, H * 0.95)
            g.add_color_stop_rgba(0, 0.65, 0.92, 0.95, (0.07 + 0.04 * math.sin(t * 0.5 + i)) * light)
            g.add_color_stop_rgba(1, 0.65, 0.92, 0.95, 0.0)
            ctx.move_to(x0 - wdt, 0)
            ctx.line_to(x0 + wdt, 0)
            ctx.line_to(x0 + wdt * 2.5 + 140, H * 0.95)
            ctx.line_to(x0 + 70, H * 0.95)
            ctx.close_path()
            ctx.set_source(g)
            ctx.fill()
    if distant:
        for px, py, sc, sp, ph in DISTANT:
            x = ((px * (W + 300) + t * sp) % (W + 300)) - 150
            y = H * py + math.sin(t * 0.2 + ph * 6) * 20
            box_jelly(ctx, x, y, sc, t * 0.7, a=0.13, tents_per=2, phase=ph * 6, col=(0.55, 0.75, 0.82))
    if particles:
        for px, py, r, sp, ph in PARTS:
            x = (px * W + math.sin(t * 0.4 + ph * 6) * 15) % W
            y = (py * H - t * sp * 10) % H
            circle(ctx, x, y, r, (0.8, 0.92, 0.95), 0.22 + 0.18 * math.sin(t + ph * 9))
        for px, py, r, aa, ph in BOKEH:
            x = (px * W + t * 4 * (ph - 0.5)) % W
            y = (py * H - t * 3) % H
            g = cairo.RadialGradient(x, y, 0, x, y, r)
            g.add_color_stop_rgba(0, 0.8, 0.92, 0.95, aa)
            g.add_color_stop_rgba(1, 0.8, 0.92, 0.95, 0)
            ctx.set_source(g)
            ctx.arc(x, y, r, 0, 2 * math.pi)
            ctx.fill()


def night(ctx, t):
    ocean(ctx, t, top=(0.04, 0.07, 0.10), bot=(0.01, 0.02, 0.04), rays=False)


def vignette(ctx, a=0.6, t=0.0):
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.35, W / 2, H / 2, H * 0.95)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0, 0, 0, a)
    ctx.set_source(g)
    ctx.paint()
    grain(ctx, 0.10, t)


def seabed(ctx, t, y=H * 0.86, c=(0.55, 0.55, 0.52)):
    """Fundo do mar com pedras e estrelas-do-mar laranja (como nas referências)."""
    ctx.move_to(0, y)
    for x in range(0, W + 80, 80):
        ctx.line_to(x, y + math.sin(x * 0.013) * 6)
    ctx.line_to(W, H)
    ctx.line_to(0, H)
    ctx.close_path()
    ink(ctx, c, 1, 2)
    rnd = random.Random(11)
    for i in range(9):
        x = rnd.uniform(0, W)
        ellipse_path(ctx, x, y + 6, rnd.uniform(18, 40), rnd.uniform(6, 11))
        ink(ctx, (0.42, 0.44, 0.43), 1, 2)
    for i in range(5):
        star(ctx, rnd.uniform(30, W - 30), y + rnd.uniform(16, 50), rnd.uniform(8, 12))


def star(ctx, x, y, r, c=ORANGE):
    ctx.move_to(x + r, y)
    for k in range(1, 11):
        ang = k * math.pi / 5
        rr = r if k % 2 == 0 else r * 0.42
        ctx.line_to(x + math.cos(ang - math.pi / 2) * rr, y + math.sin(ang - math.pi / 2) * rr)
    ctx.close_path()
    rgba(ctx, c)
    ctx.fill()


def surface_line(ctx, t, y, sky=True):
    """Linha d'água vista de lado: céu claro acima, água abaixo."""
    if sky:
        g = cairo.LinearGradient(0, 0, 0, y)
        g.add_color_stop_rgb(0, 0.62, 0.78, 0.84)
        g.add_color_stop_rgb(1, 0.88, 0.92, 0.92)
        ctx.set_source(g)
        ctx.rectangle(0, 0, W, y)
        ctx.fill()
    ctx.move_to(0, y)
    for x in range(0, W + 20, 20):
        ctx.line_to(x, y + math.sin(x * 0.03 + t * 2) * 2.5)
    rgba(ctx, WHITE, 0.9)
    ctx.set_line_width(2.5)
    ctx.stroke()
    g = cairo.LinearGradient(0, y, 0, y + 60)
    g.add_color_stop_rgba(0, 0.8, 0.95, 0.95, 0.35)
    g.add_color_stop_rgba(1, 0.8, 0.95, 0.95, 0)
    ctx.set_source(g)
    ctx.rectangle(0, y, W, 60)
    ctx.fill()


def sky_beach(ctx, t, horizon=0.48, sunset=1.0, cam=0.0, mid=None):
    hy = H * horizon
    g = cairo.LinearGradient(0, 0, 0, hy)
    g.add_color_stop_rgb(0, lerp(0.55, 0.40, sunset), lerp(0.74, 0.58, sunset), lerp(0.86, 0.76, sunset))
    g.add_color_stop_rgb(1, lerp(0.88, 0.97, sunset), lerp(0.92, 0.80, sunset), lerp(0.93, 0.64, sunset))
    ctx.set_source(g)
    ctx.rectangle(0, 0, W, hy)
    ctx.fill()
    # nuvens
    for i in range(4):
        cx = (W * (0.15 + i * 0.25) - cam * 0.1 + t * 3) % (W + 300) - 150
        for dx, r in ((-40, 22), (0, 32), (40, 24)):
            circle(ctx, cx + dx, H * (0.12 + 0.05 * (i % 2)), r, WHITE, 0.35)
    sx = W * 0.72 - cam * 0.2
    circle(ctx, sx, hy - 40, 90, (1.0, 0.92, 0.72), 0.14)
    circle(ctx, sx, hy - 40, 44, (1.0, 0.93, 0.74), 0.95)
    g = cairo.LinearGradient(0, hy, 0, H * 0.72)
    g.add_color_stop_rgb(0, 0.20, 0.52, 0.60)
    g.add_color_stop_rgb(1, 0.42, 0.78, 0.78)
    ctx.set_source(g)
    ctx.rectangle(0, hy, W, H)
    ctx.fill()
    line(ctx, 0, hy, W, hy, INK, 0.5, 2)
    for i in range(8):
        yy = hy + 10 + i * 13
        ww = 60 - i * 5 + math.sin(t * 2 + i) * 10
        line(ctx, sx - ww, yy, sx + ww, yy, (1, 0.95, 0.8), 0.55, 3)
    for i in range(3):
        yy = H * 0.66 + i * 9 + math.sin(t * 1.2 + i) * 3
        ctx.move_to(0, yy)
        for x in range(0, W + 40, 40):
            ctx.line_to(x, yy + math.sin(x * 0.02 + t * 1.5 + i) * 3)
        rgba(ctx, WHITE, 0.4)
        ctx.set_line_width(2)
        ctx.stroke()
    if mid:
        mid(ctx)
    ctx.move_to(0, H * 0.70)
    ctx.curve_to(W * 0.3, H * 0.68, W * 0.6, H * 0.74, W, H * 0.71)
    ctx.line_to(W, H + 5)
    ctx.line_to(-5, H + 5)
    ctx.close_path()
    ink(ctx, SAND, 1, 2.5)
    rnd = random.Random(5)
    for i in range(40):
        circle(ctx, rnd.uniform(0, W), rnd.uniform(H * 0.75, H), rnd.uniform(1, 2.5), (0.7, 0.62, 0.45), 0.6)
    palm(ctx, 120 - cam, H * 0.72, 1.0, t)
    palm(ctx, W - 90 - cam * 1.3, H * 0.74, 1.2, t + 1)


def palm(ctx, x, y, s, t):
    for lw, col in ((14 * s, INK), (10 * s, (0.47, 0.35, 0.24))):
        ctx.move_to(x, y)
        ctx.curve_to(x + 10 * s, y - 120 * s, x + 30 * s, y - 200 * s, x + 50 * s, y - 260 * s)
        rgba(ctx, col)
        ctx.set_line_width(lw)
        ctx.stroke()
    tx, ty = x + 50 * s, y - 260 * s
    for k in range(7):
        ang = -math.pi + k * (math.pi / 6) + math.sin(t + k) * 0.05
        ex, ey = tx + math.cos(ang) * 110 * s, ty + math.sin(ang) * 60 * s + 40 * s
        for lw, col in ((13 * s, INK), (9 * s, (0.20, 0.47, 0.34))):
            ctx.move_to(tx, ty)
            ctx.curve_to(tx + math.cos(ang) * 50 * s, ty - 30 * s, ex, ey - 30 * s, ex, ey)
            rgba(ctx, col)
            ctx.set_line_width(lw)
            ctx.stroke()


def post_bottle(ctx, x, y, s=1.0, a=1.0, glow=0.0):
    ctx.rectangle(x - 7 * s, y - 170 * s, 14 * s, 170 * s)
    ink(ctx, (0.50, 0.36, 0.24), a, 2.5)
    rrect(ctx, x - 48 * s, y - 210 * s, 96 * s, 52 * s, 6 * s)
    ink(ctx, (0.96, 0.82, 0.28), a, 2.5)
    for i in range(3):
        line(ctx, x - 34 * s, y - (196 - i * 13) * s, x + 34 * s - i * 14 * s, y - (196 - i * 13) * s,
             (0.3, 0.22, 0.1), a * 0.8, 3 * s)
    if glow > 0:
        g = cairo.RadialGradient(x + 22 * s, y - 120 * s, 0, x + 22 * s, y - 120 * s, 55 * s)
        g.add_color_stop_rgba(0, ORANGE[0], ORANGE[1], ORANGE[2], 0.5 * glow * a)
        g.add_color_stop_rgba(1, ORANGE[0], ORANGE[1], ORANGE[2], 0)
        ctx.set_source(g)
        ctx.paint()
    rrect(ctx, x + 10 * s, y - 145 * s, 24 * s, 50 * s, 6 * s)
    ink(ctx, (0.92, 0.95, 0.97), a, 2)
    ctx.rectangle(x + 15 * s, y - 155 * s, 14 * s, 11 * s)
    ink(ctx, ORANGE, a, 2)


# ---------------------------------------------------------------- criaturas
def box_jelly(ctx, x, y, s, t, a=1.0, cube=1.0, tent=1.0, col=JELLY, tents_per=5, glow=0.0, phase=0.0):
    pulse = 1 + 0.05 * math.sin(t * 2.2 + phase)
    w = 120 * s * pulse
    h = 105 * s / pulse ** 0.5
    y = y + math.sin(t * 1.1 + phase) * 4 * s
    if glow > 0:
        g = cairo.RadialGradient(x, y, 10, x, y, 220 * s)
        g.add_color_stop_rgba(0, col[0], col[1], col[2], 0.22 * glow * a)
        g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
        ctx.set_source(g)
        ctx.paint()
    corners = [(-0.5, 1.0), (-0.22, 0.55), (0.22, 0.55), (0.5, 1.0)]
    L = 260 * s * tent
    for ci, (cxk, depth) in enumerate(corners):
        # pedálio (base do feixe)
        bx = x + cxk * w * 0.92
        ellipse_path(ctx, bx, y + h * 0.48, 7 * s, 11 * s)
        rgba(ctx, col, a * 0.5 * depth)
        ctx.fill()
        for k in range(tents_per):
            spread = (k - (tents_per - 1) / 2) * 4 * s
            ph = phase + ci * 1.3 + k * 0.7
            ctx.move_to(bx + spread, y + h * 0.5)
            n = 24
            for j in range(1, n + 1):
                f = j / n
                xx = bx + spread * (1 + f * 2) + math.sin(t * 1.6 + ph + f * 5) * 16 * s * f
                yy = y + h * 0.5 + f * L * (0.85 + 0.15 * math.sin(ph))
                ctx.line_to(xx, yy)
            g = cairo.LinearGradient(0, y + h * 0.5, 0, y + h * 0.5 + L)
            g.add_color_stop_rgba(0, col[0], col[1], col[2], a * (0.4 + 0.4 * depth))
            g.add_color_stop_rgba(1, col[0], col[1], col[2], a * 0.05)
            ctx.set_source(g)
            ctx.set_line_width(max(0.8, 1.7 * s))
            ctx.stroke()
    top = y - h * 0.55
    bot = y + h * 0.45
    side_top = lerp(0.55, 0.95, cube)
    ctx.move_to(x - w / 2, bot)
    ctx.line_to(x - w / 2 * side_top, lerp(y - h * 0.05, top + h * 0.2, cube))
    ctx.curve_to(x - w / 2 * lerp(0.4, 0.8, cube), top, x + w / 2 * lerp(0.4, 0.8, cube), top,
                 x + w / 2 * side_top, lerp(y - h * 0.05, top + h * 0.2, cube))
    ctx.line_to(x + w / 2, bot)
    ctx.curve_to(x + w * 0.2, bot - 8 * s, x - w * 0.2, bot - 8 * s, x - w / 2, bot)
    ctx.close_path()
    g = cairo.LinearGradient(x - w / 2, top, x + w / 2, bot)
    g.add_color_stop_rgba(0, col[0], col[1], col[2], a * 0.45)
    g.add_color_stop_rgba(1, col[0], col[1], col[2], a * 0.15)
    ctx.set_source(g)
    ctx.fill_preserve()
    rgba(ctx, col, a * 0.9)
    ctx.set_line_width(2.2 * s if s > 0.5 else 1.2)
    ctx.stroke()
    # brilho
    ctx.move_to(x - w * 0.33, top + h * 0.25)
    ctx.curve_to(x - w * 0.3, top + h * 0.1, x - w * 0.1, top + h * 0.05, x, top + h * 0.06)
    rgba(ctx, WHITE, a * 0.5)
    ctx.set_line_width(2 * s)
    ctx.stroke()
    if cube > 0.3:
        for k in (-0.22, 0.22):
            line(ctx, x + k * w, top + h * 0.12, x + k * w * 1.15, bot - 4 * s, col, a * 0.4 * cube, 1.4 * s)
    # manúbrio (estômago)
    ctx.move_to(x - 8 * s, top + h * 0.3)
    ctx.curve_to(x - 14 * s, bot, x + 14 * s, bot, x + 8 * s, top + h * 0.3)
    rgba(ctx, (0.95, 0.72, 0.62), a * 0.45)
    ctx.fill()
    for k in (-0.36, 0.36):
        circle(ctx, x + k * w, bot - 14 * s, 3.5 * s, (0.95, 0.70, 0.45), a * 0.95)


def iruk(ctx, x, y, s, t, a=1.0):
    w = 30 * s
    h = 34 * s
    y = y + math.sin(t * 1.4) * 3
    for k, cx in enumerate((-0.45, -0.15, 0.15, 0.45)):
        ctx.move_to(x + cx * w, y + h * 0.4)
        for j in range(1, 30):
            f = j / 29
            ctx.line_to(x + cx * w + math.sin(t * 1.5 + k + f * 6) * 10 * s * f, y + h * 0.4 + f * 220 * s)
        rgba(ctx, JELLY, a * 0.6)
        ctx.set_line_width(1.0)
        ctx.stroke()
        # nematocistos em "contas"
        for j in range(3, 29, 4):
            f = j / 29
            circle(ctx, x + cx * w + math.sin(t * 1.5 + k + f * 6) * 10 * s * f, y + h * 0.4 + f * 220 * s,
                   1.4 * s, (0.95, 0.6, 0.6), a * 0.8)
    rrect(ctx, x - w / 2, y - h / 2, w, h, w * 0.3)
    rgba(ctx, JELLY, a * 0.35)
    ctx.fill_preserve()
    rgba(ctx, JELLY, a)
    ctx.set_line_width(1.5)
    ctx.stroke()
    circle(ctx, x - w * 0.15, y, 2 * s, RED, a * 0.8)
    circle(ctx, x + w * 0.2, y + 4 * s, 2 * s, RED, a * 0.8)


OUTFITS = {
    # nome: (cor do corpo, cor das pernas, cor das mãos, cor dos pés, cilindro, máscara)
    "diver": (SUIT, SUIT, ORANGE, ORANGE, True, True),
    "swim": (BLUE_SUIT, SKIN, SKIN, SKIN, False, False),
    "red": ((0.82, 0.32, 0.28), SKIN, SKIN, SKIN, False, False),
    "kid": ((0.88, 0.58, 0.25), SKIN, SKIN, SKIN, False, False),
    "lifeguard": ((0.86, 0.26, 0.22), (0.95, 0.80, 0.25), SKIN, SKIN, False, False),
    "lycra": ((0.10, 0.18, 0.42), (0.10, 0.18, 0.42), SKIN, SKIN, False, False),
}


def person(ctx, x, y, s, a=1.0, body=None, skin=SKIN, accent=None, pose="stand", t=0.0, rot=0.0,
           arm=0.0, legs_skin=False, stockings=False, outfit=None, kick=0.0):
    """Personagem articulado com contorno. (x,y) = pés. Compatível com chamadas antigas."""
    if outfit is None:
        if body is None:
            outfit = "swim"
        else:
            outfit = None
    if outfit:
        bc, lc, hc, fc, tank, mask = OUTFITS[outfit]
    else:
        bc = body
        lc = skin if legs_skin else body
        hc, fc, tank, mask = skin, skin, False, False
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot)
    ctx.scale(s, s)
    if pose == "kneel":
        ctx.translate(0, 50)
    elif pose in ("walk", "run"):
        ctx.translate(0, -abs(math.sin(t * (3 if pose == "walk" else 6))) * 4)
    else:
        ctx.translate(0, math.sin(t * 1.6) * 0.8)  # respiração
    sw = math.sin(t * 3) * 0.3 if pose == "walk" else math.sin(t * 6) * 0.55 if pose == "run" else kick * math.sin(t * 5)
    hip_y, sh_y = -100, -170
    # braço de trás
    ang = math.radians(18 + arm)
    elb = (-24 - math.sin(ang) * 34, sh_y + math.cos(ang) * 34)
    hand = (elb[0] - math.sin(ang * 1.2) * 34, elb[1] + math.cos(ang * 1.2) * 34)
    limb(ctx, [(-18, sh_y + 6), elb, hand], 13, bc, a)
    circle(ctx, hand[0], hand[1], 7.5, INK, a)
    circle(ctx, hand[0], hand[1], 6, hc, a)
    # pernas
    for side, ph in ((-1, sw), (1, -sw)):
        knee = (side * 10 + ph * 22, hip_y + 48)
        foot = (side * 11 + ph * 44, -6)
        if pose == "kneel":
            knee = (side * 6 + 40, -58)
            foot = (side * 4 - 20, -52)
        limb(ctx, [(side * 9, hip_y), knee, foot], 15, lc, a)
        if stockings:
            limb(ctx, [(side * 9, hip_y + 10), knee, foot], 15, (0.86, 0.68, 0.52), a * 0.7, outline=False)
        if outfit == "diver":
            ctx.move_to(foot[0] - 6, foot[1] - 4)
            ctx.line_to(foot[0] + side * 4 + 8, foot[1] + 18)
            ctx.line_to(foot[0] - 12, foot[1] + 18)
            ctx.close_path()
            ink(ctx, fc, a, 2)
        else:
            ellipse_path(ctx, foot[0] + 4, foot[1] + 1, 10, 5)
            ink(ctx, fc, a, 2)
    # calção
    if outfit in ("swim", "red", "kid", "lifeguard"):
        rrect(ctx, -21, hip_y - 14, 42, 34, 8)
        ink(ctx, (0.15, 0.22, 0.35) if outfit != "lifeguard" else (0.95, 0.80, 0.25), a, 2.5)
    # cilindro
    if tank:
        rrect(ctx, -34, sh_y - 4, 22, 70, 9)
        ink(ctx, YELLOW, a, 2.5)
    # tronco
    ctx.move_to(-22, sh_y)
    ctx.curve_to(-26, sh_y + 30, -22, hip_y - 10, -18, hip_y + 4)
    ctx.line_to(18, hip_y + 4)
    ctx.curve_to(22, hip_y - 10, 26, sh_y + 30, 22, sh_y)
    ctx.curve_to(10, sh_y - 10, -10, sh_y - 10, -22, sh_y)
    ctx.close_path()
    ink(ctx, bc, a, 2.5)
    if tank:
        line(ctx, -16, sh_y + 2, 4, hip_y - 6, (0.3, 0.3, 0.32), a, 4)
    # braço da frente
    ang = math.radians(18 + arm)
    elb = (24 + math.sin(ang) * 34, sh_y + math.cos(ang) * 34)
    hand = (elb[0] + math.sin(ang * 1.2) * 34, elb[1] + math.cos(ang * 1.2) * 34)
    limb(ctx, [(18, sh_y + 6), elb, hand], 13, bc, a)
    circle(ctx, hand[0], hand[1], 7.5, INK, a)
    circle(ctx, hand[0], hand[1], 6, hc, a)
    # cabeça
    ctx.new_sub_path()
    ctx.arc(0, sh_y - 30, 21, 0, 2 * math.pi)
    if mask:
        ink(ctx, SUIT, a, 2.5)
        rrect(ctx, -8, sh_y - 42, 26, 17, 6)
        ink(ctx, (0.55, 0.62, 0.66), a, 2.5)
        line(ctx, 10, sh_y - 22, 24, sh_y - 12, (0.3, 0.3, 0.32), a, 4)
    else:
        ink(ctx, skin, a, 2.5)
        ctx.arc(0, sh_y - 34, 21, math.pi * 1.05, math.pi * 1.95)
        rgba(ctx, (0.30, 0.20, 0.14), a)
        ctx.set_line_width(9)
        ctx.stroke()
        circle(ctx, 8, sh_y - 30, 2.2, INK, a)
    ctx.restore()


def fish(ctx, x, y, s, t, c=(0.75, 0.8, 0.85), a=1.0, flip=1, wiggle=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * flip, s)
    ctx.rotate(math.sin(t * 12) * wiggle)
    ctx.move_to(-24, 0)
    ctx.line_to(-46, -14 + math.sin(t * 8) * 4)
    ctx.line_to(-46, 14 + math.sin(t * 8) * 4)
    ctx.close_path()
    ink(ctx, c, a, 2 / s)
    ellipse_path(ctx, 0, 0, 30, 13.5)
    ink(ctx, c, a, 2 / s)
    ellipse_path(ctx, 2, 4, 22, 6)
    rgba(ctx, WHITE, a * 0.4)
    ctx.fill()
    circle(ctx, 16, -3, 3, INK, a)
    ctx.restore()


def shrimp(ctx, x, y, s, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    line(ctx, -28, 4, -55, -20, (0.95, 0.55, 0.45), a, 1.5)
    line(ctx, -28, 4, -58, -8, (0.95, 0.55, 0.45), a, 1.5)
    for i in range(6):
        ang = math.pi * 0.9 - i * 0.28
        ctx.new_sub_path()
        ctx.arc(math.cos(ang) * 28, math.sin(ang) * -18, 9 - i * 0.8, 0, 2 * math.pi)
        ink(ctx, (0.95, 0.55, 0.45), a, 1.5)
    circle(ctx, -24, 0, 2, INK, a)
    ctx.restore()


def turtle(ctx, x, y, s, t, a=1.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    fl = math.sin(t * 2) * 0.4
    for sx, sy, ang in ((1, -1, -0.6 - fl), (1, 1, 0.6 + fl), (-1, -1, -2.5 + fl), (-1, 1, 2.5 - fl)):
        ellipse_path(ctx, sx * 30 + math.cos(ang) * 30, sy * 30 + math.sin(ang) * 30, 32, 13, ang)
        ink(ctx, (0.45, 0.6, 0.42), a, 2.5)
    ctx.new_sub_path()
    ctx.arc(88, 0, 20, 0, 2 * math.pi)
    ink(ctx, (0.5, 0.65, 0.45), a, 2.5)
    circle(ctx, 98, -6, 3, INK, a)
    ellipse_path(ctx, 0, 0, 72, 52)
    ink(ctx, (0.36, 0.46, 0.28), a, 3)
    for i in range(-1, 2):
        for j in range(-1, 2):
            if abs(i) + abs(j) < 2:
                ellipse_path(ctx, i * 34, j * 26, 15, 11)
                ink(ctx, (0.5, 0.58, 0.35), a * 0.9, 1.5)
    ctx.restore()


# ---------------------------------------------------------------- ícones
def icon(ctx, kind, x, y, s, a=1.0, c=WHITE):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.set_line_width(5)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    rgba(ctx, c, a)
    if kind == "brain":
        ellipse_path(ctx, 0, 0, 40, 30)
        ink(ctx, (0.92, 0.65, 0.68), a, 3)
        for k in range(-2, 3):
            ctx.move_to(k * 12, -24)
            ctx.curve_to(k * 12 + 10, -8, k * 12 - 10, 8, k * 12, 24)
        rgba(ctx, (0.6, 0.3, 0.35), a)
        ctx.set_line_width(2.5)
        ctx.stroke()
    elif kind == "bone":
        limb(ctx, [(-26, 0), (26, 0)], 11, (0.93, 0.9, 0.82), a)
        for sx in (-1, 1):
            for sy in (-1, 1):
                ctx.new_sub_path()
                ctx.arc(sx * 30, sy * 8, 10, 0, 2 * math.pi)
                ink(ctx, (0.93, 0.9, 0.82), a, 2.5)
        limb(ctx, [(-26, 0), (26, 0)], 11, (0.93, 0.9, 0.82), a, outline=False)
    elif kind == "heart":
        ctx.move_to(0, 30)
        ctx.curve_to(-50, -5, -25, -45, 0, -18)
        ctx.curve_to(25, -45, 50, -5, 0, 30)
        ink(ctx, c if c != WHITE else RED, a, 3)
    elif kind == "drop":
        ctx.move_to(0, -38)
        ctx.curve_to(10, -15, 28, 0, 28, 14)
        ctx.arc(0, 14, 28, 0, math.pi)
        ctx.curve_to(-28, 0, -10, -15, 0, -38)
        ink(ctx, (0.78, 0.18, 0.2), a, 3)
    elif kind == "eye":
        ctx.move_to(-40, 0)
        ctx.curve_to(-15, -30, 15, -30, 40, 0)
        ctx.curve_to(15, 30, -15, 30, -40, 0)
        ink(ctx, WHITE, a, 3)
        ctx.new_sub_path()
        ctx.arc(0, 0, 13, 0, 2 * math.pi)
        ink(ctx, (0.3, 0.55, 0.65), a, 2)
        circle(ctx, 0, 0, 6, INK, a)
    elif kind == "bottle":
        rrect(ctx, -14, -25, 28, 55, 6)
        ink(ctx, (0.92, 0.95, 0.97), a, 2.5)
        rrect(ctx, -10, -5, 20, 18, 3)
        rgba(ctx, ORANGE, a * 0.8)
        ctx.fill()
        ctx.rectangle(-8, -36, 16, 12)
        ink(ctx, ORANGE, a, 2.5)
    elif kind == "stocking":
        ctx.move_to(-8, -35)
        ctx.line_to(-8, 18)
        ctx.curve_to(-8, 34, 24, 34, 28, 22)
        ctx.line_to(10, 14)
        ctx.line_to(10, -35)
        ctx.close_path()
        ink(ctx, (0.88, 0.70, 0.56), a, 2.5)
    elif kind == "fallen":
        ctx.restore()
        person(ctx, x + 45 * s, y + 5 * s, 0.32 * s, a, outfit="red", rot=-math.pi / 2)
        return
    elif kind == "phone":
        rrect(ctx, -16, -30, 32, 60, 6)
        ink(ctx, (0.2, 0.22, 0.25), a, 2.5)
        rrect(ctx, -12, -24, 24, 44, 3)
        rgba(ctx, (0.5, 0.75, 0.85), a)
        ctx.fill()
    elif kind == "cross":
        ctx.rectangle(-8, -26, 16, 52)
        ctx.rectangle(-26, -8, 52, 16)
        rgba(ctx, c, a)
        ctx.fill()
    ctx.restore()


def xmark(ctx, x, y, r, k, c=RED, a=1.0):
    if k <= 0:
        return
    k1, k2 = clamp(k * 2), clamp(k * 2 - 1)
    for lw, col in ((10, INK), (7, c)):
        line(ctx, x - r, y - r, x - r + 2 * r * k1, y - r + 2 * r * k1, col, a, lw)
        if k2 > 0:
            line(ctx, x + r, y - r, x + r - 2 * r * k2, y - r + 2 * r * k2, col, a, lw)


def check(ctx, x, y, r, k, c=GREEN, a=1.0):
    if k <= 0:
        return
    ctx.new_sub_path()
    ctx.arc(x, y, r * k, 0, 2 * math.pi)
    ink(ctx, c, a * k, 2)
    ctx.move_to(x - r * 0.45, y)
    ctx.line_to(x - r * 0.1, y + r * 0.35)
    ctx.line_to(x + r * 0.5, y - r * 0.35)
    rgba(ctx, WHITE, a * k)
    ctx.set_line_width(r * 0.2)
    ctx.stroke()


def card(ctx, x, y, w, h, a=1.0, fill=(0.05, 0.13, 0.16), border=(0.45, 0.62, 0.66)):
    rrect(ctx, x, y, w, h, 8)
    rgba(ctx, fill, a * 0.88)
    ctx.fill_preserve()
    rgba(ctx, border, a * 0.7)
    ctx.set_line_width(1.5)
    ctx.stroke()


def timer(ctx, x, y, r, k, a=1.0, label_txt=None):
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ink(ctx, (0.05, 0.11, 0.14), a * 0.95, 3)
    for i in range(12):
        ang = i * math.pi / 6
        line(ctx, x + math.cos(ang) * (r - 6), y + math.sin(ang) * (r - 6), x + math.cos(ang) * (r - 16),
             y + math.sin(ang) * (r - 16), SOFT, a * 0.6, 2)
    if k > 0:
        ctx.arc(x, y, r - 26, -math.pi / 2, -math.pi / 2 + 2 * math.pi * k)
        rgba(ctx, RED if k > 0.95 else ORANGE, a)
        ctx.set_line_width(10)
        ctx.stroke()
    if label_txt:
        text(ctx, label_txt, x, y + r * 0.13, r * 0.36, WHITE, a, weight="black")


# ---------------------------------------------------------------- animação
def kf(t, keys, fn=None):
    """Interpola valores (números ou tuplas) entre quadros-chave [(tempo, valor), ...] com easing."""
    fn = fn or ease
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            k = fn((t - t0) / max(1e-6, t1 - t0))
            if isinstance(v0, tuple):
                return tuple(a + (b - a) * k for a, b in zip(v0, v1))
            return v0 + (v1 - v0) * k
    return keys[-1][1]


def bubbles(ctx, x, y, t, n=10, rise=140, a=1.0, seed=0, spread=10, speed=0.7):
    """Trilha de bolhas subindo a partir de (x, y)."""
    for k in range(n):
        ph = (t * speed + k / n + seed * 0.37) % 1.0
        bx = x + math.sin(k * 7.1 + t * 3 + seed) * spread * ph
        by = y - ph * rise
        r = 1.5 + 3.5 * ph * (0.6 + 0.4 * math.sin(k * 3.3))
        aa = a * (1 - ph) * 0.9
        ctx.new_sub_path()
        ctx.arc(bx, by, r, 0, 2 * math.pi)
        rgba(ctx, (0.85, 0.95, 1.0), aa * 0.25)
        ctx.fill_preserve()
        rgba(ctx, (0.9, 0.97, 1.0), aa)
        ctx.set_line_width(1.2)
        ctx.stroke()


def splash(ctx, x, y, t, t0, a=1.0, size=1.0):
    """Respingo na superfície em t0."""
    k = (t - t0) / 1.2
    if not (0 <= k <= 1):
        return
    for i in range(14):
        ang = math.pi + (i + 0.5) / 14 * math.pi
        d = 70 * size * ease(k)
        px = x + math.cos(ang) * d
        py = y + math.sin(ang) * d * 0.9 + 140 * size * k * k
        circle(ctx, px, py, 4 * size * (1 - k) + 1, (0.92, 0.98, 1.0), a * (1 - k))
    ellipse_path(ctx, x, y, 60 * size * ease(k) + 5, 8 * size * ease(k) + 1)
    rgba(ctx, WHITE, a * (1 - k) * 0.8)
    ctx.set_line_width(2.5)
    ctx.stroke()


def swimmer(ctx, x, y, s, t, a=1.0, outfit="swim", facing=1, speed=1.0, tilt=0.0, stroke=True):
    """Pessoa nadando na horizontal: pernas batendo, braços em braçada."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(-facing, 1)
    ctx.rotate(-tilt)
    arm = (150 + math.sin(t * 4 * speed) * 22) if stroke else 60
    person(ctx, 95 * s, 0, s, a, rot=-math.pi / 2, outfit=outfit, kick=1.0 * speed, t=t, arm=arm)
    ctx.restore()


def scale_bar(ctx, x1, x2, y, k, lab, a=1.0):
    """Barra amarela de escala com marcas nas pontas e rótulo (como '5 m')."""
    if k <= 0:
        return
    xe = lerp(x1, x2, ease(k))
    line(ctx, x1, y, xe, y, YELLOW, a, 2.5)
    line(ctx, x1, y - 8, x1, y + 8, YELLOW, a, 2.5)
    if k >= 0.99:
        line(ctx, x2, y - 8, x2, y + 8, YELLOW, a, 2.5)
        text(ctx, lab, (x1 + x2) / 2, y + 28, 18, YELLOW, a * appear(k, 0.99, 0.01), "c", "bold", sp=0.5)


def flashlight(ctx, x, y, ang, length=380, spread=0.28, a=1.0):
    g = cairo.RadialGradient(x, y, 5, x, y, length)
    g.add_color_stop_rgba(0, 0.95, 0.97, 0.9, 0.55 * a)
    g.add_color_stop_rgba(1, 0.95, 0.97, 0.9, 0)
    ctx.move_to(x, y)
    ctx.line_to(x + math.cos(ang - spread) * length, y + math.sin(ang - spread) * length)
    ctx.line_to(x + math.cos(ang + spread) * length, y + math.sin(ang + spread) * length)
    ctx.close_path()
    ctx.set_source(g)
    ctx.fill()


def school(ctx, cx, cy, t, n=14, spread=120, s=0.35, a=1.0, seed=1, c=(0.5, 0.6, 0.65), speed=30):
    rnd = random.Random(seed)
    for i in range(n):
        ox, oy = rnd.uniform(-spread, spread), rnd.uniform(-spread * 0.4, spread * 0.4)
        x = cx + ox + math.sin(t * 0.8 + i) * 10 + t * speed * 0
        y = cy + oy + math.sin(t * 1.3 + i * 2) * 6
        fish(ctx, x, y, s, t + i, c=c, a=a)


def sea_color(y):
    k = clamp((y - H * 0.48) / (H * 0.24))
    return (lerp(0.20, 0.42, k), lerp(0.52, 0.78, k), lerp(0.60, 0.78, k))


def wade(ctx, x, feet_y, s, depth, t, a=1.0, **kw):
    """Pessoa dentro da água rasa: a água cobre o corpo até a profundidade 'depth' (0..1 do corpo)."""
    person(ctx, x, feet_y, s, a, t=t, **kw)
    if depth <= 0:
        return
    wl = feet_y - depth * 210 * s
    ctx.rectangle(x - 45 * s, wl, 90 * s, feet_y - wl + 6)
    g = cairo.LinearGradient(0, H * 0.48, 0, H * 0.72)
    g.add_color_stop_rgb(0, 0.20, 0.52, 0.60)
    g.add_color_stop_rgb(1, 0.42, 0.78, 0.78)
    ctx.set_source(g)
    ctx.fill()
    ctx.move_to(x - 45 * s, wl)
    for i in range(10):
        xx = x - 45 * s + i * 10 * s
        ctx.line_to(xx, wl + math.sin(t * 3 + i) * 1.2)
    rgba(ctx, WHITE, 0.8 * a)
    ctx.set_line_width(2)
    ctx.stroke()


# ---------------------------------------------------------------- ponte para o novo personagem (rig.py)
_OUTFIT_MAP = {"swim": "swimmer", "red": "friend", "kid": "kid", "lifeguard": "lifeguard", "lycra": "lycra",
               "diver": "diver", None: "swimmer"}
_old_person = person


def person(ctx, x, y, s, a=1.0, body=None, skin=SKIN, accent=None, pose="stand", t=0.0, rot=0.0,
           arm=0.0, legs_skin=False, stockings=False, outfit=None, kick=0.0, facing=None):
    """Compatível com as chamadas antigas, mas desenha o personagem de perfil do rig."""
    import rig
    o = "stockings" if stockings else _OUTFIT_MAP.get(outfit, "swimmer")
    if facing is None:
        facing = 1 if x < W * 0.6 else -1
    k = clamp(-rot / (math.pi / 2)) if rot < 0 else 0.0
    if pose == "walk":
        p = rig.p_walk(t)
    elif pose == "run":
        p = rig.p_run(t)
    elif pose == "kneel":
        p = rig.p_kneel(t)
    elif arm >= 120:
        p = rig.p_shout(t)
    else:
        p = rig.p_stand(t)
    if k > 0:
        p = rig.blend(p, rig.p_lie(t), ease(k)) if k < 1 else rig.p_lie(t)
    rig.figure(ctx, x, y, s * 1.2, p, outfit=o, facing=facing, a=a, t=t)


def swimmer(ctx, x, y, s, t, a=1.0, outfit="swim", facing=1, speed=1.0, tilt=0.0, stroke=True):
    import rig
    p = rig.p_swim(t, speed) if stroke else rig.p_float_limp(t)
    if stroke:
        p["rot"] = 88 + math.degrees(tilt) * (1 if facing > 0 else 1)
    rig.figure(ctx, x, y + 4, s * 1.2, p, outfit=_OUTFIT_MAP.get(outfit, "swimmer"), facing=facing, a=a,
               ground=False)


def wade(ctx, x, feet_y, s, depth, t, a=1.0, pose="stand", rot=0.0, arm=0.0, outfit="swim", **kw):
    person(ctx, x, feet_y, s, a, pose=pose, rot=rot, arm=arm, outfit=outfit, t=t, facing=kw.get("facing"))
    if depth <= 0:
        return
    wl = feet_y - depth * 210 * s
    ctx.rectangle(x - 60 * s, wl, 120 * s, feet_y - wl + 8)
    g = cairo.LinearGradient(0, H * 0.48, 0, H * 0.72)
    g.add_color_stop_rgb(0, 0.20, 0.52, 0.60)
    g.add_color_stop_rgb(1, 0.42, 0.78, 0.78)
    ctx.set_source(g)
    ctx.fill()
    ctx.move_to(x - 60 * s, wl)
    for i in range(13):
        ctx.line_to(x - 60 * s + i * 10 * s, wl + math.sin(t * 3 + i) * 1.2)
    rgba(ctx, WHITE, 0.8 * a)
    ctx.set_line_width(2)
    ctx.stroke()


def studio(ctx, t, ground_y=H * 0.90):
    """Fundo neutro escuro com linha de chão (como as comparações 'YOU' do canal): sem água, sem fundo do mar."""
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.06, 0.12, 0.15)
    g.add_color_stop_rgb(1, 0.02, 0.05, 0.07)
    ctx.set_source(g)
    ctx.paint()
    for px, py, r, sp, ph in PARTS[:40]:
        circle(ctx, (px * W) % W, (py * H - t * 2) % H, r * 0.8, (0.8, 0.9, 0.95), 0.10)
    line(ctx, 0, ground_y, W, ground_y, (0.55, 0.65, 0.68), 0.35, 1.5)


def body_pts(x, ground_y, s_old):
    """Pontos do corpo do personagem (em pé) para marcar dor/queimaduras: costas, peito, barriga, cabeça, canela."""
    sc = s_old * 1.2
    hip = ground_y - 94 * sc
    return dict(back=(x - 8 * sc, hip - 36 * sc), chest=(x + 6 * sc, hip - 40 * sc), belly=(x + 6 * sc, hip - 14 * sc),
                head=(x, hip - 72 * sc), shin=(x + 3 * sc, ground_y - 24 * sc), sc=sc)
