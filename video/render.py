"""Renderiza o vídeo.

Uso:
  python3 render.py preview 10 45 120 ...   -> PNGs em out/preview/
  python3 render.py sheet                   -> folha de contato a cada 15 s
  python3 render.py full                    -> out/agua_viva_caixa.mp4 (4 processos em paralelo)
"""
import os
import subprocess
import sys
from multiprocessing import Process

import cairo

from gfx import W, H, FPS
import math
from gfx import ease, clamp
from scenes2 import SCENES, CUTS
from overlays import draw_inserts

OW, OH = 1920, 1080
SC = OW / W
XF = 0.35  # meia-duração da transição


def scene_draw(ctx, t):
    for s, e, fn in SCENES:
        if s <= t < e:
            p = (t - s) / max(1.0, min(e, 935) - s)
            z = 1.0 + 0.04 * ease(p)
            dx = math.sin(t * 0.07 + s) * 6
            dy = math.cos(t * 0.05 + s) * 4
            ctx.save()
            ctx.translate(W / 2 + dx, H / 2 + dy)
            ctx.scale(z, z)
            ctx.translate(-W / 2, -H / 2)
            fn(ctx, t)
            ctx.restore()
            break
    draw_inserts(ctx, t)


def draw_frame(ctx, t):
    cut = next((c for c in CUTS if c > 0 and abs(t - c) < XF), None)
    if cut is None:
        scene_draw(ctx, t)
    else:
        k = ease((t - (cut - XF)) / (2 * XF))
        ctx.push_group()
        scene_draw(ctx, min(t, cut - 0.02))
        ctx.pop_group_to_source()
        ctx.paint()
        ctx.push_group()
        scene_draw(ctx, max(t, cut + 0.02))
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(k)
    if t < 0.8:
        ctx.set_source_rgba(0, 0, 0, 1 - t / 0.8)
        ctx.paint()

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
AUDIO = os.path.join(HERE, "narracao.wav")
MIX = os.path.join(HERE, "out", "mix.wav")


def duration():
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", AUDIO],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def render_png(t, path):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, OW, OH)
    ctx = cairo.Context(surf)
    ctx.scale(SC, SC)
    draw_frame(ctx, t)
    surf.write_to_png(path)


def render_part(i, f0, f1):
    path = os.path.join(OUT, f"part{i}.mp4")
    ff = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgra", "-s", f"{OW}x{OH}", "-r", str(FPS),
         "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", path],
        stdin=subprocess.PIPE)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, OW, OH)
    ctx = cairo.Context(surf)
    ctx.scale(SC, SC)
    for f in range(f0, f1):
        ctx.save()
        ctx.set_operator(cairo.OPERATOR_SOURCE)
        ctx.set_source_rgb(0, 0, 0)
        ctx.paint()
        ctx.restore()
        draw_frame(ctx, f / FPS)
        surf.flush()
        ff.stdin.write(bytes(surf.get_data()))
        if (f - f0) % (FPS * 30) == 0:
            print(f"parte {i}: {(f - f0) / (f1 - f0) * 100:.0f}%", flush=True)
    ff.stdin.close()
    ff.wait()


def full(nproc=4):
    os.makedirs(OUT, exist_ok=True)
    total = int(duration() * FPS) + 1
    step = total // nproc + 1
    procs = []
    for i in range(nproc):
        p = Process(target=render_part, args=(i, i * step, min(total, (i + 1) * step)))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
    lst = os.path.join(OUT, "parts.txt")
    with open(lst, "w") as f:
        for i in range(nproc):
            f.write(f"file 'part{i}.mp4'\n")
    final = os.path.join(OUT, "agua_viva_caixa_v2.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-i", MIX if os.path.exists(MIX) else AUDIO,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest",
                    "-movflags", "+faststart", final], check=True)
    print("pronto:", final)


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "preview":
        d = os.path.join(OUT, "preview")
        os.makedirs(d, exist_ok=True)
        for s in sys.argv[2:]:
            render_png(float(s), os.path.join(d, f"t{float(s):07.1f}.png"))
    elif mode == "sheet":
        d = os.path.join(OUT, "sheet")
        os.makedirs(d, exist_ok=True)
        times = [float(x) for x in sys.argv[2:]] or [x * 15.0 + 8 for x in range(62)]
        for k, t in enumerate(times):
            render_png(t, os.path.join(d, f"{k:03d}.png"))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(d, "%03d.png"), "-vf",
                        "scale=320:-1,tile=4x4", os.path.join(d, "sheet_%02d.jpg")], check=True)
    elif mode == "full":
        full()
