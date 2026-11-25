"""Cenas do vídeo 'Por que você nunca ia querer cair no meio de um cardume de lulas-de-humboldt' (11:00).
Cada cena tem duas camadas: world (recebe a gradação de cor misteriosa) e ui (textos, por cima, sem gradação).
Movimento: tudo que anda/nada usa motion.Path (direção pela velocidade, sem ré)."""
import math
import random

import rig
from motion import Path, sink
from squid import *  # noqa: F401,F403
from mood import depth_fog

HZ = H * 0.36  # linha do horizonte nas cenas de superfície


def cam(ctx, cx, cy, z):
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)


def underwater(ctx, t, surface_y=None, lit=1.0, deep=0.0):
    """Água à noite vista por baixo; cone de luz verde vindo do barco."""
    top = (lerp(0.05, 0.01, deep), lerp(0.20, 0.03, deep), lerp(0.20, 0.05, deep))
    bot = (0.0, 0.02, 0.03)
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *top)
    g.add_color_stop_rgb(1, *bot)
    ctx.set_source(g)
    ctx.paint()
    if lit > 0:
        sy = surface_y if surface_y is not None else -40
        g = cairo.RadialGradient(W / 2, sy, 20, W / 2, sy, H * 1.1)
        g.add_color_stop_rgba(0, 0.45, 0.95, 0.65, 0.55 * lit)
        g.add_color_stop_rgba(0.6, 0.25, 0.70, 0.50, 0.12 * lit)
        g.add_color_stop_rgba(1, 0.1, 0.4, 0.3, 0)
        ctx.set_source(g)
        ctx.paint()
        for i in range(6):
            x0 = W / 2 + (i - 2.5) * 50 + math.sin(t * 0.4 + i) * 10
            gg = cairo.LinearGradient(0, sy, 0, H)
            gg.add_color_stop_rgba(0, 0.7, 1.0, 0.8, 0.10 * lit)
            gg.add_color_stop_rgba(1, 0.7, 1.0, 0.8, 0)
            ctx.move_to(x0 - 10, sy)
            ctx.line_to(x0 + 10, sy)
            ctx.line_to(x0 + (i - 2.5) * 160 + 60, H)
            ctx.line_to(x0 + (i - 2.5) * 160 - 60, H)
            ctx.close_path()
            ctx.set_source(gg)
            ctx.fill()
    rnd = random.Random(3)
    for i in range(90):
        x = (rnd.random() * W + math.sin(t * 0.3 + i) * 12) % W
        y = (rnd.random() * H - t * rnd.uniform(3, 9)) % H
        circle(ctx, x, y, rnd.uniform(0.8, 2.2), (0.75, 0.95, 0.85), 0.18 + 0.15 * lit)
    if surface_y is not None:
        ctx.rectangle(0, surface_y - 400, W, 400)
        rgba(ctx, (0.03, 0.06, 0.08))
        ctx.fill()
        surface_line(ctx, t, surface_y, sky=False)


def boat_from_below(ctx, x, surface_y, L, t, a=1.0):
    """Casco visto de baixo d'água: silhueta escura na superfície."""
    dy = math.sin(t * 0.9) * 2
    ctx.move_to(x - L / 2, surface_y + dy)
    ctx.curve_to(x - L * 0.3, surface_y + L * 0.12 + dy, x + L * 0.3, surface_y + L * 0.12 + dy, x + L / 2,
                 surface_y + dy)
    ctx.close_path()
    rgba(ctx, (0.02, 0.03, 0.04), a)
    ctx.fill()


def school_paths(n, seed, t0, t1, x0, x1, y0, y1, spread=160):
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        dx, dy = rnd.uniform(-spread, spread), rnd.uniform(-spread * 0.5, spread * 0.5)
        dt = rnd.uniform(-1, 1)
        out.append((Path([(t0 + dt, x0 + dx, y0 + dy), (t1 + dt, x1 + dx * 0.6, y1 + dy * 0.6)]),
                    rnd.uniform(0.7, 1.1), rnd.randint(0, 99)))
    return out


def sea_surface_front(ctx, t, y, a=0.55):
    """Véu de água por cima da parte submersa de quem está na superfície."""
    ctx.rectangle(0, y, W, H - y)
    rgba(ctx, (0.04, 0.12, 0.14), a)
    ctx.fill()
    ctx.move_to(0, y)
    for x in range(0, int(W) + 20, 16):
        ctx.line_to(x, y + math.sin(x * 0.03 + t * 2) * 2.5)
    rgba(ctx, (0.85, 0.95, 0.95), 0.7)
    ctx.set_line_width(2)
    ctx.stroke()


def surface_scene(ctx, t, boat_x=W * 0.45, L=380, lamp=1.0, fleet=1.0):
    night_sky(ctx, t, HZ)
    night_sea(ctx, t, HZ)
    fleet_horizon(ctx, t, HZ, a=fleet)
    panga(ctx, boat_x, HZ + 60, L, t, lamp=lamp)
    sea_surface_front(ctx, t, HZ + 60, 0.45)


# ================================================================== 0:00 – 0:27 abertura
def w_open(ctx, t):
    if t < 6.5:
        # Pacífico à noite visto de cima: costa do Peru e frota de luzes
        rgba(ctx, (0.01, 0.02, 0.04))
        ctx.paint()
        z = lerp(1.0, 2.2, ease(t / 6.5))
        cam(ctx, W * 0.62, H * 0.50, z)
        ctx.move_to(W * 0.70, -20)
        for i in range(30):
            ctx.line_to(W * 0.70 + math.sin(i * 0.7) * 20 + i * 4, i * 28)
        ctx.line_to(W + 20, H + 20)
        ctx.line_to(W + 20, -20)
        ctx.close_path()
        rgba(ctx, (0.07, 0.06, 0.05))
        ctx.fill()
        rnd = random.Random(1)
        for i in range(260):
            x = rnd.gauss(W * 0.55, 60)
            y = rnd.uniform(H * 0.2, H * 0.85)
            circle(ctx, x, y, rnd.uniform(1.0, 2.2), (1.0, 0.95, 0.7), rnd.uniform(0.5, 1.0))
        for i in range(30):
            circle(ctx, W * 0.75 + rnd.uniform(0, 40), rnd.uniform(0, H), 1.5, (1, 0.8, 0.5), 0.5)
        ctx.restore()
        return
    z = kf(t, [(6.5, 1.0), (27, 1.35)])
    cam(ctx, kf(t, [(6.5, W / 2), (27, W * 0.47)]), kf(t, [(6.5, H / 2), (27, HZ + 30)]), z)
    surface_scene(ctx, t)
    # pescadores no barco
    for i, (dx, o) in enumerate(((-90, "casual"), (60, "oldtime"))):
        p = rig.p_stand(t + i)
        rig.figure(ctx, W * 0.45 + dx, HZ + 50, 0.42, p, outfit=o, facing=1 if i == 0 else -1, shadow=False, t=t)
    ctx.restore()


def u_open(ctx, t):
    kicker(ctx, "OCEANO PACÍFICO · COSTA DO PERU · MEIA-NOITE", W / 2, H * 0.92, t, 0.8, 6.2, 18, WHITE)
    label(ctx, "VISTO DO ESPAÇO: UMA CIDADE NO MEIO DO OCEANO", W / 2, H * 0.10, t, 21.5, 26.8, 20, WHITE)


# ================================================================== 0:27 – 0:56 debaixo do barco
SCHOOL_A = school_paths(12, 1, 37, 47, W * 0.5, W * 0.5, H * 1.3, H * 0.55, 260)


