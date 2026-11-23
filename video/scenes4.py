"""Revisão 4: abertura dinâmica, tentáculos que realmente tocam as pernas, sequência de ícones sem sobreposição,
cartão 'o que fazer' centralizado, cnidócito redesenhado (estilo ilustração científica)."""
import math

import scenes as S
import scenes2 as S2
import scenes3 as S3
import rig
import beach as B
from gfx import *  # noqa: F401,F403
from mapdata import *  # noqa: F401,F403


def cam(ctx, cx, cy, z):
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)


# ------------------------------------------------------------------ 00:00 – 00:07 zoom do globo até Queensland
def big_globe(ctx, t, x, y, r, lon0, lat0, a=1.0, hl=None, label_txt=None):
    lam0, ph0 = math.radians(lon0), math.radians(lat0)

    def proj(lon, lat):
        lam, ph = math.radians(lon), math.radians(lat)
        cosc = math.sin(ph0) * math.sin(ph) + math.cos(ph0) * math.cos(ph) * math.cos(lam - lam0)
        px = r * math.cos(ph) * math.sin(lam - lam0)
        py = r * (math.cos(ph0) * math.sin(ph) - math.sin(ph0) * math.cos(ph) * math.cos(lam - lam0))
        return x + px, y - py, cosc

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
    # atmosfera
    ctx.new_sub_path()
    ctx.arc(x, y, r + 4, 0, 2 * math.pi)
    rgba(ctx, (0.6, 0.85, 0.9), 0.25 * a)
    ctx.set_line_width(6)
    ctx.stroke()


def gull(ctx, x, y, s, t, ph=0.0):
    f = math.sin(t * 6 + ph) * 0.6
    ctx.move_to(x - 14 * s, y - 4 * s * f)
    ctx.curve_to(x - 8 * s, y - 8 * s, x - 3 * s, y - 2 * s, x, y)
    ctx.curve_to(x + 3 * s, y - 2 * s, x + 8 * s, y - 8 * s, x + 14 * s, y - 4 * s * f)
    rgba(ctx, (0.2, 0.22, 0.26), 0.8)
    ctx.set_line_width(2)
    ctx.stroke()


def thermometer(ctx, x, y, k, a):
    if a <= 0:
        return
    rrect(ctx, x - 9, y - 120, 18, 120, 9)
    ink(ctx, WHITE, a, 2.5)
    ctx.new_sub_path()
    ctx.arc(x, y + 6, 17, 0, 2 * math.pi)
    ink(ctx, RED, a, 2.5)
    rrect(ctx, x - 4, y - 112 * k, 8, 112 * k + 4, 4)
    rgba(ctx, RED, a)
    ctx.fill()
    text(ctx, f"{int(18 + 13 * k)}°C", x + 30, y - 50, 40, WHITE, a, "l", "black")


def sc_intro(ctx, t):
    if t < 6.5:
        # espaço -> globo girando e aproximando a Austrália
        rgba(ctx, (0.02, 0.04, 0.07))
        ctx.paint()
        for i in range(120):
            circle(ctx, (i * 211) % W, (i * 97) % H, 1.0 + (i % 3) * 0.4, WHITE, 0.4 + 0.3 * math.sin(t + i))
        k = ease(t / 6.5)
        r = lerp(170, 1500, k ** 2.2)
        lon = lerp(60, 146, ease(min(1, t / 4)))
        lat = lerp(5, -18, ease(min(1, t / 4.5)))
        big_globe(ctx, t, W / 2, H / 2 + lerp(0, 120, k), r, lon, lat, 1.0, hl=(145.8, -16.9),
                  label_txt="NORTE DE QUEENSLAND" if t > 3 else None)
        kicker(ctx, "AUSTRÁLIA · DEZEMBRO · FIM DE TARDE", W / 2, H * 0.92, t, 1.0, 6.2, 18, WHITE)
        if t > 5.9:
            rgba(ctx, WHITE, (t - 5.9) / 0.6 * 0.6)
            ctx.paint()
        return
    # praia frontal com câmera se aproximando, gaivotas e termômetro
    z = lerp(1.0, 1.15, ease((t - 6.5) / 6.5))
    ctx.save()
    ctx.translate(W / 2, H * 0.55)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -H * 0.55)
    sky_beach(ctx, t, cam=(t - 6.5) * 6)
    post_bottle(ctx, W * 0.30 - (t - 6.5) * 3 + 40, H * 0.86, 1.0)
    for i in range(4):
        gull(ctx, (W * 0.2 + i * 70 + t * 40) % (W + 200) - 100, H * (0.18 + 0.03 * (i % 2)), 1.0, t, i)
    ctx.restore()
    thermometer(ctx, W * 0.86, H * 0.42, appear(t, 9.6, 2.5), window(t, 9.4, 13.0))
    if t < 7.0:
        rgba(ctx, WHITE, 0.6 * (1 - (t - 6.5) / 0.5))
        ctx.paint()
    vignette(ctx, 0.35, t)


