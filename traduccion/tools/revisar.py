"""Comprobaciones automáticas de la traducción:
  1. Signos de apertura: frases con ! o ? sin su ¡ o ¿.
  2. Signos repetidos (!!, ¡¡, ??) y espacios dobles o antes de un signo.
  3. Nombres oficiales: los nombres puestos a mano (data/tablas/*.tsv) de movimientos, habilidades y objetos cuyo
     nombre inglés es el oficial deben ser el oficial español de PokeAPI (idioma 7, en ../pokeapi) o una
     abreviatura suya. Los automáticos (*.auto.tsv) salen de Rojo Fuego en español y no se revisan: son los
     oficiales de la 3.ª generación, que a veces difieren de los actuales (Más Psique / Autosugestión).
  python tools/revisar.py [signos|nombres]"""
import csv, glob, json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
API = os.path.join(ROOT, '..', 'pokeapi')
LIMITE = {'movimientos': 12, 'habilidades': 12, 'objetos': 12}
# nombres oficiales antiguos elegidos a propósito: caben sin abreviar (el actual no) o van a juego con el de Rojo Fuego
ANTIGUOS = {('movimientos', 381): 'Canto Helado (hoy Esquirla Helada)',
            ('objetos', 226): 'Gafas Elegidas, como Cinta Elegida de Rojo Fuego (hoy Gafas Elección)',
            ('objetos', 227): 'Pañuelo Elegido, como Cinta Elegida de Rojo Fuego (hoy Pañuelo Elección)'}


def textos():
    """(archivo, id, texto) de todas las traducciones."""
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'trad', '*.txt'))):
        ident, lineas = None, []
        for l in open(f, encoding='utf8').read().split('\n') + ['### fin']:
            if l.startswith('### '):
                if ident is not None:
                    yield os.path.basename(f), ident, '\n'.join(lineas).strip()
                ident, lineas = l[4:].strip(), []
            elif not l.startswith('#!'):
                lineas.append(l)
    for f in sorted(glob.glob(os.path.join(ROOT, 'data', 'trad', '*.json'))):
        for k, v in json.load(open(f, encoding='utf8')).items():
            yield os.path.basename(f), k[:30].replace('\n', ' '), v


def limpio(t):
    t = re.sub(r'\{[^}]*\}', 'X', t)        # códigos del juego y marcas de género
    return t.replace('\\p', '\n').replace('\\n', ' ')


def signos():
    n = 0
    for f, i, t in textos():
        s = limpio(t)
        avisos = []
        s = re.sub(r'\?{3}', 'X', s)                                   # "???" como nombre de quien habla
        s = re.sub(r'\b(Prof|Dr|Sr|Sra|Srta|Mt|Nv|Exp|St|Sto|Mr|Ms)\.', r'\1', s)   # abreviaturas
        s = re.sub(r'([!?¡¿])\1+', r'\1', s)                           # ¡¡…!! enfáticos: cuentan como uno
        # frases: se cortan tras . ! ? seguidos de espacio, o en un cuadro nuevo (los … no cortan)
        for frase in re.split(r'(?<=[.!?])\s+|\n', s):
            ab = frase.count('¡') + frase.count('¿')
            ce = frase.count('!') + frase.count('?')
            if ab == ce:                                               # admite ¿…! y ¡…? cruzados
                continue
            falta = ('¡' if frase.count('!') > frase.count('¡') else '¿') if ce > ab else \
                    ('!' if frase.count('¡') > frase.count('!') else '?')
            avisos.append('falta %s: %s' % (falta, frase.strip()))
        if re.search(r'[^ \n]  +[^ \n]', s) or re.search(r' [,.!?:;]', s):
            avisos.append('espacio de más: ' + re.sub(r'\s+', ' ', s)[:100])
        for a in avisos:
            print('%s %s  %s' % (f, i, a[:110]))
            n += 1
    print('==', n, 'avisos de signos y espacios')


def sin_tildes(s):
    s = unicodedata.normalize('NFD', s.lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def clave(s):
    return re.sub(r'[^a-z0-9]', '', sin_tildes(s.replace('é', 'e')))


def abreviatura(corto, largo):
    """¿`corto` abrevia `largo`? ("Colm. Ígneo" / "Colmillo Ígneo", "Superrepel" / "Superrepelente")."""
    a = [clave(w) for w in corto.split()]
    b = [clave(w) for w in largo.split() if clave(w) not in ('de', 'del')]
    if len(a) == len(b) and all(y.startswith(x) for x, y in zip(a, b) if x):
        return True
    return clave(largo.replace(' de ', ' ')).startswith(clave(corto))


def oficiales(tabla, col):
    nombres = {}
    for r in csv.DictReader(open(os.path.join(API, tabla), encoding='utf8')):
        nombres.setdefault(r[col], {})[r['local_language_id']] = r['name']
    return [(v['9'], v['7']) for v in nombres.values() if '9' in v and '7' in v]


def tabla(nombre):
    """{índice: (inglés del hack, español final, puesto a mano)} como lo escribe build.py."""
    out = {}
    for l in open(os.path.join(ROOT, 'data', 'tablas', nombre + '.auto.tsv'), encoding='utf8'):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 3:
            out[int(p[0])] = [p[1], p[2], False]
    for l in open(os.path.join(ROOT, 'data', 'tablas', nombre + '.tsv'), encoding='utf8'):
        if l.startswith('#') or '\t' not in l:
            continue
        p = l.rstrip('\n').split('\t')
        if int(p[0]) in out:
            out[int(p[0])][1:] = [p[-1], True]
    return out


def nombres():
    total = 0
    for nombre, csvf, col in (('movimientos', 'move_names.csv', 'move_id'),
                              ('habilidades', 'ability_names.csv', 'ability_id'),
                              ('objetos', 'item_names.csv', 'item_id')):
        of = oficiales(csvf, col)
        por_clave = {}
        for en, es in of:
            por_clave.setdefault(clave(en), set()).add(es)
        malos = []
        for i, (en, es, mano) in sorted(tabla(nombre).items()):
            if not mano or (nombre, i) in ANTIGUOS:
                continue
            k = clave(en)
            cand = por_clave.get(k)
            if not cand and len(en) >= LIMITE[nombre]:     # nombre inglés cortado por el límite de la tabla
                pref = {e for c, s in por_clave.items() if c.startswith(k) for e in s}
                cand = pref if len(pref) == 1 else None
            if not cand or not es or es in ('-', '(?)', '????????'):
                continue
            if any(clave(c) == clave(es) for c in cand):
                continue
            tipo = 'ABREVIADO' if any(abreviatura(es, c) for c in cand) else 'DISTINTO'
            malos.append((tipo, i, en, es, ' / '.join(sorted(cand))))
        for m in sorted(malos, key=lambda m: m[0] != 'DISTINTO'):
            print('%-12s %-9s %3d  %-14s -> %-14s oficial: %s' % ((nombre,) + m))
        print('== %s: %d distintos, %d abreviados' % (nombre, sum(m[0] == 'DISTINTO' for m in malos),
                                                        sum(m[0] == 'ABREVIADO' for m in malos)))
        total += len(malos)


if __name__ == '__main__':
    que = sys.argv[1:] or ['signos', 'nombres']
    if 'signos' in que:
        signos()
    if 'nombres' in que:
        nombres()
