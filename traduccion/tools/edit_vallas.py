"""Vallas publicitarias de Ciudad Plateada (tileset secundario 0x2D4ADC, gráfico LZ en su puntero +4):
"PLAY" -> "JUEGA" y "DRINK" -> "BEBE", con letras de palo como las originales (relleno 1, fondo 4).
Salida: data/gfx/vallas_gfx.bin."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77
from hoja import to_sheet, from_sheet
from rom import u32, ROM_BASE

ROOT = os.path.join(os.path.dirname(__file__), '..')
TILESET = 0x2D4ADC

ALTA = {  # 5x10 (con 6 de ancho la palabra llegaba al borde de la valla)
    'J': ['...##'] * 7 + ['##.##', '##.##', '.###.'],
    'U': ['##.##'] * 9 + ['.###.'],
    'E': ['#####', '#####', '##...', '##...', '####.', '####.', '##...', '##...', '#####', '#####'],
    'G': ['.####', '#####', '##...', '##...', '##.##', '##.##', '##.##', '##.##', '#####', '.###.'],
    'A': ['.###.', '#####', '##.##', '##.##', '##.##', '#####', '#####', '##.##', '##.##', '##.##'],
}
BAJA = {  # 6x7
    'B': ['#####.', '##..##', '##..##', '#####.', '##..##', '##..##', '#####.'],
    'E': ['######', '##....', '##....', '#####.', '##....', '##....', '######'],
}


def escribir(img, x0, x1, y0, y1, texto, fuente, borrar_hasta=None):
    for y in range(y0, y1 + 1):
        for x in range(x0, (borrar_hasta or x1) + 1):
            img[y][x] = 4
    ancho = sum(len(fuente[c][0]) for c in texto) + len(texto) - 1
    x = x0 + (x1 - x0 + 1 - ancho) // 2
    for c in texto:
        for dy, fila in enumerate(fuente[c]):
            for dx, v in enumerate(fila):
                if v == '#':
                    img[y0 + dy][x + dx] = 1
        x += len(fuente[c][0]) + 1


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    g = lz77(h, u32(h, TILESET + 4) - ROM_BASE)
    img = to_sheet(g)
    escribir(img, 28, 60, 74, 83, 'JUEGA', ALTA, borrar_hasta=63)
    escribir(img, 86, 122, 75, 81, 'BEBE', BAJA)
    os.makedirs(os.path.join(ROOT, 'data/gfx'), exist_ok=True)
    open(os.path.join(ROOT, 'data/gfx/vallas_gfx.bin'), 'wb').write(from_sheet(img, g))
    print('ok', '%X' % (u32(h, TILESET + 4) - ROM_BASE))


if __name__ == '__main__':
    main()
