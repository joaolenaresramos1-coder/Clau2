import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cairo
from PIL import Image, ImageDraw
import render
from gfx import W, H
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "sheet")
times = [t * 2.0 + 1 for t in range(332)]
per = 48
for p in range(0, len(times), per):
    S = Image.new('RGB', (8 * 240, 6 * 135))
    for i, t in enumerate(times[p:p + per]):
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
        ctx = cairo.Context(surf)
        render.draw_frame(ctx, t)
        im = Image.frombuffer('RGBA', (W, H), bytes(surf.get_data()), 'raw', 'BGRA', 0, 1).convert('RGB').resize((240, 135))
        d = ImageDraw.Draw(im); d.rectangle((0, 0, 46, 12), fill=(0, 0, 0)); d.text((2, 0), f'{int(t)//60}:{int(t)%60:02d}', fill=(255, 255, 0))
        S.paste(im, ((i % 8) * 240, (i // 8) * 135))
    S.save(os.path.join(out, f'r{p // per:02d}.jpg'), quality=88)
