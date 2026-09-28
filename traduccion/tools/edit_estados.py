"""Piezas de la barra de vida en combate (sin comprimir, 0xD11BC4 en las tres ROM): "HP" y los estados
PSN/PAR/SLP/FRZ/BRN -> PS y ENV/PAR/DOR/CON/QUE del RF español, con los colores del hack.
Píxel a píxel: donde el español coincide con el USA se deja el píxel del hack; donde cambia se usa el
color que el hack da (por mayoría) a ese color USA dentro del mismo icono.
Salida: data/gfx/estados_gfx.bin (se escribe tal cual en 0xD11BC4)."""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from graficos import _px, _tile

ROOT = os.path.join(os.path.dirname(__file__), '..')
BASE, NPIEZAS = 0xD11BC4, 118
GRUPOS = [(1, 2)] + [(s, 3) for s in range(21, 36, 3)] + [(s, 3) for s in range(71, 116, 3)]


def main():
    us = open(os.path.join(ROOT, '../Pokemon - FireRed Version (USA).gba'), 'rb').read()
    es = open(os.path.join(ROOT, '../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()
    hk = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    out = bytearray(hk[BASE:BASE + NPIEZAS * 32])

    def px(r, t):
        return _px(r[BASE + t * 32:BASE + t * 32 + 32])
    for s, n in GRUPOS:
        pu = sum((px(us, t) for t in range(s, s + n)), [])
        pe = sum((px(es, t) for t in range(s, s + n)), [])
        ph = sum((px(hk, t) for t in range(s, s + n)), [])
        if pu == pe:
            continue
        votos = {}
        for i, (a, c) in enumerate(zip(pu, ph)):
            x, y = i // 64 * 8 + i % 8, i % 64 // 8
            if n == 3 and not (2 <= x <= 17 and 1 <= y <= 6):
                continue  # solo el interior de la pastilla (los bordes el hack los pinta distinto)
            votos.setdefault(a, Counter())[c] += 1
        m = {a: v.most_common(1)[0][0] for a, v in votos.items()}
        nuevo = [c if e == u else m.get(e, e) for u, e, c in zip(pu, pe, ph)]
        for k, t in enumerate(range(s, s + n)):
            out[t * 32:t * 32 + 32] = _tile(nuevo[k * 64:k * 64 + 64])
    os.makedirs(os.path.join(ROOT, 'data/gfx'), exist_ok=True)
    open(os.path.join(ROOT, 'data/gfx/estados_gfx.bin'), 'wb').write(out)
    print('ok')


if __name__ == '__main__':
    main()