def w_under(ctx, t):
    sy = 70
    underwater(ctx, t, sy, lit=1.0)
    boat_from_below(ctx, W / 2, sy, 420, t)
    # peixinhos subindo para a luz
    if t > 31:
        rnd = random.Random(2)
        for i in range(26):
            p = Path([(31 + rnd.uniform(0, 3), rnd.uniform(0, W), H + 40),
                      (40 + rnd.uniform(0, 4), W / 2 + rnd.uniform(-260, 260), rnd.uniform(140, 330))])
            x, y = p.pos(t)
            fish(ctx, x, y, 0.38, t + i, c=(0.70, 0.80, 0.75), flip=p.facing(t))
    # sombras e lulas subindo (nadam com o manto na frente: para cima)
    for p, s, sd in SCHOOL_A:
        if t < p.keys[0][0]:
            continue
        x, y = p.pos(t)
        a = appear(t, p.keys[0][0], 2.0)
        fl = appear(t, 41, 1.5)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(-math.pi / 2 * (1 - appear(t, p.keys[1][0] - 1.5, 2.0)) + 0.2 * math.sin(t + sd))
        squid(ctx, 0, 0, 150 * s, t, head_dir=-1, a=a * (0.4 if t < 41 else 1), flash=fl, seed=sd)
        ctx.restore()
    # isca descendo e lula fisgada
    if t > 50.5:
        jy = min(330, 70 + (t - 50.5) * 160)
        line(ctx, W * 0.56, 60, W * 0.56, jy, (0.85, 0.85, 0.85), 0.8, 1.2)
        hooked = t > 53
        if hooked:
            jy = kf(t, [(53, 330), (56, 40)], fn=lambda k: k)
            line(ctx, W * 0.56, 60, W * 0.56, jy, (0.85, 0.85, 0.85), 0.8, 1.2)
            ctx.save()
            ctx.translate(W * 0.56, jy + 60)
            ctx.rotate(math.pi / 2 + math.sin(t * 12) * 0.25)
            squid(ctx, 0, 0, 170, t, head_dir=-1, flash=1.0, arms_fwd=0.6, seed=5, ink_k=appear(t, 54, 0.6))
            ctx.restore()
        jig(ctx, W * 0.56, jy, 1.0)
    depth_fog(ctx, H * 0.45, H, 0.6)


def u_under(ctx, t):
    callout(ctx, W / 2, H * 0.62, 120, W * 0.20, H * 0.22, "DEZENAS DE BRAÇOS", window(t, 47, 51))


# ================================================================== 0:56 – 1:11 a lula sai da água
def w_catch(ctx, t):
    cam(ctx, W * 0.47, HZ + 20, 2.0)
    surface_scene(ctx, t)
    bx = W * 0.45
    # pescador puxando a linha (inclina para trás ao puxar)
    pull = (math.sin(t * 5) + 1) / 2 if t < 61 else 0
    p = rig.pose(lean=-12 - 10 * pull, thighF=14, kneeF=18, thighB=-10, kneeB=6, armF=70 - 20 * pull, elbowF=20,
                 armB=60 - 20 * pull, elbowB=24)
    rig.figure(ctx, bx + 70, HZ + 50, 0.42, p, outfit="casual", facing=1, shadow=False, t=t)
    hx, hy = rig.hand_point(bx + 70, HZ + 50, 0.42, p, facing=1)
    # lula sendo içada: sai da água num arco, se debate, solta jatos e tinta
    sp = Path([(56, bx + 170, HZ + 140), (59.5, bx + 160, HZ + 70), (62.5, bx + 110, HZ + 10), (66, bx + 95, HZ + 40)])
    sx, sy = sp.pos(t)
    line(ctx, hx, hy, sx, sy - 20, (0.9, 0.9, 0.9), 0.8, 1)
    ctx.save()
    ctx.translate(sx, sy)
    ctx.rotate(math.pi / 2 + math.sin(t * 14) * 0.35)
    squid(ctx, 0, 0, 95, t, head_dir=-1, flash=1.0, arms_fwd=0.7, seed=8, ink_k=window(t, 59.5, 64, 0.4))
    ctx.restore()
    if 59.0 < t < 64:
        for k in range(6):
            ph = (t * 3 + k / 6) % 1
            circle(ctx, sx + math.sin(k * 2.1) * 40 * ph, sy + 30 - ph * 40 + ph * ph * 120, 3, (0.8, 0.95, 1.0),
                   0.8 * (1 - ph))
    splash(ctx, bx + 160, HZ + 62, t, 59.3, 1, 0.5)
    ctx.restore()


def u_catch(ctx, t):
    big_title(ctx, [("DIABLO ", RED, "black"), ("ROJO", WHITE, "light")], W / 2, H * 0.16, t, 65.5, None, 56)
    kicker(ctx, "O DIABO VERMELHO", W / 2, H * 0.22, t, 67.5, None, 18, WHITE)


# ================================================================== 1:11 – 1:37 a parte estranha
def w_strange(ctx, t):
    underwater(ctx, t, None, lit=0.5, deep=0.3)
    if t < 82:
        squid(ctx, W * 0.55, H * 0.42, 560, t, head_dir=1, flash=0.3, seed=3)
        if t > 75:
            rig.figure(ctx, W * 0.18, H * 0.86, 0.95, rig.p_stand(t), outfit="kid", facing=1, t=t)
        line(ctx, 0, H * 0.86, W, H * 0.86, SOFT, 0.25, 1)
    elif t < 88:
        # canibalismo: uma lula maior ataca uma menor
        p_small = Path([(82, W * 0.70, H * 0.55), (88, W * 0.30, H * 0.50)])
        p_big = Path([(82.5, W * 1.15, H * 0.45), (85.5, W * 0.62, H * 0.50), (88, W * 0.32, H * 0.48)])
        swim_squid(ctx, p_small, t, 160, flash=0.8, seed=11)
        att = appear(t, 84.5, 0.6)
        swim_squid(ctx, p_big, t, 300, flash=1.0, seed=12, attack=att)
    else:
        # descendo para o escuro
        y = kf(t, [(88, H * 0.30), (97, H * 1.4)])
        p = Path([(88, W * 0.5, H * 0.30), (97, W * 0.5, H * 1.4)])
        ctx.save()
        ctx.translate(*p.pos(t))
        ctx.rotate(math.pi / 2)
        squid(ctx, 0, 0, 260, t, head_dir=-1, a=1 - appear(t, 95, 2), flash=0.1, seed=4)
        ctx.restore()
        rgba(ctx, (0, 0, 0), 0.6 * appear(t, 89, 6))
        ctx.paint()


def u_strange(ctx, t):
    if t < 82:
        scale_bar(ctx, W * 0.55 - 330, W * 0.55 + 230, H * 0.72, (t - 73.2) / 0.8, "ATÉ ~1,5 M")
        big_title(ctx, [("~50 ", ORANGE, "black"), ("KG", WHITE, "light")], W * 0.78, H * 0.16, t, 75.6, None, 44)
        k = appear(t, 77.5)
        if k > 0:
            timer(ctx, W * 0.14, H * 0.22, 64, clamp((t - 77.5) / 2), k, "< 2 ANOS")
    elif t < 88:
        label(ctx, "INCLUSIVE OUTRAS LULAS", W / 2, H * 0.92, t, 85.5, None, 24, RED)
    else:
        label(ctx, "DE DIA, ELA NÃO ESTÁ AQUI", W / 2, H * 0.12, t, 88.5, None, 26, WHITE)
        kicker(ctx, "CENTENAS DE METROS ABAIXO · QUASE SEM OXIGÊNIO", W / 2, H * 0.18, t, 92, None, 16, SOFT)


# ================================================================== 1:37 – 2:03 nome e promessa
def w_name(ctx, t):
    underwater(ctx, t, None, lit=0.7, deep=0.4)
    if t < 100:
        p = Path([(97, W * 1.2, H * 0.55), (100, W * 0.55, H * 0.50)])
        swim_squid(ctx, p, t, 480, flash=0.4, seed=1)
    else:
        p = Path([(110, W * 1.2, H * 0.78), (116, W * 0.40, H * 0.74), (123, W * -0.3, H * 0.70)])
        if t > 110:
            swim_squid(ctx, p, t, 260, flash=0.5, seed=1)


