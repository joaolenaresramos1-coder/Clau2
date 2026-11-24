"""Tubarões de perfil no estilo do canal (contorno escuro, contra-sombreamento, nado com a cauda)
e elementos de cenário do vídeo do tubarão-cabeça-chata."""
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video"))

import cairo  # noqa: E402

from gfx import *  # noqa: F401,F403,E402

SHARK_TOP = (0.47, 0.52, 0.55)
SHARK_BELLY = (0.93, 0.94, 0.92)
TIGER_TOP = (0.50, 0.50, 0.44)


def _half(u, kind):
    """Meia-espessura do corpo ao longo do comprimento (u=0 focinho, u=1 base da cauda)."""
    if kind == "bull":       # cabeça curta e larga, corpo grosso
        return 1.0 * (u ** 0.42) * ((1 - u) ** 0.95) * 1.45
    if kind == "white":      # focinho cônico, corpo fusiforme
        return 1.0 * (u ** 0.62) * ((1 - u) ** 0.95) * 1.55
    if kind == "tiger":
        return 1.0 * (u ** 0.45) * ((1 - u) ** 1.05) * 1.40
    return (u ** 0.5) * (1 - u) * 1.5


def shark(ctx, x, y, L, t, kind="bull", facing=1, a=1.0, swim=1.0, mouth=0.0, top=None, silhouette=False,
          eye=True, roll=0.0):
    """Desenha um tubarão de comprimento L (px), com o focinho para +x (facing=1). (x,y) = centro."""
    top = top or (TIGER_TOP if kind == "tiger" else SHARK_TOP)
    Hh = L * {"bull": 0.175, "white": 0.15, "tiger": 0.14}.get(kind, 0.15)
    ph = t * 4.0 * swim

    def mid(u):
        return math.sin(ph - u * 4.5) * (u ** 2.2) * L * 0.045 * swim

    def P(u, off):
        """ponto no corpo: u ao longo, off em múltiplos da meia-espessura (neg = dorso)."""
        xx = (0.5 - u) * L
        return xx, mid(u) + off * Hh * _half(max(u, 1e-3), kind)

    ctx.save()
    ctx.translate(x, y)
    ctx.scale(facing, 1)
    ctx.rotate(roll)
    body_c = (0.08, 0.09, 0.10) if silhouette else top
    belly_c = (0.08, 0.09, 0.10) if silhouette else SHARK_BELLY

    def fin(pts, col):
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        ctx.close_path()
        ink(ctx, col, a, 2.2)

    # cauda (heterocerca: lobo de cima maior), barbatanas de trás primeiro
    tb = P(0.97, 0)
    sw = math.sin(ph - 4.5) * L * 0.05 * swim
    fin([(tb[0] + 6, tb[1] - Hh * 0.18), (tb[0] - L * 0.17, tb[1] - L * 0.19 + sw),
         (tb[0] - L * 0.15, tb[1] - L * 0.155 + sw), (tb[0] - L * 0.03, tb[1]),
         (tb[0] - L * 0.10, tb[1] + L * 0.10 + sw * 0.6), (tb[0] - L * 0.05, tb[1] + L * 0.09 + sw * 0.6),
         (tb[0] + 6, tb[1] + Hh * 0.15)], body_c)
    # barbatana peitoral de trás (mais escura)
    pb = P(0.27, 0.75)
    fin([(pb[0] + 6, pb[1] - 4), (pb[0] - L * 0.16, pb[1] + L * 0.14), (pb[0] - L * 0.07, pb[1] + 2)],
        (body_c[0] * 0.75, body_c[1] * 0.75, body_c[2] * 0.75))
    # corpo
    N = 40
    ctx.move_to(*P(0.0, 0))
    for i in range(1, N + 1):
        ctx.line_to(*P(i / N, -1))
    for i in range(N, -1, -1):
        ctx.line_to(*P(i / N, 0.95))
    ctx.close_path()
    ctx.save()
    ctx.clip_preserve()
    rgba(ctx, belly_c, a)
    ctx.fill_preserve()
    # dorso cinza com borda ondulada (contra-sombreamento)
    ctx.new_path()
    ctx.move_to(*P(0.0, 0))
    for i in range(1, N + 1):
        ctx.line_to(*P(i / N, -1.2))
    for i in range(N, -1, -1):
        u = i / N
        ctx.line_to(*P(u, 0.18 + 0.12 * math.sin(u * 22)))
    ctx.close_path()
    rgba(ctx, body_c, a)
    ctx.fill()
    if kind == "tiger" and not silhouette:
        for i in range(14):
            u = 0.30 + i * 0.045
            p0, p1 = P(u, -0.9), P(u + 0.01, -0.1)
            line(ctx, p0[0], p0[1], p1[0], p1[1], (0.30, 0.30, 0.26), a * 0.7, 3)
    ctx.restore()
    ctx.move_to(*P(0.0, 0))
    for i in range(1, N + 1):
        ctx.line_to(*P(i / N, -1))
    for i in range(N, -1, -1):
        ctx.line_to(*P(i / N, 0.95))
    ctx.close_path()
    rgba(ctx, INK, a)
    ctx.set_line_width(2.4)
    ctx.stroke()
    # 1ª dorsal (grande), 2ª dorsal, pélvica, anal
    d0, d1 = P(0.33, -1), P(0.50, -1)
    fin([d0, (d0[0] - L * 0.03, d0[1] - L * 0.15), (d0[0] - L * 0.10, d0[1] - L * 0.12), d1], body_c)
    e0, e1 = P(0.72, -1), P(0.79, -1)
    fin([e0, (e0[0] - L * 0.02, e0[1] - L * 0.05), (e0[0] - L * 0.06, e0[1] - L * 0.045), e1], body_c)
    q0 = P(0.62, 0.95)
    fin([q0, (q0[0] - L * 0.08, q0[1] + L * 0.05), (q0[0] - L * 0.07, q0[1])], body_c)
    # peitoral da frente
    pf = P(0.25, 0.8)
    fin([(pf[0] + 8, pf[1] - 3), (pf[0] - L * 0.13, pf[1] + L * 0.16), (pf[0] - L * 0.10, pf[1] + L * 0.10),
         (pf[0] - L * 0.05, pf[1] + 3)], body_c)
    if not silhouette:
        # fendas branquiais
        for i in range(5):
            g0, g1 = P(0.17 + i * 0.018, -0.45), P(0.175 + i * 0.018, 0.35)
            line(ctx, g0[0], g0[1], g1[0], g1[1], INK, a * 0.75, 1.6)
        # olho
        if eye:
            ex, ey = P(0.07, -0.35)
            circle(ctx, ex, ey, L * 0.009 + 1.5, INK, a)
            circle(ctx, ex + 0.8, ey - 0.8, L * 0.003, WHITE, a * 0.8)
        # boca
        m0 = P(0.06, 0.62)
        m1 = P(0.13, 0.55)
        if mouth > 0:
            jaw = L * 0.06 * mouth
            ctx.move_to(m0[0] + 4, m0[1] - 2)
            ctx.line_to(m1[0], m1[1] - 2)
            ctx.line_to(m0[0] - 2, m0[1] + jaw)
            ctx.close_path()
            ink(ctx, (0.55, 0.12, 0.14), a, 2)
            for i in range(6):
                f = i / 6
                tx = lerp(m0[0] + 2, m1[0] + 6, f)
                ty = lerp(m0[1] - 2, m1[1] - 2, f)
                ctx.move_to(tx - 3, ty)
                ctx.line_to(tx, ty + 7)
                ctx.line_to(tx + 3, ty)
                rgba(ctx, WHITE, a)
                ctx.fill()
        else:
            line(ctx, m0[0], m0[1], m1[0], m1[1], INK, a, 2)
    ctx.restore()


