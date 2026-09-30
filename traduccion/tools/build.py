"""Construye el ROM en español a partir del ROM inglés parcheado.
- Textos originales con traducción oficial: se usa el texto español oficial (ajustado de mayúsculas).
- Traducciones propias: data/trad/*.json  {"texto inglés": "texto español", "@ID": "texto para ese id"}
Salida: build/ghostgrey_es.gba y build/GhostGrey_ES.bps
"""
import glob, json, os, re, sys
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from rom import *
from spanish import Wrapper, decap, MAX_W, BS, r_effect
from bps import make_bps

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, '..')
FREE_START = 0x1700000
FREE_END = 0x1F00000   # desde aquí, el código C de la traducción (data/codigo.bin)


def parse_txt(path):
    """Formato: '### ID' y debajo la traducción. Las líneas se unen con espacio;
    '\n' fuerza salto de línea, '\p' cambia de cuadro. Líneas que empiezan por '#!' son notas."""
    out = {}
    cur = None; buf = []; flags = []
    for line in open(path, encoding='utf8').read().split(chr(10)) + ['### FIN']:
        if line.startswith('### '):
            if cur and buf:
                txt = ' '.join(x.strip() for x in buf if x.strip())
                txt = txt.replace(BS + 'n ', chr(10)).replace(BS + 'n', chr(10))
                txt = txt.replace(' ' + BS + 'p', BS + 'p').replace(BS + 'p ', BS + 'p')
                txt = txt.replace(' ' + chr(10), chr(10))
                txt = txt.replace('{sp}', ' ')  # espacio explícito (inicio/fin de fragmentos)
                for tok, code in GENERO_TOK.items():  # terminaciones según chico/chica
                    txt = txt.replace(tok, '{B%02X}' % code)
                if 'r' in flags:  # efecto de la secta de los bichos: espacio antes de cada r
                    txt = r_effect(txt)
                out['@' + cur.upper()] = txt
            parts = line[4:].split()
            cur = parts[0] if parts else None
            flags = parts[1:]
            buf = []
        elif line.startswith('#! ancho '):
            out['#ancho'] = int(line.split()[2])
        elif not line.startswith('#!'):
            buf.append(line)
    return out


# Comodines de texto que cambian según el sexo del jugador (código FD xx del motor de texto).
# El 5 es el "-kun/-chan" japonés (vacío en inglés); 8-13 son restos de Rubí/Zafiro sin uso en campo.
GENERO = {0x05: ('o', 'a'), 0x08: ('', 'a'), 0x09: ('el', 'la'), 0x0A: ('ón', 'ona'),
          0x0B: ('e', 'a'), 0x0C: ('ÓN', 'ONA'), 0x0D: ('él', 'ella')}
GENERO_TOK = {'{o}': 0x05, '{a}': 0x08, '{el}': 0x09, '{on}': 0x0A, '{e}': 0x0B, '{ON}': 0x0C, '{él}': 0x0D}
KUNCHAN = 0x9144          # función original (chico -> literal +0x20, chica -> literal +0x14)
PLACEHOLDER_TABLE = 0x231E70


def parche_genero(rom, free):
    fn = bytes(rom[KUNCHAN:KUNCHAN + 0x24])
    for code, (m, f) in GENERO.items():
        ptrs = []
        for txt in (m, f):
            data = encode(txt)
            rom[free:free + len(data)] = data
            ptrs.append(free + ROM_BASE); free += len(data)
        free = (free + 3) & ~3
        if code == 0x05:
            dst = KUNCHAN
        else:
            dst = free
            rom[dst:dst + 0x24] = fn
            free += 0x24
            rom[PLACEHOLDER_TABLE + 4 * code:PLACEHOLDER_TABLE + 4 * code + 4] = struct.pack('<I', dst + ROM_BASE + 1)
        rom[dst + 0x20:dst + 0x24] = struct.pack('<I', ptrs[0])
        rom[dst + 0x14:dst + 0x18] = struct.pack('<I', ptrs[1])
    return free