def sc_feet(ctx, t):
    """00:13 – 00:16 – água tão transparente que dá para ver os pés."""
    ocean(ctx, t, top=(0.45, 0.80, 0.82), bot=(0.30, 0.66, 0.68), distant=False, particles=False)
    # cáusticas de luz no fundo
    for i in range(40):
        x = (i * 83 + math.sin(t * 1.3 + i) * 12) % W
        y = H * 0.70 + (i * 37) % int(H * 0.3)
        ellipse_path(ctx, x, y, 26 + 8 * math.sin(t * 2 + i), 7)
        rgba(ctx, WHITE, 0.10)
        ctx.set_line_width(2)
        ctx.stroke()
    ctx.rectangle(0, H * 0.74, W, H)
    rgba(ctx, (0.90, 0.84, 0.66), 0.85)
    ctx.fill()
    surface_line(ctx, t, 70, sky=False)
    # pés dando passos
    for side, ph in ((-1, 0.0), (1, math.pi)):
        step = max(0, math.sin(t * 2.2 + ph))
        x = W * 0.5 + side * 70 + math.sin(t * 2.2 + ph) * 30
        y = H * 0.76 - step * 25
        limb(ctx, [(x - 10, 0), (x - 10, y - 30)], 34, SKIN)
        ellipse_path(ctx, x + 18, y, 46, 17)
        ink(ctx, SKIN, 1, 2.5)
    for i in range(5):
        fish(ctx, (W * 0.2 + i * 160 + t * 30 * (1 if i % 2 else -1)) % W, H * (0.45 + 0.05 * i), 0.4, t + i,
             c=(0.85, 0.85, 0.7), flip=1 if i % 2 else -1)
    vignette(ctx, 0.4, t)


def sc_open4(ctx, t):
    if t < 13:
        return sc_intro(ctx, t)
    if t < 16.2:
        return sc_feet(ctx, t)
    if t < 27:
        # entra até a cintura e depois a câmera abre mostrando o mar vazio
        z = kf(t, [(16.2, 1.25), (21.5, 1.25), (26, 1.0)])
        cx = kf(t, [(16.2, W * 0.45), (21.5, W * 0.60), (26, W / 2)])
        cam(ctx, cx, H * 0.55, z)
        S3.sc_enter(ctx, t)
        ctx.restore()
        if t > 22:
            kicker(ctx, "NENHUMA PESSOA NA ÁGUA", W / 2, H * 0.16, t, 22.3, 27, 20, (0.15, 0.2, 0.25))
        return
    return S2.sc_open(ctx, t)


# ------------------------------------------------------------------ 00:37 – 01:02 a queimadura (tentáculos tocam as pernas)
SURF_Y = 150.0


def swim_state(t):
    if t < 52:
        sx = kf(t, [(37, W * 0.36), (43, W * 0.50), (52, W * 0.54)])
        facing = 1
        p = rig.p_swim(t, 1.0 if t < 43 else 0.5)
    else:
        sx = kf(t, [(52, W * 0.54), (57.5, W * 0.42), (62, W * 0.41)])
        facing = -1
        sp = kf(t, [(52, 1.4), (56, 1.0), (57.5, 0.0)])
        p = rig.p_swim(t, max(sp, 0.01))
        if t > 57.5:
            sink = appear(t, 57.5, 3)
            limp = rig.p_float_limp(t)
            p = rig.blend(p, limp, sink)
    sy = SURF_Y + 12 + kf(t, [(57.5, 0), (62, 28)])
    return sx, sy, facing, p


def leg_points(pts, n=6):
    """Pontos ao longo das duas pernas (coxa e canela)."""
    out = []
    for side in ("F", "B"):
        a, b, c = pts["hip"], pts["knee" + side], pts["ankle" + side]
        for i in range(n):
            f = (i + 1) / (n + 1)
            if f < 0.45:
                q = f / 0.45
                out.append((lerp(a[0], b[0], q), lerp(a[1], b[1], q)))
            else:
                q = (f - 0.45) / 0.55
                out.append((lerp(b[0], c[0], q), lerp(b[1], c[1], q)))
    return out


