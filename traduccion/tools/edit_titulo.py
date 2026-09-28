"""Pantalla de título: "PRESS START IF YOU DARE" -> "PULSA START SI TE ATREVES" (última palabra resaltada)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77
from gfxedit import region, put_region, used_tiles

ROOT = os.path.join(os.path.dirname(__file__), '..')
GFX, TM, TM2 = 0x26D3C0, 0x275300, 0x2754C0
F = {
    'P': ['#######', '##...##', '##...##', '#######', '##.....'],
    'U': ['##...##', '##...##', '##...##', '###.###', '.#####.'],
    'L': ['##.....', '##.....', '##.....', '##.....', '#######'],
    'S': ['#######', '##.....', '#######', '.....##', '#######'],
    'A': ['...##...', '..####..', '.##..##.', '########', '##....##'],
    'T': ['########', '...##...', '...##...', '...##...', '...##...'],
    'R': ['######.', '##...##', '##...##', '##.###.', '##..###'],
    'I': ['##', '##', '##', '##', '##'],
    'E': ['#######', '##.....', '######.', '##.....', '#######'],
    'V': ['##...##', '##...##', '.##.##.', '.##.##.', '..###..'],
    ' ': ['......'],
}
BG, TXT, HL = 7, 2, 6


def wd(s):
    return sum(len(F[c][0]) for c in s) + len(s) - 1


def draw(img, x, y, s):
    for c in s:
        if c != ' ':
            for dy, row in enumerate(F[c]):
                for dx, ch in enumerate(row):
                    if ch == '#':
                        img[y + dy][x + dx] = TXT
        x += len(F[c][0]) + 1
    return x


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    gfx = bytearray(lz77(h, GFX)); tm = bytearray(lz77(h, TM))
    free = [t for t in range(1, len(gfx) // 32) if t not in used_tiles([tm, lz77(h, TM2)])]
    img = region(gfx, tm, 0, 16, 30, 3)          # filas de piezas 16-18 (y 128-151)
    for row in img:
        for x in range(len(row)):
            row[x] = BG
    normal, hl = 'PULSA START SI TE ', 'ATREVES'
    x0 = (240 - wd(normal + hl)) // 2
    xh = x0 + wd(normal) + 1
    xe = xh + wd(hl) - 1
    for x in range(xh - 3, xe + 3):               # recuadro resaltado, como el de "DARE"
        img[7][x] = HL
        for y in range(16, 23):
            img[y][x] = HL
    draw(img, x0, 18, normal)
    draw(img, xh, 18, hl)
    put_region(gfx, tm, 0, 16, img, free)
    open(os.path.join(ROOT, 'data/gfx/titulo_gfx.bin'), 'wb').write(gfx)
    open(os.path.join(ROOT, 'data/gfx/titulo_tm.bin'), 'wb').write(tm)
    print('piezas libres restantes', len(free))


if __name__ == '__main__':
    main()