def murky(ctx, t, k=1.0, light=0.8):
    """Água turva: marrom-esverdeada, partículas suspensas, visibilidade curta."""
    top = (lerp(0.18, 0.33, k), lerp(0.42, 0.36, k), lerp(0.46, 0.24, k))
    bot = (lerp(0.03, 0.07, k), lerp(0.12, 0.09, k), lerp(0.16, 0.05, k))
    ocean(ctx, t, top=top, bot=bot, rays=True, particles=True, light=light * (1 - 0.5 * k), distant=False)
    rnd = random.Random(21)
    for i in range(int(160 * k)):
        x = (rnd.random() * W + t * rnd.uniform(-6, 6)) % W
        y = (rnd.random() * H + t * rnd.uniform(-3, 3)) % H
        circle(ctx, x, y, rnd.uniform(0.8, 2.4), (0.75, 0.70, 0.50), 0.25)


def fog(ctx, k):
    """Névoa da água turva por cima do que está longe."""
    if k <= 0:
        return
    rgba(ctx, (0.20, 0.22, 0.14), k)
    ctx.paint()


def shark_sign(ctx, x, y, s, a=1.0):
    """Placa amarela de alerta de tubarão (genérica, sem logotipo oficial)."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(s, s)
    ctx.rectangle(-6, 0, 12, 150)
    ink(ctx, (0.45, 0.45, 0.47), a, 2)
    rrect(ctx, -80, -110, 160, 120, 10)
    ink(ctx, (0.98, 0.82, 0.10), a, 3)
    rrect(ctx, -72, -102, 144, 104, 6)
    rgba(ctx, INK, a)
    ctx.set_line_width(2.5)
    ctx.stroke()
    shark(ctx, 0, -66, 92, 0.0, "bull", 1, a, swim=0, silhouette=True)
    for i in range(3):
        wx = -50 + i * 50
        ctx.move_to(wx - 22, -36)
        ctx.curve_to(wx - 11, -44, wx + 11, -28, wx + 22, -36)
        rgba(ctx, INK, a)
        ctx.set_line_width(3)
        ctx.stroke()
    text(ctx, "RISCO DE INCIDENTE", 0, -16, 10.5, INK, a, "c", "black", sp=0.8)
    text(ctx, "COM TUBARÃO", 0, -4, 10.5, INK, a, "c", "black", sp=0.8)
    ctx.restore()


def skyline(ctx, base_y, t, a=1.0, x0=0, x1=W, seed=3, col=(0.62, 0.64, 0.68), lit=0.0):
    """Prédios da orla (Boa Viagem) atrás da praia."""
    rnd = random.Random(seed)
    x = x0
    while x < x1:
        w = rnd.uniform(34, 70)
        h = rnd.uniform(60, 190)
        ctx.rectangle(x, base_y - h, w, h)
        ink(ctx, col, a, 1.6)
        for r in range(int(h // 16)):
            for c in range(int(w // 14)):
                if rnd.random() < 0.35 + 0.4 * lit:
                    ctx.rectangle(x + 5 + c * 14, base_y - h + 6 + r * 16, 6, 7)
                    rgba(ctx, (1.0, 0.85, 0.5) if lit > 0 else (0.85, 0.88, 0.92), a * (0.5 + 0.5 * lit))
                    ctx.fill()
        x += w + rnd.uniform(4, 14)
