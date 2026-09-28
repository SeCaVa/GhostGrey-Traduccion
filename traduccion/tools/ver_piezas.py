"""Muestra un gráfico (US / ES / hack) ampliado con cuadrícula de piezas numeradas.
Uso: python tools/ver_piezas.py US_ADDR ES_ADDR PTR_HACK salida.png [ancho_piezas] [desde] [hasta] [escala]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw
from graficos import lz77
from rom import u32

PAL = [(0, 0, 0), (255, 255, 255), (200, 200, 200), (120, 120, 120), (255, 0, 0), (0, 160, 0), (0, 0, 255),
       (255, 200, 0), (255, 0, 255), (0, 200, 200), (140, 70, 0), (255, 140, 140), (140, 255, 140),
       (140, 140, 255), (80, 0, 120), (60, 60, 60)]


def render(d, wt, a, b, sc):
    n = min(len(d) // 32, b) - a
    ht = (n + wt - 1) // wt
    im = Image.new('RGB', (wt * 8 * sc, ht * 8 * sc), (40, 40, 40))
    px = im.load()
    for k in range(n):
        t = a + k
        tx, ty = k % wt * 8, k // wt * 8
        for y in range(8):
            for x in range(8):
                v = d[t * 32 + y * 4 + x // 2]
                v = (v >> 4) if x & 1 else (v & 15)
                for dy in range(sc):
                    for dx in range(sc):
                        px[(tx + x) * sc + dx, (ty + y) * sc + dy] = PAL[v]
    dr = ImageDraw.Draw(im)
    for k in range(n):
        tx, ty = k % wt * 8 * sc, k // wt * 8 * sc
        dr.rectangle([tx, ty, tx + 8 * sc - 1, ty + 8 * sc - 1], outline=(90, 90, 90))
        dr.text((tx + 1, ty), str(a + k), fill=(255, 255, 0))
    return im


if __name__ == '__main__':
    R = os.path.join(os.path.dirname(__file__), '..')
    us = open(os.path.join(R, '../Pokemon - FireRed Version (USA).gba'), 'rb').read()
    es = open(os.path.join(R, '../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()
    h = open(os.path.join(R, 'build/ghostgrey_en.gba'), 'rb').read()
    ua, ea, pa = (int(x, 16) for x in sys.argv[1:4])
    wt = int(sys.argv[5]) if len(sys.argv) > 5 else 16
    a = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    b = int(sys.argv[7]) if len(sys.argv) > 7 else 9999
    sc = int(sys.argv[8]) if len(sys.argv) > 8 else 4
    ims = [render(d, wt, a, b, sc) for d in (lz77(us, ua), lz77(es, ea), lz77(h, u32(h, pa) - 0x8000000))]
    S = Image.new('RGB', (max(i.width for i in ims), sum(i.height + 8 for i in ims)), (0, 0, 0))
    y = 0
    for i in ims:
        S.paste(i, (0, y)); y += i.height + 8
    S.save(sys.argv[4])
