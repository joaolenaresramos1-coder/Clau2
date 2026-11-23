"""Cenas de praia refeitas em corte lateral com o personagem de perfil (rig) e física coerente:
pés no chão, água cobrindo o corpo conforme a profundidade, quedas terminando deitado na areia."""
import math

import scenes as S
import scenes2 as S2
import rig
import beach as B
from gfx import *  # noqa: F401,F403
from mapdata import *  # noqa: F401,F403

SC = 0.95  # escala dos personagens na praia


def cam(ctx, cx, cy, z):
    ctx.save()
    ctx.translate(W / 2, H / 2)
    ctx.scale(z, z)
    ctx.translate(-cx, -cy)


def fig_ground(ctx, x, p, outfit, facing, t, a=1.0, s=SC, prop=None):
    rig.figure(ctx, x, B.ground_y(x), s, p, outfit=outfit, facing=facing, a=a, t=t, prop=prop,
               shadow=B.water_depth(x) < 5)


def phone_prop(ctx, x, y):
    rrect(ctx, x - 3, y - 7, 6, 11, 1.5)
    ink(ctx, (0.15, 0.15, 0.18), 1, 1)


def bottle_prop(ctx, x, y):
    rrect(ctx, x - 4, y - 14, 8, 16, 2)
    ink(ctx, (0.92, 0.95, 0.97), 1, 1.2)
    ctx.rectangle(x - 2.5, y - 18, 5, 4)
    rgba(ctx, ORANGE)
    ctx.fill()


def p_sit_ground(t=0.0, phone=False):
    p = rig.pose(lean=-8, thighF=86, kneeF=6, thighB=82, kneeB=4, footF=0, footB=0, armF=-25, elbowF=10,
                 armB=-30, elbowB=10)
    if phone:
        p.update(armF=35, elbowF=95)
    return p


def p_eat(t):
    k = (math.sin(t * 2.2) + 1) / 2
    p = p_sit_ground(t)
    p.update(armF=lerp(30, 70, k), elbowF=lerp(80, 150, k))
    return p


def p_doubled(t):
    p = p_sit_ground(t)
    w = math.sin(t * 5) * 3
    p.update(lean=42 + w, neck=22, armF=40, elbowF=100, armB=35, elbowB=100, thighF=118, kneeF=62, thighB=114,
             kneeB=58, footF=-20, footB=-20)
    return p


# ------------------------------------------------------------------ 00:13 – 00:27 entrando no mar (corte lateral)
def sc_enter(ctx, t):
    B.sky(ctx, t, sunset=0.9)
    B.sand(ctx, t)
    B.props(ctx, t, post_x=W * 0.12, towel_x=W * 0.20, cooler_x=-200)
    x = kf(t, [(13.0, W * 0.24), (20.5, W * 0.66)])
    walking = t < 20.5
    p = rig.p_walk(t, 0.9) if walking else rig.p_stand(t)
    if not walking:
        p.update(armF=35 + 8 * math.sin(t), elbowF=30, armB=25, elbowB=30)  # braços sobre a água morna
    fig_ground(ctx, x, p, "swimmer", 1, t)
    B.water(ctx, t)
    kicker(ctx, "ÁGUA A 30 °C · NINGUÉM NO MAR", W / 2, H * 0.12, t, 17.5, None, 18, (0.2, 0.25, 0.3))
    vignette(ctx, 0.35, t)


def sc_open3(ctx, t):
    if 13 <= t < 27:
        return sc_enter(ctx, t)
    return S2.sc_open(ctx, t)


