"""Cenas do vídeo 'Por que você nunca ia querer encontrar um tubarão-cabeça-chata'.
Tempos globais (segundos) sincronizados com a narração (13:04)."""
import math
import random

import rig
import recife as R
from shark import *  # noqa: F401,F403
from mapdata import *  # noqa: F401,F403


def cam(ctx, cx, cy, z):
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)


def big_globe(ctx, x, y, r, lon0, lat0, a=1.0, hl=None, label_txt=None):
    lam0, ph0 = math.radians(lon0), math.radians(lat0)

    def proj(lon, lat):
        lam, ph = math.radians(lon), math.radians(lat)
        cosc = math.sin(ph0) * math.sin(ph) + math.cos(ph0) * math.cos(ph) * math.cos(lam - lam0)
        return (x + r * math.cos(ph) * math.sin(lam - lam0),
                y - r * (math.cos(ph0) * math.sin(ph) - math.sin(ph0) * math.cos(ph) * math.cos(lam - lam0)), cosc)

    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.3, r * 0.1, x, y, r)
    g.add_color_stop_rgba(0, 0.26, 0.58, 0.66, a)
    g.add_color_stop_rgba(1, 0.07, 0.22, 0.28, a)
    ctx.save()
    ctx.new_sub_path()
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.set_source(g)
    ctx.fill_preserve()
    ctx.clip()
    for poly in (NAM, SAM, EUA, AFR, AUS, TAS) + tuple(ISLANDS):
        pts = [proj(*p) for p in poly]
        if all(c < 0 for _, _, c in pts):
            continue
        ctx.move_to(pts[0][0], pts[0][1])
        for px, py, _ in pts[1:]:
            ctx.line_to(px, py)
        ctx.close_path()
        rgba(ctx, MAPLAND, a)
        ctx.fill_preserve()
        rgba(ctx, (0.55, 0.78, 0.78), a * 0.8)
        ctx.set_line_width(1.5)
        ctx.stroke()
    if hl:
        hx, hy, c = proj(*hl)
        if c > 0:
            circle(ctx, hx, hy, 18, ORANGE, 0.3 * a)
            circle(ctx, hx, hy, 7, ORANGE, a)
            if label_txt:
                text(ctx, label_txt, hx + 18, hy + 5, 18, WHITE, a, "l", "bold", sp=1.5)
    ctx.restore()


# ------------------------------------------------------------------ mapas regionais
AMAZON = [(-50.0, 0.0), (-52.5, -1.5), (-55.5, -2.3), (-58.5, -3.1), (-61.5, -3.3), (-64.5, -3.6), (-67.5, -3.4),
          (-70.0, -4.0), (-73.2, -3.75)]
MISSISSIPPI = [(-89.3, 29.1), (-90.4, 30.4), (-91.2, 31.5), (-91.0, 33.5), (-90.1, 35.1), (-89.6, 36.9),
               (-90.2, 38.6), (-90.2, 38.9)]


def americas_map(ctx, x0, y0, w, h, lon_r, lat_r, a=1.0):
    card(ctx, x0 - 8, y0 - 8, w + 16, h + 16, a, fill=(0.14, 0.33, 0.38), border=(0.45, 0.7, 0.72))
    pr = lambda lon, lat: (x0 + (lon - lon_r[0]) / (lon_r[1] - lon_r[0]) * w,  # noqa: E731
                           y0 + (lat_r[1] - lat) / (lat_r[1] - lat_r[0]) * h)
    ctx.save()
    ctx.rectangle(x0, y0, w, h)
    ctx.clip()
    for p in (NAM, SAM):
        poly_map(ctx, p, pr, a=a)
    ctx.restore()
    return pr


def river(ctx, pts, pr, k, col=(0.35, 0.62, 0.80), a=1.0, w=4):
    n = max(2, int(len(pts) * k) + 1)
    sub = pts[:n]
    ctx.move_to(*pr(*sub[0]))
    for p in sub[1:]:
        ctx.line_to(*pr(*p))
    rgba(ctx, col, a)
    ctx.set_line_width(w)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.stroke()


def along(pts, pr, k):
    k = clamp(k)
    segs = len(pts) - 1
    f = k * segs
    i = min(segs - 1, int(f))
    q = f - i
    a, b = pr(*pts[i]), pr(*pts[i + 1])
    return lerp(a[0], b[0], q), lerp(a[1], b[1], q), math.atan2(b[1] - a[1], b[0] - a[0])


def shark_icon(ctx, x, y, s, ang=0.0, a=1.0, col=ORANGE):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    shark(ctx, 0, 0, 60 * s, 0.0, "bull", 1, a, swim=0, silhouette=False, eye=False, top=col)
    ctx.restore()


# coluna de costa de Pernambuco (mapa esquemático norte-sul)
PE_PLACES = [("RECIFE", -8.05), ("BOA VIAGEM", -8.12), ("PIEDADE", -8.17), ("CANDEIAS", -8.21),
             ("PORTO DE SUAPE", -8.39)]


def pe_coast(ctx, t, a=1.0, strip=0.0, suape=0.0, mangrove=1.0):
    x0, y0, w, h = W * 0.10, H * 0.10, W * 0.80, H * 0.80
    card(ctx, x0 - 8, y0 - 8, w + 16, h + 16, a, fill=(0.14, 0.33, 0.38), border=(0.45, 0.7, 0.72))
    lat0, lat1 = -7.95, -8.48
    yl = lambda lat: y0 + (lat0 - lat) / (lat0 - lat1) * h  # noqa: E731
    coast_x = lambda lat: x0 + w * 0.48 + math.sin(lat * 40) * 10 + (lat + 8.2) * 60  # noqa: E731
    ctx.move_to(x0, y0)
    N = 40
    for i in range(N + 1):
        lat = lat0 + (lat1 - lat0) * i / N
        ctx.line_to(coast_x(lat), yl(lat))
    ctx.line_to(x0, y0 + h)
    ctx.close_path()
    rgba(ctx, MAPLAND, a)
    ctx.fill()
    # rios desaguando
    for lat in (-8.06, -8.20, -8.36):
        cx = coast_x(lat)
        ctx.move_to(cx, yl(lat))
        ctx.curve_to(cx - 60, yl(lat) - 10, cx - 120, yl(lat) + 20, cx - 220, yl(lat) - 5)
        rgba(ctx, (0.40, 0.65, 0.78), a)
        ctx.set_line_width(4)
        ctx.stroke()
    # manguezais (somem quando as obras avançam)
    rnd = random.Random(5)
    for i in range(18):
        lat = rnd.uniform(-8.30, -8.45)
        circle(ctx, coast_x(lat) - rnd.uniform(20, 120), yl(lat), rnd.uniform(6, 12), (0.25, 0.55, 0.35),
               a * mangrove)
    # arrecifes (linha pontilhada no mar)
    for i in range(N):
        lat = lat0 + (lat1 - lat0) * i / N
        circle(ctx, coast_x(lat) + 26, yl(lat), 3, (0.55, 0.50, 0.42), a)
    # faixa de ~20 km com incidentes
    if strip > 0:
        ya, yb = yl(-8.08), yl(-8.25)
        rrect(ctx, coast_x(-8.16) - 30, ya, 120, (yb - ya) * ease(strip), 10)
        rgba(ctx, RED, 0.35 * a)
        ctx.fill()
        text(ctx, "~20 KM", coast_x(-8.16) + 110, (ya + yb) / 2, 26, WHITE, a * strip, "l", "black")
    for name, lat in PE_PLACES:
        if name == "PORTO DE SUAPE" and suape <= 0:
            continue
        aa = a * (suape if name == "PORTO DE SUAPE" else 1)
        pin(ctx, coast_x(lat), yl(lat), aa, None, ORANGE if name != "PORTO DE SUAPE" else YELLOW)
        text(ctx, name, coast_x(lat) - 16, yl(lat) + 6, 16, WHITE, aa, "r", "bold", sp=1)
    if suape > 0:
        cx, cy = coast_x(-8.39) + 40, yl(-8.39)
        line(ctx, cx, cy, cx, cy - 60 * suape, YELLOW, a, 4)
        line(ctx, cx, cy - 60 * suape, cx + 50 * suape, cy - 60 * suape, YELLOW, a, 4)
        line(ctx, cx + 45 * suape, cy - 60 * suape, cx + 45 * suape, cy - 35 * suape, YELLOW, a * 0.8, 2)
    return coast_x, yl


# ------------------------------------------------------------------ 0:00 – 0:36 abertura
def sc_open(ctx, t):
    if t < 5.0:
        rgba(ctx, (0.02, 0.04, 0.07))
        ctx.paint()
        for i in range(120):
            circle(ctx, (i * 211) % W, (i * 97) % H, 1.0 + (i % 3) * 0.4, WHITE, 0.4 + 0.3 * math.sin(t + i))
        k = ease(t / 5.0)
        r = lerp(170, 1600, k ** 2.2)
        big_globe(ctx, W / 2, H / 2 + lerp(0, 100, k), r, lerp(-10, -35, ease(min(1, t / 3.5))),
                  lerp(10, -8, ease(min(1, t / 3.8))), 1.0, hl=(-34.9, -8.1),
                  label_txt="RECIFE · PERNAMBUCO" if t > 2.5 else None)
        kicker(ctx, "JULHO · FIM DE TARDE · DEPOIS DA CHUVA", W / 2, H * 0.92, t, 0.8, 4.8, 18, WHITE)
        if t > 4.5:
            rgba(ctx, WHITE, (t - 4.5) / 0.5 * 0.6)
            ctx.paint()
        return
    tide = kf(t, [(5, 0.55), (18, 1.0)])
    murk = kf(t, [(5, 0.3), (12, 1.0)])
    # câmera: plano geral -> arrecifes -> placa
    cx = kf(t, [(5, W / 2), (17, W / 2), (19.5, R.REEF_X), (27, R.REEF_X), (29.5, W * 0.27), (36, W * 0.27)])
    cy = kf(t, [(5, H / 2), (17, H / 2), (19.5, H * 0.55), (27, H * 0.55), (29.5, R.DRY - 40), (36, R.DRY - 40)])
    z = kf(t, [(5, 1.0), (17, 1.0), (19.5, 1.5), (27, 1.5), (29.5, 2.4), (36, 2.6)])
    cam(ctx, cx, cy, z)
    R.scene(ctx, t, tide=tide, murk=murk, dusk=0.6, rain=1 - appear(t, 5, 4))
    # chuva parando
    if t < 9:
        rnd = random.Random(1)
        for i in range(120):
            x = (rnd.random() * W + t * 60) % W
            y = (rnd.random() * H + t * 900) % H
            line(ctx, x, y, x - 4, y + 16, (0.85, 0.9, 0.95), 0.5 * (1 - appear(t, 6, 3)), 1.2)
    ctx.restore()
    callout(ctx, *_scr(R.REEF_X, R.ground_y(R.REEF_X), cx, cy, z), 30, W * 0.62, H * 0.18, "ARRECIFES",
            window(t, 18.3, 27))
    kicker(ctx, "DENTRO: RASA E CALMA", W * 0.30, H * 0.86, t, 22.2, 27, 18, WHITE)
    kicker(ctx, "FORA: FUNDO DE REPENTE", W * 0.72, H * 0.86, t, 25.0, 27.5, 18, WHITE)
    if 12 < t < 18:
        kicker(ctx, "ÁGUA MARROM-ESVERDEADA · TURVA", W / 2, H * 0.16, t, 12.3, 17.8, 18, (0.15, 0.18, 0.22))
    vignette(ctx, 0.35, t)


