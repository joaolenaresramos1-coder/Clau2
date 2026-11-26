"""Cenas do vídeo 'Por que você nunca ia querer pisar num peixe-pedra' (10:11).
Duas camadas por cena: world (recebe a gradação de cor) e ui (textos)."""
import math
import random

from stonefish import *  # noqa: F401,F403
from mood import depth_fog

SF_X = W * 0.62  # onde o peixe-pedra está na cena de abertura


def cam(ctx, cx, cy, z):
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)


def small_fish(ctx, t, n=6, seed=1, y0=None, y1=None, s=0.28, a=1.0):
    rnd = random.Random(seed)
    y0 = SURF + 12 if y0 is None else y0
    y1 = FLOOR - 15 if y1 is None else y1
    for i in range(n):
        d = 1 if i % 2 else -1
        sp = rnd.uniform(25, 60)
        x = (rnd.uniform(0, W) + d * t * sp) % (W + 100) - 50
        y = rnd.uniform(y0, y1) + math.sin(t * 2 + i) * 4
        fish(ctx, x, y, s, t + i, c=[(0.95, 0.75, 0.30), (0.45, 0.70, 0.90), (0.90, 0.50, 0.40)][i % 3], a=a, flip=d)


def underwater_close(ctx, t, floor=H * 0.80, murk=0.0):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.30, 0.60, 0.60)
    g.add_color_stop_rgb(1, 0.14, 0.34, 0.36)
    ctx.set_source(g)
    ctx.paint()
    for i in range(30):
        xx = (i * 97 + math.sin(t + i) * 10) % W
        ellipse_path(ctx, xx, floor - 4, 30 + 10 * math.sin(t * 2 + i), 5)
        rgba(ctx, WHITE, 0.10)
        ctx.set_line_width(1.5)
        ctx.stroke()
    ctx.rectangle(0, floor, W, H - floor)
    ink(ctx, (0.78, 0.72, 0.56), 1, 2)
    rnd = random.Random(8)
    for i in range(14):
        sx = rnd.uniform(0, W)
        hh = rnd.uniform(40, 110)
        for j in range(3):
            ctx.move_to(sx + j * 6, floor + 2)
            ctx.curve_to(sx + j * 6 + 10 * math.sin(t * 1.3 + i), floor - hh * 0.4,
                         sx + j * 6 - 10 * math.sin(t * 1.1 + i + j), floor - hh * 0.7,
                         sx + j * 6 + 14 * math.sin(t * 0.9 + i + j), floor - hh)
            rgba(ctx, (0.30, 0.50, 0.32), 0.8)
            ctx.set_line_width(4)
            ctx.stroke()
    for i in range(8):
        rock(ctx, rnd.uniform(0, W), floor + 6, rnd.uniform(70, 140), 30 + i)
    for i in range(5):
        d = 1 if i % 2 else -1
        fx_ = (rnd.uniform(0, W) + d * t * rnd.uniform(30, 70)) % (W + 160) - 80
        fy_ = rnd.uniform(H * 0.15, floor - 60) + math.sin(t * 1.5 + i) * 10
        fish(ctx, fx_, fy_, rnd.uniform(0.35, 0.6), t + i, c=[(0.95, 0.75, 0.30), (0.45, 0.70, 0.90),
                                                             (0.90, 0.50, 0.40)][i % 3], flip=d)
    for i in range(40):
        circle(ctx, rnd.uniform(0, W), (rnd.uniform(0, H) - t * 4) % H, rnd.uniform(1, 2.2), WHITE, 0.25)


# ================================================================== 0:00 – 0:28 o recife raso
WALK = Path([(0, -60, 0), (27.5, SF_X - 150, 0), (28.6, SF_X - 105, 0)])


def w_open(ctx, t):
    x, _ = WALK.pos(t)
    cx = kf(t, [(0, W * 0.35), (22, W * 0.50), (28, SF_X - 80)])
    z = kf(t, [(0, 1.0), (22, 1.0), (28, 1.6)])
    cam(ctx, cx, kf(t, [(0, H * 0.55), (28, FLOOR - 80)]), z)

    def mid(c):
        stonefish(c, SF_X, FLOOR + 6, 120, t, camo=1.0, eyes=0.0, seed=4, bury=1.0)
        wader(c, x, t, "swimmer", WALK.facing(t), 1.2, walker_pose(WALK, t, 70))
        small_fish(c, t, 7, 2)
        # nuvenzinha de areia a cada passo
        ph = WALK.phase(t, 140)
        k = ph % 1
        if WALK.speed(t) > 3 and k < 0.5:
            circle(c, x + 10, FLOOR - 4, 10 + 30 * k, (0.85, 0.80, 0.65), 0.35 * (1 - 2 * k))

    reef_scene(ctx, t, mid, morning=1.0)
    ctx.restore()


def u_open(ctx, t):
    kicker(ctx, "NORTE DA AUSTRÁLIA · MARÉ BAIXA · MANHÃ CEDO", W / 2, H * 0.92, t, 1.0, 8.0, 18, WHITE)
    label(ctx, "ÁGUA NA ALTURA DO JOELHO", W / 2, H * 0.10, t, 8.5, 13.5, 22, (0.12, 0.15, 0.2))


# ================================================================== 0:28 – 0:56 o passo
def w_step(ctx, t):
    # close na altura do pé: o pé desce sobre a "pedra"; os espinhos levantam com a pressão
    underwater_close(ctx, t)
    fx = W * 0.45
    floor = H * 0.80
    press = appear(t, 33.2, 0.25)
    spn = appear(t, 33.0, 0.18)
    stonefish(ctx, W * 0.50, floor + 10, 640, t, camo=1.0 - 0.2 * spn, eyes=0.0, spines=spn, seed=4, breathe=False,
              bury=1.0)
    # perna e pé descendo (vem de cima, peso do corpo)
    back_y = sf_point(W * 0.50, floor + 10, 640, 0.0, -0.46)[1]
    fy = kf(t, [(28, H * 0.02), (31.5, back_y - 140), (33.2, back_y + 4)]) + (5 if t > 33.2 else 0)
    foot(ctx, fx + 10, fy, 1.05, facing=1, leg_to=(fx - 220, -60), bruise=appear(t, 40, 6) * 0.6)
    if t > 36:
        k = appear(t, 36.2, 0.4)
        circle(ctx, fx + 10, fy - 4, 14 * k, RED, 0.6)
    if 36.0 < t < 37.0:
        rgba(ctx, (1, 0.9, 0.85), 0.5 * (1 - (t - 36)))
        ctx.paint()
    if t > 38:
        k = appear(t, 38, 3) * (0.6 + 0.4 * math.sin(t * 6))
        circle(ctx, fx - 40, fy - 60, 120 + 60 * appear(t, 43, 6), RED, 0.22 * k)


def u_step(ctx, t):
    callout(ctx, W * 0.45 + 30, H * 0.47 + 30, 26, W * 0.70, H * 0.20, "UMA FISGADA", window(t, 36.5, 42))


def w_pain(ctx, t):
    studio(ctx, t, H * 0.90)
    x = W * 0.35
    rig.figure(ctx, x, H * 0.90, 2.0, rig.p_flinch(t) if t < 52 else rig.p_stand(t), outfit="swimmer", facing=1,
               t=t)
    pts = rig.world_points(x, H * 0.90, 2.0, rig.p_flinch(t) if t < 52 else rig.p_stand(t), 1)
    spread = clamp((t - 42.5) / 8)
    stops = [pts["toeF"], pts["ankleF"], pts["kneeF"], pts["hip"]]
    for i, (px, py) in enumerate(stops):
        k = clamp(spread * 3 - i)
        if k > 0:
            circle(ctx, px, py, 28 + 18 * k, RED, 0.35 * k * (0.7 + 0.3 * math.sin(t * 6 + i)))


