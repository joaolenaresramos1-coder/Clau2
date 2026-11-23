"""Dados e desenho de mapas."""
import math
from gfx import *  # noqa

# ---------------------------------------------------------------- mapas
AUS = [(113.5, -22), (114, -26), (115, -31.5), (115, -34.3), (118, -35), (123, -33.9), (126, -32.3),
       (131, -31.5), (134, -32.5), (136, -35), (138, -34.8), (138, -33), (138.5, -35.5), (140, -37.5),
       (143, -38.7), (146, -39.1), (148, -37.8), (150, -37.5), (150.5, -35), (151.5, -33), (153, -31),
       (153.6, -28), (153, -25), (151.5, -24), (150, -22), (148.5, -20), (146.5, -19), (146, -17),
       (145.3, -15), (143.5, -14), (142.5, -10.7), (141.5, -13), (141.5, -16.5), (140, -17.7), (137, -16),
       (136, -13), (133, -11.5), (130.5, -12), (129.5, -15), (127, -14), (125, -15), (123, -17),
       (121, -19.5), (117, -20.5)]
TAS = [(144.6, -40.7), (148.3, -40.9), (148, -43.2), (146.5, -43.6), (145, -42.2)]
NAM = [(-168, 66), (-140, 70), (-95, 72), (-80, 63), (-60, 55), (-66, 45), (-75, 35), (-81, 25), (-97, 26),
       (-97, 18), (-87, 15), (-80, 8), (-78, 8), (-90, 13), (-105, 20), (-112, 30), (-124, 40), (-124, 48),
       (-135, 58), (-150, 60), (-165, 60)]
SAM = [(-80, 8), (-60, 10), (-50, 0), (-35, -6), (-40, -22), (-48, -27), (-58, -38), (-65, -42), (-68, -52),
       (-75, -50), (-73, -40), (-71, -18), (-81, -5)]
EUA = [(-10, 36), (-9, 43), (-1, 46), (-5, 48), (5, 53), (8, 57), (5, 62), (15, 69), (30, 71), (60, 70),
       (80, 73), (110, 76), (140, 72), (170, 69), (180, 66), (170, 60), (160, 55), (142, 52), (135, 43),
       (127, 39), (122, 30), (120, 22), (108, 20), (106, 10), (100, 13), (103, 1), (98, 8), (92, 22), (80, 15),
       (77, 8), (72, 20), (66, 25), (57, 25), (52, 28), (48, 30), (56, 24), (58, 20), (52, 15), (43, 12),
       (35, 28), (34, 31), (27, 37), (26, 41), (23, 36), (20, 40), (13, 45), (16, 38), (10, 44), (3, 43), (-5, 36)]
AFR = [(-17, 21), (-17, 14), (-10, 5), (5, 5), (9, 4), (9, -2), (13, -12), (12, -17), (15, -27), (18, -34.5),
       (25, -34), (32, -28), (35, -22), (40, -15), (40, -5), (51, 11), (43, 12), (37, 20), (33, 31), (20, 32),
       (10, 37), (-6, 36), (-10, 30)]
ISLANDS = [[(95, 5), (105, -6), (106, -3), (98, 3)], [(105, -6), (115, -8.5), (114, -7)],
           [(109, 2), (118, 7), (119, 0), (116, -4), (110, -3)], [(120, 18), (122, 18), (126, 7), (124, 6), (121, 12)],
           [(130, 31), (136, 34), (141, 41), (142, 39), (140, 35), (132, 33)], [(131, -1), (141, -2), (150, -10),
                                                                             (142, -9), (137, -5), (132, -3)],
           [(-160, 22), (-155, 20), (-156, 19)], [(172, -34.5), (178, -38), (175, -41), (167, -46), (171, -42)],
           [(44, -12), (50, -16), (47, -25), (43, -22)], [(-5, 50), (1, 51), (-3, 58), (-6, 56)]]


