"""Cenas reconstruídas na linguagem de animação do canal de referência:
câmera que acompanha a ação, personagens em movimento, rótulos presos aos objetos, globo localizador."""
import math

import scenes as S
from gfx import *  # noqa: F401,F403
from mapdata import *  # noqa: F401,F403


def cam_begin(ctx, cx, cy, z):
    """Câmera: (cx, cy) é o ponto do mundo que fica no centro da tela, z é o zoom."""
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)


def cam_end(ctx):
    ctx.restore()


# ------------------------------------------------------------------ 00:00 – 00:37 abertura na praia
def sc_open(ctx, t):
    zoom = 1 + 0.55 * ease((t - 27) / 6)
    cam = min(t, 27) * 2.2

    def mid(c):
        if 13 <= t < 23:
            p = clamp((t - 13) / 7)
            x = W * 0.50 + p * W * 0.10 - cam * 0.5
            fy = lerp(H * 0.695, H * 0.665, p)
            wade(c, x, fy, 0.48, 0.15 + 0.40 * p, t, outfit="swim", pose="walk" if p < 1 else "stand",
                 arm=lerp(10, 40, p))
        elif t >= 23:
            p = clamp((t - 23) / 14)
            x = W * 0.62 + p * W * 0.10 - cam * 0.5
            swimmer(c, x, H * 0.635, 0.32, t, outfit="swim", facing=1)
            ctx.move_to(x - 60, H * 0.64)
            ctx.line_to(x + 50, H * 0.64)
            rgba(c, sea_color(H * 0.64), 0.6)
            c.set_line_width(5)
            c.stroke()

    ctx.save()
    px, py = W * 0.30, H * 0.80
    ctx.translate(px, py)
    ctx.scale(zoom, zoom)
    ctx.translate(-px, -py)
    sky_beach(ctx, t, cam=cam, mid=mid)
    post_bottle(ctx, W * 0.30 - cam * 0.5 + 40, H * 0.86, 1.0, glow=appear(t, 29, 1.5))
    ctx.restore()
    globe(ctx, 95, 105, 46, window(t, 2.5, 11.5), lon0=140, lat0=-18, hl=(145.8, -16.9), name="NORTE DE QUEENSLAND")
    callout(ctx, W * 0.30 - cam * 0.5 + 40 - 10, H * 0.86 - 190 * 1.0, 40, W * 0.12, H * 0.22, "UMA GARRAFA",
            window(t, 30.5, 36.5))
    vignette(ctx, 0.35, t)


# ------------------------------------------------------------------ 00:37 – 01:02 a queimadura
def _shore(ctx):
    ctx.move_to(-400, 120)
    ctx.line_to(W * 0.18, 125)
    ctx.curve_to(W * 0.35, H * 0.45, W * 0.55, H * 0.80, W * 1.1, H * 0.86)
    ctx.line_to(W * 2.2, H * 0.90)
    ctx.line_to(W * 2.2, H * 2)
    ctx.line_to(-400, H * 2)
    ctx.close_path()
    ink(ctx, (0.78, 0.71, 0.55), 1, 2.5)
    rnd = random.Random(4)
    for i in range(30):
        x = rnd.uniform(W * 0.3, W * 2)
        circle(ctx, x, H * 0.88 + rnd.uniform(0, 60), rnd.uniform(2, 5), (0.62, 0.56, 0.42), 0.7)