def parche_estadisticas(rom):
    """ChangeStatBuffs monta el texto como [adverbio] + verbo ("sharply " + "rose!"). En castellano el
    adverbio va detrás, así que se cambia el código para que escriba un único texto: el del adverbio
    (0xD1 "subió mucho!", 0xD3 "bajó mucho!") si el cambio es de 2 niveles y si no el verbo (0xD2/0xD4)."""
    nop = 'c046'
    # bne +1; movs r0,#adv; b +0; movs r0,#verbo; strb r4,[r3,#1]; strb r0,[r3,#2]; strb r4,[r3,#3];
    # movs r0,#0xFF; strb r0,[r3,#4]; nops
    parches = {  # dirección: (código original, código nuevo)
        0x27F06: ('04d15c70d3209870dc700422d01804700132d118d42008700132d01804700132d118ff200870',
                  '01d1d32000e0d4205c709870dc70ff201871' + nop * 10),
        0x27F7A: ('04d15c70d1209870dc700422d01804700132d118d22008700132d01804700132d118087862461043' + '0870',
                  '01d1d12000e0d2205c709870dc70ff201871' + nop * 12),
    }
    for a, (old, new) in parches.items():
        o, n = bytes.fromhex(old), bytes.fromhex(new)
        assert rom[a:a + len(o)] == o, 'código de estadísticas distinto en %X' % a
        assert len(n) == len(o), (hex(a), len(n), len(o))
        rom[a:a + len(n)] = n


# teclado de la pantalla de nombres: letras de cada tecla (3 páginas x 4 filas x 8 columnas), número de
# columnas y posición x de cada columna por página, y punteros a los 12 textos que dibujan las filas
TECLAS, COLUMNAS, POS_X, TEXTOS_TECLADO = 0x3E22D0, 0x3E2330, 0x3E2333, 0x3E264C
# página de símbolos con tildes y ñ, igual que en la traducción de Emerald Rogue: 8 columnas y cada tecla
# dibujada en una x fija (CLEAR_TO); las páginas de letras no cambian
SIMBOLOS = ['01234áéí', '56789óúñ', '!?♂♀/-ÁÉ', '…“”’ÍÓÚÑ']
SIMBOLOS_X = [[11, 28, 45, 62, 79, 96, 113, 131], [11, 28, 45, 62, 79, 96, 113, 130],
              [12, 28, 45, 62, 79, 96, 113, 130], [11, 28, 45, 63, 80, 96, 113, 130]]
LETRAS_X = [11, 23, 35, 67, 79, 91, 103, 133]
ESTRECHAS = encode('ilI')[:-1]


def teclado_nombres(rom, free):
    orig = ['01234   ', '56789   ', '!?♂♀/-  ', '…“”‘’   ']
    assert rom[TECLAS + 64:TECLAS + 96] == b''.join(encode(f)[:-1] for f in orig), 'teclado de nombres distinto'
    assert rom[COLUMNAS:COLUMNAS + 3] == bytes([8, 8, 6])
    rom[COLUMNAS + 2] = 8
    rom[POS_X + 16:POS_X + 24] = bytes([0, 17, 34, 51, 68, 85, 102, 119])
    for f, (fila, xs) in enumerate(zip(SIMBOLOS, SIMBOLOS_X)):
        cod = encode(fila)[:-1]
        rom[TECLAS + 64 + 8 * f:TECLAS + 72 + 8 * f] = cod
        txt = bytearray()
        for c, x in zip(cod, xs):
            txt += bytes([0xFC, 0x13, x, c])  # CLEAR_TO x
        txt.append(0xFF)
        rom[free:free + len(txt)] = txt
        k = 8 + f
        rom[TEXTOS_TECLADO + 4 * k:TEXTOS_TECLADO + 4 * k + 4] = struct.pack('<I', free + ROM_BASE)
        free += len(txt)
    # páginas de letras: el original deja "j k l ," / "J K L ," 2 px a la izquierda de "d e f ." y descuadra
    # alguna fila más; se redibujan con cada letra en la x fija de su columna (las estrechas, 1 px a la derecha)
    for k in range(8):
        cod = rom[TECLAS + 8 * k:TECLAS + 8 * k + 8]
        txt = bytearray()
        for c, x in zip(cod, LETRAS_X):
            if c != 0x00:  # espacio: tecla vacía
                txt += bytes([0xFC, 0x13, x + (c in ESTRECHAS), c])
        txt.append(0xFF)
        rom[free:free + len(txt)] = txt
        rom[TEXTOS_TECLADO + 4 * k:TEXTOS_TECLADO + 4 * k + 4] = struct.pack('<I', free + ROM_BASE)
        free += len(txt)
    return (free + 3) & ~3


WIDTHS = {}  # ancho máximo por id fijado con '#! ancho N' en el archivo de traducción


