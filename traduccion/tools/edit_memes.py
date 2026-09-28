"""Imágenes que el hack enseña con showmonpic (sprites frontales 64x64, tabla 0x2350AC):
- 392 (meme que manda Oak): "SHARE ♥" -> "COMPARTE ♥" (letra de palo como la original; el corazón se mueve).
- 268 (foto de la madre del protagonista): dedicatoria "yours ♥ / Forever" -> "tuya ♥ / siempre" (Ink Free).
Salida: data/gfx/meme_392.bin y data/gfx/meme_268.bin."""
import os, sys
from collections import Counter
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77
from hoja import to_sheet, from_sheet
from rom import u32, ROM_BASE
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
TABLA = 0x2350AC

PALO = {  # 5x10, trazos de 2 px
    'C': ['.####', '##..#', '##...', '##...', '##...', '##...', '##...', '##...', '##..#', '.####'],
    'O': ['.###.', '##.##', '##.##', '##.##', '##.##', '##.##', '##.##', '##.##', '##.##', '.###.'],
    'M': ['#...#', '##.##', '#####', '#.#.#', '#.#.#', '#...#', '#...#', '#...#', '#...#', '#...#'],
    'P': ['####.', '##.##', '##.##', '##.##', '####.', '##...', '##...', '##...', '##...', '##...'],
    'A': ['.###.', '##.##', '##.##', '##.##', '#####', '##.##', '##.##', '##.##', '##.##', '##.##'],
    'R': ['####.', '##.##', '##.##', '##.##', '####.', '##.##', '##.##', '##.##', '##.##', '##.##'],
    'T': ['#####', '#####', '.##..', '.##..', '.##..', '.##..', '.##..', '.##..', '.##..', '.##..'],
    'E': ['#####', '##...', '##...', '##...', '####.', '##...', '##...', '##...', '##...', '#####'],
}


def sprite(h, i):
    a = u32(h, TABLA + 8 * i) - ROM_BASE
    return a, lz77(h, a)


def meme_compartir(h):
    a, d = sprite(h, 392)
    img = to_sheet(d, 8)
    # corazón (x 46-58, filas 51-61) 4 px a la derecha; se borra "SHARE"
    corazon = [row[46:59] for row in img[51:62]]
    for y in range(50, 63):
        for x in range(0, 64):
            if img[y][x] == 2:
                img[y][x] = 0
    for dy, row in enumerate(corazon):
        for dx, v in enumerate(row):
            if v:
                img[51 + dy][50 + dx] = v
    x = 2
    for ch in 'COMPARTE':
        for dy, fila in enumerate(PALO[ch]):
            for dx, v in enumerate(fila):
                if v == '#':
                    img[52 + dy][x + dx] = 2
        x += 6
    return a, from_sheet(img, d, 8)


def meme_foto(h):
    a, d = sprite(h, 268)
    img = to_sheet(d, 8)
    zonas = [(2, 12, 0, 40), (11, 25, 0, 60)]  # (fila0, fila1, x0, x1) de "yours" y "Forever"
    texto = {(x, y) for y0, y1, x0, x1 in zonas for y in range(y0, y1) for x in range(x0, x1) if img[y][x] == 3}
    while texto:  # rellena la letra con el color de alrededor
        nuevos = {}
        for x, y in texto:
            c = Counter(img[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                        if 0 <= y + dy < 64 and 0 <= x + dx < 64 and (x + dx, y + dy) not in texto)
            c.pop(0, None)
            if c:
                nuevos[(x, y)] = c.most_common(1)[0][0]
        if not nuevos:
            break
        for (x, y), v in nuevos.items():
            img[y][x] = v
            texto.discard((x, y))
    for y in range(2, 10):  # restos de la "y" de "yours" (colores 1 y 2) fuera de la foto
        for x in range(0, 8):
            img[y][x] = 0
    f = ImageFont.truetype('C:/Windows/Fonts/Inkfree.ttf', 13)
    for txt, x0, y0 in (('tuya', 8, 2), ('siempre', 18, 13)):
        t = Image.new('1', (100, 30)); dr = ImageDraw.Draw(t); dr.fontmode = '1'
        dr.text((1, 1), txt, font=f, fill=1)
        t = t.crop(t.getbbox())
        for y in range(t.height):
            for x in range(t.width):
                if t.getpixel((x, y)):
                    img[y0 + y][x0 + x] = 3
    return a, from_sheet(img, d, 8)


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    os.makedirs(os.path.join(ROOT, 'data/gfx'), exist_ok=True)
    for nombre, fn in (('meme_392', meme_compartir), ('meme_268', meme_foto)):
        a, d = fn(h)
        open(os.path.join(ROOT, 'data/gfx/%s.bin' % nombre), 'wb').write(d)
        print(nombre, '%X' % a)


if __name__ == '__main__':
    main()
