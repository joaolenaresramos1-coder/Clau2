"""Cenas do vídeo. Todos os tempos são globais (segundos da narração)."""
import math
import cairo
from gfx import *  # noqa: F401,F403
from mapdata import *  # noqa: F401,F403


# 00:00 – 00:37  Praia vazia e poste
def sc_beach_open(ctx, t):
    cam = min(t, 27) * 3
    zoom = 1 + 0.6 * ease((t - 27) / 6)
    ctx.save()
    px, py = W * 0.30, H * 0.80
    ctx.translate(px, py)
    ctx.scale(zoom, zoom)
    ctx.translate(-px, -py)
    sky_beach(ctx, t, cam=cam)
    post_bottle(ctx, W * 0.30 - cam * 0.5 + 81 * 0.5, H * 0.86, 1.0, glow=appear(t, 29, 1.5))
    ctx.restore()
    if t > 13:
        k = window(t, 13, 22)
        # pés na água
        for side in (-1, 1):
            ctx.save()
            ctx.translate(W * 0.55 + side * 22, H * 0.64)
            rgba(ctx, SKIN, 0.9 * k)
            ctx.rectangle(-9, -60, 18, 60)
            ctx.fill()
            ctx.restore()
    vignette(ctx, 0.35)


# 00:37 – 01:02  A queimadura
def sc_sting(ctx, t):
    ocean(ctx, t, top=(0.15, 0.48, 0.55), bot=(0.04, 0.18, 0.24))
    # superfície
    surface_line(ctx, t, 60)
    swim = math.sin(t * 4)
    # nadador visto de baixo
    person(ctx, W * 0.30 + 40, 80, 0.9, rot=-math.pi / 2 - 0.1, legs_skin=True, outfit="swim",
           arm=60 + swim * 30)
    box_jelly(ctx, W * 0.36 + (t - 37) * 6, H * 0.30, 1.1, t, a=0.8)
    # marcas vermelhas
    k = appear(t, 47, 2.0)
    if k > 0:
        for i in range(4):
            ctx.move_to(W * 0.10, 66 + i * 6)
            ctx.curve_to(W * 0.13, 52 + i * 8, W * 0.17, 80, W * 0.10 + 140 * k, 70 + i * 7)
            rgba(ctx, RED, 0.9 * k)
            ctx.set_line_width(3)
            ctx.stroke()
        rgba(ctx, RED, 0.15 * k * (0.6 + 0.4 * math.sin(t * 6)))
        ctx.paint()
    # distância até a areia
    k2 = appear(t, 52.5)
    if k2 > 0:
        d = 10 if t < 57 else max(5, 10 - (t - 57) * 2)
        card(ctx, W * 0.62, H * 0.70, 420, 120, k2)
        line(ctx, W * 0.62 + 30, H * 0.70 + 85, W * 0.62 + 390, H * 0.70 + 85, (0.4, 0.6, 0.65), k2, 4)
        xx = W * 0.62 + 30 + (10 - d) / 10 * 360
        circle(ctx, xx, H * 0.70 + 85, 10, ORANGE, k2)
        text(ctx, "AREIA", W * 0.62 + 390, H * 0.70 + 60, 18, SAND, k2, "r")
        text(ctx, f"{d:.0f} M", W * 0.62 + 30, H * 0.70 + 55, 44, WHITE, k2, "l")
    if t > 58:
        rgba(ctx, (0, 0, 0), 0.5 * appear(t, 58, 4))
        ctx.paint()
    vignette(ctx, 0.6)


# 01:02 – 01:40  O animal sem cérebro + a pequena
def sc_nobrain(ctx, t):
    ocean(ctx, t)
    if t < 81:
        box_jelly(ctx, W / 2, H * 0.30, 1.4, t, glow=1)
        kinds = ["brain", "bone", "heart", "drop"]
        names = ["CÉREBRO", "OSSOS", "CORAÇÃO", "SANGUE"]
        cues = [65.0, 66.5, 67.8, 69.0]
        for i, (kd, nm, c0) in enumerate(zip(kinds, names, cues)):
            a = window(t, c0, 76)
            x = W / 2 + (i - 1.5) * 190
            card(ctx, x - 75, H * 0.62, 150, 140, a)
            icon(ctx, kd, x, H * 0.62 + 58, 0.9, a)
            text(ctx, nm, x, H * 0.62 + 122, 18, WHITE, a)
            xmark(ctx, x, H * 0.62 + 58, 40, appear(t, c0 + 0.5, 0.6) * a)
        big_title(ctx, [("95% ", ORANGE), ("ÁGUA", WHITE)], W / 2, H * 0.62 + 70, t, 71.2, 81, 64)
        big_title(ctx, [("~70 ", ORANGE), ("MORTES NA AUSTRÁLIA", WHITE)], W / 2, H * 0.62 + 140, t, 73.5, 81, 40)
    else:
        sh = ease((t - 89) / 2)
        box_jelly(ctx, W / 2 - sh * 250, H * 0.33, 1.4 - sh * 0.3, t, glow=1)
        name_tag(ctx, "Chironex fleckeri", 40, 60, t, 81.5, None, 30)
        kicker(ctx, "ÁGUA-VIVA-CAIXA AUSTRALIANA", 40, 100, t, 84, align="l")
        k = appear(t, 91)
        if k > 0:
            x, y = W * 0.75, H * 0.40
            # dedo
            rrect(ctx, x - 25, y + 30, 50, 200, 24)
            rgba(ctx, SKIN, k)
            ctx.fill()
            rrect(ctx, x - 17, y + 36, 34, 40, 12)
            rgba(ctx, (0.97, 0.85, 0.8), k)
            ctx.fill()
            iruk(ctx, x, y - 20, 0.8, t, k)
            label(ctx, "DO TAMANHO DE UMA UNHA", x, H * 0.92, t, 93.5, None, 24, ORANGE)
    vignette(ctx)


# 01:40 – 02:02  Promessa
def sc_promise(ctx, t):
    ocean(ctx, t)
    items = [("bottle", "A GARRAFA", 100.5), ("stocking", "A MEIA-CALÇA", 105.0), ("eye", "24 OLHOS", 109.0),
             ("fallen", "O QUE FAZER", 112.0)]
    for i, (kd, nm, c0) in enumerate(items):
        a = window(t, c0, 116.5)
        x = W / 2 + (i - 1.5) * 260
        card(ctx, x - 110, H * 0.30, 220, 220, a)
        icon(ctx, kd, x, H * 0.30 + 95, 1.2, a)
        text(ctx, nm, x, H * 0.30 + 190, 22, ORANGE, a)
    kicker(ctx, "POR QUE VOCÊ NUNCA IA QUERER ENCONTRAR UMA", W / 2, H * 0.40, t, 117, size=20)
    big_title(ctx, [("ÁGUA-VIVA-", WHITE, "black"), ("CAIXA", ORANGE, "light")], W / 2, H * 0.40 + 75, t, 117.4, None, 72)
    if t > 117:
        box_jelly(ctx, W / 2, H * 0.68, 0.7, t, a=appear(t, 117.5))
    vignette(ctx)


