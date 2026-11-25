"""Gradação de cor 'misteriosa' (menos colorido, mais escuro e frio), aplicada por cima de cada quadro.

- Dessatura as cores (cartoon colorido vira ilustração sóbria).
- Puxa sombras para azul-petróleo e escurece os médios.
- Névoa de profundidade, vinheta forte e granulação de filme.
- Partículas em suspensão e feixes de luz fracos dão volume à água.
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video"))

import cairo  # noqa: E402

from gfx import W, H, grain, rgba, circle, PARTS  # noqa: E402


def grade(ctx, t, desat=0.30, dark=0.08, tint=(0.10, 0.32, 0.38), vig=0.45, particles=True):
    # 1) dessaturação: sobrepõe cinza com operador HSL 'saturation'
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_HSL_SATURATION)
    ctx.set_source_rgba(0.5, 0.5, 0.5, desat)
    ctx.paint()
    ctx.restore()
    # 2) sombras frias (multiply) e escurecimento geral
    ctx.save()
    ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    ctx.set_source_rgba(1 - dark * 0.6, 1 - dark * 0.35, 1 - dark * 0.25, 1.0)
    ctx.paint()
    ctx.set_operator(cairo.OPERATOR_SOFT_LIGHT)
    ctx.set_source_rgba(*tint, 0.40)
    ctx.paint()
    ctx.restore()
    # 3) partículas em suspensão (primeiro plano, desfocadas)
    if particles:
        for px, py, r, sp, ph in PARTS[:50]:
            x = (px * W + math.sin(t * 0.3 + ph * 5) * 20) % W
            y = (py * H - t * sp * 6) % H
            g = cairo.RadialGradient(x, y, 0, x, y, r * 4)
            g.add_color_stop_rgba(0, 0.8, 0.9, 0.9, 0.10)
            g.add_color_stop_rgba(1, 0.8, 0.9, 0.9, 0)
            ctx.set_source(g)
            ctx.arc(x, y, r * 4, 0, 2 * math.pi)
            ctx.fill()
    # 4) vinheta forte + granulação
    g = cairo.RadialGradient(W / 2, H / 2, H * 0.40, W / 2, H / 2, H * 1.0)
    g.add_color_stop_rgba(0, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.0, 0.02, 0.03, vig)
    ctx.set_source(g)
    ctx.paint()
    grain(ctx, 0.08, t)


def depth_fog(ctx, y_from, y_to, a=0.6, col=(0.02, 0.07, 0.09)):
    """Escurece o que está mais fundo (abaixo de y_from)."""
    g = cairo.LinearGradient(0, y_from, 0, y_to)
    g.add_color_stop_rgba(0, *col, 0)
    g.add_color_stop_rgba(1, *col, a)
    ctx.set_source(g)
    ctx.rectangle(0, y_from, W, H)
    ctx.fill()
