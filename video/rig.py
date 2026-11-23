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


def figure(ctx, x, y, s, p, outfit="swimmer", facing=1, a=1.0, ground=True, shadow=True, t=0.0, prop=None):
    """Desenha o personagem. (x, y) = ponto no chão (ground=True) ou quadril (ground=False)."""
    o = OUTFITS[outfit]
    J = _joints(p)
    rot = p.get("rot", 0.0)
    # todos os pontos, girados pela rotação global
    pts = [J["hip"], J["shoulder"], J["neck"], J["head"]]
    for side in ("F", "B"):
        pts += list(J["legs"][side]) + list(J["arms"][side])
    R = lambda q: _rot(q, rot)  # noqa: E731
    lowest = max(R(q)[1] for q in pts) + (HEAD_R if abs(rot) > 45 else 2)
    if abs(rot) > 45:
        lowest = max(lowest, max(R(q)[1] for q in pts) + 7)
    oy = -lowest if ground else 0.0

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s * facing, s)
    if ground and shadow:
        xs = [R(q)[0] for q in pts]
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

    def leg(side, dark):
        knee, ankle, toe = J["legs"][side]
        _chain(ctx, [J["hip"], knee, ankle], [11.5, 8.5, 6.5], [o["leg"], o["leg"]], a, dark)
        # pé / nadadeira
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
            ctx.set_line_width(1.8)
            ctx.stroke()
        else:
            _chain(ctx, [ankle, toe], [7, 5.5 if o["feet"] == "bare" else 7], [o["foot"]], a, dark)
        if o["shorts"]:
            _taper(ctx, J["hip"], _add(J["hip"], p["thigh" + side], THIGH * 0.42), 15, 13)
            rgba(ctx, _shade(o["shorts"]) if dark else o["shorts"], a)
            ctx.fill_preserve()
            rgba(ctx, INK, a)
            ctx.set_line_width(1.6)
            ctx.stroke()

    def arm(side, dark):
        elbow, wrist, hand = J["arms"][side]
        sh = J["shoulder"]
        _chain(ctx, [sh, elbow, wrist], [9, 7, 6], [o["arm"], o["arm"] if o["arm"] != SKIN else SKIN], a, dark)
        if o["top"] != o["arm"] and o["arm"] == SKIN:
            _taper(ctx, sh, _add(sh, p["arm" + side], UPPER * 0.45), 10.5, 9.5)
            rgba(ctx, _shade(o["top"]) if dark else o["top"], a)
            ctx.fill_preserve()
            rgba(ctx, INK, a)
            ctx.set_line_width(1.5)
            ctx.stroke()
        if o["band"]:
            m = _add(sh, p["arm" + side], UPPER * 0.55)
            _taper(ctx, _add(sh, p["arm" + side], UPPER * 0.42), m, 9.2, 8.8)
            rgba(ctx, _shade(o["band"]) if dark else o["band"], a)
            ctx.fill()
        ctx.new_sub_path()
        ctx.arc(hand[0], hand[1], 4.6, 0, 2 * math.pi)
        rgba(ctx, INK, a)
        ctx.fill()
        ctx.new_sub_path()
        ctx.arc(hand[0], hand[1], 3.2, 0, 2 * math.pi)
        rgba(ctx, _shade(o["hand"]) if dark else o["hand"], a)
        ctx.fill()

    arm("B", True)
    leg("B", True)
    # cilindro de mergulho nas costas
    lean = J["lean"]
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
        ctx.set_line_width(1.8)
        ctx.stroke()
        ctx.restore()
    # tronco
    ctx.save()
    ctx.translate(*J["hip"])
    ctx.rotate(math.radians(lean))
    T = TORSO
    ctx.move_to(-9, 4)
    ctx.curve_to(-12, -T * 0.35, -11, -T * 0.75, -8, -T + 2)
    ctx.curve_to(-4, -T - 4, 5, -T - 4, 8, -T + 3)
    ctx.curve_to(12, -T * 0.7, 11, -T * 0.35, 9, 4)
    ctx.close_path()
    rgba(ctx, o["top"], a)
    ctx.fill_preserve()
    rgba(ctx, INK, a)
    ctx.set_line_width(1.8)
    ctx.stroke()
    if o["tank"]:
        ctx.move_to(-8, -T + 6)
        ctx.line_to(6, -T * 0.45)
        rgba(ctx, (0.08, 0.08, 0.09), a)
        ctx.set_line_width(2.4)
        ctx.stroke()
    ctx.restore()
    leg("F", False)
    # cabeça
    h = J["head"]
    ctx.save()
    ctx.translate(*h)
    ctx.rotate(math.radians(lean + p["neck"]))
    _chain(ctx, [(0, HEAD_R - 2), (0, HEAD_R + NECK)], [6, 6.5], [o["hood"] or SKIN], a)
    ctx.new_sub_path()
    ctx.save()
    ctx.scale(0.92, 1.05)
    ctx.arc(0, 0, HEAD_R, 0, 2 * math.pi)
    ctx.restore()
    rgba(ctx, o["hood"] or SKIN, a)
    ctx.fill_preserve()
    rgba(ctx, INK, a)
    ctx.set_line_width(1.8)
    ctx.stroke()
    if not o["hood"]:
        # nariz
        ctx.move_to(HEAD_R * 0.85, -2)
        ctx.line_to(HEAD_R * 1.12, 2.5)
        ctx.line_to(HEAD_R * 0.85, 4)
        rgba(ctx, SKIN, a)
        ctx.fill_preserve()
        rgba(ctx, INK, a)
        ctx.set_line_width(1.4)
        ctx.stroke()
        # cabelo
        if o["hair"]:
            ctx.new_sub_path()
            ctx.arc(-1, -1, HEAD_R + 0.5, math.pi * 0.95, math.pi * 1.92)
            ctx.line_to(-2, -2)
            ctx.close_path()
            rgba(ctx, o["hair"], a)
            ctx.fill()
        ctx.new_sub_path()
        ctx.arc(HEAD_R * 0.42, -2.5, 1.2, 0, 2 * math.pi)
        rgba(ctx, INK, a)
        ctx.fill()
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
        rgba(ctx, (0.08, 0.08, 0.08), a)
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