# 02:02 – 02:43  Anatomia
def sc_anatomy(ctx, t):
    ocean(ctx, t)
    label(ctx, "O QUE ELA É?", W / 2, 70, t, 122.3, 125, 40)
    cube = appear(t, 129.5, 1.5)
    inv = 1 - 0.75 * appear(t, 152.5, 2)
    jx = W * 0.38 if t > 133.5 else W / 2
    jx = lerp(W / 2, W * 0.38, appear(t, 133.5, 1))
    box_jelly(ctx, jx, H * 0.25, 1.3, t, a=inv, cube=cube, tent=1.0, glow=0.5 * inv)
    label(ctx, "COMUM: REDONDA" if cube < 0.5 else "ESTA: UM CUBO", jx, H * 0.08 + 10, t, 125.2, 134, 26,
          ORANGE)
    # bola de basquete
    k = window(t, 134.5, 143)
    if k > 0:
        bx, by = W * 0.72, H * 0.27
        circle(ctx, bx, by, 62, (0.88, 0.5, 0.2), k)
        for ang in (0, math.pi / 2):
            line(ctx, bx + math.cos(ang) * 62, by + math.sin(ang) * 62, bx - math.cos(ang) * 62,
                 by - math.sin(ang) * 62, (0.2, 0.1, 0.05), k, 3)
        text(ctx, "~30 CM", bx, by + 120, 48, ORANGE, k)
        text(ctx, "UM POUCO MAIOR QUE UMA BOLA DE BASQUETE", bx, by + 152, 16, WHITE, k)
    k = window(t, 139, 152)
    if k > 0:
        text(ctx, "ATÉ 15", W * 0.72, H * 0.30, 64, ORANGE, k)
        text(ctx, "TENTÁCULOS POR CANTO", W * 0.72, H * 0.30 + 40, 22, WHITE, k)
        text(ctx, "ATÉ 60", W * 0.72, H * 0.52, 64, ORANGE, appear(t, 144) * k)
        text(ctx, "NO TOTAL", W * 0.72, H * 0.52 + 40, 22, WHITE, appear(t, 144) * k)
        callout(ctx, jx - 72, H * 0.32, 24, jx - 210, H * 0.18, "CANTO", appear(t, 140) * k)
        callout(ctx, jx + 72, H * 0.32, 24, jx + 160, H * 0.12, "CANTO", appear(t, 140.5) * k)
    k = window(t, 147.5, 153)
    if k > 0:
        x = W * 0.70
        line(ctx, x, H * 0.18, x, H * 0.80, ORANGE, k, 4)
        line(ctx, x - 12, H * 0.18, x + 12, H * 0.18, ORANGE, k, 4)
        line(ctx, x - 12, H * 0.80, x + 12, H * 0.80, ORANGE, k, 4)
        text(ctx, "~3 M", x + 30, H * 0.50, 56, ORANGE, k, "l")
        text(ctx, "MAIS QUE UM CARRO", x + 30, H * 0.50 + 34, 18, WHITE, k, "l")
    label(ctx, "QUASE INVISÍVEL", W * 0.70, H * 0.50, t, 153.5, None, 46, WHITE)
    vignette(ctx)


# 02:43 – 03:11  Células urticantes
def sc_cnido(ctx, t):
    ocean(ctx, t, top=(0.06, 0.15, 0.2))
    label(ctx, "CÉLULAS URTICANTES", W / 2, 70, t, 163.3, None, 36, ORANGE)
    label(ctx, "MILHÕES DELAS", W / 2, 105, t, 166.0, None, 22)
    cx, cy = W * 0.40, H * 0.55
    fire = appear(t, 174, 0.15)
    # pele
    k_skin = appear(t, 187.5)
    if k_skin > 0:
        ctx.rectangle(W * 0.68, 0, W * 0.32, H)
        rgba(ctx, SKIN, k_skin)
        ctx.fill()
        text(ctx, "PELE", W * 0.84, H * 0.15, 26, (0.4, 0.2, 0.1), k_skin)
    # cápsula
    ctx.save()
    ctx.translate(cx, cy)
    ctx.scale(1.0, 0.62)
    ctx.arc(0, 0, 150, 0, 2 * math.pi)
    ctx.restore()
    rgba(ctx, JELLY, 0.25)
    ctx.fill_preserve()
    rgba(ctx, JELLY, 0.9)
    ctx.set_line_width(3)
    ctx.stroke()
    if fire < 1:
        ctx.move_to(cx + 120, cy)
        for i in range(200):
            ang = i * 0.25
            r = 90 - i * 0.42
            ctx.line_to(cx + math.cos(ang) * r, cy + math.sin(ang) * r * 0.55)
        rgba(ctx, ORANGE, 0.9 * (1 - fire))
        ctx.set_line_width(2.5)
        ctx.stroke()
    if fire > 0:
        ex = cx + 150 + fire * (W * 0.40 + 20 * appear(t, 188))
        line(ctx, cx + 150, cy, ex, cy, ORANGE, 1, 4)
        for sy in (-1, 1):
            line(ctx, ex, cy, ex - 18, cy + sy * 12, ORANGE, 1, 3)
        if t < 175:
            rgba(ctx, WHITE, 0.4 * (1 - appear(t, 174.1, 0.6)))
            ctx.paint()
    # gatilho
    callout(ctx, cx + 148, cy - 8, 16, cx + 230, cy - 90, "GATILHO", window(t, 171.5, 177))
    callout(ctx, cx, cy, 60, cx - 170, cy - 140, "ARPÃO ENROLADO", window(t, 165.5, 173.5))
    big_title(ctx, [("< 1 MILIONÉSIMO ", ORANGE), ("DE SEGUNDO", WHITE)], W / 2, H * 0.90, t, 177.5, 187.5, 40)
    vignette(ctx)


# 03:11 – 03:31  Por que tão forte
def sc_why(ctx, t):
    ocean(ctx, t)
    seabed(ctx, t)
    label(ctx, "POR QUE TÃO FORTE?", W / 2, 70, t, 191.3, 196, 36, ORANGE)
    box_jelly(ctx, W * 0.30, H * 0.20, 1.1, t)
    shrimp(ctx, W * 0.24, H * 0.55, 1.2, appear(t, 195))
    struggle = appear(t, 199.5)
    fish(ctx, W * 0.38, H * 0.60, 1.4, t, wiggle=0.4 * struggle * (1 - appear(t, 204, 0.4)), a=appear(t, 196))
    label(ctx, "PARAR A PRESA NA HORA", W * 0.33, H * 0.86, t, 204, None, 28, ORANGE)
    k = appear(t, 207, 1.2)
    if k > 0:
        person(ctx, W * 0.78, H * 0.95, 1.7, a=k, outfit="swim", t=t)
        text(ctx, "NÓS: SÓ UM BICHO GRANDE", W * 0.78, H * 0.18, 22, WHITE, k)
    vignette(ctx)


