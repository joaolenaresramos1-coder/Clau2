"""Movimento com lógica física para personagens e animais.

Regras que este módulo garante:
- A direção (facing) sai SEMPRE da velocidade real: ninguém anda ou nada de costas.
  Quando para, mantém a última direção (histerese), sem "virar" sozinho.
- A cadência do passo/braçada é proporcional à velocidade: pés não deslizam no chão,
  e quem está parado não continua batendo as pernas.
- O corpo inclina na direção em que sobe/desce (nado, mergulho, subida).
- Dentro d'água tudo desacelera suave (sem paradas bruscas); objetos soltos afundam
  ou flutuam com velocidade constante e um leve balanço.
"""
import math

PX_PER_M = 120.0  # escala usada para converter px/s em passos


def smooth(k):
    k = max(0.0, min(1.0, k))
    return k * k * (3 - 2 * k)


class Path:
    """Trajetória por quadros-chave [(t, x, y), ...] com interpolação suave."""

    def __init__(self, keys):
        self.keys = sorted(keys)

    def pos(self, t):
        k = self.keys
        if t <= k[0][0]:
            return k[0][1], k[0][2]
        for (t0, x0, y0), (t1, x1, y1) in zip(k, k[1:]):
            if t <= t1:
                q = smooth((t - t0) / max(1e-6, t1 - t0))
                return x0 + (x1 - x0) * q, y0 + (y1 - y0) * q
        return k[-1][1], k[-1][2]

    def vel(self, t, dt=1 / 24):
        x0, y0 = self.pos(t - dt)
        x1, y1 = self.pos(t + dt)
        return (x1 - x0) / (2 * dt), (y1 - y0) / (2 * dt)

    def facing(self, t, default=1, thresh=4.0):
        """Direção pela velocidade; parado, olha para onde estava indo por último."""
        vx, _ = self.vel(t)
        if abs(vx) > thresh:
            return 1 if vx > 0 else -1
        # procura para trás o último instante com movimento
        tt = t
        for _ in range(240):
            tt -= 1 / 24
            if tt < self.keys[0][0]:
                break
            vx, _ = self.vel(tt)
            if abs(vx) > thresh:
                return 1 if vx > 0 else -1
        return default

    def speed(self, t):
        vx, vy = self.vel(t)
        return math.hypot(vx, vy)

    def phase(self, t, stride_px, t0=None):
        """Fase do ciclo (passos/braçadas) integrada da distância percorrida: pé não desliza."""
        t0 = self.keys[0][0] if t0 is None else t0
        n = max(1, int((t - t0) * 24))
        d = 0.0
        px, py = self.pos(t0)
        for i in range(1, n + 1):
            x, y = self.pos(t0 + i / 24)
            d += math.hypot(x - px, y - py)
            px, py = x, y
        return d / stride_px

    def pitch(self, t, scale=0.6, limit=0.6):
        """Inclinação do corpo (rad) pela razão entre velocidade vertical e horizontal."""
        vx, vy = self.vel(t)
        if abs(vx) + abs(vy) < 2:
            return 0.0
        a = math.atan2(vy, abs(vx)) * scale
        return max(-limit, min(limit, a))


def sink(t, t0, y0, floor, speed=40.0, wobble=6.0):
    """Objeto solto afundando com velocidade constante e balanço lateral até o fundo."""
    if t < t0:
        return 0.0, y0
    y = min(floor, y0 + (t - t0) * speed)
    dx = math.sin((t - t0) * 2.2) * wobble * (1 if y < floor else 0)
    return dx, y


def rise(t, t0, y0, top, speed=60.0):
    """Bolhas e objetos que flutuam: sobem até a superfície e param nela."""
    if t < t0:
        return y0
    return max(top, y0 - (t - t0) * speed)