def sc_sting2(ctx, t):
    # céu + água
    ocean(ctx, t, top=(0.18, 0.52, 0.58), bot=(0.05, 0.20, 0.26), distant=False)
    # trajetória do nadador
    if t < 52:
        sx = kf(t, [(37, W * 0.40), (43, W * 0.55), (52, W * 0.58)])
        facing = 1
        speed = 1.0 if t < 43 else 0.5
    else:
        sx = kf(t, [(52, W * 0.58), (58, W * 0.46), (62, W * 0.44)])
        facing = -1
        speed = kf(t, [(52, 1.4), (56, 1.0), (58.5, 0.0)])
    sy = 152 + kf(t, [(58, 0), (62, 40)])
    tilt = kf(t, [(58, 0.0), (62, 0.35)])
    # câmera: plano aberto -> close nas pernas -> abre de novo
    legs_x = sx - 45 * 0.75 * facing
    cx = kf(t, [(37, W / 2), (43, W / 2), (46, legs_x), (51, legs_x), (53, W / 2)])
    cy = kf(t, [(37, H / 2), (43, H / 2), (46, 175), (51, 175), (53, H / 2)])
    z = kf(t, [(43, 1.0), (46, 2.3), (51, 2.3), (53, 1.0)])
    cam_begin(ctx, cx, cy, z)
    # céu
    ctx.rectangle(-400, -600, W * 3, 720)
    rgba(ctx, (0.80, 0.88, 0.90))
    ctx.fill()
    surface_line(ctx, t, 120, sky=False)
    _shore(ctx)
    # água-viva subindo
    jx = kf(t, [(37, W * 0.68), (43, W * 0.60), (52, W * 0.66), (62, W * 0.75)])
    jy = kf(t, [(37, H * 0.78), (43, 205), (50, 230), (62, H * 0.55)])
    box_jelly(ctx, jx, jy, 0.75, t, a=0.85, glow=0.4)
    swimmer(ctx, sx, sy, 0.75, t, outfit="swim", facing=facing, speed=speed, tilt=tilt, stroke=t < 58.5)
    # marcas de chicote nas pernas
    k = appear(t, 43, 2.5)
    if k > 0:
        for i in range(4):
            x0 = sx - facing * (12 + i * 4) * 0.75
            x1 = sx - facing * (80 + i * 4) * 0.75
            y0 = sy - 12 + i * 7
            ctx.move_to(x0, y0)
            ctx.curve_to(lerp(x0, x1, 0.3), y0 - 6, lerp(x0, x1, 0.6), y0 + 6, lerp(x0, x1, k), y0 + 2)
            rgba(ctx, RED, 0.9)
            ctx.set_line_width(2.2)
            ctx.stroke()
    if t > 58:
        bubbles(ctx, sx + facing * 100, sy - 10, t, n=8, rise=60, a=appear(t, 58))
    cam_end(ctx)
    # flash da queimadura
    if 43 <= t < 44.5:
        rgba(ctx, (1, 0.9, 0.85), 0.6 * (1 - (t - 43) / 1.5))
        ctx.paint()
    if 43 <= t < 50:
        rgba(ctx, RED, 0.18 * (1 - appear(t, 47, 3)) * (0.6 + 0.4 * math.sin(t * 7)))
        ctx.paint()
    # distância até a areia (rótulo preso ao nadador, como "20 M" na referência)
    k2 = window(t, 52.5, 62)
    if k2 > 0:
        d = kf(t, [(52.5, 10), (56, 10), (58, 5)])
        line(ctx, W * 0.17, 128, sx - 130, 128, YELLOW, k2, 2)
        line(ctx, W * 0.17, 120, W * 0.17, 136, YELLOW, k2, 2)
        text(ctx, f"{d:.0f} M", (W * 0.17 + sx - 130) / 2, 112, 26, WHITE, k2, "c", "black", sp=1)
    if t > 58:
        rgba(ctx, (0, 0, 0), 0.55 * appear(t, 58, 4))
        ctx.paint()
    vignette(ctx, 0.55, t)


# ------------------------------------------------------------------ 05:50 – 05:58 banhistas no início do século
def sc_history2(ctx, t):
    if t >= 358:
        return S.sc_history(ctx, t)

    def mid(c):
        for i in range(3):
            fall = appear(t, 355.8 + i * 0.5, 0.9)
            x = W * (0.40 + i * 0.12)
            fy = H * 0.675
            wade(c, x, fy + fall * 20, 0.45, 0.45 + 0.5 * fall, t, outfit="swim", rot=-fall * 0.6,
                 arm=lerp(20, 120, fall))

    sky_beach(ctx, t, sunset=0.6, mid=mid)
    rgba(ctx, (0.85, 0.75, 0.55), 0.25)  # tom sépia de época
    ctx.paint()
    chapter(ctx, "AUSTRÁLIA TROPICAL", "INÍCIO DO", "SÉCULO 20", W / 2, H * 0.22, t, 350.5, None, 52)
    vignette(ctx, 0.5, t)