def u_pain(ctx, t):
    timer(ctx, W * 0.72, H * 0.40, 90, clamp((t - 42.5) / 4), appear(t, 42.5), "1 MIN")
    label(ctx, "PÉ → TORNOZELO → CANELA", W * 0.72, H * 0.66, t, 46.5, None, 22, RED)
    label(ctx, "“CORTEM A MINHA PERNA”", W * 0.72, H * 0.76, t, 52.5, None, 24, ORANGE)


def w_look(ctx, t):
    if t < 63:
        cam(ctx, SF_X - 60, FLOOR - 40, 1.8)

        def mid(c):
            stonefish(c, SF_X, FLOOR + 6, 120, t, camo=1.0, eyes=0.0, seed=4, bury=1.0)
            rig.figure(c, SF_X - 125, FLOOR, 1.2, rig.p_flinch(t), outfit="swimmer", facing=1, t=t, shadow=False)

        reef_scene(ctx, t, mid)
        ctx.restore()
        return
    # a pedra abre os olhos
    underwater_close(ctx, t)
    e = appear(t, 64.2, 1.2)
    stonefish(ctx, W * 0.50, H * 0.88, 760, t, camo=1 - 0.6 * e, eyes=e, seed=4,
              spines=appear(t, 66.8, 0.5) * window(t, 66.8, 76), bury=1 - appear(t, 69, 3))


def u_look(ctx, t):
    if t >= 63:
        sx, gy, L = W * 0.50, H * 0.88, 760
        callout(ctx, *sf_point(sx, gy, L, 0.31, -0.33), 26, W * 0.80, H * 0.14, "OLHOS", window(t, 65.5, 72))
        callout(ctx, *sf_point(sx, gy, L, 0.45, 0.10), 30, W * 0.88, H * 0.46, "BOCA", window(t, 66.2, 72))
        callout(ctx, *sf_point(sx, gy, L, -0.05, -0.62), 60, W * 0.18, H * 0.14, "13 ESPINHOS", window(t, 66.8, 76))
        label(ctx, "A UM PALMO DO SEU PÉ", W / 2, H * 0.08, t, 74.5, 79, 22, WHITE)


# ================================================================== 1:19 – 1:50 nome e promessa
def w_name(ctx, t):
    underwater_close(ctx, t)
    stonefish(ctx, W * 0.55, H * 0.90, 600, t, camo=0.2, eyes=1, seed=4, algae=0.6)


def u_name(ctx, t):
    if t < 88:
        name_tag(ctx, "Synanceia verrucosa", 40, 60, t, 79.3, None, 28)
        big_title(ctx, [("PEIXE-", WHITE, "black"), ("PEDRA", ORANGE, "light")], W / 2, H * 0.16, t, 79.5, None, 60)
        kicker(ctx, "O PEIXE MAIS VENENOSO DO MUNDO", W / 2, H * 0.22, t, 81.2, None, 18, WHITE)
        label(ctx, "FOI VOCÊ QUE PISOU NELE", W / 2, H * 0.94, t, 85.8, None, 24, ORANGE)
        return
    items = [("A PEDRA", 88.5), ("A DOR", 92.0), ("FORA D'ÁGUA", 95.0), ("O SOCORRO", 97.5)]
    for i, (nm, c0) in enumerate(items):
        a = window(t, c0, 105.6)
        x = W / 2 + (i - 1.5) * 260
        card(ctx, x - 110, H * 0.30, 220, 120, a)
        text(ctx, nm, x, H * 0.30 + 70, 22, ORANGE, a, "c", "black", sp=2)
    kicker(ctx, "POR QUE VOCÊ NUNCA IA QUERER PISAR NUM", W / 2, H * 0.40, t, 106, None, 20)
    big_title(ctx, [("PEIXE-", WHITE, "black"), ("PEDRA", ORANGE, "light")], W / 2, H * 0.40 + 75, t, 106.4, None, 72)


# ================================================================== 1:50 – 2:30 o que ele é
def w_anat(ctx, t):
    underwater_close(ctx, t)
    camo = kf(t, [(110, 0.0), (128, 0.0), (134, 0.6)])
    stonefish(ctx, W * 0.50, H * 0.88, 700, t, camo=camo, eyes=1, seed=4, algae=appear(t, 138, 2))


def u_anat(ctx, t):
    sx, L = W * 0.50, 700
    label(ctx, "O QUE ELE É?", W / 2, 70, t, 110.2, 114, 34, ORANGE)
    kicker(ctx, "ÁGUAS RASAS E QUENTES · DO MAR VERMELHO À AUSTRÁLIA", W / 2, 70, t, 114, 121, 15, WHITE)
    if not (128.8 < t < 135.2 or 137.9 < t < 151.2):
        scale_bar(ctx, sx - L / 2, sx + L / 2, H * 0.94, (t - 121.5) / 0.8, "30–40 CM")
    callout(ctx, *sf_point(sx, H * 0.88, L, -0.05, 0.0), 70, W * 0.16, H * 0.18, "CORPO GROSSO", window(t, 124, 130))
    callout(ctx, *sf_point(sx, H * 0.88, L, 0.45, 0.10), 40, W * 0.84, H * 0.18, "BOCA VIRADA PARA CIMA",
            window(t, 125.5, 130))
    label(ctx, "SEM ESCAMAS · VERRUGAS E DOBRAS", W / 2, 70, t, 128, 138, 22, WHITE)
    label(ctx, "ALGAS CRESCEM POR CIMA, COMO NUMA PEDRA", W / 2, 70, t, 138, 144, 20, WHITE)
    callout(ctx, *sf_point(sx, H * 0.88, L, 0.31, -0.33), 30, W * 0.70, H * 0.20, "OLHOS NO ALTO DA CABEÇA",
            window(t, 144.2, 150))


# ================================================================== 2:30 – 3:07 o bote
def w_ambush(ctx, t):
    underwater_close(ctx, t)
    sx, ground, L = W * 0.40, H * 0.88, 520
    slow = 176 <= t < 183
    # peixinho passa por cima; no bote (t=177.5 em câmera lenta) é sugado
    tb = 162.0 if not slow else 179.5
    span = 0.12 if not slow else 1.2
    mouth = window(t, tb - span * 0.3, tb + span, span * 0.3) if t < 183 else 0
    stonefish(ctx, sx, ground, L, t, camo=0.3, eyes=1, seed=4, mouth=mouth)
    mx, my = sf_point(sx, ground, L, 0.45, 0.10)
    if (t < tb and t > 155) or (slow and t < tb):
        t0 = 155 if not slow else 176
        p = Path([(t0, W * 1.1, my - 160), (tb - (0.05 if not slow else 0.5), mx + 30, my - 40)])
        x, y = p.pos(t)
        fish(ctx, x, y, 1.0, t, c=(0.95, 0.75, 0.30), flip=p.facing(t))
    elif tb <= t < tb + span:
        k = (t - tb) / span
        fish(ctx, lerp(mx + 30, mx, k), lerp(my - 40, my, k), 1.0 * (1 - k), t, c=(0.95, 0.75, 0.30), flip=-1)
        for i in range(10):
            ang = i * 0.6
            r = 120 * (1 - k)
            line(ctx, mx + math.cos(ang) * r, my + math.sin(ang) * r, mx + math.cos(ang) * (r + 20),
                 my + math.sin(ang) * (r + 20), WHITE, 0.6, 2)
    if slow:
        rgba(ctx, (0.1, 0.2, 0.25), 0.25)
        ctx.paint()


