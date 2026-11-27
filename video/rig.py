"""Personagem articulado de perfil, no modelo do canal de referência.

- Vista lateral, proporção adulta (~7,5 cabeças), membros finos afunilados, contorno escuro.
- Cinemática direta: cada pose é um conjunto de ângulos; o corpo é montado a partir do quadril.
- Gravidade: em modo "ground", o ponto mais baixo do corpo é apoiado na linha do chão (y=0),
  então pés, joelhos ou costas sempre encostam no chão, e ninguém flutua.
"""
import math

import cairo

from gfx import INK, rgba, clamp, lerp, ease

# ------------------------------------------------------------------ proporções (escala 1 = ~180 px de altura)
THIGH, SHIN, FOOT = 46.0, 44.0, 15.0
TORSO, NECK, HEAD_R = 54.0, 6.0, 11.5
UPPER, FORE, HAND = 31.0, 29.0, 7.5

SKIN = (0.91, 0.72, 0.58)
SUIT = (0.17, 0.18, 0.20)

OUTFITS = {
    # tronco, braço, perna, pé, tipo de pé, cabelo, capuz, máscara, cilindro, faixa, calção, mãos
    "diver": dict(top=SUIT, arm=SUIT, leg=SUIT, foot=(0.95, 0.55, 0.20), feet="fins", hair=None, hood=SUIT,
                  mask=True, tank=(0.80, 0.82, 0.84), band=(0.95, 0.55, 0.20), shorts=None, hand=SUIT),
    "swimmer": dict(top=(0.20, 0.42, 0.62), arm=SKIN, leg=SKIN, foot=SKIN, feet="bare", hair=(0.30, 0.20, 0.14),
                    hood=None, mask=False, tank=None, band=None, shorts=(0.16, 0.22, 0.34), hand=SKIN),
    "friend": dict(top=(0.82, 0.30, 0.26), arm=SKIN, leg=SKIN, foot=SKIN, feet="bare", hair=(0.12, 0.10, 0.09),
                   hood=None, mask=False, tank=None, band=None, shorts=(0.20, 0.24, 0.30), hand=SKIN),
    # amiga: cabelo comprido preso em rabo de cavalo, maiô
    "amiga": dict(top=(0.80, 0.34, 0.42), arm=SKIN, leg=SKIN, foot=SKIN, feet="bare", hair=(0.24, 0.14, 0.09),
                  hood=None, mask=False, tank=None, band=None, shorts=None, hand=SKIN, long_hair=True),
    "lifeguard": dict(top=(0.88, 0.22, 0.20), arm=SKIN, leg=SKIN, foot=SKIN, feet="bare", hair=(0.55, 0.40, 0.22),
                      hood=None, mask=False, tank=None, band=None, shorts=(0.95, 0.80, 0.22), hand=SKIN),
    "stockings": dict(top=(0.88, 0.22, 0.20), arm=SKIN, leg=(0.55, 0.40, 0.33), foot=(0.55, 0.40, 0.33), feet="bare",
                      hair=(0.55, 0.40, 0.22), hood=None, mask=False, tank=None, band=None,
                      shorts=(0.95, 0.80, 0.22), hand=SKIN),
    "lycra": dict(top=(0.12, 0.20, 0.44), arm=(0.12, 0.20, 0.44), leg=(0.12, 0.20, 0.44), foot=SKIN, feet="bare",
                  hair=(0.30, 0.20, 0.14), hood=None, mask=False, tank=None, band=(0.30, 0.70, 0.85),
                  shorts=None, hand=SKIN),
    "casual": dict(top=(0.88, 0.86, 0.80), arm=(0.88, 0.86, 0.80), leg=(0.30, 0.34, 0.42), foot=(0.30, 0.22, 0.18),
                   feet="boots", hair=(0.40, 0.28, 0.18), hood=None, mask=False, tank=None, band=None, shorts=None,
                   hand=SKIN),
    "doctor": dict(top=(0.93, 0.95, 0.96), arm=(0.93, 0.95, 0.96), leg=(0.35, 0.45, 0.55), foot=(0.25, 0.25, 0.28),
                   feet="boots", hair=(0.55, 0.55, 0.55), hood=None, mask=False, tank=None, band=None, shorts=None,
                   hand=SKIN),
    "kid": dict(top=(0.95, 0.70, 0.22), arm=SKIN, leg=SKIN, foot=SKIN, feet="bare", hair=(0.75, 0.55, 0.25),
                hood=None, mask=False, tank=None, band=None, shorts=(0.20, 0.45, 0.55), hand=SKIN),
    "oldtime": dict(top=(0.62, 0.52, 0.40), arm=(0.62, 0.52, 0.40), leg=(0.45, 0.38, 0.30), foot=(0.25, 0.20, 0.15),
                    feet="boots", hair=(0.25, 0.20, 0.15), hood=None, mask=False, tank=None, band=None, shorts=None,
                    hand=SKIN),
}


def _shade(c, k=0.72):
    return (c[0] * k, c[1] * k, c[2] * k)


