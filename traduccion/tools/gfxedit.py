"""Utilidades para editar texto dibujado en fondos: componer una zona de un mapa de piezas como imagen
indexada, modificarla y volver a partirla en piezas (reutilizando piezas libres) actualizando el mapa."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77, _px, _tile


def tm_get(tm, c, r):
    return tm[2 * (r * 32 + c)] | tm[2 * (r * 32 + c) + 1] << 8


def tm_set(tm, c, r, e):
    tm[2 * (r * 32 + c)] = e & 0xFF; tm[2 * (r * 32 + c) + 1] = e >> 8


def tile_px(gfx, t, hf=0, vf=0):
    p = _px(gfx[t * 32:t * 32 + 32])
    return [[p[(7 - y if vf else y) * 8 + (7 - x if hf else x)] for x in range(8)] for y in range(8)]


def region(gfx, tm, c0, r0, w, h):
    """Devuelve matriz de índices de color (h*8 x w*8) de la zona."""
    img = [[0] * (w * 8) for _ in range(h * 8)]
    for r in range(h):
        for c in range(w):
            e = tm_get(tm, c0 + c, r0 + r)
            p = tile_px(gfx, e & 0x3FF, e >> 10 & 1, e >> 11 & 1)
            for y in range(8):
                for x in range(8):
                    img[r * 8 + y][c * 8 + x] = p[y][x]
    return img


def used_tiles(tms):
    s = set()
    for tm in tms:
        for k in range(len(tm) // 2):
            s.add((tm[2 * k] | tm[2 * k + 1] << 8) & 0x3FF)
    return s


def put_region(gfx, tm, c0, r0, img, free_tiles):
    """Vuelve a partir la imagen en piezas. Las piezas iguales a las existentes se mantienen;
    las nuevas ocupan piezas libres. Modifica gfx (bytearray) y tm (bytearray)."""
    h, w = len(img) // 8, len(img[0]) // 8
    for r in range(h):
        for c in range(w):
            e = tm_get(tm, c0 + c, r0 + r)
            p = [img[r * 8 + y][c * 8 + x] for y in range(8) for x in range(8)]
            cur = tile_px(gfx, e & 0x3FF, e >> 10 & 1, e >> 11 & 1)
            if [v for row in cur for v in row] == p:
                continue
            t = free_tiles.pop(0)
            gfx[t * 32:t * 32 + 32] = _tile(p)
            tm_set(tm, c0 + c, r0 + r, (e & 0xF000) | t)
