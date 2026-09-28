"""Compone una pantalla (mapa de piezas 32xN + gráfico 4bpp) para ver cómo queda el texto.
Uso: python tools/ver_pantalla.py salida.png GFX_BYTES_FILE|- tilemaps... (dir. en la ROM del hack)"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
from graficos import lz77
from ver_piezas import PAL


def compose(gfx, tm, sc=2, base=0):
    n = len(tm) // 2
    rows = n // 32
    im = Image.new('RGB', (256, rows * 8), (0, 0, 0))
    px = im.load()
    for k in range(n):
        e = tm[2 * k] | tm[2 * k + 1] << 8
        t = (e & 0x3FF) - base; hf = e >> 10 & 1; vf = e >> 11 & 1
        if t < 0 or (t + 1) * 32 > len(gfx):
            continue
        tx, ty = k % 32 * 8, k // 32 * 8
        for y in range(8):
            for x in range(8):
                sx = 7 - x if hf else x; sy = 7 - y if vf else y
                v = gfx[t * 32 + sy * 4 + sx // 2]
                v = (v >> 4) if sx & 1 else (v & 15)
                px[tx + x, ty + y] = PAL[v]
    return im.resize((im.width * sc, im.height * sc), Image.NEAREST)