def _dir(angle_deg):
    """Ângulo medido a partir da vertical para baixo; positivo = para a frente (+x)."""
    a = math.radians(angle_deg)
    return math.sin(a), math.cos(a)


def _add(p, ang, length):
    dx, dy = _dir(ang)
    return (p[0] + dx * length, p[1] + dy * length)


# ------------------------------------------------------------------ poses (ângulos em graus)
BASE = dict(lean=0.0, neck=0.0, thighF=0.0, kneeF=0.0, footF=0.0, thighB=0.0, kneeB=0.0, footB=0.0,
            armF=8.0, elbowF=10.0, armB=-6.0, elbowB=10.0, rot=0.0)


def pose(**kw):
    p = dict(BASE)
    p.update(kw)
    return p


def blend(a, b, k):
    return {key: lerp(a[key], b[key], k) for key in a}


def p_stand(t=0.0):
    b = math.sin(t * 1.7) * 1.2
    return pose(lean=1 + b * 0.3, armF=6 + b, armB=-4 - b, thighF=2, thighB=-2)


def p_walk(t, speed=1.0):
    ph = t * speed * 2 * math.pi * 0.85
    s = math.sin(ph)
    return pose(lean=4, thighF=19 * s, thighB=-19 * s,
                kneeF=8 + 38 * max(0, math.sin(ph + 1.6)), kneeB=8 + 38 * max(0, math.sin(ph + 1.6 + math.pi)),
                footF=-6 * s, footB=6 * s,
                armF=-20 * s, armB=20 * s, elbowF=18, elbowB=18)


def p_run(t, speed=1.0):
    ph = t * speed * 2 * math.pi * 1.4
    s = math.sin(ph)
    return pose(lean=16, thighF=42 * s + 8, thighB=-42 * s + 8,
                kneeF=20 + 70 * max(0, math.sin(ph + 1.4)), kneeB=20 + 70 * max(0, math.sin(ph + 1.4 + math.pi)),
                armF=-40 * s, armB=40 * s, elbowF=85, elbowB=85)


def p_kneel(t=0.0):
    return pose(lean=8, thighF=6, kneeF=95, thighB=4, kneeB=95, footF=0, footB=0, armF=10, armB=-2)


def p_cpr(t, rate=1.8):
    push = (math.sin(t * 2 * math.pi * rate) + 1) / 2
    return pose(lean=28 + 6 * push, thighF=14, kneeF=104, thighB=12, kneeB=102, footF=0, footB=0,
                armF=10 + 4 * push, elbowF=0, armB=8 + 4 * push, elbowB=0, neck=18)


def p_sit(t=0.0):
    return pose(lean=-4, thighF=88, kneeF=88, thighB=84, kneeB=84, armF=20, elbowF=40, armB=10, elbowB=40)


def p_phone(t=0.0):
    p = p_stand(t)
    p.update(armF=40, elbowF=145)
    return p


def p_shout(t=0.0):
    w = math.sin(t * 7) * 10
    return pose(lean=-4, armF=165 + w, elbowF=10, armB=155 - w, elbowB=10, thighF=6, thighB=-6)


def p_flinch(t=0.0):
    return pose(lean=-10, armF=150, elbowF=40, armB=130, elbowB=50, thighF=12, kneeF=20, thighB=-8)


def p_swim(t, speed=1.0):
    """Nado crawl (usar com rot=90: corpo deitado, cabeça para a frente)."""
    ph = t * speed * 2 * math.pi * 0.9
    k = math.sin(ph * 2.2)
    return pose(lean=0, thighF=6 + 14 * k, kneeF=10 + 12 * max(0, k), thighB=6 - 14 * k,
                kneeB=10 + 12 * max(0, -k), footF=40, footB=40,
                armF=(math.degrees(ph) % 360), elbowF=15, armB=(math.degrees(ph) + 180) % 360, elbowB=15, rot=88)


def p_fin(t, speed=1.0):
    """Mergulhador nadando com nadadeiras (braços junto ao corpo)."""
    k = math.sin(t * speed * 2 * math.pi * 0.8)
    return pose(lean=0, thighF=10 + 16 * k, kneeF=18 + 14 * max(0, k), thighB=10 - 16 * k,
                kneeB=18 + 14 * max(0, -k), footF=35, footB=35, armF=60, elbowF=40, armB=50, elbowB=40, rot=80)


def p_tread(t):
    """Na vertical na água, pernas pedalando e braços remando."""
    k = math.sin(t * 3)
    return pose(lean=6, thighF=30 + 20 * k, kneeF=50 + 20 * k, thighB=30 - 20 * k, kneeB=50 - 20 * k,
                armF=60 + 20 * k, elbowF=30, armB=50 - 20 * k, elbowB=30)


def p_lie(t=0.0):
    """Deitado de costas (rot=-90 = cabeça para trás/esquerda quando olhando para a direita)."""
    return pose(lean=0, armF=4, elbowF=6, armB=-4, elbowB=6, thighF=2, thighB=-2, rot=-90)