def _scr(x, y, cx, cy, z):
    return W / 2 + (x - cx) * z, H / 2 + (y - cy) * z


# ------------------------------------------------------------------ 0:36 – 0:56 entrando depois dos arrecifes
def person_in_sea(ctx, x, t, outfit, facing, s=0.8, tide=1.0):
    """Anda pelo chão enquanto dá pé; quando fica fundo demais, passa a boiar na superfície."""
    d = R.depth(x, tide)
    hip_h = 94 * s
    if d < hip_h * 1.35:
        p = rig.p_walk(t, 0.7)
        rig.figure(ctx, x, R.ground_y(x), s, p, outfit=outfit, facing=facing, t=t, shadow=False)
        return R.ground_y(x) - 170 * s
    lvl = R.sea_level(tide)
    rig.figure(ctx, x, lvl + 62 * s, s, rig.p_tread(t), outfit=outfit, facing=facing, ground=False, t=t)
    return lvl - 20 * s


def sc_enter(ctx, t):
    if t >= 48:
        return sc_below(ctx, t)
    fx = kf(t, [(36, W * 0.33), (42, W * 0.56), (47, W * 0.76)], fn=lambda k: k)
    yx = kf(t, [(41, W * 0.31), (44, W * 0.52), (48, W * 0.70)], fn=lambda k: k)
    cx = kf(t, [(36, W * 0.45), (48, W * 0.62)])
    cam(ctx, cx, H * 0.52, 1.35)

    def mid(c):
        person_in_sea(c, fx, t, "friend", 1)
        person_in_sea(c, yx, t, "swimmer", 1)

    R.scene(ctx, t, tide=1.0, murk=1.0, mid=mid)
    ctx.restore()
    kicker(ctx, "CINTURA · PEITO · SEM CHÃO", W / 2, H * 0.12, t, 42.3, 48, 18, (0.15, 0.18, 0.22))
    vignette(ctx, 0.35, t)


def sc_below(ctx, t):
    """Visão debaixo d'água turva: as pernas de vocês em cima e uma sombra grande embaixo."""
    murky(ctx, t, 1.0, light=0.6)
    lvl = 90
    ctx.rectangle(0, 0, W, lvl)
    rgba(ctx, (0.62, 0.62, 0.52))
    ctx.fill()
    surface_line(ctx, t, lvl, sky=False)
    for x, o in ((W * 0.42, "friend"), (W * 0.58, "swimmer")):
        rig.figure(ctx, x, lvl + 85, 1.0, rig.p_tread(t + x), outfit=o, facing=1, ground=False, t=t)
    fog(ctx, 0.35)
    k = appear(t, 51.5, 1.0)
    if k > 0:
        sx = kf(t, [(51.5, W * 0.95), (54, W * 0.55), (56, W * 0.20)])
        sy = H * 0.78
        turn = kf(t, [(52.5, 1), (54.5, -1)])
        shark(ctx, sx, sy, 340, t, "bull", facing=-1 if turn < 0 else 1, silhouette=True, a=0.55 * k)
    fog(ctx, 0.25)
    vignette(ctx, 0.75, t)


# ------------------------------------------------------------------ 0:56 – 1:30 a revelação
def sc_reveal(ctx, t):
    murky(ctx, t, 0.8)
    if t < 64:
        sx = kf(t, [(56, W * 1.1), (60, W * 0.52)])
        shark(ctx, sx, H * 0.50, 520, t, "bull", facing=-1, swim=0.8)
        k = window(t, 58.5, 64)
        if k > 0:
            shark(ctx, W * 0.5, H * 0.22, 640, t, "white", facing=-1, a=0.25 * k, silhouette=True, swim=0.4)
            text(ctx, "TUBARÃO-BRANCO DOS FILMES", W * 0.5, H * 0.08, 16, SOFT, k, "c", "semi", sp=2)
            callout(ctx, W * 0.52 - 80, H * 0.50, 70, W * 0.22, H * 0.78, "MENOR · MAIS BAIXO · MAIS GROSSO",
                    appear(t, 60.5))
    elif t < 71:
        shark(ctx, W * 0.5, H * 0.38, 480, t, "bull", facing=-1, swim=0.7)
        items = [("RASA", 66.0), ("QUENTE", 67.0), ("TURVA", 68.2)]
        for i, (nm, c0) in enumerate(items):
            a = appear(t, c0)
            x = W / 2 + (i - 1) * 260
            y = H * 0.78
            if i == 0:
                line(ctx, x - 40, y - 30, x + 40, y - 30, WHITE, a, 2)
                line(ctx, x - 40, y + 10, x + 40, y + 10, SAND, a, 6)
                scale_bar(ctx, x - 45, x - 45, y, 1, "")
            elif i == 1:
                rrect(ctx, x - 8, y - 50, 16, 60, 8)
                ink(ctx, WHITE, a, 2)
                circle(ctx, x, y + 14, 14, RED, a)
                rrect(ctx, x - 3, y - 30, 6, 40, 3)
                rgba(ctx, RED, a)
                ctx.fill()
            else:
                ctx.move_to(x, y - 45)
                ctx.curve_to(x + 30, y - 5, x + 30, y + 20, x, y + 20)
                ctx.curve_to(x - 30, y + 20, x - 30, y - 5, x, y - 45)
                ink(ctx, (0.55, 0.48, 0.30), a, 2.5)
            text(ctx, nm, x, y + 55, 22, WHITE, a, "c", "black", sp=3)
    else:
        sc_amazon(ctx, t)
        return
    vignette(ctx, 0.6, t)


def sc_amazon(ctx, t):
    ocean(ctx, t, rays=False)
    pr = americas_map(ctx, W * 0.10, H * 0.08, W * 0.80, H * 0.84, (-95, -30), (-25, 15), appear(t, 71))
    k = clamp((t - 73.5) / 6)
    river(ctx, AMAZON, pr, 1.0, a=appear(t, 72))
    x, y, ang = along(AMAZON, pr, k)
    shark_icon(ctx, x, y, 0.8, ang + math.pi, appear(t, 73))
    if t > 78:
        text(ctx, "MILHARES DE KM DO OCEANO", x - 20, y - 30, 20, WHITE, appear(t, 78), "c", "black", sp=1.5)
    text(ctx, "RIO AMAZONAS", W * 0.55, H * 0.40, 16, (0.75, 0.88, 0.95), appear(t, 73), "c", "bold", sp=2)
    vignette(ctx, 0.5, t)


def sc_name(ctx, t):
    murky(ctx, t, 0.7)
    sx = kf(t, [(81, W * 1.15), (90, W * 0.30)], fn=lambda k: k)
    shark(ctx, sx, H * 0.55, 600, t, "bull", facing=-1, swim=0.9)
    name_tag(ctx, "Carcharhinus leucas", 40, 60, t, 81.4, None, 28)
    big_title(ctx, [("TUBARÃO-", WHITE, "black"), ("CABEÇA-CHATA", ORANGE, "light")], W / 2, H * 0.16, t, 81.8,
              None, 56)
    kicker(ctx, "EM OUTROS PAÍSES: TUBARÃO-TOURO", W / 2, H * 0.22, t, 83.2, None, 17, WHITE)
    vignette(ctx, 0.55, t)


# ------------------------------------------------------------------ 1:30 – 1:50 promessa
def sc_promise(ctx, t):
    ocean(ctx, t)
    items = [("rio", "ÁGUA DOCE", 91.2), ("pin", "RECIFE", 95.0), ("placa", "A PLACA", 99.0),
             ("aid", "O QUE FAZER", 102.0)]
    for i, (kd, nm, c0) in enumerate(items):
        a = window(t, c0, 105.6)
        if a <= 0:
            continue
        x = W / 2 + (i - 1.5) * 270
        y0 = H * 0.28 + (1 - appear(t, c0, 0.5)) * 25
        card(ctx, x - 115, y0, 230, 230, a)
        cx, cy = x, y0 + 95
        if kd == "rio":
            ctx.move_to(cx - 80, cy - 40)
            ctx.curve_to(cx - 20, cy - 50, cx - 30, cy + 20, cx + 80, cy + 30)
            rgba(ctx, (0.40, 0.65, 0.80), a)
            ctx.set_line_width(14)
            ctx.stroke()
            shark_icon(ctx, cx, cy - 5, 0.9, -0.3, a, SHARK_TOP)
        elif kd == "pin":
            pin(ctx, cx, cy, a)
            circle(ctx, cx, cy, 30, ORANGE, 0.2 * a)
        elif kd == "placa":
            shark_sign(ctx, cx, cy + 40, 0.65, a)
        else:
            gy = cy + 45
            line(ctx, cx - 90, gy, cx + 90, gy, SOFT, a * 0.5, 1.5)
            rig.figure(ctx, cx + 15, gy, 0.75, rig.p_lie(0), outfit="friend", facing=-1, a=a, shadow=False)
            p = rig.p_kneel(t)
            p.update(lean=45, armF=40, elbowF=10, armB=30, elbowB=10)
            rig.figure(ctx, cx - 35, gy, 0.75, p, outfit="swimmer", facing=1, a=a, shadow=False)
        text(ctx, nm, x, y0 + 205, 20, ORANGE, a, "c", "bold", sp=2)
    kicker(ctx, "POR QUE VOCÊ NUNCA IA QUERER ENCONTRAR UM", W / 2, H * 0.38, t, 106, None, 20)
    big_title(ctx, [("TUBARÃO-", WHITE, "black"), ("CABEÇA-CHATA", ORANGE, "light")], W / 2, H * 0.38 + 75, t,
              106.4, None, 66)
    if t > 106:
        shark(ctx, kf(t, [(106, W * 1.2), (110, W * 0.6)]), H * 0.72, 380, t, "bull", facing=-1,
              a=appear(t, 106.5))
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 1:50 – 2:39 anatomia e mordida
def seesaw(ctx, cx, cy, tilt, a, left, right):
    ctx.move_to(cx, cy)
    ctx.line_to(cx - 30, cy + 50)
    ctx.line_to(cx + 30, cy + 50)
    ctx.close_path()
    ink(ctx, (0.55, 0.58, 0.60), a, 2)
    ctx.save()
    ctx.translate(cx, cy)
    ctx.rotate(tilt)
    rrect(ctx, -330, -8, 660, 14, 5)
    ink(ctx, (0.80, 0.82, 0.84), a, 2)
    left(ctx, -200, -8)
    right(ctx, 200, -8)
    ctx.restore()