# ------------------------------------------------------------------ 07:15 – 07:43 Jack Barnes
def sc_barnes2(ctx, t):
    if t >= 447:
        return S.sc_barnes(ctx, t)
    night(ctx, t)
    surface_line(ctx, t, H * 0.42, sky=False)
    rgba(ctx, (0.03, 0.05, 0.09))
    ctx.rectangle(0, 0, W, H * 0.42)
    ctx.fill()
    for i in range(60):
        circle(ctx, (i * 197) % W, (i * 89) % int(H * 0.38), 1.2, WHITE, 0.5)
    bx = kf(t, [(435, W * 0.30), (447, W * 0.42)])
    # barco
    ctx.move_to(bx - 150, H * 0.40)
    ctx.line_to(bx + 150, H * 0.40)
    ctx.line_to(bx + 120, H * 0.46)
    ctx.line_to(bx - 130, H * 0.46)
    ctx.close_path()
    ink(ctx, (0.78, 0.78, 0.76), 1, 2.5)
    person(ctx, bx + 40, H * 0.40, 0.42, outfit="swim", arm=kf(t, [(435, 40), (438, 110), (441, 40), (444, 110)]), t=t)
    # lampião
    line(ctx, bx - 100, H * 0.40, bx - 100, H * 0.28, (0.4, 0.4, 0.4), 1, 3)
    g = cairo.RadialGradient(bx - 100, H * 0.28, 2, bx - 100, H * 0.28, 160)
    g.add_color_stop_rgba(0, 1, 0.85, 0.5, 0.5)
    g.add_color_stop_rgba(1, 1, 0.85, 0.5, 0)
    ctx.set_source(g)
    ctx.paint()
    circle(ctx, bx - 100, H * 0.28, 7, (1, 0.9, 0.6))
    # rede de mão mergulhando
    nx = bx + 90
    ny = kf(t, [(435, H * 0.44), (438, H * 0.62), (441, H * 0.44), (444, H * 0.62)])
    line(ctx, bx + 55, H * 0.33, nx, ny, (0.6, 0.5, 0.35), 1, 4)
    ctx.arc(nx, ny + 18, 20, 0, math.pi)
    rgba(ctx, WHITE, 0.6)
    ctx.set_line_width(2)
    ctx.stroke()
    iruk(ctx, W * 0.62, H * 0.66, 0.9, t, appear(t, 437))
    callout(ctx, W * 0.62, H * 0.66, 26, W * 0.78, H * 0.56, "DO TAMANHO DE UMA UNHA", appear(t, 438.5))
    chapter(ctx, "CAIRNS · 1961", "JACK", "BARNES", W / 2, 95, t, 435.5, None, 44)
    globe(ctx, W - 95, 105, 40, window(t, 436, 440.5), lon0=140, lat0=-18, hl=(145.8, -16.9), name="CAIRNS")
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 07:43 – 08:15 redes e recife
def _reef(ctx, x0, t):
    rnd = random.Random(9)
    for i in range(16):
        x = x0 + i * 85
        h = rnd.uniform(90, 200)
        col = [(0.92, 0.48, 0.42), (0.96, 0.72, 0.38), (0.62, 0.50, 0.80), (0.40, 0.72, 0.62)][i % 4]
        ctx.move_to(x, H * 0.92)
        ctx.curve_to(x + 10, H * 0.92 - h, x + 30, H * 0.92 - h * 0.6, x + 40, H * 0.92 - h * 0.9)
        ctx.curve_to(x + 55, H * 0.92 - h * 0.4, x + 70, H * 0.92 - h * 0.7, x + 80, H * 0.92)
        ctx.close_path()
        ink(ctx, col, 1, 2)
    for i in range(3):
        school(ctx, x0 + 300 + i * 380, H * 0.55 + i * 40, t, n=6, spread=60, s=0.3,
               c=[(0.95, 0.75, 0.3), (0.5, 0.7, 0.9), (0.9, 0.5, 0.4)][i], seed=i)