def p_float_limp(t=0.0):
    return pose(lean=10, armF=60 + 4 * math.sin(t), elbowF=30, armB=40, elbowB=25, thighF=20, kneeF=30,
                thighB=10, kneeB=20, rot=70)


def p_reach_down(t=0.0):
    return pose(lean=45, thighF=10, kneeF=20, thighB=-10, kneeB=10, armF=70, elbowF=10, armB=60, elbowB=10)


def p_fall(t, t0, t1=None):
    """Desmaio: joelhos cedem e o corpo tomba para trás até ficar deitado."""
    d = (t1 or t0 + 1.1) - t0
    k = clamp((t - t0) / d)
    if k < 0.45:
        q = ease(k / 0.45)
        return blend(p_stand(t), pose(lean=10, thighF=40, kneeF=80, thighB=30, kneeB=75, armF=30, armB=10), q)
    q = ease((k - 0.45) / 0.55)
    return blend(pose(lean=10, thighF=40, kneeF=80, thighB=30, kneeB=75, armF=30, armB=10), p_lie(t), q)


# ------------------------------------------------------------------ montagem
def _joints(p):
    hip = (0.0, 0.0)
    lean = p["lean"]
    shoulder = _add(hip, 180 - lean, TORSO - 4)
    neck_base = _add(hip, 180 - lean, TORSO + 2)
    head = _add(neck_base, 180 - lean - p["neck"], NECK + HEAD_R)
    legs = {}
    for side in ("F", "B"):
        knee = _add(hip, p["thigh" + side], THIGH)
        ankle = _add(knee, p["thigh" + side] - p["knee" + side], SHIN)
        toe = _add(ankle, p["thigh" + side] - p["knee" + side] + 90 + p["foot" + side] - 0, FOOT)
        legs[side] = (knee, ankle, toe)
    arms = {}
    for side in ("F", "B"):
        elbow = _add(shoulder, p["arm" + side], UPPER)
        wrist = _add(elbow, p["arm" + side] + p["elbow" + side], FORE)
        hand = _add(wrist, p["arm" + side] + p["elbow" + side], HAND * 0.6)
        arms[side] = (elbow, wrist, hand)
    return dict(hip=hip, shoulder=shoulder, neck=neck_base, head=head, legs=legs, arms=arms, lean=lean)


def _rot(pt, ang):
    a = math.radians(ang)
    return (pt[0] * math.cos(a) - pt[1] * math.sin(a), pt[0] * math.sin(a) + pt[1] * math.cos(a))


def _taper(ctx, p1, p2, w1, w2):
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    L = math.hypot(dx, dy) or 1e-6
    nx, ny = -dy / L, dx / L
    ctx.move_to(p1[0] + nx * w1 / 2, p1[1] + ny * w1 / 2)
    ctx.line_to(p2[0] + nx * w2 / 2, p2[1] + ny * w2 / 2)
    ctx.arc_negative(p2[0], p2[1], w2 / 2, math.atan2(ny, nx), math.atan2(ny, nx) - math.pi)
    ctx.line_to(p1[0] - nx * w1 / 2, p1[1] - ny * w1 / 2)
    ctx.arc_negative(p1[0], p1[1], w1 / 2, math.atan2(-ny, -nx), math.atan2(-ny, -nx) - math.pi)
    ctx.close_path()


def _chain(ctx, pts, widths, colors, a, dark=False):
    """Membro: primeiro o contorno (mais largo, tinta), depois as cores por segmento."""
    for pass_ in (0, 1):
        for i in range(len(pts) - 1):
            w1, w2 = widths[i], widths[i + 1]
            if pass_ == 0:
                _taper(ctx, pts[i], pts[i + 1], w1 + 3.2, w2 + 3.2)
                rgba(ctx, INK, a * 0.95)
            else:
                _taper(ctx, pts[i], pts[i + 1], w1, w2)
                c = colors[i]
                rgba(ctx, _shade(c) if dark else c, a)
            ctx.fill()


# ------------------------------------------------------------------ desenho (v2: formas anatômicas, referência do canal)
LINE = 1.9


def _unit(dx, dy):
    L = math.hypot(dx, dy) or 1e-6
    return dx / L, dy / L


def _cr(ctx, pts, closed=False, move=True):
    """Curva suave (Catmull-Rom -> Bézier) passando pelos pontos."""
    n = len(pts)
    if move:
        ctx.move_to(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        ctx.curve_to(p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6,
                     p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6, p2[0], p2[1])
    if closed:
        ctx.close_path()


def _limb_outline(pts, wb, wf):
    """Pontos do contorno de um membro: wb = meia-largura do lado de trás, wf = da frente, por ponto."""
    back, front = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        if i == 0:
            d = _unit(pts[1][0] - p[0], pts[1][1] - p[1])
        elif i == n - 1:
            d = _unit(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1])
        else:
            d1 = _unit(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1])
            d2 = _unit(pts[i + 1][0] - p[0], pts[i + 1][1] - p[1])
            d = _unit(d1[0] + d2[0], d1[1] + d2[1])
        nx, ny = -d[1], d[0]  # normal "de trás" (para um membro apontando para baixo, aponta para -x)
        back.append((p[0] + nx * wb[i], p[1] + ny * wb[i]))
        front.append((p[0] - nx * wf[i], p[1] - ny * wf[i]))
    return back, front