def u_name(ctx, t):
    if t < 100:
        name_tag(ctx, "Dosidicus gigas", 40, 60, t, 97.3, None, 28)
        big_title(ctx, [("LULA-DE-", WHITE, "black"), ("HUMBOLDT", ORANGE, "light")], W / 2, H * 0.16, t, 97.5, None,
                  56)
        return
    items = [("O AR", 100.5), ("A LUZ", 104.0), ("O CARDUME", 108.5), ("O RESGATE", 111.5)]
    for i, (nm, c0) in enumerate(items):
        a = window(t, c0, 116.0)
        x = W / 2 + (i - 1.5) * 260
        card(ctx, x - 110, H * 0.30, 220, 150, a)
        text(ctx, nm, x, H * 0.30 + 85, 24, ORANGE, a, "c", "black", sp=2)
    kicker(ctx, "POR QUE VOCÊ NUNCA IA QUERER CAIR NO MEIO DE UM CARDUME DE", W / 2, H * 0.40, t, 116.3, None, 18)
    big_title(ctx, [("LULAS-DE-", WHITE, "black"), ("HUMBOLDT", ORANGE, "light")], W / 2, H * 0.40 + 70, t, 116.8,
              None, 62)


# ================================================================== 2:03 – 3:07 anatomia
SX, SY, SL = W * 0.52, H * 0.52, 760


def w_anat(ctx, t):
    underwater(ctx, t, None, lit=0.35, deep=0.5)
    if 144 < t < 157:
        # close numa ventosa: anel com dentinhos
        cx, cy = W * 0.36, H * 0.55
        ctx.new_sub_path()
        ctx.arc(cx, cy, 170, 0, 2 * math.pi)
        ink(ctx, (0.80, 0.45, 0.40), 1, 3)
        ctx.new_sub_path()
        ctx.arc(cx, cy, 120, 0, 2 * math.pi)
        ink(ctx, (0.92, 0.85, 0.70), 1, 3)
        ctx.new_sub_path()
        ctx.arc(cx, cy, 80, 0, 2 * math.pi)
        ink(ctx, (0.35, 0.12, 0.12), 1, 2)
        for k in range(22):
            ang = k * 2 * math.pi / 22
            x1, y1 = cx + math.cos(ang) * 112, cy + math.sin(ang) * 112
            x2, y2 = cx + math.cos(ang) * 84, cy + math.sin(ang) * 84
            ctx.move_to(x1 + math.cos(ang + 1.57) * 9, y1 + math.sin(ang + 1.57) * 9)
            ctx.line_to(x2, y2)
            ctx.line_to(x1 - math.cos(ang + 1.57) * 9, y1 - math.sin(ang + 1.57) * 9)
            ctx.close_path()
            ink(ctx, WHITE, appear(t, 147 + k * 0.05), 1.2)
        return
    if 157 <= t < 168:
        # bico de papagaio: mandíbula de cima com gancho, de baixo menor; abre e fecha
        cx, cy = W * 0.40, H * 0.55
        o = 0.18 * (math.sin(t * 3) + 1) / 2
        ctx.save()
        ctx.translate(cx, cy)
        ctx.rotate(-o)
        ctx.move_to(-110, -10)
        ctx.curve_to(-60, -120, 90, -130, 150, -30)
        ctx.curve_to(165, -5, 160, 25, 140, 45)
        ctx.curve_to(120, 5, 60, -20, -110, 20)
        ctx.close_path()
        ink(ctx, (0.30, 0.25, 0.22), 1, 3)
        ctx.restore()
        ctx.save()
        ctx.translate(cx, cy + 20)
        ctx.rotate(o)
        ctx.move_to(-100, 10)
        ctx.curve_to(-40, 90, 70, 90, 110, 20)
        ctx.curve_to(80, 30, 20, 30, -100, -5)
        ctx.close_path()
        ink(ctx, (0.24, 0.20, 0.18), 1, 3)
        ctx.restore()
        return
    if 168 <= t < 187:
        # propulsão a jato: manto contrai, água sai pelo sifão para a frente, lula vai para trás
        p = Path([(168, W * 0.75, H * 0.50), (175, W * 0.30, H * 0.52), (178, W * 0.25, H * 0.40),
                  (181, W * 0.60, H * 0.35), (184, W * 0.62, H * 0.62)])
        x, y = p.pos(t)
        mv = p.facing(t)
        swim_squid(ctx, p, t, 420, flash=0.1, seed=6)
        sp = p.speed(t)
        for k in range(10):
            ph = (t * 2.5 + k / 10) % 1
            jx = x - mv * (-60 - ph * 260)
            circle(ctx, jx, y + math.sin(k) * 14 * ph, 6 + 20 * ph, (0.7, 0.9, 0.95),
                   0.35 * (1 - ph) * min(1, sp / 80))
        return
    squid(ctx, SX, SY, SL, t, head_dir=1, flash=0.0, seed=2, arms_fwd=0.15)


def u_anat(ctx, t):
    if t < 144:
        label(ctx, "O QUE ELA É?", W / 2, 80, t, 123.2, 126, 34, ORANGE)
        kicker(ctx, "UM MOLUSCO · PARENTE DO POLVO, DO CARACOL E DA OSTRA", W / 2, 80, t, 126, 133.5, 16, WHITE)
        kicker(ctx, "PERDEU A CONCHA · VIROU UMA MÁQUINA DE NADAR", W / 2, 80, t, 133.5, 144, 16, WHITE)
        callout(ctx, SX - SL * 0.30, SY, 90, W * 0.20, H * 0.20, "CORPO EM TUBO", window(t, 136.0, 144))
        callout(ctx, SX - SL * 0.60, SY, 50, W * 0.10, H * 0.82, "NADADEIRAS", window(t, 137.5, 144))
        callout(ctx, SX + SL * 0.30, SY, 80, W * 0.80, H * 0.18, "8 BRAÇOS + 2 TENTÁCULOS", window(t, 140.0, 144))
    elif t < 157:
        label(ctx, "VENTOSA", W * 0.72, H * 0.30, t, 144.5, None, 30, ORANGE)
        kicker(ctx, "ANEL DURO COM DENTINHOS AFIADOS", W * 0.72, H * 0.36, t, 145.5, None, 15, WHITE)
        label(ctx, "COMO DEZENAS DE PEQUENAS SERRAS", W * 0.72, H * 0.60, t, 150.5, None, 20, RED)
    elif t < 168:
        label(ctx, "BICO", W * 0.74, H * 0.32, t, 157.5, None, 34, ORANGE)
        kicker(ctx, "PROTEÍNA, SEM MINERAL NENHUM", W * 0.74, H * 0.38, t, 163.5, None, 15, WHITE)
        label(ctx, "CORTA PEIXE, CASCA E CARNE", W * 0.74, H * 0.62, t, 165.5, None, 20, WHITE)
    else:
        big_title(ctx, [("PROPULSÃO ", WHITE, "black"), ("A JATO", ORANGE, "light")], W / 2, H * 0.14, t, 177.5,
                  None, 44)
        kicker(ctx, "ÁGUA SAI PELO SIFÃO · A LULA VAI PARA O OUTRO LADO", W / 2, H * 0.20, t, 175, None, 15, WHITE)


# ================================================================== 3:07 – 3:30 cromatóforos
def w_chroma(ctx, t):
    underwater(ctx, t, None, lit=0.4, deep=0.5)
    if t < 195:
        rnd = random.Random(9)
        for i in range(60):
            cx, cy = rnd.uniform(W * 0.1, W * 0.9), rnd.uniform(H * 0.2, H * 0.85)
            op = 0.5 + 0.5 * math.sin(t * 6 + i)
            r = 10 + 26 * op
            circle(ctx, cx, cy, r, (0.75, 0.22, 0.20), 0.85)
            for k in range(6):
                ang = k * math.pi / 3
                line(ctx, cx + math.cos(ang) * r, cy + math.sin(ang) * r, cx + math.cos(ang) * (r + 14),
                     cy + math.sin(ang) * (r + 14), (0.85, 0.75, 0.70), 0.5, 1.5)
    else:
        for i, (x, y, sd) in enumerate(((W * 0.35, H * 0.40, 1), (W * 0.62, H * 0.60, 2))):
            p = Path([(195, x + 40 * (1 - 2 * i), y), (210, x - 40 * (1 - 2 * i), y + 10)])
            swim_squid(ctx, p, t, 340, flash=1.0, seed=sd)