# 03:31 – 04:09  O veneno
def sc_venom(ctx, t):
    studio(ctx, t, H * 0.92)
    label(ctx, "O QUE O VENENO FAZ", W / 2, 70, t, 211.3, None, 34, ORANGE)
    # células
    k = window(t, 214, 224)
    for i in range(12):
        x = W * 0.18 + (i % 6) * 80
        y = H * 0.38 + (i // 6) * 90
        hole = appear(t, 214.5 + i * 0.25, 0.4)
        circle(ctx, x, y, 34, (0.9, 0.55, 0.55), k * (1 - 0.5 * hole))
        circle(ctx, x + 5, y - 4, 10 * hole, (0.08, 0.12, 0.16), k)
    label(ctx, "ABRE BURACOS NAS CÉLULAS", W * 0.40, H * 0.75, t, 215, 224, 26)
    # cicatriz
    k = window(t, 218.5, 224)
    if k > 0:
        rrect(ctx, W * 0.66, H * 0.30, 300, 280, 20)
        rgba(ctx, SKIN, k)
        ctx.fill()
        for i in range(4):
            ctx.move_to(W * 0.66 + 20, H * 0.36 + i * 55)
            ctx.curve_to(W * 0.66 + 100, H * 0.36 + i * 55 - 25, W * 0.66 + 200, H * 0.36 + i * 55 + 25,
                         W * 0.66 + 280, H * 0.36 + i * 55)
            rgba(ctx, (0.7, 0.3, 0.3), k)
            ctx.set_line_width(7)
            ctx.stroke()
        text(ctx, "MARCAS DE CHICOTE", W * 0.66 + 150, H * 0.30 + 320, 22, WHITE, k)
    # coração
    k = window(t, 224, 235)
    if k > 0:
        stop = appear(t, 228.5, 1.5)
        beat = 1 + 0.12 * abs(math.sin(t * 4)) * (1 - stop)
        icon(ctx, "heart", W / 2, H * 0.48, 2.6 * beat, k, lerp(1, 0.45, stop) and (RED if stop < 0.5 else (0.45, 0.3, 0.3)))
        # linha de ECG
        ctx.move_to(W * 0.15, H * 0.80)
        for x in range(int(W * 0.15), int(W * 0.85), 4):
            ph = (x * 0.02 - t * 6) % 12
            amp = (40 if ph < 1 else 0) * (1 - stop)
            ctx.line_to(x, H * 0.80 - amp * math.sin(ph * math.pi))
        rgba(ctx, GREEN if stop < 0.5 else RED, k)
        ctx.set_line_width(3)
        ctx.stroke()
        label(ctx, "PODE PARAR O CORAÇÃO EM MINUTOS", W / 2, H * 0.25, t, 226, 235, 28)
    # quanto basta
    k = appear(t, 235.5)
    if k > 0:
        big_title(ctx, [("ALGUNS METROS ", ORANGE), ("DE TENTÁCULO", WHITE)], W / 2, H * 0.30, t, 235.5, None, 40)
        label(ctx, "PODEM BASTAR PARA MATAR UM ADULTO", W / 2, H * 0.30 + 40, t, 236.5, None, 22)
        person(ctx, W * 0.42, H * 0.92, 1.6, a=appear(t, 237), outfit="swim")
        person(ctx, W * 0.58, H * 0.92, 1.0, a=appear(t, 243), outfit="kid")
        label(ctx, "CRIANÇA: BEM MENOS", W * 0.58, H * 0.55, t, 243.5, None, 20, ORANGE)
    vignette(ctx)


# 04:09 – 04:51  Os olhos
def sc_eyes(ctx, t):
    ocean(ctx, t)
    big_title(ctx, [("ELA ", WHITE, "black"), ("ENXERGA", ORANGE, "light")], W / 2, H / 2, t, 252.0, 255.5, 80)
    if t < 255:
        box_jelly(ctx, W / 2, H * 0.22, 0.9, t, a=0.5)
        vignette(ctx)
        return
    if t < 278:
        k = appear(t, 255.2)
        # ropálio ampliado
        cx, cy = W * 0.40, H * 0.50
        line(ctx, cx, cy - 230, cx, cy - 120, JELLY, k, 10)
        ctx.save()
        ctx.translate(cx, cy)
        ctx.scale(1, 1.25)
        ctx.arc(0, 0, 120, 0, 2 * math.pi)
        ctx.restore()
        rgba(ctx, JELLY, 0.2 * k)
        ctx.fill_preserve()
        rgba(ctx, JELLY, 0.8 * k)
        ctx.set_line_width(3)
        ctx.stroke()
        simple = [(-55, -90), (55, -90), (-60, 95), (60, 95)]
        lens = [(0, -30), (0, 50)]
        hs = window(t, 264, 266.5)
        hl = appear(t, 266.5)
        for x, y in simple:
            circle(ctx, cx + x, cy + y, 13, (0.25, 0.15, 0.1), k)
            circle(ctx, cx + x, cy + y, 22, ORANGE, 0.5 * hs)
        for i, (x, y) in enumerate(lens):
            r = 38 if i == 0 else 26
            circle(ctx, cx + x, cy + y, r, (0.15, 0.1, 0.08), k)
            circle(ctx, cx + x, cy + y, r * 0.55, (0.6, 0.8, 0.9), 0.8 * k)
            circle(ctx, cx + x - r * 0.2, cy + y - r * 0.2, r * 0.15, WHITE, k)
            circle(ctx, cx + x, cy + y, r + 10, ORANGE, 0.45 * hl)
        name_tag(ctx, "Ropálio", 40, 60, t, 257, None, 30)
        callout(ctx, cx, cy - 30, 50, cx - 230, cy - 160, "OLHO COM LENTE", appear(t, 267))
        label(ctx, "6 OLHOS EM CADA", W * 0.72, H * 0.30, t, 261.3, None, 34)
        label(ctx, "4 SENSORES DE LUZ", W * 0.72, H * 0.42, t, 264, None, 24, (0.8, 0.9, 0.9))
        label(ctx, "2 COM LENTE, RETINA E CÓRNEA", W * 0.72, H * 0.50, t, 266.5, None, 22, ORANGE)
        big_title(ctx, [("24 ", ORANGE), ("OLHOS", WHITE)], W * 0.72, H * 0.68, t, 269.5, None, 60)
        big_title(ctx, [("0 ", RED), ("CÉREBROS", WHITE)], W * 0.72, H * 0.80, t, 273.0, None, 46)
    else:
        # nadando entre pilares
        for i in range(4):
            x = W * (0.15 + i * 0.25)
            ctx.rectangle(x - 18, 0, 36, H)
            rgba(ctx, (0.08, 0.14, 0.16), 0.9)
            ctx.fill()
        p = (t - 278) / 13
        jx = W * 0.05 + p * W * 0.9
        jy = H * 0.45 + math.sin(p * math.pi * 3) * 60
        box_jelly(ctx, jx, jy - 60, 0.7, t, glow=0.6)
        label(ctx, "ELA NADA DE PROPÓSITO", W / 2, H * 0.90, t, 282.5, None, 30, ORANGE)
    vignette(ctx)


# 04:51 – 05:09  Experimento 2023
def sc_learn(ctx, t):
    ocean(ctx, t, rays=False)
    chapter(ctx, "UMA ÁGUA-VIVA-CAIXA DO CARIBE", "2023", "ELA APRENDE", W / 2, 80, t, 291.5, None, 40)
    
    tx, ty, tw, th = W * 0.25, H * 0.22, W * 0.5, H * 0.60
    card(ctx, tx, ty, tw, th, 1, fill=(0.1, 0.22, 0.26))
    for i in range(14):
        rgba(ctx, (0.55, 0.6, 0.6), 0.35)
        ctx.rectangle(tx + i * tw / 14, ty, tw / 28, 18)
        ctx.rectangle(tx + i * tw / 14, ty + th - 18, tw / 28, 18)
        ctx.fill()
    learned = appear(t, 301, 2)
    period = 2.6
    ph = ((t - 291) % period) / period
    amp = lerp(1.0, 0.55, learned)
    yy = ty + th / 2 + math.sin(ph * 2 * math.pi) * (th / 2 - 60) * amp
    bump = abs(math.sin(ph * 2 * math.pi)) > 0.97 and learned < 0.5
    box_jelly(ctx, tx + tw / 2, yy - 20, 0.35, t, glow=0.4, tents_per=2)
    if bump:
        circle(ctx, tx + tw / 2, yy + (40 if math.sin(ph * 2 * math.pi) > 0 else -60), 30, RED, 0.5)
    label(ctx, "SEM CÉREBRO", W / 2, H * 0.91, t, 304, None, 30, ORANGE)
    label(ctx, "~1.000 NEURÔNIOS EM CADA ROPÁLIO", W / 2, H * 0.97, t, 305.5, None, 20)
    vignette(ctx)


# 05:09 – 05:50  Ciclo de vida e temporada
def sc_cycle(ctx, t):
    ocean(ctx, t)
    if t < 339:
        cx, cy, r = W / 2, H * 0.52, 200
        ctx.arc(cx, cy, r, 0, 2 * math.pi)
        rgba(ctx, (0.5, 0.7, 0.72), 0.35)
        ctx.set_line_width(3)
        ctx.stroke()
        k = appear(t, 317.5, 20)
        ctx.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * k)
        rgba(ctx, ORANGE, 0.9)
        ctx.set_line_width(5)
        ctx.stroke()
        nodes = [("PÓLIPO NO MANGUE", -math.pi / 2, 317.0), ("ÁGUA-VIVA JOVEM", 0, 326.0),
                 ("ADULTA", math.pi / 2, 332.0), ("MORRE NO INVERNO", math.pi, 336.0)]
        for i, (nm, ang, c0) in enumerate(nodes):
            a = appear(t, c0)
            x, y = cx + math.cos(ang) * r, cy + math.sin(ang) * r
            circle(ctx, x, y, 46, (0.06, 0.16, 0.2), a)
            ctx.arc(x, y, 46, 0, 2 * math.pi)
            rgba(ctx, (0.5, 0.7, 0.72), a)
            ctx.set_line_width(2)
            ctx.stroke()
            if i == 0:
                for j in range(3):
                    line(ctx, x - 15 + j * 15, y + 25, x - 15 + j * 15, y - 10, (0.85, 0.7, 0.6), a, 5)
                    circle(ctx, x - 15 + j * 15, y - 14, 7, (0.85, 0.7, 0.6), a)
            elif i == 3:
                box_jelly(ctx, x, y - 10, 0.25, t, a=a * 0.35, tents_per=2)
            else:
                box_jelly(ctx, x, y - 12, 0.18 if i == 1 else 0.3, t, a=a, tents_per=2)
            off = 75
            tx = x + (off if i == 1 else -off if i == 3 else 0)
            ty = y + (75 if i == 2 else -62 if i == 0 else 8)
            text(ctx, nm, tx, ty, 20, WHITE, a, "l" if i == 1 else "r" if i == 3 else "c")
        big_title(ctx, [("ALGUNS MM ", WHITE), ("→ BOLA DE BASQUETE", ORANGE)], cx, cy + 10, t, 330, None, 22)
        label(ctx, "EM POUCOS MESES", cx, cy + 40, t, 331, None, 18)
    else:
        months = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
        season = {0, 1, 2, 3, 4, 10, 11}
        bw = 86
        x0 = W / 2 - 6 * bw - 5.5 * 6
        for i, m in enumerate(months):
            a = appear(t, 339.3 + i * 0.12)
            on = i in season and appear(t, 341.5 + (i if i > 5 else i + 12) * 0.08) > 0.5
            x = x0 + i * (bw + 6)
            rrect(ctx, x, H * 0.40, bw, 90, 8)
            rgba(ctx, ORANGE if on else (0.12, 0.25, 0.3), a)
            ctx.fill()
            text(ctx, m, x + bw / 2, H * 0.40 + 55, 24, (0.1, 0.1, 0.1) if on else WHITE, a)
        label(ctx, "TEMPORADA DE ÁGUAS-VIVAS NO NORTE DA AUSTRÁLIA", W / 2, H * 0.30, t, 339.5, None, 26)
        label(ctx, "MAIS OU MENOS DE OUTUBRO/NOVEMBRO A MAIO", W / 2, H * 0.62, t, 342.5, None, 22, ORANGE)
        label(ctx, "POR ISSO A PRAIA ESTAVA VAZIA", W / 2, H * 0.80, t, 346, None, 30)
    vignette(ctx)