def sc_nets2(ctx, t):
    ocean(ctx, t, top=(0.18, 0.52, 0.58), bot=(0.05, 0.20, 0.26), distant=False)
    pan = kf(t, [(489, 0), (492, W * 1.05)])
    cam_begin(ctx, W / 2 + pan, H / 2, 1.0)
    ctx.rectangle(-400, -600, W * 4, 720)
    rgba(ctx, (0.80, 0.88, 0.90))
    ctx.fill()
    surface_line(ctx, t, 120, sky=False)
    _shore(ctx)
    _reef(ctx, W * 1.25, t)
    # banhistas protegidos dentro da rede
    for i, x in enumerate((W * 0.24, W * 0.36)):
        swimmer(ctx, x, 150, 0.5, t + i, outfit=["swim", "red"][i], facing=1 if i else -1, speed=0.4)
    # rede
    k = appear(t, 475.5, 1.5)
    nx = W * 0.52
    if k > 0:
        bottom = 120 + (H * 0.80 - 120) * k
        for j in range(0, 9):
            line(ctx, nx - 30 + j * 7, 122, nx - 30 + j * 7, bottom, WHITE, 0.35, 1.2)
        yy = 130
        while yy < bottom:
            line(ctx, nx - 30, yy, nx + 26, yy + 8, WHITE, 0.3, 1.2)
            yy += 22
        for j in range(4):
            circle(ctx, nx - 36 + j * 22, 118, 8, ORANGE)
    # água-viva grande batendo na rede
    jx = kf(t, [(463, W * 0.95), (476, W * 0.68)]) + (24 * abs(math.sin(t * 1.2)) if t > 476 else 0)
    box_jelly(ctx, jx, H * 0.40, 0.75, t, glow=0.4)
    callout(ctx, nx, H * 0.45, 30, nx - 160, H * 0.60, "REDE DE PROTEÇÃO", window(t, 476.5, 482))
    # irukandji atravessando a malha
    ix = kf(t, [(479, W * 0.70), (481, W * 0.58), (488.5, W * 0.50), (490, W * 0.45)])
    if 479 <= t < 489:
        iruk(ctx, ix, H * 0.42, 0.8, t, appear(t, 479))
        callout(ctx, ix, H * 0.42, 18, ix + 90, H * 0.30, "~1 CM", appear(t, 479.4))
    # no recife
    if t >= 489:
        swimmer(ctx, W * 1.45 + (t - 489) * 18, 145, 0.6, t, outfit="red", facing=1, speed=0.8)
        iruk(ctx, W * 1.70 - (t - 489) * 10, H * 0.42, 0.8, t)
    cam_end(ctx)
    kicker(ctx, "NO RECIFE E EM MAR ABERTO", W / 2, H * 0.12, t, 490.5, None, 20, WHITE)
    vignette(ctx, 0.5, t)


# ------------------------------------------------------------------ 09:35 – 10:22 o cenário na praia
def _friend_path(t):
    """Posição/pose do amigo na praia."""
    if t < 586:
        return None
    if t < 592:
        p = clamp((t - 586) / 6)
        return dict(x=lerp(W * 0.55, W * 0.66, p), y=lerp(H * 0.86, H * 0.675, p), s=lerp(0.62, 0.45, p),
                    depth=clamp((p - 0.6) / 0.4) * 0.45, pose="walk", rot=0, arm=20)
    if t < 595:
        return dict(x=W * 0.66, y=H * 0.675, s=0.45, depth=0.45, pose="stand", rot=0, arm=30)
    if t < 595.6:
        return dict(x=W * 0.66, y=H * 0.675, s=0.45, depth=0.45, pose="stand", rot=0, arm=160)
    if t < 599:
        p = clamp((t - 595.6) / 3.4)
        return dict(x=lerp(W * 0.66, W * 0.56, p), y=lerp(H * 0.675, H * 0.86, p), s=lerp(0.45, 0.62, p),
                    depth=0.45 * clamp(1 - p / 0.4), pose="walk", rot=math.sin(t * 6) * 0.08, arm=40)
    f = appear(t, 599, 0.8)
    return dict(x=W * 0.56, y=H * 0.86 + f * 8, s=0.62, depth=0, pose="stand", rot=-f * math.pi / 2, arm=40)


