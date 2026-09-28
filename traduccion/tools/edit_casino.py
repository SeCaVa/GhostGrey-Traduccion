"""Tragaperras del casino (rediseñada por el hack): "CREDIT" -> "CRÉDITO", "PAYOUT" -> "PREMIO"."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77, _tile
from gfxedit import region, tm_get, tm_set, put_region, used_tiles
from rom import u32

ROOT = os.path.join(os.path.dirname(__file__), '..')
PTR_GFX, TM = 0x1413AC, 0x7B1980
F = {
    'C': ['.##', '#..', '#..', '#..', '.##'], 'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'E': ['###', '#..', '##.', '#..', '###'], 'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'I': ['###', '.#.', '.#.', '.#.', '###'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'O': ['.#.', '#.#', '#.#', '#.#', '.#.'], 'P': ['##.', '#.#', '##.', '#..', '#..'],
    'M': ['#.#', '###', '#.#', '#.#', '#.#'],
}


def write(img, x, txt, acc=None):
    for i, c in enumerate(txt):
        for dy, row in enumerate(F[c]):
            for dx, ch in enumerate(row):
                if ch == '#':
                    img[1 + dy][x + dx] = 3
        if acc == i:
            img[0][x + 1] = 3; img[0][x + 2] = 3
        x += 4


# letras huecas de los carteles laterales: esqueleto (relleno 2) de 12 filas; el contorno (1) se añade solo
BIG = {
    'P': ['###.', '#..#', '#..#', '#..#', '#..#', '###.', '#...', '#...', '#...', '#...', '#...', '#...'],
    'O': ['.##.', '#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'N': ['#..#', '##.#', '##.#', '##.#', '#.##', '#.##', '#.##', '#..#', '#..#', '#..#', '#..#', '#..#'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '#...#', '#...#'],
    'A': ['.##.', '#..#', '#..#', '#..#', '#..#', '####', '#..#', '#..#', '#..#', '#..#', '#..#', '#..#'],
    'S': ['.###', '#...', '#...', '#...', '#...', '.##.', '...#', '...#', '...#', '...#', '...#', '###.'],
    'G': ['.###', '#...', '#...', '#...', '#...', '#.##', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
}


def big_word(img, x0, x1, y, word, gap=3):
    """Dibuja una palabra centrada entre x0 y x1 (fila superior del contorno en y). 'Á' = A con tilde."""
    glyphs = [BIG['A'] if c == 'Á' else BIG[c] for c in word]
    w = sum(len(g[0]) for g in glyphs) + gap * (len(glyphs) - 1) + 2
    x = x0 + (x1 - x0 + 1 - w) // 2 + 1
    fill = set()
    for c, g in zip(word, glyphs):
        for dy, row in enumerate(g):
            for dx, ch in enumerate(row):
                if ch == '#':
                    fill.add((x + dx, y + 1 + dy))
        if c == 'Á':
            fill.add((x + 1, y - 1)); fill.add((x + 2, y - 2))
        x += len(g[0]) + gap
    for (fx, fy) in fill:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (fx + dx, fy + dy)
                if q not in fill:
                    img[q[1]][q[0]] = 1
    for (fx, fy) in fill:
        img[fy][fx] = 2


def carteles(g, tm, free):
    # cada cartel ocupa 4 columnas (una más que el original, hacia el hueco rojo) y las filas 5-9
    for c0, words in ((0, ('PON', 'MÁS')), (26, ('GANA', 'MÁS'))):
        img = region(g, tm, c0, 5, 4, 5)
        xa, xb = (0, 31) if c0 == 0 else (7, 32)
        for y in range(4, 36):
            for x in range(32):
                if y >= 30 and (x >= 24 if c0 == 0 else x <= 6):
                    continue  # tubería decorativa junto a la columna extra
                img[y][x] = 4
        big_word(img, xa, xb - 1, 5, words[0], gap=2 if len(words[0]) > 3 else 3)
        big_word(img, xa, xb - 1, 23, words[1])
        cnt = {}
        for k in range(len(tm) // 2):
            t = (tm[2 * k] | tm[2 * k + 1] << 8) & 0x3FF
            cnt[t] = cnt.get(t, 0) + 1
        for r in range(5):
            for c in range(4):
                e = tm_get(tm, c0 + c, 5 + r)
                px = [img[r * 8 + y][c * 8 + x] for y in range(8) for x in range(8)]
                t = e & 0x3FF
                if cnt[t] != 1:  # pieza compartida (fondo rojo liso): se usa una pieza libre
                    if px == [4] * 64:
                        continue
                    t = free.pop(0)
                    tm_set(tm, c0 + c, 5 + r, (e & 0xF000) | t)
                g[t * 32:t * 32 + 32] = _tile(px)


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    a = u32(h, PTR_GFX) - 0x8000000
    g = bytearray(lz77(h, a)); tm = bytearray(lz77(h, TM))
    free = [t for t in range(2, len(g) // 32) if t not in used_tiles([tm])]
    img = region(g, tm, 8, 2, 16, 1)
    for x0, x1 in ((18, 45), (66, 93)):
        for y in range(0, 6):
            for x in range(x0, x1 + 1):
                img[y][x] = 4
    write(img, 18, 'CREDITO', acc=2)
    write(img, 68, 'PREMIO')
    for c in range(16):  # las piezas de esta fila son únicas: se reescriben en su sitio
        t = tm_get(tm, 8 + c, 2) & 0x3FF
        if t == 6:
            continue
        g[t * 32:t * 32 + 32] = _tile([img[y][c * 8 + x] for y in range(8) for x in range(8)])
    carteles(g, tm, free)
    open(os.path.join(ROOT, 'data/gfx/casino_tm.bin'), 'wb').write(tm)
    print('libres', len(free))
    open(os.path.join(ROOT, 'data/gfx/casino_gfx.bin'), 'wb').write(g)
    print('%X' % a)


if __name__ == '__main__':
    main()