def u_chroma(ctx, t):
    if t < 195:
        label(ctx, "CÉLULAS DE COR", W / 2, 80, t, 188.5, None, 32, ORANGE)
        kicker(ctx, "ABREM E FECHAM EM FRAÇÕES DE SEGUNDO", W / 2, 118, t, 189.5, None, 16, WHITE)
    else:
        label(ctx, "UMA LINGUAGEM DE LUZ E COR?", W / 2, H * 0.12, t, 199.5, None, 26, WHITE)
        kicker(ctx, "NINGUÉM CONSEGUIU TRADUZIR AINDA", W / 2, H * 0.18, t, 202, None, 15, SOFT)
        label(ctx, "LEMBRE DO PISCA-PISCA", W / 2, H * 0.92, t, 209, None, 24, ORANGE)


# ================================================================== 3:30 – 4:16 o fundo sem oxigênio
DEPTH_MAX = 800.0


def w_deep(ctx, t):
    d = kf(t, [(210, 0), (226, 600), (245, 600), (256, 30)])
    k = d / DEPTH_MAX
    underwater(ctx, t, None, lit=max(0, 0.6 - k), deep=min(1, 0.3 + k))
    rgba(ctx, (0, 0, 0), 0.55 * k)
    ctx.paint()
    up = t > 245
    p = Path([(210, W * 0.48, H * 0.35), (226, W * 0.48, H * 0.55), (245, W * 0.48, H * 0.55),
              (256, W * 0.48, H * 0.35)])
    x, y = p.pos(t)
    slow = window(t, 230, 245, 2.0)
    ctx.save()
    ctx.translate(x, y + math.sin(t * (2 - 1.6 * slow)) * 6)
    ctx.rotate(math.pi / 2 * (1 if not up else -1) * (1 - window(t, 226, 245, 1.5)))
    squid(ctx, 0, 0, 300, t * (1 - 0.8 * slow), head_dir=-1, flash=0.05, seed=7,
          pulse=1 - 0.8 * slow)
    ctx.restore()


def u_deep(ctx, t):
    d = kf(t, [(210, 0), (226, 600), (245, 600), (256, 30)])
    x = W * 0.92
    line(ctx, x, H * 0.10, x, H * 0.90, SOFT, 0.6, 2)
    for i in range(9):
        yy = H * 0.10 + i * H * 0.10
        line(ctx, x - 10, yy, x, yy, SOFT, 0.6, 2)
        text(ctx, f"{i * 100} M", x - 16, yy + 5, 12, SOFT, 0.7, "r", "bold", sp=0.5)
    yy = H * 0.10 + d / DEPTH_MAX * H * 0.80
    circle(ctx, x, yy, 7, ORANGE)
    text(ctx, f"{int(d)} M", x - 20, yy - 12, 20, ORANGE, 1, "r", "black")
    k = window(t, 222, 245)
    if k > 0:
        text(ctx, "OXIGÊNIO", W * 0.08, H * 0.12, 14, WHITE, k, "l", "bold", sp=2)
        lv = kf(t, [(222, 1.0), (226, 0.06)])
        rrect(ctx, W * 0.08, H * 0.14, 300, 18, 9)
        rgba(ctx, (0.2, 0.25, 0.28), k)
        ctx.fill()
        rrect(ctx, W * 0.08, H * 0.14, 300 * lv, 18, 9)
        rgba(ctx, RED if lv < 0.3 else GREEN, k)
        ctx.fill()
        label(ctx, "ZONA DE MÍNIMO DE OXIGÊNIO", W * 0.45, H * 0.86, t, 224.5, 245, 20, ORANGE)
    k = window(t, 233.5, 245)
    if k > 0:
        rrect(ctx, W * 0.08, H * 0.24, 70, 34, 6)
        ink(ctx, (0.1, 0.1, 0.1), k, 2)
        rrect(ctx, W * 0.08 + 4, H * 0.24 + 4, 62 * 0.15, 26, 3)
        rgba(ctx, YELLOW, k)
        ctx.fill()
        text(ctx, "MODO ECONOMIA", W * 0.08 + 85, H * 0.24 + 23, 16, YELLOW, k, "l", "black", sp=1)
    label(ctx, "QUANDO O SOL SE PÕE, ELA SOBE", W * 0.45, H * 0.10, t, 245.5, None, 22, WHITE)


# ================================================================== 4:16 – 4:42 a cadeia da luz
def w_light(ctx, t):
    sy = 70
    underwater(ctx, t, sy, lit=1.0)
    boat_from_below(ctx, W / 2, sy, 420, t)
    rnd = random.Random(5)
    stage = 0 if t < 258.5 else 1 if t < 260 else 2
    for i in range(140):
        x = W / 2 + rnd.gauss(0, 200) + math.sin(t + i) * 6
        y = 110 + abs(rnd.gauss(0, 120))
        circle(ctx, x, y, 1.6, (0.85, 1.0, 0.85), 0.6 * appear(t, 256.5))
    if t > 258.5:
        for i in range(18):
            p = Path([(258.5, rnd.uniform(0, W), H + 30), (262, W / 2 + rnd.uniform(-220, 220), rnd.uniform(160, 300))])
            x, y = p.pos(t)
            fish(ctx, x, y, 0.25, t + i, c=(0.70, 0.80, 0.75), flip=p.facing(t))
    if t > 260:
        for i, (p, s, sd) in enumerate(school_paths(5, 4, 260, 264, W / 2, W / 2, H * 1.3, H * 0.62, 260)):
            x, y = p.pos(t)
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(-math.pi / 2 * (1 - appear(t, 263, 1.5)))
            squid(ctx, 0, 0, 140 * s, t, head_dir=-1, flash=0.8, seed=sd)
            ctx.restore()
    if t > 266.5:
        jy = min(330, 70 + (t - 266.5) * 150)
        hooked = t > 271
        if hooked:
            jy = kf(t, [(271, 330), (277, 40)], fn=lambda k: k)
        line(ctx, W * 0.40, 60, W * 0.40, jy, (0.85, 0.85, 0.85), 0.8, 1.2)
        if hooked:
            ctx.save()
            ctx.translate(W * 0.40, jy + 60)
            ctx.rotate(math.pi / 2 + math.sin(t * 12) * 0.25)
            squid(ctx, 0, 0, 160, t, head_dir=-1, flash=1.0, arms_fwd=0.6, seed=7)
            ctx.restore()
        jig(ctx, W * 0.40, jy, 1.0)
    depth_fog(ctx, H * 0.5, H, 0.55)


def u_light(ctx, t):
    items = [("LUZ", 256.5), ("PLÂNCTON", 257.5), ("PEIXINHOS", 258.5), ("LULAS", 260.0)]
    for i, (nm, c0) in enumerate(items):
        a = window(t, c0, 266)
        x = W * 0.20 + i * W * 0.20
        text(ctx, nm, x, H * 0.94, 20, ORANGE if i == 3 else WHITE, a, "c", "black", sp=2)
        if i < 3:
            text(ctx, "→", x + W * 0.10, H * 0.94, 20, SOFT, a, "c", "black")
    callout(ctx, W * 0.40, 300, 26, W * 0.62, H * 0.30, "ISCA BRILHANTE · PONTAS SEM FARPA", window(t, 267.5, 272))
    label(ctx, "CENTENAS POR NOITE, POR PESCADOR", W / 2, H * 0.94, t, 277.5, None, 22, WHITE)


# ================================================================== 4:42 – 5:30 dentro do cardume
SCHOOL_B = school_paths(14, 9, 282, 300, W * 1.3, W * 0.5, H * 0.5, H * 0.55, 300)