# 05:50 – 06:41  História 1955
def sc_history(ctx, t):
    ocean(ctx, t, top=(0.06, 0.13, 0.17))
    if t < 358:
        chapter(ctx, "AUSTRÁLIA TROPICAL", "INÍCIO DO", "SÉCULO 20", W / 2, H * 0.25, t, 354, None, 52)
        for i in range(3):
            fall = appear(t, 356 + i * 0.4, 0.8)
            person(ctx, W * (0.35 + i * 0.15), H * 0.85, 1.1, rot=-fall * math.pi / 2 * 0.95,
                   outfit="swim", a=appear(t, 354.3))
        vignette(ctx)
        return
    pr = draw_aus(ctx, W * 0.08, H * 0.10, W * 0.50, H * 0.80, appear(t, 358))
    pin(ctx, *pr(146.0, -18.3), appear(t, 374.5), "CARDWELL")
    pin(ctx, *pr(145.8, -16.9), appear(t, 377), "CAIRNS", c=WHITE)
    chapter(ctx, "CARDWELL · QUEENSLAND", "JANEIRO", "1955", W * 0.80, H * 0.22, t, 368.5, None, 36)
    label(ctx, "MENINO DE 5 ANOS", W * 0.80, H * 0.29, t, 370.5, None, 22)
    label(ctx, "DR. HUGO FLECKER", W * 0.80, H * 0.40, t, 377.5, None, 28)
    if t > 382:
        k = appear(t, 382)
        x0, y0 = W * 0.66, H * 0.48
        for i in range(10):
            line(ctx, x0 + i * 30, y0, x0 + i * 30, y0 + 150, WHITE, 0.3 * k, 1.5)
        for j in range(6):
            line(ctx, x0, y0 + j * 30, x0 + 270, y0 + j * 30, WHITE, 0.3 * k, 1.5)
        box_jelly(ctx, x0 + 135, y0 + 60, 0.5, t, a=appear(t, 387), tents_per=3)
    name_tag(ctx, "Chironex fleckeri", W * 0.66, H * 0.86, t, 394.5, None, 30)
    label(ctx, "“MÃO DA MORTE”", W * 0.80, H * 0.93, t, 398, None, 24, RED)
    vignette(ctx)


# 06:41 – 07:15  Síndrome de Irukandji
def sc_syndrome(ctx, t):
    studio(ctx, t, H * 0.90)
    bp = body_pts(W * 0.33, H * 0.90, 1.8)
    chapter(ctx, "CAIRNS · QUEENSLAND", "1952", "UMA DOENÇA ESTRANHA", W / 2, 95, t, 403.5, None, 44)
    person(ctx, W * 0.33, H * 0.90, 1.8, outfit="swim", a=appear(t, 405))
    circle(ctx, *bp["shin"], 7, RED, appear(t, 410) * 0.9)
    label(ctx, "UMA QUEIMADURA PEQUENA", W * 0.33, H * 0.27, t, 410, 414, 22)
    k = appear(t, 414.5)
    if k > 0:
        timer(ctx, W * 0.70, H * 0.45, 130, clamp((t - 414.5) / 3.5), k, "30 MIN")
    pain = appear(t, 418.5)
    if pain > 0:
        for (key, c0) in (("back", 418.5), ("chest", 419.5), ("belly", 420)):
            pk = appear(t, c0) * (0.5 + 0.5 * math.sin(t * 6 + c0))
            circle(ctx, *bp[key], 26, RED, 0.45 * pk)
        for i, w in enumerate(["DOR NAS COSTAS", "CÃIBRAS", "VÔMITO", "SUOR", "SENSAÇÃO DE MORTE"]):
            label(ctx, w, W * 0.70, H * 0.80 + 0 * i, t, 418.5 + i * 1.2, 418.5 + (i + 1) * 1.2, 30,
                  RED if i == 4 else WHITE)
    big_title(ctx, [("SÍNDROME DE ", WHITE), ("IRUKANDJI", ORANGE)], W * 0.70, H * 0.85, t, 430.5, None, 34)
    vignette(ctx)


# 07:15 – 07:43  Jack Barnes
def sc_barnes(ctx, t):
    studio(ctx, t, H * 0.82)
    chapter(ctx, "1961", "JACK", "BARNES", W / 2, 95, t, 435.5, None, 44)
    if t < 447:
        iruk(ctx, W / 2, H * 0.35, 2.2, t, appear(t, 440))
        label(ctx, "DO TAMANHO DE UMA UNHA", W / 2, H * 0.92, t, 442.5, None, 24, ORANGE)
    else:
        names = [("ELE MESMO", 1.6, 448.0), ("FILHO, 9 ANOS", 1.05, 450.5), ("SALVA-VIDAS", 1.6, 452.5)]
        for i, (nm, s, c0) in enumerate(names):
            a = appear(t, c0)
            x = W * (0.28 + i * 0.22)
            person(ctx, x, H * 0.82, s, a=a, outfit=["swim", "kid", "lifeguard"][i])
            text(ctx, nm, x, H * 0.90, 22, WHITE, a)
            hk = appear(t, 455.5 + i * 0.2)
            icon(ctx, "cross", x + 55, H * 0.32, 0.6, hk, RED)
            check(ctx, x - 55, H * 0.32, 18, appear(t, 457.5 + i * 0.2))
        label(ctx, "HOSPITAL", W * 0.03, H * 0.33, t, 455.5, None, 18, RED, "l")
        label(ctx, "SOBREVIVERAM", W * 0.03, H * 0.38, t, 457.5, None, 18, GREEN, "l")
        name_tag(ctx, "Carukia barnesi", 40, 60, t, 460.5, None, 30)
    vignette(ctx)