def _limb(ctx, pts, wb, wf, col, a, dark, shade=True):
    """Membro em uma peça só (sem emendas no joelho/cotovelo), com sombreado no lado de trás."""
    back, front = _limb_outline(pts, wb, wf)

    def cap(center, p_from, p_to, outward):
        r = math.hypot(p_to[0] - p_from[0], p_to[1] - p_from[1]) / 2
        cx, cy = (p_from[0] + p_to[0]) / 2, (p_from[1] + p_to[1]) / 2
        a0 = math.atan2(p_from[1] - cy, p_from[0] - cx)
        a1 = math.atan2(p_to[1] - cy, p_to[0] - cx)
        # escolhe o sentido do arco que passa pelo lado de fora (outward)
        mid_pos = a0 + ((a1 - a0) % (2 * math.pi)) / 2
        if math.cos(mid_pos) * outward[0] + math.sin(mid_pos) * outward[1] > 0:
            ctx.arc(cx, cy, r, a0, a0 + ((a1 - a0) % (2 * math.pi)))
        else:
            ctx.arc_negative(cx, cy, r, a0, a0 - ((a0 - a1) % (2 * math.pi)))

    d_end = _unit(pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1])
    d_start = _unit(pts[0][0] - pts[1][0], pts[0][1] - pts[1][1])

    def path():
        _cr(ctx, back)
        cap(pts[-1], back[-1], front[-1], d_end)
        _cr(ctx, front[::-1], move=False)
        cap(pts[0], front[0], back[0], d_start)
        ctx.close_path()

    c = _shade(col) if dark else col
    path()
    rgba(ctx, c, a)
    ctx.fill()
    if shade:
        ctx.save()
        path()
        ctx.clip()
        inner = [((b[0] + p[0]) / 2, (b[1] + p[1]) / 2) for b, p in zip(back, pts)]
        _cr(ctx, back)
        _cr(ctx, inner[::-1], move=False)
        ctx.close_path()
        rgba(ctx, _shade(c, 0.80), a)
        ctx.fill()
        ctx.restore()
    path()
    rgba(ctx, INK, a)
    ctx.set_line_width(LINE)
    ctx.stroke()


def _foot_shape(ctx, ankle, toe, col, a, dark, kind):
    f = _unit(toe[0] - ankle[0], toe[1] - ankle[1])
    n = (f[1], -f[0])  # perpendicular "para cima" (em direção à canela) quando o pé está no chão

    def P(u, v):
        return (ankle[0] + f[0] * u + n[0] * v, ankle[1] + f[1] * u + n[1] * v)

    if kind == "boots":
        pts = [P(-3.5, 6), P(4, 4.5), P(11, 1.5), P(17.5, -1.5), P(18.5, -4.5), P(16, -6.5), P(-4, -6.5),
               P(-6.5, -4), P(-6, 2)]
    else:  # pé descalço: calcanhar, arco, peito do pé, dedos
        pts = [P(-3.2, 5.5), P(2.5, 4.2), P(8.5, 1.8), P(14.5, -0.8), P(17.8, -2.6), P(17.6, -4.6), P(14, -5.4),
               P(7, -5.0), P(3, -5.6), P(-3.5, -5.6), P(-6.2, -3.6), P(-6.0, 1.0)]
    c = _shade(col) if dark else col
    _cr(ctx, pts, closed=True)
    rgba(ctx, c, a)
    ctx.fill_preserve()
    rgba(ctx, INK, a)
    ctx.set_line_width(LINE)
    ctx.stroke()
    if kind == "boots":
        ctx.move_to(*P(-6.3, -4.6))
        ctx.line_to(*P(18.2, -4.6))
        rgba(ctx, INK, a * 0.8)
        ctx.set_line_width(1.2)
        ctx.stroke()
    else:
        ctx.move_to(*P(14.2, -1.0))
        ctx.curve_to(*P(14.8, -2.2), *P(14.8, -3.6), *P(14.2, -5.0))
        rgba(ctx, INK, a * 0.5)
        ctx.set_line_width(1.0)
        ctx.stroke()


def _hand_shape(ctx, wrist, hand, col, a, dark, front_sign):
    f = _unit(hand[0] - wrist[0], hand[1] - wrist[1])
    n = (-f[1] * front_sign, f[0] * front_sign)

    def P(u, v):
        return (wrist[0] + f[0] * u + n[0] * v, wrist[1] + f[1] * u + n[1] * v)

    pts = [P(-1.5, -2.9), P(5, -3.8), P(10, -2.6), P(11.5, 0), P(10, 2.6), P(6, 3.4), P(4.5, 5.6), P(2.4, 5.2),
           P(1.5, 3.0), P(-1.5, 2.8)]
    c = _shade(col) if dark else col
    _cr(ctx, pts, closed=True)
    rgba(ctx, c, a)
    ctx.fill_preserve()
    rgba(ctx, INK, a)
    ctx.set_line_width(LINE * 0.85)
    ctx.stroke()