def w_school(ctx, t):
    underwater(ctx, t, None, lit=0.55, deep=0.35)
    if t < 296:
        for p, s, sd in SCHOOL_B:
            swim_squid(ctx, p, t, 170 * s, flash=0.3, seed=sd)
        if t > 288.5:
            rnd = random.Random(1)
            for i in range(40):
                p = Path([(288.5, W * 0.2 + rnd.uniform(-80, 80), H * 0.3 + rnd.uniform(-40, 40)),
                          (296, W * 0.6 + rnd.uniform(-80, 80), H * 0.3 + rnd.uniform(-40, 40))])
                x, y = p.pos(t)
                fish(ctx, x, y, 0.18, t + i, c=(0.75, 0.80, 0.82), flip=p.facing(t))
        return
    # lula fisgada se debatendo; as outras percebem e atacam
    hx, hy = W * 0.50, kf(t, [(296, H * 0.70), (316, H * 0.30)], fn=lambda k: k)
    line(ctx, hx, -10, hx, hy - 60, (0.85, 0.85, 0.85), 0.8, 1.2)
    ctx.save()
    ctx.translate(hx, hy)
    ctx.rotate(math.pi / 2 + math.sin(t * 13) * 0.3)
    squid(ctx, 0, 0, 200, t, head_dir=-1, flash=1.0, arms_fwd=0.7, seed=3, ink_k=window(t, 298, 303, 0.4))
    ctx.restore()
    for i, (sx0, sd) in enumerate(((-0.2, 21), (1.2, 22), (1.25, 23))):
        t0 = 300.5 + i * 2.5
        p = Path([(t0, W * sx0, H * (0.75 + 0.05 * i)), (t0 + 3, hx + (-90 if sx0 < 0.5 else 90), hy + 40 + i * 25),
                  (t0 + 20, hx + (-80 if sx0 < 0.5 else 80), hy + 30 + i * 25)])
        if t > t0:
            x, y = p.pos(t)
            att = appear(t, t0 + 1.5, 0.8)
            swim_squid(ctx, p, t, 220, flash=1.0, seed=sd, attack=att)
    depth_fog(ctx, H * 0.6, H, 0.5)


def u_school(ctx, t):
    if t < 296:
        label(ctx, "SARDINHAS: JUNTAS = SEGURAS", W / 2, H * 0.12, t, 289, 293.5, 22, WHITE)
        label(ctx, "LULAS: A AMEAÇA PODE SER A DO LADO", W / 2, H * 0.12, t, 293.5, None, 22, RED)
    else:
        label(ctx, "UM ANIMAL SE DEBATENDO = UM ANIMAL FRACO", W / 2, H * 0.92, t, 300, 316, 20, WHITE)
        items = [("MOVIMENTO", 316.5), ("LUZ FORTE", 318.0), ("SANGUE NA ÁGUA", 319.5)]
        for i, (nm, c0) in enumerate(items):
            a = appear(t, c0)
            x = W / 2 + (i - 1) * 300
            card(ctx, x - 130, H * 0.82, 260, 54, a)
            text(ctx, nm, x, H * 0.82 + 34, 18, ORANGE, a, "c", "black", sp=1.5)


# ================================================================== 5:30 – 6:11 lendas e fatos
def w_legend(ctx, t):
    if t < 339:
        # lenda: barco escuro e homem caindo, em tom sépia (memória de pescador)
        night_sky(ctx, t, HZ)
        night_sea(ctx, t, HZ)
        panga(ctx, W * 0.45, HZ + 60, 380, t, lamp=0.6)
        sea_surface_front(ctx, t, HZ + 60, 0.45)
        rgba(ctx, (0.45, 0.32, 0.18), 0.35)
        ctx.paint()
        return
    underwater(ctx, t, None, lit=0.3, deep=0.5)
    if t > 349:
        # mergulhador agarrado: o equipamento é arrancado e afunda (sink)
        dp = Path([(349, W * 0.35, H * 0.40), (361, W * 0.40, H * 0.38)])
        x, y = dp.pos(t)
        rig.figure(ctx, x, y, 1.6, rig.p_fin(t, 0.5), outfit="diver", facing=1, ground=False, t=t)
        p = Path([(350, W * 0.85, H * 0.65), (352.5, x + 120, y + 30), (361, x + 110, y + 20)])
        swim_squid(ctx, p, t, 260, flash=1.0, seed=31, attack=appear(t, 351, 0.6))
        dx, sy = sink(t, 354, y + 20, H * 0.95, 45)
        if t > 354:
            rrect(ctx, x + 40 + dx, sy, 26, 12, 4)
            ink(ctx, YELLOW, 1, 1.5)


def u_legend(ctx, t):
    if t < 339:
        label(ctx, "HISTÓRIAS DE PESCADORES · PERU E MÉXICO", W / 2, H * 0.12, t, 330.5, None, 22, (0.95, 0.85, 0.65))
        return
    if t < 349:
        card(ctx, W * 0.30, H * 0.22, W * 0.40, H * 0.50, appear(t, 339))
        k = appear(t, 339.3)
        for i, (lb, val) in enumerate((("NOME", "—"), ("DATA", "—"), ("REGISTRO", "—"))):
            text(ctx, lb, W * 0.33, H * 0.32 + i * 60, 16, SOFT, k, "l", "bold", sp=2)
            text(ctx, val, W * 0.60, H * 0.32 + i * 60, 22, WHITE, k, "l", "black")
        s = appear(t, 343.5, 0.3)
        if s > 0:
            ctx.save()
            ctx.translate(W / 2, H * 0.60)
            ctx.rotate(-0.12)
            ctx.scale(1.4 - 0.4 * s, 1.4 - 0.4 * s)
            rrect(ctx, -210, -34, 420, 68, 8)
            rgba(ctx, RED, 0.9 * s)
            ctx.set_line_width(4)
            ctx.stroke()
            text(ctx, "NENHUMA MORTE CONFIRMADA", 0, 10, 22, RED, s, "c", "black", sp=1)
            ctx.restore()
        return
    callout(ctx, W * 0.40 + 40, H * 0.50, 30, W * 0.62, H * 0.86, "EQUIPAMENTO ARRANCADO", window(t, 354.5, 361))
    label(ctx, "O PERIGO É ENTRAR NO MUNDO DELA", W / 2, H * 0.12, t, 362, None, 24, ORANGE)


# ================================================================== 6:11 – 6:54 o cenário
FALL_T = 400.5


def fisher_fall(t, bx):
    """Trajetória física da queda: escorrega na borda, cai em arco (gravidade) e afunda até subir de volta."""
    x0, y0 = bx + 150, HZ + 46
    if t < FALL_T:
        return x0, y0, "stand"
    dt = t - FALL_T
    vx, vy, g = 90.0, -120.0, 900.0
    x = x0 + vx * min(dt, 0.9)
    y = y0 + vy * dt + 0.5 * g * dt * dt
    surf = HZ + 60
    if y < surf + 10:
        return x, y, "fall"
    # dentro d'água: afunda um pouco e volta à superfície
    tw = t - (FALL_T + 0.6)
    return x, surf + 28 + max(0, 50 - tw * 60), "water"


