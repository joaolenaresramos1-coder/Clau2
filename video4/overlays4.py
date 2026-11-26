"""Inserções de fotos e vídeo reais (Wikimedia Commons) por cima da animação,
com movimento de câmera (Ken Burns), vinheta, rótulo e crédito, como no canal de referência."""
import glob
import math
import os
import subprocess

import cairo

import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "video"))
from gfx import W, H, WHITE, ORANGE, SOFT, appear, window, ease, clamp, text, kicker, name_tag, rgba, vignette

HERE = os.path.dirname(os.path.abspath(__file__))
MEDIA = os.path.join(HERE, "media")
CACHE = os.path.join(HERE, "out", "media_cache")

# (início, fim, arquivo, crédito, rótulo, sobretítulo, zoom de, zoom até, foco x, foco y)
INSERTS = [
    (0.6, 7.6, "coral_0.jpg", "Foto: U.S. Geological Survey · Domínio público", None, "", 1.0, 1.15, 0.5, 0.5),
    (57.0, 62.8, "stonefish_2.jpg", "Foto: zsispeo / CC BY-SA 2.0", None, "CONSEGUE ACHAR O PEIXE?", 1.0, 1.25, 0.5,
     0.55),
    (82.5, 88.0, "stonefish_0.jpg", "Foto: walknboston / CC BY 2.0", None, "", 1.0, 1.15, 0.5, 0.5),
    (138.2, 144.0, "synanceia_3.jpg", "Foto: Dan Schofield / CC BY 4.0", None, "", 1.0, 1.15, 0.5, 0.5),
    (147.0, 151.0, "synanceia_1.jpg", "Foto: Tim Evanson / CC BY-SA 2.0", None, "", 1.0, 1.15, 0.5, 0.5),
    (165.0, 175.5, "stonefish_1.jpg", "Foto: prilfish / CC BY 2.0", None, "UM PEIXE-PEDRA ESCONDIDO PERTO DE UMA MOREIA",
     1.0, 1.2, 0.6, 0.5),
    (304.5, 310.0, "synanceia_2.jpg", "Foto: B. P. White / CC BY-SA 4.0", None, "", 1.0, 1.15, 0.5, 0.5),
    (566.5, 573.5, "stonefish_3.jpg", "Foto: 4nitsirk / CC BY-SA 2.0", None, "", 1.0, 1.15, 0.5, 0.5),
]

_IMG = {}


def _load(path):
    if path not in _IMG:
        if path.endswith(".png"):
            _IMG[path] = cairo.ImageSurface.create_from_png(path)
        else:
            png = os.path.join(CACHE, os.path.basename(path) + ".png")
            if not os.path.exists(png):
                os.makedirs(CACHE, exist_ok=True)
                subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", "scale='min(2400,iw)':-2", png],
                               check=True)
            _IMG[path] = cairo.ImageSurface.create_from_png(png)
    return _IMG[path]


def _video_frames(name):
    d = os.path.join(CACHE, name + "_frames")
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(MEDIA, name), "-vf", "fps=24,scale=1280:-2",
                        os.path.join(d, "%05d.png")], check=True)
    return sorted(glob.glob(os.path.join(d, "*.png")))


def available():
    return [i for i in INSERTS if os.path.exists(os.path.join(MEDIA, i[2])) and
            os.path.getsize(os.path.join(MEDIA, i[2])) > 20000]


ACTIVE = None
_BLUR = {}