def _torso_shape(ctx, T, female):
    """Tronco de perfil (x = frente, y para cima negativo), do quadril ao ombro."""
    if female:
        pts = [(-8.0, 9), (-10.0, 2), (-10.5, -T * 0.18), (-8.5, -T * 0.45), (-9.5, -T * 0.75), (-7.5, -T + 1), (-2, -T - 3.5),
               (5, -T - 1.5), (8.5, -T * 0.82), (12.5, -T * 0.66), (10.5, -T * 0.55), (7.5, -T * 0.40),
               (9.5, -T * 0.12), (9.5, 2), (7.0, 9), (0, 11)]
    else:
        pts = [(-9.5, 5), (-10.5, -T * 0.25), (-10.5, -T * 0.6), (-9.5, -T * 0.88), (-5, -T - 3), (3, -T - 3),
               (9, -T * 0.86), (11, -T * 0.62), (10, -T * 0.32), (9.5, 5)]
    _cr(ctx, pts, closed=True)


def _head_shape(ctx, R):
    pts = [(-R * 1.0, R * 0.05), (-R * 0.82, -R * 0.62), (-R * 0.15, -R * 1.0), (R * 0.55, -R * 0.82),
           (R * 0.86, -R * 0.38), (R * 0.90, -R * 0.12), (R * 1.20, R * 0.20), (R * 0.98, R * 0.33),
           (R * 1.00, R * 0.52), (R * 0.90, R * 0.66), (R * 0.88, R * 0.86), (R * 0.45, R * 1.00),
           (R * 0.05, R * 0.80), (-R * 0.45, R * 0.70), (-R * 0.85, R * 0.48)]
    _cr(ctx, pts, closed=True)


def _hair(ctx, R, o, a, t):
    col = o["hair"]
    female = o.get("long_hair")
    if female:
        pts = [(R * 0.78, -R * 0.52), (R * 0.45, -R * 0.98), (-R * 0.30, -R * 1.12), (-R * 1.02, -R * 0.62),
               (-R * 1.10, R * 0.10), (-R * 0.80, R * 0.45), (-R * 0.42, R * 0.18), (-R * 0.10, -R * 0.12),
               (R * 0.35, -R * 0.42)]
    else:
        pts = [(R * 0.80, -R * 0.50), (R * 0.55, -R * 0.98), (-R * 0.20, -R * 1.14), (-R * 0.95, -R * 0.72),
               (-R * 1.06, -R * 0.05), (-R * 0.82, R * 0.40), (-R * 0.52, R * 0.20), (-R * 0.30, -R * 0.20),
               (R * 0.10, -R * 0.42), (R * 0.45, -R * 0.50)]
    _cr(ctx, pts, closed=True)
    rgba(ctx, col, a)
    ctx.fill_preserve()
    rgba(ctx, INK, a)
    ctx.set_line_width(LINE * 0.9)
    ctx.stroke()
    # mechas
    for k in range(3):
        ctx.move_to(R * (0.40 - k * 0.38), -R * (0.92 - k * 0.04))
        ctx.curve_to(R * (0.20 - k * 0.38), -R * 0.70, R * (0.05 - k * 0.38), -R * 0.55, R * (-0.10 - k * 0.38),
                     -R * (0.45 - k * 0.12))
        rgba(ctx, _shade(col, 0.6), a * 0.8)
        ctx.set_line_width(1.0)
        ctx.stroke()
    if female:
        sw = 1.6 * math.sin((t or 0) * 3.0)
        pony = [(-R * 0.85, -R * 0.55), (-R * 1.55, -R * 0.35), (-R * 1.70 + sw, R * 0.55), (-R * 1.35 + sw, R * 1.75),
                (-R * 1.05 + sw, R * 1.30), (-R * 1.05, R * 0.35), (-R * 0.90, -R * 0.20)]
        _cr(ctx, pony, closed=True)
        rgba(ctx, col, a)
        ctx.fill_preserve()
        rgba(ctx, INK, a)
        ctx.set_line_width(LINE * 0.9)
        ctx.stroke()
        ctx.new_sub_path()
        ctx.arc(-R * 0.95, -R * 0.42, 2.0, 0, 2 * math.pi)
        rgba(ctx, (0.85, 0.30, 0.35), a)
        ctx.fill()