def sc_anatomy(ctx, t):
    ocean(ctx, t)
    if t < 124:
        sx, sy, L = W * 0.48, H * 0.52, 760
        shark(ctx, sx, sy, L, t, "bull", facing=1, swim=0.4)
        label(ctx, "COMO ELE É?", W / 2, 80, t, 110.2, 114, 36, ORANGE)
        callout(ctx, sx + L * 0.47, sy - 10, 46, W * 0.80, H * 0.16, "FOCINHO CURTO, LARGO E ARREDONDADO",
                window(t, 113.5, 121))
        callout(ctx, sx, sy + 20, 60, W * 0.30, H * 0.86, "CINZA EM CIMA · BRANCO EMBAIXO", window(t, 120.2, 124))
    elif t < 127:
        shark(ctx, W * 0.45, H * 0.32, 640, t, "bull", 1, swim=0.4)
        scale_bar(ctx, W * 0.45 - 320, W * 0.45 + 320, H * 0.50, (t - 124.3) / 0.8, "FÊMEA · 3 M OU MAIS")
        shark(ctx, W * 0.45, H * 0.70, 460, t, "bull", 1, swim=0.4)
        scale_bar(ctx, W * 0.45 - 230, W * 0.45 + 230, H * 0.84, (t - 125) / 0.8, "MACHO · MENOR")
    else:
        k = appear(t, 128.5, 1.5)

        def left(c, x, y):
            c.save()
            c.translate(x, y - 40)
            shark(c, 0, 0, 230, t, "bull", 1, swim=0)
            c.restore()

        def right(c, x, y):
            for i in range(3):
                rig.figure(c, x - 50 + i * 50, y, 0.6, rig.p_stand(t + i), outfit=["swimmer", "friend", "kid"][i],
                           facing=-1, shadow=False)

        seesaw(ctx, W / 2, H * 0.70, 0.0 * k, 1, left, right)
        big_title(ctx, [("200+ ", ORANGE, "black"), ("KG", WHITE, "light")], W * 0.30, H * 0.30, t, 127.2, None, 48)
        kicker(ctx, "≈ TRÊS PESSOAS ADULTAS", W * 0.72, H * 0.30, t, 131, None, 18, WHITE)
    vignette(ctx, 0.6, t)


def sc_bite(ctx, t):
    ocean(ctx, t, top=(0.06, 0.14, 0.18))
    if t < 146:
        chapter(ctx, "ESTUDO DE 2012", "FORÇA DA", "MORDIDA", W / 2, 110, t, 135.0, None, 40)
        bars = [("CABEÇA-CHATA", 1.00, ORANGE), ("TIGRE", 0.78, SOFT), ("BRANCO", 0.70, SOFT), ("MARTELO", 0.48, SOFT),
                ("LIMÃO", 0.40, SOFT)]
        for i, (nm, v, col) in enumerate(bars):
            a = appear(t, 137 + i * 0.3)
            y = H * 0.32 + i * 70
            text(ctx, nm, W * 0.30, y + 8, 18, WHITE, a, "r", "bold", sp=1.5)
            rrect(ctx, W * 0.32, y - 16, W * 0.45 * v * appear(t, 137.5 + i * 0.3, 1.2), 34, 6)
            rgba(ctx, col, a)
            ctx.fill()
        kicker(ctx, "EM RELAÇÃO AO TAMANHO DO CORPO (ILUSTRATIVO)", W / 2, H * 0.92, t, 140, None, 14, SOFT)
    else:
        m = appear(t, 146.2, 0.6)
        shark(ctx, W * 0.30, H * 0.50, 620, t, "bull", facing=1, swim=0.2, mouth=m)
        for j, (c0, ttl, up) in enumerate(((146.6, "CIMA: CORTAR", True), (150.8, "BAIXO: SEGURAR", False))):
            a_ = appear(t, c0)
            cx0, cy0 = W * 0.78, H * (0.30 + 0.38 * j)
            card(ctx, cx0 - 170, cy0 - 90, 340, 180, a_)
            for i in range(4):
                tx = cx0 - 105 + i * 70
                if up:
                    ctx.move_to(tx - 26, cy0 - 40)
                    for q in range(7):
                        ctx.line_to(tx - 26 + q * 4.3 + 2, cy0 - 34 + q * 8 + (2 if q % 2 else -2))
                    ctx.line_to(tx, cy0 + 30)
                    ctx.line_to(tx + 26, cy0 - 40)
                else:
                    ctx.move_to(tx - 10, cy0 + 30)
                    ctx.line_to(tx, cy0 - 45)
                    ctx.line_to(tx + 10, cy0 + 30)
                ctx.close_path()
                ink(ctx, WHITE, a_, 2)
            text(ctx, ttl, cx0, cy0 + 70, 18, ORANGE, a_, "c", "black", sp=2)
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 2:39 – 3:23 água doce: modo mar / modo rio
def salt_dots(ctx, cx, cy, rx, ry, n, seed, col=WHITE, a=1.0, inside=True):
    rnd = random.Random(seed)
    for i in range(n):
        ang, r = rnd.uniform(0, 6.28), rnd.uniform(0, 1) ** 0.5
        circle(ctx, cx + math.cos(ang) * rx * r, cy + math.sin(ang) * ry * r, 3, col, a)


def sc_fresh(ctx, t):
    if t < 182:
        # peixe comum em água doce: incha
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgb(0, 0.30, 0.45, 0.50)
        g.add_color_stop_rgb(1, 0.10, 0.20, 0.24)
        ctx.set_source(g)
        ctx.paint()
        chapter(ctx, "UM PEIXE DE ÁGUA SALGADA", "NA ÁGUA", "DOCE", W / 2, 100, t, 163, None, 40)
        swell = appear(t, 175, 2.5)
        cx, cy = W * 0.50, H * 0.56
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(1 + 0.15 * swell, 1 + 0.45 * swell)
        fish(ctx, 0, 0, 5.0, t, c=(0.75, 0.78, 0.80), wiggle=0.05 * (1 - swell))
        ctx.restore()
        salt_dots(ctx, cx, cy, 110, 45, 60, 1, WHITE, appear(t, 168))
        text(ctx, "MUITO SAL DENTRO", cx, cy + 140, 18, WHITE, appear(t, 168.5), "c", "bold", sp=2)
        rnd = random.Random(2)
        for i in range(16):
            circle(ctx, rnd.uniform(0, W), rnd.uniform(H * 0.25, H), 3, WHITE, 0.5 * appear(t, 171))
        text(ctx, "QUASE NENHUM FORA", W * 0.85, H * 0.88, 16, SOFT, appear(t, 171), "c", "bold", sp=2)
        k = appear(t, 174)
        for i in range(8):
            ang = i * math.pi / 4
            r0 = 230 - ((t * 60 + i * 20) % 90)
            x1, y1 = cx + math.cos(ang) * r0, cy + math.sin(ang) * r0 * 0.6
            line(ctx, x1, y1, x1 - math.cos(ang) * 22, y1 - math.sin(ang) * 14, (0.55, 0.80, 0.95), k, 3)
        if t > 178.5:
            xmark(ctx, cx, cy, 60, appear(t, 178.8, 0.6))
    else:
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgb(0, 0.36, 0.40, 0.26)
        g.add_color_stop_rgb(1, 0.10, 0.12, 0.08)
        ctx.set_source(g)
        ctx.paint()
        sx, sy, L = W * 0.50, H * 0.52, 800
        shark(ctx, sx, sy, L, t, "bull", facing=1, swim=0.4, a=0.55)
        # rins (brilham) e glândula retal (desliga)
        kid = appear(t, 184.5)
        ellipse_path(ctx, sx - 40, sy + 10, 120, 18)
        ink(ctx, (0.85, 0.45, 0.40), kid, 2)
        circle(ctx, sx - 40, sy + 10, 140, (0.95, 0.55, 0.45), 0.12 * kid * (0.6 + 0.4 * math.sin(t * 4)))
        callout(ctx, sx - 40, sy + 10, 60, W * 0.30, H * 0.20, "RINS TRABALHANDO MAIS", window(t, 184.5, 193))
        for i in range(6):  # urina saindo
            ph = ((t * 0.8 + i / 6) % 1)
            circle(ctx, sx - 200 - ph * 120, sy + 40 + ph * 30, 4, (0.95, 0.90, 0.5), kid * (1 - ph))
        gl = 1 - appear(t, 193.5, 1.5)
        circle(ctx, sx - 250, sy - 8, 14, YELLOW if gl > 0.5 else (0.45, 0.45, 0.45), 0.9 * appear(t, 192))
        callout(ctx, sx - 250, sy - 8, 24, W * 0.18, H * 0.80, "GLÂNDULA DO SAL: DESLIGA", window(t, 192.5, 199))
        # chave modo mar / modo rio
        k = appear(t, 197)
        if k > 0:
            on = appear(t, 199.2, 0.4)
            bx, by = W * 0.78, H * 0.80
            rrect(ctx, bx - 60, by - 22, 120, 44, 22)
            ink(ctx, lerp(0.3, 0.2, on) and ((0.25, 0.55, 0.85) if on < 0.5 else (0.55, 0.45, 0.25)), k, 2)
            circle(ctx, bx - 38 + 76 * on, by, 18, WHITE, k)
            text(ctx, "MODO MAR", bx - 80, by + 8, 16, WHITE, k * (1 - 0.6 * on), "r", "bold", sp=1)
            text(ctx, "MODO RIO", bx + 80, by + 8, 16, ORANGE, k * (0.4 + 0.6 * on), "l", "bold", sp=1)
    vignette(ctx, 0.55, t)


