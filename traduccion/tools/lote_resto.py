"""Exporta los textos de código pendientes, excluyendo rangos (easy chat, decoraciones...).
Uso: python tools/lote_resto.py NOMBRE INI-FIN [INI-FIN ...] (rangos a incluir; por defecto todo)"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from build import load_trad
ROOT = os.path.join(os.path.dirname(__file__), '..')
EXCL = [(0x3E0000, 0x3F0000), (0x450000, 0x460000)]
inv = json.load(open(os.path.join(ROOT, 'data/inventory.json'), encoding='utf8'))
done = load_trad(inv)
rng = [tuple(int(x, 16) for x in r.split('-')) for r in sys.argv[2:]] or [(0, 1 << 32)]
out = []; seen = set()
for e in inv:
    t = int(e['id'], 16)
    if e['kind'] != 'code' or any(a <= t < b for a, b in EXCL) or not any(a <= t < b for a, b in rng):
        continue
    if e['es_off'] or e['en'] in done or '@' + e['id'] in done or not e['en'].strip() or e['en'] in seen:
        continue
    if '( ( (' in e['en']:
        continue
    seen.add(e['en'])
    out.append('### %s\n%s\n' % (e['id'], e['en']))
p = os.path.join(ROOT, 'data/lotes', sys.argv[1] + '.txt')
open(p, 'w', encoding='utf8').write('\n'.join(out))
print(p, len(out), sum(len(x.split()) for x in out))