# 07:43 – 08:15  Redes de proteção
def sc_nets(ctx, t):
    if t < 489:
        ocean(ctx, t, top=(0.15, 0.48, 0.55), bot=(0.04, 0.18, 0.24))
        label(ctx, "O PERIGO SE INVERTE", W / 2, 70, t, 463.5, 469, 36, ORANGE)
        k = appear(t, 476)
        nx = W * 0.55
        for j in range(16):
            line(ctx, nx - 6 * (j % 2), j * 45, nx + 6 * ((j + 1) % 2), j * 45 + 45, WHITE, 0.5 * k, 2)
        for j in range(0, 16):
            line(ctx, nx - 25, j * 45, nx + 25, j * 45 + 22, WHITE, 0.35 * k, 1.5)
        label(ctx, "REDE DE PROTEÇÃO", nx, H * 0.95, t, 476, None, 22)
        # grande bate na rede
        bx = W * 0.75 - 40 * abs(math.sin(t * 0.8)) * k
        box_jelly(ctx, bx, H * 0.28, 0.9, t, a=1 if t < 479 else 0.6)
        if t > 479:
            p = clamp((t - 480) / 8)
            iruk(ctx, W * 0.80 - p * W * 0.6, H * 0.45, 0.9, t, appear(t, 479.5))
            label(ctx, "~1 CM", W * 0.80 - p * W * 0.6, H * 0.40, t, 481, None, 28, ORANGE)
        text(ctx, "PRAIA", W * 0.20, H * 0.12, 22, SAND, appear(t, 476))
        text(ctx, "MAR", W * 0.85, H * 0.12, 22, (0.6, 0.85, 0.9), appear(t, 476))
    else:
        ocean(ctx, t, top=(0.15, 0.55, 0.6), bot=(0.05, 0.25, 0.3))
        for i in range(9):
            x = i * 160
            ctx.move_to(x, H)
            ctx.curve_to(x + 30, H * 0.7, x + 60, H * 0.75, x + 80, H * 0.6 + (i % 3) * 30)
            ctx.curve_to(x + 100, H * 0.8, x + 130, H * 0.8, x + 150, H)
            rgba(ctx, [(0.9, 0.5, 0.45), (0.95, 0.75, 0.4), (0.6, 0.5, 0.8)][i % 3], 0.85)
            ctx.fill()
        person(ctx, W * 0.40, 60, 0.7, rot=-math.pi / 2, legs_skin=True, outfit="red", arm=70)
        iruk(ctx, W * 0.65, H * 0.35, 0.8, t)
        label(ctx, "NO RECIFE E EM MAR ABERTO", W / 2, H * 0.55, t, 490, None, 34)
    vignette(ctx)


# 08:15 – 09:02  A pegadinha
def sc_trick(ctx, t):
    ocean(ctx, t, top=(0.07, 0.15, 0.2))
    if t < 506:
        rrect(ctx, W * 0.30, H * 0.20, 500, 360, 30)
        rgba(ctx, SKIN)
        ctx.fill()
        circle(ctx, W * 0.30 + 250, H * 0.20 + 180, 22, RED, 0.45 * appear(t, 497))
        label(ctx, "UMA MANCHINHA VERMELHA", W / 2, H * 0.90, t, 497, None, 30)
        label(ctx, "E A PESSOA SE SENTE ÓTIMA", W / 2, H * 0.96, t, 502, None, 20, GREEN)
    elif t < 534:
        studio(ctx, t, H * 0.92)
        timer(ctx, W * 0.25, H * 0.45, 140, clamp((t - 506.5) / 3), 1, "30 MIN")
        import rig
        hunch = appear(t, 510, 1.5)
        pz = rig.blend(rig.p_stand(t), rig.pose(lean=30, thighF=20, kneeF=25, thighB=10, kneeB=20, armF=40,
                                                 elbowF=90, armB=30, elbowB=80, neck=15), hunch)
        rig.figure(ctx, W * 0.62, H * 0.92, 2.28, pz, outfit="red".replace("red", "friend"), facing=-1, t=t)
        bp = body_pts(W * 0.62, H * 0.92, 1.9)
        for (key, c0) in (("back", 510), ("chest", 511), ("belly", 512)):
            pk = appear(t, c0) * (0.5 + 0.5 * math.sin(t * 5 + c0))
            x0, y0 = bp[key]
            circle(ctx, x0 - 10, y0 + 25 * hunch, 30, RED, 0.45 * pk)
        label(ctx, "COSTAS · PEITO · BARRIGA", W * 0.62, H * 0.12, t, 510, None, 26, RED)
        label(ctx, "VEM EM ONDAS", W * 0.62, H * 0.18, t, 512.5, None, 20)
        label(ctx, "INTERNADOS POR DIAS", W * 0.25, H * 0.82, t, 514.5, 518.5, 24)
        label(ctx, "SANGRAMENTO NO CÉREBRO", W * 0.25, H * 0.82, t, 519, 523, 22, RED)
        label(ctx, "INSUFICIÊNCIA CARDÍACA", W * 0.25, H * 0.88, t, 523, 534, 22, RED)
        label(ctx, "“EU VOU MORRER?”", W * 0.25, H * 0.82, t, 529.5, 534, 30, ORANGE)
    else:
        chapter(ctx, "QUEENSLAND", "2002", "", W / 2, H * 0.42, t, 534.3, None, 80)
        label(ctx, "DOIS TURISTAS MORTOS EM QUEENSLAND", W / 2, H * 0.52, t, 535.5, None, 30)
        label(ctx, "A IRUKANDJI FOI APONTADA COMO CAUSA", W / 2, H * 0.60, t, 539, None, 22, (0.8, 0.9, 0.9))
    vignette(ctx)


# 09:02 – 09:35  Meia-calça, lycra, vinagre
def sc_protect(ctx, t):
    if t < 563:
        studio(ctx, t, H * 0.92)
        chapter(ctx, "QUEENSLAND", "ANOS", "80", W / 2, 90, t, 545.5, None, 46)
        person(ctx, W * 0.35, H * 0.92, 2.0, outfit="lifeguard", stockings=True,
               a=appear(t, 546))
        label(ctx, "SALVA-VIDAS DE MEIA-CALÇA", W * 0.35, H * 0.20, t, 547.5, None, 22)
        k = appear(t, 555.5)
        if k > 0:
            x0 = W * 0.62
            ctx.rectangle(x0, H * 0.55, 380, 160)
            rgba(ctx, SKIN, k)
            ctx.fill()
            line(ctx, x0, H * 0.53, x0 + 380, H * 0.53, (0.85, 0.65, 0.5), k, 10)
            for i in range(6):
                x = x0 + 30 + i * 60
                fire = clamp((t - 556 - i * 0.2) / 0.5)
                line(ctx, x, H * 0.30, x, H * 0.30 + fire * (H * 0.22), ORANGE, k, 3)
                if fire >= 1:
                    xmark(ctx, x, H * 0.48, 10, 1, RED, k)
            text(ctx, "O TECIDO BLOQUEIA", x0 + 190, H * 0.86, 24, WHITE, k)
    else:
        sky_beach(ctx, t, sunset=0.3)
        person(ctx, W * 0.30, H * 0.92, 1.6, outfit="lycra", a=appear(t, 563))
        label(ctx, "ROUPA DE LYCRA", W * 0.30, H * 0.36, t, 563.5, None, 24, WHITE)
        post_bottle(ctx, W * 0.65, H * 0.92, 1.3, a=appear(t, 568.5), glow=appear(t, 572.5))
        big_title(ctx, [("LEMBRE DESSA ", WHITE), ("GARRAFA", ORANGE)], W / 2, H * 0.15, t, 573, None, 44)
        vignette(ctx, 0.3)


