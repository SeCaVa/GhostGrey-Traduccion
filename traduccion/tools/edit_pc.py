"""PC de Bill (gráfico rediseñado por el hack): mezcla con el español y rehace el título "GHST DATA"."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77, mezcla
from hoja import to_sheet, from_sheet

ROOT = os.path.join(os.path.dirname(__file__), '..')
GFX = 0x8B1480
FONT8 = {
    'D': ['###.', '#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '###.'],
    'A': ['.##.', '#..#', '#..#', '#..#', '####', '#..#', '#..#', '#..#'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'O': ['.##.', '#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'S': ['.##.', '#..#', '#...', '.##.', '...#', '...#', '#..#', '.##.'],
    'F': ['####', '#...', '#...', '###.', '#...', '#...', '#...', '#...'],
    'N': ['#..#', '##.#', '##.#', '#.##', '#.##', '#..#', '#..#', '#..#'],
    '.': ['.', '.', '.', '.', '.', '.', '.', '#'],
    ' ': ['..', '..', '..', '..', '..', '..', '..', '..'],
}


def draw(img, x, y, s, col):
    for ch in s:
        g = FONT8[ch]
        for dy, row in enumerate(g):
            for dx, c in enumerate(row):
                if c == '#':
                    img[y + dy][x + dx] = col
        x += len(g[0]) + 1


def width(s):
    return sum(len(FONT8[c][0]) for c in s) + len(s) - 1


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    us = open(os.path.join(ROOT, '../Pokemon - FireRed Version (USA).gba'), 'rb').read()
    es = open(os.path.join(ROOT, '../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()
    g, _, _ = mezcla(lz77(us, 0xE9C438), lz77(es, 0xE9C404), lz77(h, GFX))
    img = to_sheet(g)
    for y in range(4, 12):
        for x in range(8, 72):
            if img[y][x] == 0xB:
                img[y][x] = 3
    t = 'DATOS FANT.'
    draw(img, 40 - width(t) // 2, 4, t, 0xB)
    # "MENU" -> "MENÚ": se baja el texto una fila para que quepa la tilde sobre la U
    for y in range(28, 19, -1):
        for x in range(92, 118):
            img[y][x] = img[y - 1][x]
    for x in range(92, 118):
        img[20][x] = 0xB
    img[20][112] = 7; img[19][113] = 7
    os.makedirs(os.path.join(ROOT, 'data/gfx'), exist_ok=True)
    open(os.path.join(ROOT, 'data/gfx/pc_gfx.bin'), 'wb').write(from_sheet(img, g))


if __name__ == '__main__':
    main()