def u_ambush(ctx, t):
    label(ctx, "ELE NÃO PERSEGUE · ELE ESPERA", W / 2, H * 0.10, t, 151.5, 160, 24, WHITE)
    kicker(ctx, "MINUTOS · HORAS", W / 2, H * 0.16, t, 160, 165, 18, SOFT)
    if 176 <= t < 183:
        text(ctx, "CÂMERA LENTA", W * 0.08, H * 0.10, 18, ORANGE, 1, "l", "black", sp=2)
        timer(ctx, W * 0.86, H * 0.20, 60, clamp((t - 176) / 6), 1, "0,01 s")
    label(ctx, "A PRESA SIMPLESMENTE SOME", W / 2, H * 0.94, t, 181.5, 184, 22, ORANGE)
    label(ctx, "ELE NÃO SE MEXE. ELE ESPERA.", W / 2, H * 0.94, t, 184.2, None, 24, WHITE)


# ================================================================== 3:07 – 3:58 os espinhos
def spine_close(ctx, t, cx, base_y, press, a=1.0):
    """Um espinho em corte: duas bolsas de veneno e a bainha de pele que desce quando pressionado."""
    L = 360
    tip = (cx, base_y - L)
    # sulcos
    line(ctx, cx, base_y, tip[0], tip[1], INK, a, 16)
    line(ctx, cx, base_y, tip[0], tip[1], (0.92, 0.88, 0.80), a, 12)
    for s in (-1, 1):
        line(ctx, cx + s * 3, base_y - 40, cx + s * 2, tip[1] + 30, (0.55, 0.50, 0.45), a, 2)
    # bolsas de veneno: espremidas pela bainha
    sq = 1 - 0.55 * press
    for s in (-1, 1):
        ellipse_path(ctx, cx + s * 26 * sq, base_y - 170 + 60 * press, 20 * sq, 60)
        ink(ctx, (0.55, 0.78, 0.40), a, 2)
    # bainha de pele (luva) que desce
    sh = lerp(base_y - 300, base_y - 120, press)
    ctx.move_to(cx - 44, base_y)
    ctx.line_to(cx - 26, sh)
    ctx.curve_to(cx - 10, sh - 14, cx + 10, sh - 14, cx + 26, sh)
    ctx.line_to(cx + 44, base_y)
    ctx.close_path()
    rgba(ctx, (0.55, 0.42, 0.36), 0.55 * a)
    ctx.fill_preserve()
    rgba(ctx, INK, a)
    ctx.set_line_width(2)
    ctx.stroke()
    # veneno subindo pelos sulcos
    if press > 0.3:
        for k in range(8):
            ph = (t * 1.2 + k / 8) % 1
            for s in (-1, 1):
                circle(ctx, cx + s * 3, lerp(base_y - 180, tip[1] + 20, ph), 3.5, (0.60, 0.90, 0.40),
                       a * (press - 0.3) / 0.7)


def w_spines(ctx, t):
    underwater_close(ctx, t)
    if t < 199:
        stonefish(ctx, W * 0.50, H * 0.88, 700, t, camo=0.3, eyes=1, seed=4,
                  spines=window(t, 194.5, 199, 0.8))
        if t > 194:
            fy = kf(t, [(194, -150), (195.6, H * 0.40), (198, H * 0.42)]) + 2 * math.sin(t * 30) * window(t, 195.5, 197)
            foot(ctx, W * 0.47, fy, 1.2, facing=1, leg_to=(W * 0.22, fy - 520))
        return
    press = kf(t, [(199, 0.0), (205, 0.0), (209, 1.0), (222, 1.0), (224, 0.0)])
    # foco: escurece o fundo (corte anatômico em close)
    ctx.rectangle(-W, -H, 3 * W, 3 * H)
    rgba(ctx, (0.03, 0.07, 0.09), 0.45)
    ctx.fill()
    cx, base_y, L = W * 0.36, H * 0.84, 380
    # pele do dorso do peixe: faixa grossa, verrugosa, manchada (corte)
    def skin_path():
        ctx.move_to(-W, H * 2)
        ctx.line_to(-W, base_y + 18)
        for i in range(0, 61):
            x = -W + i * (3 * W / 60)
            y = base_y + 10 * math.sin(x * 0.012) + 6 * math.sin(x * 0.041 + 1) - 22 * math.exp(-((x - cx) / 70) ** 2)
            ctx.line_to(x, y)
        ctx.line_to(2 * W, H * 2)
        ctx.close_path()
    skin_path()
    g = cairo.LinearGradient(0, base_y - 20, 0, H)
    g.add_color_stop_rgb(0, 0.46, 0.40, 0.38)
    g.add_color_stop_rgb(0.35, 0.58, 0.40, 0.40)  # carne
    g.add_color_stop_rgb(1, 0.40, 0.26, 0.28)
    ctx.set_source(g)
    ctx.fill_preserve()
    rgba(ctx, INK, 1)
    ctx.set_line_width(3)
    ctx.stroke()
    ctx.save()
    skin_path()
    ctx.clip()
    rnd = random.Random(11)
    for k in range(70):  # verrugas e manchas na camada de pele
        x = rnd.uniform(-W * 0.2, W * 1.2)
        y = base_y + rnd.uniform(-6, 30)
        r = rnd.uniform(4, 13)
        col = rnd.choice([(0.38, 0.33, 0.30), (0.55, 0.50, 0.42), (0.62, 0.48, 0.34), (0.42, 0.46, 0.38)])
        circle(ctx, x, y, r, col, 0.8)
    # fibras musculares embaixo
    for k in range(12):
        yy = base_y + 50 + k * 9
        line(ctx, -W, yy, 2 * W, yy + 6 * math.sin(k), (0.30, 0.18, 0.20), 0.25, 1.5)
    ctx.restore()
    vf = appear(t, 213, 1.0) * (1 - appear(t, 222, 1))
    spine_detail(ctx, t, cx, base_y, L, press, venom_flow=vf)
    if 204 <= t < 225:
        tip_y = base_y - L
        # o pé desce (com tremor quando o peso entra) e o espinho penetra a sola
        shake = 3 * math.sin(t * 40) * window(t, 206, 210, 0.5)
        lift = kf(t, [(204, -260), (206, -40), (209, 0), (222, 0), (224.5, -300)])
        fy = tip_y + press * 70 + lift + shake
        foot(ctx, cx + 30, fy, 1.3, facing=1, leg_to=(W * 0.08, fy - 520))
        if press > 0.3:
            pa = (press - 0.3) / 0.7
            # ponta do espinho dentro do pé (translúcida através da pele)
            ctx.move_to(cx + L * 0.06 - 9, fy)
            ctx.line_to(cx + L * 0.06 + 1, tip_y)
            ctx.line_to(cx + L * 0.06 + 9, fy)
            rgba(ctx, (0.93, 0.90, 0.84), 0.55 * pa)
            ctx.fill()
            # dor: anéis pulsando no ponto de entrada + veneno espalhando no pé
            for k in range(3):
                ph = (t * 1.4 + k / 3) % 1
                ctx.arc(cx + L * 0.06, fy - 10, 10 + ph * 90, 0, 2 * math.pi)
                rgba(ctx, (0.95, 0.35, 0.25), pa * (1 - ph) * 0.8)
                ctx.set_line_width(3)
                ctx.stroke()
            if vf > 0:
                g = cairo.RadialGradient(cx + L * 0.06, fy - 20, 4, cx + L * 0.06, fy - 20, 40 + 80 * vf)
                g.add_color_stop_rgba(0, 0.55, 0.95, 0.35, 0.55 * vf)
                g.add_color_stop_rgba(1, 0.55, 0.95, 0.35, 0)
                ctx.set_source(g)
                ctx.arc(cx + L * 0.06, fy - 20, 40 + 80 * vf, 0, 2 * math.pi)
                ctx.fill()
        # areia/partículas soltas pela pisada
        if 208 <= t < 212:
            rnd = random.Random(5)
            for k in range(24):
                ph = (t - 208) / 4
                ang = rnd.uniform(math.pi * 1.05, math.pi * 1.95)
                sp = rnd.uniform(60, 220)
                x = cx + math.cos(ang) * sp * ph * 1.5
                y = base_y - 10 + math.sin(ang) * sp * ph + 120 * ph * ph
                circle(ctx, x, y, rnd.uniform(1.5, 3.5), (0.85, 0.80, 0.70), 0.8 * (1 - ph))