# ------------------------------------------------------------------ 3:23 – 4:16 rios e filhotes
NICARAGUA_R = [(-83.7, 10.9), (-84.2, 11.0), (-84.6, 11.1), (-84.9, 11.15)]


def sc_rivers(ctx, t):
    ocean(ctx, t, rays=False)
    if t < 209:
        pr = americas_map(ctx, W * 0.10, H * 0.08, W * 0.80, H * 0.84, (-110, -70), (20, 45), appear(t, 202))
        river(ctx, MISSISSIPPI, pr, 1, a=appear(t, 203))
        x, y, ang = along(MISSISSIPPI, pr, clamp((t - 204) / 4))
        shark_icon(ctx, x, y, 0.7, ang + math.pi, appear(t, 204))
        label(ctx, "RIO MISSISSIPPI · +1.000 KM DO MAR", W / 2, H * 0.94, t, 205, None, 20, WHITE)
    elif t < 216:
        pr = americas_map(ctx, W * 0.10, H * 0.08, W * 0.80, H * 0.84, (-88, -82), (9.5, 13), appear(t, 209))
        lx, ly = pr(-85.4, 11.5)
        ellipse_path(ctx, lx, ly, 150, 90, -0.4)
        ink(ctx, (0.40, 0.65, 0.80), 1, 2)
        river(ctx, NICARAGUA_R, pr, 1, w=6)
        x, y, ang = along(NICARAGUA_R, pr, clamp((t - 210.5) / 3.5))
        hop = abs(math.sin(t * 5)) * 25 * (1 if t < 214 else 0)
        shark_icon(ctx, x, y - hop, 0.8, ang + math.pi, 1)
        text(ctx, "LAGO NICARÁGUA", lx, ly + 8, 22, WHITE, 1, "c", "bold", sp=2)
        label(ctx, "SOBE AS CORREDEIRAS PULANDO", W / 2, H * 0.94, t, 212.5, None, 20, ORANGE)
    else:
        pr = americas_map(ctx, W * 0.10, H * 0.08, W * 0.80, H * 0.84, (-85, -40), (-20, 8), appear(t, 216))
        river(ctx, AMAZON, pr, 1)
        x, y, ang = along(AMAZON, pr, clamp((t - 217) / 5))
        shark_icon(ctx, x, y, 0.7, ang + math.pi, 1)
        px, py = pr(-73.2, -3.75)
        pin(ctx, px, py, appear(t, 219), "IQUITOS, PERU", side="l")
        label(ctx, "~4.000 KM RIO ACIMA", W / 2, H * 0.94, t, 220, None, 22, ORANGE)
    vignette(ctx, 0.5, t)


def mangrove(ctx, x, y, s, a=1.0):
    for i in range(5):
        ctx.move_to(x, y - 40 * s)
        ctx.curve_to(x - 10 * s + i * 5 * s, y - 20 * s, x - 30 * s + i * 15 * s, y - 5 * s, x - 30 * s + i * 15 * s,
                     y + 20 * s)
        rgba(ctx, (0.40, 0.30, 0.20), a)
        ctx.set_line_width(3 * s)
        ctx.stroke()
    line(ctx, x, y - 40 * s, x, y - 90 * s, (0.40, 0.30, 0.20), a, 5 * s)
    for dx, dy, r in ((-20, -100, 26), (10, -110, 30), (25, -92, 22)):
        circle(ctx, x + dx * s, y + dy * s, r * s, (0.22, 0.48, 0.30), a)


def sc_nursery(ctx, t):
    if t < 245:
        # estuário: água doce turva (esquerda) encontrando o mar (direita)
        g = cairo.LinearGradient(0, 0, W, 0)
        g.add_color_stop_rgb(0, 0.38, 0.36, 0.22)
        g.add_color_stop_rgb(1, 0.12, 0.30, 0.36)
        ctx.set_source(g)
        ctx.paint()
        ctx.rectangle(0, 0, W, 110)
        rgba(ctx, (0.75, 0.80, 0.80))
        ctx.fill()
        surface_line(ctx, t, 110, sky=False)
        ctx.move_to(0, H * 0.86)
        for x in range(0, W + 20, 20):
            ctx.line_to(x, H * 0.86 + math.sin(x * 0.02) * 8)
        ctx.line_to(W, H)
        ctx.line_to(0, H)
        ctx.close_path()
        ink(ctx, (0.45, 0.40, 0.30), 1, 2)
        for x in (W * 0.06, W * 0.16, W * 0.26):
            mangrove(ctx, x, H * 0.86, 1.4)
        for i in range(5):  # filhotes entre as raízes
            px = W * 0.12 + i * 70 + math.sin(t * 0.7 + i) * 30
            shark(ctx, px, H * 0.62 + (i % 2) * 50, 110, t + i, "bull", facing=1 if i % 2 else -1,
                  a=appear(t, 227 + i * 0.3))
        callout(ctx, W * 0.22, H * 0.64, 90, W * 0.40, H * 0.22, "FILHOTES NO ESTUÁRIO", window(t, 228, 244))
        k = appear(t, 233)
        shark(ctx, W * 0.82, H * 0.48, 420, t, "bull", facing=-1, a=k)
        callout(ctx, W * 0.82, H * 0.48, 110, W * 0.70, H * 0.86, "TUBARÕES GRANDES — INCLUSIVE CABEÇA-CHATA",
                window(t, 237, 244))
        kicker(ctx, "FOZ DE RIO · ÁGUA TURVA · BERÇÁRIO", W / 2, H * 0.30, t, 240, None, 22, WHITE)
    else:
        # cidade na foz do rio
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgb(0, 0.55, 0.70, 0.80)
        g.add_color_stop_rgb(1, 0.85, 0.88, 0.85)
        ctx.set_source(g)
        ctx.paint()
        skyline(ctx, H * 0.60, t, 1, W * 0.05, W * 0.50, seed=9, col=(0.66, 0.68, 0.72), lit=0.2)
        ctx.rectangle(0, H * 0.60, W * 0.55, H)
        ink(ctx, SAND, 1, 2)
        ctx.move_to(W * 0.20, H * 0.60)
        ctx.curve_to(W * 0.30, H * 0.75, W * 0.45, H * 0.70, W * 0.55, H * 0.78)
        ctx.line_to(W * 0.55, H * 0.82)
        ctx.curve_to(W * 0.40, H * 0.78, W * 0.28, H * 0.80, W * 0.18, H * 0.62)
        ctx.close_path()
        rgba(ctx, (0.45, 0.42, 0.28))
        ctx.fill()
        ctx.rectangle(W * 0.55, H * 0.60, W, H)
        rgba(ctx, (0.22, 0.45, 0.50))
        ctx.fill()
        for i in range(3):
            shark(ctx, W * 0.70 + i * 120 + math.sin(t + i) * 20, H * 0.78 + i * 25, 160, t + i, "bull",
                  facing=-1, a=appear(t, 248 + i * 0.5))
        label(ctx, "EXATAMENTE ONDE AS CIDADES COSTUMAM FICAR", W / 2, H * 0.14, t, 250.5, None, 24,
              (0.10, 0.15, 0.20))
    vignette(ctx, 0.5, t)


# ------------------------------------------------------------------ 4:16 – 4:38 Nova Jersey, 1916
def sc_1916(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.80, 0.74, 0.60)
    g.add_color_stop_rgb(1, 0.55, 0.48, 0.36)
    ctx.set_source(g)
    ctx.paint()
    for i in range(14):
        x = i * 100 + 30
        line(ctx, x, H * 0.48, x, H * 0.30 - (i % 3) * 20, (0.40, 0.33, 0.24), 1, 6)
        circle(ctx, x, H * 0.28 - (i % 3) * 20, 40, (0.45, 0.42, 0.30), 0.9)
    ctx.rectangle(0, H * 0.48, W, H * 0.12)
    ink(ctx, (0.62, 0.54, 0.40), 1, 2)
    ctx.rectangle(0, H * 0.60, W, H * 0.40)
    rgba(ctx, (0.42, 0.44, 0.36))
    ctx.fill()
    line(ctx, 0, H * 0.60, W, H * 0.60, (0.85, 0.82, 0.70), 1, 2)
    for i, x in enumerate((W * 0.30, W * 0.45)):
        rig.figure(ctx, x, H * 0.60 + 55, 0.9, rig.p_tread(t + i), outfit="oldtime", facing=1, ground=False, t=t)
    fx = kf(t, [(262, W * 1.1), (272, W * 0.55)])
    ctx.move_to(fx, H * 0.60)
    ctx.line_to(fx + 18, H * 0.60 - 34)
    ctx.line_to(fx + 40, H * 0.60)
    ctx.close_path()
    ink(ctx, (0.30, 0.32, 0.30), appear(t, 262), 2)
    ctx.rectangle(0, H * 0.60 + 2, W, H)
    rgba(ctx, (0.42, 0.44, 0.36), 0.55)
    ctx.fill()
    chapter(ctx, "NOVA JERSEY · EUA", "1916", "", W / 2, H * 0.14, t, 256.3, None, 56)
    label(ctx, "4 MORTES EM MENOS DE 2 SEMANAS", W / 2, H * 0.22, t, 258, None, 22, (0.15, 0.12, 0.08))
    label(ctx, "DUAS NUM RIACHO, LONGE DA PRAIA", W / 2, H * 0.94, t, 264.5, 272.5, 22, WHITE)
    label(ctx, "SUSPEITO: CABEÇA-CHATA?", W / 2, H * 0.94, t, 272.5, None, 22, ORANGE) if t > 272.5 else None
    rgba(ctx, (0.6, 0.5, 0.3), 0.15)
    ctx.paint()
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 4:38 – 6:11 Recife: incidentes e causas
def sc_brazil(ctx, t):
    ocean(ctx, t, rays=False)
    if t < 291:
        chapter(ctx, "AGORA VAMOS PARA O BRASIL", "PERNAMBUCO", "", W / 2, H * 0.16, t, 278.3, None, 50)
        x0, x1, y = W * 0.10, W * 0.90, H * 0.62
        line(ctx, x0, y, x1, y, SOFT, appear(t, 280), 2)
        for yr in range(1990, 2026, 5):
            xx = lerp(x0, x1, (yr - 1990) / 35)
            text(ctx, str(yr), xx, y + 30, 14, SOFT, appear(t, 280), "c", "bold", sp=1)
        rnd = random.Random(7)
        n = int(clamp((t - 283) / 6) * 60)
        for i in range(n):
            yr = 1992 + rnd.random() ** 1.6 * 32
            xx = lerp(x0, x1, (yr - 1990) / 35)
            yy = y - 16 - (i % 6) * 14
            col = RED if rnd.random() < 0.35 else ORANGE
            circle(ctx, xx, yy, 5, col)
        label(ctx, "1992: COMEÇAM OS INCIDENTES", W / 2, H * 0.80, t, 283.5, None, 22, ORANGE)
        kicker(ctx, "VERMELHO: FATAIS (ILUSTRATIVO)", W / 2, H * 0.86, t, 290, None, 14, SOFT)
    else:
        pe_coast(ctx, t, appear(t, 291), strip=appear(t, 294, 2.5))
        label(ctx, "QUASE TODOS NESTE TRECHO", W / 2, H * 0.06 + 20, t, 295, None, 20, WHITE)
    vignette(ctx, 0.5, t)


