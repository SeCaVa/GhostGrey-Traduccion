"""Tablas de nombres de longitud fija (movimientos, habilidades, objetos, tipos, clases de entrenador).
Genera data/tablas/NOMBRE.tsv con: índice, nombre del hack (inglés), propuesta en español.
Si el nombre del hack coincide con el de la versión USA, se propone el oficial español.
Las líneas con la 3.ª columna vacía están pendientes; build.py escribe las que tengan texto."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from rom import *
from spanish import decap

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, '..')
# nombre: (dir. hack, paso, bytes del nombre, nº entradas hack, dir. USA, dir. ES, nº entradas vanilla)
TABLES = {
    'movimientos': (0x901800, 13, 13, 540, 0x247094, 0x242800, 355),
    'habilidades': (0x950000, 13, 13, 156, 0x24FC40, 0x24B408, 78),
    'objetos': (0x3DB028, 44, 14, 400, 0x3DB028, 0x3D4F50, 375),
    'tipos': (0x961B50, 7, 7, 24, 0x24F1A0, 0x24A90C, 18),
    'clases': (0x23E558, 13, 13, 107, 0x23E558, 0x239CC4, 107),
    'categorias': (0x44E850, 0x24, 12, 387, 0x44E850, 0x44912C, 387),
    'entrenadores': (0x23EACC, 40, 12, 743, None, None, 0),  # solo manual (data/tablas/entrenadores.tsv)
}


MINOR = {'de', 'del', 'la', 'el', 'y', 'a', 'en', 'los', 'las'}
KEEP = {'PS', 'MT', 'MO', 'PP', 'EXP.', 'S.S.', 'S.A.', 'ID'}


def tcase(e):
    """Nombre oficial en mayúsculas -> estilo título ("PUÑO FUEGO" -> "Puño Fuego")."""
    out = []
    for k, w in enumerate(e.split(' ')):
        if w.upper() in KEEP or any(ch.isdigit() for ch in w):
            out.append(w); continue
        lw = w.lower().replace('poké', 'poké')
        if k > 0 and lw in MINOR:
            out.append(lw)
        else:
            out.append(lw[:1].upper() + lw[1:])
    r = ' '.join(out)
    return r.replace('Pokéball', 'Poké Ball').replace('Superball', 'Super Ball').replace('Ultraball', 'Ultra Ball')


def norm(s):
    return (s or '').replace(' ', '').replace('é', 'E').upper()


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    us = open(os.path.join(ROOT, '../Pokemon - FireRed Version (USA).gba'), 'rb').read()
    es = open(os.path.join(ROOT, '../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()
    for name, (ha, st, nl, n, ua, ea, nv) in TABLES.items():
        if ua is None:
            continue
        out = []
        # diccionario inglés->español de la tabla vanilla (para tablas reordenadas por el hack)
        dic = {}
        for i in range(nv):
            u, _ = decode(us, ua + st * i)
            e, _ = decode(es, ea + st * i)
            if u and e:
                dic.setdefault(norm(u), {}).setdefault(e, 0)
                dic[norm(u)][e] += 1
        for i in range(n):
            s, _ = decode(h, ha + st * i)
            if s is None:
                break
            prop = ''
            if i < nv:
                u, _ = decode(us, ua + st * i)
                e, _ = decode(es, ea + st * i)
                if u and e and norm(s) == norm(u):
                    prop = tcase(e)
            if not prop and name in ('categorias',) and norm(s) in dic:
                d = dic[norm(s)]
                prop = tcase(max(d, key=d.get))
            out.append('%d\t%s\t%s' % (i, s, prop))
        p = os.path.join(ROOT, 'data/tablas', name + '.auto.tsv')
        open(p, 'w', encoding='utf8').write('\n'.join(out) + '\n')
        print(name, len(out), 'pendientes', sum(1 for x in out if x.endswith('\t') and x.split('\t')[1].strip()))


if __name__ == '__main__':
    main()