def sc_scenario2(ctx, t):
    if t >= 622.5:
        return S.sc_scenario(ctx, t)
    fr = _friend_path(t)

    def mid(c):
        # rede de proteção à esquerda
        k = appear(t, 584.5)
        for i in range(12):
            line(c, W * 0.06 + i * 26, H * 0.56, W * 0.06 + i * 26, H * 0.68, WHITE, 0.55 * k, 2)
        for i in range(6):
            circle(c, W * 0.06 + i * 60, H * 0.56, 5, ORANGE, k)
        if fr and fr["y"] < H * 0.70:
            wade(c, fr["x"], fr["y"], fr["s"], fr["depth"], t, outfit="red", pose=fr["pose"], rot=fr["rot"],
                 arm=fr["arm"])

    sky_beach(ctx, t, sunset=0.2, mid=mid)
    if fr and fr["y"] >= H * 0.70:
        person(ctx, fr["x"], fr["y"], fr["s"], outfit="red", pose=fr["pose"], rot=fr["rot"], arm=fr["arm"], t=t)
    if 595 <= t < 597:
        splash(ctx, W * 0.66, H * 0.66, t, 595.0, 1, 0.6)
    # tentáculos e marcas nas pernas depois da queda
    if t > 600:
        x0, y0 = W * 0.56, H * 0.86 + 8
        for i in range(4):
            line(ctx, x0 - 10, y0 - 14 - i * 4, x0 - 75, y0 - 10 - i * 5, JELLY, 0.9 * appear(t, 600), 1.5)
            line(ctx, x0 - 5, y0 - 12 - i * 4, x0 - 70, y0 - 8 - i * 5, RED, 0.8 * appear(t, 603.5), 3)
    # você
    yx = kf(t, [(595.5, W * 0.30), (599.5, W * 0.48)])
    pose = "run" if 595.5 < t < 599.5 else ("kneel" if t >= 599.5 else "stand")
    person(ctx, yx, H * 0.93, 0.66, outfit="swim", pose=pose, t=t, a=appear(t, 588.5), arm=25)
    # objetos com rótulos presos
    rrect(ctx, W * 0.14, H * 0.86, 110, 62, 8)
    ink(ctx, (0.25, 0.55, 0.85), 1, 2.5)
    rrect(ctx, W * 0.14, H * 0.86, 110, 16, 6)
    ink(ctx, WHITE, 1, 2)
    post_bottle(ctx, W * 0.88, H * 0.84, 0.75, glow=appear(t, 616))
    callout(ctx, W * 0.14 + 55, H * 0.86 + 30, 50, W * 0.12, H * 0.62, "ISOPOR COM ÁGUA", appear(t, 613.3))
    callout(ctx, W * 0.88 + 15, H * 0.84 - 110, 36, W * 0.78, H * 0.56, "VINAGRE · 30 M", appear(t, 616.3))
    callout(ctx, yx + 22, H * 0.93 - 80, 22, W * 0.40, H * 0.60, "CELULAR", appear(t, 619.5))
    globe(ctx, 95, 105, 40, window(t, 584.8, 591), lon0=140, lat0=-18, hl=(145.8, -16.9), name="CAIRNS")
    vignette(ctx, 0.3, t)


# ------------------------------------------------------------------ 11:19 – 11:54 RCP na areia
def sc_answers2(ctx, t):
    if not (679 <= t < 714):
        return S.sc_answers(ctx, t)

    def mid(c):
        pass

    sky_beach(ctx, t, sunset=0.2, mid=mid)
    # amigo deitado
    person(ctx, W * 0.50, H * 0.89, 0.62, outfit="red", rot=-math.pi / 2, t=0)
    for i in range(4):
        line(ctx, W * 0.43, H * 0.89 - 6 - i * 4, W * 0.37, H * 0.89 - 4 - i * 5, RED, 0.8, 3)
    # você: grita, depois ajoelha e faz RCP
    if t < 690.5:
        person(ctx, W * 0.62, H * 0.94, 0.66, outfit="swim", t=t, arm=150 + math.sin(t * 8) * 10)
        if t > 680.5:
            text(ctx, "AJUDA!", W * 0.62, H * 0.50, 30, WHITE, window(t, 680.6, 683.5), "c", "black")
    else:
        press = (math.sin(t * 2 * math.pi * 1.8) + 1) / 2 if t > 696 else 0
        ctx.save()
        ctx.translate(0, press * 6)
        person(ctx, W * 0.53, H * 0.95, 0.66, outfit="swim", pose="kneel", t=t, arm=-10 if t > 696 else 20)
        ctx.restore()
    # pessoa ligando para a emergência
    if t > 683.3:
        bx = kf(t, [(683.3, W + 60), (685.5, W * 0.80)])
        person(ctx, bx, H * 0.93, 0.6, outfit="lifeguard", pose="walk" if t < 685.5 else "stand", t=t, arm=135)
        callout(ctx, bx, H * 0.93 - 140, 22, W * 0.88, H * 0.46, "EMERGÊNCIA", appear(t, 685.5))
    # pessoa correndo até o vinagre e voltando
    if t > 686.3:
        vx = kf(t, [(686.3, W * 0.72), (690, W * 0.95), (703, W * 0.95), (709, W * 0.62)])
        flip = 1
        person(ctx, vx, H * 0.86, 0.5, outfit="kid", pose="run" if (t < 690 or 703 < t < 709) else "stand", t=t)
        if t > 703:
            icon(ctx, "bottle", vx + 22, H * 0.86 - 70, 0.4)
    post_bottle(ctx, W * 0.97, H * 0.80, 0.6, a=1.0 if t < 703 else 1.0)
    label(ctx, "ELE ESTÁ RESPIRANDO?", W / 2, H * 0.20, t, 690.5, 695.3, 34, WHITE)
    label(ctx, "NÃO ESTÁ.", W / 2, H * 0.20, t, 695.3, 697.5, 40, RED)
    big_title(ctx, [("RCP ", ORANGE, "black"), ("AGORA", WHITE, "light")], W / 2, H * 0.20, t, 697.5, None, 64)
    kicker(ctx, "NÃO ESPERE O VINAGRE · NÃO ESPERE A AMBULÂNCIA", W / 2, H * 0.27, t, 699.5)
    label(ctx, "MANTÉM O SANGUE CIRCULANDO", W / 2, H * 0.33, t, 705, None, 22, GREEN)
    vignette(ctx, 0.3, t)


