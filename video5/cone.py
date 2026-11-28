"""Caramujo-cone (Conus geographus) de perfil, modelado a partir de fotos reais (iNaturalist):
- concha em cone: ombro largo atrás com espira baixa em degraus, afinando até a ponta da frente;
  fundo creme com manchas marrom-alaranjadas em faixas, "tendas" brancas e rede fina de linhas;
- pé achatado e mosqueado embaixo da concha, passando dela atrás e na frente;
- sifão listrado saindo da ponta da frente, curvado para cima (balança devagar);
- cabeça pequena com tentáculos e olhos minúsculos; tromba fina que estica com o dente-arpão na ponta;
- "boca-rede" do geográfico: membrana que se abre como um funil para engolir peixes.
Lógica física: ele anda devagar (onda no pé), nunca nada; o sifão aponta para a frente/cima.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "video4"), os.path.join(HERE, "..", "video3"),
                os.path.join(HERE, "..", "video")]

import cairo  # noqa: E402

from gfx import *  # noqa: F401,F403,E402
from stonefish import blob, _smooth_path  # noqa: E402

CREAM = (0.95, 0.89, 0.78)
BROWN = (0.66, 0.36, 0.18)
DBROWN = (0.42, 0.20, 0.10)
FOOT = (0.55, 0.47, 0.38)


def cone_point(x, ground, L, u, h, facing=1):
    """Ponto do caramujo: u ao longo do corpo (-0.5 trás .. +0.5 frente), h altura em L acima do chão."""
    return x + facing * u * L, ground - h * L


def _shell_pts(L, ground, lift):
    hf = L * 0.055 + lift

    def P(u, h):
        return (u * L, ground - hf - h * L)

    return [P(-0.24, 0.285), P(-0.10, 0.285), P(0.04, 0.255), P(0.16, 0.20), P(0.26, 0.12), P(0.315, 0.05),
            P(0.30, 0.008), P(0.12, -0.005), P(-0.08, 0.0), P(-0.20, 0.015), P(-0.255, 0.05), P(-0.275, 0.10),
            P(-0.30, 0.13), P(-0.345, 0.155), P(-0.30, 0.18), P(-0.285, 0.225), P(-0.265, 0.265)], P


def cone_snail(ctx, x, ground, L, t, facing=1, a=1.0, crawl=0.0, siphon=1.0, proboscis=0.0, prob_to=None,
               mouth=0.0, bury=0.0, seed=3, head=1.0, xray=0.0, shell_only=False, harpoon=True):
    """Desenha o caramujo. prob_to = ponto (x, y) da tela para onde a tromba se estica (proboscis 0..1)."""
    rnd = random.Random(seed)
    ctx.save()
    ctx.translate(x, 0)
    ctx.scale(facing, 1)
    hf = L * 0.055
    wave = crawl * 2.0 * math.sin(t * 3.0)
    # ---------------- pé (embaixo de tudo), mosqueado, com onda de rastejar
    if not shell_only:
        fp = []
        for i in range(25):
            u = -0.50 + i * (0.92 / 24)
            bump = math.sin(u * 30 - t * 4 * crawl) * L * 0.004 * crawl
            fp.append((u * L, ground - hf * (0.55 + 0.45 * math.sin(math.pi * (i / 24)) ** 0.5) - bump))
        ctx.move_to(-0.50 * L, ground)
        for p in fp:
            ctx.line_to(*p)
        ctx.curve_to(0.44 * L, ground - hf, 0.46 * L, ground - hf * 0.3, 0.43 * L, ground)
        ctx.close_path()
        ctx.save()
        ctx.clip_preserve()
        rgba(ctx, FOOT, a)
        ctx.fill()
        for k in range(26):  # listras/manchas escuras do pé (como na foto)
            u = rnd.uniform(-0.48, 0.42)
            ctx.move_to(u * L, ground - hf * rnd.uniform(0.2, 0.9))
            ctx.line_to(u * L + L * rnd.uniform(0.02, 0.05), ground - hf * rnd.uniform(0.1, 0.9))
            rgba(ctx, (0.18, 0.13, 0.10), a * 0.8)
            ctx.set_line_width(L * 0.006)
            ctx.stroke()
        g = cairo.LinearGradient(0, ground - hf, 0, ground)
        g.add_color_stop_rgba(0, 1, 1, 1, 0.18 * a)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.25 * a)
        ctx.set_source(g)
        ctx.paint()
        ctx.restore()
        ctx.move_to(-0.50 * L, ground)
        for p in fp:
            ctx.line_to(*p)
        ctx.curve_to(0.44 * L, ground - hf, 0.46 * L, ground - hf * 0.3, 0.43 * L, ground)
        rgba(ctx, INK, a)
        ctx.set_line_width(2)
        ctx.stroke()
    # ---------------- cabeça, tentáculos, tromba (na frente, por baixo da ponta da concha)
    hx, hy = 0.37 * L, ground - hf * 0.9
    if not shell_only and head > 0:
        blob(ctx, hx, hy, L * 0.045, L * 0.028, seed + 5, amp=0.08)
        ink(ctx, (0.62, 0.52, 0.44), a, 2)
        for k, ang in enumerate((-0.9, -0.5)):
            sw = 0.08 * math.sin(t * 1.5 + k)
            ex, ey = hx + math.cos(ang + sw) * L * 0.07, hy + math.sin(ang + sw) * L * 0.07
            line(ctx, hx, hy - L * 0.01, ex, ey, INK, a, 3.2)
            line(ctx, hx, hy - L * 0.01, ex, ey, (0.62, 0.52, 0.44), a, 1.8)
            circle(ctx, ex, ey, L * 0.006, INK, a)
    # tromba: tubo fino que sai da cabeça e se estica até prob_to
    if not shell_only and proboscis > 0:
        if prob_to is not None:
            tx, ty = (prob_to[0] - x) * facing, prob_to[1]
        else:
            tx, ty = hx + L * 0.45, hy - L * 0.10
        ex, ey = lerp(hx, tx, proboscis), lerp(hy, ty, proboscis)
        mx, my = (hx + ex) / 2, min(hy, ey) - L * 0.06 * proboscis
        ctx.move_to(hx, hy)
        ctx.curve_to(mx, my + L * 0.03, mx, my, ex, ey)
        rgba(ctx, INK, a)
        ctx.set_line_width(L * 0.022 + 3)
        ctx.stroke()
        ctx.move_to(hx, hy)
        ctx.curve_to(mx, my + L * 0.03, mx, my, ex, ey)
        rgba(ctx, (0.88, 0.62, 0.58), a)
        ctx.set_line_width(L * 0.022)
        ctx.stroke()
        if harpoon:
            ang = math.atan2(ey - my, ex - mx)
            harpoon_tooth(ctx, ex, ey, L * 0.07, ang, a)
    # boca-rede (falsa boca do geográfico): funil translúcido que se abre para a frente
    if not shell_only and mouth > 0:
        r = L * 0.26 * mouth
        cx_, cy_ = hx + r * 0.55, hy - r * 0.35
        ctx.move_to(hx, hy)
        ctx.curve_to(hx + r * 0.2, hy - r * 0.9, cx_ + r * 0.6, cy_ - r * 0.9, cx_ + r * 0.9, cy_ - r * 0.3)
        ctx.curve_to(cx_ + r * 1.0, cy_ + r * 0.3, cx_ + r * 0.5, hy + r * 0.25, hx, hy)
        ctx.close_path()
        rgba(ctx, (0.92, 0.70, 0.66), 0.40 * a)
        ctx.fill_preserve()
        rgba(ctx, INK, a)
        ctx.set_line_width(2)
        ctx.stroke()
        for k in range(5):
            f = k / 4
            ctx.move_to(hx + r * 0.1, hy - r * 0.05)
            ctx.line_to(cx_ + r * (0.95 - 0.1 * abs(f - 0.5)), cy_ - r * 0.6 + f * r * 1.0)
            rgba(ctx, (0.55, 0.30, 0.30), 0.35 * a)
            ctx.set_line_width(1.2)
            ctx.stroke()
    # ---------------- sifão listrado (da ponta da frente, curvado para cima)
    if not shell_only and siphon > 0:
        bx, by = 0.30 * L, ground - hf - L * 0.03
        sw = math.sin(t * 0.9) * 0.10
        pts = []
        for i in range(12):
            f = i / 11
            ang = -0.25 - 1.1 * f * siphon + sw * f
            if i == 0:
                px, py = bx, by
            else:
                px, py = pts[-1][0] + math.cos(ang) * L * 0.024 * siphon, pts[-1][1] + math.sin(ang) * L * 0.024 * siphon
            pts.append((px, py))
        for wpass, col in ((L * 0.030 + 3, INK), (L * 0.030, (0.92, 0.86, 0.74))):
            ctx.move_to(*pts[0])
            for p in pts[1:]:
                ctx.line_to(*p)
            rgba(ctx, col, a)
            ctx.set_line_width(wpass)
            ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ctx.stroke()
        for i in range(1, 11, 2):  # listras escuras
            p, q = pts[i], pts[i + 1]
            ctx.move_to(*p)
            ctx.line_to(*q)
            rgba(ctx, (0.25, 0.16, 0.10), a)
            ctx.set_line_width(L * 0.027)
            ctx.set_line_cap(cairo.LINE_CAP_BUTT)
            ctx.stroke()
        ctx.set_line_cap(cairo.LINE_CAP_BUTT)
    # ---------------- concha
    shp, P = _shell_pts(L, ground, 0 if not shell_only else -hf)
    _smooth_path(ctx, shp)
    ctx.save()
    ctx.clip_preserve()
    rgba(ctx, CREAM, a)
    ctx.fill()
    # faixas mosqueadas marrom-alaranjadas (3 faixas, como no geográfico), manchas pequenas e irregulares
    for band_u, w in ((-0.17, 0.07), (0.03, 0.08), (0.20, 0.06)):
        for k in range(34):
            u = band_u + rnd.uniform(-w, w)
            h = rnd.uniform(0.0, 0.29)
            blob(ctx, *P(u, h), L * rnd.uniform(0.010, 0.026), L * rnd.uniform(0.008, 0.020), seed * 7 + k, amp=0.4)
            rgba(ctx, BROWN if k % 4 else DBROWN, a * rnd.uniform(0.55, 0.9))
            ctx.fill()
    for k in range(40):  # manchinhas soltas fora das faixas
        u, h = rnd.uniform(-0.25, 0.30), rnd.uniform(0.0, 0.29)
        circle(ctx, *P(u, h), L * rnd.uniform(0.003, 0.008), BROWN, a * 0.6)
    # "tendas" brancas (triângulos) espalhadas
    for k in range(110):
        u, h = rnd.uniform(-0.26, 0.30), rnd.uniform(0.0, 0.29)
        px, py = P(u, h)
        s_ = L * rnd.uniform(0.004, 0.010)
        ctx.move_to(px - s_, py + s_ * 0.6)
        ctx.line_to(px, py - s_ * 0.8)
        ctx.line_to(px + s_, py + s_ * 0.6)
        ctx.close_path()
        rgba(ctx, (1, 0.97, 0.92), a * 0.9)
        ctx.fill()
    # rede fina (linhas espirais ao longo do comprimento)
    for k in range(9):
        h = 0.02 + k * 0.032
        ctx.move_to(*P(-0.26, h + 0.02))
        ctx.curve_to(*P(-0.05, h), *P(0.15, h * 0.65), *P(0.31, h * 0.15))
        rgba(ctx, DBROWN, a * 0.25)
        ctx.set_line_width(1)
        ctx.stroke()
    # volume: luz em cima, sombra embaixo
    g = cairo.LinearGradient(0, ground - hf - L * 0.30, 0, ground - hf)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.20 * a)
    g.add_color_stop_rgba(0.45, 1, 1, 1, 0.0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.30 * a)
    ctx.set_source(g)
    ctx.paint()
    # brilho
    ctx.move_to(*P(-0.20, 0.25))
    ctx.curve_to(*P(-0.02, 0.22), *P(0.12, 0.17), *P(0.22, 0.11))
    rgba(ctx, WHITE, a * 0.45)
    ctx.set_line_width(L * 0.010)
    ctx.stroke()
    # raio-x: corpo mole, glândula de veneno (bulbo), duto enrolado e saco de dentes
    if xray > 0:
        rgba(ctx, (0.05, 0.10, 0.14), 0.75 * xray * a)
        ctx.paint()
        blob(ctx, *P(-0.02, 0.12), L * 0.24, L * 0.09, seed + 9, amp=0.08)
        rgba(ctx, (0.85, 0.55, 0.55), 0.55 * xray * a)
        ctx.fill()
        bx_, by_ = P(-0.16, 0.16)
        circle(ctx, bx_, by_, L * 0.035, (0.95, 0.75, 0.30), xray * a)  # bulbo do veneno
        ctx.move_to(bx_ + L * 0.03, by_)
        for k in range(14):
            ctx.line_to(bx_ + L * (0.04 + k * 0.02), by_ + math.sin(k * 1.3) * L * 0.025)
        rgba(ctx, (0.55, 0.95, 0.35), xray * a)
        ctx.set_line_width(3)
        ctx.stroke()
        sx_, sy_ = P(0.20, 0.07)
        ellipse_path(ctx, sx_, sy_, L * 0.05, L * 0.025, 0)
        rgba(ctx, (0.95, 0.95, 0.95), 0.35 * xray * a)
        ctx.fill()
        for k in range(6):
            line(ctx, sx_ - L * 0.04 + k * L * 0.015, sy_ + L * 0.012, sx_ - L * 0.03 + k * L * 0.015,
                 sy_ - L * 0.015, WHITE, xray * a, 1.6)
    ctx.restore()
    _smooth_path(ctx, shp)
    rgba(ctx, INK, a)
    ctx.set_line_width(2.2)
    ctx.stroke()
    # degraus da espira
    for k in range(3):
        u0 = -0.27 - k * 0.032
        ctx.move_to(*P(u0, 0.27 - k * 0.04))
        ctx.curve_to(*P(u0 - 0.006, 0.20 - k * 0.01), *P(u0 - 0.006, 0.12 + k * 0.01), *P(u0, 0.06 + k * 0.04))
        rgba(ctx, INK, a * 0.55)
        ctx.set_line_width(1.3)
        ctx.stroke()
    # meio enterrado
    if bury > 0:
        ctx.move_to(-0.62 * L, ground + 2)
        ctx.curve_to(-0.40 * L, ground - L * 0.18 * bury, 0.30 * L, ground - L * 0.20 * bury, 0.55 * L, ground + 2)
        ctx.close_path()
        rgba(ctx, (0.86, 0.80, 0.66), a * min(1, bury * 1.5))
        ctx.fill()
    ctx.restore()


def harpoon_tooth(ctx, x, y, size, ang, a=1.0, detail=False):
    """Dente radular: agulha oca com farpas na ponta (o 'arpão')."""
    ctx.save()
    ctx.translate(x, y)
    ctx.rotate(ang)
    s = size
    ctx.move_to(-s * 0.6, -s * 0.06)
    ctx.line_to(s * 0.25, -s * 0.05)
    ctx.line_to(s * 0.18, -s * 0.13)  # farpa
    ctx.line_to(s * 0.40, -s * 0.03)
    ctx.line_to(s * 0.55, 0)
    ctx.line_to(s * 0.40, s * 0.03)
    ctx.line_to(s * 0.18, s * 0.13)  # farpa
    ctx.line_to(s * 0.25, s * 0.05)
    ctx.line_to(-s * 0.6, s * 0.06)
    ctx.close_path()
    rgba(ctx, (0.97, 0.96, 0.92), a)
    ctx.fill_preserve()
    rgba(ctx, INK, a)
    ctx.set_line_width(max(1.2, s * 0.03))
    ctx.stroke()
    if detail:  # canal oco por dentro
        line(ctx, -s * 0.55, 0, s * 0.35, 0, (0.55, 0.95, 0.35), a, max(1.5, s * 0.025))
    ctx.restore()


def insulin_cloud(ctx, cx, cy, r, t, a=1.0, seed=1):
    rnd = random.Random(seed)
    for k in range(26):
        ang = rnd.uniform(0, 2 * math.pi)
        rr = r * rnd.uniform(0.1, 1.0) * (0.9 + 0.1 * math.sin(t * 1.3 + k))
        px = cx + math.cos(ang) * rr + 6 * math.sin(t * 0.7 + k)
        py = cy + math.sin(ang) * rr * 0.6 - 4 * math.cos(t * 0.5 + k)
        g = cairo.RadialGradient(px, py, 1, px, py, r * 0.35)
        g.add_color_stop_rgba(0, 0.75, 0.90, 0.95, 0.20 * a)
        g.add_color_stop_rgba(1, 0.75, 0.90, 0.95, 0)
        ctx.set_source(g)
        ctx.arc(px, py, r * 0.35, 0, 2 * math.pi)
        ctx.fill()
    for k in range(30):
        ang = rnd.uniform(0, 2 * math.pi)
        rr = r * rnd.uniform(0.0, 1.0)
        circle(ctx, cx + math.cos(ang + t * 0.1) * rr, cy + math.sin(ang + t * 0.1) * rr * 0.6, 1.6, WHITE, 0.5 * a)
