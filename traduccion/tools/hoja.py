"""Hoja de piezas (16 de ancho) como matriz de índices, para editar texto sin tocar el mapa de piezas."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import _px, _tile


def to_sheet(g, wt=16):
    n = len(g) // 32; ht = (n + wt - 1) // wt
    img = [[0] * (wt * 8) for _ in range(ht * 8)]
    for t in range(n):
        p = _px(g[t * 32:t * 32 + 32])
        for y in range(8):
            for x in range(8):
                img[t // wt * 8 + y][t % wt * 8 + x] = p[y * 8 + x]
    return img


def from_sheet(img, g, wt=16):
    out = bytearray(g)
    for t in range(len(g) // 32):
        out[t * 32:t * 32 + 32] = _tile([img[t // wt * 8 + y][t % wt * 8 + x] for y in range(8) for x in range(8)])
    return bytes(out)


def dump(img, x0, y0, x1, y1):
    for y in range(y0, y1):
        print('%3d' % y, ''.join('0123456789abcdef'[v] for v in img[y][x0:x1]))