# 09:35 – 10:37  Cenário interativo
def sc_scenario(ctx, t):
    if t < 622.5:
        sky_beach(ctx, t, sunset=0.2)
        label(ctx, "O QUE VOCÊ FARIA DE VERDADE?", W / 2, 70, t, 578, 584, 36, WHITE)
        label(ctx, "JANEIRO · PERTO DE CAIRNS", W / 2, 70, t, 581.5, 590, 30, ORANGE)
        # rede
        k = appear(t, 584.5)
        for i in range(12):
            line(ctx, W * 0.10 + i * 28, H * 0.56, W * 0.10 + i * 28, H * 0.68, WHITE, 0.6 * k, 2)
        line(ctx, W * 0.10, H * 0.56, W * 0.10 + 11 * 28, H * 0.56, ORANGE, k, 3)
        # amigo
        if t < 596:
            fx = W * 0.62
            person(ctx, fx, H * 0.68, 0.8, outfit="red", a=appear(t, 586))
        else:
            fall = appear(t, 596.5, 1.0)
            person(ctx, lerp(W * 0.62, W * 0.55, fall), lerp(H * 0.68, H * 0.86, fall), 0.9, rot=-fall * math.pi / 2,
                   outfit="red")
            if t > 600:
                for i in range(4):
                    line(ctx, W * 0.55 - 10, H * 0.86 - 12 - i * 3, W * 0.55 + 70, H * 0.86 - 8 - i * 4, JELLY,
                         0.9 * appear(t, 600), 2)
                    line(ctx, W * 0.55, H * 0.86 - 10 - i * 3, W * 0.55 + 65, H * 0.86 - 6 - i * 4, RED,
                         0.8 * appear(t, 603.5), 4)
        # você
        person(ctx, W * 0.35, H * 0.95, 1.0, outfit="swim", a=appear(t, 589))
        if 595 < t < 597:
            rgba(ctx, WHITE, 0.3 * (1 - appear(t, 595, 1)))
            ctx.paint()
            text(ctx, "!!!", W * 0.62, H * 0.40, 80, RED, 1)
        # objetos
        k = appear(t, 613)
        rrect(ctx, W * 0.16, H * 0.86, 110, 60, 8)
        rgba(ctx, (0.3, 0.6, 0.85), k)
        ctx.fill()
        text(ctx, "ISOPOR", W * 0.16 + 55, H * 0.84, 18, WHITE, k)
        post_bottle(ctx, W * 0.88, H * 0.82, 0.8, a=appear(t, 616), glow=appear(t, 616))
        text(ctx, "VINAGRE · 30 M", W * 0.88, H * 0.52, 18, ORANGE, appear(t, 616))
        icon(ctx, "phone", W * 0.42, H * 0.70, 0.8, appear(t, 619.5))
        text(ctx, "CELULAR", W * 0.42, H * 0.64, 18, WHITE, appear(t, 619.5))
        vignette(ctx, 0.3)
    else:
        ocean(ctx, t, rays=False)
        label(ctx, "PRIMEIRA DECISÃO", W / 2, 70, t, 622.5, None, 34, WHITE)
        opts = [("A", "ÁGUA DOCE E ESFREGAR", 623.5), ("B", "ARRANCAR COM AS MÃOS", 629.2),
                ("C", "CORRER ATRÁS DO VINAGRE", 631.3)]
        for i, (lt, nm, c0) in enumerate(opts):
            a = appear(t, c0)
            x = W / 2 + (i - 1) * 400
            card(ctx, x - 180, H * 0.22, 360, 300, a, fill=(0.1, 0.3, 0.35))
            if i == 0:
                rrect(ctx, x - 30, H * 0.30, 60, 120, 10)
                rgba(ctx, (0.5, 0.8, 0.95), a)
                ctx.fill()
                for j in range(5):
                    circle(ctx, x + 40 + j * 8, H * 0.46 + j * 14, 5, (0.5, 0.8, 0.95), a)
            elif i == 1:
                for s in (-1, 1):
                    rrect(ctx, x + s * 50 - 25, H * 0.32, 50, 90, 22)
                    rgba(ctx, SKIN, a)
                    ctx.fill()
                for j in range(4):
                    line(ctx, x - 70, H * 0.45 + j * 8, x + 70, H * 0.43 + j * 10, JELLY, a, 2)
            else:
                icon(ctx, "bottle", x, H * 0.40, 2.2, a)
            text(ctx, lt, x - 150, H * 0.22 + 270, 34, ORANGE, a, "l")
            text(ctx, nm, x - 110, H * 0.22 + 270, 19, WHITE, a, "l")
        k = appear(t, 634.2)
        if k > 0:
            text(ctx, "ESCOLHA UMA ANTES DE EU TE CONTAR", W / 2, H * 0.83, 30, ORANGE, k)
            rem = max(0, 637 - t)
            text(ctx, f"{math.ceil(rem)}" if rem > 0 else "", W / 2, H * 0.94, 44, WHITE, k)
        vignette(ctx)


# 10:37 – 11:54  Respostas e RCP
def sc_answers(ctx, t):
    ocean(ctx, t, rays=False)
    if t < 679:
        opts = [("A", "ÁGUA DOCE", 637.3), ("B", "ARRANCAR", 662.0), ("C", "VINAGRE", 672.5)]
        for i, (lt, nm, c0) in enumerate(opts):
            a = appear(t, 637)
            x = W / 2 + (i - 1) * 400
            focus = window(t, c0, c0 + (24.5 if i == 0 else 10.5 if i == 1 else 7))
            card(ctx, x - 160, H * 0.10, 320, 100, a, fill=(0.1, 0.3, 0.35) if focus < 0.5 else (0.15, 0.4, 0.45))
            text(ctx, lt + "  " + nm, x, H * 0.10 + 62, 30, ORANGE if focus > 0.5 else WHITE, a)
            if i == 0:
                xmark(ctx, x + 130, H * 0.10 + 50, 22, appear(t, 641.5))
            if i == 1:
                xmark(ctx, x + 130, H * 0.10 + 50, 22, appear(t, 667) * 0.6)
            if i == 2:
                check(ctx, x + 130, H * 0.10 + 50, 22, appear(t, 673))
        if t < 662:
            label(ctx, "A PIOR DA LISTA", W / 2, H * 0.36, t, 642, None, 40, RED)
            for i in range(8):
                x = W * 0.2 + i * 110
                fire = clamp((t - 645.5 - i * 0.3) / 0.4)
                circle(ctx, x, H * 0.62, 30, JELLY, 0.3)
                ctx.arc(x, H * 0.62, 30, 0, 2 * math.pi)
                rgba(ctx, JELLY, 0.9)
                ctx.set_line_width(2)
                ctx.stroke()
                if fire > 0:
                    line(ctx, x, H * 0.62 + 30, x, H * 0.62 + 30 + fire * 100, ORANGE, 1, 3)
            label(ctx, "MUITAS CÉLULAS DISPARAM", W / 2, H * 0.92, t, 648, 655, 26)
            label(ctx, "ESFREGAR FAZ O MESMO", W / 2, H * 0.92, t, 655, None, 26, ORANGE)
        elif t < 672:
            label(ctx, "PUXAR ANTES DE TRATAR", W / 2, H * 0.45, t, 664, None, 36)
            label(ctx, "MAIS CÉLULAS DISPARAM — NELE E EM VOCÊ", W / 2, H * 0.55, t, 666, None, 24, ORANGE)
        else:
            label(ctx, "ACERTOU", W / 2, H * 0.45, t, 673, None, 50, GREEN)
            label(ctx, "MAS NÃO É A PRIMEIRA COISA A FAZER", W / 2, H * 0.56, t, 674.5, None, 30, ORANGE)
    elif t < 714:
        steps = [("1", "GRITE POR AJUDA", 680.5), ("2", "ALGUÉM LIGA PARA A EMERGÊNCIA", 683.5),
                 ("3", "ALGUÉM BUSCA O VINAGRE", 686.5), ("4", "ELE ESTÁ RESPIRANDO?", 690.5)]
        for i, (n, s, c0) in enumerate(steps):
            a = appear(t, c0)
            y = H * 0.18 + i * 70
            circle(ctx, W * 0.08, y - 10, 22, ORANGE, a)
            text(ctx, n, W * 0.08, y, 24, (0.1, 0.1, 0.1), a)
            text(ctx, s, W * 0.12, y, 26, WHITE, a, "l")
        label(ctx, "NÃO ESTÁ.", W * 0.12, H * 0.18 + 4 * 70, t, 695.3, None, 30, RED, "l")
        k = appear(t, 696)
        if k > 0:
            press = (math.sin(t * 2 * math.pi * 1.8) + 1) / 2
            person(ctx, W * 0.62, H * 0.86, 1.0, rot=-math.pi / 2, outfit="red", a=k)
            ctx.save()
            ctx.translate(W * 0.76, H * 0.80 - press * 8)
            rrect(ctx, -26, -110, 52, 90, 16)
            rgba(ctx, (0.2, 0.45, 0.65), k)
            ctx.fill()
            circle(ctx, 0, -135, 21, SKIN, k)
            line(ctx, -10, -95, -50, -20 + press * 6, (0.2, 0.45, 0.65), k, 12)
            line(ctx, 10, -95, -45, -20 + press * 6, (0.2, 0.45, 0.65), k, 12)
            ctx.restore()
            big_title(ctx, [("RCP ", ORANGE), ("AGORA", WHITE)], W * 0.72, H * 0.38, t, 696.5, None, 54)
            label(ctx, "NÃO ESPERE O VINAGRE · NÃO ESPERE A AMBULÂNCIA", W * 0.72, H * 0.45, t, 699.5, None, 18)
            label(ctx, "MANTÉM O SANGUE CIRCULANDO", W * 0.72, H * 0.96, t, 705, None, 22, GREEN)
    else:
        pr = draw_aus(ctx, W * 0.06, H * 0.12, W * 0.48, H * 0.76, appear(t, 714))
        pin(ctx, *pr(151.3, -23.8), appear(t, 716), "GLADSTONE")
        chapter(ctx, "RIO CALLIOPE · GLADSTONE", "2010", "", W * 0.78, H * 0.27, t, 714.5, None, 56)
        label(ctx, "RACHAEL, 10 ANOS", W * 0.78, H * 0.34, t, 716, None, 30)
        
        label(ctx, "DESMAIOU · VINAGRE NAS QUEIMADURAS", W * 0.78, H * 0.52, t, 722, None, 18)
        label(ctx, "SOBREVIVEU", W * 0.78, H * 0.66, t, 727.5, None, 50, GREEN)
    vignette(ctx)