def sc_sting4(ctx, t):
    ocean(ctx, t, top=(0.18, 0.52, 0.58), bot=(0.05, 0.20, 0.26), distant=False)
    sx, sy, facing, p = swim_state(t)
    scale = 0.95
    pts = rig.world_points(sx, sy, scale, p, facing, ground=False)
    legs_c = ((pts["kneeF"][0] + pts["hip"][0]) / 2, (pts["kneeF"][1] + pts["hip"][1]) / 2)
    cx = kf(t, [(37, W / 2), (44.5, W / 2), (46.5, legs_c[0]), (51, legs_c[0]), (52.5, W / 2)])
    cy = kf(t, [(37, H / 2), (44.5, H / 2), (46.5, legs_c[1] + 30), (51, legs_c[1] + 30), (52.5, H / 2)])
    z = kf(t, [(44.5, 1.0), (46.5, 2.4), (51, 2.4), (52.5, 1.0)])
    cam(ctx, cx, cy, z)
    ctx.rectangle(-600, -800, W * 3, 800 + SURF_Y)
    rgba(ctx, (0.82, 0.89, 0.90))
    ctx.fill()
    surface_line(ctx, t, SURF_Y, sky=False)
    S2._shore(ctx)
    # água-viva: sobe até ficar logo abaixo das pernas, encosta, depois afunda e se afasta
    lp_ = leg_points(pts)
    contact = window(t, 38.6, 45.0, 0.8)
    target = (legs_c[0] + 10, legs_c[1] + 75)
    jx = kf(t, [(37, W * 0.66), (38.8, target[0]), (45, target[0] + 10), (52, W * 0.70), (62, W * 0.78)])
    jy = kf(t, [(37, H * 0.80), (38.8, target[1]), (45, target[1] + 10), (52, H * 0.55), (62, H * 0.62)])
    if 38.0 < t < 45.5:
        jx, jy = lerp(jx, target[0], contact), lerp(jy, target[1], contact)
    box_jelly(ctx, jx, jy, 0.62, t, a=0.9, glow=0.5, tent=0.6 if contact > 0.3 else 1.0)
    # tentáculos esticados que agarram as pernas
    if contact > 0:
        base = [(jx + (i - 5.5) * 6, jy + 30) for i in range(12)]
        for i, (bx, by) in enumerate(base):
            ex, ey = lp_[i % len(lp_)]
            mx, my = (bx + ex) / 2 + math.sin(t * 2 + i) * 10, (by + ey) / 2 + 22
            ctx.move_to(bx, by)
            ctx.curve_to(mx, my + 10, lerp(mx, ex, 0.5), ey + 18, lerp(bx, ex, contact), lerp(by, ey, contact))
            rgba(ctx, JELLY, 0.85 * contact)
            ctx.set_line_width(1.4)
            ctx.stroke()
    rig.figure(ctx, sx, sy, scale, p, outfit="swimmer", facing=facing, ground=False, t=t)
    # vergões vermelhos exatamente onde os tentáculos tocaram
    k = appear(t, 43, 2.5)
    if k > 0:
        for i, (ex, ey) in enumerate(lp_):
            L = 7 * k
            line(ctx, ex - L, ey - 3, ex + L, ey + 3, RED, 0.9, 2.2)
    if t > 57.5:
        hp = pts["head"]
        bubbles(ctx, hp[0], hp[1] - 6, t, n=8, rise=50, a=appear(t, 57.5))
    ctx.restore()
    if 43 <= t < 44.4:
        rgba(ctx, (1, 0.92, 0.88), 0.55 * (1 - (t - 43) / 1.4))
        ctx.paint()
    if 43 <= t < 50:
        rgba(ctx, RED, 0.16 * (1 - appear(t, 47, 3)) * (0.6 + 0.4 * math.sin(t * 7)))
        ctx.paint()
    callout(ctx, *(_cam_pt(legs_c, cx, cy, z)), 60 * z / 2.4 if z > 1.1 else 30, W * 0.22, H * 0.20,
            "LINHAS VERMELHAS", window(t, 47.2, 51.5))
    k2 = window(t, 52.5, 62)
    if k2 > 0:
        d = kf(t, [(52.5, 10), (55.5, 10), (57.5, 5)])
        x0 = W * 0.17
        x1 = sx - 120
        line(ctx, x0, SURF_Y - 22, x1, SURF_Y - 22, YELLOW, k2, 2)
        line(ctx, x0, SURF_Y - 30, x0, SURF_Y - 14, YELLOW, k2, 2)
        line(ctx, x1, SURF_Y - 30, x1, SURF_Y - 14, YELLOW, k2, 2)
        text(ctx, f"{d:.0f} M ATÉ A AREIA", (x0 + x1) / 2, SURF_Y - 36, 20, (0.1, 0.15, 0.2), k2, "c", "black", sp=1)
    if t > 58:
        rgba(ctx, (0, 0, 0), 0.55 * appear(t, 58, 4))
        ctx.paint()
    vignette(ctx, 0.5, t)


