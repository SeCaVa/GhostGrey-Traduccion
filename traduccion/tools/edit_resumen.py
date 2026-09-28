"""Pantalla de datos del Pokémon (rediseñada por el hack): mezcla con el gráfico español y redibuja
las etiquetas propias del hack en castellano. Escribe data/gfx/resumen_*.bin (los inserta build.py)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77, mezcla
from gfxedit import region, put_region, used_tiles

ROOT = os.path.join(os.path.dirname(__file__), '..')
GFX, TM1, TM3 = 0x728940, 0x728740, 0x729C00
OTHER_TMS = [0x7AC940, 0x729E80, 0xE9BBCC, 0x7AC500, 0x463C80]

# fuente 7 filas, estilo de las etiquetas del hack
FONT = {
    'A': ['.##.', '#..#', '#..#', '####', '#..#', '#..#', '#..#'],
    'B': ['###.', '#..#', '#..#', '###.', '#..#', '#..#', '###.'],
    'D': ['###.', '#..#', '#..#', '#..#', '#..#', '#..#', '###.'],
    'E': ['####', '#...', '#...', '###.', '#...', '#...', '####'],
    'H': ['#..#', '#..#', '#..#', '####', '#..#', '#..#', '#..#'],
    'I': ['###', '.#.', '.#.', '.#.', '.#.', '.#.', '###'],
    'J': ['..##', '...#', '...#', '...#', '#..#', '#..#', '.##.'],
    'L': ['#...', '#...', '#...', '#...', '#...', '#...', '####'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#', '#...#', '#...#'],
    'N': ['#..#', '##.#', '##.#', '#.##', '#.##', '#..#', '#..#'],
    'O': ['.##.', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'P': ['###.', '#..#', '#..#', '###.', '#...', '#...', '#...'],
    'R': ['###.', '#..#', '#..#', '###.', '#.#.', '#..#', '#..#'],
    'S': ['.###', '#...', '#...', '.##.', '...#', '...#', '###.'],
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..'],
    'X': ['#..#', '#..#', '.##.', '.##.', '.##.', '#..#', '#..#'],
    '.': ['.', '.', '.', '.', '.', '.', '#'],
    'º': ['###', '#.#', '###', '...', '###', '...', '...'],
    ' ': ['..', '..', '..', '..', '..', '..', '..'],
}


def text_width(s):
    return sum(len(FONT[ch][0]) for ch in s) + len(s) - 1


def draw_text(img, x, y, s, col):
    for ch in s:
        g = FONT[ch]
        for dy, row in enumerate(g):
            for dx, c in enumerate(row):
                if c == '#':
                    img[y + dy][x + dx] = col
        x += len(g[0]) + 1


def clear_span(img, y0, y1, marks, x0=0, x1=9999):
    """Borra el recuadro/texto original de las filas y0..y1: rellena el tramo con píxeles 'marks'
    con el color que hay justo a su izquierda en cada fila."""
    xs = [x for y in range(y0, y1 + 1) for x, v in enumerate(img[y]) if v in marks and x0 <= x <= x1]
    if not xs:
        return
    a, b = min(xs) - 1, max(xs) + 1
    for y in range(y0, y1 + 1):
        vals = [img[y][x] for x in range(a, b + 1) if img[y][x] not in marks]
        fill = max(set(vals), key=vals.count) if vals else img[y][a - 1]
        if fill == 2 and marks == (0xE, 0xF):
            fill = img[y][a - 1]  # el recuadro gris se sustituye por el fondo de la pastilla
        for x in range(a, b + 1):
            img[y][x] = fill


def label_box(img, top, text, xmin, xmax):
    """Etiqueta amarilla: recuadro gris (2) con bordes (e) y texto (f), centrado entre xmin y xmax."""
    clear_span(img, top - 1, top + 7, (0xE, 0xF), xmin, xmax)
    w = text_width(text) + 2
    c = (xmin + xmax) // 2
    bx0 = c - w // 2; bx1 = bx0 + w - 1
    for x in range(bx0, bx1 + 1):
        img[top - 1][x] = 2
    for y in range(top, top + 8):
        img[y][bx0 - 1] = 0xE; img[y][bx1 + 1] = 0xE
        for x in range(bx0, bx1 + 1):
            img[y][x] = 2
    draw_text(img, bx0 + 1, top, text, 0xF)


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    us = open(os.path.join(ROOT, '../Pokemon - FireRed Version (USA).gba'), 'rb').read()
    es = open(os.path.join(ROOT, '../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()
    gfx, _, _ = mezcla(lz77(us, 0xE9A460), lz77(es, 0xE9A3E0), lz77(h, GFX))
    gfx = bytearray(gfx)
    tm1 = bytearray(lz77(h, TM1)); tm3 = bytearray(lz77(h, TM3))
    others = [lz77(h, a) for a in OTHER_TMS]
    used = used_tiles([tm1, tm3] + others)
    free = [t for t in range(1, len(gfx) // 32) if t not in used]

    # página 1: columna de etiquetas amarillas (6x12 piezas desde col 15, fila 2)
    img = region(gfx, tm1, 15, 2, 6, 12)
    for top, txt in [(7, 'N.º'), (22, 'NOMBRE'), (37, 'TIPO'), (52, 'EO'), (67, 'Nº ID'), (82, 'OBJETO')]:
        label_box(img, top, txt, 6, 41)
    put_region(gfx, tm1, 15, 2, img, free)
    # "TRAINER MEMO" (pastilla azul, filas 12-13 de las columnas 0-11)
    img = region(gfx, tm1, 0, 12, 12, 2)
    clear_span(img, 8, 14, (0xF,), 8, 90)
    t = 'NOTAS ENTR.'
    draw_text(img, 44 - text_width(t) // 2, 8, t, 0xF)
    put_region(gfx, tm1, 0, 12, img, free)

    # página 3: pastillas moradas "EXP." y "HABILIDAD" (columnas 0-9, filas 13-17)
    img = region(gfx, tm3, 0, 13, 10, 5)
    for top, txt in [(4, 'EXP.'), (28, 'HABILIDAD')]:
        clear_span(img, top - 1, top + 7, (0xE,), 6, 66)
        w = text_width(txt); x0 = 36 - w // 2
        for y in (top - 1, top):  # joroba superior de la pastilla, algo más ancha si hace falta
            for x in range(x0 - 2, x0 + w + 2):
                if img[y][x] in (1, 2):
                    img[y][x] = 0xD
        draw_text(img, x0, top, txt, 0xE)
    put_region(gfx, tm3, 0, 13, img, free)

    out = os.path.join(ROOT, 'data/gfx'); os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'resumen_gfx.bin'), 'wb').write(gfx)
    open(os.path.join(out, 'resumen_tm1.bin'), 'wb').write(tm1)
    open(os.path.join(out, 'resumen_tm3.bin'), 'wb').write(tm3)
    print('piezas libres restantes', len(free))


if __name__ == '__main__':
    main()