def sc_why_here(ctx, t):
    if t < 325:
        ocean(ctx, t, rays=False)
        man = 1 - appear(t, 317, 3)
        pe_coast(ctx, t, 1, strip=1 - appear(t, 306, 1), suape=appear(t, 314.5), mangrove=man)
        big_title(ctx, [("POR QUE ", WHITE, "black"), ("ALI?", ORANGE, "light")], W / 2, H * 0.06 + 34, t, 305.5,
                  313, 40)
        label(ctx, "OBRAS ALTERARAM ESTUÁRIOS E MANGUEZAIS", W / 2, H * 0.96, t, 317.5, None, 20, ORANGE)
        if t > 321:
            for i in range(3):
                k = clamp((t - 321 - i * 0.4) / 3)
                shark_icon(ctx, W * 0.62, lerp(H * 0.75, H * 0.35, k), 0.6, -math.pi / 2, appear(t, 321 + i * 0.4))
    elif t < 341:
        # o corredor: canal fundo logo depois dos arrecifes
        cam(ctx, W * 0.62, H * 0.62, 1.15)
        sx = kf(t, [(328, W * 1.15), (340, W * 0.65)], fn=lambda k: k)

        def mid(c):
            shark(c, sx, H * 0.80, 230, t, "bull", facing=-1, swim=0.8)

        R.scene(ctx, t, tide=1.0, murk=0.8, mid=mid, sign=False)
        ctx.restore()
        callout(ctx, W * 0.78, H * 0.72, 90, W * 0.80, H * 0.16, "CANAL FUNDO — UM CORREDOR COLADO NA AREIA",
                window(t, 333, 341))
    elif t < 347:
        # rios trazendo água turva
        ocean(ctx, t, top=(0.30, 0.34, 0.22), bot=(0.08, 0.10, 0.06))
        for i in range(30):
            ph = ((t * 0.3 + i / 30) % 1)
            circle(ctx, W * 0.10 + ph * W * 0.8, H * 0.30 + math.sin(i) * 120, 60 * ph + 10, (0.45, 0.38, 0.22),
                   0.25 * (1 - ph))
        label(ctx, "RIOS TRAZEM ÁGUA TURVA, ESGOTO E RESTOS DE ANIMAIS", W / 2, H * 0.88, t, 341.5, None, 20, WHITE)
    else:
        ocean(ctx, t, top=(0.16, 0.40, 0.46), bot=(0.04, 0.14, 0.18))
        ctx.rectangle(0, 0, W, 150)
        rgba(ctx, (0.78, 0.84, 0.86))
        ctx.fill()
        surface_line(ctx, t, 150, sky=False)
        bx = kf(t, [(347, -300), (360, W * 0.9)], fn=lambda k: k)
        ctx.move_to(bx - 260, 120)
        ctx.line_to(bx + 260, 120)
        ctx.line_to(bx + 220, 180)
        ctx.line_to(bx - 240, 180)
        ctx.close_path()
        ink(ctx, (0.55, 0.30, 0.28), 1, 2.5)
        rrect(ctx, bx - 140, 60, 220, 60, 4)
        ink(ctx, (0.85, 0.86, 0.88), 1, 2)
        for i in range(2):
            shark(ctx, bx - 320 - i * 160, 260 + i * 60, 200, t + i, "bull", facing=1, a=appear(t, 348))
        label(ctx, "NAVIOS QUE ATRAEM TUBARÕES", W / 2, H * 0.88, t, 348, 352.5, 22, WHITE)
        label(ctx, "JUNTAS: UM LUGAR PERFEITO PARA UM ENCONTRO", W / 2, H * 0.88, t, 353, None, 22, ORANGE)
    vignette(ctx, 0.5, t)


def sc_tiger(ctx, t):
    murky(ctx, t, 0.7)
    shark(ctx, W * 0.36, H * 0.40, 480, t, "bull", facing=1)
    shark(ctx, kf(t, [(360, W * 1.2), (363, W * 0.68)]), H * 0.66, 560, t, "tiger", facing=-1)
    name_tag(ctx, "Tubarão-tigre", W * 0.55, H * 0.92, t, 361.5, None, 24)
    label(ctx, "ÁGUA MORNA · TURVA · PERTO DA COSTA", W / 2, H * 0.10, t, 366.5, None, 22, WHITE)
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 6:11 – 6:43 CEMIT e o padrão
def sc_cemit(ctx, t):
    ocean(ctx, t)
    if t < 379:
        chapter(ctx, "GOVERNO DE PERNAMBUCO", "2004", "CEMIT", W / 2, H * 0.16, t, 374.0, None, 52)
        shark_sign(ctx, W * 0.5, H * 0.62, 1.4, window(t, 371, 374.5))
        k = appear(t, 375)
        sx = kf(t, [(375, W * 1.1), (379, W * 0.6)])
        shark(ctx, sx, H * 0.60, 440, t, "bull", facing=-1, a=k)
        circle(ctx, sx + 30, H * 0.60 - 70, 7, YELLOW, k)
        for r in range(3):
            rr = ((t * 60 + r * 30) % 90)
            ctx.new_sub_path()
            ctx.arc(sx + 30, H * 0.60 - 70, rr, 0, 2 * math.pi)
            rgba(ctx, YELLOW, k * (1 - rr / 90))
            ctx.set_line_width(2)
            ctx.stroke()
        callout(ctx, sx + 30, H * 0.60 - 70, 16, W * 0.75, H * 0.32, "TUBARÕES MARCADOS", window(t, 377, 379))
    else:
        label(ctx, "O PADRÃO", W / 2, H * 0.14, t, 379.2, None, 40, ORANGE)
        items = [("DEPOIS DOS ARRECIFES", 381.5), ("MARÉ CHEIA", 391.3), ("DEPOIS DE CHUVA · ÁGUA TURVA", 392.8),
                 ("FIM DE TARDE", 395.0)]
        for i, (nm, c0) in enumerate(items):
            a = appear(t, c0)
            y = H * 0.30 + i * 80
            card(ctx, W * 0.22, y - 30, W * 0.56, 60, a)
            check(ctx, W * 0.22 + 36, y, 18, appear(t, c0 + 0.3), RED)
            text(ctx, nm, W * 0.22 + 70, y + 8, 22, WHITE, a, "l", "bold", sp=2)
        if t > 399:
            shark_sign(ctx, W * 0.86, H * 0.95, 0.8, appear(t, 399))
            label(ctx, "POR ISSO A PLACA EXISTE", W * 0.40, H * 0.92, t, 399.2, None, 24, YELLOW)
    vignette(ctx, 0.55, t)


