"""Ficha de entrenador del hack ("KANTO ID"): gráfico 0x1067740 (puntero 0x89568), mapa 30x20 0x945DC0
(puntero 0x894F4). Partes del RF original: mezcla con el español. Rótulos propios del hack:
"DOB" -> "NAC." y "BADGES" -> "MEDALLAS", con la misma letra.
Salida: data/gfx/ficha_gfx.bin y data/gfx/ficha_tm.bin."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77, mezcla, _px, _tile
from rom import u32, ROM_BASE

ROOT = os.path.join(os.path.dirname(__file__), '..')
P_GFX, P_TM = 0x89568, 0x894F4
P_OTROS_TM = (0x89478, 0x89488, 0x894AC, 0x894BC, 0x894E8, 0x89510, 0x8951C, 0x89530)
W = 30  # ancho del mapa

# letra fina del rótulo "DOB" (7 filas + subrayado)
FINA = {
    'N': ['#...#', '##..#', '#.#.#', '#.#.#', '#..##', '#...#', '#...#'],
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'C': ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'],
    '.': ['.', '.', '.', '.', '.', '.', '#'],
}
# letra gruesa de "BADGES" (5 filas)
GRUESA = {
    'M': ['######', '##.#.#', '##.#.#', '##.#.#', '##.#.#'],
    'E': ['####', '##..', '####', '##..', '####'],
    'D': ['###.', '##.#', '##.#', '##.#', '####'],
    'A': ['####', '##.#', '##.#', '####', '##.#'],
    'L': ['##..', '##..', '##..', '##..', '####'],
    'S': ['####', '##..', '####', '..##', '####'],
}


def tm_get(tm, c, r):
    return tm[2 * (r * W + c)] | tm[2 * (r * W + c) + 1] << 8


def tm_set(tm, c, r, e):
    tm[2 * (r * W + c)] = e & 0xFF; tm[2 * (r * W + c) + 1] = e >> 8


def pieza(gfx, e):
    p = _px(gfx[(e & 0x3FF) * 32:][:32])
    hf, vf = e >> 10 & 1, e >> 11 & 1
    return [[p[(7 - y if vf else y) * 8 + (7 - x if hf else x)] for x in range(8)] for y in range(8)]


def region(gfx, tm, c0, r0, w):
    img = [[0] * (w * 8) for _ in range(8)]
    for c in range(w):
        p = pieza(gfx, tm_get(tm, c0 + c, r0))
        for y in range(8):
            img[y][c * 8:c * 8 + 8] = p[y]
    return img


def poner(gfx, tm, c0, r0, img, libres):
    for c in range((len(img[0])) // 8):
        e = tm_get(tm, c0 + c, r0)
        p = [img[y][c * 8 + x] for y in range(8) for x in range(8)]
        if [v for row in pieza(gfx, e) for v in row] == p:
            continue
        t = libres.pop(0)
        gfx[t * 32:t * 32 + 32] = _tile(p)
        tm_set(tm, c0 + c, r0, (e & 0xF000) | t)


def dibujar(img, x, y, texto, fuente, col):
    for ch in texto:
        g = fuente[ch]
        for dy, fila in enumerate(g):
            for dx, v in enumerate(fila):
                if v == '#':
                    img[y + dy][x + dx] = col
        x += len(g[0]) + 1
    return x


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    us = open(os.path.join(ROOT, '../Pokemon - FireRed Version (USA).gba'), 'rb').read()
    es = open(os.path.join(ROOT, '../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()
    gh = lz77(h, u32(h, P_GFX) - ROM_BASE)
    gfx, _, _ = mezcla(lz77(us, 0xE991F8), lz77(es, 0xE9912C), gh)
    gfx = bytearray(gfx)
    tm = bytearray(lz77(h, u32(h, P_TM) - ROM_BASE))
    usadas = set()
    for p in (P_TM,) + P_OTROS_TM:
        m = lz77(h, u32(h, p) - ROM_BASE)
        usadas |= {(m[2 * k] | m[2 * k + 1] << 8) & 0x3FF for k in range(len(m) // 2)}
    libres = [t for t in range(len(gfx) // 32) if t not in usadas and t > 0]

    # "DOB" (columnas 2-3, fila 7) -> "NAC." en columnas 2-4
    img = region(gh, tm, 2, 7, 3)  # rótulos propios del hack: se parte del gráfico sin mezclar
    for y in range(8):
        for x in range(24):
            img[y][x] = 1
    fin = dibujar(img, 0, 0, 'NAC.', FINA, 0xF)
    for x in range(fin - 1):
        img[7][x] = 0xF  # subrayado
    poner(gfx, tm, 2, 7, img, libres)

    # "BADGES" (fila 15, desde x = 8 + 11) -> "MEDALLAS"
    img = region(gh, tm, 1, 15, 7)
    for y in range(2, 7):
        for x in range(11, 56):
            if img[y][x] == 0xE:
                img[y][x] = 0xF
    dibujar(img, 11, 2, 'MEDALLAS', GRUESA, 0xE)
    poner(gfx, tm, 1, 15, img, libres)

    os.makedirs(os.path.join(ROOT, 'data/gfx'), exist_ok=True)
    open(os.path.join(ROOT, 'data/gfx/ficha_gfx.bin'), 'wb').write(gfx)
    open(os.path.join(ROOT, 'data/gfx/ficha_tm.bin'), 'wb').write(tm)
    print('piezas libres restantes', len(libres))


if __name__ == '__main__':
    main()