# ------------------------------------------------------------------ 05:50 – 05:58 banhistas no começo do século
def sc_history3(ctx, t):
    if t >= 358:
        return S.sc_history(ctx, t)
    B.sky(ctx, t, sunset=0.6)
    B.sand(ctx, t)
    for i, x in enumerate((W * 0.60, W * 0.68, W * 0.77)):
        t0 = 355.8 + i * 0.6
        p = rig.p_stand(t + i) if t < t0 else rig.p_fall(t, t0, t0 + 1.4)
        fig_ground(ctx, x, p, "oldtime" if i != 1 else "swimmer", -1 if i % 2 else 1, t)
        if t > t0 + 1.2:
            bubbles(ctx, x, B.SURF + 30, t, n=6, rise=30, a=1 - appear(t, t0 + 3, 1.5), seed=i)
    B.water(ctx, t)
    rgba(ctx, (0.85, 0.72, 0.50), 0.28)
    ctx.paint()
    chapter(ctx, "AUSTRÁLIA TROPICAL", "INÍCIO DO", "SÉCULO 20", W / 2, H * 0.20, t, 350.5, None, 52)
    vignette(ctx, 0.55, t)


# ------------------------------------------------------------------ 09:35 – 10:22 o amigo é queimado
FX_FALL = W * 0.40


def friend_state(t):
    """Posição, pose e direção do amigo (lógica: anda, entra até a cintura, é queimado, volta, desmaia)."""
    if t < 586:
        return None
    if t < 591.5:
        x = kf(t, [(586, W * 0.30), (591.5, W * 0.66)], fn=lambda k: k)
        return x, rig.p_walk(t, 0.9 if x < B.SHORE_X else 0.6), 1
    if t < 595:
        p = rig.p_stand(t)
        p.update(armF=40, elbowF=30, armB=30, elbowB=30)
        return W * 0.66, p, 1
    if t < 595.7:
        return W * 0.66, rig.p_flinch(t), 1
    if t < 599:
        x = kf(t, [(595.7, W * 0.66), (599, FX_FALL)], fn=lambda k: k)
        p = rig.p_walk(t, 1.1)
        p["lean"] = 14 + 8 * math.sin(t * 9)
        return x, p, -1
    return FX_FALL, rig.p_fall(t, 599, 600.2), -1


def you_state(t, x_friend):
    if t < 595.5:
        return W * 0.20, p_sit_ground(t, phone=True), 1
    if t < 598.8:
        return kf(t, [(595.5, W * 0.20), (598.8, x_friend - 150)], fn=lambda k: k), rig.p_run(t), 1
    if t < 600.5:
        return x_friend - 150 + (t - 598.8) * 20, rig.p_stand(t), 1
    return x_friend - 115, rig.p_kneel(t), 1


def draw_legs_marks(ctx, t, x, gy):
    """Tentáculos e vergões nas pernas do amigo deitado (cabeça para a direita, pés para a esquerda)."""
    for i in range(4):
        y = gy - 6 - i * 3
        line(ctx, x - 20, y, x - 80, y + 2, JELLY, 0.9 * appear(t, 600), 1.3)
        line(ctx, x - 25, y - 1, x - 75, y + 1, RED, 0.85 * appear(t, 603.5), 2.5)