# ------------------------------------------------------------------ 14:03 – 14:10 tartaruga comendo a água-viva
def sc_hope2(ctx, t):
    if t >= 850:
        return S.sc_hope(ctx, t)
    ocean(ctx, t)
    tx = kf(t, [(843, -150), (847.6, W * 0.50), (850, W * 0.66)])
    ty = kf(t, [(843, H * 0.62), (847.6, H * 0.47), (850, H * 0.44)])
    bite = appear(t, 847.6, 0.6)
    jx, jy = W * 0.66, H * 0.36
    if bite < 1:
        box_jelly(ctx, jx, jy, 0.55 * (1 - 0.6 * bite), t, a=1 - bite)
    turtle(ctx, tx, ty, 1.15, t)
    label(ctx, "TARTARUGAS MARINHAS COMEM ELAS", W / 2, H * 0.90, t, 845, None, 28)
    vignette(ctx, 0.6, t)


REPLACE = {
    "sc_beach_open": sc_open,
    "sc_sting": sc_sting2,
    "sc_history": sc_history2,
    "sc_barnes": sc_barnes2,
    "sc_nets": sc_nets2,
    "sc_scenario": sc_scenario2,
    "sc_answers": sc_answers2,
    "sc_hope": sc_hope2,
}
SCENES = [(s, e, REPLACE.get(fn.__name__, fn)) for s, e, fn in S.SCENES]
CUTS = S.CUTS


