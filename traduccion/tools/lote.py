"""Exporta un lote de textos pendientes de traducir.
Uso: python tools/lote.py NOMBRE [--mapas 3.0,4.1,...] [--ids 01C5A04,0A58B80,...] [--rango INI-FIN] [--todo]
Escribe data/lotes/NOMBRE.txt con: id, dónde aparece, texto inglés y pista (texto oficial en esa dirección).
Los textos ya traducidos (en data/trad) u oficiales se omiten salvo --todo."""
import argparse, glob, json, os, sys
sys.path.insert(0, os.path.dirname(__file__))

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, '..')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('nombre')
    ap.add_argument('--mapas', default='')
    ap.add_argument('--ids', default='')
    ap.add_argument('--rango', default='')
    ap.add_argument('--todo', action='store_true')
    a = ap.parse_args()
    inv = json.load(open(os.path.join(ROOT, 'data/inventory.json'), encoding='utf8'))
    pairs = json.load(open(os.path.join(ROOT, 'data/vanilla_pairs.json'), encoding='utf8'))
    pairs.update(json.load(open(os.path.join(ROOT, 'data/vanilla_pairs_code.json'), encoding='utf8')))
    from build import load_trad
    done = load_trad(inv)
    mapas = set(x for x in a.mapas.split(',') if x)
    ids = set(x.upper().zfill(7) for x in a.ids.split(',') if x)
    lo = hi = None
    if a.rango:
        lo, hi = (int(x, 16) for x in a.rango.split('-'))
    out = []
    seen = set()
    for e in inv:
        sel = e['id'] in ids
        if mapas and any(w.split(' ')[0] in mapas for w in e['where']):
            sel = True
        if lo is not None and lo <= int(e['id'], 16) < hi:
            sel = True
        if not sel:
            continue
        if not a.todo and (e['es_off'] or e['en'] in done or '@' + e['id'] in done
                           or (e['kind'] == 'script' and 'S:' + e['en'] in done)):
            continue
        if not e['en'].strip():
            continue
        if e['en'] in seen:
            continue
        seen.add(e['en'])
        hint = pairs.get(e['id'])
        out.append('### %s  [%s] %s\n%s\n%s' % (
            e['id'], e['kind'], ', '.join(e['where'][:4]), e['en'],
            ('>>> oficial: ' + hint[1]) if hint else ''))
    os.makedirs(os.path.join(ROOT, 'data/lotes'), exist_ok=True)
    p = os.path.join(ROOT, 'data/lotes', a.nombre + '.txt')
    open(p, 'w', encoding='utf8').write('\n\n'.join(out) + '\n')
    print(p, len(out), 'textos,', sum(len(x.split()) for x in out), 'palabras aprox')


main()