def poly_map(ctx, pts, proj, c=MAPLAND, a=1.0, outline=True):
    x, y = proj(*pts[0])
    ctx.move_to(x, y)
    for p in pts[1:]:
        ctx.line_to(*proj(*p))
    ctx.close_path()
    rgba(ctx, c, a)
    if outline:
        ctx.fill_preserve()
        rgba(ctx, (0.55, 0.78, 0.78), a * 0.9)
        ctx.set_line_width(3)
        ctx.stroke()
    else:
        ctx.fill()


def world_proj(x0, y0, w, h):
    return lambda lon, lat: (x0 + (lon + 180) / 360 * w, y0 + (85 - lat) / 145 * h)


def draw_world(ctx, x0, y0, w, h, a=1.0):
    card(ctx, x0 - 10, y0 - 10, w + 20, h + 20, a, fill=(0.14, 0.33, 0.38), border=(0.45, 0.7, 0.72))
    pr = world_proj(x0, y0, w, h)
    for p in (NAM, SAM, EUA, AFR, AUS, TAS) + tuple(ISLANDS):
        poly_map(ctx, p, pr, a=a)
    return pr


def aus_proj(x0, y0, w, h):
    return lambda lon, lat: (x0 + (lon - 110) / 48 * w, y0 + (-8 - lat) / 38 * h)


def draw_aus(ctx, x0, y0, w, h, a=1.0):
    card(ctx, x0 - 10, y0 - 10, w + 20, h + 20, a, fill=(0.14, 0.33, 0.38), border=(0.45, 0.7, 0.72))
    pr = aus_proj(x0, y0, w, h)
    poly_map(ctx, AUS, pr, a=a)
    poly_map(ctx, TAS, pr, a=a)
    return pr


def pin(ctx, x, y, k, name=None, c=ORANGE, side="r"):
    if k <= 0:
        return
    circle(ctx, x, y, 14 * k, c, 0.25 * k)
    circle(ctx, x, y, 6 * k, c, k)
    if name:
        text(ctx, name, x + (16 if side == "r" else -16), y + 6, 20, WHITE, k, "l" if side == "r" else "r")


def globe(ctx, x, y, r, k, lon0=135, lat0=-25, hl=(146, -17), name=None):
    """Globo localizador pequeno com destaque laranja e rótulo (como 'GULF OF CALIFORNIA')."""
    if k <= 0:
        return
    import math as _m
    lam0, ph0 = _m.radians(lon0), _m.radians(lat0)

    def proj(lon, lat):
        lam, ph = _m.radians(lon), _m.radians(lat)
        cosc = _m.sin(ph0) * _m.sin(ph) + _m.cos(ph0) * _m.cos(ph) * _m.cos(lam - lam0)
        px = r * _m.cos(ph) * _m.sin(lam - lam0)
        py = r * (_m.cos(ph0) * _m.sin(ph) - _m.sin(ph0) * _m.cos(ph) * _m.cos(lam - lam0))
        return x + px, y - py, cosc

    ctx.save()
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * _m.pi)
    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.3, 2, x, y, r)
    g.add_color_stop_rgba(0, 0.28, 0.62, 0.68, k)
    g.add_color_stop_rgba(1, 0.10, 0.30, 0.36, k)
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.clip()
    for poly in (AUS, EUA, AFR, TAS) + tuple(ISLANDS):
        pts = [proj(*p) for p in poly]
        if all(c < 0 for _, _, c in pts):
            continue
        ctx.move_to(pts[0][0], pts[0][1])
        for px, py, _ in pts[1:]:
            ctx.line_to(px, py)
        ctx.close_path()
        rgba(ctx, MAPLAND, k)
        ctx.fill()
    hx, hy, _ = proj(*hl)
    circle(ctx, hx, hy, r * 0.22, ORANGE, 0.35 * k)
    circle(ctx, hx, hy, r * 0.09, ORANGE, k)
    ctx.restore()
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * _m.pi)
    rgba(ctx, WHITE, 0.85 * k)
    ctx.set_line_width(2)
    ctx.stroke()
    if name:
        text(ctx, name, x, y + r + 22, 13, WHITE, k, "c", "bold", sp=1.2)
