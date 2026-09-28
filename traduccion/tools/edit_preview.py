"""Pantallas de carga al entrar en mazmorras (map preview de RF). El hack tiene su propia tabla en 0xA08340
(30 entradas de 16 bytes: mapsec, tipo, flag, gráfico LZ, mapa LZ 32x20, paleta). Solo la de la Cueva
Diglett (entrada 2) lleva texto: "OUTSIDER LEAVE" -> "FORASTERO FUERA" (fuente Ink Free, estirada en vertical
para imitar las letras a mano del original).
Salida: data/gfx/preview_diglett_gfx.bin y _tm.bin."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77, _px, _tile
from rom import u32, ROM_BASE
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
TABLA, ENTRADA = 0xA08340, 2
FONDO, LETRA = 3, 0xC


def pantalla(g, tm, W=32):
    img = [[0] * (W * 8) for _ in range(len(tm) // 2 // W * 8)]
    for k in range(len(tm) // 2):
        e = tm[2 * k] | tm[2 * k + 1] << 8
        p = _px(g[(e & 0x3FF) * 32:][:32])
        hf, vf = e >> 10 & 1, e >> 11 & 1
        for y in range(8):
            for x in range(8):
                img[k // W * 8 + y][k % W * 8 + x] = p[(7 - y if vf else y) * 8 + (7 - x if hf else x)]
    return img


def rehacer(img, tm, W=32):
    """Piezas únicas (reutilizando volteos) y mapa nuevo conservando la paleta de cada casilla."""
    piezas = {}; gfx = bytearray(); out = bytearray(tm)
    for k in range(len(tm) // 2):
        c, r = k % W, k // W
        px = [[img[r * 8 + y][c * 8 + x] for x in range(8)] for y in range(8)]
        hallada = None
        for hf in (0, 1):
            for vf in (0, 1):
                clave = _tile([px[7 - y if vf else y][7 - x if hf else x] for y in range(8) for x in range(8)])
                if clave in piezas:
                    hallada = (piezas[clave], hf, vf)
                    break
            if hallada:
                break
        if not hallada:
            clave = _tile([v for fila in px for v in fila])
            piezas[clave] = len(gfx) // 32; gfx += clave
            hallada = (piezas[clave], 0, 0)
        e = (tm[2 * k] | tm[2 * k + 1] << 8) & 0xF000 | hallada[0] | hallada[1] << 10 | hallada[2] << 11
        out[2 * k] = e & 0xFF; out[2 * k + 1] = e >> 8
    return bytes(gfx), bytes(out)


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    pg = u32(h, TABLA + 16 * ENTRADA + 4) - ROM_BASE
    pm = u32(h, TABLA + 16 * ENTRADA + 8) - ROM_BASE
    g, tm = lz77(h, pg), lz77(h, pm)
    img = pantalla(g, tm)
    for y in range(104, 132):
        for x in range(60, 190):
            if img[y][x] == LETRA:
                img[y][x] = FONDO
    f = ImageFont.truetype('C:/Windows/Fonts/Inkfree.ttf', 18)
    t = Image.new('1', (400, 60)); d = ImageDraw.Draw(t); d.fontmode = '1'
    d.text((2, 2), 'FORASTERO FUERA', font=f, fill=1)
    t = t.crop(t.getbbox())
    t = t.resize((t.width, t.height * 3 // 2), Image.NEAREST)
    x0, y0 = 120 - t.width // 2, 106
    for y in range(t.height):
        for x in range(t.width):
            if t.getpixel((x, y)):
                img[y0 + y][x0 + x] = LETRA
    ng, nt = rehacer(img, tm)
    assert len(ng) <= len(g), 'demasiadas piezas: %d > %d' % (len(ng) // 32, len(g) // 32)
    os.makedirs(os.path.join(ROOT, 'data/gfx'), exist_ok=True)
    open(os.path.join(ROOT, 'data/gfx/preview_diglett_gfx.bin'), 'wb').write(ng)
    open(os.path.join(ROOT, 'data/gfx/preview_diglett_tm.bin'), 'wb').write(nt)
    print('piezas %d (antes %d)  gráfico %X  mapa %X' % (len(ng) // 32, len(g) // 32, pg, pm))


if __name__ == '__main__':
    main()
