"""Cenas do vídeo do caramujo-cone, sincronizadas com a narração (t.txt).

Regras: física primeiro (pés no chão, gravidade, ninguém nada de costas, o caramujo só rasteja devagar),
tom misterioso (o grade de cor é aplicado no render), bastante movimento em toda cena,
e marcações sempre ancoradas no ponto exato do desenho (mark/mcallout).
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "video4"), os.path.join(HERE, "..", "video3"),
                os.path.join(HERE, "..", "video")]

import cairo  # noqa: E402

from cone import *  # noqa: F401,F403,E402
from stonefish import rock, reef_scene, FLOOR, SURF, wader, walker_pose, foot  # noqa: E402
from scenes_stone import ANCH, mark, mcallout, cam, underwater_close, pain_fx  # noqa: E402
import rig  # noqa: E402
from motion import Path  # noqa: E402
from mapdata import draw_world, world_proj  # noqa: E402

SNAIL_C = (0.93, 0.62, 0.30)
WAIST = FLOOR - 112  # água na cintura


# ------------------------------------------------------------------ peças reutilizáveis
def night_tint(ctx, k):
    if k > 0:
        rgba(ctx, (0.02, 0.05, 0.12), 0.55 * k)
        ctx.paint()


def sand_floor(ctx, t, floor, seed=4, rocks=True, night=0.0):
    ctx.rectangle(-W, floor, 3 * W, 2 * H)
    ink(ctx, (0.80, 0.74, 0.58), 1, 2)
    rnd = random.Random(seed)
    for i in range(70):
        circle(ctx, rnd.uniform(-W * 0.2, W * 1.2), floor + rnd.uniform(6, H - floor), rnd.uniform(1, 3),
               (0.62, 0.56, 0.44), 0.6)
    if rocks:
        for i in range(6):
            rock(ctx, rnd.uniform(-W * 0.1, W * 1.1), floor + 8, rnd.uniform(80, 150), 40 + i)


def glint(ctx, x, y, t, k=1.0):
    """Brilho (estrela de 4 pontas) piscando."""
    if k <= 0:
        return
    s = (10 + 6 * math.sin(t * 5)) * k
    for ang in (0, math.pi / 2):
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(ang + t * 0.5)
        ctx.move_to(-s * 2, 0)
        ctx.line_to(0, -s * 0.25)
        ctx.line_to(s * 2, 0)
        ctx.line_to(0, s * 0.25)
        ctx.close_path()
        rgba(ctx, WHITE, 0.8 * k)
        ctx.fill()
        ctx.restore()


def hand_close(ctx, x, y, s, a=1.0, curl=0.3, skin=SKIN, numb=0.0, tingle=0.0, t=0.0, from_dir=(-1.0, 0.6)):
    """Mão de perfil, palma para cima, desenhada a partir de referência: antebraço, punho, palma com
    almofada, quatro dedos separados (2 falanges visíveis, unhas) que curvam para cima com 'curl', e polegar
    do lado de perto. (x, y) = centro da palma; from_dir = direção de onde vem o antebraço."""
    col = tuple(lerp(c, g, numb * 0.5) for c, g in zip(skin, (0.70, 0.72, 0.80)))
    dark = tuple(c * 0.86 for c in col)
    fx, fy = from_dir
    L = math.hypot(fx, fy)
    fx, fy = fx / L, fy / L
    ang = math.atan2(-fy, -fx)  # a mão aponta para longe do antebraço
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    ctx.scale(s, s)
    # antebraço (afunila até o punho)
    ctx.move_to(-30, -16)
    ctx.line_to(-700, -34)
    ctx.line_to(-700, 34)
    ctx.line_to(-30, 18)
    ctx.close_path()
    rgba(ctx, col, a)
    ctx.fill()
    for yy0, yy1 in ((-16, -34), (18, 34)):
        ctx.move_to(-40, yy0)
        ctx.line_to(-700, yy1)
        rgba(ctx, INK, a)
        ctx.set_line_width(2.4)
        ctx.stroke()
    # dedos de trás (mais escuros, por trás da palma): 3 dedos
    for k in range(3):
        bx = 34 - k * 3
        c1 = (bx + 22, -6 - k * 2 - 20 * curl)
        c2 = (c1[0] + 18 - 14 * curl, c1[1] - 4 - 22 * curl)
        limb(ctx, [(bx, -4 - k * 3), c1, c2], 15 - k * 1.2, dark, a)
    # palma (com almofada da base dos dedos e do polegar)
    def palm_path():
        ctx.move_to(-46, -17)
        ctx.curve_to(-10, -24, 24, -22, 44, -14)
        ctx.curve_to(54, -10, 56, 6, 46, 15)
        ctx.curve_to(26, 23, -10, 25, -46, 19)

    palm_path()
    ctx.close_path()
    rgba(ctx, col, a)
    ctx.fill()
    palm_path()
    rgba(ctx, INK, a)
    ctx.set_line_width(2.4)
    ctx.stroke()
    ctx.move_to(-30, -6)
    ctx.curve_to(-6, -12, 18, -10, 38, -4)
    rgba(ctx, INK, 0.30 * a)
    ctx.set_line_width(1.3)
    ctx.stroke()
    # dedo da frente (indicador), com unha
    c1 = (64, -4 - 22 * curl)
    c2 = (c1[0] + 20 - 16 * curl, c1[1] - 4 - 24 * curl)
    limb(ctx, [(40, -2), c1, c2], 16, col, a)
    nx, ny = c2
    ctx.save()
    ctx.translate(nx, ny)
    ctx.rotate(math.atan2(c2[1] - c1[1], c2[0] - c1[0]))
    ellipse_path(ctx, -3, -3, 5, 3)
    ink(ctx, (0.96, 0.86, 0.80), a, 1.0)
    ctx.restore()
    # polegar (do lado de perto, sobe da base da palma)
    t1 = (4, -30)
    t2 = (26, -40 - 6 * curl)
    limb(ctx, [(-16, -12), t1, t2], 18, col, a)
    ctx.restore()
    if tingle > 0:
        rnd = random.Random(int(t * 12))
        for k in range(int(14 * tingle)):
            px, py = x + rnd.uniform(-60, 80) * s, y + rnd.uniform(-40, 25) * s
            circle(ctx, px, py, rnd.uniform(1.5, 3.5), (1, 0.9, 0.5), 0.9 * tingle)


def shell_in_hand(ctx, x, y, L, t, a=1.0, ang=-0.08, live=0.0, prob=0.0, prob_to=None):
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    cone_snail(ctx, 0, 0, L, t, a=a, shell_only=live <= 0, siphon=live, head=live, proboscis=prob,
               prob_to=None if prob_to is None else (prob_to[0] - x, prob_to[1] - y))
    ctx.restore()


def shore(ctx, t, sand_y=H * 0.70, sea_y=H * 0.52, dusk=0.0):
    g = cairo.LinearGradient(0, 0, 0, sea_y)
    g.add_color_stop_rgb(0, lerp(0.52, 0.42, dusk), lerp(0.66, 0.42, dusk), lerp(0.76, 0.55, dusk))
    g.add_color_stop_rgb(1, lerp(0.92, 0.95, dusk), lerp(0.86, 0.72, dusk), lerp(0.76, 0.58, dusk))
    ctx.set_source(g)
    ctx.rectangle(-W, -H, 3 * W, sea_y + H)
    ctx.fill()
    circle(ctx, W * 0.80, sea_y - 60 + 40 * dusk, 34, (1.0, 0.90, 0.70), 0.9)
    g = cairo.LinearGradient(0, sea_y, 0, sand_y)
    g.add_color_stop_rgb(0, 0.30, 0.55, 0.60)
    g.add_color_stop_rgb(1, 0.40, 0.70, 0.70)
    ctx.set_source(g)
    ctx.rectangle(-W, sea_y, 3 * W, sand_y - sea_y + 2)
    ctx.fill()
    for k in range(4):  # ondinhas chegando
        yy = sea_y + (sand_y - sea_y) * ((t * 0.12 + k / 4) % 1)
        ctx.move_to(-W, yy)
        for xx in range(-int(W), int(2 * W), 30):
            ctx.line_to(xx, yy + 2 * math.sin(xx * 0.02 + t + k))
        rgba(ctx, WHITE, 0.25)
        ctx.set_line_width(1.5)
        ctx.stroke()
    ctx.rectangle(-W, sand_y, 3 * W, 2 * H)
    ink(ctx, (0.86, 0.79, 0.62), 1, 2)
    rnd = random.Random(2)
    for i in range(60):
        circle(ctx, rnd.uniform(-W * 0.2, W * 1.2), sand_y + rnd.uniform(5, H - sand_y), rnd.uniform(1, 2.5),
               (0.70, 0.62, 0.46), 0.6)


def fishy(ctx, x, y, s, t, c=(0.95, 0.72, 0.30), a=1.0, flip=1, dizzy=0.0, stiff=0.0):
    """Peixe com estados: tonto (gira, balança) e paralisado (rígido, de lado)."""
    rot = dizzy * 0.5 * math.sin(t * 3) + stiff * 1.2
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(rot * flip)
    fish(ctx, 0, 0, s, t * (1 - stiff), c, a, flip, wiggle=0.04 * (1 - stiff))
    ctx.restore()
    if dizzy > 0:
        for k in range(3):
            ang = t * 3 + k * 2.1
            circle(ctx, x + math.cos(ang) * 30 * s, y - 34 * s + math.sin(ang) * 8 * s, 3, (1, 1, 0.6), 0.8 * dizzy)


# ================================================================== 0:00 – 0:14 o recife raso
def w_open(ctx, t):
    walk = Path([(-1, -80, 0), (9.5, W * 0.42, 0), (10.5, W * 0.46, 0)])
    cx = kf(t, [(0, W * 0.40), (14, W * 0.55)])
    cam(ctx, cx, H * 0.50, kf(t, [(0, 1.0), (10, 1.0), (14, 1.25)]))

    def mid(c):
        # a concha no fundo, brilhando
        cone_snail(c, W * 0.66, FLOOR + 4, 60, t, siphon=0, head=0, shell_only=True, bury=0.2)
        x, _ = walk.pos(t)
        wader(c, x, t, "swimmer", walk.facing(t), 1.2, walker_pose(walk, t, 70))

    def front(c):
        glint(c, W * 0.66, FLOOR - 10, t, window(t, 10, 15, 0.6))

    reef_scene(ctx, t, mid, front, surf=WAIST, xoff=t * 6)
    ctx.restore()


def u_open(ctx, t):
    kicker(ctx, "NORTE DA AUSTRÁLIA · MAREA BAIXA · MEIO DA TARDE".replace("MAREA", "MARÉ"), W / 2, H * 0.90, t,
           0.8, 9.5, 16, WHITE)
    label(ctx, "ÁGUA NA CINTURA", W / 2, H * 0.10, t, 4.5, 9.5, 22, WHITE)


# ================================================================== 0:14 – 0:24 a concha mais bonita
def w_find(ctx, t):
    underwater_close(ctx, t, floor=H * 0.80)
    z = kf(t, [(14, 1.0), (24, 1.35)])
    ctx.save()
    ctx.translate(W * 0.55, H * 0.78)
    ctx.scale(z, z)
    ctx.translate(-W * 0.55, -H * 0.78)
    cone_snail(ctx, W * 0.55, H * 0.80, 420, t, siphon=0, head=0, shell_only=True, seed=3)
    mark(ctx, "padrao", W * 0.52, H * 0.80 - 70, 60)
    glint(ctx, W * 0.48, H * 0.80 - 95, t, 0.8)
    glint(ctx, W * 0.62, H * 0.80 - 60, t + 1.3, 0.6)
    ctx.restore()
    # luz do sol ondulando
    for k in range(6):
        xx = W * (0.1 + k * 0.17) + 30 * math.sin(t * 0.4 + k)
        ctx.move_to(xx - 30, 0)
        ctx.line_to(xx + 30, 0)
        ctx.line_to(xx + 120, H)
        ctx.line_to(xx + 40, H)
        ctx.close_path()
        rgba(ctx, WHITE, 0.04 + 0.02 * math.sin(t * 1.5 + k))
        ctx.fill()


def u_find(ctx, t):
    label(ctx, "UMA DAS CONCHAS MAIS BONITAS QUE VOCÊ JÁ VIU", W / 2, H * 0.10, t, 17, 20.5, 22, WHITE)
    mcallout(ctx, "padrao", W * 0.78, H * 0.22, "MANCHAS MARRONS E BRANCAS, COMO UMA REDE", window(t, 20.3, 24.2))


# ================================================================== 0:24 – 0:40 pega a concha / picada
def w_pick(ctx, t):
    underwater_close(ctx, t, floor=H * 0.84)
    # a mão desce, pega e sobe com a concha (vista de lado)
    sx, sy = W * 0.50, H * 0.84
    reach = kf(t, [(24, 0.0), (26.5, 1.0), (28.5, 1.0), (31.5, 0.0)])
    hold = appear(t, 27.2, 0.4)
    hx = W * 0.50
    hy = lerp(-120, sy - 30, reach) if t < 28.5 else lerp(H * 0.45, sy - 30, reach)
    if t < 32:
        if hold < 1 or t < 28.5:
            cone_snail(ctx, sx + 0, sy if t < 27.4 else hy + 6, 150, t, siphon=0, head=0, shell_only=True)
        hand_close(ctx, hx - 20, hy + 10, 1.25, curl=0.2 + 0.5 * hold, from_dir=(-0.5, -1.0))
        if t >= 27.4:
            cone_snail(ctx, hx, hy + 6, 150, t, siphon=0, head=0, shell_only=True)
        bubbles(ctx, hx, hy - 40, t, n=6, rise=200, a=0.6, seed=2)
        return
    # close: concha na palma; a tromba sai pela ponta e pica
    studio(ctx, t, H * 0.95)
    hx, hy = W * 0.42, H * 0.58
    hand_close(ctx, hx, hy, 2.4, curl=0.35, tingle=0, t=t)
    prob = kf(t, [(32.0, 0.0), (33.0, 0.0), (34.0, 1.0), (35.2, 1.0), (36.0, 0.0)])
    tip = (hx + 40, hy - 64)
    shell_in_hand(ctx, hx - 10, hy - 52, 330, t, live=appear(t, 32.2, 0.8), prob=prob, prob_to=tip)
    mark(ctx, "picada", *tip, 20)
    if t > 34.0:
        k = appear(t, 34.0, 0.3)
        circle(ctx, tip[0], tip[1] + 6, 5 * k, RED, 0.9)


def u_pick(ctx, t):
    label(ctx, "MAIS PESADA DO QUE PARECE", W / 2, H * 0.10, t, 30, 32, 22, WHITE)
    mcallout(ctx, "picada", W * 0.72, H * 0.20, "UMA PICADINHA, COMO UMA FARPA", window(t, 33.8, 37.2))
    big_title(ctx, [("QUASE NÃO ", WHITE, "black"), ("DÓI", ORANGE, "light")], W * 0.74, H * 0.40, t, 37.2, None, 40)
    label(ctx, "E ESSE É O PROBLEMA", W * 0.74, H * 0.50, t, 38.6, None, 22, RED)


# ================================================================== 0:40 – 1:10 os sintomas
SYM = [(40.0, "FORMIGAMENTO NA MÃO"), (44.0, "DORMÊNCIA"), (46.0, "SOBE PELO BRAÇO"), (48.0, "BOCA E LÁBIOS"),
       (50.0, "VISÃO EMBAÇADA"), (52.0, "VISÃO DUPLA"), (55.0, "FALA"), (56.5, "ENGOLIR"), (58.0, "RESPIRAR")]


def w_sym(ctx, t):
    studio(ctx, t, H * 0.90)
    if t < 61:
        # pessoa em pé; o formigamento sobe da mão ao rosto; visão dupla = imagem dobrada
        sway = 3 * math.sin(t * 1.3) * appear(t, 52, 2)
        p = rig.blend(rig.p_stand(t), rig.pose(lean=6 + sway, armF=30, elbowF=60, armB=-6, neck=10), appear(t, 40.5, 1))
        x = W * 0.34
        dbl = appear(t, 52, 1.5) * (1 - appear(t, 60.5, 0.5))
        if dbl > 0:
            rig.figure(ctx, x + 18 * dbl + 6 * math.sin(t * 2), H * 0.90, 2.2, p, outfit="swimmer", a=0.35 * dbl, t=t,
                       shadow=False)
        rig.figure(ctx, x, H * 0.90, 2.2, p, outfit="swimmer", t=t)
        pts = rig.world_points(x, H * 0.90, 2.2, p, 1)
        path = [pts["handF"], pts["wristF"], pts["elbowF"], pts["shoulder"], pts["head"]]
        k = clamp((t - 40) / 10)  # o formigamento sobe
        for i, (px, py) in enumerate(path):
            f = clamp(k * 4 - i)
            if f > 0:
                rnd = random.Random(int(t * 10) + i)
                for j in range(8):
                    circle(ctx, px + rnd.uniform(-18, 18), py + rnd.uniform(-18, 18), rnd.uniform(1.5, 3),
                           (1, 0.88, 0.45), 0.9 * f)
        mark(ctx, "boca", pts["head"][0] + 22, pts["head"][1] + 12, 16)
        # respirar: peito sobe e desce cada vez menos
        if t > 58:
            br = 1 - appear(t, 58, 2.5)
            cx_, cy_ = pts["shoulder"][0] + 10, pts["shoulder"][1] + 40
            ellipse_path(ctx, cx_, cy_, 30 + 6 * br * math.sin(t * 4), 20)
            rgba(ctx, (0.55, 0.80, 0.95), 0.25)
            ctx.fill()
        if 50 <= t < 52.2:  # embaçado: véu
            rgba(ctx, (0.85, 0.88, 0.90), 0.25 * window(t, 50, 52.2))
            ctx.paint()
        return
    # 1:01 – 1:10 acordado, sem conseguir se mexer
    x = W * 0.30
    rig.figure(ctx, x, H * 0.80, 2.2, rig.p_lie(t), outfit="swimmer", t=t)
    hp = rig.head_point(x, H * 0.80, 2.2, rig.p_lie(t))
    # olho aberto piscando devagar + ondas de som chegando no ouvido
    blink = 1 if (t % 3.0) > 0.15 else 0.2
    ellipse_path(ctx, hp[0] + 4, hp[1] - 10, 7, 5 * blink)
    ink(ctx, WHITE, 1, 1.5)
    circle(ctx, hp[0] + 5, hp[1] - 10, 2.5 * blink, INK)
    for k in range(4):
        ph = (t * 0.6 + k / 4) % 1
        ctx.arc(hp[0] - 10, hp[1], 30 + ph * 220, -0.6 - math.pi / 2, 0.6 - math.pi / 2)
        rgba(ctx, WHITE, 0.4 * (1 - ph) * appear(t, 66, 0.5))
        ctx.set_line_width(2)
        ctx.stroke()
    # tentativa de mexer a mão: tremor mínimo
    hpnt = rig.hand_point(x, H * 0.80, 2.2, rig.p_lie(t))
    if t > 68:
        circle(ctx, hpnt[0], hpnt[1], 12 + 2 * math.sin(t * 20), RED, 0.25)


def u_sym(ctx, t):
    if t < 61:
        y0 = H * 0.16
        for i, (t0, s) in enumerate(SYM):
            if t >= t0:
                a = appear(t, t0, 0.4)
                text(ctx, s, W * 0.70, y0 + i * 44, 20 if i < 8 else 24, RED if i == 8 else WHITE, a, "l", "black",
                     sp=1.5)
        mcallout(ctx, "boca", W * 0.56, H * 0.50, "LÁBIOS FORMIGANDO", window(t, 48.0, 50.2))
        if t > 55 and t < 56.6:
            text(ctx, "S-SO-COR...", W * 0.40, H * 0.12, 26, WHITE, window(t, 55, 56.6), "c", "black")
        return
    label(ctx, "ACORDADO", W * 0.70, H * 0.30, t, 63, None, 40, WHITE)
    label(ctx, "OUVINDO TUDO", W * 0.70, H * 0.40, t, 66, None, 24, ORANGE)
    label(ctx, "SEM CONSEGUIR SE MEXER", W * 0.70, H * 0.48, t, 68, None, 22, RED)


# ================================================================== 1:10 – 1:17 a concha não estava vazia
def w_xray(ctx, t):
    studio(ctx, t, H * 0.92)
    z = kf(t, [(70, 1.0), (77, 1.15)])
    ctx.save()
    ctx.translate(W / 2, H * 0.70)
    ctx.scale(z, z)
    ctx.translate(-W / 2, -H * 0.70)
    xr = appear(t, 70.6, 1.2) * (1 - appear(t, 73.6, 0.6))
    live = appear(t, 72.4, 1.0)
    fire = kf(t, [(73.8, 0.0), (74.3, 1.0), (76.2, 1.0), (77, 0.6)])
    cone_snail(ctx, W * 0.45, H * 0.82, 560, t, siphon=live, head=live, xray=xr, proboscis=fire,
               prob_to=(W * 0.92, H * 0.55))
    ctx.restore()
    if 74.0 < t < 74.5:
        rgba(ctx, WHITE, 0.5 * (1 - (t - 74.0) / 0.5))
        ctx.paint()


def u_xray(ctx, t):
    label(ctx, "A CONCHA NÃO ESTAVA VAZIA", W / 2, H * 0.10, t, 70.2, 74, 26, WHITE)
    big_title(ctx, [("ELE TE ", WHITE, "black"), ("ARPOOU", RED, "light")], W / 2, H * 0.14, t, 74.2, None, 44)


# ================================================================== 1:17 – 1:53 nome e promessa
def w_name(ctx, t):
    if t < 92:
        underwater_close(ctx, t, floor=H * 0.82)
        night_tint(ctx, 0.35)
        x = kf(t, [(77, W * 0.30), (92, W * 0.40)])  # bem devagar
        cone_snail(ctx, x, H * 0.84, 520, t, crawl=1.0, seed=3)
        if t > 88.5:  # um peixe passa — e mesmo assim ele caça
            fx = kf(t, [(88.5, W * 1.1), (92, W * 0.70)])
            fishy(ctx, fx, H * 0.55, 0.9, t, flip=-1)
        return
    underwater_close(ctx, t, floor=H * 0.86)
    rgba(ctx, (0.02, 0.06, 0.08), 0.55)
    ctx.paint()


PROM = [("CAÇA PEIXES MAIS RÁPIDOS", 92.6), ("NENHUM LADO SEGURO", 98.0), ("UM AMIGO PICADO", 101.4),
        ("VENENO QUE VIROU REMÉDIO", 104.2)]


def u_name(ctx, t):
    if t < 92:
        if t < 83.2:
            name_tag(ctx, "Conus geographus", 40, 60, t, 77.6, None, 28)
            big_title(ctx, [("CARAMUJO-", WHITE, "black"), ("CONE", ORANGE, "light")], W / 2, H * 0.16, t, 77.4, None,
                      60)
            kicker(ctx, "UM DOS ANIMAIS MAIS VENENOSOS DO PLANETA", W / 2, H * 0.22, t, 80.0, None, 18, WHITE)
            return
        for i, (s, t0, ic) in enumerate([("LENTO", 84.3, "snail"), ("OLHOS RUINS", 85.9, "eye"),
                                          ("NÃO NADA", 87.2, "x"), ("NÃO CORRE", 88.0, "x")]):
            a = window(t, t0, 89.2)
            x = W * 0.20 + i * 260
            text(ctx, s, x + 60, H * 0.14, 22, WHITE, a, "c", "black", sp=1.5)
        label(ctx, "MESMO ASSIM, ELE CAÇA PEIXES", W / 2, H * 0.14, t, 89.4, None, 26, ORANGE)
        return
    for i, (s, t0) in enumerate(PROM):
        a = window(t, t0, 108.6)
        x = W / 2 + (i - 1.5) * 290
        card(ctx, x - 130, H * 0.30, 260, 120, a)
        text(ctx, str(i + 1), x, H * 0.30 + 45, 28, ORANGE, a, "c", "black")
        text(ctx, s, x, H * 0.30 + 88, 15, WHITE, a, "c", "black", sp=1)
    kicker(ctx, "POR QUE VOCÊ NUNCA IA QUERER PEGAR A CONCHA DE UM", W / 2, H * 0.42, t, 109, None, 19)
    big_title(ctx, [("CARAMUJO-", WHITE, "black"), ("CONE", ORANGE, "light")], W / 2, H * 0.42 + 75, t, 109.4, None,
              72)


# ================================================================== 1:53 – 2:25 o que ele é
def w_what(ctx, t):
    if t < 119:
        underwater_close(ctx, t, floor=H * 0.80)
        # centenas de espécies: conchas variadas entrando uma a uma
        for i in range(7):
            a = appear(t, 116 + i * 0.3, 0.4)
            if a > 0:
                x = W * 0.10 + i * W * 0.135
                y = H * 0.80 - 20 * (1 - a)
                cone_snail(ctx, x, y, 150 + (i % 3) * 30, t, shell_only=True, seed=10 + i * 3, a=a)
        return
    if t < 127:  # mapa: Indo-Pacífico
        studio(ctx, t, H * 0.95)
        draw_world(ctx, W * 0.05, H * 0.12, W * 0.90, H * 0.76)
        proj = world_proj(W * 0.05, H * 0.12, W * 0.90, H * 0.76)
        k = appear(t, 120, 1.5)
        # faixa do Indo-Pacífico: do Mar Vermelho (~35E, 20N) até a Austrália (~150E, -25)
        for lon in range(35, 185, 6):
            lat = 18 - (lon - 35) * 0.28
            x, y = proj(lon, lat)
            circle(ctx, x, y, 30 * k, ORANGE, 0.22 * k * (0.7 + 0.3 * math.sin(t * 3 + lon)))
        for lon, lat, key in ((38, 21, "mv"), (145, -18, "aus")):
            x, y = proj(lon, lat)
            mark(ctx, key, x, y, 14)
        return
    if t < 137:  # o geográfico: concha "mapa antigo", 10–15 cm
        underwater_close(ctx, t, floor=H * 0.80)
        cone_snail(ctx, W * 0.50, H * 0.82, 600, t, crawl=0.4, seed=3)
        a, b = cone_point(W * 0.50, H * 0.82, 600, -0.375, 0), cone_point(W * 0.50, H * 0.82, 600, 0.315, 0)
        ANCH["regua"] = (ctx.user_to_device(a[0], H * 0.90), ctx.user_to_device(b[0], H * 0.90))
        mark(ctx, "concha", *cone_point(W * 0.50, H * 0.82, 600, -0.02, 0.21), 90)
        return
    # de dia enterrado / escondido; à noite sai
    underwater_close(ctx, t, floor=H * 0.82)
    nt = appear(t, 142.6, 1.5)
    night_tint(ctx, nt)
    bury = 1 - appear(t, 142.8, 1.6)
    x = kf(t, [(142.8, W * 0.45), (145.5, W * 0.50)])
    cone_snail(ctx, x, H * 0.84, 420, t, crawl=nt, bury=bury * 0.9, siphon=0.4 + 0.6 * nt, seed=3)
    if nt > 0:
        circle(ctx, W * 0.85, H * 0.12, 26, (0.95, 0.95, 0.85), 0.8 * nt)


def u_what(ctx, t):
    label(ctx, "O QUE ELE É?", W / 2, H * 0.10, t, 113.3, 116, 36, ORANGE)
    label(ctx, "CENTENAS DE ESPÉCIES", W / 2, H * 0.10, t, 116, 119, 26, WHITE)
    if 119 <= t < 127:
        kicker(ctx, "MARES QUENTES · OS MAIS PERIGOSOS NO INDO-PACÍFICO", W / 2, H * 0.08, t, 119.3, None, 16, WHITE)
        mcallout(ctx, "mv", W * 0.30, H * 0.20, "MAR VERMELHO", window(t, 123.2, 127.2))
        mcallout(ctx, "aus", W * 0.70, H * 0.86, "AUSTRÁLIA", window(t, 124.2, 127.2))
    if 127 <= t < 137:
        big_title(ctx, [("CARAMUJO-CONE ", WHITE, "black"), ("GEOGRÁFICO", ORANGE, "light")], W / 2, H * 0.12, t, 127.3,
                  None, 34)
        kicker(ctx, "O MAIS PERIGOSO DE TODOS", W / 2, H * 0.18, t, 128.0, None, 16, WHITE)
        if 131 < t < 137.2 and "regua" in ANCH:
            (ax, ay), (bx, by) = [ctx.device_to_user(*q) for q in ANCH["regua"]]
            scale_bar(ctx, ax, bx, ay, (t - 131.2) / 0.8, "10–15 CM")
        mcallout(ctx, "concha", W * 0.80, H * 0.30, "PARECE UM MAPA ANTIGO", window(t, 133.6, 137.2))
    label(ctx, "DE DIA: ENTERRADO OU ESCONDIDO", W / 2, H * 0.10, t, 137.4, 142.6, 22, WHITE)
    label(ctx, "À NOITE, ELE SAI PARA CAÇAR", W / 2, H * 0.10, t, 142.8, None, 24, ORANGE)


# ================================================================== 2:25 – 2:35 mais devagar que você
def w_slow(ctx, t):
    """Comparação de velocidade em duas faixas (física correta: a pessoa anda no chão seco,
    o caramujo rasteja no fundo do mar), as duas ao mesmo tempo."""
    studio(ctx, t, H * 0.95)
    # faixa de cima: pessoa andando na areia
    g1 = H * 0.44
    ctx.rectangle(0, g1, W, 8)
    rgba(ctx, (0.80, 0.74, 0.58), 0.9)
    ctx.fill()
    walk = Path([(145.5, -60, 0), (153.5, W * 1.08, 0)])
    if 145.5 < t < 153.5:
        x, _ = walk.pos(t)
        rig.figure(ctx, x, g1, 1.25, walker_pose(walk, t, 70), outfit="swimmer", facing=1, t=t)
    # faixa de baixo: fundo do mar, o caramujo rastejando
    g2 = H * 0.86
    ctx.rectangle(0, H * 0.52, W, g2 - H * 0.52)
    rgba(ctx, (0.18, 0.40, 0.42), 0.9)
    ctx.fill()
    ctx.rectangle(0, g2, W, H - g2)
    rgba(ctx, (0.62, 0.58, 0.46), 1)
    ctx.fill()
    x = kf(t, [(145, W * 0.12), (155, W * 0.16)])
    cone_snail(ctx, x, g2, 240, t, crawl=1.0, seed=3)
    for k in range(2):
        text(ctx, ("VOCÊ ANDANDO", "CARAMUJO-CONE")[k], W * 0.03, (H * 0.10, H * 0.58)[k], 16, WHITE,
             appear(t, 146), "l", "black", sp=1.5)
    if t > 152.3:
        fx = kf(t, [(152.3, W * 1.1), (155, W * 0.70)])
        fishy(ctx, fx, H * 0.68, 0.9, t, flip=-1)


def u_slow(ctx, t):
    label(ctx, "MAIS DEVAGAR DO QUE VOCÊ ANDA", W / 2, H * 0.06, t, 148, 152.3, 24, WHITE)
    label(ctx, "MAS ELE COME PEIXES", W / 2, H * 0.06, t, 152.3, None, 28, ORANGE)


# ================================================================== 2:35 – 2:55 a arma: dentes-arpão
def w_weapon(ctx, t):
    studio(ctx, t, H * 0.92)
    if t < 164:  # raio-x: o saco de dentes dentro da boca
        cone_snail(ctx, W * 0.42, H * 0.86, 640, t, xray=appear(t, 156.5, 1.0), seed=3)
        mark(ctx, "dentes", *cone_point(W * 0.42, H * 0.86, 640, 0.20, 0.125), 50)
        # dentes saindo do saco e aparecendo em destaque à direita
        k = appear(t, 159, 1.2)
        for i in range(5):
            harpoon_tooth(ctx, W * 0.80, H * 0.20 + i * 55, 140 * k, -0.15 + 0.06 * i, k, detail=True)
        return
    if t < 167:  # parece uma agulha de injeção
        k = appear(t, 164.2, 0.6)
        harpoon_tooth(ctx, W * 0.50, H * 0.40, 520, 0, 1, detail=True)
        # seringa comparada
        x0, y0 = W * 0.22, H * 0.70
        rrect(ctx, x0, y0 - 22, 360 * k, 44, 8)
        ink(ctx, (0.90, 0.94, 0.96), 0.9 * k, 2)
        line(ctx, x0 + 360 * k, y0, x0 + 360 * k + 200 * k, y0, (0.80, 0.82, 0.84), k, 4)
        mark(ctx, "farpa", W * 0.50 + 520 * 0.18, H * 0.40 - 520 * 0.12, 26)
        mark(ctx, "oco", W * 0.50 - 520 * 0.2, H * 0.40, 26)
        return
    # carrega o dente na ponta da tromba
    cone_snail(ctx, W * 0.36, H * 0.86, 560, t, proboscis=0.55, prob_to=(W * 0.80, H * 0.55), harpoon=False, seed=3)
    load = appear(t, 168.5, 2.5)
    hx_, hy_ = cone_point(W * 0.36, H * 0.86, 560, 0.37, 0.05)
    mx, my = hx_ + (W * 0.80 - hx_) * 0.55, hy_ + (H * 0.55 - hy_) * 0.55
    tx, ty = lerp(hx_, mx, load), lerp(hy_, my, load)
    harpoon_tooth(ctx, tx, ty, 50, math.atan2(H * 0.55 - hy_, W * 0.80 - hx_), 1)
    mark(ctx, "ponta", tx, ty, 30)


def u_weapon(ctx, t):
    label(ctx, "COMO?", W / 2, H * 0.10, t, 154.2, 155.6, 40, WHITE)
    label(ctx, "ELE TEM UMA ARMA", W / 2, H * 0.10, t, 155.6, 157.4, 30, ORANGE)
    mcallout(ctx, "dentes", W * 0.30, H * 0.16, "DENTES OCOS, FINOS, COM FARPAS", window(t, 157.6, 163.8))
    mcallout(ctx, "farpa", W * 0.78, H * 0.16, "FARPA", window(t, 164.3, 167.2))
    mcallout(ctx, "oco", W * 0.24, H * 0.16, "OCO, COMO UMA AGULHA DE INJEÇÃO", window(t, 164.6, 167.2))
    mcallout(ctx, "ponta", W * 0.82, H * 0.20, "DENTE NA PONTA DA TROMBA", window(t, 169.5, 175.2))
    label(ctx, "COMO UM ARPÃO CARREGADO", W / 2, H * 0.10, t, 172.0, 175.2, 24, ORANGE)


# ================================================================== 2:55 – 3:23 a caçada
def w_hunt(ctx, t):
    underwater_close(ctx, t, floor=H * 0.84)
    night_tint(ctx, 0.55)
    sx, gy, L = W * 0.30, H * 0.86, 520
    fish_x, fish_y = W * 0.74, H * 0.56
    hit_t = 180.6
    stiff = appear(t, 191.0, 1.5)
    # o peixe: nadando no lugar; depois do arpão fica rígido; depois é puxado para a boca
    pull = appear(t, 197.5, 2.0)
    hx_, hy_ = cone_point(sx, gy, L, 0.42, 0.06)
    fx = lerp(fish_x + 6 * math.sin(t * 2) * (1 - stiff), hx_ + 40, ease(pull))
    fy = lerp(fish_y + 4 * math.sin(t * 1.7) * (1 - stiff), hy_ - 20, ease(pull))
    mouth = appear(t, 197.0, 1.0) * (1 - appear(t, 201.5, 1.0))
    # tromba: estica devagar (175–179), dispara (180.6), fica presa no peixe
    if t < 179.5:
        prob = kf(t, [(175.0, 0.0), (179.5, 0.80)])
        to = (fx, fy)
    elif t < hit_t:
        prob = 0.80
        to = (fx, fy)
    else:
        prob = 1.0 if pull < 0.95 else 0.0
        to = (fx - 10, fy)
    if mouth > 0.9:
        prob = 0.0
    cone_snail(ctx, sx, gy, L, t, crawl=0.0, proboscis=prob, prob_to=to, mouth=mouth, seed=3)
    if pull < 0.97:
        fishy(ctx, fx, fy, 1.2, t, flip=-1, stiff=stiff)
    mark(ctx, "peixe", fx, fy, 50)
    # veneno entrando
    if 186 < t < 192:
        for k in range(8):
            ph = (t * 1.5 + k / 8) % 1
            circle(ctx, lerp(hx_, fx, ph), lerp(hy_, fy, ph) - 30 * math.sin(ph * math.pi), 4, (0.55, 0.95, 0.35),
                   0.9 * window(t, 186, 192))
    if hit_t <= t < hit_t + 0.35:
        rgba(ctx, WHITE, 0.6 * (1 - (t - hit_t) / 0.35))
        ctx.paint()


def u_hunt(ctx, t):
    label(ctx, "ESTICA A TROMBA DEVAGAR", W / 2, H * 0.10, t, 175.2, 179.2, 22, WHITE)
    big_title(ctx, [("DISPARA", RED, "black")], W / 2, H * 0.14, t, 179.2, 181.0, 56)
    if 181 < t < 188:
        text(ctx, "MENOS DE 1 MILÉSIMO DE SEGUNDO", W / 2, H * 0.10, 22, ORANGE, window(t, 181, 188), "c", "black",
             sp=1.5)
        text(ctx, "UM DOS MOVIMENTOS MAIS RÁPIDOS DO REINO ANIMAL", W / 2, H * 0.94, 18, WHITE,
             window(t, 185.2, 188), "c", "semi", sp=1.2)
    mcallout(ctx, "peixe", W * 0.80, H * 0.22, "VENENO INJETADO PELO DENTE OCO", window(t, 188.2, 192.2))
    mcallout(ctx, "peixe", W * 0.80, H * 0.22, "PARALISADO QUASE NA HORA", window(t, 192.3, 197.2))
    label(ctx, "A BOCA SE ABRE COMO UMA REDE", W / 2, H * 0.10, t, 197.4, 203.0, 24, WHITE)


# ================================================================== 3:23 – 3:43 a nuvem de insulina
def w_insulin(ctx, t):
    underwater_close(ctx, t, floor=H * 0.84)
    night_tint(ctx, 0.55)
    sx, gy, L = W * 0.28, H * 0.86, 460
    cloud = appear(t, 206.0, 3.0)
    mouth = appear(t, 218.2, 0.8)
    cone_snail(ctx, sx, gy, L, t, mouth=mouth, seed=3)
    hx_, hy_ = cone_point(sx, gy, L, 0.42, 0.06)
    if cloud > 0:
        insulin_cloud(ctx, W * 0.60, H * 0.55, 260 * cloud, t, a=1 - 0.5 * appear(t, 219, 3))
    mark(ctx, "nuvem", W * 0.60, H * 0.52, 80)
    dz = appear(t, 212.0, 2.0)
    for i in range(6):
        base = (W * 0.50 + (i % 3) * 120, H * 0.42 + (i // 3) * 110)
        eaten = appear(t, 218.6 + i * 0.6, 0.6)
        if eaten >= 1:
            continue
        sp = 1 - 0.85 * dz
        x = base[0] + 30 * math.sin(t * 1.2 * sp + i) - 20
        y = base[1] + 10 * math.sin(t * 2 * sp + i * 2)
        x, y = lerp(x, hx_ + 40, ease(eaten)), lerp(y, hy_ - 20, ease(eaten))
        fishy(ctx, x, y, 0.8, t * sp + i, c=[(0.95, 0.72, 0.30), (0.50, 0.72, 0.90)][i % 2], flip=-1, dizzy=dz)


def u_insulin(ctx, t):
    label(ctx, "MAIS UM TRUQUE", W / 2, H * 0.10, t, 203.3, 206.0, 26, ORANGE)
    mcallout(ctx, "nuvem", W * 0.84, H * 0.16, "UMA NUVEM DE INSULINA", window(t, 206.2, 212.0))
    label(ctx, "QUEDA BRUSCA DE AÇÚCAR NO SANGUE", W / 2, H * 0.10, t, 212.0, 216.0, 22, WHITE)
    label(ctx, "LENTOS, TONTOS", W / 2, H * 0.10, t, 216.0, 218.4, 26, ORANGE)
    label(ctx, "UM POR UM", W / 2, H * 0.10, t, 218.6, None, 26, RED)


# ================================================================== 3:43 – 4:06 não existe lado seguro
def w_reach(ctx, t):
    studio(ctx, t, H * 0.92)
    if t < 235:
        # a tromba se estica e se dobra em volta da concha: alcança a frente, o meio e a parte de trás
        sx, gy, L = W * 0.50, H * 0.74, 560
        targets = [(cone_point(sx, gy, L, 0.30, 0.30)), (cone_point(sx, gy, L, 0.0, 0.40)),
                   (cone_point(sx, gy, L, -0.33, 0.33))]
        ph = clamp((t - 226) / 9)
        idx = min(2, int(ph * 3))
        k = (ph * 3) % 1 if ph < 1 else 1
        prob = math.sin(k * math.pi) if ph < 1 else 0.6
        cone_snail(ctx, sx, gy, L, t, proboscis=prob * appear(t, 226, 0.5), prob_to=targets[idx], seed=3)
        for i, (px, py) in enumerate(targets):
            if ph * 3 > i + 0.5:
                xmark(ctx, px, py - 20, 18, 1)
        return
    if t < 242:
        # mão segurando pela parte de trás: a tromba alcança a palma
        hx, hy = W * 0.38, H * 0.62
        hand_close(ctx, hx, hy, 2.2, curl=0.4)
        prob = kf(t, [(235.5, 0.0), (238.5, 1.0), (240.5, 1.0), (241.5, 0.4)])
        tip = (hx + 30, hy - 50)
        shell_in_hand(ctx, hx - 20, hy - 46, 320, t, live=1, prob=prob, prob_to=tip)
        mark(ctx, "mao", *tip, 24)
        return
    # camadas: luva fina, roupa de mergulho, pele — o arpão atravessa
    layers = [("LUVA FINA", (0.62, 0.66, 0.70)), ("ROUPA DE MERGULHO", (0.30, 0.34, 0.40)), ("PELE", SKIN)]
    for i, (_, c) in enumerate(layers):
        ctx.rectangle(W * 0.30, H * 0.30 + i * 70, W * 0.40, 60)
        ink(ctx, c, 1, 2)
    ty = kf(t, [(242, H * 0.05), (243.0, H * 0.30 + 3 * 70 + 10)])
    harpoon_tooth(ctx, W * 0.50, ty, 160, math.pi / 2, 1)
    for i in range(3):
        mark(ctx, "c%d" % i, W * 0.70, H * 0.30 + i * 70 + 30, 1)


def u_reach(ctx, t):
    label(ctx, "A PARTE QUE IMPORTA PARA VOCÊ", W / 2, H * 0.10, t, 223.3, 226.0, 24, ORANGE)
    label(ctx, "A TROMBA SE DOBRA EM VOLTA DA CONCHA", W / 2, H * 0.10, t, 226.0, 232.0, 22, WHITE)
    big_title(ctx, [("NENHUM LADO ", WHITE, "black"), ("SEGURO", RED, "light")], W / 2, H * 0.12, t, 232.2, 235.0, 40)
    if 232 < t < 235:
        for i, s in enumerate(("PONTA", "MEIO", "TRÁS")):
            text(ctx, s, W * (0.30 + i * 0.20), H * 0.94, 20, WHITE, appear(t, 232.4 + i * 0.9), "c", "black", sp=1.5)
    mcallout(ctx, "mao", W * 0.74, H * 0.20, "ELA ALCANÇA A SUA MÃO", window(t, 238.6, 242.0))
    if t >= 242:
        for i, s in enumerate(("LUVA FINA", "ROUPA DE MERGULHO", "PELE")):
            text(ctx, s, W * 0.72, H * 0.30 + i * 70 + 38, 18, WHITE, appear(t, 242.2 + i * 1.1), "l", "black",
                 sp=1.2)


# ================================================================== 4:06 – 4:57 o veneno
def lungs(ctx, cx, cy, s, breath, a=1.0, stop=0.0):
    """Pulmões + diafragma (vista de frente). breath 0..1 = expansão."""
    for sgn in (-1, 1):
        ctx.save()
        ctx.translate(cx + sgn * 48 * s, cy)
        ctx.scale(1 + 0.10 * breath, 1 + 0.12 * breath)
        blob(ctx, 0, 0, 42 * s, 78 * s, 5 + sgn, amp=0.06)
        ink(ctx, (0.88, 0.55, 0.58), a, 2.2)
        ctx.restore()
    line(ctx, cx, cy - 110 * s, cx, cy - 40 * s, (0.92, 0.88, 0.86), a, 10 * s)
    # diafragma: abaixa na inspiração
    dy = 22 * s * breath
    ctx.move_to(cx - 110 * s, cy + 80 * s + dy)
    ctx.curve_to(cx - 60 * s, cy + 40 * s + dy, cx + 60 * s, cy + 40 * s + dy, cx + 110 * s, cy + 80 * s + dy)
    rgba(ctx, (0.75, 0.30, 0.30) if stop < 0.5 else (0.50, 0.50, 0.55), a)
    ctx.set_line_width(8 * s)
    ctx.stroke()


def w_venom(ctx, t):
    studio(ctx, t, H * 0.92)
    rnd = random.Random(4)
    if t < 256:  # mistura de centenas de conotoxinas
        k = appear(t, 248.5, 1.5)
        cols = [(0.55, 0.95, 0.35), (0.95, 0.75, 0.30), (0.45, 0.75, 0.95), (0.95, 0.45, 0.55), (0.80, 0.60, 0.95)]
        for i in range(160):
            ang = rnd.uniform(0, 2 * math.pi) + t * rnd.uniform(0.05, 0.25)
            r = rnd.uniform(20, 300) * k
            x, y = W * 0.50 + math.cos(ang) * r, H * 0.52 + math.sin(ang) * r * 0.6
            shp = i % 3
            c = cols[i % 5]
            if shp == 0:
                circle(ctx, x, y, 5, c, 0.9 * k)
            elif shp == 1:
                line(ctx, x - 6, y, x + 6, y + 4, c, 0.9 * k, 4)
            else:
                rrect(ctx, x - 4, y - 4, 8, 8, 2)
                rgba(ctx, c, 0.9 * k)
                ctx.fill()
        return
    if t < 261:  # junção nervo–músculo: sinais passando e sendo bloqueados
        nx, ny = W * 0.30, H * 0.50
        limb(ctx, [(W * 0.02, ny - 40), (nx, ny)], 26, (0.95, 0.85, 0.55))
        circle(ctx, nx + 20, ny, 34, (0.95, 0.85, 0.55))
        ctx.rectangle(nx + 70, ny - 120, W * 0.50, 240)
        ink(ctx, (0.82, 0.42, 0.42), 1, 2)
        for i in range(7):
            line(ctx, nx + 80, ny - 100 + i * 33, nx + 70 + W * 0.50 - 10, ny - 100 + i * 33, (0.65, 0.30, 0.32), 0.6, 2)
        block = appear(t, 258.2, 1.5)
        for k in range(10):
            ph = (t * 1.2 + k / 10) % 1
            x = lerp(W * 0.02, nx + 60, ph)
            if x > nx + 40 and block > 0.5:
                continue
            circle(ctx, x, lerp(ny - 40, ny, ph), 6, YELLOW, 0.9)
        for k in range(6):  # toxinas encaixando nos receptores
            y = ny - 50 + k * 20
            x = lerp(W * 0.70, nx + 64, appear(t, 257 + k * 0.25, 0.8))
            circle(ctx, x, y, 7, (0.55, 0.95, 0.35), 0.95)
        mark(ctx, "juncao", nx + 60, ny, 40)
        return
    if t < 266:  # cérebro -> corpo: fios cortados um por um
        x, gy = W * 0.40, H * 0.90
        p = rig.p_stand(t)
        rig.figure(ctx, x, gy, 2.4, p, outfit="swimmer", t=t)
        pts = rig.world_points(x, gy, 2.4, p, 1)
        brain = (pts["head"][0], pts["head"][1] - 8)
        targets = [pts["handF"], pts["handB"], pts["ankleF"], pts["ankleB"], pts["shoulder"], pts["hip"]]
        for i, q in enumerate(targets):
            cut = appear(t, 261.6 + i * 0.6, 0.3)
            mx, my = (brain[0] + q[0]) / 2 + 60, (brain[1] + q[1]) / 2
            if cut < 1:
                ctx.move_to(*brain)
                ctx.curve_to(mx, my, mx, my, *q)
                rgba(ctx, YELLOW, 0.9)
                ctx.set_line_width(2.5)
                ctx.stroke()
                ph = (t * 1.5 + i * 0.2) % 1
                circle(ctx, lerp(brain[0], q[0], ph) + 60 * math.sin(ph * math.pi) * 0.5,
                       lerp(brain[1], q[1], ph), 4, WHITE, 0.9)
            else:
                xmark(ctx, mx - 30, my, 12, 1)
        return
    if t < 278:  # quase não dói; sintomas
        x, gy = W * 0.30, H * 0.90
        p = rig.blend(rig.p_stand(t), rig.pose(lean=8, armF=20, elbowF=40, neck=12), appear(t, 271, 2))
        rig.figure(ctx, x, gy, 2.2, p, outfit="swimmer", t=t)
        # medidor de dor (quase vazio)
        mx_, my_ = W * 0.70, H * 0.40
        rrect(ctx, mx_ - 160, my_ - 18, 320, 36, 18)
        ink(ctx, (0.10, 0.18, 0.20), window(t, 266.2, 271.2), 2)
        rrect(ctx, mx_ - 156, my_ - 14, 30 + 10 * math.sin(t * 3), 28, 14)
        rgba(ctx, GREEN, window(t, 266.2, 271.2))
        ctx.fill()
        return
    if t < 289:  # os músculos da respiração param — o coração não
        stop = appear(t, 280.5, 2.5)
        br = (0.5 + 0.5 * math.sin(t * 2.2)) * (1 - stop)
        lungs(ctx, W * 0.34, H * 0.52, 1.6, br, stop=stop)
        mark(ctx, "diafragma", W * 0.34, H * 0.52 + 80 * 1.6 + 22 * 1.6 * br, 60)
        beat = 1 + 0.12 * max(0, math.sin(t * 7.5))
        ctx.save()
        ctx.translate(W * 0.74, H * 0.52)
        ctx.scale(beat, beat)
        icon(ctx, "heart", 0, 0, 1.6, appear(t, 283.2, 0.6), RED)
        ctx.restore()
        mark(ctx, "coracao", W * 0.74, H * 0.52, 60)
        return
    # consciente, sentindo tudo
    x = W * 0.30
    rig.figure(ctx, x, H * 0.80, 2.2, rig.p_lie(t), outfit="swimmer", t=t)
    hp = rig.head_point(x, H * 0.80, 2.2, rig.p_lie(t))
    blink = 1 if (t % 2.6) > 0.15 else 0.2
    ellipse_path(ctx, hp[0] + 4, hp[1] - 10, 7, 5 * blink)
    ink(ctx, WHITE, 1, 1.5)
    circle(ctx, hp[0] + 5, hp[1] - 10, 2.5 * blink, INK)


def u_venom(ctx, t):
    label(ctx, "E O QUE ESSE VENENO FAZ?", W / 2, H * 0.10, t, 246.2, 248.4, 28, ORANGE)
    if t < 256:
        big_title(ctx, [("CONOTOXINAS", ORANGE, "black")], W / 2, H * 0.14, t, 251.4, None, 44)
        kicker(ctx, "CENTENAS DE PEQUENAS SUBSTÂNCIAS", W / 2, H * 0.20, t, 251.8, None, 16, WHITE)
        return
    mcallout(ctx, "juncao", W * 0.40, H * 0.18, "NERVO → MÚSCULO: A MENSAGEM É BLOQUEADA", window(t, 256.6, 261.2))
    label(ctx, "COMO CORTAR OS FIOS ENTRE O CÉREBRO E O CORPO", W / 2, H * 0.08, t, 261.2, 266.0, 20, WHITE)
    if 266 <= t < 278:
        label(ctx, "MUITAS VEZES, QUASE NÃO DÓI", W * 0.70, H * 0.30, t, 266.2, 271.2, 22, WHITE)
        items = [("FORMIGAMENTO E DORMÊNCIA", 271.0), ("VISÃO DUPLA", 273.2), ("FALA ENROLADA", 274.0),
                 ("DIFICULDADE DE ENGOLIR", 275.0)]
        for i, (s, t0) in enumerate(items):
            text(ctx, s, W * 0.56, H * 0.28 + i * 50, 20, WHITE, appear(t, t0), "l", "black", sp=1.3)
    if 278 <= t < 289:
        label(ctx, "OS MÚSCULOS PARAM DE OBEDECER", W / 2, H * 0.08, t, 278.2, 283.0, 22, WHITE)
        mcallout(ctx, "diafragma", W * 0.12, H * 0.20, "DIAFRAGMA: SEM ORDENS", window(t, 285.6, 289.2))
        mcallout(ctx, "coracao", W * 0.84, H * 0.20, "O CORAÇÃO CONTINUA", window(t, 283.4, 289.2))
    if t >= 289:
        label(ctx, "CONSCIENTE", W * 0.70, H * 0.30, t, 289.2, None, 40, WHITE)
        label(ctx, "SENTINDO TUDO", W * 0.70, H * 0.40, t, 291.0, None, 24, ORANGE)
        label(ctx, "SEM CONSEGUIR PEDIR AJUDA", W * 0.70, H * 0.48, t, 292.4, None, 20, RED)
        if t > 295:
            timer(ctx, W * 0.70, H * 0.70, 60, clamp((t - 295.2) / 1.5), appear(t, 295.0), "< 1 H")


# ================================================================== 4:57 – 5:25 sem antídoto
def cigarette(ctx, x, y, s, burn, t, a=1.0):
    L = 220 * s * (1 - 0.6 * burn)
    rrect(ctx, x, y - 9 * s, 70 * s, 18 * s, 4)
    ink(ctx, (0.85, 0.60, 0.30), a, 2)
    rrect(ctx, x + 70 * s, y - 9 * s, L, 18 * s, 4)
    ink(ctx, (0.96, 0.96, 0.94), a, 2)
    ex = x + 70 * s + L
    circle(ctx, ex, y, 9 * s, (1.0, 0.45, 0.15), a * (0.7 + 0.3 * math.sin(t * 9)))
    for k in range(5):
        ph = (t * 0.4 + k / 5) % 1
        ctx.move_to(ex, y - 10 * s)
        ctx.curve_to(ex - 20 * s, y - 60 * s * ph, ex + 20 * s, y - 100 * s * ph, ex + 10 * math.sin(t + k) * s,
                     y - 160 * s * ph)
        rgba(ctx, (0.85, 0.88, 0.90), 0.35 * a * (1 - ph))
        ctx.set_line_width(4 * s)
        ctx.stroke()


def w_deaths(ctx, t):
    studio(ctx, t, H * 0.92)
    if t < 303:
        n = int(clamp((t - 297.2) / 2.5) * 36)
        for i in range(n):
            x, y = W * 0.18 + (i % 12) * 50, H * 0.30 + (i // 12) * 70
            line(ctx, x, y, x, y + 46, WHITE, 0.9, 4)
        if t > 300.2:
            cone_snail(ctx, W * 0.72, H * 0.84, 300, t, shell_only=True, seed=3)
            hand_close(ctx, W * 0.72, H * 0.70 - 30 * math.sin(t), 1.2, curl=0.2, from_dir=(0.4, -1))
        return
    if t < 311:  # não existe antídoto
        k = appear(t, 304.0, 0.5)
        rrect(ctx, W * 0.45, H * 0.30, 120, 200, 16)
        ink(ctx, (0.85, 0.92, 0.95), k, 2.5)
        rrect(ctx, W * 0.45 + 15, H * 0.30 + 70, 90, 110, 10)
        rgba(ctx, (0.75, 0.80, 0.85), 0.5 * k)
        ctx.fill()
        xmark(ctx, W * 0.45 + 60, H * 0.30 + 100, 110, appear(t, 305.8, 0.6))
        return
    if t < 318.5:  # caramujo-cigarro
        cigarette(ctx, W * 0.25, H * 0.55, 1.6, clamp((t - 313) / 5), t)
        return
    timer(ctx, W * 0.40, H * 0.52, 110, clamp((t - 318.8) / 6), 1, "TEMPO")


def u_deaths(ctx, t):
    label(ctx, "DEZENAS DE MORTES REGISTRADAS", W / 2, H * 0.10, t, 297.3, 303.0, 24, WHITE)
    label(ctx, "A MAIORIA PEGOU A CONCHA NA MÃO", W * 0.72, H * 0.94, t, 300.3, 303.0, 18, ORANGE)
    big_title(ctx, [("NÃO EXISTE ", WHITE, "black"), ("ANTÍDOTO", RED, "light")], W / 2, H * 0.14, t, 305.6, 311.0,
              48)
    label(ctx, "NENHUM SORO · NENHUM REMÉDIO", W / 2, H * 0.86, t, 307.2, 311.0, 20, WHITE)
    big_title(ctx, [("CARAMUJO-", WHITE, "black"), ("CIGARRO", ORANGE, "light")], W / 2, H * 0.16, t, 311.2, 318.4,
              46)
    label(ctx, "A LENDA: TEMPO DE FUMAR UM CIGARRO", W / 2, H * 0.86, t, 313.8, 318.4, 20, WHITE)
    label(ctx, "EXAGERO: NA MAIORIA DOS CASOS, EXISTE TEMPO", W * 0.70, H * 0.40, t, 318.6, None, 20, WHITE)
    label(ctx, "O QUE VOCÊ FAZ COM ELE DECIDE TUDO", W * 0.70, H * 0.50, t, 322.0, None, 22, ORANGE)


# ================================================================== 5:25 – 5:49 como evitar
def w_avoid(ctx, t):
    if t < 336:
        underwater_close(ctx, t, floor=H * 0.84)
        cone_snail(ctx, W * 0.55, H * 0.86, 360, t, crawl=0.6, seed=3)
        if t < 331.5:
            hy = kf(t, [(325, -200), (328.5, H * 0.52)]) + 6 * math.sin(t * 3)
            hand_close(ctx, W * 0.52, hy, 1.4, curl=0.1, from_dir=(-0.4, -1))
            xmark(ctx, W * 0.55, H * 0.62, 120, appear(t, 328.6, 0.5))
        else:
            mark(ctx, "forma", *cone_point(W * 0.55, H * 0.86, 360, 0, 0.18), 80)
        return
    if t < 341.6:  # olhe, fotografe
        underwater_close(ctx, t, floor=H * 0.84)
        cone_snail(ctx, W * 0.55, H * 0.86, 360, t, crawl=0.6, seed=3)
        # celular/câmera na mão, flash
        hx, hy = W * 0.25, H * 0.40
        rrect(ctx, hx - 60, hy - 100, 120, 200, 16)
        ink(ctx, (0.15, 0.17, 0.20), 1, 2.5)
        rrect(ctx, hx - 50, hy - 88, 100, 170, 8)
        rgba(ctx, (0.30, 0.60, 0.62), 1)
        ctx.fill()
        cone_snail(ctx, hx, hy + 30, 80, t, seed=3)
        circle(ctx, hx, hy - 100 + 8, 3, INK)
        if 338.5 < t < 339.0:
            rgba(ctx, WHITE, 0.7 * (1 - (t - 338.5) / 0.5))
            ctx.paint()
        return
    # nunca no bolso da roupa de banho: calção visto de lado com bolso lateral
    studio(ctx, t, H * 0.92)
    x0, y0 = W * 0.30, H * 0.22
    ctx.move_to(x0, y0)
    ctx.line_to(x0 + 380, y0)
    ctx.line_to(x0 + 400, y0 + 330)
    ctx.line_to(x0 + 220, y0 + 340)
    ctx.line_to(x0 + 190, y0 + 150)
    ctx.line_to(x0 + 160, y0 + 340)
    ctx.line_to(x0 - 20, y0 + 330)
    ctx.close_path()
    ink(ctx, (0.18, 0.30, 0.48), 1, 2.5)
    rrect(ctx, x0 - 6, y0 - 8, 392, 30, 10)
    ink(ctx, (0.14, 0.24, 0.40), 1, 2)
    for k in range(3):
        line(ctx, x0 + 170 + k * 10, y0 + 22, x0 + 168 + k * 10, y0 + 60, WHITE, 0.8, 2)
    # bolso com a concha dentro
    cone_snail(ctx, x0 + 300, y0 + 150, 120, t, shell_only=True, seed=3)
    ctx.move_to(x0 + 240, y0 + 120)
    ctx.line_to(x0 + 370, y0 + 120)
    ctx.line_to(x0 + 375, y0 + 250)
    ctx.line_to(x0 + 245, y0 + 250)
    ctx.close_path()
    ink(ctx, (0.15, 0.26, 0.42), 0.55, 2)
    line(ctx, x0 + 240, y0 + 120, x0 + 370, y0 + 120, INK, 1, 3)
    if t > 345.6:
        prob = appear(t, 345.6, 0.8)
        line(ctx, x0 + 330, y0 + 170, x0 + 330 + 70 * prob, y0 + 280, (0.88, 0.62, 0.58), 1, 5)
        harpoon_tooth(ctx, x0 + 330 + 70 * prob, y0 + 280, 30, 1.0, prob)
    xmark(ctx, x0 + 190, y0 + 170, 190, appear(t, 343.0, 0.5))


def u_avoid(ctx, t):
    label(ctx, "COMO AS PESSOAS EVITAM?", W / 2, H * 0.10, t, 325.2, 327.8, 26, ORANGE)
    big_title(ctx, [("NUNCA PEGUE ", WHITE, "black"), ("UMA CONCHA VIVA", ORANGE, "light")], W / 2, H * 0.12, t,
              328.0, 331.2, 34)
    mcallout(ctx, "forma", W * 0.80, H * 0.22, "FORMA DE CONE, DESENHOS BONITOS", window(t, 331.4, 336.0))
    label(ctx, "INDO-PACÍFICO", W / 2, H * 0.10, t, 333.8, 336.0, 22, WHITE)
    label(ctx, "OLHE · FOTOGRAFE · DEIXE ONDE ESTÁ", W / 2, H * 0.10, t, 336.2, 341.6, 24, WHITE)
    label(ctx, "NUNCA NO BOLSO DA ROUPA DE BANHO", W / 2, H * 0.10, t, 342.0, None, 24, RED)
    label(ctx, "JÁ ACONTECEU: PICADOS PELA CONCHA NO BOLSO", W / 2, H * 0.92, t, 345.8, None, 18, WHITE)


# ================================================================== 5:49 – 6:28 o cenário com o amigo
def w_scen(ctx, t):
    if t < 370:
        you = Path([(349, W * 0.10, 0), (359, W * 0.40, 0)])
        fr = Path([(349, W * 0.25, 0), (359, W * 0.58, 0)])

        def mid(c):
            cone_snail(c, W * 0.66, FLOOR + 4, 60, t, shell_only=t >= 359.5, seed=3)
            if t < 359:  # nadando de snorkel na superfície (crawl, rosto na água, sempre para a frente)
                for pth, out, off in ((you, "snorkel", 0.0), (fr, "snorkel2", 0.7)):
                    x, _ = pth.pos(t)
                    rig.figure(c, x, WAIST + 14, 1.15, rig.p_swim(t + off, 0.8), outfit=out, facing=1, t=t,
                               ground=False, shadow=False)
                return
            # o amigo fica de pé (água na cintura) segurando a concha no alto
            x1, _ = you.pos(359)
            x2, _ = fr.pos(359)
            wader(c, x1, t, "snorkel", 1, 1.2, rig.p_stand(t))
            up = appear(t, 359.6, 0.8)
            look = appear(t, 363.0, 0.8)
            laugh = window(t, 367.6, 370.0) * math.sin(t * 14) * 3
            p = rig.blend(rig.p_stand(t), rig.pose(armF=150, elbowF=10, lean=-4 + laugh, neck=-10), up)
            p = rig.blend(p, rig.pose(armF=60, elbowF=90, lean=10 + laugh, neck=30), look)
            wader(c, x2, t, "snorkel2", -1, 1.2, p)
            hp = rig.hand_point(x2, FLOOR, 1.2, p, -1)
            cone_snail(c, hp[0] - 6, hp[1] + 4, 40, t, shell_only=True, seed=3)
            mark(c, "palma", hp[0], hp[1], 16)

        reef_scene(ctx, t, mid, surf=WAIST, xoff=t * 4)
        return
    # 10 minutos depois: sentado na areia, com sintomas
    shore(ctx, t, dusk=appear(t, 370, 4) * 0.6)
    x = W * 0.44
    sit = rig.pose(lean=-6 + 2 * math.sin(t * 0.8), thighF=88, kneeF=40, thighB=86, kneeB=50, armF=28, elbowF=50,
                   armB=-30, elbowB=10, neck=8)
    rig.figure(ctx, x, H * 0.80, 2.0, sit, outfit="snorkel2", facing=-1, t=t)
    pts = rig.world_points(x, H * 0.80, 2.0, sit, -1)
    mark(ctx, "mao2", *pts["handF"], 22)
    mark(ctx, "labios", pts["head"][0] - 22, pts["head"][1] + 12, 16)
    rig.figure(ctx, W * 0.66, H * 0.80, 2.0, rig.p_stand(t), outfit="snorkel", facing=-1, t=t)
    if t > 377 and t < 380:  # visão dupla
        rig.figure(ctx, x + 14, H * 0.80, 2.0, sit, outfit="snorkel2", facing=-1, t=t, a=0.3, shadow=False)
    if t > 383:  # o que você tem: celular, toalha, camiseta
        for i, kind in enumerate(("phone", "towel", "shirt")):
            a = appear(t, 383.4 + i * 0.8)
            cx_, cy_ = W * 0.20 + i * 120, H * 0.88
            if kind == "phone":
                icon(ctx, "phone", cx_, cy_, 1.0, a)
            elif kind == "towel":
                rrect(ctx, cx_ - 40, cy_ - 16, 80, 32, 6)
                ink(ctx, (0.85, 0.40, 0.35), a, 2)
                line(ctx, cx_ - 40, cy_ - 4, cx_ + 40, cy_ - 4, WHITE, a, 3)
            else:
                ctx.move_to(cx_ - 30, cy_ - 22)
                ctx.line_to(cx_ - 46, cy_ - 8)
                ctx.line_to(cx_ - 34, cy_)
                ctx.line_to(cx_ - 26, cy_ - 8)
                ctx.line_to(cx_ - 26, cy_ + 24)
                ctx.line_to(cx_ + 26, cy_ + 24)
                ctx.line_to(cx_ + 26, cy_ - 8)
                ctx.line_to(cx_ + 34, cy_)
                ctx.line_to(cx_ + 46, cy_ - 8)
                ctx.line_to(cx_ + 30, cy_ - 22)
                ctx.close_path()
                ink(ctx, (0.85, 0.85, 0.80), a, 2)


def u_scen(ctx, t):
    chapter(ctx, "FIM DE TARDE · RECIFE RASO", "O QUE VOCÊ", "FARIA?", W / 2, H * 0.14, t, 349.5, 355.0, 44)
    label(ctx, "VOCÊ E UM AMIGO, DE SNORKEL", W / 2, H * 0.10, t, 355.2, 359.4, 22, WHITE)
    mcallout(ctx, "palma", W * 0.80, H * 0.20, "“SENTI UMA PICADINHA”", window(t, 364.4, 368.0))
    label(ctx, "“NÃO FOI NADA”", W * 0.80, H * 0.20, t, 368.2, 370.0, 22, WHITE)
    kicker(ctx, "10 MINUTOS DEPOIS", W / 2, H * 0.08, t, 370.2, 374.0, 18, ORANGE)
    mcallout(ctx, "mao2", W * 0.20, H * 0.22, "MÃO DORMENTE", window(t, 373.0, 376.0))
    mcallout(ctx, "labios", W * 0.20, H * 0.22, "LÁBIOS FORMIGANDO", window(t, 375.2, 377.2))
    label(ctx, "VISÃO DOBRADA · VOZ ENROLADA", W / 2, H * 0.08, t, 377.2, 380.4, 20, WHITE)
    label(ctx, "SOZINHOS NA PRAIA", W / 2, H * 0.08, t, 380.6, 383.2, 22, ORANGE)
    label(ctx, "CELULAR · TOALHA · CAMISETA", W * 0.33, H * 0.78, t, 383.4, None, 18, WHITE)


# ================================================================== 6:27 – 6:48 a decisão
PANELS = [("A", "CHUPAR O VENENO E CORTAR", 390.0), ("B", "ÁGUA BEM QUENTE", 394.0),
          ("C", "ENROLAR O BRAÇO FIRME E NÃO MEXER", 398.8)]


def icon_choice(ctx, kind, cx, cy, a, t):
    if kind == "A":  # faca + gota
        ctx.move_to(cx - 60, cy + 10)
        ctx.line_to(cx + 30, cy - 30)
        ctx.line_to(cx + 40, cy - 20)
        ctx.close_path()
        ink(ctx, (0.85, 0.88, 0.90), a, 2)
        rrect(ctx, cx + 28, cy - 34, 40, 16, 4)
        ink(ctx, (0.40, 0.28, 0.20), a, 2)
        circle(ctx, cx - 40, cy + 30, 9, RED, a)
    elif kind == "B":
        rrect(ctx, cx - 60, cy - 10, 120, 50, 10)
        ink(ctx, (0.45, 0.72, 0.85), a, 2)
        for k in range(3):
            xx = cx - 30 + k * 30
            ctx.move_to(xx, cy - 16)
            ctx.curve_to(xx - 8, cy - 30, xx + 8, cy - 40, xx, cy - 56 - 4 * math.sin(t * 2 + k))
            rgba(ctx, WHITE, 0.6 * a)
            ctx.set_line_width(2.5)
            ctx.stroke()
    else:  # rolo de faixa
        limb(ctx, [(cx - 70, cy + 10), (cx + 30, cy + 10)], 40, SKIN, a)
        for k in range(5):
            xx = cx - 60 + k * 18
            line(ctx, xx, cy - 12, xx + 10, cy + 32, (0.95, 0.95, 0.92), a, 8)
        circle(ctx, cx + 50, cy - 10, 22, (0.95, 0.95, 0.92), a)


def w_choice(ctx, t):
    studio(ctx, t, H * 0.92)


def u_choice(ctx, t):
    label(ctx, "PRIMEIRA DECISÃO", W / 2, H * 0.12, t, 387.2, None, 34, WHITE)
    for i, (lt, nm, t0) in enumerate(PANELS):
        a = appear(t, t0)
        x = W / 2 + (i - 1) * 380
        card(ctx, x - 170, H * 0.28, 340, 220, a)
        icon_choice(ctx, lt, x, H * 0.28 + 100, a, t)
        text(ctx, lt, x - 140, H * 0.28 + 200, 24, ORANGE, a, "l", "black")
        text(ctx, nm, x - 110, H * 0.28 + 196, 12, WHITE, a, "l", "black", sp=0.8)
    label(ctx, "ESCOLHA UMA ANTES DE EU TE CONTAR", W / 2, H * 0.82, t, 405.0, None, 22, ORANGE)
    if t > 405.6:
        text(ctx, str(max(1, 3 - int(t - 405.6))), W / 2, H * 0.92, 30, WHITE, 1, "c", "black")


# ================================================================== 6:48 – 7:23 as respostas
def arm_close(ctx, x, y, s, a=1.0, skin=SKIN):
    """Antebraço e mão de perfil, deitados (para ferida, faixa, tala)."""
    limb(ctx, [(x - 420 * s, y), (x, y)], 70 * s, skin, a)
    hand_close(ctx, x + 40 * s, y - 4 * s, 0.9 * s, curl=0.15, skin=skin, from_dir=(-1, 0))


def w_answers(ctx, t):
    studio(ctx, t, H * 0.92)
    x, y = W * 0.58, H * 0.58
    arm_close(ctx, x, y, 1.4)
    wx, wy = x + 40, y - 10
    mark(ctx, "ferida", wx, wy, 20)
    if t < 423:  # chupar/cortar: o veneno já está nos tecidos; o corte só cria outra ferida
        spread = appear(t, 415, 3)
        for k in range(30):
            rnd = random.Random(k)
            px = wx - rnd.uniform(0, 300) * (0.3 + 0.7 * spread)
            py = wy + rnd.uniform(-30, 30)
            circle(ctx, px, py, 4, (0.55, 0.95, 0.35), 0.8)
        if t > 419.5:
            line(ctx, wx - 60, wy - 14, wx + 20, wy + 10, RED, appear(t, 419.5, 0.4), 4)
            circle(ctx, wx - 20, wy, 40, (0.85, 0.75, 0.25), 0.25 * appear(t, 421, 1))
        return
    if t < 438:  # água quente: o veneno continua chegando aos nervos
        rrect(ctx, x - 300, y - 30, 480, 120, 18)
        rgba(ctx, (0.45, 0.72, 0.85), 0.45)
        ctx.fill()
        for k in range(4):
            xx = x - 200 + k * 100
            ctx.move_to(xx, y - 40)
            ctx.curve_to(xx - 10, y - 70, xx + 10, y - 90, xx, y - 120 - 6 * math.sin(t * 2 + k))
            rgba(ctx, WHITE, 0.5)
            ctx.set_line_width(3)
            ctx.stroke()
        # nervos acendendo: o veneno chegando mesmo assim
        for k in range(3):
            yy = y - 20 + k * 18
            line(ctx, x - 420 * 1.4, yy, x + 40, yy, YELLOW, 0.4, 2)
            ph = (t * 0.8 + k / 3) % 1
            circle(ctx, lerp(x + 40, x - 420 * 1.4, ph), yy, 5, (0.55, 0.95, 0.35), 0.9)
        return
    # certo: faixa firme
    k = appear(t, 438.6, 2.5)
    for i in range(int(14 * k)):
        xx = x + 40 - i * 34
        line(ctx, xx, y - 40, xx - 24, y + 40, (0.95, 0.95, 0.92), 1, 14)
        line(ctx, xx, y - 40, xx - 24, y + 40, INK, 0.25, 1)


def u_answers(ctx, t):
    marks = {"A": (408.2, 423, "x"), "B": (423, 438, "x"), "C": (438, 443, "v")}
    for i, (lt, nm, _) in enumerate(PANELS):
        x = W / 2 + (i - 1) * 380 - 170
        card(ctx, x, 26, 340, 60, 1)
        text(ctx, lt + "  " + nm, x + 170, 64, 11, WHITE, 1, "c", "bold", sp=0.6)
        s0 = marks[lt][0]
        if t > s0 + 1:
            (xmark if marks[lt][2] == "x" else check)(ctx, x + 322, 56, 13, appear(t, s0 + 1))
    label(ctx, "UMA DAS PIORES IDEIAS", W / 2, H * 0.22, t, 410.6, 423, 36, RED)
    mcallout(ctx, "ferida", W * 0.86, H * 0.36, "O VENENO JÁ ENTROU NOS TECIDOS", window(t, 414.8, 419.2))
    mcallout(ctx, "ferida", W * 0.86, H * 0.36, "O CORTE: UMA FERIDA NOVA", window(t, 419.2, 423.0))
    label(ctx, "FUNCIONA NO PEIXE-PEDRA, NÃO AQUI", W / 2, H * 0.22, t, 427.8, 438, 28, ORANGE)
    label(ctx, "NÃO IMPEDE O VENENO DE CHEGAR NOS NERVOS", W / 2, H * 0.88, t, 430.6, 438, 20, WHITE)
    label(ctx, "ACERTOU", W / 2, H * 0.22, t, 441.6, None, 44, GREEN)


# ================================================================== 7:23 – 8:04 imobilização com pressão
def w_bandage(ctx, t):
    studio(ctx, t, H * 0.92)
    if t < 454:
        # faixa firme x torniquete (que corta a circulação)
        for i, (lab_, good) in enumerate((("FAIXA", True), ("TORNIQUETE", False))):
            x, y = W * 0.62, H * (0.40 + i * 0.30)
            arm_close(ctx, x, y, 0.9)
            if good:
                for k in range(int(10 * appear(t, 444, 2))):
                    xx = x + 20 - k * 30
                    line(ctx, xx, y - 26, xx - 20, y + 26, (0.95, 0.95, 0.92), 1, 12)
            else:
                rrect(ctx, x - 300, y - 40, 26, 80, 6)
                ink(ctx, (0.25, 0.22, 0.2), appear(t, 449.4), 2)
                xmark(ctx, x - 287, y, 50, appear(t, 450.0, 0.4))
            mark(ctx, "b%d" % i, x - 150, y, 40)
        return
    if t < 466:  # enrolando: da mão subindo pelo braço inteiro (com toalha/camiseta)
        x, gy = W * 0.40, H * 0.90
        p = rig.pose(lean=-8, thighF=88, kneeF=0, thighB=86, kneeB=0, armF=40, elbowF=0, armB=10, elbowB=20, neck=4)
        rig.figure(ctx, x, gy, 2.6, p, outfit="snorkel2", facing=1, t=t)
        pts = rig.world_points(x, gy, 2.6, p, 1)
        seq = [pts["handF"], pts["wristF"], pts["elbowF"], pts["shoulder"]]
        k = clamp((t - 454.5) / 7.0)
        n = int(k * 18)
        for i in range(n):
            f = i / 18
            seg = min(2, int(f * 3))
            ff = f * 3 - seg
            px = lerp(seq[seg][0], seq[seg + 1][0], ff)
            py = lerp(seq[seg][1], seq[seg + 1][1], ff)
            line(ctx, px - 14, py - 10, px + 14, py + 10, (0.95, 0.92, 0.88), 1, 9)
        mark(ctx, "faixa", *(pts["elbowF"]), 40)
        return
    if t < 472:  # tala / junto do corpo
        x, gy = W * 0.40, H * 0.90
        p = rig.pose(lean=-8, thighF=88, kneeF=0, thighB=86, kneeB=0, armF=10, elbowF=0, armB=10, elbowB=20, neck=4)
        rig.figure(ctx, x, gy, 2.6, p, outfit="snorkel2", facing=1, t=t)
        pts = rig.world_points(x, gy, 2.6, p, 1)
        line(ctx, pts["shoulder"][0] + 14, pts["shoulder"][1], pts["handF"][0] + 14, pts["handF"][1], (0.60, 0.45, 0.30),
             1, 10)
        for q in (pts["elbowF"], pts["wristF"]):
            line(ctx, q[0] - 18, q[1], q[0] + 26, q[1], WHITE, 1, 8)
        return
    # sistema linfático: com o músculo mexendo, o veneno anda rápido; parado e com pressão, devagar
    still = appear(t, 476.5, 1.5)
    for i, (lab_, sp) in enumerate((("MEXENDO", 1.0), ("PARADO + PRESSÃO", 0.15))):
        y = H * (0.40 + i * 0.28)
        line(ctx, W * 0.15, y, W * 0.85, y, (0.60, 0.80, 0.70), 0.6, 18)
        for k in range(8):
            ph = (t * 0.25 * (sp if i == 1 else 1.0) + k / 8) % 1
            if i == 1:
                ph = ph * 0.25
            circle(ctx, lerp(W * 0.15, W * 0.85, ph), y, 7, (0.55, 0.95, 0.35), 0.9 * (still if i == 1 else 1))
        text(ctx, lab_, W * 0.15, y - 26, 18, WHITE, 1 if i == 0 else still, "l", "black", sp=1.2)


def u_bandage(ctx, t):
    big_title(ctx, [("IMOBILIZAÇÃO ", WHITE, "black"), ("COM PRESSÃO", GREEN, "light")], W / 2, H * 0.12, t, 443.6,
              449.0, 40)
    label(ctx, "RECOMENDADA PELOS SERVIÇOS DE EMERGÊNCIA DA AUSTRÁLIA", W / 2, H * 0.18, t, 446.0, 449.0, 16, WHITE)
    mcallout(ctx, "b1", W * 0.20, H * 0.85, "NÃO CORTA A CIRCULAÇÃO", window(t, 450.2, 454.0))
    label(ctx, "FIRME, COMO PARA UM TORNOZELO TORCIDO", W / 2, H * 0.10, t, 454.2, 458.2, 20, WHITE)
    mcallout(ctx, "faixa", W * 0.78, H * 0.24, "DA MÃO ATÉ O OMBRO", window(t, 458.2, 461.4))
    label(ctx, "TOALHA RASGADA OU CAMISETA SERVEM", W / 2, H * 0.10, t, 461.4, 466.0, 20, ORANGE)
    label(ctx, "TALA OU BRAÇO PRESO JUNTO DO CORPO", W / 2, H * 0.10, t, 466.2, 472.0, 20, WHITE)
    label(ctx, "O VENENO VIAJA PELO SISTEMA LINFÁTICO", W / 2, H * 0.10, t, 472.2, 481.0, 20, WHITE)
    big_title(ctx, [("VOCÊ GANHA ", WHITE, "black"), ("TEMPO", GREEN, "light")], W / 2, H * 0.12, t, 481.2, None, 44)


# ================================================================== 8:04 – 8:21 emergência e repouso
def w_call(ctx, t):
    shore(ctx, t, dusk=0.6)
    x = W * 0.36
    rig.figure(ctx, x, H * 0.82, 2.0, rig.p_lie(t), outfit="snorkel2", t=t)
    p = rig.blend(rig.p_kneel(t), rig.p_phone(t), 1 - appear(t, 491, 1))
    rig.figure(ctx, W * 0.66, H * 0.82, 2.0, p, outfit="snorkel", facing=-1, t=t)
    if t < 491:
        hp = rig.hand_point(W * 0.66, H * 0.82, 2.0, p, -1)
        mark(ctx, "fone", *hp, 18)


def u_call(ctx, t):
    mcallout(ctx, "fone", W * 0.86, H * 0.20, "EMERGÊNCIA: “PICADA DE CARAMUJO-CONE”", window(t, 485.2, 489.0))
    label(ctx, "POSSÍVEL PARALISIA", W / 2, H * 0.10, t, 489.0, 491.0, 24, ORANGE)
    label(ctx, "DEITADO · PARADO · CALMO", W / 2, H * 0.10, t, 491.2, 498.0, 24, WHITE)
    label(ctx, "SEM ANDAR NADA", W / 2, H * 0.10, t, 498.0, None, 26, RED)


# ================================================================== 8:21 – 8:48 respire por ele
def w_breath(ctx, t):
    shore(ctx, t, dusk=0.7)
    x = W * 0.34
    rig.figure(ctx, x, H * 0.82, 2.0, rig.p_lie(t), outfit="snorkel2", t=t)
    lp = rig.world_points(x, H * 0.82, 2.0, rig.p_lie(t))
    # coração batendo (sempre), ar não entra até o resgate
    hx, hy = lp["shoulder"][0] - 10, lp["shoulder"][1] - 6
    beat = 1 + 0.15 * max(0, math.sin(t * 7.5))
    ctx.save()
    ctx.translate(hx, hy - 30)
    ctx.scale(beat * 0.6, beat * 0.6)
    icon(ctx, "heart", 0, 0, 1, window(t, 503, 512), RED)
    ctx.restore()
    mark(ctx, "coracao2", hx, hy - 30, 24)
    if t >= 511:
        cpr = 517.5 <= t < 521.5
        p = rig.p_cpr(t) if cpr else rig.pose(lean=60 + 8 * math.sin(t * 1.2), thighF=14, kneeF=104, thighB=12,
                                                 kneeB=102, footF=0, footB=0, armF=30, elbowF=40, armB=20, elbowB=40,
                                                 neck=20)
        rig.figure(ctx, x + (40 if cpr else 150), H * 0.82, 2.0, p, outfit="snorkel", facing=-1, t=t)
        if not cpr:  # ar entrando: peito sobe a cada sopro
            br = max(0, math.sin(t * 2.0))
            for k in range(3):
                ph = (t * 1.0 + k / 3) % 1
                circle(ctx, lp["head"][0] + 30 - ph * 20, lp["head"][1] - 20 + ph * 10, 4, WHITE, 0.6 * (1 - ph) * br)
    if t > 521.5:  # fale com ele
        for k in range(3):
            ph = (t * 0.7 + k / 3) % 1
            ctx.arc(x + 160, H * 0.50, 20 + ph * 60, math.pi * 0.7, math.pi * 1.3)
            rgba(ctx, WHITE, 0.5 * (1 - ph))
            ctx.set_line_width(2)
            ctx.stroke()


def u_breath(ctx, t):
    label(ctx, "A PARTE MAIS IMPORTANTE", W / 2, H * 0.10, t, 501.2, 503.4, 26, ORANGE)
    mcallout(ctx, "coracao2", W * 0.66, H * 0.20, "O CORAÇÃO AINDA ESTÁ BATENDO", window(t, 503.6, 509.2))
    label(ctx, "O PROBLEMA É SÓ O AR QUE NÃO ENTRA", W / 2, H * 0.10, t, 509.2, 511.2, 22, WHITE)
    big_title(ctx, [("RESPIRE ", WHITE, "black"), ("POR ELE", GREEN, "light")], W / 2, H * 0.12, t, 511.3, 517.2, 44)
    label(ctx, "SEM PARAR, ATÉ A AJUDA CHEGAR", W / 2, H * 0.20, t, 513.4, 517.2, 20, WHITE)
    label(ctx, "SE O CORAÇÃO PARAR: MASSAGEM CARDÍACA JUNTO", W / 2, H * 0.10, t, 517.4, 521.4, 20, ORANGE)
    label(ctx, "ELE PODE ESTAR OUVINDO: FALE COM ELE", W / 2, H * 0.10, t, 521.6, None, 22, WHITE)


# ================================================================== 8:48 – 9:16 hospital
def w_hosp(ctx, t):
    studio(ctx, t, H * 0.90)
    # leito + respirador (máquina) bombeando
    bx, by = W * 0.30, H * 0.70
    rrect(ctx, bx - 40, by, 520, 30, 8)
    ink(ctx, (0.80, 0.84, 0.86), 1, 2)
    line(ctx, bx - 30, by + 30, bx - 30, H * 0.90, (0.70, 0.72, 0.74), 1, 6)
    line(ctx, bx + 460, by + 30, bx + 460, H * 0.90, (0.70, 0.72, 0.74), 1, 6)
    rec = appear(t, 538.5, 4)
    p = rig.blend(rig.p_lie(t), rig.pose(lean=-60, thighF=88, kneeF=0, thighB=88, kneeB=0, armF=40, elbowF=20), 0)
    rig.figure(ctx, bx + 40, by, 1.8, p, outfit="snorkel2", t=t, shadow=False)
    vx, vy = W * 0.78, H * 0.48
    rrect(ctx, vx - 70, vy - 90, 140, 180, 12)
    ink(ctx, (0.85, 0.88, 0.90), 1, 2)
    pump = 0.5 + 0.5 * math.sin(t * 1.6)
    rrect(ctx, vx - 40, vy - 10 + 30 * pump * (1 - rec), 80, 40, 6)
    ink(ctx, (0.55, 0.75, 0.85), 1, 2)
    hp = rig.head_point(bx + 40, by, 1.8, p)
    ctx.move_to(vx - 70, vy + 40)
    ctx.curve_to(vx - 200, vy + 120, hp[0] + 80, hp[1] - 60, hp[0] + 10, hp[1])
    rgba(ctx, (0.75, 0.85, 0.90), 1 - rec)
    ctx.set_line_width(5)
    ctx.stroke()
    mark(ctx, "resp", vx, vy, 90)
    if t > 533:  # relógio: horas passando
        timer(ctx, W * 0.16, H * 0.24, 50, ((t - 533) / 3) % 1, 1, "HORAS")


def u_hosp(ctx, t):
    mcallout(ctx, "resp", W * 0.60, H * 0.12, "RESPIRADOR: RESPIRA NO LUGAR DELE", window(t, 528.4, 533.2))
    label(ctx, "E ELES ESPERAM", W / 2, H * 0.10, t, 533.4, 536.2, 26, WHITE)
    label(ctx, "O CORPO ELIMINA O VENENO AOS POUCOS", W / 2, H * 0.10, t, 536.2, 538.4, 20, WHITE)
    label(ctx, "HORAS, ÀS VEZES UM DIA: OS MÚSCULOS VOLTAM", W / 2, H * 0.10, t, 538.6, 543.0, 20, ORANGE)
    label(ctx, "RECUPERAÇÃO COMPLETA", W / 2, H * 0.10, t, 543.2, 546.2, 26, GREEN)
    label(ctx, "CONTRA UM VENENO SEM ANTÍDOTO...", W / 2, H * 0.40, t, 546.4, None, 24, WHITE)
    label(ctx, "...ALGUÉM QUE NÃO DESISTE DE RESPIRAR POR VOCÊ", W / 2, H * 0.50, t, 550.0, None, 24, GREEN)


# ================================================================== 9:16 – 10:24 a reviravolta
def w_twist(ctx, t):
    if t < 576:
        underwater_close(ctx, t, floor=H * 0.84)
        night_tint(ctx, 0.4)
        cone_snail(ctx, W * 0.36, H * 0.86, 460, t, crawl=0.8, seed=3)
        if 563 < t < 569:  # alvos naturais: peixe, minhoca, caramujo
            a = window(t, 563, 569)
            fishy(ctx, W * 0.72, H * 0.30, 0.8, t, a=a, flip=-1)
            ctx.move_to(W * 0.66, H * 0.52)
            for k in range(20):
                ctx.line_to(W * 0.66 + k * 8, H * 0.52 + 8 * math.sin(k * 0.8 + t * 3))
            rgba(ctx, (0.85, 0.55, 0.55), a)
            ctx.set_line_width(7)
            ctx.stroke()
            cone_snail(ctx, W * 0.80, H * 0.75, 110, t, a=a, seed=9)
        if t > 571:  # a mão apertando a concha: ele se defende
            hand_close(ctx, W * 0.40, H * 0.55, 1.6, curl=0.6 * appear(t, 571.4, 1), from_dir=(-0.3, -1))
        return
    studio(ctx, t, H * 0.92)
    if t < 584:  # o veneno vira remédio: frasco -> moléculas estudadas
        k = appear(t, 576.6, 1.5)
        for i in range(20):
            ang = i * 0.314 + t * 0.2
            circle(ctx, W * 0.50 + math.cos(ang) * 220 * k, H * 0.52 + math.sin(ang) * 120 * k, 8,
                   [(0.55, 0.95, 0.35), (0.95, 0.75, 0.30), (0.45, 0.75, 0.95)][i % 3], k)
        rrect(ctx, W * 0.50 - 40, H * 0.52 - 70, 80, 140, 14)
        ink(ctx, (0.85, 0.92, 0.95), 1, 2.5)
        return
    if t < 597:  # medula: o sinal de dor é bloqueado
        sx_ = W * 0.30
        rrect(ctx, sx_ - 30, H * 0.12, 60, H * 0.70, 26)
        ink(ctx, (0.92, 0.90, 0.85), 1, 2.5)
        for i in range(8):
            rrect(ctx, sx_ - 44, H * 0.14 + i * 62, 88, 30, 8)
            ink(ctx, (0.80, 0.78, 0.72), 1, 2)
        blk = appear(t, 592.2, 1.0)
        for k in range(6):
            ph = (t * 0.8 + k / 6) % 1
            x = lerp(W * 0.90, sx_ + 40, ph)
            if blk > 0.5 and x < sx_ + 180:
                continue
            circle(ctx, x, H * 0.55, 7, RED, 0.9)
        if blk > 0:
            line(ctx, sx_ + 170, H * 0.45, sx_ + 170, H * 0.65, GREEN, blk, 10)
        mark(ctx, "medula", sx_, H * 0.55, 40)
        return
    # centenas de substâncias estudadas: dor, epilepsia...
    for i in range(3):
        a = appear(t, 600.0 + i * 1.6)
        x = W * (0.22 + i * 0.28)
        card(ctx, x - 110, H * 0.32, 220, 160, a)
        icon(ctx, ["drop", "brain", "heart"][i], x, H * 0.32 + 70, 1.2, a)


def u_twist(ctx, t):
    label(ctx, "E AQUI VEM A REVIRAVOLTA", W / 2, H * 0.10, t, 556.2, 559.0, 26, ORANGE)
    label(ctx, "O VENENO NÃO FOI FEITO PARA VOCÊ", W / 2, H * 0.10, t, 563.0, 569.0, 22, WHITE)
    label(ctx, "PEIXES · MINHOCAS · OUTROS CARAMUJOS", W * 0.72, H * 0.92, t, 565.0, 569.0, 18, ORANGE)
    label(ctx, "VOCÊ É SÓ UM ACIDENTE", W / 2, H * 0.10, t, 569.0, 571.2, 24, RED)
    label(ctx, "UM ANIMAL QUE SÓ QUER SE DEFENDER", W / 2, H * 0.10, t, 571.4, 576.2, 22, WHITE)
    big_title(ctx, [("VIROU ", WHITE, "black"), ("REMÉDIO", GREEN, "light")], W / 2, H * 0.14, t, 577.8, 584.0, 52)
    label(ctx, "CONTRA DOR CRÔNICA MUITO FORTE", W * 0.70, H * 0.30, t, 584.4, 597.0, 22, WHITE)
    label(ctx, "ÀS VEZES, NEM A MORFINA RESOLVE", W * 0.70, H * 0.38, t, 589.6, 597.0, 18, ORANGE)
    mcallout(ctx, "medula", W * 0.70, H * 0.60, "BLOQUEIA A DOR NA MEDULA, SEM DEPENDÊNCIA", window(t, 592.2, 597.2))
    label(ctx, "CENTENAS DE SUBSTÂNCIAS EM ESTUDO", W / 2, H * 0.14, t, 597.4, 605.0, 24, WHITE)
    for i, s in enumerate(("DOR", "EPILEPSIA", "OUTRAS DOENÇAS")):
        text(ctx, s, W * (0.22 + i * 0.28), H * 0.32 + 140, 18, WHITE, appear(t, 600.0 + i * 1.6), "c", "black",
             sp=1.2)
    label(ctx, "UM ANIMAL SEM ANTÍDOTO PODE TER RESPOSTAS", W / 2, H * 0.86, t, 605.2, 610.0, 22, ORANGE)


# ================================================================== 10:10 – 10:24 recifes sofrendo
def w_reefs(ctx, t):
    underwater_close(ctx, t, floor=H * 0.84)
    bleach = appear(t, 611, 5)
    rnd = random.Random(7)
    for i in range(10):
        x = W * 0.06 + i * 125
        h = rnd.uniform(90, 200)
        col = [(0.92, 0.48, 0.42), (0.96, 0.72, 0.38), (0.62, 0.50, 0.80)][i % 3]
        col = tuple(lerp(c, 0.95, bleach) for c in col)
        ctx.move_to(x, H * 0.84)
        ctx.curve_to(x + 10, H * 0.84 - h, x + 50, H * 0.84 - h, x + 70, H * 0.84)
        ink(ctx, col, 1, 2)
    # mãos coletando conchas
    if t > 614:
        y = kf(t, [(614, -150), (615.5, H * 0.66), (617, H * 0.66), (618.5, -200)])
        hand_close(ctx, W * 0.62, y, 1.2, curl=0.5, from_dir=(-0.3, -1))
        cone_snail(ctx, W * 0.62, y - 20 if t > 616 else H * 0.84, 120, t, shell_only=True, seed=3)
    if t > 617.5:  # biblioteca de substâncias se apagando
        for i in range(14):
            a = 1 - appear(t, 619 + i * 0.3, 0.6)
            rrect(ctx, W * 0.10 + i * 75, H * 0.12, 50, 90, 6)
            ink(ctx, [(0.55, 0.95, 0.35), (0.95, 0.75, 0.30), (0.45, 0.75, 0.95)][i % 3], a * appear(t, 617.6), 2)


def u_reefs(ctx, t):
    label(ctx, "CALOR · POLUIÇÃO · COLETA DE CONCHAS", W / 2, H * 0.92, t, 611.0, 617.4, 22, RED)
    label(ctx, "UMA BIBLIOTECA INTEIRA QUE NINGUÉM ESTUDOU", W / 2, H * 0.92, t, 617.6, None, 20, WHITE)


# ================================================================== 10:24 – 10:58 final
def w_end(ctx, t):
    if t < 639:
        underwater_close(ctx, t, floor=H * 0.84)
        night_tint(ctx, 0.5)
        x = kf(t, [(624, W * 0.25), (639, W * 0.36)])
        cone_snail(ctx, x, H * 0.86, 520, t, crawl=1, seed=3)
        if t > 636:
            fx = kf(t, [(636, W * 1.1), (639, W * 0.80)])
            fishy(ctx, fx, H * 0.50, 1.0, t, flip=-1)
        return
    if t < 647:  # o perigo: a sua mão
        underwater_close(ctx, t, floor=H * 0.84)
        cone_snail(ctx, W * 0.55, H * 0.86, 300, t, shell_only=True, seed=3)
        glint(ctx, W * 0.55, H * 0.78, t, 1)
        y = kf(t, [(639, -100), (643, H * 0.50)]) + 8 * math.sin(t * 2)
        hand_close(ctx, W * 0.52, y, 1.4, curl=0.1, from_dir=(-0.4, -1))
        return
    # admire, fotografe, deixe onde está
    underwater_close(ctx, t, floor=H * 0.84)
    cone_snail(ctx, W * 0.55, H * 0.86, 360, t, crawl=0.5, seed=3)
    if 652.6 < t < 653.1:
        rgba(ctx, WHITE, 0.6 * (1 - (t - 652.6) / 0.5))
        ctx.paint()


def u_end(ctx, t):
    if t < 629.5:
        kicker(ctx, "POR QUE VOCÊ NUNCA IA QUERER PEGAR A CONCHA DE UM", W / 2, H * 0.12, t, 624.4, None, 18)
        big_title(ctx, [("CARAMUJO-", WHITE, "black"), ("CONE", ORANGE, "light")], W / 2, H * 0.12 + 60, t, 624.8, None,
                  56)
        return
    label(ctx, "NÃO É UM MONSTRO", W / 2, H * 0.10, t, 629.6, 632.2, 26, WHITE)
    label(ctx, "LENTO · NÃO TE PERSEGUE · NEM SABE QUE VOCÊ ESTÁ ALI", W / 2, H * 0.10, t, 632.2, 636.2, 18, WHITE)
    label(ctx, "SÓ QUER CAÇAR O PRÓXIMO PEIXE", W / 2, H * 0.10, t, 636.2, 639.0, 22, ORANGE)
    big_title(ctx, [("O PERIGO É ", WHITE, "black"), ("A SUA MÃO", RED, "light")], W / 2, H * 0.12, t, 639.2, 647.0,
              44)
    label(ctx, "A CONCHA BONITA QUE PARECE VAZIA", W / 2, H * 0.92, t, 642.4, 647.0, 20, WHITE)
    label(ctx, "ADMIRE · FOTOGRAFE · DEIXE ONDE ESTÁ", W / 2, H * 0.10, t, 650.0, None, 24, GREEN)


def w_card(ctx, t):
    underwater_close(ctx, t, floor=H * 0.84)
    cone_snail(ctx, W * 0.18, H * 0.86, 220, t, crawl=1, seed=3)


def u_card(ctx, t):
    t0 = 658.3
    text(ctx, "ASSISTA", W * 0.10, H * 0.42, 64, WHITE, appear(t, t0), "l", "black")
    text(ctx, "A SEGUIR", W * 0.10, H * 0.52, 64, ORANGE, appear(t, t0 + 0.3), "l", "black")
    text(ctx, "mais do fundo do mar", W * 0.10, H * 0.59, 20, SOFT, appear(t, t0 + 0.7), "l", "semi")
    k = appear(t, t0 + 1.0)
    rrect(ctx, W * 0.52, H * 0.26, W * 0.40, H * 0.40, 12)
    ctx.set_dash([10, 8])
    rgba(ctx, WHITE, 0.6 * k)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.set_dash([])


SCENES = [
    (0.0, 14.0, w_open, u_open),
    (14.0, 24.0, w_find, u_find),
    (24.0, 40.0, w_pick, u_pick),
    (40.0, 70.0, w_sym, u_sym),
    (70.0, 77.0, w_xray, u_xray),
    (77.0, 113.0, w_name, u_name),
    (113.0, 145.0, w_what, u_what),
    (145.0, 154.0, w_slow, u_slow),
    (154.0, 175.0, w_weapon, u_weapon),
    (175.0, 203.0, w_hunt, u_hunt),
    (203.0, 223.0, w_insulin, u_insulin),
    (223.0, 246.0, w_reach, u_reach),
    (246.0, 297.0, w_venom, u_venom),
    (297.0, 325.0, w_deaths, u_deaths),
    (325.0, 349.0, w_avoid, u_avoid),
    (349.0, 387.0, w_scen, u_scen),
    (387.0, 408.0, w_choice, u_choice),
    (408.0, 443.0, w_answers, u_answers),
    (443.0, 484.0, w_bandage, u_bandage),
    (484.0, 501.0, w_call, u_call),
    (501.0, 528.0, w_breath, u_breath),
    (528.0, 556.0, w_hosp, u_hosp),
    (556.0, 610.0, w_twist, u_twist),
    (610.0, 624.0, w_reefs, u_reefs),
    (624.0, 658.0, w_end, u_end),
    (658.0, 99999.0, w_card, u_card),
]
CUTS = sorted({s for s, *_ in SCENES if s > 0} | {32.0, 61.0, 92.0, 119.0, 127.0, 137.0, 164.0, 167.0, 235.0,
                                                  242.0, 256.0, 261.0, 266.0, 278.0, 289.0, 303.0, 311.0, 318.5,
                                                  336.0, 341.6, 370.0, 454.0, 466.0, 472.0, 576.0, 584.0, 597.0,
                                                  639.0, 647.0})