# ------------------------------------------------------------------ 02:14 – 02:43 comparações de tamanho (barras amarelas)
def sc_anatomy2(ctx, t):
    if t < 134.5 or t >= 152.5:
        return S.sc_anatomy(ctx, t)
    ocean(ctx, t)
    if t < 147.5:
        # água-viva x bola de basquete
        jx, jy = W * 0.34, H * 0.30
        box_jelly(ctx, jx, jy, 1.25, t, glow=0.4)
        name_tag(ctx, "Água-viva-caixa", 40, 60, t, 134.6, None, 26)
        scale_bar(ctx, jx - 75, jx + 75, H * 0.12, (t - 135) / 0.8, "~30 CM")
        bx, by = W * 0.72, H * 0.30
        k = appear(t, 136)
        if k > 0:
            ctx.new_sub_path()
            ctx.arc(bx, by, 58, 0, 2 * math.pi)
            ink(ctx, (0.88, 0.50, 0.22), k, 3)
            for ang in (0, math.pi / 2):
                line(ctx, bx + math.cos(ang) * 58, by + math.sin(ang) * 58, bx - math.cos(ang) * 58,
                     by - math.sin(ang) * 58, INK, k, 2.5)
            text(ctx, "Bola de basquete", bx - 70, by - 80, 18, WHITE, k, "l", "semi", sp=0.4)
            scale_bar(ctx, bx - 58, bx + 58, by + 90, (t - 136.5) / 0.8, "~24 CM")
        # cantos com 15 tentáculos
        callout(ctx, jx - 72, jy + 48, 26, jx - 230, jy + 150, "ATÉ 15 POR CANTO", window(t, 139.5, 147.5))
        callout(ctx, jx + 72, jy + 48, 26, jx + 230, jy + 150, "4 CANTOS = ATÉ 60", window(t, 144.2, 147.5))
    else:
        # tentáculo de 3 m x carro
        jx = W * 0.22
        box_jelly(ctx, jx, H * 0.12, 0.7, t, glow=0.3, tent=2.2)
        scale_bar(ctx, W * 0.40, W * 0.90, H * 0.50, (t - 148) / 1.0, "~3 M DE TENTÁCULO")
        cx, cy = W * 0.65, H * 0.78
        k = appear(t, 149.5)
        if k > 0:
            rrect(ctx, cx - 190, cy - 40, 380, 70, 22)
            ink(ctx, (0.85, 0.30, 0.28), k, 3)
            rrect(ctx, cx - 110, cy - 90, 200, 60, 20)
            ink(ctx, (0.85, 0.30, 0.28), k, 3)
            rrect(ctx, cx - 95, cy - 80, 80, 40, 8)
            ink(ctx, (0.7, 0.85, 0.9), k, 2)
            rrect(ctx, cx - 5, cy - 80, 80, 40, 8)
            ink(ctx, (0.7, 0.85, 0.9), k, 2)
            for wx in (cx - 115, cx + 115):
                ctx.new_sub_path()
                ctx.arc(wx, cy + 32, 32, 0, 2 * math.pi)
                ink(ctx, (0.15, 0.15, 0.17), k, 3)
                circle(ctx, wx, cy + 32, 12, (0.6, 0.6, 0.62), k)
            text(ctx, "MAIS QUE UM CARRO", cx, cy + 105, 18, WHITE, k, "c", "bold", sp=1)
    vignette(ctx, 0.6, t)


# ------------------------------------------------------------------ 08:15 – 08:26 snorkel no recife
def sc_trick2(ctx, t):
    if t >= 506:
        return S.sc_trick(ctx, t)
    ocean(ctx, t, top=(0.16, 0.55, 0.60), bot=(0.05, 0.25, 0.30), distant=False)
    ctx.rectangle(0, 0, W, 110)
    rgba(ctx, (0.80, 0.88, 0.90))
    ctx.fill()
    surface_line(ctx, t, 110, sky=False)
    _reef(ctx, -60, t)
    # barco de passeio
    bx = W * 0.80
    ctx.move_to(bx - 170, 80)
    ctx.line_to(bx + 170, 80)
    ctx.line_to(bx + 140, 135)
    ctx.line_to(bx - 150, 135)
    ctx.close_path()
    ink(ctx, WHITE, 1, 2.5)
    rrect(ctx, bx - 80, 30, 160, 50, 6)
    ink(ctx, (0.85, 0.88, 0.9), 1, 2.5)
    sx = kf(t, [(495, W * 0.18), (500, W * 0.42), (504, W * 0.60)])
    swimmer(ctx, sx, 135, 0.6, t, outfit="red", facing=1, speed=0.8)
    # tubo de snorkel
    line(ctx, sx + 60, 128, sx + 64, 100, (0.95, 0.75, 0.2), 1, 5)
    iruk(ctx, W * 0.38, H * 0.30, 0.7, t)
    if 497 <= t < 499:
        circle(ctx, sx - 40, 150, 30 * appear(t, 497, 0.3), RED, 0.4 * (1 - appear(t, 497.6, 1.2)))
    callout(ctx, sx - 40, 150, 14, sx - 120, H * 0.45, "UMA MANCHINHA", window(t, 497.5, 502))
    label(ctx, "E A PESSOA SE SENTE ÓTIMA", W / 2, H * 0.42, t, 502, None, 26, WHITE)
    vignette(ctx, 0.5, t)


REPLACE.update({"sc_anatomy": sc_anatomy2, "sc_trick": sc_trick2})
SCENES = [(s, e, REPLACE.get(fn.__name__, fn)) for s, e, fn in S.SCENES]
