"""Dibuja gráficos 4bpp (US | ES | hack) en una hoja PNG para revisarlos."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw
from graficos import lz77
from rom import u32, ROM_BASE

ROOT = os.path.join(os.path.dirname(__file__), '..')


def tiles_img(d, wt=16, scale=2):
    n = len(d) // 32
    ht = (n + wt - 1) // wt
    im = Image.new('L', (wt * 8, max(1, ht) * 8), 0)
    px = im.load()
    for t in range(n):
        tx, ty = t % wt * 8, t // wt * 8
        for y in range(8):
            for x in range(8):
                b = d[t * 32 + y * 4 + x // 2]
                v = (b >> 4) if x & 1 else (b & 15)
                px[tx + x, ty + y] = v * 17
    return im.resize((im.width * scale, im.height * scale), Image.NEAREST)


def sheet(items, out, wt=16):
    us = open(os.path.join(ROOT, '../Pokemon - FireRed Version (USA).gba'), 'rb').read()
    es = open(os.path.join(ROOT, '../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    rows = []
    for r in items:
        a = tiles_img(lz77(us, int(r['us'], 16)), wt)
        b = tiles_img(lz77(es, int(r['es'], 16)), wt)
        p = int(r['punteros'][0], 16)
        dh = lz77(h, u32(h, p) - ROM_BASE)
        c = tiles_img(dh, wt) if dh else Image.new('L', (8, 8))
        rows.append((r['us'], a, b, c))
    W = sum(max(x[i].width for x in rows) for i in (1, 2, 3)) + 120
    H = sum(max(x[1].height, x[2].height, x[3].height) + 14 for x in rows)
    S = Image.new('L', (W, H), 60)
    dr = ImageDraw.Draw(S)
    y = 0
    w1 = max(x[1].width for x in rows); w2 = max(x[2].width for x in rows)
    for name, a, b, c in rows:
        dr.text((2, y + 2), name, fill=255)
        S.paste(a, (70, y + 12)); S.paste(b, (80 + w1, y + 12)); S.paste(c, (90 + w1 + w2, y + 12))
        y += max(a.height, b.height, c.height) + 14
    S.save(out)


if __name__ == '__main__':
    g = json.load(open(os.path.join(ROOT, 'data/graficos.json')))
    sel = [r for r in g if eval(sys.argv[2])]
    sheet(sel[:int(sys.argv[3]) if len(sys.argv) > 3 else 40], sys.argv[1], wt=int(sys.argv[4]) if len(sys.argv) > 4 else 16)
    print(len(sel))