def u_spines(ctx, t):
    if t < 199:
        label(ctx, "13 ESPINHOS · NORMALMENTE DEITADOS", W / 2, H * 0.10, t, 189.3, 194.5, 24, WHITE)
        label(ctx, "PRESSÃO DE CIMA: ELES SE LEVANTAM", W / 2, H * 0.10, t, 194.5, None, 24, ORANGE)
        return
    callout(ctx, W * 0.36 + 34, H * 0.84 - 120, 30, W * 0.66, H * 0.30, "BOLSA DE VENENO (2 POR ESPINHO)",
            window(t, 201, 207))
    callout(ctx, W * 0.36 + 36, H * 0.84 - 60, 26, W * 0.66, H * 0.48, "BAINHA DE PELE, COMO UMA LUVA",
            window(t, 205, 212))
    callout(ctx, W * 0.36 + 10, H * 0.84 - 200, 18, W * 0.66, H * 0.20, "DOIS SULCOS", window(t, 213, 220))
    label(ctx, "PELE DO DORSO DO PEIXE (CORTE)", W * 0.80, H * 0.93, t, 200, 224, 16, WHITE)
    label(ctx, "QUANTO MAIS FORTE O PASSO, MAIS VENENO", W / 2, H * 0.08, t, 217, 223, 22, ORANGE)
    if t > 223:
        big_title(ctx, [("É UMA ", WHITE, "black"), ("DEFESA", ORANGE, "light")], W * 0.70, H * 0.40, t, 230, None,
                  44)
        label(ctx, "NÃO SERVE PARA CAÇAR", W * 0.70, H * 0.30, t, 224.5, None, 22, WHITE)
        label(ctx, "E, POR ACIDENTE, CONTRA O SEU PÉ", W * 0.70, H * 0.52, t, 236, None, 20, RED)