def w_scene(ctx, t):
    bx = W * 0.42
    cam(ctx, kf(t, [(371, W / 2), (390, W * 0.52), (397, W * 0.58)]), kf(t, [(371, HZ + 20), (397, HZ + 50)]),
        kf(t, [(371, 1.6), (390, 1.9), (397, 2.0)]))
    night_sky(ctx, t, HZ)
    night_sea(ctx, t, HZ)
    fleet_horizon(ctx, t, HZ)
    panga(ctx, bx, HZ + 60, 380, t)
    # convés escorregadio com lulas e tinta
    for i in range(7):
        squid(ctx, bx - 120 + i * 30, HZ + 40, 40, 0.0, head_dir=1 if i % 2 else -1, flash=0, seed=i)
    rig.figure(ctx, bx - 60, HZ + 46, 0.42, rig.p_stand(t), outfit="swimmer", facing=1, shadow=False, t=t)
    x, y, st = fisher_fall(t, bx)
    if st == "stand":
        pull = (math.sin(t * 5) + 1) / 2
        p = rig.pose(lean=-12 - 10 * pull, thighF=14, kneeF=18, thighB=-10, kneeB=6, armF=70, elbowF=20, armB=60,
                     elbowB=24)
        rig.figure(ctx, x, y, 0.42, p, outfit="casual", facing=1, shadow=False, t=t)
    elif st == "fall":
        p = rig.blend(rig.p_flinch(t), rig.pose(rot=110, armF=150, armB=130), appear(t, FALL_T, 0.6))
        rig.figure(ctx, x, y, 0.42, p, outfit="casual", facing=1, ground=False, t=t)
    else:
        p = rig.p_tread(t * 3)
        rig.figure(ctx, x, y, 0.42, p, outfit="casual", facing=-1, ground=False, t=t)
    splash(ctx, bx + 230, HZ + 62, t, FALL_T + 0.55, 1, 0.5)
    sea_surface_front(ctx, t, HZ + 60, 0.5)
    if t > 405:
        k = appear(t, 405, 2)
        for i in range(8):
            ang = i * 0.8 + t * 0.4
            sx = x + math.cos(ang) * 70
            sy = HZ + 90 + abs(math.sin(ang)) * 40
            fl = 0.5 + 0.5 * math.sin(t * 18 + i)
            circle(ctx, sx, sy, 9, lerp(0.7, 0.95, fl) and (lerp(0.78, 0.93, fl), lerp(0.22, 0.88, fl),
                                                            lerp(0.20, 0.84, fl)), 0.6 * k)
    ctx.restore()


def u_scene(ctx, t):
    chapter(ctx, "MEIA-NOITE · MAR AGITADO", "O QUE VOCÊ", "FARIA?", W / 2, H * 0.14, t, 371.5, 380, 44)
    kicker(ctx, "CONVÉS ESCORREGADIO · ÁGUA, TINTA E ISCA", W / 2, H * 0.90, t, 382, 394, 16, WHITE)
    if 401 < t < 404:
        text(ctx, "SPLASH", W * 0.62, H * 0.30, 30, WHITE, window(t, 401, 404), "c", "black")


# ================================================================== 6:54 – 7:49 decisão e respostas
PANELS = [("A", "PULAR NA ÁGUA", 418.0), ("B", "BOIA + ‘FIQUE PARADO’", 420.0), ("C", "DESLIGAR AS LUZES", 424.0)]


def mini_boat(ctx, x, y, w, h, kind, t):
    ctx.save()
    rrect(ctx, x + 6, y + 6, w - 12, h - 12, 6)
    ctx.clip()
    ctx.translate(x + 6, y + 6)
    ctx.scale((w - 12) / W, (h - 12) / H)
    lamp = 0.0 if kind == "C" else 1.0
    night_sky(ctx, t, HZ)
    night_sea(ctx, t, HZ)
    panga(ctx, W * 0.40, HZ + 60, 520, t, lamp=lamp)
    rig.figure(ctx, W * 0.70, HZ + 130, 0.8, rig.p_tread(t * 3), outfit="casual", facing=-1, ground=False, t=t)
    if kind == "A":
        rig.figure(ctx, W * 0.82, HZ + 130, 0.8, rig.p_tread(t * 3 + 1), outfit="swimmer", facing=-1, ground=False,
                   t=t)
    if kind == "B":
        line(ctx, W * 0.45, HZ + 20, W * 0.74, HZ + 64, (0.9, 0.9, 0.9), 1, 3)
        ctx.new_sub_path()
        ctx.arc(W * 0.76, HZ + 66, 26, 0, 2 * math.pi)
        rgba(ctx, ORANGE)
        ctx.set_line_width(12)
        ctx.stroke()
    sea_surface_front(ctx, t, HZ + 60, 0.5)
    ctx.restore()


def w_choice(ctx, t):
    underwater(ctx, t, None, lit=0.0, deep=0.6)
    for i, (lt, nm, c0) in enumerate(PANELS):
        a = appear(t, c0)
        if a <= 0:
            continue
        x = W / 2 + (i - 1) * 370 - 165
        card(ctx, x, H * 0.22, 330, 200, a, fill=(0.06, 0.12, 0.14))
        mini_boat(ctx, x, H * 0.22, 330, 200, lt, t)


def u_choice(ctx, t):
    label(ctx, "PRIMEIRA DECISÃO", W / 2, 70, t, 414.3, None, 32, WHITE)
    for i, (lt, nm, c0) in enumerate(PANELS):
        a = appear(t, c0)
        x = W / 2 + (i - 1) * 370 - 165
        text(ctx, lt, x + 12, H * 0.22 + 240, 30, ORANGE, a, "l", "black")
        text(ctx, nm, x + 44, H * 0.22 + 238, 14, WHITE, a, "l", "bold", sp=1)
    k = appear(t, 427)
    if k > 0:
        text(ctx, "ESCOLHA UMA ANTES DE EU TE CONTAR", W / 2, H * 0.80, 26, ORANGE, k, "c", "black", sp=2)
        rem = max(0, 430 - t)
        text(ctx, f"{math.ceil(rem)}" if rem > 0 else "", W / 2, H * 0.92, 44, WHITE, k, "c", "black")


def w_answers(ctx, t):
    if t < 448:
        night_sky(ctx, t, HZ)
        night_sea(ctx, t, HZ)
        panga(ctx, W * 0.35, HZ + 60, 380, t)
        for i, (x, o) in enumerate(((W * 0.58, "casual"), (W * 0.68, "swimmer"))):
            rig.figure(ctx, x, HZ + 130, 0.42 * 2, rig.p_tread(t * 3 + i), outfit=o, facing=-1, ground=False, t=t)
        sea_surface_front(ctx, t, HZ + 60, 0.5)
        for i in range(10):
            ang = i * 0.7 + t * 0.6
            circle(ctx, W * 0.63 + math.cos(ang) * 120, HZ + 130 + abs(math.sin(ang)) * 60, 10, RED, 0.5)
        return
    # apagar as luzes: as lulas se espalham, mas você perde o colega de vista
    off = appear(t, 450, 1.5)
    night_sky(ctx, t, HZ)
    night_sea(ctx, t, HZ)
    panga(ctx, W * 0.35, HZ + 60, 380, t, lamp=1 - off)
    p = Path([(450, W * 0.62, HZ + 130), (465, W * 0.90, HZ + 135)])
    x, y = p.pos(t)
    rig.figure(ctx, x, y, 0.84, rig.p_tread(t * 3), outfit="casual", facing=-1, ground=False, t=t,
               a=1 - 0.85 * appear(t, 456, 4))
    sea_surface_front(ctx, t, HZ + 60, 0.5)
    rgba(ctx, (0, 0, 0), 0.55 * off)
    ctx.paint()


def u_answers(ctx, t):
    marks = {"A": (429.5, 448, "x"), "C": (448, 465, "x")}
    for i, (lt, nm, _) in enumerate(PANELS):
        x = W / 2 + (i - 1) * 370 - 165
        card(ctx, x, 30, 330, 60, 1, fill=(0.06, 0.12, 0.14))
        text(ctx, lt + "  " + nm, x + 165, 68, 13, WHITE, 1, "c", "bold", sp=1)
        if lt in marks and t > marks[lt][0] + 1:
            xmark(ctx, x + 310, 60, 14, appear(t, marks[lt][0] + 1))
    if t < 448:
        label(ctx, "A PIOR", W / 2, H * 0.24, t, 431, None, 44, RED)
        label(ctx, "QUEM ESTÁ NO BARCO NÃO VIRA A SEGUNDA VÍTIMA", W / 2, H * 0.92, t, 442.5, None, 20, WHITE)
    else:
        label(ctx, "MAIS PERTO... MAS VOCÊ PERDE ELE DE VISTA", W / 2, H * 0.24, t, 449, None, 24, ORANGE)