# ------------------------------------------------------------------ 6:43 – 7:25 por que ele morde
def sc_why_bite(ctx, t):
    murky(ctx, t, 0.85)
    if t < 416:
        label(ctx, "POR QUE UM TUBARÃO MORDE UMA PESSOA?", W / 2, H * 0.12, t, 403.2, 409, 28, WHITE)
        label(ctx, "NA MAIORIA DOS CASOS: NÃO É FOME DE GENTE", W / 2, H * 0.12, t, 409, None, 24, ORANGE)
        shark(ctx, W * 0.50, H * 0.42, 460, t, "bull", facing=-1)
        preys = [("PEIXES", 410.0), ("RAIAS", 410.8), ("TUBARÕES", 411.4), ("TARTARUGAS", 412.2), ("AVES", 413.0)]
        for i, (nm, c0) in enumerate(preys):
            a = appear(t, c0)
            x = W / 2 + (i - 2) * 200
            y = H * 0.78
            if i == 0:
                fish(ctx, x, y, 1.0, t, a=a)
            elif i == 1:
                ctx.move_to(x - 40, y)
                ctx.line_to(x, y - 30)
                ctx.line_to(x + 40, y)
                ctx.line_to(x, y + 30)
                ctx.close_path()
                ink(ctx, (0.60, 0.55, 0.45), a, 2)
                line(ctx, x, y + 30, x, y + 70, (0.60, 0.55, 0.45), a, 3)
            elif i == 2:
                shark(ctx, x, y, 110, t, "bull", facing=-1, a=a)
            elif i == 3:
                turtle(ctx, x, y, 0.45, t, a)
            else:
                ctx.move_to(x - 40, y)
                ctx.curve_to(x - 20, y - 30, x - 5, y - 10, x, y)
                ctx.curve_to(x + 5, y - 10, x + 20, y - 30, x + 40, y)
                rgba(ctx, WHITE, a)
                ctx.set_line_width(4)
                ctx.stroke()
            text(ctx, nm, x, y + 70, 16, WHITE, a, "c", "bold", sp=2)
    elif t < 425:
        sx, sy, L = W * 0.50, H * 0.50, 760
        shark(ctx, sx, sy, L, t, "bull", facing=-1, swim=0.4)
        fog(ctx, 0.25 * (1 - appear(t, 418, 1)))
        k = appear(t, 419)
        if k > 0:
            ctx.move_to(sx - L * 0.38, sy - 25)
            ctx.curve_to(sx - L * 0.1, sy - 35, sx + L * 0.2, sy - 25, sx + L * 0.45, sy - 10)
            ctx.set_dash([8, 6])
            rgba(ctx, YELLOW, k)
            ctx.set_line_width(3)
            ctx.stroke()
            ctx.set_dash([])
            callout(ctx, sx, sy - 30, 30, W * 0.70, H * 0.18, "LINHA LATERAL: SENTE VIBRAÇÕES", k)
        k2 = appear(t, 422)
        if k2 > 0:
            rnd = random.Random(3)
            for i in range(30):
                circle(ctx, sx - L * 0.45 + rnd.uniform(0, 60), sy + rnd.uniform(-25, 25), 2.5, YELLOW, k2)
            callout(ctx, sx - L * 0.42, sy, 40, W * 0.18, H * 0.82, "POROS: SINAIS ELÉTRICOS", k2)
    else:
        ctx.rectangle(0, 0, W, 120)
        rgba(ctx, (0.62, 0.62, 0.52))
        ctx.fill()
        surface_line(ctx, t, 120, sky=False)
        px = W * 0.40
        p = rig.p_tread(t * 2.5)
        rig.figure(ctx, px, 120 + 70, 1.0, p, outfit="friend", facing=1, ground=False, t=t)
        for r in range(4):
            rr = ((t * 140 + r * 60) % 260)
            ctx.new_sub_path()
            ctx.arc(px, 140, rr, 0, math.pi)
            rgba(ctx, WHITE, 0.6 * (1 - rr / 260) * appear(t, 426))
            ctx.set_line_width(2)
            ctx.stroke()
        fog(ctx, 0.25)
        sx = kf(t, [(428, W * 1.1), (433, W * 0.55), (434.2, px + 40), (436, W * 0.70), (440, W * 0.60),
                    (441.5, px + 30), (445, W * 0.80)])
        sy = kf(t, [(428, H * 0.85), (433, H * 0.65), (434.2, 230), (436, H * 0.60), (440, H * 0.55),
                    (441.5, 220), (445, H * 0.80)])
        fc = -1 if t < 436 or (440 < t < 441.5) else 1
        shark(ctx, sx, sy, 300, t, "bull", facing=fc, a=appear(t, 428), mouth=window(t, 440.8, 442.5, 0.3))
        label(ctx, "PARECE UM ANIMAL SE DEBATENDO", W / 2, H * 0.92, t, 427, 432, 22, WHITE)
        label(ctx, "MORDE PARA DESCOBRIR O QUE É", W / 2, H * 0.92, t, 432, 436, 22, ORANGE)
        label(ctx, "PRIMEIRO UM EMPURRÃO, DEPOIS VOLTA E MORDE", W / 2, H * 0.92, t, 436, None, 20, RED)
        if 434 < t < 435:
            rgba(ctx, WHITE, 0.3 * (1 - (t - 434)))
            ctx.paint()
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 7:25 – 9:40 o que você faria
def mini_panel(ctx, x, y, w, h, a, kind, t):
    """Painel A/B/C com mini-cena no corte lateral da praia."""
    card(ctx, x, y, w, h, a, fill=(0.10, 0.28, 0.33))
    ctx.save()
    rrect(ctx, x + 6, y + 6, w - 12, h - 12, 6)
    ctx.clip()
    ctx.translate(x + 6, y + 6)
    ctx.scale((w - 12) / W, (h - 12) / H)
    tide = 1.0

    def mid(c):
        if kind == "A":
            for i, xx in enumerate((W * 0.74, W * 0.80)):
                c.save()
                rig.figure(c, xx, R.sea_level(tide) + 50, 0.8, rig.p_tread(t + i), outfit=["friend", "swimmer"][i],
                           facing=1, ground=False, t=t)
                c.restore()
        elif kind == "B":
            rig.figure(c, W * 0.48, R.ground_y(W * 0.48), 0.8, rig.p_stand(t), outfit="swimmer", facing=1,
                       shadow=False)
        else:
            rig.figure(c, W * 0.74, R.sea_level(tide) + 50, 0.8, rig.p_tread(t * 3), outfit="swimmer", facing=1,
                       ground=False, t=t)

    R.scene(ctx, t, tide=tide, murk=1.0, mid=mid, sign=False)
    if kind == "C":
        for r in range(3):
            rr = ((t * 120 + r * 40) % 120)
            ctx.new_sub_path()
            ctx.arc(W * 0.74, R.sea_level(tide), rr, 0, math.pi)
            rgba(ctx, WHITE, 0.8 * (1 - rr / 120))
            ctx.set_line_width(3)
            ctx.stroke()
    ctx.restore()
    rgba(ctx, (0, 0, 0), 0.0)


PANELS = [("A", "IR JUNTO, MAS FICAR PERTO", 486.5), ("B", "FICAR DO LADO DE DENTRO", 489.5),
          ("C", "BATER NA ÁGUA PARA ESPANTAR", 491.5)]


def sc_choice(ctx, t):
    if t < 484:
        tide = 1.0
        fx = W * 0.36
        z = kf(t, [(445, 1.0), (452, 1.25), (466, 1.25), (470, 1.6), (476, 1.6), (480, 1.25)])
        ccx = kf(t, [(445, W * 0.50), (452, W * 0.36), (466, W * 0.55), (470, R.REEF_X), (476, W * 0.50),
                     (480, W * 0.36)])
        ccy = kf(t, [(445, H * 0.52), (470, H * 0.56), (480, H * 0.50)])
        cam(ctx, ccx, ccy, z)

        def mid(c):
            p = rig.p_stand(t)
            if t > 481:
                p.update(armF=160, elbowF=20, armB=150, elbowB=20)  # tirando a camisa
            rig.figure(c, fx, R.ground_y(fx), 0.8, p, outfit="friend", facing=1, t=t)
            rig.figure(c, fx - 60, R.ground_y(fx - 60), 0.8, rig.p_stand(t + 1), outfit="swimmer", facing=1, t=t)
            # canal de água doce despejando água escura
            if t > 474:
                for i in range(12):
                    ph = ((t * 0.4 + i / 12) % 1)
                    circle(c, W * 0.40 + ph * 300, R.sea_level(tide) + 20 + ph * 60, 20 + 50 * ph, (0.30, 0.26, 0.16),
                           0.35 * (1 - ph) * appear(t, 474))

        R.scene(ctx, t, tide=tide, murk=1.0, dusk=0.7, mid=mid)
        ctx.restore()
        chapter(ctx, "BOA VIAGEM · JULHO · FIM DE TARDE", "O QUE VOCÊ", "FARIA?", W / 2, H * 0.14, t, 445.5, 452, 44)
        kicker(ctx, "MARÉ SUBINDO · ÁGUA MARROM · FOZ DE UM CANAL AO LADO", W / 2, H * 0.10, t, 461, None, 15,
               (0.12, 0.15, 0.2))
        vignette(ctx, 0.35, t)
        return
    ocean(ctx, t, rays=False)
    label(ctx, "PRIMEIRA DECISÃO", W / 2, 70, t, 484.2, None, 32, WHITE)
    for i, (lt, nm, c0) in enumerate(PANELS):
        a = appear(t, c0)
        x = W / 2 + (i - 1) * 370 - 165
        mini_panel(ctx, x, H * 0.22, 330, 200, a, lt, t)
        text(ctx, lt, x + 12, H * 0.22 + 240, 30, ORANGE, a, "l", "black")
        text(ctx, nm, x + 44, H * 0.22 + 238, 14, WHITE, a, "l", "bold", sp=1)
    k = appear(t, 498)
    if k > 0:
        text(ctx, "ESCOLHA UMA ANTES DE EU TE CONTAR", W / 2, H * 0.80, 26, ORANGE, k, "c", "black", sp=2)
        rem = max(0, 501.5 - t)
        text(ctx, f"{math.ceil(rem)}" if rem > 0 else "", W / 2, H * 0.92, 44, WHITE, k, "c", "black")
    vignette(ctx, 0.5, t)


def sc_answers(ctx, t):
    ocean(ctx, t, rays=False)
    marks = {"C": (502, 516, "x"), "A": (516, 537, "x"), "B": (537, 544, "v")}
    for i, (lt, nm, _) in enumerate(PANELS):
        x = W / 2 + (i - 1) * 370 - 165
        s0, s1, kind = marks[lt]
        focus = window(t, s0, s1)
        a = 0.45 + 0.55 * focus if t < 544 else 1
        card(ctx, x, 40, 330, 70, 1, fill=(0.10, 0.28, 0.33) if focus < 0.5 else (0.16, 0.40, 0.46))
        text(ctx, lt + "  " + nm, x + 165, 84, 13, ORANGE if focus > 0.5 else WHITE, a, "c", "bold", sp=1)
        if t > s0 + 1:
            (xmark if kind == "x" else check)(ctx, x + 310, 75, 16, appear(t, s0 + 1))
    if t < 516:
        label(ctx, "A PIOR", W / 2, H * 0.28, t, 504.5, None, 44, RED)
        # agitação na superfície em água turva = sinal de animal em apuros
        lvl = H * 0.50
        ctx.rectangle(0, lvl, W, H)
        rgba(ctx, (0.30, 0.30, 0.20), 0.6)
        ctx.fill()
        surface_line(ctx, t, lvl, sky=False)
        rig.figure(ctx, W * 0.40, lvl + 60, 0.9, rig.p_tread(t * 3), outfit="swimmer", facing=1, ground=False, t=t)
        for r in range(4):
            rr = ((t * 160 + r * 60) % 300)
            ctx.new_sub_path()
            ctx.arc(W * 0.40, lvl + 10, rr, 0, math.pi)
            rgba(ctx, WHITE, 0.6 * (1 - rr / 300))
            ctx.set_line_width(2)
            ctx.stroke()
        shark(ctx, kf(t, [(507, W * 1.1), (513, W * 0.70)]), H * 0.82, 300, t, "bull", facing=-1,
              a=appear(t, 507) * 0.8)
        label(ctx, "PARA ELE, VOCÊ PARECE UM ANIMAL EM APUROS", W / 2, H * 0.40, t, 513, None, 20, WHITE)
    elif t < 537:
        label(ctx, "FICAR EM GRUPO AJUDA...", W / 2, H * 0.26, t, 516.5, 523, 32, WHITE)
        label(ctx, "MAS VOCÊ JUNTOU TODOS OS FATORES DE RISCO", W / 2, H * 0.26, t, 523, None, 26, RED)
        facts = [("DEPOIS DOS ARRECIFES", 527.0), ("MARÉ CHEIA", 528.3), ("ÁGUA TURVA", 529.2), ("FIM DE TARDE", 530.0),
                 ("PERTO DA FOZ DE UM RIO", 531.0)]
        for i, (nm, c0) in enumerate(facts):
            a = appear(t, c0)
            y = H * 0.38 + i * 62
            card(ctx, W * 0.25, y - 24, W * 0.50, 48, a)
            circle(ctx, W * 0.25 + 30, y, 12, RED, a)
            text(ctx, nm, W * 0.25 + 56, y + 7, 20, WHITE, a, "l", "bold", sp=2)
    else:
        label(ctx, "ACERTOU", W / 2, H * 0.42, t, 537.3, None, 56, GREEN)
        label(ctx, "MAS HOJE, NEM ISSO É O IDEAL", W / 2, H * 0.54, t, 542, None, 28, ORANGE)
    vignette(ctx, 0.5, t)