def figure(ctx, x, y, s, p, outfit="swimmer", facing=1, a=1.0, ground=True, shadow=True, t=0.0, prop=None):
    """Desenha o personagem. (x, y) = ponto no chão (ground=True) ou quadril (ground=False)."""
    o = OUTFITS[outfit]
    female = bool(o.get("long_hair"))
    J = _joints(p)
    rot = p.get("rot", 0.0)
    pts = [J["hip"], J["shoulder"], J["neck"], J["head"]]
    for side in ("F", "B"):
        pts += list(J["legs"][side]) + list(J["arms"][side])
    R_ = lambda q: _rot(q, rot)  # noqa: E731
    lowest = max(R_(q)[1] for q in pts) + (HEAD_R if abs(rot) > 45 else 2)
    if abs(rot) > 45:
        lowest = max(lowest, max(R_(q)[1] for q in pts) + 7)
    oy = -lowest if ground else 0.0

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)
    if ground and shadow:
        xs = [R_(q)[0] for q in pts]
        cx, w = (min(xs) + max(xs)) / 2, (max(xs) - min(xs)) / 2 + 12
        ctx.save()
        ctx.translate(cx, 1)
        ctx.scale(w, 4)
        ctx.arc(0, 0, 1, 0, 2 * math.pi)
        ctx.restore()
        rgba(ctx, (0, 0, 0), 0.22 * a)
        ctx.fill()
    ctx.translate(0, oy)
    ctx.rotate(math.radians(rot))
    lean = J["lean"]
    hipw = 1.08 if female else 1.0

    def leg(side, dark):
        knee, ankle, toe = J["legs"][side]
        hip = J["hip"]
        thigh_mid = ((hip[0] * 0.5 + knee[0] * 0.5), (hip[1] * 0.5 + knee[1] * 0.5))
        calf = (knee[0] + (ankle[0] - knee[0]) * 0.30, knee[1] + (ankle[1] - knee[1]) * 0.30)
        chain = [hip, thigh_mid, knee, calf, ankle]
        # meia-largura atrás / frente: coxa cheia, joelho estreito, panturrilha saliente atrás, tornozelo fino
        wb = [7.0 * hipw, 6.0 * hipw, 4.4, 5.6, 2.8]
        wf = [6.0 * hipw, 5.4 * hipw, 4.6, 4.0, 3.0]
        if o["feet"] == "fins":
            fx, fy = toe[0] - ankle[0], toe[1] - ankle[1]
            tip = (ankle[0] + fx * 2.4, ankle[1] + fy * 2.4)
            ctx.move_to(ankle[0] - fy * 0.25, ankle[1] + fx * 0.25)
            ctx.line_to(tip[0] - fy * 0.18, tip[1] + fx * 0.18)
            ctx.line_to(tip[0] + fy * 0.12, tip[1] - fx * 0.12)
            ctx.line_to(ankle[0] + fy * 0.25, ankle[1] - fx * 0.25)
            ctx.close_path()
            rgba(ctx, _shade(o["foot"]) if dark else o["foot"], a)
            ctx.fill_preserve()
            rgba(ctx, INK, a)
            ctx.set_line_width(LINE)
            ctx.stroke()
        _limb(ctx, chain, wb, wf, o["leg"], a, dark)
        if o["feet"] != "fins":
            _foot_shape(ctx, ankle, toe, o["foot"], a, dark, o["feet"])
        if o["shorts"]:
            ln = o.get("shorts_len", 0.45)
            end = (hip[0] + (knee[0] - hip[0]) * ln, hip[1] + (knee[1] - hip[1]) * ln)
            mid = ((hip[0] + end[0]) / 2, (hip[1] + end[1]) / 2)
            k = 1.18
            _limb(ctx, [hip, mid, end], [wb[0] * k, wb[0] * k * 0.98, wb[1] * k], [wf[0] * k, wf[0] * k, wf[1] * k],
                  o["shorts"], a, dark)

    def arm(side, dark):
        elbow, wrist, hand = J["arms"][side]
        sh = J["shoulder"]
        bic = (sh[0] + (elbow[0] - sh[0]) * 0.45, sh[1] + (elbow[1] - sh[1]) * 0.45)
        fore = (elbow[0] + (wrist[0] - elbow[0]) * 0.35, elbow[1] + (wrist[1] - elbow[1]) * 0.35)
        g = 0.88 if female else 1.0
        chain = [sh, bic, elbow, fore, wrist]
        wb = [5.0 * g, 4.4 * g, 3.4 * g, 3.8 * g, 2.7 * g]
        wf = [4.6 * g, 4.6 * g, 3.4 * g, 3.5 * g, 2.7 * g]
        _limb(ctx, chain, wb, wf, o["arm"], a, dark)
        _hand_shape(ctx, wrist, hand, o["hand"], a, dark, 1)
        if o["top"] != o["arm"] and o["arm"] == SKIN and not female:
            end = (sh[0] + (elbow[0] - sh[0]) * 0.48, sh[1] + (elbow[1] - sh[1]) * 0.48)
            mid = ((sh[0] + end[0]) / 2, (sh[1] + end[1]) / 2)
            _limb(ctx, [sh, mid, end], [6.0, 5.8, 5.6], [5.6, 5.8, 5.8], o["top"], a, dark)
        if o["band"]:
            m0 = (sh[0] + (elbow[0] - sh[0]) * 0.42, sh[1] + (elbow[1] - sh[1]) * 0.42)
            m1 = (sh[0] + (elbow[0] - sh[0]) * 0.55, sh[1] + (elbow[1] - sh[1]) * 0.55)
            _limb(ctx, [m0, m1], [4.8, 4.6], [4.8, 4.6], o["band"], a, dark, shade=False)

    arm("B", True)
    leg("B", True)
    if o["tank"]:
        ctx.save()
        c = _add(J["hip"], 180 - lean, TORSO * 0.62)
        ctx.translate(*c)
        ctx.rotate(math.radians(lean))
        ctx.translate(-13, 0)
        ctx.new_sub_path()
        x0, y0, w, h, r = -7, -24, 14, 46, 6
        ctx.arc(x0 + w - r, y0 + r, r, -math.pi / 2, 0)
        ctx.arc(x0 + w - r, y0 + h - r, r, 0, math.pi / 2)
        ctx.arc(x0 + r, y0 + h - r, r, math.pi / 2, math.pi)
        ctx.arc(x0 + r, y0 + r, r, math.pi, 3 * math.pi / 2)
        ctx.close_path()
        rgba(ctx, o["tank"], a)
        ctx.fill_preserve()
        rgba(ctx, INK, a)
        ctx.set_line_width(LINE)
        ctx.stroke()
        ctx.restore()
    leg("F", False)
    # pescoço
    h = J["head"]
    nb = J["neck"]
    neck_col = o["hood"] or SKIN
    ctx.save()
    ctx.translate(*h)
    ctx.rotate(math.radians(lean + p["neck"]))
    _limb(ctx, [(-1.5, HEAD_R * 0.5), (-1.0, HEAD_R + NECK + 4)], [3.6, 4.2], [3.4, 4.0], neck_col, a, False, False)
    ctx.restore()
    # tronco
    ctx.save()
    ctx.translate(*J["hip"])
    ctx.rotate(math.radians(lean))
    T = TORSO
    _torso_shape(ctx, T, female)
    rgba(ctx, o["top"], a)
    ctx.fill()
    ctx.save()
    _torso_shape(ctx, T, female)
    ctx.clip()
    ctx.rectangle(-16, -T - 8, 9, T + 16)  # sombra nas costas
    rgba(ctx, _shade(o["top"], 0.80), a)
    ctx.fill()
    if female and o["arm"] == SKIN:  # maiô: alça e decote, ombro de pele
        ctx.move_to(-11, -T * 0.80)
        ctx.curve_to(-6, -T * 0.86, 2, -T * 0.86, 13, -T * 0.72)
        ctx.line_to(13, -T - 10)
        ctx.line_to(-11, -T - 10)
        ctx.close_path()
        rgba(ctx, SKIN, a)
        ctx.fill()
        ctx.move_to(-11, -T * 0.80)
        ctx.curve_to(-6, -T * 0.86, 2, -T * 0.86, 13, -T * 0.72)
        rgba(ctx, INK, a)
        ctx.set_line_width(LINE * 0.8)
        ctx.stroke()
    elif not female and o["shorts"] and o["top"] != o["shorts"]:
        # barra da camiseta
        ctx.move_to(-12, -T * 0.06)
        ctx.curve_to(-4, -T * 0.02, 4, -T * 0.02, 12, -T * 0.08)
        rgba(ctx, INK, a * 0.6)
        ctx.set_line_width(1.1)
        ctx.stroke()
        # gola
        ctx.move_to(-3, -T - 2)
        ctx.curve_to(0, -T + 2.5, 4, -T + 2, 6, -T - 1)
        rgba(ctx, INK, a * 0.6)
        ctx.set_line_width(1.1)
        ctx.stroke()
    ctx.restore()
    _torso_shape(ctx, T, female)
    rgba(ctx, INK, a)
    ctx.set_line_width(LINE)
    ctx.stroke()
    if o["tank"]:
        ctx.move_to(-8, -T + 6)
        ctx.line_to(6, -T * 0.45)
        rgba(ctx, (0.08, 0.08, 0.09), a)
        ctx.set_line_width(2.4)
        ctx.stroke()
    ctx.restore()
    # cabeça
    ctx.save()
    ctx.translate(*h)
    ctx.rotate(math.radians(lean + p["neck"]))
    R = HEAD_R
    if o["hood"]:
        ctx.new_sub_path()
        ctx.save()
        ctx.scale(0.92, 1.05)
        ctx.arc(0, 0, R, 0, 2 * math.pi)
        ctx.restore()
        rgba(ctx, o["hood"], a)
        ctx.fill_preserve()
        rgba(ctx, INK, a)
        ctx.set_line_width(LINE)
        ctx.stroke()
    else:
        _head_shape(ctx, R)
        rgba(ctx, SKIN, a)
        ctx.fill_preserve()
        rgba(ctx, INK, a)
        ctx.set_line_width(LINE)
        ctx.stroke()
        # orelha
        ctx.new_sub_path()
        ctx.save()
        ctx.translate(-R * 0.18, R * 0.12)
        ctx.scale(0.75, 1.0)
        ctx.arc(0, 0, R * 0.24, 0, 2 * math.pi)
        ctx.restore()
        rgba(ctx, _shade(SKIN, 0.92), a)
        ctx.fill_preserve()
        rgba(ctx, INK, a)
        ctx.set_line_width(1.1)
        ctx.stroke()
        # olho, sobrancelha, boca
        ctx.new_sub_path()
        ctx.arc(R * 0.52, -R * 0.10, 1.35, 0, 2 * math.pi)
        rgba(ctx, INK, a)
        ctx.fill()
        if female:
            ctx.move_to(R * 0.52, -R * 0.10)
            ctx.line_to(R * 0.70, -R * 0.20)
            ctx.set_line_width(0.9)
            ctx.stroke()
        ctx.move_to(R * 0.36, -R * 0.34)
        ctx.curve_to(R * 0.48, -R * 0.42, R * 0.62, -R * 0.40, R * 0.72, -R * 0.33)
        rgba(ctx, o["hair"] or INK, a)
        ctx.set_line_width(1.5)
        ctx.stroke()
        ctx.move_to(R * 0.98, R * 0.53)
        ctx.line_to(R * 0.78, R * 0.56)
        rgba(ctx, INK, a * 0.8)
        ctx.set_line_width(1.0)
        ctx.stroke()
        if o["hair"]:
            _hair(ctx, R, o, a, t)
    if o["mask"]:
        ctx.new_sub_path()
        x0, y0, w, hh, r = 3, -8, 11, 9, 3
        ctx.arc(x0 + w - r, y0 + r, r, -math.pi / 2, 0)
        ctx.arc(x0 + w - r, y0 + hh - r, r, 0, math.pi / 2)
        ctx.arc(x0 + r, y0 + hh - r, r, math.pi / 2, math.pi)
        ctx.arc(x0 + r, y0 + r, r, math.pi, 3 * math.pi / 2)
        ctx.close_path()
        rgba(ctx, (0.62, 0.82, 0.90), a)
        ctx.fill_preserve()
        rgba(ctx, INK, a)
        ctx.set_line_width(1.5)
        ctx.stroke()
        ctx.move_to(8, 4)
        ctx.line_to(14, 7)
        rgba(ctx, (0.08, 0.08, 0.09), a)
        ctx.set_line_width(3)
        ctx.stroke()
    ctx.restore()
    arm("F", False)
    if prop:
        hand = J["arms"]["F"][2]
        prop(ctx, hand[0], hand[1])
    ctx.restore()