# ================================================================== 7:45 – 8:54 o resgate certo
def w_rescue(ctx, t):
    bx = W * 0.36
    cam(ctx, W * 0.50, HZ + 60, 1.6)
    night_sky(ctx, t, HZ)
    night_sea(ctx, t, HZ)
    fleet_horizon(ctx, t, HZ, a=0.6)
    panga(ctx, bx, HZ + 60, 380, t)
    # você aponta e grita; outro joga a boia com corda (arco balístico) além do colega
    rig.figure(ctx, bx + 120, HZ + 46, 0.42, rig.p_shout(t) if t < 476 else rig.p_stand(t), outfit="swimmer",
               facing=1, shadow=False, t=t)
    thrower = rig.pose(lean=-6, armF=150 if t < 479 else 60, elbowF=10, armB=40) if t < 482 else rig.pose(
        lean=-15, armF=60, elbowF=30, armB=55, elbowB=30)
    rig.figure(ctx, bx + 40, HZ + 46, 0.42, thrower, outfit="oldtime", facing=1, shadow=False, t=t)
    # colega na água: debatendo-se até 486, depois parado segurando a boia
    vx = W * 0.66
    calm = appear(t, 486, 2)
    pull = clamp((t - 524) / 10)
    px = lerp(vx, bx + 190, ease(pull))
    p = rig.p_tread(t * lerp(3, 0.8, calm))
    rig.figure(ctx, px, HZ + 100, 0.42 * 2, p, outfit="casual", facing=-1, ground=False, t=t)
    # boia em arco: sai da mão em 479, cai além dele, é puxada até ele
    if t > 479:
        dt = t - 479
        bx0, by0 = bx + 60, HZ - 10
        tx = vx + 80
        tf = 1.1
        if dt < tf:
            q = dt / tf
            byy = by0 + (HZ + 62 - by0) * q - 160 * math.sin(math.pi * q)
            bxx = lerp(bx0, tx, q)
        else:
            bxx = lerp(tx, px + 20, ease(clamp((dt - tf) / 4)))
            byy = HZ + 62 + math.sin(t * 2) * 2
        line(ctx, bx + 60, HZ + 30, bxx, byy, (0.9, 0.9, 0.85), 0.9, 1.5)
        ctx.new_sub_path()
        ctx.arc(bxx, byy, 16, 0, 2 * math.pi)
        rgba(ctx, ORANGE)
        ctx.set_line_width(8)
        ctx.stroke()
    # lanterna apontada para ele
    if t > 516:
        flashlight(ctx, bx + 120, HZ + 10, math.atan2(HZ + 100 - (HZ + 10), px - (bx + 120)), 520, 0.12,
                   appear(t, 516))
    # lulas em volta: agitadas enquanto ele se debate, perdem interesse quando ele para
    k = 1 - 0.7 * calm
    for i in range(7):
        ang = i * 0.9 + t * (0.8 - 0.5 * calm)
        r = 90 + 80 * calm
        sx = px + math.cos(ang) * r
        sy = HZ + 150 + abs(math.sin(ang)) * 60 + 50 * calm
        fl = 0.5 + 0.5 * math.sin(t * 16 + i)
        circle(ctx, sx, sy, 9, (lerp(0.78, 0.93, fl), lerp(0.22, 0.88, fl), lerp(0.2, 0.84, fl)), 0.55 * k)
    sea_surface_front(ctx, t, HZ + 60, 0.5)
    ctx.restore()


def u_rescue(ctx, t):
    label(ctx, "ALGUÉM SÓ OLHA PARA ELE — O TEMPO TODO", W / 2, H * 0.10, t, 471.5, 479, 20, WHITE)
    label(ctx, "BOIA COM CORDA, UM POUCO ALÉM DELE", W / 2, H * 0.10, t, 479, 485, 20, WHITE)
    big_title(ctx, [("PARE DE SE ", WHITE, "black"), ("DEBATER", ORANGE, "light")], W / 2, H * 0.12, t, 488.5, 507, 44)
    label(ctx, "PARADO, ELE NÃO PARECE UM ANIMAL FERIDO", W / 2, H * 0.92, t, 495, 507, 20, GREEN)
    label(ctx, "PAREM A ISCA · SOLTEM AS LINHAS", W / 2, H * 0.10, t, 507, 516, 20, WHITE)
    label(ctx, "LANTERNA NELE, NÃO NA ÁGUA EM VOLTA", W / 2, H * 0.10, t, 516, 521, 20, YELLOW)
    label(ctx, "AGARROU? EMPURRE E PROTEJA ROSTO E PESCOÇO", W / 2, H * 0.10, t, 521, 528, 20, WHITE)
    label(ctx, "PUXEM PELA BORDA MAIS BAIXA", W / 2, H * 0.10, t, 528, None, 20, ORANGE)


# ================================================================== 8:54 – 9:17 no convés
def w_aid(ctx, t):
    studio(ctx, t, H * 0.86)
    y = H * 0.62
    limb(ctx, [(-60, y), (W * 0.45, y + 6), (W * 0.70, y + 10)], 110, SKIN)
    ellipse_path(ctx, W * 0.74, y + 10, 46, 60, 0.2)
    ink(ctx, SKIN, 1, 2.5)
    rnd = random.Random(2)
    for i in range(9):
        cx, cy = W * 0.20 + i * 55, y + rnd.uniform(-30, 30)
        ctx.new_sub_path()
        ctx.arc(cx, cy, 14, 0, 2 * math.pi)
        rgba(ctx, (0.70, 0.20, 0.20), appear(t, 538 + i * 0.1))
        ctx.set_line_width(3)
        ctx.stroke()
    line(ctx, W * 0.52, y - 20, W * 0.60, y + 25, (0.55, 0.05, 0.05), appear(t, 542), 6)
    if t > 545:
        for k in range(8):
            ph = (t * 1.5 + k / 8) % 1
            circle(ctx, W * 0.56 + math.sin(k) * 30, y - 140 + ph * 120, 4, (0.7, 0.85, 1.0), 0.7 * (1 - ph))
    if t > 547:
        rrect(ctx, W * 0.50, y - 50, 120, 90, 10)
        ink(ctx, (0.90, 0.88, 0.82), appear(t, 547), 2)


def u_aid(ctx, t):
    callout(ctx, W * 0.30, H * 0.62, 30, W * 0.22, H * 0.22, "CÍRCULOS DE CORTES (VENTOSAS)", window(t, 538.5, 547))
    callout(ctx, W * 0.56, H * 0.63, 30, W * 0.70, H * 0.22, "CORTE DO BICO", window(t, 542.5, 547))
    label(ctx, "LAVE BEM · PRESSIONE ONDE SANGRA", W / 2, H * 0.10, t, 545.5, None, 24, WHITE)
    label(ctx, "NO MAR, INFECCIONA FÁCIL → MÉDICO EM TERRA", W / 2, H * 0.94, t, 548, None, 20, ORANGE)