def sc_rules(ctx, t):
    if t < 573:
        tide = kf(t, [(544, 0.0)])
        cam(ctx, W * 0.48, H * 0.50, 1.25)

        def mid(c):
            for i, xx in enumerate((W * 0.44, W * 0.50)):
                rig.figure(c, xx, R.ground_y(xx), 0.8, rig.p_stand(t + i), outfit=["kid", "swimmer"][i],
                           facing=1 if i else -1, shadow=False)

        R.scene(ctx, t, tide=0.0, murk=0.05, dusk=0.1, mid=mid)
        ctx.restore()
        kicker(ctx, "PISCINA NATURAL · MARÉ BAIXA · ÁGUA CLARA · ATÉ A CINTURA", W / 2, H * 0.10, t, 545.5, None, 15,
               (0.12, 0.15, 0.2))
        rules = [("NÃO PASSE A LINHA DOS ARRECIFES", 555.0), ("NADA DE ÁGUA TURVA / FOZ DE RIO", 557.5),
                 ("EVITE O COMEÇO DA MANHÃ E O FIM DA TARDE", 563.0), ("SEM SANGRAMENTO, BRILHOS OU PESCA", 565.5),
                 ("RESPEITE BANDEIRAS E PLACAS", 570.0)]
        for i, (nm, c0) in enumerate(rules):
            a = window(t, c0, 573)
            y = H * 0.70 + (i % 3) * 52
            x = W * 0.06 if i < 3 else W * 0.54
            card(ctx, x, y - 22, W * 0.42, 44, a)
            check(ctx, x + 24, y, 13, appear(t, c0 + 0.2))
            text(ctx, nm, x + 46, y + 6, 15, WHITE, a, "l", "bold", sp=1)
        vignette(ctx, 0.35, t)
        return
    # hoje: ficar na areia
    cam(ctx, W * 0.30, H * 0.48, 1.3)

    def mid(c):
        p = rig.pose(lean=-8, thighF=86, kneeF=6, thighB=82, kneeB=4, armF=-25, elbowF=10, armB=-30, elbowB=10)
        rig.figure(c, W * 0.22, R.DRY, 0.8, p, outfit="swimmer", facing=1, t=t)

    R.scene(ctx, t, tide=1.0, murk=1.0, dusk=0.7, mid=mid)
    ctx.restore()
    big_title(ctx, [("FICAR ", WHITE, "black"), ("NA AREIA", ORANGE, "light")], W / 2, H * 0.16, t, 577.5, None, 52)
    vignette(ctx, 0.35, t)


# ------------------------------------------------------------------ 9:40 – 11:06 a mordida e o socorro
def sc_attack(ctx, t):
    if t < 603:
        cam(ctx, W * 0.62, H * 0.56, 1.3)
        fx = W * 0.78

        def mid(c):
            p = rig.p_tread(t * (3 if t > 586 else 1))
            rig.figure(c, fx, R.sea_level(1) + 50, 0.8, p, outfit="friend", facing=-1, ground=False, t=t)
            rig.figure(c, W * 0.30, R.DRY, 0.8, rig.p_shout(t) if t > 597 else rig.p_stand(t), outfit="swimmer",
                       facing=1, t=t)
            if t > 590.5:
                k = appear(t, 590.5, 3)
                lvl = R.sea_level(1)
                for i in range(10):
                    rnd = random.Random(i)
                    r_ = 10 + 18 * k
                    circle(c, fx + rnd.uniform(-50, 50) * k, lvl + r_ + 4 + rnd.uniform(0, 50) * k, r_,
                           (0.40, 0.08, 0.08), 0.30 * k)
            if t > 592:
                shark(c, kf(t, [(592, fx + 40), (600, W * 1.2)]), R.sea_level(1) + 140, 200, t, "bull", facing=1,
                      a=0.6)

        R.scene(ctx, t, tide=1.0, murk=1.0, dusk=0.8, mid=mid)
        ctx.restore()
        if 586 < t < 589:
            text(ctx, "AAAH!", W * 0.75, H * 0.22, 40, WHITE, window(t, 586.2, 589), "c", "black")
        label(ctx, "O TUBARÃO MORDEU E SOLTOU", W / 2, H * 0.92, t, 593.5, None, 22, WHITE)
        label(ctx, "1ª REGRA: NÃO VIRE MAIS UMA VÍTIMA", W / 2, H * 0.12, t, 597.5, None, 26, ORANGE)
        vignette(ctx, 0.4, t)
        return
    ocean(ctx, t, rays=False)
    if t < 609:
        rig.figure(ctx, W * 0.30, H * 0.88, 1.5, rig.p_shout(t), outfit="swimmer", facing=1, t=t)
        rig.figure(ctx, W * 0.62, H * 0.88, 1.5, rig.p_phone(t), outfit="casual", facing=-1, t=t)
        big_title(ctx, [("SAMU ", WHITE, "black"), ("192", ORANGE, "black")], W * 0.70, H * 0.30, t, 603.8, None, 60)
        big_title(ctx, [("BOMBEIROS ", WHITE, "black"), ("193", ORANGE, "black")], W * 0.70, H * 0.42, t, 606, None,
                  44)
    else:
        sx, sy, L = W * 0.45, H * 0.52, 820
        shark(ctx, sx, sy, L, t, "bull", facing=1, swim=0.2)
        Hh = L * 0.175
        ex, ey = sx + L * 0.43, sy - Hh * 0.35 * 0.55
        callout(ctx, ex, ey, 22, W * 0.70, H * 0.16, "OLHOS", appear(t, 615.5), 22)
        callout(ctx, sx + L * 0.32, sy, 40, W * 0.55, H * 0.86, "BRÂNQUIAS", appear(t, 616.3), 22)
        check(ctx, W * 0.70 + 100, H * 0.16 - 8, 16, appear(t, 615.8))
        check(ctx, W * 0.55 + 150, H * 0.86 - 8, 16, appear(t, 616.6))
        k = appear(t, 617.5)
        xmark(ctx, sx + L * 0.50, sy + 6, 26, k)
        text(ctx, "NÃO NO FOCINHO", W * 0.92, H * 0.66, 18, RED, k, "c", "black", sp=1)
        label(ctx, "SE AINDA ESTIVER SENDO ATACADO", W / 2, H * 0.08, t, 609.3, None, 22, WHITE)
        label(ctx, "NA MAIORIA DOS CASOS: MORDE UMA VEZ E VAI EMBORA", W / 2, H * 0.08, t, 620.5, None, 20, ORANGE) \
            if t > 620.5 else None
    vignette(ctx, 0.5, t)


def sc_first_aid(ctx, t):
    if t < 640:
        cam(ctx, W * 0.40, H * 0.50, 1.35)
        fx = kf(t, [(625, W * 0.66), (630, W * 0.40)], fn=lambda k: k)

        def mid(c):
            if t < 630:
                rig.figure(c, fx, R.ground_y(fx), 0.8, rig.p_walk(t, 1.2), outfit="swimmer", facing=-1, t=t)
                rig.figure(c, fx + 40, R.ground_y(fx + 40), 0.8, rig.p_lie(0), outfit="friend", facing=1, t=0)
            else:
                rig.figure(c, W * 0.40, R.DRY, 0.8, rig.p_lie(0), outfit="friend", facing=1, t=0)
                for i in range(6):
                    circle(c, W * 0.40 - 50 - i * 6, R.DRY - 6, 6 + i, (0.55, 0.05, 0.05), 0.8)

        R.scene(ctx, t, tide=1.0, murk=1.0, dusk=0.8, mid=mid)
        ctx.restore()
        label(ctx, "O MAIOR PERIGO AGORA: O SANGRAMENTO", W / 2, H * 0.12, t, 630.5, None, 26, RED)
        label(ctx, "UMA MORDIDA NA PERNA PODE ATINGIR ARTÉRIAS GRANDES", W / 2, H * 0.90, t, 634, None, 18, WHITE)
        vignette(ctx, 0.4, t)
        return
    studio(ctx, t, H * 0.86)
    # close na perna: pressão e torniquete
    y = H * 0.70
    limb(ctx, [(-60, y - 20), (W * 0.36, y - 6), (W * 0.62, y + 4)], 96, SKIN)
    ellipse_path(ctx, W * 0.66, y - 4, 50, 30, -0.6)
    ink(ctx, SKIN, 1, 2.5)
    rrect(ctx, -60, y - 75, 220, 112, 20)
    ink(ctx, (0.20, 0.24, 0.30), 1, 2.5)
    wx = W * 0.46
    for i in range(7):
        line(ctx, wx - 40 + i * 12, y - 40, wx - 30 + i * 12, y + 30, (0.55, 0.05, 0.05), 0.9, 4)
    if t < 647:
        k = appear(t, 640.5)
        rrect(ctx, wx - 70, y - 60, 140, 110, 12)
        ink(ctx, (0.90, 0.88, 0.82), k, 2)
        for hx in (wx - 30, wx + 30):
            ellipse_path(ctx, hx, y - 70 + 6 * math.sin(t * 3), 30, 18)
            ink(ctx, SKIN, k, 2)
        label(ctx, "PRESSÃO DIRETA E FIRME", W * 0.75, H * 0.22, t, 640.5, None, 26, ORANGE)
        kicker(ctx, "CAMISA · TOALHA · AS MÃOS", W * 0.75, H * 0.28, t, 644, None, 16, WHITE)
    else:
        k = appear(t, 647.5)
        tx = W * 0.26
        rrect(ctx, tx - 14, y - 62, 28, 120, 6)
        ink(ctx, (0.25, 0.22, 0.20), k, 2)
        rrect(ctx, tx - 8, y - 90, 16, 34, 4)
        ink(ctx, (0.70, 0.70, 0.72), k, 2)
        callout(ctx, tx, y - 20, 50, W * 0.18, H * 0.22, "TORNIQUETE ACIMA DA FERIDA", appear(t, 648))
        kicker(ctx, "CINTO · CORDA · BERMUDA TORCIDA", W * 0.70, H * 0.22, t, 651, None, 16, WHITE)
        if t > 654:
            card(ctx, W * 0.58, H * 0.30, 300, 90, appear(t, 654))
            text(ctx, "ANOTE A HORA", W * 0.58 + 150, H * 0.30 + 34, 18, WHITE, appear(t, 654), "c", "bold", sp=2)
            text(ctx, "17:42", W * 0.58 + 150, H * 0.30 + 74, 34, ORANGE, appear(t, 654.5), "c", "black")
        label(ctx, "DEITADO · AQUECIDO · ACORDADO, ATÉ A AMBULÂNCIA", W / 2, H * 0.95, t, 661, None, 18, GREEN)
    vignette(ctx, 0.5, t)