def load_trad(inv=None):
    trad = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'data/trad/*'))):
        if f.endswith('.json'):
            d = json.load(open(f, encoding='utf8'))
        elif f.endswith('.txt'):
            d = parse_txt(f)
        else:
            continue
        w = d.pop('#ancho', None) if isinstance(d, dict) else None
        for k, v in d.items():
            if v:
                trad[k] = v
                if w and k.startswith('@'):
                    WIDTHS[k[1:]] = w
    # una traducción por id se aplica también a los textos idénticos (si no son cortos/ambiguos)
    if inv:
        by_id = {e['id']: e for e in inv}
        for k, v in list(trad.items()):
            if k.startswith('@') and k[1:] in by_id:
                e = by_id[k[1:]]
                if len(e['en']) >= 20:
                    trad.setdefault(e['en'], v)
                elif e['kind'] == 'script':
                    trad.setdefault('S:' + e['en'], v)  # frases cortas: solo entre scripts
    return trad


def png_a_tiles(path, base):
    """Lee un PNG indexado (16 colores, ancho múltiplo de 8) y lo convierte en piezas 4bpp.
    Las piezas se ordenan por filas; solo se sustituyen las que existen en el PNG."""
    from PIL import Image
    im = Image.open(path)
    px = im.load(); wt = im.width // 8
    out = bytearray(base)
    for t in range(min(len(base) // 32, wt * (im.height // 8))):
        tx, ty = t % wt * 8, t // wt * 8
        for y in range(8):
            for x in range(0, 8, 2):
                out[t * 32 + y * 4 + x // 2] = (px[tx + x, ty + y] & 15) | (px[tx + x + 1, ty + y] & 15) << 4
    return bytes(out)


def load_tablas():
    """Une las propuestas automáticas (data/tablas/*.auto.tsv, de tools/names.py) con las
    traducciones manuales (data/tablas/*.tsv). Devuelve {tabla: ((dir, paso, bytes, n), {índice: nombre})}."""
    from names import TABLES
    out = {}
    for tname, (ha, st, nl, n, *_r) in TABLES.items():
        names = {}
        for suf in ('.auto.tsv', '.tsv'):
            p = os.path.join(ROOT, 'data/tablas', tname + suf)
            if not os.path.exists(p):
                continue
            for line in open(p, encoding='utf8').read().split(chr(10)):
                if not line.strip() or line.startswith('#'):
                    continue
                parts = line.split('\t')
                val = parts[-1] if suf == '.tsv' else (parts[2] if len(parts) > 2 else '')
                if val.strip():
                    names[int(parts[0])] = val
        out[tname] = ((ha, st, nl, n), names)
    return out


def main(make_patch=True, only_official=False):
    src = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    rom = bytearray(src)
    inv = json.load(open(os.path.join(ROOT, 'data/inventory.json'), encoding='utf8'))
    # textos que el inventario no detecta (plantillas sin palabras, etc.): data/extra_inv.json
    xp = os.path.join(ROOT, 'data/extra_inv.json')
    if os.path.exists(xp):
        ids = {e['id'] for e in inv}
        for x in json.load(open(xp, encoding='utf8')):
            if x not in ids:
                t = int(x, 16)
                s, n = decode(src, t)
                inv.append({'id': x, 'en': s, 'len': n - t, 'refs': [], 'kind': 'code', 'where': [],
                            'us': None, 'es_off': None})
    trad = {} if only_official else load_trad(inv)
    wr = Wrapper(src)

    # rangos que se solapan: no se escriben en su sitio
    spans = sorted((int(e['id'], 16), int(e['id'], 16) + e['len']) for e in inv)
    overlap = set()
    for (a, b), (c, d) in zip(spans, spans[1:]):
        if c < b:
            overlap.add(a); overlap.add(c)

    # punteros alineados en toda la ROM (por si el texto también se usa desde código/tablas)
    words = np.frombuffer(src[:len(src) // 4 * 4], dtype='<u4')
    targets = {int(e['id'], 16) + ROM_BASE for e in inv}
    mask = np.isin(words, np.fromiter(targets, dtype=np.uint32))
    aligned = {}
    for i in np.nonzero(mask)[0]:
        aligned.setdefault(int(words[i]) - ROM_BASE, []).append(int(i) * 4)

    # punteros no alineados dentro de scripts que el inventario no recorrió (scripts llamados desde
    # código, como los de recoger objetos): loadpointer (0F 0x), message (67), 9B y C8
    import re as _re
    for m in _re.finditer(rb'(?:\x0f[\x00-\x03]|[\x67\x9b\xc8])(?=...[\x08\x09])', src):
        f = m.end()
        t = u32(src, f) - ROM_BASE
        if f % 4 and t + ROM_BASE in targets:
            aligned.setdefault(t, []).append(f)
    # textos de trainerbattle (5C tipo entrenador id textos…): la revancha (tipo 5/7) suele reutilizar los
    # textos del combate normal y el inventario solo apunta uno de los dos scripts
    NTEXTOS = {0: 2, 1: 2, 2: 2, 3: 1, 4: 3, 5: 2, 6: 3, 7: 3, 8: 3, 9: 2}
    for a in np.nonzero(np.frombuffer(src, dtype=np.uint8) == 0x5C)[0]:
        a = int(a)
        n = NTEXTOS.get(src[a + 1])
        if n is None or a + 6 + 4 * n > len(src) or not 0 < struct.unpack_from('<H', src, a + 2)[0] < 0x400:
            continue
        if not all(0x08000000 <= u32(src, a + 6 + 4 * k) < 0x0A000000 for k in range(n)):
            continue
        for k in range(n):
            f = a + 6 + 4 * k
            t = u32(src, f) - ROM_BASE
            if f % 4 and t + ROM_BASE in targets and f not in aligned.get(t, []):
                aligned.setdefault(t, []).append(f)

    tablas = load_tablas()
    en_tabla = set()
    for (ha, st, nl, _), names in tablas.values():
        for i in names:
            en_tabla.update(range(ha + st * i, ha + st * i + nl))
    free = FREE_START
    stats = {'oficial': 0, 'propia': 0, 'en_sitio': 0, 'reubicada': 0, 'anchas': [], 'tabla': 0}
    for e in inv:
        t = int(e['id'], 16)
        if t in en_tabla:
            continue  # lo escribe la tabla de nombres
        es = trad.get('@' + e['id']) or trad.get(e['en'])
        if not es and e['kind'] == 'script':
            es = trad.get('S:' + e['en'])
        fixed = e['kind'] == 'code' and BS + 'l' not in e['en'] and BS + 'p' not in e['en']
        if fixed:
            # ventana de disposición fija: se respetan los saltos; el límite es el ancho del inglés
            lines_en = e['en'].split(chr(10))
            maxw = max(wr.width(x) for x in lines_en) + 4 if len(lines_en) >= 3 else MAX_W
            if len(lines_en) >= 3 and maxw < 118:  # descripciones de movimientos: ~118 px
                maxw = 118
            elif 120 <= maxw < 190:  # ventanas anchas (descripciones de objetos): ~190 px
                maxw = 190
            elif 196 <= maxw < 228:  # Pokédex: ~228 px
                maxw = 228
            maxw = WIDTHS.get(e['id'], maxw)
        else:
            maxw = MAX_W
        if es:
            stats['propia'] += 1
            text = es if fixed else wr.wrap(es)
            if fixed and len(e['en'].split(chr(10))) < 3 and wr.too_wide(text):
                text = wr.wrap(text)
            if es == '<vacío>':  # cadena vacía (p. ej. prefijo "Wild ")
                text = ''
        elif e['es_off']:
            stats['oficial'] += 1
            text = decap(e['es_off'])
            # tras un icono de botón ({XF8xx}) va mayúscula: "{A}Sel. {B}Atrás"
            text = re.sub(r'(\{XF8..\})([a-záéíóúñ])', lambda m: m.group(1) + m.group(2).upper(), text)
            text = text.replace('}Ok', '}OK')
            if not fixed and wr.too_wide(text):
                text = wr.wrap(text)
            maxw = None  # el texto oficial ya está pensado para su ventana
        else:
            continue
        bad = wr.too_wide(text, maxw) if maxw else []
        if bad:
            stats['anchas'].append((e['id'], bad))
        data = encode(text)
        if len(data) <= e['len'] and t not in overlap:
            rom[t:t + e['len']] = data + b'\xff' * (e['len'] - len(data))
            stats['en_sitio'] += 1
        else:
            if free + len(data) > FREE_END:
                raise RuntimeError('sin espacio libre')
            rom[free:free + len(data)] = data
            new = struct.pack('<I', free + ROM_BASE)
            fields = set(e['refs']) | set(aligned.get(t, []))
            for f in fields:
                assert u32(src, f) == t + ROM_BASE, (e['id'], hex(f))
                rom[f:f + 4] = new
            free += len(data)
            free = (free + 3) & ~3
            stats['reubicada'] += 1

    free = parche_genero(rom, (free + 3) & ~3)
    free = teclado_nombres(rom, free)
    parche_estadisticas(rom)
    # parches de código ensamblados con tools/parches_asm.py (Pokédex en metros y kilos)
    # parches de código (tools/parches_asm.py) y de datos, como el orden de los carteles de un mapa
    # (tools/edit_carteles.py escribe data/parches_datos.json)
    pd = os.path.join(ROOT, 'data/parches_datos.json')
    for pch in json.load(open(os.path.join(ROOT, 'data/parches_codigo.json'))) + (
            json.load(open(pd)) if os.path.exists(pd) else []):
        a, o, n = int(pch['addr'], 16), bytes.fromhex(pch['orig']), bytes.fromhex(pch['new'])
        assert rom[a:a + len(o)] == o, 'parche de código: bytes distintos en %X' % a
        rom[a:a + len(n)] = n
    # código C de la traducción (tools/codigo_c.py): pantallas de crédito tras el logo del creador del hack y
    # clases de entrenador en femenino según el sprite (data/tablas/clases_femeninas.tsv)
    cj = os.path.join(ROOT, 'data/codigo.json')
    if os.path.exists(cj):
        info = json.load(open(cj))
        blob = open(os.path.join(ROOT, 'data/codigo.bin'), 'rb').read()
        a = int(info['dir'], 16)
        assert FREE_END <= a and rom[a:a + len(blob)] == bytes([0xFF]) * len(blob), 'código C: la zona no está libre'
        rom[a:a + len(blob)] = blob
        cambios = [(p['addr'], struct.pack('<I', int(p['orig'], 16)), struct.pack('<I', int(p['new'], 16)))
                   for p in info['ganchos']]  # punteros a funciones del bloque
        cambios += [(p['addr'], bytes.fromhex(p['orig']), bytes.fromhex(p['new'])) for p in info['parches']]
        for g, o, n in cambios:
            g = int(g, 16)
            assert rom[g:g + len(o)] == o, 'código C: bytes distintos en %X' % g
            rom[g:g + len(n)] = n
        tf = int(info['clases_femeninas'], 16)
        tabla = bytearray()
        for l in open(os.path.join(ROOT, 'data/tablas/clases_femeninas.tsv'), encoding='utf8'):
            if l.startswith('#') or not l.strip():
                continue
            c, spr, nombre = l.rstrip('\n').split('\t')
            texto = encode(nombre)
            if len(texto) > 13:
                raise ValueError('clase femenina demasiado larga: ' + nombre)
            # sprite "#N": solo el entrenador N (cuando chicos y chicas comparten sprite)
            ent, spr = (int(spr[1:]), 0) if spr.startswith('#') else (0xFFFF, int(spr))
            tabla += struct.pack('<HBB', ent, int(c), spr) + texto + bytes([0xFF]) * (16 - len(texto))
        tabla += bytes([0xFF]) * 20
        assert rom[tf:tf + len(tabla)] == bytes([0xFF]) * len(tabla), 'clases femeninas: la zona no está libre'
        rom[tf:tf + len(tabla)] = tabla

    # tablas de nombres de longitud fija (data/tablas)
    for tname, ((ha, st, nl, _), names) in tablas.items():
        for i, name in names.items():
            data = encode(name)
            if len(data) > nl or (tname == 'objetos' and len(data) > 13):  # tienda: 12 letras + fin
                raise ValueError('nombre demasiado largo en %s[%d]: %s' % (tname, i, name))
            a0 = ha + st * i
            rom[a0:a0 + nl] = data + b'\x00' * (nl - len(data))
            stats['tabla'] += 1

    # gráficos con texto: versión oficial española de los que el hack no modificó (data/graficos_es.json)
    gp = os.path.join(ROOT, 'data/graficos_es.json')
    if os.path.exists(gp):
        from graficos import lz77_end
        es_rom = open(os.path.join(ROOT, '../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()
        usa_rom = open(os.path.join(ROOT, '../Pokemon - FireRed Version (USA).gba'), 'rb').read()
        words = np.frombuffer(bytes(rom[:len(rom) // 4 * 4]), dtype='<u4')
        ngfx = 0
        for r in json.load(open(gp)):
            ua, ea = int(r['us'], 16), int(r['es'], 16)
            if r.get('crudo'):  # sin comprimir y del mismo tamaño: se sobrescribe en su sitio
                n = int(r['crudo'], 16)
                assert rom[ua:ua + n] == usa_rom[ua:ua + n], 'gráfico %s modificado por el hack' % r['us']
                rom[ua:ua + n] = es_rom[ea:ea + n]
                ngfx += 1
                continue
            blob = es_rom[ea:lz77_end(es_rom, ea)]
            free = (free + 3) & ~3
            if free + len(blob) > FREE_END:
                raise RuntimeError('sin espacio libre')
            rom[free:free + len(blob)] = blob
            idx = np.nonzero(words == ua + ROM_BASE)[0]
            for i in idx:
                rom[int(i) * 4:int(i) * 4 + 4] = struct.pack('<I', free + ROM_BASE)
            free += len(blob)
            ngfx += 1
            if not len(idx):
                print('  aviso: gráfico sin punteros', r['us'])
        # gráficos modificados por el hack: pieza a pieza, española donde el hack no tocó nada
        from graficos import lz77, lz77_comp, mezcla
        mp = os.path.join(ROOT, 'data/graficos_mezcla.json')
        for r in (json.load(open(mp)) if os.path.exists(mp) else []):
            ua, ea, pa = int(r['us'], 16), int(r['es'], 16), int(r['ptr'], 16)
            ha = u32(src, pa) - ROM_BASE
            dh = lz77(src, ha)
            if r.get('png'):
                dh = png_a_tiles(os.path.join(ROOT, r['png']), dh)
            m, _, _ = mezcla(lz77(usa_rom, ua), lz77(es_rom, ea), dh)
            blob = lz77_comp(m)
            free = (free + 3) & ~3
            rom[free:free + len(blob)] = blob
            idx = np.nonzero(words == ha + ROM_BASE)[0]
            for i in idx:
                rom[int(i) * 4:int(i) * 4 + 4] = struct.pack('<I', free + ROM_BASE)
            free += len(blob)
            ngfx += 1
        # gráficos editados a mano (tools/edit_*.py): se comprimen y se redirigen los punteros
        bp = os.path.join(ROOT, 'data/gfx_bin.json')
        for r in (json.load(open(bp)) if os.path.exists(bp) else []):
            oa = int(r['orig'], 16)
            if r.get('sin_comprimir'):  # gráfico sin comprimir: se sobrescribe en su sitio
                raw = open(os.path.join(ROOT, r['file']), 'rb').read()
                rom[oa:oa + len(raw)] = raw
                ngfx += 1
                continue
            blob = lz77_comp(open(os.path.join(ROOT, r['file']), 'rb').read())
            free = (free + 3) & ~3
            rom[free:free + len(blob)] = blob
            idx = np.nonzero(words == oa + ROM_BASE)[0]
            if not len(idx):
                print('  aviso: sin punteros a', r['orig'])
            for i in idx:
                rom[int(i) * 4:int(i) * 4 + 4] = struct.pack('<I', free + ROM_BASE)
            free += len(blob)
            ngfx += 1
        stats['graficos'] = ngfx

    # cabecera: código de juego español no; se mantiene BPRE para compatibilidad con el hack
    out = os.path.join(ROOT, 'build/ghostgrey_es.gba')
    open(out, 'wb').write(rom)
    print('oficiales %(oficial)d  propias %(propia)d  en sitio %(en_sitio)d  reubicadas %(reubicada)d' % stats)
    print('espacio libre usado: %d KB' % ((free - FREE_START) // 1024), ' nombres en tablas:', stats['tabla'],
          ' gráficos:', stats.get('graficos', 0))
    for i, b in stats['anchas'][:20]:
        print('  ANCHA', i, b)
    if make_patch:
        usa = open(os.path.join(ROOT, '../Pokemon - FireRed Version (USA).gba'), 'rb').read()
        p = make_bps(usa, bytes(rom))
        open(os.path.join(ROOT, 'build/GhostGrey_ES.bps'), 'wb').write(p)
        print('parche: %d KB' % (len(p) // 1024))


if __name__ == '__main__':
    main(make_patch='--nopatch' not in sys.argv, only_official='--oficial' in sys.argv)