# 12:18 – 13:01  Vinagre, água do mar, antiveneno
def sc_vinegar(ctx, t):
    ocean(ctx, t, rays=False)
    if t < 766:
        x0 = W * 0.15
        ctx.rectangle(x0, H * 0.62, 500, 140)
        rgba(ctx, SKIN)
        ctx.fill()
        for i in range(4):
            line(ctx, x0 + 20, H * 0.66 + i * 28, x0 + 480, H * 0.64 + i * 30, RED, 0.7, 5)
        ctx.save()
        ctx.translate(x0 + 260, H * 0.30)
        ctx.rotate(0.9 * appear(t, 738.5))
        icon(ctx, "bottle", 0, 0, 2.5, 1)
        ctx.restore()
        pour = appear(t, 739.5)
        for i in range(10):
            yy = H * 0.38 + ((t * 300 + i * 30) % 160)
            circle(ctx, x0 + 300, yy, 4, (0.95, 0.9, 0.7), 0.8 * pour)
        big_title(ctx, [("VINAGRE · ", ORANGE), ("30 SEGUNDOS", WHITE)], W * 0.72, H * 0.25, t, 741.5, None, 40)
        label(ctx, "IMPEDE AS CÉLULAS QUE AINDA", W * 0.72, H * 0.36, t, 747, None, 22)
        label(ctx, "NÃO DISPARARAM DE DISPARAR", W * 0.72, H * 0.41, t, 747, None, 22)
        label(ctx, "SEM VINAGRE? ÁGUA DO MAR", W * 0.72, H * 0.55, t, 754, None, 26, GREEN)
        label(ctx, "NUNCA ÁGUA DOCE", W * 0.72, H * 0.62, t, 757, None, 26, RED)
        label(ctx, "XIXI NÃO AJUDA", W * 0.72, H * 0.72, t, 759.5, None, 22, (0.8, 0.9, 0.9))
    else:
        # ambulância
        k = appear(t, 766)
        x, y = W * 0.30 - 200 * (1 - k), H * 0.62
        rrect(ctx, x - 160, y - 110, 320, 130, 14)
        rgba(ctx, WHITE, k)
        ctx.fill()
        rgba(ctx, RED, k)
        ctx.rectangle(x - 160, y - 30, 320, 16)
        ctx.fill()
        icon(ctx, "cross", x, y - 65, 0.9, k, RED)
        circle(ctx, x - 90, y + 25, 26, (0.15, 0.15, 0.15), k)
        circle(ctx, x + 90, y + 25, 26, (0.15, 0.15, 0.15), k)
        circle(ctx, x + 40, y - 125, 10, (0.3, 0.5, 1.0) if int(t * 4) % 2 else RED, k)
        label(ctx, "ANTIVENENO", W * 0.72, H * 0.35, t, 767.5, None, 40, ORANGE)
        label(ctx, "PRODUZIDO DESDE 1970", W * 0.72, H * 0.43, t, 769, None, 24)
        label(ctx, "MÉDICOS AINDA DISCUTEM O QUANTO AJUDA", W * 0.72, H * 0.52, t, 773, None, 18,
              (0.8, 0.9, 0.9))
    vignette(ctx)


# 13:01 – 13:33  E se fosse Irukandji
def sc_twist(ctx, t):
    ocean(ctx, t, top=(0.07, 0.15, 0.2))
    seabed(ctx, t, y=H * 0.91)
    big_title(ctx, [("E SE FOSSE ", WHITE), ("IRUKANDJI", ORANGE), ("?", WHITE)], W / 2, 80, t, 781.5, None, 40)
    label(ctx, "NENHUM GRITO · NENHUMA MARCA", W / 2, 130, t, 788, None, 22, (0.8, 0.9, 0.9))
    person(ctx, W * 0.30, H * 0.90, 1.7, outfit="red", a=appear(t, 785))
    if t > 793:
        timer(ctx, W * 0.65, H * 0.48, 110, clamp((t - 795) / 3), 1, "30 MIN")
        pk = appear(t, 798) * (0.5 + 0.5 * math.sin(t * 6))
        circle(ctx, W * 0.30, H * 0.90 - 300, 40, RED, 0.5 * pk)
    label(ctx, "AVISE SOBRE QUALQUER QUEIMADURA", W * 0.65, H * 0.78, t, 800, None, 26, ORANGE)
    label(ctx, "A IRUKANDJI VOCÊ NUNCA ENXERGA", W * 0.65, H * 0.84, t, 809, None, 20)
    vignette(ctx)


# 13:33 – 14:03  Mapa mundial
def sc_world(ctx, t):
    ocean(ctx, t, rays=False)
    pr = draw_world(ctx, W * 0.07, H * 0.14, W * 0.86, H * 0.66, appear(t, 813))
    spots = [(145.8, -16.9, "AUSTRÁLIA", 814), (100.5, 13.5, "TAILÂNDIA", 816), (121, 14, "FILIPINAS", 817),
             (115, -2, "INDONÉSIA", 818), (139, 35, "JAPÃO", 819), (-157, 21, "HAVAÍ", 820.5)]
    for lon, lat, nm, c0 in spots:
        x, y = pr(lon, lat)
        pin(ctx, x, y, appear(t, c0), nm, RED if c0 > 814 else ORANGE, "l" if nm in ("TAILÂNDIA",) else "r")
    label(ctx, "MUITAS MORTES NUNCA SÃO REGISTRADAS", W / 2, H * 0.92, t, 823, 833, 26)
    if t > 833:
        x, y = pr(150, -22)
        k = appear(t, 834)
        line(ctx, x, y - 40, x, y + 20 * k + 20, ORANGE, k, 4)
        line(ctx, x - 10, y + 20 * k + 10, x, y + 20 * k + 22, ORANGE, k, 4)
        line(ctx, x + 10, y + 20 * k + 10, x, y + 20 * k + 22, ORANGE, k, 4)
        label(ctx, "MAIS PARA O SUL? AINDA NÃO CONFIRMADO", W / 2, H * 0.92, t, 834, None, 24, ORANGE)
    vignette(ctx)


