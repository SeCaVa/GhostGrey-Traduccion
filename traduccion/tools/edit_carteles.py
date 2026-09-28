"""Carteles y textos dibujados propios del hack (revisión de gráficos del 2026-09-27).
Criterio: lo que viene del Rojo de Game Boy se deja como en el Rojo español de GB ("POKé", "SHOP", "GIM");
lo que es del hack se traduce; las marcas (BrunoCorp "BC", chucherías...) no se tocan.
Cada edición deja data/gfx/<nombre>.bin y se registra en data/gfx_bin.json (build.py lo recomprime y reapunta)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77, _px, _tile

ROOT = os.path.join(os.path.dirname(__file__), '..')
GB = os.path.join(ROOT, '../Pokemon - Edicion Roja (Spain) (SGB Enhanced).gb')


PARCHES = []  # parches de datos (data/parches_datos.json, los aplica build.py)


def registrar(nombre, orig, nota):
    p = os.path.join(ROOT, 'data/gfx_bin.json')
    lista = json.load(open(p, encoding='utf8'))
    f = 'data/gfx/%s.bin' % nombre
    lista = [r for r in lista if r['file'] != f]
    lista.append({'file': f, 'orig': '%X' % orig, 'nota': nota})
    json.dump(lista, open(p, 'w'), indent=1)  # ASCII: build.py lo lee sin codificación


def guardar(nombre, orig, datos, nota):
    os.makedirs(os.path.join(ROOT, 'data/gfx'), exist_ok=True)
    open(os.path.join(ROOT, 'data/gfx/%s.bin' % nombre), 'wb').write(datos)
    registrar(nombre, orig, nota)
    print(nombre, '%X' % orig, len(datos) // 32, 'piezas')


def pieza_gb(gb, t, tonos):
    """Pieza 2bpp del tileset exterior del Rojo español (0x64000) con los tonos GB pasados a índices 4bpp."""
    px = []
    for y in range(8):
        lo, hi = gb[0x64000 + t * 16 + y * 2], gb[0x64000 + t * 16 + y * 2 + 1]
        px += [tonos[(lo >> (7 - x)) & 1 | ((hi >> (7 - x)) & 1) << 1] for x in range(8)]
    return _tile(px)


def collage_gb(h):
    """Fondo de combate 7 (0x24EEAC): collage de piezas del Rojo de GB. "GYM" -> "GIM", "MART" -> "SHOP"
    (piezas del Rojo español de GB)."""
    a = 0xFFAD80
    d = bytearray(lz77(h, a))
    gb = open(GB, 'rb').read()
    tonos = {0: 3, 1: 0, 2: 2, 3: 1}
    for dst, src in ((162, 47), (163, 63), (58, 68), (59, 69)):
        d[dst * 32:dst * 32 + 32] = pieza_gb(gb, src, tonos)
    guardar('gb_collage', a, bytes(d), 'fondo de combate collage GB: GIM, SHOP (tools/edit_carteles.py)')


# letra de 3x5 de la carta del hack (sacada del propio dibujo; B F Q Z Ñ añadidas en el mismo estilo)
MINI = {
    'A': ['.#.', '#.#', '###', '#.#', '#.#'], 'B': ['##.', '#.#', '##.', '#.#', '##.'],
    'C': ['.##', '#..', '#..', '#..', '.##'], 'D': ['##.', '#.#', '#.#', '#.#', '##.'],
    'E': ['###', '#..', '###', '#..', '###'], 'F': ['###', '#..', '##.', '#..', '#..'],
    'G': ['.##', '#..', '#.#', '#.#', '.##'], 'H': ['#.#', '#.#', '###', '#.#', '#.#'],
    'I': ['###', '.#.', '.#.', '.#.', '###'], 'J': ['..#', '..#', '..#', '#.#', '###'],
    'K': ['#.#', '#.#', '##.', '#.#', '#.#'], 'L': ['#..', '#..', '#..', '#..', '###'],
    'M': ['#...#', '##.##', '#.#.#', '#...#', '#...#'], 'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'Ñ': ['####', '....', '##.#', '#.##', '#..#'],
    'O': ['.##', '#.#', '#.#', '#.#', '##.'], 'P': ['##.', '#.#', '###', '#..', '#..'],
    'Q': ['.##', '#.#', '#.#', '##.', '.##'], 'R': ['##.', '#.#', '##.', '#.#', '#.#'],
    'S': ['.##', '#..', '###', '..#', '##.'], 'T': ['###', '.#.', '.#.', '.#.', '.#.'],
    'U': ['#.#', '#.#', '#.#', '#.#', '##.'], 'V': ['#.#', '#.#', '#.#', '#.#', '.#.'],
    'W': ['#...#', '#...#', '#.#.#', '##.##', '#...#'], 'X': ['#.#', '#.#', '.#.', '#.#', '#.#'],
    'Y': ['#.#', '#.#', '.#.', '.#.', '.#.'], 'Z': ['###', '..#', '.#.', '#..', '###'],
    '.': ['.', '.', '.', '.', '#'], ',': ['.', '.', '.', '.', '#', '#'], ':': ['.', '#', '.', '#', '.'],
    '^': ['.#.', '#.#', '...', '...', '...'], ')': ['#.', '.#', '.#', '.#', '#.'],
}


def ancho_mini(txt):
    return sum(len(MINI[c][0]) + 1 if c != ' ' else 1 for c in txt) - 1


def escribir_mini(img, x, y, txt, col):
    for c in txt:
        if c == ' ':
            x += 1
            continue
        for dy, fila in enumerate(MINI[c]):
            for dx, v in enumerate(fila):
                if v == '#':
                    img[y + dy][x + dx] = col
        x += len(MINI[c][0]) + 1


def carta_nota(h):
    """Carta 14 (tabla de cartas 0x3D2AAC, 20x18 piezas): nota del hack con letra de 3x5.
    "I DON'T HAVE MUCH TIME TO EXPLAIN. THEY'VE GOT EYES EVERYWHERE, ESPECIALKJKK,,,M / N / NICE TRY PAL :^)"."""
    from edit_preview import pantalla, rehacer
    ga, ta = 0x3D1FD4, 0xB766C0
    g, tm = lz77(h, ga), lz77(h, ta)
    img = pantalla(g, tm, 20)
    for y in range(28, 140):  # se borra la letra (color 3) dentro del marco
        for x in range(4, 154):
            if img[y][x] == 3:
                img[y][x] = 2
    lineas = [(6, 30, 'NO TENGO TIEMPO PARA EXPLICARLO. NOS'), (6, 39, 'VIGILAN EN TODAS PARTES, SOBRE TOKJKK,,,M'),
              (27, 48, 'N'), (6, 99, 'BUEN INTENTO, COLEGA :^)')]
    for x, y, txt in lineas:
        assert x + ancho_mini(txt) <= 152, txt
        escribir_mini(img, x, y, txt, 3)
    ng, nt = rehacer(img, tm, 20)
    assert len(ng) // 32 <= 80, 'demasiadas piezas: %d' % (len(ng) // 32)
    guardar('carta_nota_gfx', ga, ng, 'carta de la nota (tools/edit_carteles.py)')
    guardar('carta_nota_tm', ta, nt, 'mapa de la carta de la nota')


def borrar_color(img, zona, col):
    """Quita los píxeles `col` de la zona (x0, y0, x1, y1) rellenándolos con el color vecino más común."""
    from collections import Counter
    x0, y0, x1, y1 = zona
    quitar = {(x, y) for y in range(y0, y1) for x in range(x0, x1) if img[y][x] == col}
    while quitar:
        nuevos = {}
        for x, y in quitar:
            c = Counter(img[y + dy][x + dx] for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                        if (x + dx, y + dy) not in quitar and 0 <= y + dy < len(img) and 0 <= x + dx < len(img[0]))
            if c:
                nuevos[(x, y)] = c.most_common(1)[0][0]
        if not nuevos:
            break
        for (x, y), v in nuevos.items():
            img[y][x] = v
            quitar.discard((x, y))


def texto_ink(txt, tam, estirar=1.0, grosor=0):
    """Máscara (lista de filas de 0/1) del texto en Ink Free sin suavizado."""
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype('C:/Windows/Fonts/Inkfree.ttf', tam)
    t = Image.new('1', (600, 120)); d = ImageDraw.Draw(t); d.fontmode = '1'
    d.text((4, 4), txt, font=f, fill=1, stroke_width=grosor, stroke_fill=1)
    t = t.crop(t.getbbox())
    if estirar != 1.0:
        t = t.resize((t.width, round(t.height * estirar)), Image.NEAREST)
    return [[t.getpixel((x, y)) for x in range(t.width)] for y in range(t.height)]


def pegar(img, m, x0, y0, col):
    for y, fila in enumerate(m):
        for x, v in enumerate(fila):
            if v:
                img[y0 + y][x0 + x] = col


# letras a mano de la carta de Halloween: E, L y ¡ salen de "HALLOWEEN!"; F, I y Z hechas con los mismos trazos
MANO = {
    '¡': ['.##.', '####', '.##.', '....', '.##.', '.###', '.###', '.###', '.###', '.###', '.###', '####',
          '####', '####', '####', '##..'],
    'F': ['..#......', '..#######', '..#######', '..######.', '..##.....', '..#......', '.##......',
          '.########', '.#######.', '.#.......', '.#.......', '##.......', '##.......', '##.......',
          '##.......', '#........'],
    'E': ['..######', '..#####.', '..##....', '.##.....', '.##.....', '.####...', '########', '########',
          '##......', '##......', '###.....', '###.....', '#######.', '.#######'],
    'L': ['..#......', '..#......', '.##......', '.##......', '###......', '###......', '###......',
          '###......', '###......', '###......', '###......', '###......', '###......', '###......',
          '#########', '.########'],
    'I': ['..#', '.##', '.##', '###', '###', '###', '###', '###', '###', '###', '###', '###', '###',
          '###', '###', '.##'],
    'Z': ['#########', '#########', '......###', '.....###.', '.....###.', '....###..', '...###...',
          '...###...', '..###....', '..###....', '.###.....', '###......', '###......', '#########',
          '#########'],
}


def escribir_mano(img, x, base, txt, col):
    """Escribe con MANO apoyando las letras en la línea `base` (fila de abajo)."""
    for c in txt:
        g = MANO[c]
        for dy, fila in enumerate(g):
            for dx, v in enumerate(fila):
                if v == '#':
                    img[base - len(g) + 1 + dy][x + dx] = col
        x += len(g[0]) + 2
    return x


def carta_halloween(h):
    """Carta 3 (0x3D2A1C): "HAPPY HALLOWEEN!" -> "¡FELIZ HALLOWEEN!" (Halloween se queda como en España)."""
    from edit_preview import pantalla, rehacer
    ga, ta = 0xB19380, 0xB19AC0
    g, tm = lz77(h, ga), lz77(h, ta)
    img = pantalla(g, tm, 20)
    borrar_color(img, (38, 32, 104, 51), 4)
    ancho = sum(len(MANO[c][0]) + 2 for c in '¡FELIZ') - 2
    escribir_mano(img, 72 - ancho // 2, 49, '¡FELIZ', 4)
    ng, nt = rehacer(img, tm, 20)
    print('  piezas halloween', len(ng) // 32, 'antes', len(g) // 32)
    guardar('carta_halloween_gfx', ga, ng, 'carta de Halloween (tools/edit_carteles.py)')
    guardar('carta_halloween_tm', ta, nt, 'mapa de la carta de Halloween')


def mascara_encima(img, patron, filas, r=3):
    """Lo que tapa el patrón repetido (calaveras, óvalos...): los píxeles que no coinciden con el patrón se
    agrupan en manchas (uniendo lo que está a menos de r px) y cada mancha se rellena fila a fila de su borde
    izquierdo al derecho, porque lo que tapa es opaco (los ojos de la calavera no dejan ver el texto)."""
    W = len(img[0]); ph, pw = len(patron), len(patron[0])
    m = {(x, y) for y in filas for x in range(W) if img[y][x] != patron[y % ph][x % pw]}
    vec = [(dx, dy) for dy in range(-r, r + 1) for dx in range(-r, r + 1)]
    tapa, vistos = set(), set()
    for p0 in m:
        if p0 in vistos:
            continue
        mancha, pila = [], [p0]
        vistos.add(p0)
        while pila:
            x, y = pila.pop()
            mancha.append((x, y))
            for dx, dy in vec:
                q = (x + dx, y + dy)
                if q in m and q not in vistos:
                    vistos.add(q); pila.append(q)
        if len(mancha) < 12:  # motas sueltas: solo esos píxeles
            tapa.update(mancha)
            continue
        filas_m = {}
        for x, y in mancha:
            a, b = filas_m.get(y, (x, x))
            filas_m[y] = (min(a, x), max(b, x))
        for y, (a, b) in filas_m.items():
            tapa.update((x, y) for x in range(a, b + 1))
    return tapa


def fondo_gotico(h, ga, ta, nombre, franja, fondo, texto):
    """Fondos con "DIE in BATTLE" repetido (letra gótica) -> "MUERE en BATALLA", respetando lo que hay encima."""
    from edit_preview import pantalla, rehacer
    from gotica import dibujar, ancho
    g, tm = lz77(h, ga), lz77(h, ta)
    img = pantalla(g, tm, 32)
    # patrón inglés limpio: franja de 32 px de 0x85ED80 (texto 1 sobre 15), con los colores de este fondo
    ref = pantalla(lz77(h, 0x85ED80), lz77(h, 0x850D00), 32)
    viejo = [[texto if ref[y][x] == 1 else fondo for x in range(256)] for y in range(32)]
    nuevo = [[fondo] * 256 for _ in range(32)]
    t = 'MUERE en BATALLA'
    dibujar(nuevo, (256 - ancho(t, 3, 10)) // 2, 5, t, texto, 3, 10)
    for b0 in range(min(franja), max(franja) + 1, 32):  # cada franja de 32 px puede ir desplazada
        filas = range(b0, b0 + 32)
        dx, dy = max(((a, b) for a in range(128) for b in range(-3, 4)),
                     key=lambda d: sum(img[y][x] == viejo[(y + d[1]) % 32][(x + d[0]) % 256]
                                       for y in filas for x in range(0, 256, 2)))
        ver = [[viejo[(y + dy) % 32][(x + dx) % 256] for x in range(256)] for y in range(32)]
        tapa = mascara_encima(img, ver, filas)
        for y in filas:
            for x in range(256):
                if (x, y) not in tapa:
                    img[y][x] = nuevo[(y + dy) % 32][(x + dx) % 256]
    ng, nt = rehacer(img, tm, 32)
    print('  piezas %s %d antes %d' % (nombre, len(ng) // 32, len(g) // 32))
    guardar(nombre + '_gfx', ga, ng, 'fondo "MUERE en BATALLA" (tools/edit_carteles.py)')
    guardar(nombre + '_tm', ta, nt, 'mapa del fondo ' + nombre)


# letra pixelada del fondo 0xBC8300 (celdas de 8 px); M, U y R hechas en el mismo estilo
PIXEL = {
    'D': ['#####...', '#....#..', '#.....#.', '#.....#.', '#.....#.', '#....#..', '#####...'],
    'I': ['.#####..', '...#....', '...#....', '...#....', '...#....', '...#....', '.#####..'],
    'E': ['#######.', '#.......', '#.......', '######..', '#.......', '#.......', '#######.'],
    'N': ['#.....#.', '##....#.', '#.#...#.', '#..#..#.', '#...#.#.', '#....##.', '#.....#.'],
    'B': ['#####...', '#....#..', '#....#..', '######..', '#.....#.', '#.....#.', '######..'],
    'A': ['...#....', '..#.#...', '..#.#...', '.#...#..', '.#####..', '#.....#.', '#.....#.'],
    'T': ['#######.', '...#....', '...#....', '...#....', '...#....', '...#....', '...#....'],
    'L': ['#.......', '#.......', '#.......', '#.......', '#.......', '#.......', '#######.'],
    'M': ['#.....#.', '##...##.', '#.#.#.#.', '#..#..#.', '#.....#.', '#.....#.', '#.....#.'],
    'U': ['#.....#.', '#.....#.', '#.....#.', '#.....#.', '#.....#.', '.#...#..', '..###...'],
    'R': ['#####...', '#....#..', '#....#..', '#####...', '#..#....', '#...#...', '#....#..'],
    ' ': ['........'] * 7,
}


def banda_pixel(txt, texto, fondo):
    """Franja de 8 px de alto con `txt` en la letra PIXEL (ancho = 8 * len(txt))."""
    fila = [[fondo] * (8 * len(txt)) for _ in range(8)]
    for i, c in enumerate(txt):
        for y, f in enumerate(PIXEL[c]):
            for x, v in enumerate(f):
                if v == '#':
                    fila[y][i * 8 + x] = texto
    return fila


def fondo_pixel(h):
    """Fondo de combate 0x24EF88: "DIE IN BATTLE" en letra pixelada amarilla -> "MUERE EN BATALLA"."""
    from edit_preview import pantalla, rehacer
    ga, ta = 0xBC8300, 0xBC7F80
    g, tm = lz77(h, ga), lz77(h, ta)
    img = pantalla(g, tm, 32)
    viejo = banda_pixel('DIE IN BATTLE ', 7, 1)
    nuevo = banda_pixel('MUERE EN BATALLA ', 7, 1)
    pv, pn = len(viejo[0]), len(nuevo[0])
    esperado = [fila[:] for fila in img]  # lo que habría si solo estuviera el texto repetido
    desfases = {}
    for b0 in range(0, len(img), 8):
        filas = range(b0, b0 + 8)
        # solo cuentan los píxeles de letra (el fondo negro coincide en cualquier franja oscura)
        ok, dx = max((sum(img[y][x] == 7 for y in filas for x in range(256) if viejo[y - b0][(x + d) % pv] == 7), d)
                     for d in range(pv))
        letra = sum(v == '#' for c in 'DIE IN BATTLE ' for f in PIXEL[c] for v in f) * 256 // pv
        if ok < 0.3 * letra:
            continue
        desfases[b0] = dx
        for y in filas:
            esperado[y] = [viejo[y - b0][(x + dx) % pv] for x in range(256)]
    filas = [y for b0 in desfases for y in range(b0, b0 + 8)]
    tapa = mascara_encima(img, esperado, filas)
    for b0, dx in desfases.items():
        dn = dx * pn // pv
        for y in range(b0, b0 + 8):
            for x in range(256):
                if (x, y) not in tapa:
                    img[y][x] = nuevo[y - b0][(x + dn) % pn]
    cambiadas = len(desfases)
    ng, nt = rehacer(img, tm, 32)
    print('  franjas', cambiadas, 'piezas', len(ng) // 32, 'antes', len(g) // 32)
    guardar('muere3_gfx', ga, ng, 'fondo pixelado "MUERE EN BATALLA" (tools/edit_carteles.py)')
    guardar('muere3_tm', ta, nt, 'mapa del fondo pixelado')


# letra del fondo "There are Worse Things..." (0x862940); filas 0-14 de cada línea, base en la fila 11.
# a e o r s . salen del original; H y c p hechas en el mismo estilo
PEORES = {
    'H': ['.......', '##...##', '##...##', '##...##', '##...##', '##...##', '#######', '#######', '##...##',
          '##...##', '##...##', '##...##'],
    'a': ['........'] * 5 + ['..####..', '.##..##.', '##....##', '##....##', '##....##', '.##..###', '..####.#'],
    'y': ['......'] * 5 + ['##..##', '##..##', '##..##', '##..##', '.#####', '..####', '....##', '#...##',
                           '#####.', '.###..'],
    'c': ['......'] * 5 + ['..###.', '.#####', '##...#', '##....', '##....', '##...#', '.#####'],
    'o': ['......'] * 5 + ['.####.', '######', '##..##', '#....#', '#....#', '##..##', '.####.'],
    's': ['......'] * 5 + ['.####.', '######', '##...#', '####..', '..####', '#...##', '#####.'],
    'p': ['......'] * 5 + ['#####.', '######', '##..##', '##..##', '##..##', '######', '#####.', '##....',
                           '##....', '##....'],
    'e': ['......'] * 5 + ['..###.', '.#####', '##...#', '######', '##....', '##...#', '.#####'],
    'r': ['......'] * 5 + ['#####.', '.#####', '.##..#', '.##...', '.##...', '.##...', '.##...'],
    '.': ['..'] * 10 + ['##', '##'],
}


def tira_peores(txt, col, fondo, hueco=1, espacio=5):
    """Tira de 15 filas con `txt` en la letra PEORES; devuelve (filas, ancho)."""
    ancho = sum(espacio if c == ' ' else len(PEORES[c][0]) + hueco for c in txt)
    t = [[fondo] * ancho for _ in range(15)]
    x = 0
    for c in txt:
        if c == ' ':
            x += espacio
            continue
        for y, f in enumerate(PEORES[c]):
            for dx, v in enumerate(f):
                if v == '#':
                    t[y][x + dx] = col
        x += len(PEORES[c][0]) + hueco
    return t, ancho


def fondo_peores(h):
    """Fondo 0x862940 (llamado desde 0xED20C): líneas de "There are Worse Things..." -> "Hay cosas peores...".
    Cada línea empieza la frase donde empezaba "There"."""
    from edit_preview import pantalla, rehacer
    ga, ta = 0x862940, 0x863500
    g, tm = lz77(h, ga), lz77(h, ta)
    img = pantalla(g, tm, 32)
    tira, P = tira_peores('Hay cosas peores...', 1, 6)
    ink = lambda y, x: img[y][x % 256] == 1

    def there(y0):  # x donde empieza "There": barra de la T seguida de h, sin el punto de la i de "Things"
        return next((x for x in range(256) if all(ink(y0 + 1, x + k) for k in range(6)) and ink(y0 + 3, x + 2)
                     and not ink(y0 + 3, x) and ink(y0 + 1, x + 7) and not ink(y0 + 3, x + 15)
                     and not ink(y0 + 3, x + 16)), None)
    lineas, y0 = [], 240
    while y0 < len(img) - 15:
        x0 = there(y0)
        if x0 is None:
            y0 += 1
            continue
        lineas.append((y0, x0))
        y0 += 13
    print('  líneas', lineas)
    for y0, x0 in lineas:
        for y in range(y0, y0 + 15):
            for x in range(256):
                if img[y][x] in (1, 3):  # 3: relleno de una g del original
                    img[y][x] = 6
                v = tira[y - y0][(x - x0) % P]
                if v == 1:
                    img[y][x] = 1
    ng, nt = rehacer(img, tm, 32)
    print('  piezas peores', len(ng) // 32, 'antes', len(g) // 32)
    guardar('peores_gfx', ga, ng, 'fondo "Hay cosas peores..." (tools/edit_carteles.py)')
    guardar('peores_tm', ta, nt, 'mapa del fondo "Hay cosas peores..."')


# letra a mano estrecha (trazo de 1 px, 9 de alto) para los carteles pintados del hack
GARABATO = {
    'T': ['#####', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..', '..#..', '.#...'],
    'E': ['.###', '#...', '#...', '###.', '#...', '#...', '#...', '#...', '.###'],
    'M': ['#...#', '##.##', '#.#.#', '#.#.#', '#...#', '#...#', '#...#', '#...#', '#...#'],
    'L': ['#...', '#...', '#...', '#...', '#...', '#...', '#...', '#...', '.###'],
    'A': ['..#..', '.#.#.', '.#.#.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'G': ['.###', '#...', '#...', '#...', '#.##', '#..#', '#..#', '#..#', '.##.'],
    'R': ['###.', '#..#', '#..#', '###.', '#.#.', '#..#', '#..#', '#..#', '#..#'],
    'U': ['#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
}
SALTOS = [0, 1, 0, -1, 1, 0, 1, -1, 0, 1]  # vaivén vertical de cada letra, para que parezca pintado a mano


def ancho_garabato(txt):
    return sum(3 if c == ' ' else len(GARABATO[c][0]) + 1 for c in txt) - 1


def escribir_garabato(img, x, y, txt, col):
    for i, c in enumerate(txt):
        if c == ' ':
            x += 3
            continue
        for dy, fila in enumerate(GARABATO[c]):
            for dx, v in enumerate(fila):
                if v == '#':
                    img[y + dy + SALTOS[i % len(SALTOS)]][x + dx] = col
        x += len(GARABATO[c][0]) + 1


def limpiar(img, zona, col, fondo):
    x0, y0, x1, y1 = zona
    for y in range(y0, y1):
        for x in range(x0, x1):
            if img[y][x] == col:
                img[y][x] = fondo


def tileset_gruta(h):
    """Tileset 0x8ECE40: carteles pintados "YOU WILL / BE EATEN" -> "SERÁS / DEVORADO" y
    "BEWARE / THE GROTTO" -> "TEME / LA GRUTA" (rojo, color 4, sobre blanco)."""
    from hoja import to_sheet, from_sheet
    a = 0x8ECE40
    g = lz77(h, a)
    img = to_sheet(g)
    limpiar(img, (80, 72, 113, 88), 4, 0)
    for y, txt in ((73, 'SERAS'), (81, 'DEVORADO')):
        x = 80 + (33 - ancho_mini(txt)) // 2
        escribir_mini(img, x, y, txt, 4)
        if txt == 'SERAS':  # tilde de la Á (cuarta letra)
            img[y - 1][x + ancho_mini('SER') + 2] = 4
    limpiar(img, (64, 136, 113, 167), 4, 0)
    for y, txt in ((139, 'TEME'), (154, 'LA GRUTA')):
        escribir_garabato(img, 64 + (49 - ancho_garabato(txt)) // 2, y, txt, 4)
    guardar('tileset_gruta', a, from_sheet(img, g), 'carteles SERÁS DEVORADO / TEME LA GRUTA (tools/edit_carteles.py)')


# letra de bloque 3x5 de los carteles de Ciudad Azafrán (N de 4 de ancho, como en el original)
BLOQUE = {
    'A': ['###', '#.#', '###', '#.#', '#.#'], 'C': ['###', '#..', '#..', '#..', '###'],
    'D': ['##.', '#.#', '#.#', '#.#', '##.'], 'E': ['###', '#..', '##.', '#..', '###'],
    'F': ['###', '#..', '##.', '#..', '#..'], 'I': ['#', '#', '#', '#', '#'],
    'L': ['#..', '#..', '#..', '#..', '###'], 'N': ['#..#', '##.#', '#.##', '#..#', '#..#'],
    'O': ['###', '#.#', '#.#', '#.#', '###'], 'P': ['###', '#.#', '###', '#..', '#..'],
    'R': ['###', '#.#', '##.', '#.#', '#.#'], 'S': ['###', '#..', '###', '..#', '###'],
    'T': ['###', '.#.', '.#.', '.#.', '.#.'], 'Z': ['###', '..#', '.#.', '#..', '###'],
}


def escribir_bloque(img, x0, x1, y, txt, col):
    ancho = sum(len(BLOQUE[c][0]) + 1 for c in txt) - 1
    x = x0 + (x1 - x0 - ancho + 1) // 2
    for c in txt:
        for dy, f in enumerate(BLOQUE[c]):
            for dx, v in enumerate(f):
                if v == '#':
                    img[y + dy][x + dx] = col
        x += len(BLOQUE[c][0]) + 1


# letra del póster "POLICE / BRUNOCORP" (sacada del póster; A hecha igual)
POSTER = {
    'P': ['####.', '##..#', '##..#', '####.', '##...', '##...', '##...'],
    'O': ['.##.', '#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'L': ['##..', '##..', '##..', '##..', '##..', '##..', '####'],
    'I': ['##', '##', '##', '##', '##', '##', '##'],
    'C': ['.##.', '##.#', '##..', '##..', '##..', '##.#', '.##.'],
    'A': ['.##.', '##.#', '##.#', '####', '##.#', '##.#', '##.#'],
}


def poster_policia(img):
    """"POLICE" (filas 1-7, x 80-127; la fila 4 es una raya de color 2) -> "POLICIA". BRUNOCORP es marca."""
    for y in range(1, 8):
        for x in range(80, 128):
            if img[y][x] == 4:
                img[y][x] = 2 if y == 4 else 1
    x = 80
    for c in 'POLICIA':
        for dy, f in enumerate(POSTER[c]):
            for dx, v in enumerate(f):
                if v == '#':
                    img[1 + dy][x + dx] = 4
        x += len(POSTER[c][0]) + 1


def azafran(h):
    """Ciudad Azafrán del hack (mapa 3.10, tileset secundario 0xC53300): carteles "SAFFRON POLICE" y
    "SAFFRON STADIUM" -> "POLICÍA ▪ AZAFRÁN" / "ESTADIO ▪ AZAFRÁN". Las letras ocupan los 5 px del cartel, así
    que la tilde (2 px en diagonal) va encima, sobre la raya roja y la gris.
    La pieza SAFFRON (metatiles 37E-37F) es común y va delante, así que en el mapa se cambia el orden
    de los bloques. SNACK SNEASEL y BRUNO CORP. son marcas y se quedan."""
    from hoja import to_sheet, from_sheet
    a = 0xC61080
    g = lz77(h, a)
    img = to_sheet(g)
    for (x0, x1, y), txt, tilde in (((48, 80, 14), 'AZAFRAN', 5), ((48, 80, 102), 'POLICIA', 5),
                                    ((48, 80, 70), 'ESTADIO', None)):
        for yy in range(y, y + 5):
            for x in range(x0, x1):
                if img[yy][x] == 1:
                    img[yy][x] = 3
        escribir_bloque(img, x0, x1, y, txt, 1)
        if tilde is not None:  # misma cuenta de posiciones que escribir_bloque
            ancho = sum(len(BLOQUE[c][0]) + 1 for c in txt) - 1
            xl = x0 + (x1 - x0 - ancho + 1) // 2 + sum(len(BLOQUE[c][0]) + 1 for c in txt[:tilde])
            xc = xl + len(BLOQUE[txt[tilde]][0]) // 2  # columna central de la letra
            img[y - 2][xc + 1] = 1
            img[y - 1][xc] = 1
    poster_policia(img)
    guardar('tileset_azafran', a, from_sheet(img, g), 'carteles de Ciudad Azafrán (tools/edit_carteles.py)')
    # orden de los bloques en el mapa 3.10
    from rom import iter_maps, u32, u16, off
    import struct
    mh = next(hh for gg, mm, hh in iter_maps(h) if (gg, mm) == (3, 10))
    lay = off(u32(h, mh)); w, alto = u32(h, lay), u32(h, lay + 4); datos = off(u32(h, lay + 12))
    cambios = {(0x37E, 0x37F, 0x399, 0x386, 0x387): (3, 4, 2, 0, 1), (0x37E, 0x37F, 0x386, 0x387): (2, 3, 0, 1),
               (0x37E, 0x37F, 0x3CD, 0x3CE): (2, 3, 0, 1)}
    parches = []
    for y in range(alto):
        fila = [u16(h, datos + 2 * (y * w + x)) for x in range(w)]
        for x in range(w):
            for patron, orden in cambios.items():
                trozo = fila[x:x + len(patron)]
                if tuple(v & 0x3FF for v in trozo) == patron:
                    nuevo = [trozo[i] for i in orden]
                    a0 = datos + 2 * (y * w + x)
                    parches.append({'addr': '%X' % a0, 'orig': struct.pack('<%dH' % len(trozo), *trozo).hex(),
                                    'new': struct.pack('<%dH' % len(nuevo), *nuevo).hex(),
                                    'nota': 'carteles de Azafrán: orden de las palabras'})
    PARCHES.extend(parches)
    b = 0x810040  # otro tileset con el mismo póster
    g2 = lz77(h, b)
    img2 = to_sheet(g2)
    poster_policia(img2)
    guardar('tileset_poster', b, from_sheet(img2, g2), 'póster POLICIA (tools/edit_carteles.py)')
    print('  carteles de Azafrán reordenados:', len(parches))


def texto_ttf(txt, fuente, tam):
    """Máscara (filas de 0/1) de `txt` con una fuente de Windows sin suavizado."""
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype('C:/Windows/Fonts/' + fuente, tam)
    t = Image.new('1', (400, 60)); d = ImageDraw.Draw(t); d.fontmode = '1'
    d.text((4, 4), txt, font=f, fill=1)
    t = t.crop(t.getbbox())
    return [[t.getpixel((x, y)) for x in range(t.width)] for y in range(t.height)]


def sin_cambios(h):
    """Tileset 0x12C7FC0: cartel rojo "NO REFUNDS" (x 64-127, filas 162-171) -> "SIN CAMBIOS" (Impact)."""
    from hoja import to_sheet, from_sheet
    a = 0x12C7FC0
    g = lz77(h, a)
    img = to_sheet(g)
    borrar_color(img, (64, 160, 128, 173), 4)
    m = texto_ttf('SIN CAMBIOS', 'impact.ttf', 12)
    pegar(img, m, 64 + (64 - len(m[0])) // 2, 162, 4)
    guardar('tileset_reembolso', a, from_sheet(img, g), 'cartel SIN CAMBIOS (tools/edit_carteles.py)')


# letra fina de 3x6 del rótulo "LUNA FAMILY" (0x12ADCC0)
FINA6 = {
    'F': ['###', '#..', '#..', '##.', '#..', '#..'], 'A': ['.#.', '#.#', '#.#', '###', '#.#', '#.#'],
    'M': ['#...#', '##.##', '##.##', '#.#.#', '#...#', '#...#'], 'I': ['#'] * 6,
    'L': ['#..', '#..', '#..', '#..', '#..', '###'], 'U': ['#..#', '#..#', '#..#', '#..#', '#..#', '.##.'],
    'N': ['#..#', '##.#', '##.#', '#.##', '#.##', '#..#'],
}


def familia_luna(h):
    """Rótulo "LUNA FAMILY" (6 piezas: x 72-111 filas 0-7 y la sexta en x 72-79 filas 8-15) -> "FAMILIA LUNA"."""
    from hoja import to_sheet, from_sheet
    a = 0x12ADCC0
    g = lz77(h, a)
    img = to_sheet(g)
    tira = [[0] * 48 for _ in range(8)]
    col = lambda x, y: (72 + x, y) if x < 40 else (72 + x - 40, 8 + y)  # posición en la hoja
    for y in range(8):
        for x in range(48):
            sx, sy = col(x, y)
            if img[sy][sx] == 2 and 1 <= y <= 6:
                img[sy][sx] = 0
    txt = 'FAMILIA LUNA'
    ancho = sum(2 if c == ' ' else len(FINA6[c][0]) + 1 for c in txt) - 1
    x = 1 + (47 - ancho) // 2
    for c in txt:
        if c == ' ':
            x += 2
            continue
        for dy, f in enumerate(FINA6[c]):
            for dx, v in enumerate(f):
                if v == '#':
                    sx, sy = col(x + dx, 1 + dy)
                    img[sy][sx] = 2
        x += len(FINA6[c][0]) + 1
    guardar('tileset_luna', a, from_sheet(img, g), 'rótulo FAMILIA LUNA (tools/edit_carteles.py)')


# relleno (color 4) de la letra con contorno del anuncio de 0x1264080; el contorno (1) se añade alrededor
RELLENO = {
    'G': ['444', '4..', '4.4', '444'], 'U': ['4.4', '4.4', '4.4', '444'], 'A': ['444', '4.4', '444', '4.4'],
    'Y': ['4.4', '4.4', '.4.', '.4.'],
    'B': ['44.', '4.4', '44.', '4.4', '44.'], 'E': ['444', '4..', '44.', '4..', '444'],  # 5 filas, como LEVEL
}


def escribir_contorno(img, x, y, txt):
    """Letras de relleno 4 con contorno 1 (8 vecinos). (x, y): esquina del relleno de la primera letra."""
    relleno = set()
    for c in txt:
        for dy, f in enumerate(RELLENO[c]):
            for dx, v in enumerate(f):
                if v == '4':
                    relleno.add((x + dx, y + dy))
        x += len(RELLENO[c][0]) + 2
    for px, py in relleno:
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if (px + dx, py + dy) not in relleno:
                    img[py + dy][px + dx] = 1
    for px, py in relleno:
        img[py][px] = 4


def anuncio(h):
    """Anuncio con la mascota (0x1264080): "COOL" -> "GUAY" y "DRINK" -> "BEBE"; "LEVEL+" es la marca."""
    from hoja import to_sheet, from_sheet
    a = 0x1264080
    g = lz77(h, a)
    img = to_sheet(g)
    for (x0, y0, x1, y1) in ((8, 65, 31, 72), (0, 89, 32, 95)):
        for y in range(y0, y1):
            for x in range(x0, x1):
                if img[y][x] in (1, 4):
                    img[y][x] = 0
    escribir_contorno(img, 9, 67, 'GUAY')
    escribir_contorno(img, 6, 89, 'BEBE')
    guardar('tileset_anuncio', a, from_sheet(img, g), 'anuncio GUAY / BEBE (tools/edit_carteles.py)')


# letra de la ventana "Cancel / OK" dibujada en el tileset 0x123BC40 (r hecha igual que la n)
VENTANA = {
    'C': ['.####.', '#....#', '#.....', '#.....', '#.....', '#.....', '#.....', '#....#', '.####.'],
    'a': ['.....', '.....', '.....', '.###.', '....#', '.####', '#...#', '#...#', '.####'],
    'n': ['.....', '.....', '.....', '#.##.', '##..#', '#...#', '#...#', '#...#', '#...#'],
    'c': ['.....', '.....', '.....', '.###.', '#...#', '#....', '#....', '#...#', '.###.'],
    'e': ['.....', '.....', '.....', '.###.', '#...#', '#####', '#....', '#...#', '.###.'],
    'l': ['#'] * 9,
    'r': ['....', '....', '....', '#.##', '##..', '#...', '#...', '#...', '#...'],
}


def ventana_cancelar(h):
    """Ventana dibujada en un mapa (tileset 0x123BC40): botón "Cancel" -> "Cancelar" ("OK" se queda)."""
    from hoja import to_sheet, from_sheet
    a = 0x123BC40
    g = lz77(h, a)
    img = to_sheet(g)
    for y in range(52, 61):
        for x in range(84, 126):
            if img[y][x] == 1:
                img[y][x] = 3
    txt = 'Cancelar'
    x = 83 + (44 - (sum(len(VENTANA[c][0]) + 1 for c in txt) - 1)) // 2
    for c in txt:
        for dy, f in enumerate(VENTANA[c]):
            for dx, v in enumerate(f):
                if v == '#':
                    img[52 + dy][x + dx] = 1
        x += len(VENTANA[c][0]) + 1
    guardar('tileset_ventana', a, from_sheet(img, g), 'botón Cancelar (tools/edit_carteles.py)')


def pintada_soy(h):
    """Pintada roja "I AM" en la pared de la cueva (tileset 0x91A400, metatiles 2AB-2AC; mapa 7.12) -> "SOY"."""
    from hoja import to_sheet, from_sheet
    a = 0x91A400
    g = lz77(h, a)
    img = to_sheet(g)
    borrar_color(img, (64, 64, 96, 80), 4)
    m = texto_ink('SOY', 13)
    m = [[1 if v or (x and fila[x - 1]) else 0 for x, v in enumerate(fila + [0])] for fila in m]  # trazo de 2 px
    pegar(img, m, 64 + (32 - len(m[0])) // 2, 64 + (16 - len(m)) // 2, 4)
    guardar('tileset_pintada', a, from_sheet(img, g), 'pintada SOY (tools/edit_carteles.py)')


# ---------------------------------------------------------------- letras del suelo (mapa 12.4)
SUELO = [(5, 'FAMILIA EN UNA VIDA'), (7, 'Y AL FINAL'), (9, 'EVOLUCIONAR POR PAPÁ'), (11, 'UNA LUNA ETERNA')]
# original: FAMILY IN ONE LIFE / AND AFTER ALL / EVOLVE FOR MY FATHER / ONE MOON FOREVER
BLOQUE_LETRA = {'A': 0x3A0, 'D': 0x3A1, 'E': 0x3A2, 'F': 0x3A3, 'U': 0x3A4, 'I': 0x3A5, 'L': 0x3A6,
                'M': 0x3A8, 'N': 0x3A9, 'O': 0x3AA, 'R': 0x3AB, 'T': 0x3AC, 'V': 0x3AD, 'Y': 0x3AE,
                'P': 0x34B, 'C': 0x349, 'Á': 0x344}
# qué passkey revela cada letra (como en el original; las nuevas van con letras parecidas del mismo grupo)
GRUPOS = [('AYNÁ', b''), ('IOUC', bytes.fromhex('2f190030')), ('MRDP', bytes.fromhex('2f190030')),
          ('FLE', b''), ('TV', b'')]
# bloques de 16x16: fondo con la cuadrícula del suelo y letra de color 2 (trazo de 2 px)
FONDO_LETRA = (['1333333413333334'] + ['3333333433333334'] * 6 + ['4444444244444442', '1333333413333334']
               + ['3333333433333334'] * 6 + ['4444444244444442'])
LETRA_A = ['3333333223333334', '3333332222333334', '3333322222233334', '3333322222233334', '3333322332233334',
           '4444222332224442', '1333223333223334', '3333222222223334', '3332222432222334', '3332222432222334',
           '3322223433222234', '3322223433222234']  # filas 2-13 de la A original


def bloque_letra(filas_letra, desde=2):
    """Bloque de 16x16: la cuadrícula con los píxeles de color 2 de `filas_letra` puestos desde la fila `desde`."""
    b = [list(f) for f in FONDO_LETRA]
    for dy, f in enumerate(filas_letra):
        for x, v in enumerate(f):
            if v == '2':
                b[desde + dy][x] = '2'
    return [''.join(f) for f in b]


def letras_nuevas():
    """Letras que no existían: {letra: (metatile, piezas [arriba izq, arriba der, abajo izq, abajo der], dibujo)}.
    La U va en el bloque de la H (no se usa); las demás en piezas y metatiles libres del tileset."""
    U = bloque_letra(['3322333433332234'] * 5 + ['4422444244442242', '1322333413332234', '3322333433332234',
                                                 '3322233433322234', '3332223433222334', '3333222222223334',
                                                 '3333322222233334'])
    P = bloque_letra(['3222222223333334', '3222222222333334', '3222333422233334', '3222333432233334',
                      '3222333422233334', '4222222222444442', '1222222223333334'] + ['3222333433333334'] * 5)
    C = bloque_letra(['3333322222233334', '3333222222223334', '3332223433222334', '3322233433322234',
                      '3322333433333334', '4422444244444442', '1322333413333334', '3322333433333334',
                      '3322233433322234', '3332223433222334', '3333222222223334', '3333322222233334'])
    A = bloque_letra(LETRA_A, 3)  # la A una fila más abajo para que quepa la tilde
    for y, x in ((1, 10), (1, 11), (2, 9), (2, 10)):
        A[y] = A[y][:x] + '2' + A[y][x + 1:]
    return {'U': (0x3A4, (136, 137, 152, 153), U), 'P': (0x34B, (234, 235, 250, 251), P),
            'C': (0x349, (5, 21, 264, 272), C), 'Á': (0x344, (288, 295, 304, 310), A)}


def letras_suelo(h):
    """Sala de control (mapa 12.4): las passkeys van revelando en el suelo letras de 16x16 (tileset 0xF78F00,
    metatiles 3A0-3AE) que forman una frase. Se reescriben los scripts que las colocan con la frase española;
    las letras que faltaban (U, P, C, Á) van en piezas y metatiles libres. Los scripts nuevos van en 0x1FF4000
    y se reapuntan las llamadas."""
    import struct
    from hoja import to_sheet, from_sheet
    from rom import u32, off
    a = 0xF78F00
    g = lz77(h, a)
    img = to_sheet(g)
    ts = 0xBE6540
    mt, attr = off(u32(h, ts + 12)), off(u32(h, ts + 20))
    for letra, (meta, piezas, dib) in letras_nuevas().items():
        for k, t in enumerate(piezas):  # cada cuarto del bloque en su pieza
            x0, y0 = t % 16 * 8, t // 16 * 8
            for y in range(8):
                for x in range(8):
                    img[y0 + y][x0 + x] = int(dib[k // 2 * 8 + y][k % 2 * 8 + x], 16)
        if meta == 0x3A4:
            continue  # la U usa el metatile de la H tal cual
        m = mt + (meta - 0x280) * 16  # piezas con la paleta 11 (como las letras); capa de encima vacía
        nuevo = struct.pack('<8H', *[0xB000 | (640 + t) for t in piezas], 0, 0, 0, 0)
        PARCHES.append({'addr': '%X' % m, 'orig': h[m:m + 16].hex(), 'new': nuevo.hex(),
                        'nota': 'metatile de la ' + letra})
        at = attr + 4 * (meta - 0x280)
        PARCHES.append({'addr': '%X' % at, 'orig': h[at:at + 4].hex(), 'new': '00000000',
                        'nota': letra + ': suelo normal'})
    guardar('tileset_letras', a, from_sheet(img, g), 'letras del suelo U P C Á (tools/edit_carteles.py)')

    def poner(letras):
        out = bytearray()
        for y, txt in SUELO:
            for i, c in enumerate(txt):
                if c in letras:
                    out += b'\xa2' + struct.pack('<4H', 2 + i, y, BLOQUE_LETRA[c], 0)
        return out
    puerta = b'\xa2' + struct.pack('<4H', 11, 0, 0x00E, 0)
    usadas = set(''.join(t for _, t in SUELO)) - {' '}
    assert usadas <= set(''.join(l for l, _ in GRUPOS)), usadas - set(''.join(l for l, _ in GRUPOS))
    bloques = [pre + poner(l) + b'\x03' for l, pre in GRUPOS[:4]]
    bloques.append(poner('TV') + puerta + b'\x03')                       # la última passkey: abre la puerta
    bloques.append(poner(''.join(l for l, _ in GRUPOS)) + puerta + b'\x02')  # al volver a entrar: todo
    # (dirección del campo puntero en el script original, índice del bloque nuevo)
    llamadas = [(0x1082C18, 0), (0x1082C24, 1), (0x1082C30, 2), (0x1082D9B, 3), (0x1082E5A, 4), (0xF78785, 5)]
    viejos = [0x1082C47, 0x1082CB4, 0x1082D31, 0x1082ED7, 0xF744F2, 0xF7878D]
    base = 0x1FF4000
    datos, dirs = bytearray(), []
    for b in bloques:
        dirs.append(base + len(datos))
        datos += b
    assert all(v == 0xFF for v in h[base:base + len(datos)])
    PARCHES.append({'addr': '%X' % base, 'orig': h[base:base + len(datos)].hex(), 'new': datos.hex(),
                    'nota': 'scripts nuevos de las letras del suelo'})
    for campo, i in llamadas:
        assert u32(h, campo) == 0x8000000 + viejos[i], hex(campo)
        PARCHES.append({'addr': '%X' % campo, 'orig': h[campo:campo + 4].hex(),
                        'new': struct.pack('<I', 0x8000000 + dirs[i]).hex(), 'nota': 'llamada a letras del suelo'})
    print('  letras del suelo: %d bytes de script' % len(datos))


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    fondo_gotico(h, 0x85ED80, 0x850D00, 'muere1', range(0, 128), 15, 1)
    fondo_gotico(h, 0x84EC00, 0x84E100, 'muere2', range(0, 384), 3, 1)
    fondo_pixel(h)
    fondo_peores(h)
    tileset_gruta(h)
    azafran(h)
    sin_cambios(h)
    familia_luna(h)
    anuncio(h)
    ventana_cancelar(h)
    pintada_soy(h)
    letras_suelo(h)
    collage_gb(h)
    carta_nota(h)
    carta_halloween(h)
    json.dump(PARCHES, open(os.path.join(ROOT, 'data/parches_datos.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