def _blurred(key, img):
    if key not in _BLUR:
        iw, ih = img.get_width(), img.get_height()
        cur = img
        for _ in range(4):
            w2, h2 = max(4, cur.get_width() // 3), max(4, cur.get_height() // 3)
            s = cairo.ImageSurface(cairo.FORMAT_ARGB32, w2, h2)
            c = cairo.Context(s)
            c.scale(w2 / cur.get_width(), h2 / cur.get_height())
            c.set_source_surface(cur, 0, 0)
            c.get_source().set_filter(cairo.FILTER_BILINEAR)
            c.paint()
            cur = s
        _BLUR[key] = cur
    return _BLUR[key]


def draw_inserts(ctx, t):
    global ACTIVE
    if ACTIVE is None:
        ACTIVE = available()
    for (t0, t1, fn, credit, name, kick, z0, z1, fx, fy) in ACTIVE:
        if not (t0 - 0.1 <= t <= t1 + 0.1):
            continue
        a = window(t, t0, t1, 0.45)
        if a <= 0:
            continue
        p = clamp((t - t0) / (t1 - t0))
        if fn.endswith((".webm", ".ogv", ".mp4")):
            frames = _video_frames(fn)
            idx = min(len(frames) - 1, int((t - t0) * 24) % len(frames))
            img = _load(frames[idx])
        else:
            img = _load(os.path.join(MEDIA, fn))
        iw, ih = img.get_width(), img.get_height()
        base = ctx.get_matrix()
        ctx.save()
        ctx.push_group()
        rgba(ctx, (0, 0, 0))
        ctx.paint()
        portrait = iw / ih < 1.2
        if portrait:
            # fundo: a própria imagem ampliada e desfocada; frente: imagem inteira com moldura
            small = _blurred(fn, img)
            sw, sh = small.get_width(), small.get_height()
            zb = max(W / sw, H / sh) * 1.1
            ctx.save()
            ctx.translate(W / 2 - sw * zb / 2, H / 2 - sh * zb / 2)
            ctx.scale(zb, zb)
            ctx.set_source_surface(small, 0, 0)
            ctx.get_source().set_filter(cairo.FILTER_BILINEAR)
            ctx.paint()
            ctx.restore()
            rgba(ctx, (0.01, 0.06, 0.08), 0.55)
            ctx.paint()
            z = (H * 0.80 / ih) * (z0 + (z1 - z0) * 0.4 * ease(p))
            x0, y0 = W / 2 - iw * z / 2, H / 2 - ih * z / 2 - 28
            ctx.save()
            ctx.rectangle(x0 - 3, y0 - 3, iw * z + 6, ih * z + 6)
            rgba(ctx, (0.9, 0.95, 0.95), 0.85)
            ctx.fill()
            ctx.translate(x0, y0)
            ctx.scale(z, z)
            ctx.set_source_surface(img, 0, 0)
            ctx.get_source().set_filter(cairo.FILTER_GOOD)
            ctx.paint()
            ctx.restore()
        else:
            cover = max(W / iw, H / ih)
            z = cover * (z0 + (z1 - z0) * ease(p))
            cx, cy = iw * fx, ih * fy
            tx = min(0, max(W - iw * z, W / 2 - cx * z))
            ty = min(0, max(H - ih * z, H / 2 - cy * z))
            ctx.save()
            ctx.translate(tx, ty)
            ctx.scale(z, z)
            ctx.set_source_surface(img, 0, 0)
            ctx.get_source().set_filter(cairo.FILTER_GOOD)
            ctx.paint()
            ctx.restore()
        ctx.set_matrix(base)
        # leve correção de cor para combinar com a paleta (sombra azul-petróleo)
        ctx.set_source_rgba(0.02, 0.12, 0.15, 0.18)
        ctx.paint()
        vignette(ctx, 0.55, t)
        g = cairo.LinearGradient(0, H * 0.7, 0, H)
        g.add_color_stop_rgba(0, 0, 0, 0, 0)
        g.add_color_stop_rgba(1, 0, 0, 0, 0.55)
        ctx.set_source(g)
        ctx.paint()
        text(ctx, credit, 18, H - 16, 12, SOFT, 0.85, "l", "semi", sp=0.6)
        if kick:
            kicker(ctx, kick, W / 2, H - 46, t, t0 + 0.4, None, 16, WHITE)
        if name:
            name_tag(ctx, name, 40, 60, t, t0 + 0.6, None, 30)
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(a)
        ctx.restore()