def head_point(x, y, s, p, facing=1, ground=True):
    """Posição da cabeça na tela (para bolhas, falas, etc.)."""
    J = _joints(p)
    rot = p.get("rot", 0.0)
    pts = [J["hip"], J["shoulder"], J["neck"], J["head"]]
    for side in ("F", "B"):
        pts += list(J["legs"][side]) + list(J["arms"][side])
    lowest = max(_rot(q, rot)[1] for q in pts) + (HEAD_R if abs(rot) > 45 else 2)
    if abs(rot) > 45:
        lowest = max(lowest, max(_rot(q, rot)[1] for q in pts) + 7)
    oy = -lowest if ground else 0.0
    hx, hy = _rot(J["head"], rot)
    return x + hx * s * facing, y + (hy + oy) * s


def hand_point(x, y, s, p, facing=1, ground=True, side="F"):
    J = _joints(p)
    rot = p.get("rot", 0.0)
    pts = [J["hip"], J["shoulder"], J["neck"], J["head"]]
    for sd in ("F", "B"):
        pts += list(J["legs"][sd]) + list(J["arms"][sd])
    lowest = max(_rot(q, rot)[1] for q in pts) + (HEAD_R if abs(rot) > 45 else 2)
    if abs(rot) > 45:
        lowest = max(lowest, max(_rot(q, rot)[1] for q in pts) + 7)
    oy = -lowest if ground else 0.0
    hx, hy = _rot(J["arms"][side][2], rot)
    return x + hx * s * facing, y + (hy + oy) * s


