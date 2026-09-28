"""Iconos de tipo y etiquetas de la pantalla de movimientos (gráfico sin comprimir de 128x128).
Hack: tabla de iconos 0x96197C (ancho, alto, pieza) y gráfico 0x961C00. Se toma el icono español
equivalente y se le ponen los colores del hack. Casos especiales:
- LUCHA: el hack usa letra sin sombra -> la sombra española pasa al color de fondo.
- TIPO/POTENCIA/PRECISIÓN/PP: el hack las cambió de sitio (ha metido HADA en 0xA8).
- HADA: no existe en RF; se compone con letras de HIELO, AGUA y DRAGÓN.
Salida: data/gfx/tipos_gfx.bin (se escribe tal cual en 0x961C00)."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import _px, _tile

ROOT = os.path.join(os.path.dirname(__file__), '..')
H_TABLA, H_GFX = 0x96197C, 0x961C00
US_TABLA, US_GFX = 0x452C94, 0xE95DDC
ES_GFX = 0xE95D10
TAM = 0x2000


def icono(d, off, w, h=12):
    img = [[0] * w for _ in range(h)]
    for ty in range((h + 7) // 8):
        for tx in range(w // 8):
            p = _px(d[(off + ty * 16 + tx) * 32:][:32])
            for y in range(min(8, h - ty * 8)):
                for x in range(8):
                    img[ty * 8 + y][tx * 8 + x] = p[y * 8 + x]
    return img


def poner(d, off, img):
    h, w = len(img), len(img[0])
    for ty in range((h + 7) // 8):
        for tx in range(w // 8):
            t = off + ty * 16 + tx
            p = _px(d[t * 32:t * 32 + 32])
            for y in range(min(8, h - ty * 8)):
                for x in range(8):
                    p[y * 8 + x] = img[ty * 8 + y][tx * 8 + x]
            d[t * 32:t * 32 + 32] = _tile(p)


def mapa(a, b):
    """Mapa de colores píxel a píxel de a -> b; None si no es coherente."""
    m = {}
    for ra, rb in zip(a, b):
        for x, y in zip(ra, rb):
            if m.setdefault(x, y) != y:
                return None
    return m


def main():
    us = open(os.path.join(ROOT, '../Pokemon - FireRed Version (USA).gba'), 'rb').read()
    es = open(os.path.join(ROOT, '../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()
    hk = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    du, de = us[US_GFX:US_GFX + TAM], es[ES_GFX:ES_GFX + TAM]
    out = bytearray(hk[H_GFX:H_GFX + TAM])
    tabla = [tuple(hk[H_TABLA + 4 * i:H_TABLA + 4 * i + 3]) for i in range(25)]
    us_offs = {us[US_TABLA + 4 * i + 2] for i in range(24)}
    especiales = {0x64, 0xA8, 0xC0, 0xC8, 0xE0, 0xE8, 0xF0}
    for i, (w, h, off) in enumerate(tabla[1:], 1):
        if off in especiales or off not in us_offs:
            continue
        m = mapa(icono(du, off, w), icono(out, off, w))
        ie = icono(de, off, w)
        assert m and all(v in m for r in ie for v in r), 'icono %X' % off
        poner(out, off, [[m[v] for v in r] for r in ie])

    # LUCHA: fondo y letra del hack, sin sombra
    ih = icono(out, 0x64, 32)
    fondo = ih[1][1]
    poner(out, 0x64, [[{0: 0, 0xF: 0xF}.get(v, fondo) for v in r] for r in icono(de, 0x64, 32)])

    # etiquetas: hack C0=TIPO, C8=POTENCIA, E0=PRECISIÓN (en RF español están en A8, C0 y C8); PP igual
    for dst, src in ((0xC0, 0xA8), (0xC8, 0xC0), (0xE0, 0xC8)):
        ih = icono(out, dst, 40)
        cuenta = {}
        for r in ih:
            for v in r:
                if v not in (0, 0xF):
                    cuenta[v] = cuenta.get(v, 0) + 1
        pastilla = max(cuenta, key=cuenta.get)
        poner(out, dst, [[{0: 0, 0xF: 0xF}.get(v, pastilla) for v in r] for r in icono(de, src, 40)])

    # HADA con letras españolas (celdas de 5 columnas: 4 de letra + sombra)
    def letra(off, col):
        return [r[col:col + 5] for r in icono(de, off, 32)]
    H, A, D = letra(0x4C, 4), letra(0x28, 6), letra(0xA0, 1)
    ih = icono(out, 0xA8, 32)
    fondo, sombra = ih[1][1], 8
    nuevo = [r[:] for r in ih]
    for y in range(2, 10):
        for x in range(1, 31):
            nuevo[y][x] = fondo
    x0 = (32 - 20) // 2
    for k, L in enumerate((H, A, D, A)):
        for y in range(2, 10):
            for x in range(5):
                v = L[y][x]
                if v in (0xE, 0xF):
                    nuevo[y][x0 + 5 * k + x] = 0xF if v == 0xF else sombra
    poner(out, 0xA8, nuevo)

    os.makedirs(os.path.join(ROOT, 'data/gfx'), exist_ok=True)
    open(os.path.join(ROOT, 'data/gfx/tipos_gfx.bin'), 'wb').write(out)
    print('ok')


if __name__ == '__main__':
    main()