# ------------------------------------------------------------------ 11:06 – 12:20 a reviravolta e o lado do tubarão
def sc_twist(ctx, t):
    ocean(ctx, t)
    if t < 685:
        label(ctx, "O MAR DO RECIFE ESTÁ CHEIO DE TUBARÕES CAÇANDO GENTE?", W / 2, H * 0.12, t, 667, 676, 22, WHITE)
        big_title(ctx, [("NÃO ", RED, "black"), ("ESTÁ.", WHITE, "light")], W / 2, H * 0.12, t, 676, None, 40) \
            if t > 676 else None
        n = 400
        for i in range(n):
            x = W * 0.08 + (i % 40) * (W * 0.84 / 40)
            y = H * 0.26 + (i // 40) * 46
            a = appear(t, 668 + (i / n) * 3)
            col = RED if i in (137, 288) else (0.55, 0.70, 0.75)
            circle(ctx, x, y - 10, 5, col, a)
            rrect(ctx, x - 5, y - 2, 10, 16, 4)
            rgba(ctx, col, a)
            ctx.fill()
        kicker(ctx, "MILHÕES DE PESSOAS ENTRAM NO MAR · INCIDENTES SÃO RAROS (ILUSTRATIVO)", W / 2, H * 0.95, t, 678,
               None, 13, SOFT)
    else:
        items = ["ÁGUA TURVA", "MARÉ CHEIA", "DEPOIS DOS ARRECIFES", "FIM DE TARDE", "FOZ DE RIO"]
        for i, nm in enumerate(items):
            k = appear(t, 691 + i * 0.6)
            gather = appear(t, 699, 1.2)
            ang = i * 2 * math.pi / 5 - math.pi / 2
            x = W / 2 + math.cos(ang) * 260 * (1 - 0.55 * gather)
            y = H * 0.52 + math.sin(ang) * 200 * (1 - 0.55 * gather)
            circle(ctx, x, y, 70, RED, 0.25 * k)
            text(ctx, nm, x, y + 6, 15, WHITE, k, "c", "bold", sp=1)
        label(ctx, "OS MESMOS INGREDIENTES", W / 2, H * 0.10, t, 686, None, 30, ORANGE)
        label(ctx, "O PERIGO ESTÁ CONCENTRADO — E DÁ PARA EVITAR", W / 2, H * 0.94, t, 699.5, None, 22, GREEN)
    vignette(ctx, 0.55, t)


def sc_shark_side(ctx, t):
    if t < 719:
        ocean(ctx, t, rays=False)
        pe_coast(ctx, t, 1, suape=1, mangrove=1 - appear(t, 712, 3))
        label(ctx, "FORAM AS PESSOAS QUE MUDARAM A COSTA", W / 2, H * 0.06 + 20, t, 711.5, None, 22, WHITE)
        kicker(ctx, "PORTOS · OBRAS · MANGUEZAIS ATERRADOS · RIOS POLUÍDOS", W / 2, H * 0.97, t, 714, None, 14, SOFT)
    elif t < 727:
        murky(ctx, t, 0.4)
        for i in range(12):
            x = W * 0.12 + (i % 6) * 190
            y = H * 0.36 + (i // 6) * 170
            k = appear(t, 719.5 + i * 0.12)
            ctx.move_to(x - 30, y + 40)
            ctx.line_to(x + 5, y - 40)
            ctx.line_to(x + 30, y + 40)
            ctx.close_path()
            ink(ctx, (0.40, 0.44, 0.46), k, 2)
        big_title(ctx, [("MILHÕES ", RED, "black"), ("POR ANO", WHITE, "light")], W / 2, H * 0.16, t, 720, None, 44)
        kicker(ctx, "PESCA E COMÉRCIO DE BARBATANAS", W / 2, H * 0.22, t, 721.5, None, 16, WHITE)
        label(ctx, "MUITAS ESPÉCIES ESTÃO DESAPARECENDO", W / 2, H * 0.92, t, 724, None, 22, ORANGE)
    else:
        # dois mundos: rio e mar
        g = cairo.LinearGradient(0, 0, W, 0)
        g.add_color_stop_rgb(0, 0.38, 0.36, 0.22)
        g.add_color_stop_rgb(1, 0.12, 0.30, 0.36)
        ctx.set_source(g)
        ctx.paint()
        sx = W * 0.5 + math.sin(t * 0.25) * W * 0.30
        shark(ctx, sx, H * 0.50, 380, t, "bull", facing=1 if math.cos(t * 0.25) > 0 else -1)
        label(ctx, "RIO", W * 0.15, H * 0.12, t, 728, None, 30, (0.90, 0.85, 0.60))
        label(ctx, "MAR", W * 0.85, H * 0.12, t, 729, None, 30, (0.70, 0.90, 0.95))
        for i in range(3):
            mangrove(ctx, W * 0.06 + i * 90, H * 0.95, 1.1, appear(t, 733))
        label(ctx, "OS FILHOTES NASCEM NOS ESTUÁRIOS QUE A GENTE DESTRÓI", W / 2, H * 0.92, t, 733, 740, 18, WHITE)
        label(ctx, "ELE CAÇA NA ÁGUA TURVA — SEMPRE CAÇOU", W / 2, H * 0.92, t, 740, None, 20, ORANGE)
    vignette(ctx, 0.55, t)


# ------------------------------------------------------------------ 12:20 – 13:04 final
def sc_ending(ctx, t):
    if t < 762.5:
        murky(ctx, t, 1.0, 0.5)
        lvl = 90
        ctx.rectangle(0, 0, W, lvl)
        rgba(ctx, (0.60, 0.60, 0.50))
        ctx.fill()
        surface_line(ctx, t, lvl, sky=False)
        rig.figure(ctx, W * 0.50, lvl + 85, 1.0, rig.p_tread(t), outfit="swimmer", facing=1, ground=False, t=t)
        fog(ctx, 0.35)
        sx = kf(t, [(748, W * 1.2), (762.5, -W * 0.2)], fn=lambda k: k)
        shark(ctx, sx, H * 0.78, 420, t, "bull", facing=-1, silhouette=t > 754, a=0.7)
        label(ctx, "NA ÁGUA MARROM, VOCÊ É SÓ MAIS UMA COISA SE MEXENDO", W / 2, H * 0.94, t, 750, 754.5, 18, WHITE)
        label(ctx, "O PERIGO DE VERDADE É A COMBINAÇÃO", W / 2, H * 0.94, t, 754.5, None, 22, ORANGE)
        vignette(ctx, 0.7, t)
        return
    z = kf(t, [(762.5, 1.0), (770, 2.4)])
    cam(ctx, kf(t, [(762.5, W / 2), (770, W * 0.27)]), kf(t, [(762.5, H / 2), (770, R.DRY - 40)]), z)
    R.scene(ctx, t, tide=1.0, murk=1.0, dusk=0.9, lit=0.8)
    ctx.restore()
    big_title(ctx, [("LEIA A PLACA ", WHITE, "black"), ("AMARELA", YELLOW, "light")], W / 2, H * 0.14, t, 768.5, None,
              48)
    vignette(ctx, 0.4, t)


def sc_endcard(ctx, t):
    ocean(ctx, t)
    text(ctx, "ASSISTA", W * 0.10, H * 0.48, 64, WHITE, appear(t, 773.5), "l", "black")
    text(ctx, "A SEGUIR", W * 0.10, H * 0.58, 64, ORANGE, appear(t, 773.8), "l", "black")
    text(ctx, "mais do fundo do mar", W * 0.10, H * 0.65, 20, SOFT, appear(t, 774.2), "l", "semi")
    k = appear(t, 774.5)
    rrect(ctx, W * 0.52, H * 0.30, W * 0.40, H * 0.40, 12)
    ctx.set_dash([10, 8])
    rgba(ctx, WHITE, 0.6 * k)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.set_dash([])
    shark(ctx, W * 0.20 + math.sin(t * 0.3) * 60, H * 0.84, 160, t, "bull", facing=1, a=0.6)
    vignette(ctx, 0.6, t)


SCENES = [
    (0.0, 36.0, sc_open),
    (36.0, 56.0, sc_enter),
    (56.0, 81.0, sc_reveal),
    (81.0, 90.0, sc_name),
    (90.0, 110.0, sc_promise),
    (110.0, 134.0, sc_anatomy),
    (134.0, 159.0, sc_bite),
    (159.0, 201.0, sc_fresh),
    (201.0, 223.0, sc_rivers),
    (223.0, 256.0, sc_nursery),
    (256.0, 278.0, sc_1916),
    (278.0, 305.0, sc_brazil),
    (305.0, 360.0, sc_why_here),
    (360.0, 371.0, sc_tiger),
    (371.0, 403.0, sc_cemit),
    (403.0, 445.0, sc_why_bite),
    (445.0, 502.0, sc_choice),
    (502.0, 544.0, sc_answers),
    (544.0, 580.0, sc_rules),
    (580.0, 625.0, sc_attack),
    (625.0, 665.0, sc_first_aid),
    (665.0, 705.0, sc_twist),
    (705.0, 748.0, sc_shark_side),
    (748.0, 773.0, sc_ending),
    (773.0, 99999.0, sc_endcard),
]
CUTS = sorted({s for s, _, _ in SCENES if s > 0} | {5.0, 48.0, 64.0, 71.0, 124.0, 127.0, 146.0, 182.0, 209.0, 216.0,
                                                     245.0, 291.0, 325.0, 341.0, 347.0, 379.0, 416.0, 425.0, 484.0,
                                                     516.0, 537.0, 573.0, 603.0, 609.0, 640.0, 647.0, 685.0, 719.0,
                                                     727.0, 762.5})