def world_points(x, y, s, p, facing=1, ground=True):
    """Coordenadas na tela de todas as articulações (para encostar objetos no corpo: tentáculos, mãos, marcas)."""
    J = _joints(p)
    rot = p.get("rot", 0.0)
    pts = [J["hip"], J["shoulder"], J["neck"], J["head"]]
    for side in ("F", "B"):
        pts += list(J["legs"][side]) + list(J["arms"][side])
    lowest = max(_rot(q, rot)[1] for q in pts) + (HEAD_R if abs(rot) > 45 else 2)
    if abs(rot) > 45:
        lowest = max(lowest, max(_rot(q, rot)[1] for q in pts) + 7)
    oy = -lowest if ground else 0.0

    def tr(q):
        rx, ry = _rot(q, rot)
        return (x + rx * s * facing, y + (ry + oy) * s)

    out = dict(hip=tr(J["hip"]), shoulder=tr(J["shoulder"]), head=tr(J["head"]))
    for side in ("F", "B"):
        k, a, toe = J["legs"][side]
        out["knee" + side], out["ankle" + side], out["toe" + side] = tr(k), tr(a), tr(toe)
        e, w, h = J["arms"][side]
        out["elbow" + side], out["wrist" + side], out["hand" + side] = tr(e), tr(w), tr(h)
    return out