# 14:03 – 14:38  Tartarugas e antídoto
def sc_hope(ctx, t):
    ocean(ctx, t)
    if t < 850:
        turtle(ctx, W * 0.40 + (t - 843) * 15, H * 0.50, 1.3, t)
        box_jelly(ctx, W * 0.72, H * 0.30, 0.6, t)
        label(ctx, "TARTARUGAS MARINHAS COMEM ELAS", W / 2, H * 0.90, t, 845, None, 30)
    else:
        chapter(ctx, "UNIVERSIDADE DE SYDNEY", "2019", "UM ANTÍDOTO?", W / 2, 90, t, 853.5, None, 40)
        kicker(ctx, "EDIÇÃO GENÉTICA", W / 2, 130, t, 855)
        # célula com colesterol
        k = appear(t, 861)
        cx, cy = W * 0.30, H * 0.52
        circle(ctx, cx, cy, 130, (0.85, 0.55, 0.55), 0.4)
        ctx.arc(cx, cy, 130, 0, 2 * math.pi)
        rgba(ctx, (0.85, 0.55, 0.55), 1)
        ctx.set_line_width(4)
        ctx.stroke()
        for i in range(10):
            ang = i * 2 * math.pi / 10 + t * 0.2
            circle(ctx, cx + math.cos(ang) * 130, cy + math.sin(ang) * 130, 10,
                   ORANGE, k * (1 - 0.8 * appear(t, 864)))
        label(ctx, "O VENENO PRECISA DE COLESTEROL", W * 0.30, H * 0.88, t, 861, None, 22, ORANGE)
        # camundongo
        k = appear(t, 866.5)
        if k > 0:
            mx, my = W * 0.72, H * 0.55
            ctx.save()
            ctx.translate(mx, my)
            ctx.scale(1.4, 0.8)
            ctx.arc(0, 0, 60, 0, 2 * math.pi)
            ctx.restore()
            rgba(ctx, (0.75, 0.75, 0.78), k)
            ctx.fill()
            circle(ctx, mx + 75, my - 20, 30, (0.75, 0.75, 0.78), k)
            circle(ctx, mx + 70, my - 52, 16, (0.9, 0.7, 0.75), k)
            circle(ctx, mx + 92, my - 24, 4, (0.1, 0.1, 0.1), k)
            ctx.move_to(mx - 80, my)
            ctx.curve_to(mx - 140, my - 20, mx - 150, my + 40, mx - 200, my + 10)
            rgba(ctx, (0.9, 0.7, 0.75), k)
            ctx.set_line_width(4)
            ctx.stroke()
            big_title(ctx, [("ATÉ ", WHITE), ("15 MINUTOS", ORANGE)], mx, H * 0.30, t, 867.5, None, 40)
            label(ctx, "BLOQUEOU A DOR E O DANO NA PELE", mx, H * 0.80, t, 870, None, 20)
            label(ctx, "AINDA NÃO É TRATAMENTO", mx, H * 0.88, t, 873.5, None, 22, (0.8, 0.9, 0.9))
            label(ctx, "MAS É A PRIMEIRA PISTA REAL", mx, H * 0.94, t, 875.5, None, 22, GREEN)
    vignette(ctx)


# 14:38 – 15:20  Fechamento
def sc_ending(ctx, t):
    if t < 910:
        ocean(ctx, t, light=0.7)
        fade = 1 - appear(t, 887, 6)
        box_jelly(ctx, W / 2, H * 0.30, 1.3, t, a=0.3 + 0.7 * fade, glow=fade)
        label(ctx, "POUCOS MESES DE VIDA", W / 2, H * 0.85, t, 883, 888, 30)
        label(ctx, "VOCÊ SÓ FOI A COISA GRANDE QUE NADOU PARA DENTRO DA REDE DELA", W / 2, H * 0.85, t, 896, 900,
              22, ORANGE)
        if t > 900:
            p = clamp((t - 901) / 9)
            iruk(ctx, W * 0.15 + p * W * 0.7, H * 0.55, 0.9, t, appear(t, 900.5))
    else:
        sky_beach(ctx, t, sunset=1.0, cam=(t - 910) * 2)
        z = appear(t, 914, 5)
        ctx.save()
        ctx.translate(W * 0.45, H * 0.9)
        ctx.scale(1 + z * 0.5, 1 + z * 0.5)
        post_bottle(ctx, 0, 0, 1.3, glow=appear(t, 914))
        ctx.restore()
        big_title(ctx, [("LEIA A PLACA ", WHITE), ("DO POSTE", ORANGE)], W / 2, H * 0.15, t, 915.5, None, 48)
        vignette(ctx, 0.4)


# 15:20 – fim  Tela final
def sc_endcard(ctx, t):
    ocean(ctx, t)
    text(ctx, "ASSISTA", W * 0.10, H * 0.48, 64, WHITE, appear(t, 920.5), "l")
    text(ctx, "A SEGUIR", W * 0.10, H * 0.58, 64, ORANGE, appear(t, 920.8), "l")
    text(ctx, "mais do fundo do mar", W * 0.10, H * 0.65, 20, (0.7, 0.85, 0.88), appear(t, 921.2), "l", "normal")
    ctx.move_to(W * 0.45, H * 0.53)
    ctx.line_to(W * 0.45 - 22, H * 0.53 - 14)
    ctx.line_to(W * 0.45 - 22, H * 0.53 + 14)
    ctx.close_path()
    rgba(ctx, ORANGE, appear(t, 921))
    ctx.fill()
    k = appear(t, 921.5)
    rrect(ctx, W * 0.52, H * 0.30, W * 0.40, H * 0.40, 12)
    ctx.set_dash([10, 8])
    rgba(ctx, WHITE, 0.6 * k)
    ctx.set_line_width(2)
    ctx.stroke()
    ctx.set_dash([])
    box_jelly(ctx, W * 0.12, H * 0.80, 0.3, t, a=0.6, tents_per=2)
    vignette(ctx)


SCENES = [
    (0.0, 37.0, sc_beach_open),
    (37.0, 62.0, sc_sting),
    (62.0, 100.0, sc_nobrain),
    (100.0, 122.0, sc_promise),
    (122.0, 163.0, sc_anatomy),
    (163.0, 191.0, sc_cnido),
    (191.0, 211.0, sc_why),
    (211.0, 249.0, sc_venom),
    (249.0, 291.0, sc_eyes),
    (291.0, 309.0, sc_learn),
    (309.0, 350.0, sc_cycle),
    (350.0, 401.0, sc_history),
    (401.0, 435.0, sc_syndrome),
    (435.0, 463.0, sc_barnes),
    (463.0, 495.0, sc_nets),
    (495.0, 542.0, sc_trick),
    (542.0, 575.0, sc_protect),
    (575.0, 637.0, sc_scenario),
    (637.0, 738.0, sc_answers),
    (738.0, 781.0, sc_vinegar),
    (781.0, 813.0, sc_twist),
    (813.0, 843.0, sc_world),
    (843.0, 878.0, sc_hope),
    (878.0, 920.0, sc_ending),
    (920.0, 99999.0, sc_endcard),
]

CUTS = sorted({s for s, _, _ in SCENES} | {e for _, e, _ in SCENES if e < 9999} |
              {358.0, 447.0, 489.0, 506.0, 534.0, 563.0, 622.5, 679.0, 714.0, 766.0, 850.0, 910.0})


def draw_frame(ctx, t):
    for s, e, fn in SCENES:
        if s <= t < e:
            ctx.save()
            fn(ctx, t)
            ctx.restore()
            break
    # pequeno "dip" escuro nos cortes
    for c in CUTS:
        d = abs(t - c)
        if c > 0 and d < 0.25:
            rgba(ctx, (0, 0, 0), 1 - d / 0.25)
            ctx.paint()
    if t < 0.6:
        rgba(ctx, (0, 0, 0), 1 - t / 0.6)
        ctx.paint()
