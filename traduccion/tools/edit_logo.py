"""Logo de la pantalla de título (8bpp, 0xEAB8C4 + mapa 0xEAD390): "Ghost Grey Version" -> "Versión Ghost Grey".
Las tres palabras se reordenan con los mismos píxeles de la letra del hack (cada una con su vaivén vertical) y se
añade la tilde de la ó. "Ghost Grey" baja 1 px para apoyarse en la misma línea que "Versión". Las piezas cambiadas van a huecos libres del gráfico.
  python tools/edit_logo.py [vista_previa.png]"""
import os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77

ROOT = os.path.join(os.path.dirname(__file__), '..')
GFX, MAPA, PAL = 0xEAB8C4, 0xEAD390, 0xEAB6C4
Y0, Y1 = 64, 73            # filas del texto (con el rabo de la y)
X0, X1 = 44, 150           # columnas donde está el texto
TINTA = 20                 # color del texto
BAJAR = {0: 1, 1: 1, 2: 0}  # px que baja cada palabra (Ghost, Grey, Version): en el original Version iba 1 px más baja
ACENTO = ['...##', '..##.']  # tilde de 2 px de trazo, como las letras; dos filas por encima de la o


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    g, t = bytearray(lz77(h, GFX)), lz77(h, MAPA)
    m = list(struct.unpack('<%dH' % (len(t) // 2), t))
    assert all(e & 0xFC00 == 0 for e in m)       # sin volteos ni paletas: el índice es la pieza
    img = [[g[m[y // 8 * 32 + x // 8] * 64 + y % 8 * 8 + x % 8] for x in range(256)] for y in range(160)]

    # palabras: columnas con tinta separadas por huecos de más de 2 columnas
    cols = [x for x in range(X0, X1) if any(img[y][x] == TINTA for y in range(Y0, Y1))]
    assert all(img[y][x] in (0, TINTA) for y in range(Y0, Y1) for x in range(X0, X1))
    palabras, ini = [], cols[0]
    for a, b in zip(cols, cols[1:] + [None]):
        if b is None or b - a > 3:
            palabras.append((ini, a + 1))
            ini = b
    assert len(palabras) == 3, palabras                      # Ghost, Grey, Version
    hueco = palabras[1][0] - palabras[0][1]
    bloques = [[img[y][a:b] for y in range(Y0, Y1)] for a, b in palabras]

    # letras de "Version" (columnas con tinta separadas por columnas vacías) para situar la tilde en la o
    ver = bloques[2]
    letras, x = [], 0
    while x < len(ver[0]):
        if any(f[x] == TINTA for f in ver):
            a = x
            while x < len(ver[0]) and any(f[x] == TINTA for f in ver):
                x += 1
            letras.append((a, x))
        x += 1
    assert len(letras) == 7, letras                          # V e r s i o n
    oa, ob = letras[5]
    arriba = min(y for y in range(len(ver)) for xx in range(oa, ob) if ver[y][xx] == TINTA)

    # se reescribe: Versión Ghost Grey, centrado donde estaba
    for y in range(Y0, Y1 + 1):
        for x in range(X0, X1):
            img[y][x] = 0
    total = sum(len(b[0]) for b in bloques) + 2 * hueco
    x = (palabras[0][0] + palabras[2][1] - total) // 2
    for i in (2, 0, 1):
        for dy, fila in enumerate(bloques[i]):
            for dx, v in enumerate(fila):
                if v == TINTA:
                    img[Y0 + dy + BAJAR[i]][x + dx] = TINTA
        if i == 2:
            xo = x + oa + (ob - oa - len(ACENTO[0])) // 2 + 1
            for dy, fila in enumerate(ACENTO):
                for dx, c in enumerate(fila):
                    if c == '#':
                        img[Y0 + arriba - 3 + dy][xo + dx] = TINTA
        x += len(bloques[i][0]) + hueco

    # piezas: las filas de piezas del texto se rehacen; las nuevas van a huecos que no usa el mapa
    usadas = set(m)
    libres = [i for i in range(len(g) // 64) if i not in usadas]
    for r in range(Y0 // 8, (Y1 + 8) // 8):
        for c in range(32):
            pieza = bytes(img[r * 8 + y][c * 8 + x] for y in range(8) for x in range(8))
            if g[m[r * 32 + c] * 64:m[r * 32 + c] * 64 + 64] == pieza:
                continue
            igual = next((i for i in usadas if g[i * 64:i * 64 + 64] == pieza), None)
            if igual is None:
                igual = libres.pop(0)
                g[igual * 64:igual * 64 + 64] = pieza
                usadas.add(igual)
            m[r * 32 + c] = igual
    open(os.path.join(ROOT, 'data/gfx/logo_gfx.bin'), 'wb').write(g)
    open(os.path.join(ROOT, 'data/gfx/logo_tm.bin'), 'wb').write(struct.pack('<%dH' % len(m), *m))
    for y in range(Y0 - 4, Y1 + 1):
        print(''.join('#' if img[y][x] == TINTA else '.' for x in range(X0, X1)))
    if len(sys.argv) > 1:
        from PIL import Image
        pal = [struct.unpack_from('<H', h, PAL + 2 * i)[0] for i in range(208)]
        im = Image.new('RGB', (240, 160))
        for y in range(160):
            for x in range(240):
                c = pal[img[y][x]] if img[y][x] < 208 else 0
                im.putpixel((x, y), ((c & 31) << 3, (c >> 5 & 31) << 3, (c >> 10 & 31) << 3))
        im.resize((720, 480), Image.NEAREST).save(sys.argv[1])


if __name__ == '__main__':
    main()