def _cam_pt(p, cx, cy, z):
    return (W / 2 + (p[0] - cx) * z, H / 2 + (p[1] - cy) * z)


# ------------------------------------------------------------------ 01:02 – 01:40 sem cérebro / 95% água / 70 mortes
def sc_nobrain4(ctx, t):
    if t >= 81:
        return S.sc_nobrain(ctx, t)
    ocean(ctx, t)
    # água-viva sobe para a parte de cima, deixando espaço para os gráficos embaixo
    jy = kf(t, [(62, H * 0.32), (64.5, H * 0.16)])
    box_jelly(ctx, W / 2, jy, 1.15, t, glow=1, tent=0.75)
    # 1) quatro ícones riscados (64.5 – 71)
    kinds = ["brain", "bone", "heart", "drop"]
    names = ["CÉREBRO", "OSSOS", "CORAÇÃO", "SANGUE"]
    cues = [65.0, 66.5, 67.8, 69.0]
    for i, (kd, nm, c0) in enumerate(zip(kinds, names, cues)):
        a = window(t, c0, 71.0)
        x = W / 2 + (i - 1.5) * 180
        y = H * 0.74 + (1 - appear(t, c0, 0.4)) * 20
        icon(ctx, kd, x, y, 0.95, a)
        text(ctx, nm, x, y + 62, 16, WHITE, a, "c", "semi", sp=2.5)
        xmark(ctx, x, y, 38, appear(t, c0 + 0.45, 0.5) * a)
    # 2) 95% água — o sino se enche de água (71 – 73.4)
    k = window(t, 71.2, 73.4, 0.3)
    if k > 0:
        lvl = appear(t, 71.2, 1.4) * 0.95
        bx, by, bw, bh = W / 2 - 70, H * 0.60, 140, 150
        rrect(ctx, bx, by, bw, bh, 22)
        rgba(ctx, WHITE, 0.08 * k)
        ctx.fill_preserve()
        rgba(ctx, JELLY, 0.7 * k)
        ctx.set_line_width(2)
        ctx.stroke()
        ctx.save()
        rrect(ctx, bx, by, bw, bh, 22)
        ctx.clip()
        yy = by + bh * (1 - lvl)
        ctx.move_to(bx, yy)
        for xx in range(int(bx), int(bx + bw) + 6, 6):
            ctx.line_to(xx, yy + math.sin(xx * 0.1 + t * 4) * 2)
        ctx.line_to(bx + bw, by + bh)
        ctx.line_to(bx, by + bh)
        ctx.close_path()
        rgba(ctx, (0.35, 0.70, 0.85), 0.8 * k)
        ctx.fill()
        ctx.restore()
        text(ctx, f"{int(round(lvl * 100))}%", W / 2 + 120, H * 0.74, 64, ORANGE, k, "l", "black")
        text(ctx, "ÁGUA", W / 2 + 120, H * 0.80, 26, WHITE, k, "l", "bold", sp=3)
    # 3) ~70 mortes: matriz de ícones de pessoas (73.6 – 81)
    k = window(t, 73.6, 81.0, 0.35)
    if k > 0:
        n = int(clamp((t - 73.8) / 2.6) * 70)
        cols = 14
        for i in range(70):
            x = W / 2 + (i % cols - (cols - 1) / 2) * 34
            y = H * 0.62 + (i // cols) * 46
            col = RED if i < n else (0.35, 0.45, 0.5)
            circle(ctx, x, y - 13, 6, col, k)
            rrect(ctx, x - 6, y - 5, 12, 20, 5)
            rgba(ctx, col, k)
            ctx.fill()
        big_title(ctx, [("~70 ", ORANGE, "black"), ("MORTES NA AUSTRÁLIA", WHITE, "bold")], W / 2, H * 0.56, t, 73.8,
                  81.0, 34)
        kicker(ctx, "DESDE QUE OS REGISTROS COMEÇARAM", W / 2, H * 0.97, t, 76, 81, 15, SOFT)
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 01:40 – 02:02 cartões da promessa (ícones centralizados)
def first_aid_icon(ctx, x, y, s, a, t):
    """Cena em miniatura: vítima deitada e socorrista ajoelhado — centralizada no cartão."""
    gy = y + 40 * s
    line(ctx, x - 70 * s, gy, x + 70 * s, gy, SOFT, a * 0.5, 1.5)
    rig.figure(ctx, x + 8 * s, gy, 0.55 * s, rig.p_lie(0), outfit="friend", facing=-1, a=a, shadow=False)
    p = rig.p_cpr(t)
    hx, hy = rig.hand_point(0, gy, 0.55 * s, p, facing=1)
    rig.figure(ctx, x + 22 * s - hx, gy, 0.55 * s, p, outfit="swimmer", facing=1, a=a, shadow=False)


def sc_promise4(ctx, t):
    ocean(ctx, t)
    items = [("bottle", "A GARRAFA", 100.5), ("stocking", "A MEIA-CALÇA", 105.0), ("eye", "24 OLHOS", 109.0),
             ("aid", "O QUE FAZER", 112.0)]
    for i, (kd, nm, c0) in enumerate(items):
        a = window(t, c0, 116.5)
        if a <= 0:
            continue
        x = W / 2 + (i - 1.5) * 270
        y0 = H * 0.30 + (1 - appear(t, c0, 0.5)) * 25
        card(ctx, x - 115, y0, 230, 230, a)
        if kd == "aid":
            first_aid_icon(ctx, x, y0 + 80, 1.45, a, t)
        else:
            icon(ctx, kd, x, y0 + 100, 1.5, a)
        text(ctx, nm, x, y0 + 200, 20, ORANGE, a, "c", "bold", sp=2)
    kicker(ctx, "POR QUE VOCÊ NUNCA IA QUERER ENCONTRAR UMA", W / 2, H * 0.40, t, 117, None, 20)
    big_title(ctx, [("ÁGUA-VIVA-", WHITE, "black"), ("CAIXA", ORANGE, "light")], W / 2, H * 0.40 + 75, t, 117.4,
              None, 72)
    if t > 117:
        box_jelly(ctx, W / 2, H * 0.68, 0.7, t, a=appear(t, 117.5))
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 02:43 – 03:11 o cnidócito (ilustração científica)
def nematocyst(ctx, cx, cy, s, t, fire_t, a=1.0):
    """Cápsula vertical com opérculo, cnidocílio (gatilho) e túbulo em hélice; dispara para cima."""
    fire = clamp((t - fire_t) / 0.18) if t >= fire_t else 0.0
    w, h = 70 * s, 120 * s
    # cápsula (parede dupla)
    for rr, al in ((1.0, 0.35), (0.86, 0.18)):
        ellipse_path(ctx, cx, cy, w * rr, h * rr)
        rgba(ctx, JELLY, al * a)
        ctx.fill_preserve()
        rgba(ctx, JELLY, 0.95 * a)
        ctx.set_line_width(2.2)
        ctx.stroke()
    top = cy - h
    # opérculo (tampa) — abre ao disparar
    ctx.save()
    ctx.translate(cx - 22 * s, top + 4)
    ctx.rotate(-1.9 * ease(fire))
    ellipse_path(ctx, 22 * s, 0, 22 * s, 7 * s)
    ink(ctx, (0.80, 0.90, 0.95), a, 2)
    ctx.restore()
    # cnidocílio (o gatilho): pelinho rígido ao lado da tampa
    line(ctx, cx + 30 * s, top + 14 * s, cx + 46 * s, top - 34 * s, (0.95, 0.92, 0.80), a, 3)
    # túbulo enrolado em hélice dentro da cápsula (antes do disparo)
    if fire < 1:
        aa = a * (1 - fire)
        turns = 11
        for i in range(turns):
            yy = cy + h * 0.65 - i * (h * 1.3 / turns)
            ellipse_path(ctx, cx, yy, w * 0.52, 7 * s)
            rgba(ctx, (0.96, 0.96, 0.92), 0.85 * aa)
            ctx.set_line_width(2.2)
            ctx.stroke()
        # haste central (eixo com espinhos dobrados)
        line(ctx, cx, cy + h * 0.6, cx, cy - h * 0.55, (0.96, 0.96, 0.92), 0.6 * aa, 2)
    # túbulo disparado: sai pela abertura, reto, com espinhos na base
    if fire > 0:
        L = 480 * s * ease(fire)
        line(ctx, cx, top, cx, top - L, (0.96, 0.96, 0.92), a, 3)
        for j in range(5):
            yb = top - 18 * s - j * 14 * s
            if top - yb < L:
                line(ctx, cx, yb, cx - 13 * s, yb + 12 * s, (0.96, 0.96, 0.92), a, 2)
                line(ctx, cx, yb, cx + 13 * s, yb + 12 * s, (0.96, 0.96, 0.92), a, 2)
        # veneno descendo pelo túbulo
        for j in range(8):
            ph = ((t - fire_t) * 1.4 + j / 8) % 1
            circle(ctx, cx, top - L * ph, 4 * s, (0.55, 0.85, 0.40), a * (1 - ph) * appear(t, fire_t + 0.3, 0.4))


def sc_cnido4(ctx, t):
    ocean(ctx, t, top=(0.06, 0.15, 0.2))
    if t < 166.5:
        # tentáculo ampliado coberto de cápsulas ("milhões delas")
        z = kf(t, [(163, 1.0), (166.5, 2.6)])
        cam(ctx, W * 0.55, H * 0.55, z)
        ctx.move_to(-100, H * 0.48)
        ctx.curve_to(W * 0.3, H * 0.42, W * 0.7, H * 0.66, W + 100, H * 0.58)
        rgba(ctx, (0.85, 0.55, 0.60), 0.5)
        ctx.set_line_width(110)
        ctx.stroke()
        rnd = random.Random(4)
        for i in range(260):
            u = rnd.random()
            x = -100 + u * (W + 200)
            yc = (H * 0.48 * (1 - u) ** 3 + 3 * (1 - u) ** 2 * u * H * 0.42 + 3 * (1 - u) * u * u * H * 0.66
                  + u ** 3 * H * 0.58)
            y = yc + rnd.uniform(-45, 45)
            ellipse_path(ctx, x, y, 5, 8, rnd.uniform(-0.5, 0.5))
            rgba(ctx, JELLY, 0.85)
            ctx.fill()
        ctx.restore()
        label(ctx, "CÉLULAS URTICANTES", W / 2, 70, t, 163.3, None, 36, ORANGE)
        kicker(ctx, "MILHÕES DELAS EM CADA TENTÁCULO", W / 2, 108, t, 165.0, None, 17)
        vignette(ctx, 0.6, t)
        return
    cx, cy = W * 0.5, H * 0.70
    # pele aparece acima quando o túbulo vai perfurar
    ks = appear(t, 187.5)
    if ks > 0:
        ctx.rectangle(0, 0, W, H * 0.18)
        rgba(ctx, SKIN, ks)
        ctx.fill()
        ctx.rectangle(0, H * 0.18 - 10, W, 10)
        rgba(ctx, (0.80, 0.55, 0.45), ks)
        ctx.fill()
        text(ctx, "PELE", W * 0.08, H * 0.10, 22, (0.4, 0.2, 0.1), ks, "l", "black", sp=2)
    nematocyst(ctx, cx, cy, 1.0, t, 174.0)
    label(ctx, "CÉLULAS URTICANTES", W / 2, 70, t, 163.3, 174, 36, ORANGE)
    callout(ctx, cx + 46, cy - 120 - 34, 16, cx + 210, cy - 210, "GATILHO", window(t, 171.3, 176))
    callout(ctx, cx, cy, 55, cx - 230, cy - 150, "ARPÃO ENROLADO", window(t, 166.8, 171.3))
    callout(ctx, cx - 10, cy - 116, 18, cx - 230, cy - 210, "TAMPA", window(t, 168.5, 173.5))
    if 174 <= t < 175.2:
        rgba(ctx, WHITE, 0.35 * (1 - (t - 174) / 1.2))
        ctx.paint()
    big_title(ctx, [("< 1 MILIONÉSIMO ", ORANGE, "black"), ("DE SEGUNDO", WHITE, "light")], W * 0.70, H * 0.42, t,
              177.5, 187.5, 34)
    kicker(ctx, "UM DOS MOVIMENTOS MAIS RÁPIDOS DA BIOLOGIA", W * 0.70, H * 0.48, t, 178.5, 187.5, 14)
    label(ctx, "PERFURA A PELE E INJETA O VENENO", W / 2, H * 0.96, t, 188, None, 22, WHITE)
    vignette(ctx, 0.6, t)


REPLACE = {
    "sc_open3": sc_open4,
    "sc_sting2": sc_sting4,
    "sc_nobrain": sc_nobrain4,
    "sc_promise": sc_promise4,
    "sc_cnido": sc_cnido4,
}
SCENES = [(s, e, REPLACE.get(fn.__name__, fn)) for s, e, fn in S3.SCENES]
CUTS = sorted(set(S3.CUTS) | {6.5, 16.2, 166.5})


# ------------------------------------------------------------------ 01:29 – 01:40 a Irukandji ao lado de uma mão de verdade
def hand_from_bottom(ctx, tipx, tipy, s, a):
    """Antebraço entrando pela borda de baixo, mão fechada com o indicador apontando para cima."""
    wx, wy = tipx + 40 * s, tipy + 150 * s
    limb(ctx, [(tipx + 90 * s, H + 40), (wx, wy)], 60 * s, SKIN, a)
    ellipse_path(ctx, wx - 8 * s, wy - 18 * s, 44 * s, 38 * s)
    ink(ctx, SKIN, a, 2.5)
    limb(ctx, [(tipx + 4 * s, wy - 40 * s), (tipx, tipy + 10 * s)], 22 * s, SKIN, a)
    rrect(ctx, tipx - 8 * s, tipy + 2 * s, 16 * s, 20 * s, 6 * s)
    ink(ctx, (0.97, 0.86, 0.82), a, 1.5)


def sc_nobrain4b(ctx, t):
    if t < 89:
        return sc_nobrain4(ctx, t)
    ocean(ctx, t)
    sh = ease((t - 89) / 2)
    box_jelly(ctx, W / 2 - sh * 250, H * 0.30, 1.4 - sh * 0.3, t, glow=1)
    name_tag(ctx, "Chironex fleckeri", 40, 60, t, 81.5, None, 30)
    k = appear(t, 91)
    if k > 0:
        tx, ty = W * 0.76, H * 0.44
        hand_from_bottom(ctx, tx, ty, 1.0, k)
        iruk(ctx, tx - 50, ty - 10, 0.75, t, k)
        scale_bar(ctx, tx - 62, tx - 38, ty - 45, (t - 92) / 0.6, "~1 CM")
        label(ctx, "DO TAMANHO DE UMA UNHA", W * 0.70, H * 0.12, t, 93.5, None, 24, ORANGE)
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 03:11 – 03:31 a presa presa no tentáculo
def sc_why4(ctx, t):
    ocean(ctx, t)
    ctx.rectangle(0, 0, W, 130)
    rgba(ctx, (0.80, 0.88, 0.90))
    ctx.fill()
    surface_line(ctx, t, 130, sky=False)
    label(ctx, "POR QUE TÃO FORTE?", W / 2, 190, t, 191.3, 196, 36, ORANGE)
    jx, jy = W * 0.30, H * 0.32
    box_jelly(ctx, jx, jy, 1.0, t, glow=0.4)
    # camarão e peixe enroscados nas pontas dos tentáculos
    sx, sy = jx - 55, H * 0.70
    shrimp(ctx, sx, sy, 1.1, appear(t, 195))
    struggle = appear(t, 199.5) * (1 - appear(t, 204, 0.4))
    fx, fy = jx + 50, H * 0.74
    fish(ctx, fx, fy, 1.3, t, wiggle=0.45 * struggle, a=appear(t, 196))
    for i in range(4):
        a = appear(t, 196)
        line(ctx, fx - 40 + i * 18, fy - 32, fx - 30 + i * 18, fy + 30, JELLY, 0.9 * a, 1.6)
        line(ctx, sx - 30 + i * 14, sy - 26, sx - 24 + i * 14, sy + 20, JELLY, 0.9 * appear(t, 195), 1.4)
    label(ctx, "PRECISA PARAR A PRESA NA HORA", W * 0.33, H * 0.92, t, 204, None, 24, ORANGE)
    # nós: um banhista boiando na superfície, pernas na água
    k = appear(t, 207, 1.2)
    if k > 0:
        rig.figure(ctx, W * 0.76, 196, 1.25, rig.p_tread(t), outfit="swimmer", facing=-1, a=k, ground=False, t=t)
        ctx.rectangle(0, 131, W, H)
        rgba(ctx, (0.10, 0.32, 0.38), 0.30 * k)
        ctx.fill()
        surface_line(ctx, t, 130, sky=False)
        text(ctx, "NÓS: SÓ UM BICHO GRANDE NA MESMA ÁGUA", W * 0.72, H * 0.62, 18, WHITE, k, "c", "bold", sp=1.5)
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 12:18 – 12:46 vinagre derramado sobre a perna, com tentáculos
def sc_vinegar4(ctx, t):
    if t >= 766:
        return S.sc_vinegar(ctx, t)
    studio(ctx, t, H * 0.86)
    # perna (deitada) em close: coxa à esquerda, pé à direita
    y = H * 0.74
    limb(ctx, [(-60, y - 20), (W * 0.30, y - 6), (W * 0.56, y + 4)], 90, SKIN)
    ellipse_path(ctx, W * 0.60, y - 4, 50, 30, -0.6)
    ink(ctx, SKIN, 1, 2.5)
    rrect(ctx, -60, y - 75, 200, 110, 20)
    ink(ctx, (0.20, 0.24, 0.30), 1, 2.5)  # calção
    # fluxo de vinagre avançando ao longo da perna
    pour_x = kf(t, [(739.5, W * 0.12), (746, W * 0.55)])
    for i, x0 in enumerate([W * (0.14 + j * 0.09) for j in range(5)]):
        ctx.move_to(x0, y - 40)
        ctx.curve_to(x0 + 30, y - 10, x0 - 20, y + 15, x0 + 15, y + 42)
        rgba(ctx, JELLY, 0.95)
        ctx.set_line_width(2)
        ctx.stroke()
        line(ctx, x0 - 6, y - 38, x0 + 20, y + 40, RED, 0.55, 5)
        for j in range(6):
            cx_ = x0 + 4 + j * 2.5 + math.sin(j) * 8
            cy_ = y - 32 + j * 13
            off = pour_x > x0 and t > 739.5
            circle(ctx, cx_, cy_, 4.5, (0.6, 0.65, 0.68) if off else YELLOW, 1)
            if not off:
                circle(ctx, cx_, cy_, 8, YELLOW, 0.25 * (0.5 + 0.5 * math.sin(t * 6 + j)))
    # garrafa inclinada, seguindo o fluxo
    bx = pour_x + 30
    ctx.save()
    ctx.translate(bx, H * 0.36)
    ctx.rotate(2.2 * appear(t, 738.5, 1.0))
    icon(ctx, "bottle", 0, 0, 2.2, 1)
    ctx.restore()
    pour = appear(t, 739.5)
    if pour > 0:
        ctx.move_to(bx - 40, H * 0.38)
        ctx.curve_to(bx - 46, H * 0.48, bx - 40, H * 0.58, bx - 38, y - 44)
        rgba(ctx, (0.95, 0.92, 0.75), 0.75 * pour)
        ctx.set_line_width(6)
        ctx.stroke()
    callout(ctx, W * 0.32 + 6, y - 20, 22, W * 0.24, H * 0.20, "CÉLULAS AINDA ARMADAS", window(t, 738.6, 744))
    big_title(ctx, [("VINAGRE · ", ORANGE, "black"), ("30 SEGUNDOS", WHITE, "light")], W * 0.78, H * 0.24, t, 741.5,
              None, 34)
    kicker(ctx, "DESARMA AS CÉLULAS QUE AINDA NÃO DISPARARAM", W * 0.78, H * 0.31, t, 747, None, 13, WHITE)
    label(ctx, "SEM VINAGRE? ÁGUA DO MAR", W * 0.78, H * 0.42, t, 754, None, 22, GREEN)
    label(ctx, "NUNCA ÁGUA DOCE", W * 0.78, H * 0.48, t, 757, None, 22, RED)
    label(ctx, "XIXI NÃO AJUDA", W * 0.78, H * 0.54, t, 759.5, None, 20, SOFT)
    vignette(ctx, 0.5, t)


REPLACE.update({"sc_nobrain": sc_nobrain4b, "sc_why": sc_why4, "sc_vinegar": sc_vinegar4})
SCENES = [(s, e, REPLACE.get(fn.__name__, fn)) for s, e, fn in S3.SCENES]
CUTS = sorted(set(S3.CUTS) | {6.5, 16.2, 166.5, 575.0})