def sc_scenario3(ctx, t):
    if t >= 622.5:
        return S.sc_scenario(ctx, t)
    if t < 584.5:
        return S2.sc_scenario2(ctx, t)
    B.sky(ctx, t, sunset=0.15)
    B.sand(ctx, t)
    B.net_background(ctx, t, a=appear(t, 584.5))
    B.props(ctx, t, glow=appear(t, 616))
    fs = friend_state(t)
    if fs:
        fx, fp, ff = fs
        fig_ground(ctx, fx, fp, "friend", ff, t)
        if 595 <= t < 597:
            splash(ctx, W * 0.66, B.SURF, t, 595.0, 1, 0.5)
            if t < 596:
                circle(ctx, W * 0.66, B.SURF + 60, 50 * appear(t, 595, 0.3), RED, 0.35 * (1 - appear(t, 595.3, 0.7)))
        if t > 600:
            draw_legs_marks(ctx, t, fx, B.ground_y(fx))
    yx, yp, yf = you_state(t, FX_FALL)
    fig_ground(ctx, yx, yp, "swimmer", yf, t, prop=phone_prop if t < 595.5 else None)
    # água-viva no mar, perto de onde o amigo entrou
    box_jelly(ctx, W * 0.72 + math.sin(t * 0.3) * 20, B.SURF + 120, 0.5, t, a=0.75)
    B.water(ctx, t)
    if 594 < t < 596.5:
        text(ctx, "AAAH!", W * 0.66, H * 0.30, 34, WHITE, window(t, 595, 596.5), "c", "black")
    callout(ctx, W * 0.26, B.ground_y(W * 0.26) - 20, 34, W * 0.30, H * 0.22, "ISOPOR COM ÁGUA", appear(t, 613.3))
    callout(ctx, W * 0.10 + 14, B.ground_y(W * 0.10) - 75, 26, W * 0.08, H * 0.18, "VINAGRE · 30 M", appear(t, 616.3))
    callout(ctx, W * 0.20 + 10, B.ground_y(W * 0.20) - 6, 18, W * 0.17, H * 0.32, "CELULAR", appear(t, 619.5))
    globe(ctx, W - 95, 105, 40, window(t, 584.8, 591), lon0=140, lat0=-18, hl=(145.8, -16.9), name="PERTO DE CAIRNS")
    vignette(ctx, 0.3, t)


# ------------------------------------------------------------------ 11:19 – 11:54 pedir ajuda e RCP
def sc_answers3(ctx, t):
    if not (679 <= t < 714):
        return S2.sc_answers2(ctx, t)
    fx = FX_FALL
    gy = B.ground_y(fx)
    z = kf(t, [(679, 1.0), (681, 1.35)])
    cam(ctx, fx + 40, gy - 90, z)
    B.sky(ctx, t, sunset=0.15)
    B.sand(ctx, t)
    B.props(ctx, t, glow=appear(t, 686))
    # amigo deitado (cabeça para a direita)
    rig.figure(ctx, fx, gy, SC, rig.p_lie(t), outfit="friend", facing=-1, t=0)
    draw_legs_marks(ctx, 999, fx, gy)
    chest_x = fx + 30 * SC
    # você: grita por ajuda, depois ajoelha, confere a respiração e faz RCP
    if t < 690.5:
        fig_ground(ctx, fx - 120, rig.p_shout(t) if t > 680.5 else rig.p_stand(t), "swimmer", 1, t)
    else:
        if t < 696:
            p = rig.p_kneel(t)
            p.update(lean=55, neck=25, armF=40, elbowF=20, armB=30, elbowB=20)
        else:
            p = rig.p_cpr(t)
        hx, hy = rig.hand_point(0, gy, SC, p, facing=1)
        rig.figure(ctx, chest_x - hx + (6 if t < 696 else 0), gy, SC, p, outfit="swimmer", facing=1, t=t)
    # alguém liga para a emergência
    if t > 683.3:
        bx = kf(t, [(683.3, W + 80), (686, fx + 230)], fn=lambda k: k)
        p = rig.p_walk(t) if t < 686 else rig.p_phone(t)
        fig_ground(ctx, bx, p, "casual", -1, t, prop=phone_prop if t >= 686 else None)
        hx, hy = rig.head_point(bx, B.ground_y(bx), SC, p, facing=-1)
        callout(ctx, hx - 6, hy, 16, hx + 40, hy - 70, "EMERGÊNCIA", appear(t, 686.2))
    # alguém corre até o vinagre e volta
    if t > 686.3:
        vx = kf(t, [(686.3, fx - 60), (691, W * 0.12 + 30), (692.5, W * 0.12 + 30), (708, fx - 70)],
                fn=lambda k: k)
        going = t < 691
        back = 692.5 <= t < 708
        p = rig.p_run(t) if (going or back) else (rig.p_reach_down(t) if t < 692.5 else rig.p_stand(t))
        fig_ground(ctx, vx, p, "kid", -1 if going else 1, t, s=SC * 0.8,
                   prop=bottle_prop if t >= 692.5 else None)
    if t < 690.5 and t > 680.5:
        hx, hy = rig.head_point(fx - 120, gy, SC, rig.p_shout(t), facing=1)
        text(ctx, "AJUDA!", hx, hy - 30, 26, WHITE, window(t, 680.6, 683.5), "c", "black")
    ctx.restore()
    label(ctx, "ELE ESTÁ RESPIRANDO?", W / 2, H * 0.16, t, 690.5, 695.3, 34, WHITE)
    label(ctx, "NÃO ESTÁ.", W / 2, H * 0.16, t, 695.3, 697.5, 40, RED)
    big_title(ctx, [("RCP ", ORANGE, "black"), ("AGORA", WHITE, "light")], W / 2, H * 0.16, t, 697.5, None, 64)
    kicker(ctx, "NÃO ESPERE O VINAGRE · NÃO ESPERE A AMBULÂNCIA", W / 2, H * 0.23, t, 699.5, None, 17, (0.15, 0.2, 0.25))
    label(ctx, "MANTÉM O SANGUE CIRCULANDO", W / 2, H * 0.92, t, 705, None, 24, WHITE)
    vignette(ctx, 0.3, t)


