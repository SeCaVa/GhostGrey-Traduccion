"""Tileset de edificios del hack: "GYM" -> "GIM", "MART" -> "SHOP" (como en el Rojo español de Game Boy),
"SELL" -> "ORO" (compraventa)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77
from hoja import to_sheet, from_sheet
from rom import u32

ROOT = os.path.join(os.path.dirname(__file__), '..')
PTR = 0x2D4A98
F5 = {
    'T': ['###', '.#.', '.#.', '.#.', '.#.'], 'I': ['###', '.#.', '.#.', '.#.', '###'],
    'E': ['###', '#..', '##.', '#..', '###'], 'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'D': ['##.', '#.#', '#.#', '#.#', '##.'], 'A': ['.#.', '#.#', '###', '#.#', '#.#'],
    'G': ['###', '#..', '#.#', '#.#', '###'], 'O': ['###', '#.#', '#.#', '#.#', '###'],
    'R': ['##.', '#.#', '##.', '#.#', '#.#'], 'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'],
    'S': ['###', '#..', '###', '..#', '###'], 'H': ['#.#', '#.#', '###', '#.#', '#.#'],
    'P': ['###', '#.#', '###', '#..', '#..'],
}


def put(img, x0, y0, w, txt, fg, bg):
    for y in range(y0, y0 + 5):
        for x in range(x0, x0 + w):
            img[y][x] = bg
    tw = sum(len(F5[c][0]) for c in txt) + len(txt) - 1
    x = x0 + (w - tw) // 2
    for c in txt:
        for dy, row in enumerate(F5[c]):
            for dx, ch in enumerate(row):
                if ch == '#':
                    img[y0 + dy][x + dx] = fg
        x += len(F5[c][0]) + 1


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    a = u32(h, PTR) - 0x8000000
    g = lz77(h, a)
    img = to_sheet(g)
    # piezas 2-3 = "POKé" (Centro Pokémon, se deja igual); piezas 4-5 = "MART" -> "SHOP" (tienda)
    put(img, 32, 3, 16, 'SHOP', 1, 4)
    put(img, 16, 10, 16, 'GIM', 4, 1)     # piezas 18-19, filas 10-14
    put(img, 112, 179, 16, 'ORO', 4, 1)   # piezas 366-367: cartel "SELL" de la compraventa de Fucsia
    open(os.path.join(ROOT, 'data/gfx/tileset_gfx.bin'), 'wb').write(from_sheet(img, g))
    print('%X' % a)


if __name__ == '__main__':
    main()