# ================================================================== 3:58 – 4:54 o veneno
def w_venom(ctx, t):
    studio(ctx, t, H * 0.92)
    if t < 262:
        # células com buracos (tremendo, vazando) e nervo disparando
        for i in range(12):
            x = W * 0.16 + (i % 6) * 90 + 2 * math.sin(t * 9 + i)
            y = H * 0.42 + (i // 6) * 100 + 2 * math.cos(t * 7 + i * 2)
            hole = appear(t, 243.5 + i * 0.25, 0.4)
            r = 38 * (1 + 0.04 * math.sin(t * 3 + i)) * (1 - 0.12 * hole)
            circle(ctx, x, y, r, (0.90, 0.55, 0.55), 1 - 0.4 * hole)
            circle(ctx, x - 8, y + 6, 9, (0.62, 0.30, 0.34), 0.8 - 0.4 * hole)  # núcleo
            circle(ctx, x + 6, y - 5, 12 * hole * (1 + 0.15 * math.sin(t * 6 + i)), (0.05, 0.08, 0.10))
            if hole > 0:  # conteúdo vazando pelo buraco
                for k in range(4):
                    ph = (t * 0.8 + k / 4 + i * 0.13) % 1
                    circle(ctx, x + 6 + ph * 40 * math.cos(i + k), y - 5 - ph * 40 * math.sin(i + k * 2),
                           3 * (1 - ph), (0.95, 0.70, 0.70), hole * (1 - ph))
        # proteínas do veneno (verdes) chegando e grudando
        for k in range(18):
            ph = min(1, max(0, (t - 241 - k * 0.15) / 2.5))
            tx = W * 0.16 + (k % 6) * 90 + 6
            ty = H * 0.42 + ((k // 6) % 2) * 100 - 30
            sx, sy = W * 0.5 + 300 * math.cos(k), -40
            circle(ctx, lerp(sx, tx, ease(ph)), lerp(sy, ty, ease(ph)), 5, (0.55, 0.95, 0.35), 0.9 * (1 - appear(t, 247, 1)))
        ctx.move_to(W * 0.62, H * 0.45)
        for k in range(60):
            xx = W * 0.62 + k * 7
            spike = math.exp(-((k - (t * 30) % 80) / 3) ** 2) * 60
            yy = H * 0.45 + ((math.sin(k * 1.7 + t * 25) * 18 - spike) if t > 249 else 0)
            ctx.line_to(xx, yy)
        rgba(ctx, YELLOW, 1)
        ctx.set_line_width(3)
        ctx.stroke()
        if t > 249:  # sinais de dor correndo para o cérebro
            for k in range(5):
                ph = (t * 1.3 + k / 5) % 1
                circle(ctx, W * 0.62 + ph * 420, H * 0.45 - 10, 6, RED, 0.9 * math.sin(ph * math.pi))
        return
    # o pé inchando, latejando e escurecendo; a dor sobe pela perna
    sw = appear(t, 262, 3)
    beat = 0.5 + 0.5 * math.sin(t * 2 * math.pi * 1.2)
    y = H * 0.66
    fx, fy = W * 0.40, y + 60
    shake = 1.5 * math.sin(t * 31) * sw
    foot(ctx, fx + shake, fy, 1.6, facing=1, swell=sw * (0.9 + 0.1 * beat), bruise=sw * (0.55 + 0.15 * beat),
         leg_to=(W * 0.02, y - 260))
    pain_fx(ctx, t, fx + 50, fy - 14, sw, (W * 0.02 + 40, y - 230), appear(t, 263, 10))


def pain_fx(ctx, t, x, y, a, up_to=None, spread=1.0):
    """Dor: anéis pulsando no ponto da picada, raios e ondas vermelhas subindo pela perna."""
    if a <= 0:
        return
    for k in range(3):
        ph = (t * 1.2 + k / 3) % 1
        ctx.arc(x, y, 12 + ph * 110, 0, 2 * math.pi)
        rgba(ctx, (0.95, 0.30, 0.25), a * (1 - ph) * 0.7)
        ctx.set_line_width(3)
        ctx.stroke()
    for k in range(8):  # raios de dor
        ang = k * math.pi / 4 + 0.2 * math.sin(t * 3)
        r0 = 30 + 6 * math.sin(t * 8 + k)
        line(ctx, x + math.cos(ang) * r0, y + math.sin(ang) * r0, x + math.cos(ang) * (r0 + 22),
             y + math.sin(ang) * (r0 + 22), (1.0, 0.55, 0.30), a * 0.6 * (0.5 + 0.5 * math.sin(t * 6 + k)), 3)
    if up_to is not None and spread > 0:
        for k in range(4):  # ondas subindo pela perna
            ph = ((t * 0.7 + k / 4) % 1) * spread
            px, py = lerp(x, up_to[0], ph), lerp(y, up_to[1], ph)
            g = cairo.RadialGradient(px, py, 2, px, py, 60)
            g.add_color_stop_rgba(0, 0.95, 0.25, 0.20, 0.45 * a * (1 - ph / max(spread, 0.01) * 0.6))
            g.add_color_stop_rgba(1, 0.95, 0.25, 0.20, 0)
            ctx.set_source(g)
            ctx.arc(px, py, 60, 0, 2 * math.pi)
            ctx.fill()


def u_venom(ctx, t):
    label(ctx, "UMA MISTURA DE PROTEÍNAS", W / 2, H * 0.10, t, 240, 243.5, 26, WHITE)
    label(ctx, "ABRE BURACOS NAS CÉLULAS", W * 0.32, H * 0.75, t, 243.5, 262, 20, WHITE)
    label(ctx, "NERVOS DE DOR DISPARANDO", W * 0.80, H * 0.60, t, 249, 262, 18, YELLOW)
    label(ctx, "UMA DAS PIORES DORES QUE EXISTEM", W / 2, H * 0.10, t, 253, 262, 24, RED)
    if t > 262:
        items = [("INCHAÇO", 262.5), ("PELE ROXA / PRETA", 263.5), ("SUOR · VÔMITO · DESMAIO", 266.5),
                 ("PRESSÃO CAI", 271.5)]
        for i, (nm, c0) in enumerate(items):
            text(ctx, nm, W * 0.76, H * 0.20 + i * 60, 20, RED if i == 3 else WHITE, appear(t, c0), "c", "black",
                 sp=1.5)
        k = appear(t, 275.5)
        if k > 0:
            x0, x1, y = W * 0.10, W * 0.90, H * 0.92
            line(ctx, x0, y, x1, y, SOFT, k, 2)
            for i, (nm, f, c0) in enumerate((("HORAS: DOR FORTE", 0.25, 275.5), ("SEMANAS: INCHAÇO", 0.7, 278))):
                circle(ctx, lerp(x0, x1, f), y, 8, ORANGE, appear(t, c0))
                text(ctx, nm, lerp(x0, x1, f), y - 18, 16, WHITE, appear(t, c0), "c", "black", sp=1)
        label(ctx, "MORTES SÃO RARAS — MAS ACONTECEM", W / 2, H * 0.08, t, 285.5, None, 22, ORANGE)


# ================================================================== 4:54 – 5:18 fora d'água
def w_out(ctx, t):
    # maré baixa: recife quase seco, poça pequena, peixe-pedra preso na poça
    g = cairo.LinearGradient(0, 0, 0, H * 0.6)
    g.add_color_stop_rgb(0, 0.58, 0.72, 0.80)
    g.add_color_stop_rgb(1, 0.95, 0.88, 0.80)
    ctx.set_source(g)
    ctx.paint()
    floor = H * 0.70
    ctx.rectangle(0, floor, W, H - floor)
    ink(ctx, (0.74, 0.68, 0.52), 1, 2)
    px, pw = W * 0.55, 300
    ellipse_path(ctx, px, floor + 6, pw / 2, 26)
    rgba(ctx, (0.35, 0.62, 0.62), 0.9)
    ctx.fill()
    stonefish(ctx, px, floor + 22, 160, t, camo=0.7, eyes=0.6, seed=4)
    ellipse_path(ctx, px, floor + 6, pw / 2, 26)
    rgba(ctx, (0.35, 0.62, 0.62), 0.35)
    ctx.fill()
    rnd = random.Random(2)
    for i in range(10):
        rock(ctx, rnd.uniform(0, W), floor + 8, rnd.uniform(60, 110), 60 + i)
    if t > 310:
        p = Path([(310, W * 0.05, 0), (318, W * 0.42, 0)])
        x, _ = p.pos(t)
        rig.figure(ctx, x, floor, 1.2, walker_pose(p, t, 70), outfit="kid", facing=p.facing(t), t=t)


def u_out(ctx, t):
    big_title(ctx, [("ELE AGUENTA FICAR ", WHITE, "black"), ("FORA D'ÁGUA", ORANGE, "light")], W / 2, H * 0.12, t,
              296.5, 304, 36)
    label(ctx, "HORAS NUMA POÇA RASA, ESPERANDO A MARÉ", W / 2, H * 0.12, t, 304, 310, 22, WHITE)
    label(ctx, "EXATAMENTE ONDE AS PESSOAS ANDAM DESCALÇAS", W / 2, H * 0.12, t, 312.5, None, 22, RED)


# ================================================================== 5:18 – 5:53 como evitar
def w_avoid(ctx, t):
    if t < 338:
        fpath = Path([(318, W * 0.10, 0), (330, W * 0.50, 0), (337, W * 0.62, 0)])
        sf_x = kf(t, [(330.5, W * 0.62), (332.5, W * 0.80)])
        x0, _ = fpath.pos(t)
        cam(ctx, kf(t, [(318, W * 0.40), (337, W * 0.62)]), FLOOR - 70, 1.6)

        def mid(c):
            stonefish(c, sf_x, FLOOR + 6, 130, t, camo=0.6, eyes=1.0, seed=4)
            x, _ = fpath.pos(t)
            p = walker_pose(fpath, t, 60)
            if t > 328:  # arrastando os pés: pés baixos, sem levantar
                p.update(kneeF=4, kneeB=4)
            wader(c, x, t, "lycra", fpath.facing(t), 1.2, p)
            if t > 328:
                circle(c, x + 30, FLOOR - 6, 30, (0.85, 0.80, 0.65), 0.3)

        reef_scene(ctx, t, mid)
        ctx.restore()
        return
    studio(ctx, t, H * 0.86)
    rrect(ctx, W * 0.45, H * 0.30, 80, 150, 10)
    ink(ctx, (0.92, 0.95, 0.97), 1, 2.5)
    rrect(ctx, W * 0.45 + 10, H * 0.30 + 50, 60, 60, 4)
    ink(ctx, (0.85, 0.30, 0.25), 1, 2)
    rrect(ctx, W * 0.45 + 20, H * 0.30 - 20, 40, 24, 4)
    ink(ctx, (0.6, 0.6, 0.62), 1, 2)


def u_avoid(ctx, t):
    if t < 338:
        label(ctx, "SAPATO DE SOLA GROSSA · CHINELO NÃO ADIANTA", W / 2, H * 0.10, t, 320, 327, 20, WHITE)
        label(ctx, "ARRASTE OS PÉS EM VEZ DE PISAR DE CIMA", W / 2, H * 0.10, t, 327.5, None, 22, ORANGE)
        label(ctx, "ELE FOGE", W * 0.80, H * 0.40, t, 333, None, 22, GREEN)
        return
    label(ctx, "EXISTE ANTÍDOTO", W / 2, H * 0.14, t, 338.2, None, 30, ORANGE)
    kicker(ctx, "SORO PRODUZIDO NA AUSTRÁLIA · USADO NOS CASOS GRAVES", W / 2, H * 0.20, t, 340, None, 15, WHITE)
    label(ctx, "MAS O PRIMEIRO SOCORRO É OUTRA COISA", W / 2, H * 0.86, t, 348.5, None, 24, WHITE)


# ================================================================== 5:53 – 6:28 o cenário
def w_scene(ctx, t):
    you = Path([(358, -60, 0), (366, W * 0.30, 0), (369, W * 0.40, 0)])
    fr = Path([(358, W * 0.05, 0), (366, W * 0.55, 0), (367, W * 0.58, 0)])
    cam(ctx, kf(t, [(353, W / 2), (367, W * 0.52), (372, W * 0.55)]), kf(t, [(353, H * 0.55), (372, FLOOR - 80)]),
        kf(t, [(353, 1.0), (367, 1.0), (372, 1.5)]))

    def mid(c):
        stonefish(c, W * 0.61, FLOOR + 6, 110, t, camo=1.0, eyes=0.0, seed=4,
                  spines=appear(t, 366.8, 0.2))
        x, _ = you.pos(t)
        wader(c, x, t, "swimmer", you.facing(t), 1.2, walker_pose(you, t, 70))
        fx, _ = fr.pos(t)
        if t < 367:
            wader(c, fx, t, "friend", fr.facing(t), 1.2, walker_pose(fr, t, 70))
        else:
            # grita, levanta a perna e cai sentada na água (gravidade): termina sentada no fundo
            fall = appear(t, 367.3, 0.7)
            p = rig.blend(rig.p_flinch(t), rig.pose(lean=-10, thighF=80, kneeF=40, thighB=70, kneeB=30, armF=70,
                                                    elbowF=80, armB=60, elbowB=80), fall)
            rig.figure(c, fx, FLOOR, 1.2, p, outfit="friend", facing=1, t=t, shadow=False)
        splash(c, W * 0.58, SURF, t, 367.7, 1, 0.6)

    reef_scene(ctx, t, mid)
    ctx.restore()


def u_scene(ctx, t):
    chapter(ctx, "MANHÃ · MARÉ BAIXA", "O QUE VOCÊ", "FARIA?", W / 2, H * 0.14, t, 353.5, 360, 44)
    if 367 < t < 369:
        text(ctx, "AI!", W * 0.62, H * 0.30, 40, WHITE, window(t, 367, 369), "c", "black")
    callout(ctx, W * 0.55, H * 0.55, 40, W * 0.30, H * 0.20, "UM FURO NA SOLA · A PELE EMPALIDECE", window(t, 373, 381))
    label(ctx, "100 M ATÉ A AREIA · ÁGUA, TOALHA E CELULAR", W / 2, H * 0.94, t, 382, None, 20, WHITE)


# ================================================================== 6:28 – 7:26 decisão e respostas
PANELS = [("A", "GELO / ÁGUA GELADA", 389.5), ("B", "TORNIQUETE", 393.0), ("C", "ÁGUA BEM QUENTE", 397.0)]


def icon_panel(ctx, kind, cx, cy, a, t):
    if kind == "A":
        for i in range(3):
            rrect(ctx, cx - 50 + i * 34, cy - 30 + (i % 2) * 14, 30, 30, 5)
            ink(ctx, (0.85, 0.95, 1.0), a, 2)
    elif kind == "B":
        limb(ctx, [(cx - 80, cy), (cx + 80, cy)], 40, SKIN, a)
        rrect(ctx, cx - 8, cy - 30, 16, 60, 4)
        ink(ctx, (0.25, 0.22, 0.2), a, 2)
    else:
        rrect(ctx, cx - 60, cy - 20, 120, 60, 8)
        ink(ctx, (0.50, 0.75, 0.85), a, 2)
        for k in range(3):
            xx = cx - 30 + k * 30
            ctx.move_to(xx, cy - 30)
            ctx.curve_to(xx - 10, cy - 45, xx + 10, cy - 55, xx, cy - 70 - 4 * math.sin(t * 3 + k))
            rgba(ctx, WHITE, 0.7 * a)
            ctx.set_line_width(2)
            ctx.stroke()


def w_choice(ctx, t):
    studio(ctx, t, H * 0.92)
    for i, (lt, nm, c0) in enumerate(PANELS):
        a = appear(t, c0)
        if a > 0:
            x = W / 2 + (i - 1) * 370
            card(ctx, x - 165, H * 0.24, 330, 220, a)
            icon_panel(ctx, lt, x, H * 0.24 + 110, a, t)


def u_choice(ctx, t):
    label(ctx, "PRIMEIRA DECISÃO", W / 2, 80, t, 388.2, None, 32, WHITE)
    for i, (lt, nm, c0) in enumerate(PANELS):
        a = appear(t, c0)
        x = W / 2 + (i - 1) * 370 - 165
        text(ctx, lt, x + 12, H * 0.24 + 262, 30, ORANGE, a, "l", "black")
        text(ctx, nm, x + 44, H * 0.24 + 260, 15, WHITE, a, "l", "bold", sp=1)
    if t > 400:
        text(ctx, "ESCOLHA UMA ANTES DE EU TE CONTAR", W / 2, H * 0.84, 26, ORANGE, appear(t, 400), "c", "black", sp=2)
        rem = max(0, 402.2 - t)
        text(ctx, f"{math.ceil(rem)}" if rem > 0 else "", W / 2, H * 0.94, 40, WHITE, 1, "c", "black")


def w_answers(ctx, t):
    studio(ctx, t, H * 0.92)
    y = H * 0.62
    foot(ctx, W * 0.42, y + 60, 1.5, facing=1, swell=0.5, bruise=0.4, leg_to=(W * 0.02, y - 220))
    vx, vy = W * 0.42, y + 40
    if t < 420:  # gelo: cubos caem e se empilham; vasos fecham; veneno fica concentrado
        k = appear(t, 409, 2)
        for i in range(5):
            t0 = 403 + i * 0.5
            if t < t0:
                continue
            land = y - 70 - (i % 2) * 34
            yy = min(land, -60 + 900 * (t - t0) ** 2)
            bounce = 6 * math.exp(-6 * max(0, t - t0 - math.sqrt((land + 60) / 900))) * abs(math.sin((t - t0) * 20))
            ctx.save()
            ctx.translate(W * 0.36 + i * 38, yy - bounce)
            ctx.rotate(0.3 * math.sin(i * 2.1))
            rrect(ctx, -17, -17, 34, 34, 6)
            ink(ctx, (0.85, 0.95, 1.0), 0.95, 2)
            line(ctx, -10, -10, 4, -12, WHITE, 0.8, 2)
            ctx.restore()
        # vasos sanguíneos se fechando
        for j in range(3):
            w0 = 8 * (1 - 0.7 * k)
            ctx.move_to(vx - 160, vy - 30 + j * 20)
            ctx.curve_to(vx - 60, vy - 50 + j * 20, vx + 40, vy - 10 + j * 20, vx + 140, vy - 30 + j * 20)
            rgba(ctx, (0.75, 0.20, 0.22), 0.5)
            ctx.set_line_width(w0)
            ctx.stroke()
        # gotinhas de condensação/frio
        for j in range(8):
            ph = (t * 0.6 + j / 8) % 1
            circle(ctx, W * 0.36 + j * 22, y - 40 + ph * 60, 2.5, (0.85, 0.95, 1.0), 0.7 * (1 - ph) * appear(t, 405))
        circle(ctx, vx, vy, (40 - 15 * k) * (1 + 0.08 * math.sin(t * 7)), (0.40, 0.18, 0.40), 0.8)
        circle(ctx, vx, vy, 60, RED, 0.25 * k * (0.6 + 0.4 * math.sin(t * 6)))
        pain_fx(ctx, t, vx + 20, vy - 10, 0.5 + 0.5 * k)
    elif t < 430:  # torniquete apertando: pé fica pálido/roxo
        sq = appear(t, 421, 2.5)
        bx = W * 0.20
        rrect(ctx, bx - 4 * sq, y - 70 + 8 * sq, 26 + 8 * sq, 110 - 16 * sq, 6)
        ink(ctx, (0.25, 0.22, 0.2), 1, 2)
        for j in range(3):  # setas de aperto
            ang = j * 0.4 - 0.4
            line(ctx, bx - 50, y - 15 + j * 15 - 20 * math.sin(ang), bx - 15 - 6 * sq, y - 15 + j * 15, WHITE, 0.6 * sq, 2)
        circle(ctx, vx, vy, 50 + 6 * math.sin(t * 5), (0.40, 0.18, 0.40), 0.7)
        # pé abaixo do torniquete fica arroxeado (sem sangue chegando)
        g = cairo.RadialGradient(vx, vy - 20, 10, vx, vy - 20, 220)
        g.add_color_stop_rgba(0, 0.35, 0.20, 0.45, 0.35 * sq)
        g.add_color_stop_rgba(1, 0.35, 0.20, 0.45, 0)
        ctx.set_source(g)
        ctx.arc(vx, vy - 20, 220, 0, 2 * math.pi)
        ctx.fill()
        pain_fx(ctx, t, vx + 20, vy - 10, 1.0)
    else:  # calor desativa o veneno: proteínas se quebrando
        heat = appear(t, 432, 4)
        circle(ctx, vx, vy, 50 * (1 - 0.6 * heat), (0.40, 0.18, 0.40), 0.7)
        for k in range(10):
            ang = k * 0.63 + t * 0.5
            ph = (t * 0.7 + k / 10) % 1
            px, py = vx + math.cos(ang) * 120, vy + math.sin(ang) * 60 - ph * 50
            line(ctx, px, py, px + 10, py - 14, ORANGE, 0.6 * heat * (1 - ph), 3)
        for k in range(14):  # proteína (verde) -> fragmentos que somem
            ang = k * 2 * math.pi / 14 + t * 0.3
            r = 70 + 50 * heat
            px, py = vx + math.cos(ang) * r, vy - 20 + math.sin(ang) * r * 0.5
            if heat < 0.5:
                circle(ctx, px, py, 7, (0.55, 0.95, 0.35), 0.9)
            else:
                for f in range(3):
                    circle(ctx, px + f * 6 * heat, py - f * 5 * heat, 3, (0.55, 0.95, 0.35), 0.9 * (1.4 - heat))
        pain_fx(ctx, t, vx + 20, vy - 10, 1 - 0.7 * heat)


def u_answers(ctx, t):
    marks = {"A": (402.3, 420, "x"), "B": (420, 430, "x"), "C": (430, 447, "v")}
    for i, (lt, nm, _) in enumerate(PANELS):
        x = W / 2 + (i - 1) * 370 - 165
        card(ctx, x, 30, 330, 60, 1)
        text(ctx, lt + "  " + nm, x + 165, 68, 13, WHITE, 1, "c", "bold", sp=1)
        s0 = marks[lt][0]
        if t > s0 + 1:
            (xmark if marks[lt][2] == "x" else check)(ctx, x + 310, 60, 14, appear(t, s0 + 1))
    label(ctx, "A PIOR", W / 2, H * 0.22, t, 403.5, 420, 44, RED)
    label(ctx, "O FRIO CONCENTRA O VENENO NO LUGAR", W / 2, H * 0.90, t, 409, 420, 20, WHITE)
    label(ctx, "TAMBÉM NÃO — MAIS DANO AO TECIDO", W / 2, H * 0.22, t, 420.5, 430, 28, ORANGE)
    label(ctx, "ACERTOU", W / 2, H * 0.22, t, 431, 440, 44, GREEN)
    label(ctx, "O VENENO É SENSÍVEL AO CALOR", W / 2, H * 0.90, t, 436, None, 22, ORANGE)


# ================================================================== 7:26 – 8:40 o socorro certo
def w_aid(ctx, t):
    if t < 463:
        you = Path([(448, W * 0.60, 0), (458, W * 0.20, 0)])

        def mid(c):
            x, _ = you.pos(t)
            wader(c, x, t, "swimmer", you.facing(t), 1.2, walker_pose(you, t, 60))
            wader(c, x - 50 * you.facing(t), t, "friend", you.facing(t), 1.2,
                  rig.blend(walker_pose(you, t, 60), rig.p_flinch(t), 0.4))

        reef_scene(ctx, t, mid)
        return
    # pé na bacia de água quente; termômetro; mão testando
    studio(ctx, t, H * 0.92)
    bx, by = W * 0.42, H * 0.78
    rrect(ctx, bx - 220, by - 140, 440, 160, 18)
    ink(ctx, (0.55, 0.62, 0.68), 1, 3)
    rrect(ctx, bx - 205, by - 120, 410, 130, 12)
    rgba(ctx, (0.45, 0.72, 0.85), 0.8)
    ctx.fill()
    foot(ctx, bx + 60, by - 14, 1.0, facing=1, swell=0.4, bruise=0.35, leg_to=(bx - 330, by - 360))
    # superfície ondulando
    ctx.move_to(bx - 205, by - 118)
    for i in range(41):
        xx = bx - 205 + i * 10.25
        ctx.line_to(xx, by - 118 + 3 * math.sin(xx * 0.05 + t * 4))
    ctx.line_to(bx + 205, by + 10)
    ctx.line_to(bx - 205, by + 10)
    ctx.close_path()
    rgba(ctx, (0.45, 0.72, 0.85), 0.35)
    ctx.fill()
    for k in range(10):  # bolhas de calor
        ph = (t * 0.5 + k / 10) % 1
        circle(ctx, bx - 180 + (k * 41) % 360, by - ph * 110, 3, WHITE, 0.5 * (1 - ph))
    for k in range(6):  # vapor subindo e se dissipando
        ph = (t * 0.35 + k / 6) % 1
        xx = bx - 170 + k * 70 + 20 * math.sin(t + k)
        yy = by - 140 - ph * 160
        ctx.move_to(xx, yy)
        ctx.curve_to(xx - 14, yy - 25, xx + 14, yy - 45, xx + 4 * math.sin(t * 2 + k), yy - 70)
        rgba(ctx, WHITE, 0.5 * math.sin(ph * math.pi))
        ctx.set_line_width(3)
        ctx.stroke()
    if 473.5 < t < 481:  # a sua mão testando a água (desce, fica, sobe)
        hy = by - 125 + kf(t, [(473.5, -260), (475, 10), (479, 10), (480.8, -260)])
        hx = bx + 150
        ctx.save()
        ctx.translate(hx, hy)
        limb(ctx, [(10, -60), (40, -300)], 46, SKIN, 1)
        ctx.move_to(-28, -60)
        ctx.curve_to(-30, -20, -26, 10, -16, 34)
        for f in range(4):
            fx0 = -16 + f * 11
            ctx.curve_to(fx0, 50 - abs(f - 1.5) * 6, fx0 + 9, 50 - abs(f - 1.5) * 6, fx0 + 10, 34)
        ctx.curve_to(36, 0, 36, -40, 32, -60)
        ctx.close_path()
        ink(ctx, SKIN, 1, 2.5)
        ctx.restore()
        if 475 < t < 479:
            for k in range(2):
                ph = (t * 1.5 + k / 2) % 1
                ellipse_path(ctx, hx, by - 118, 30 + ph * 60, 6 + ph * 8)
                rgba(ctx, WHITE, 0.6 * (1 - ph))
                ctx.set_line_width(2)
                ctx.stroke()


def u_aid(ctx, t):
    if t < 463:
        label(ctx, "SAIAM DA ÁGUA COM CALMA", W / 2, H * 0.10, t, 448.5, 454, 22, WHITE)
        label(ctx, "LIGUE: “PICADA DE PEIXE-PEDRA”", W / 2, H * 0.10, t, 454, 458, 22, ORANGE)
        label(ctx, "ESPINHO PRESO? SÓ TIRE SE FOR FÁCIL", W / 2, H * 0.10, t, 458, None, 20, WHITE)
        return
    label(ctx, "SEM BACIA? GARRAFAS AO SOL, TORNEIRA DE QUIOSQUE", W / 2, H * 0.10, t, 486, 494, 18, WHITE)
    label(ctx, "RESPIRANDO? TONTA? PÁLIDA? SUANDO FRIO?", W / 2, H * 0.10, t, 494, 507, 18, WHITE)
    label(ctx, "HOSPITAL: DOR · RAIO-X · ANTÍDOTO NOS CASOS GRAVES", W / 2, H * 0.10, t, 507, None, 18, ORANGE)
    big_title(ctx, [("~45 ", ORANGE, "black"), ("°C", WHITE, "light")], W * 0.80, H * 0.24, t, 466, None, 56)
    kicker(ctx, "QUENTE, MAS NÃO FERVENDO", W * 0.80, H * 0.30, t, 466.5, None, 15, WHITE)
    label(ctx, "TESTE COM A SUA MÃO, NÃO COM O PÉ DELA", W * 0.72, H * 0.44, t, 474.5, 486, 18, YELLOW)
    if t > 480:
        timer(ctx, W * 0.80, H * 0.58, 70, clamp((t - 480.5) / 4), appear(t, 480.5), "30–90 MIN")


# ================================================================== 8:40 – 9:26 a reviravolta
def w_twist(ctx, t):
    if t < 540:
        underwater_close(ctx, t)
        # raia passando ao fundo (silhueta) — "tubarões, raias" não conseguem mordê-lo
        rx = kf(t, [(527, W * 1.3), (540, -W * 0.3)])
        ry = H * 0.42 + 14 * math.sin(t * 0.9)
        ctx.save()
        ctx.translate(rx, ry)
        flap = 18 * math.sin(t * 2.4)
        ctx.move_to(-90, 0)
        ctx.curve_to(-40, -30 - flap, 30, -60 - flap, 70, -10)
        ctx.line_to(90, 0)
        ctx.line_to(70, 10)
        ctx.curve_to(30, 60 + flap, -40, 30 + flap, -90, 0)
        ctx.close_path()
        rgba(ctx, (0.10, 0.20, 0.24), 0.55)
        ctx.fill()
        line(ctx, 85, 0, 230, 6 * math.sin(t * 3), (0.10, 0.20, 0.24), 0.55, 3)
        ctx.restore()
        stonefish(ctx, W * 0.50, H * 0.88, 600, t, camo=0.6, eyes=1, seed=4, algae=0.8, breathe=1)
        # cardume de peixinhos passando bem na frente da boca — ele nem se mexe
        for k in range(7):
            px = kf(t, [(522 + k * 0.4, -W * 0.2), (536 + k * 0.4, W * 1.2)])
            py = H * 0.55 + 30 * math.sin(k * 1.3) + 10 * math.sin(t * 2 + k)
            fish(ctx, px, py, 0.8, t + k, (0.85, 0.75, 0.45), 0.95, flip=1, wiggle=0.06)
        return
    if t < 556:
        studio(ctx, t, H * 0.86)
        bx, by = W * 0.45, H * 0.70
        ellipse_path(ctx, bx, by, 260, 60)
        ink(ctx, (0.90, 0.88, 0.84), 1, 3)
        ellipse_path(ctx, bx, by - 10, 220, 40)
        rgba(ctx, (0.80, 0.60, 0.35), 0.9)
        ctx.fill()
        for k in range(5):
            xx = bx - 120 + k * 60
            ctx.move_to(xx, by - 50)
            ctx.curve_to(xx - 14, by - 80, xx + 14, by - 100, xx, by - 130 - 6 * math.sin(t * 2 + k))
            rgba(ctx, WHITE, 0.5)
            ctx.set_line_width(3)
            ctx.stroke()
        return
    underwater_close(ctx, t)
    bleach = appear(t, 557, 6)
    rnd = random.Random(7)
    for i in range(10):
        x = W * 0.08 + i * 120
        h = rnd.uniform(80, 180)
        col = [(0.92, 0.48, 0.42), (0.96, 0.72, 0.38), (0.62, 0.50, 0.80)][i % 3]
        col = tuple(lerp(c, 0.95, bleach) for c in col)
        ctx.move_to(x, H * 0.80)
        ctx.curve_to(x + 10, H * 0.80 - h, x + 40, H * 0.80 - h, x + 60, H * 0.80)
        ink(ctx, col, 1, 2)


def u_twist(ctx, t):
    label(ctx, "O PEIXE MAIS VENENOSO DO MUNDO...", W / 2, H * 0.10, t, 521, 526, 22, WHITE)
    label(ctx, "...NUNCA PERSEGUE NINGUÉM", W / 2, H * 0.10, t, 526, 535, 24, ORANGE)
    label(ctx, "O VENENO SERVE PARA NÃO SER ESMAGADO", W / 2, H * 0.94, t, 535, 540, 20, WHITE)
    if 540 <= t < 556:
        label(ctx, "HONG KONG · OKINAWA · FILIPINAS", W / 2, H * 0.14, t, 544, None, 22, WHITE)
        label(ctx, "COZIDO, O VENENO SE DESFAZ", W / 2, H * 0.92, t, 551, None, 24, ORANGE)
    if t >= 556:
        label(ctx, "CALOR · POLUIÇÃO · TURISMO", W / 2, H * 0.12, t, 557.5, None, 24, RED)


# ================================================================== 9:26 – 10:11 final
def w_end(ctx, t):
    if t < 578:
        underwater_close(ctx, t)
        stonefish(ctx, W * 0.50, H * 0.88, 620, t, camo=kf(t, [(566, 0.3), (578, 1.0)]), eyes=1, seed=4)
        return
    cam(ctx, kf(t, [(578, W / 2), (598, W * 0.60)]), kf(t, [(578, H * 0.55), (598, FLOOR - 40)]),
        kf(t, [(578, 1.0), (598, 2.2)]))

    def mid(c):
        stonefish(c, SF_X, FLOOR + 6, 120, t, camo=1.0, eyes=appear(t, 595.5, 1.5), seed=4)
        p = Path([(578, -60, 0), (594, SF_X - 160, 0)])
        x, _ = p.pos(t)
        wp = walker_pose(p, t, 60)
        wp.update(kneeF=4, kneeB=4)
        wader(c, x, t, "lycra", p.facing(t), 1.2, wp)

    reef_scene(ctx, t, mid)
    ctx.restore()


def u_end(ctx, t):
    if t < 578:
        label(ctx, "ELE SÓ QUER SER UMA PEDRA", W / 2, H * 0.12, t, 575.5, None, 26, WHITE)
        return
    label(ctx, "A ÁGUA RASA QUE PARECE SEGURA", W / 2, H * 0.10, t, 580.5, 584, 20, WHITE)
    label(ctx, "O PÉ DESCALÇO · O PASSO DE CIMA", W / 2, H * 0.10, t, 583.5, 588, 20, WHITE)
    big_title(ctx, [("DESCONFIE ", WHITE, "black"), ("DA PEDRA", ORANGE, "light")], W / 2, H * 0.92, t, 595.5, None,
              44)


def w_card(ctx, t):
    underwater_close(ctx, t)
    stonefish(ctx, W * 0.16, H * 0.88, 200, t, camo=0.8, eyes=1, seed=4)


def u_card(ctx, t):
    text(ctx, "ASSISTA", W * 0.10, H * 0.42, 64, WHITE, appear(t, 600.5), "l", "black")
    text(ctx, "A SEGUIR", W * 0.10, H * 0.52, 64, ORANGE, appear(t, 600.8), "l", "black")
    text(ctx, "mais do fundo do mar", W * 0.10, H * 0.59, 20, SOFT, appear(t, 601.2), "l", "semi")
    k = appear(t, 601.5)
    rrect(ctx, W * 0.52, H * 0.26, W * 0.40, H * 0.40, 12)
    ctx.set_dash([10, 8])
    rgba(ctx, WHITE, 0.6 * k)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.set_dash([])


SCENES = [
    (0.0, 28.0, w_open, u_open),
    (28.0, 42.0, w_step, u_step),
    (42.0, 56.0, w_pain, u_pain),
    (56.0, 79.0, w_look, u_look),
    (79.0, 110.0, w_name, u_name),
    (110.0, 151.0, w_anat, u_anat),
    (151.0, 187.0, w_ambush, u_ambush),
    (187.0, 238.0, w_spines, u_spines),
    (238.0, 294.0, w_venom, u_venom),
    (294.0, 318.0, w_out, u_out),
    (318.0, 353.0, w_avoid, u_avoid),
    (353.0, 388.0, w_scene, u_scene),
    (388.0, 402.2, w_choice, u_choice),
    (402.2, 447.0, w_answers, u_answers),
    (447.0, 520.0, w_aid, u_aid),
    (520.0, 566.0, w_twist, u_twist),
    (566.0, 600.0, w_end, u_end),
    (600.0, 99999.0, w_card, u_card),
]
CUTS = sorted({s for s, *_ in SCENES if s > 0} | {63.0, 88.0, 199.0, 262.0, 338.0, 463.0, 540.0, 556.0, 578.0})