# ------------------------------------------------------------------ 13:01 – 13:33 e se fosse Irukandji
def sc_twist3(ctx, t):
    B.sky(ctx, t, sunset=0.1)
    B.sand(ctx, t)
    B.props(ctx, t, cooler_x=W * 0.34)
    fx = W * 0.22
    if t < 789:
        p = p_sit_ground(t)
    elif t < 798:
        p = p_eat(t)
    else:
        p = rig.blend(p_eat(t), p_doubled(t), appear(t, 798, 1.2))
    rig.figure(ctx, fx, B.ground_y(fx), SC * 1.2, p, outfit="friend", facing=1, t=t)
    if t > 798.5:
        hip_y = B.ground_y(fx) - 20
        pk = appear(t, 798.5) * (0.5 + 0.5 * math.sin(t * 6))
        circle(ctx, fx + 30, hip_y - 40, 26, RED, 0.45 * pk)
        circle(ctx, fx + 5, hip_y - 60, 22, RED, 0.35 * pk)
    # manchinha que ninguém notou
    callout(ctx, fx + 90, B.ground_y(fx) - 10, 10, fx + 170, H * 0.42, "SÓ UMA MANCHINHA", window(t, 790, 796))
    B.water(ctx, t)
    if t > 793:
        timer(ctx, W * 0.70, H * 0.30, 85, clamp((t - 795) / 3), 1, "30 MIN")
    big_title(ctx, [("E SE FOSSE ", WHITE), ("IRUKANDJI", ORANGE), ("?", WHITE)], W / 2, 70, t, 781.5, None, 40)
    kicker(ctx, "NENHUM GRITO · NENHUMA MARCA", W / 2, 110, t, 788, None, 17, (0.15, 0.2, 0.25))
    label(ctx, "AVISE SOBRE QUALQUER QUEIMADURA", W / 2, H * 0.90, t, 800, None, 26, WHITE)
    label(ctx, "A IRUKANDJI VOCÊ NUNCA ENXERGA", W / 2, H * 0.96, t, 809, None, 20, WHITE)
    vignette(ctx, 0.35, t)


REPLACE = {
    "sc_open": sc_open3,
    "sc_history2": sc_history3,
    "sc_scenario2": sc_scenario3,
    "sc_answers2": sc_answers3,
    "sc_twist": sc_twist3,
}
SCENES = [(s, e, REPLACE.get(fn.__name__, fn)) for s, e, fn in S2.SCENES]
CUTS = sorted(set(S2.CUTS) | {13.0, 27.0, 584.5})