# ================================================================== 9:17 – 10:13 a reviravolta
def w_twist(ctx, t):
    if t < 572:
        underwater(ctx, t, None, lit=0.3, deep=0.5)
        cx, cy, r = W / 2, H * 0.55, 200
        ctx.new_sub_path()
        ctx.arc(cx, cy, r, 0, 2 * math.pi)
        rgba(ctx, SOFT, 0.3)
        ctx.set_line_width(3)
        ctx.stroke()
        k = clamp((t - 562) / 9)
        ctx.new_sub_path()
        ctx.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * k)
        rgba(ctx, ORANGE, 0.9)
        ctx.set_line_width(5)
        ctx.stroke()
        ang = -math.pi / 2 + 2 * math.pi * k
        ctx.save()
        ctx.translate(cx + math.cos(ang) * r, cy + math.sin(ang) * r)
        ctx.rotate(ang + math.pi)
        squid(ctx, 0, 0, lerp(40, 160, k), t, head_dir=-1, flash=0.3, seed=1, a=1 - appear(t, 571, 0.8))
        ctx.restore()
        return
    if t < 595:
        # fotos de satélite: luzes da frota no Pacífico
        rgba(ctx, (0.01, 0.02, 0.04))
        ctx.paint()
        ctx.move_to(W * 0.72, -20)
        for i in range(30):
            ctx.line_to(W * 0.72 + math.sin(i * 0.7) * 20 + i * 3, i * 28)
        ctx.line_to(W + 20, H + 20)
        ctx.line_to(W + 20, -20)
        ctx.close_path()
        rgba(ctx, (0.08, 0.07, 0.06))
        ctx.fill()
        rnd = random.Random(7)
        n = int(clamp((t - 576) / 6) * 900)
        for i in range(n):
            x = rnd.gauss(W * 0.45, 140)
            y = rnd.uniform(H * 0.05, H * 0.95)
            circle(ctx, x, y, rnd.uniform(0.8, 2.0), (1.0, 0.95, 0.7), rnd.uniform(0.4, 1.0))
        return
    # El Niño: água esquentando no mapa
    rgba(ctx, (0.02, 0.06, 0.09))
    ctx.paint()
    k = appear(t, 595.5, 3)
    for i in range(40):
        y = H * 0.25 + i * 10
        g = cairo.LinearGradient(0, 0, W, 0)
        g.add_color_stop_rgba(0, 0.9, 0.3, 0.2, 0)
        g.add_color_stop_rgba(0.6, 0.95, 0.45, 0.2, 0.5 * k * (0.5 + 0.5 * math.sin(i * 0.5 + t)))
        g.add_color_stop_rgba(1, 0.95, 0.45, 0.2, 0.2 * k)
        ctx.set_source(g)
        ctx.rectangle(0, y, W * 0.8, 8)
        ctx.fill()
    ctx.move_to(W * 0.80, -20)
    for i in range(30):
        ctx.line_to(W * 0.80 + math.sin(i * 0.7) * 20 + i * 3, i * 28)
    ctx.line_to(W + 20, H + 20)
    ctx.line_to(W + 20, -20)
    ctx.close_path()
    rgba(ctx, MAPLAND)
    ctx.fill()
    for i in range(5):
        p = Path([(600 + i, W * 0.60, H * 0.55), (612 + i, W * 0.30, H * (0.20 + 0.12 * i))])
        if t > 600 + i:
            swim_squid(ctx, p, t, 70, flash=0.3, seed=i)


def u_twist(ctx, t):
    if t < 572:
        label(ctx, "NÃO ESTÁ NO MAR PARA PEGAR NINGUÉM", W / 2, H * 0.10, t, 557.5, None, 24, WHITE)
        items = [("1–2 ANOS", 562), ("DIA NO ESCURO", 566), ("SOBE TODA NOITE", 567.5), ("SE REPRODUZ", 570),
                 ("E MORRE", 571.3)]
        for i, (nm, c0) in enumerate(items):
            ang = -math.pi / 2 + i * 2 * math.pi / 5
            text(ctx, nm, W / 2 + math.cos(ang) * 290, H * 0.55 + math.sin(ang) * 250, 16,
                 RED if i == 4 else WHITE, appear(t, c0), "c", "black", sp=1.5)
    elif t < 595:
        label(ctx, "UMA DAS MAIORES PESCARIAS DE INVERTEBRADOS DO MUNDO", W / 2, H * 0.10, t, 573, None, 20, WHITE)
        kicker(ctx, "MILHARES DE BARCOS · CENTENAS DE MILHARES DE TONELADAS POR ANO", W / 2, H * 0.92, t, 579.5, None,
               14, SOFT)
    else:
        big_title(ctx, [("EL ", WHITE, "black"), ("NIÑO", ORANGE, "light")], W * 0.40, H * 0.12, t, 595.5, None, 44)
        kicker(ctx, "MUDAM DE LUGAR · CRESCEM MENOS · AMADURECEM MAIS CEDO", W * 0.40, H * 0.92, t, 598, None, 14,
               WHITE)


# ================================================================== 10:13 – 11:00 final
def w_end(ctx, t):
    if t < 645:
        underwater(ctx, t, 70, lit=appear(t, 613, 4), deep=0.4)
        boat_from_below(ctx, W / 2, 70, 420, t, a=appear(t, 613, 4))
        for p, s, sd in school_paths(10, 31, 613, 640, W / 2, W / 2, H * 1.4, H * 0.55, 300):
            if t < p.keys[0][0]:
                continue
            x, y = p.pos(t)
            ctx.save()
            ctx.translate(x, y)
            ctx.rotate(-math.pi / 2)
            squid(ctx, 0, 0, 150 * s, t, head_dir=-1, flash=appear(t, 640, 2), seed=sd)
            ctx.restore()
        depth_fog(ctx, H * 0.4, H, 0.7)
        return
    cam(ctx, W * 0.47, HZ + 20, kf(t, [(645, 1.0), (652, 1.6)]))
    surface_scene(ctx, t)
    for i in range(14):
        ang = i * 0.45 + t * 0.4
        sx = W * 0.45 + math.cos(ang) * 260
        sy = HZ + 110 + abs(math.sin(ang * 1.3)) * 80
        fl = 0.5 + 0.5 * math.sin(t * 16 + i)
        circle(ctx, sx, sy, 9, (lerp(0.78, 0.93, fl), lerp(0.22, 0.88, fl), lerp(0.2, 0.84, fl)), 0.55)
    ctx.restore()


def u_end(ctx, t):
    if t < 645:
        label(ctx, "ELA NÃO TE CAÇA · SÓ SOBE DO ESCURO ATRÁS DA LUZ", W / 2, H * 0.92, t, 619, 630, 20, WHITE)
        items = [("A NOITE", 631.5), ("A LUZ", 632.3), ("A ISCA", 633), ("O SANGUE", 633.8), ("ALGUÉM SE DEBATENDO", 634.8)]
        for i, (nm, c0) in enumerate(items):
            text(ctx, nm, W * 0.80, H * 0.30 + i * 56, 24, RED if i == 4 else WHITE, window(t, c0, 645), "c", "black",
                 sp=2)
        return
    big_title(ctx, [("FIQUE DENTRO ", WHITE, "black"), ("DO BARCO", ORANGE, "light")], W / 2, H * 0.14, t, 646, None,
              48)


def w_card(ctx, t):
    underwater(ctx, t, None, lit=0.2, deep=0.6)
    p = Path([(650, W * 1.2, H * 0.82), (662, -W * 0.2, H * 0.80)])
    swim_squid(ctx, p, t, 160, a=0.7, flash=0.2, seed=2)


def u_card(ctx, t):
    text(ctx, "ASSISTA", W * 0.10, H * 0.48, 64, WHITE, appear(t, 650.5), "l", "black")
    text(ctx, "A SEGUIR", W * 0.10, H * 0.58, 64, ORANGE, appear(t, 650.8), "l", "black")
    text(ctx, "mais do fundo do mar", W * 0.10, H * 0.65, 20, SOFT, appear(t, 651.2), "l", "semi")
    k = appear(t, 651.5)
    rrect(ctx, W * 0.52, H * 0.30, W * 0.40, H * 0.40, 12)
    ctx.set_dash([10, 8])
    rgba(ctx, WHITE, 0.6 * k)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.set_dash([])


SCENES = [
    (0.0, 27.0, w_open, u_open),
    (27.0, 56.0, w_under, u_under),
    (56.0, 71.0, w_catch, u_catch),
    (71.0, 97.0, w_strange, u_strange),
    (97.0, 123.0, w_name, u_name),
    (123.0, 188.0, w_anat, u_anat),
    (188.0, 210.0, w_chroma, u_chroma),
    (210.0, 256.0, w_deep, u_deep),
    (256.0, 282.0, w_light, u_light),
    (282.0, 330.0, w_school, u_school),
    (330.0, 371.0, w_legend, u_legend),
    (371.0, 414.0, w_scene, u_scene),
    (414.0, 429.5, w_choice, u_choice),
    (429.5, 465.0, w_answers, u_answers),
    (465.0, 536.0, w_rescue, u_rescue),
    (536.0, 557.0, w_aid, u_aid),
    (557.0, 613.0, w_twist, u_twist),
    (613.0, 650.0, w_end, u_end),
    (650.0, 99999.0, w_card, u_card),
]
CUTS = sorted({s for s, *_ in SCENES if s > 0} | {6.5, 82.0, 88.0, 100.0, 144.0, 157.0, 168.0, 195.0, 296.0, 339.0,
                                                  349.0, 448.0, 572.0, 595.0, 645.0})
