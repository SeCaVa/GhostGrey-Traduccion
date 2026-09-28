"""Inventario de textos del hack (ROM inglés parcheado).
Salida: data/inventory.json  lista ordenada de entradas:
  {id, en, refs:[offsets de campos puntero], kind, where:[contextos], us: offset_us|None, es_off: texto oficial|None}
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from rom import *

HERE = os.path.dirname(__file__)
gg = open(os.path.join(HERE, '../build/ghostgrey_en.gba'), 'rb').read()
us = open(os.path.join(HERE, '../../Pokemon - FireRed Version (USA).gba'), 'rb').read()
pairs = {int(k, 16): v for k, v in json.load(open(os.path.join(HERE, '../data/vanilla_pairs.json'), encoding='utf8')).items()}
code_pairs = {int(k, 16): v for k, v in json.load(open(os.path.join(HERE, '../data/vanilla_pairs_code.json'), encoding='utf8')).items()}
for k, v in code_pairs.items():
    pairs.setdefault(k, v)


def norm(s):
    s = s.lower().replace('poké', 'poke').replace('é', 'e')
    return re.sub(r'\s+|\\[lnp]', ' ', s).strip()


by_norm = {}
for a, (su, se) in pairs.items():
    by_norm.setdefault(norm(su), (a, se))

entries = {}  # offset texto -> entrada


def entry(t, kind):
    e = entries.get(t)
    if e is None:
        s, end = decode(gg, t)
        e = entries[t] = {'id': '%07X' % t, 'en': s, 'len': end - t, 'refs': [], 'kind': kind,
                          'where': [], 'us': None, 'es_off': None}
    return e


# 1) textos referenciados desde scripts de mapas
w = ScriptWalker(gg)
for g, m, h in iter_maps(gg):
    for k, s in map_scripts(gg, h):
        before = set(w.text_refs)
        w.walk(s)
        for f in set(w.text_refs) - before:
            e = entry(w.text_refs[f], 'script')
            e['refs'].append(f)
            tag = '%d.%d %s' % (g, m, k)
            if tag not in e['where']:
                e['where'].append(tag)
# los textos ya visitados por otra ruta pueden tener campos adicionales
for f, t in w.text_refs.items():
    e = entry(t, 'script')
    if f not in e['refs']:
        e['refs'].append(f)

# 1b) textos referenciados por punteros alineados (código y tablas)
import numpy as np
words = np.frombuffer(gg, dtype='<u4')
cand = np.nonzero((words >= ROM_BASE) & (words < ROM_BASE + len(gg)))[0]
script_bytes = w.visited
for i in cand:
    t = int(words[i]) - ROM_BASE
    if t in entries or t <= 0 or gg[t - 1] not in (0xFF, 0x00):
        continue
    if t in w.visited or t in w.movement_ptrs or t in w.mart_ptrs:
        continue
    s_, end = decode(gg, t)
    if not s_ or len(s_) < 2:
        continue
    plain = re.sub(r'\{[^}]*\}|\\[lnp]|\n', ' ', s_)
    letters = sum(ch.isalpha() for ch in plain)
    if letters < 2 or not re.search('[A-Za-z]{2}', plain):
        continue
    # descartar basura: demasiados símbolos raros
    rare = sum(ch in 'ÀÁÂÇÈÊËÌÎÏÒÔŒÙÛßàâçèêëìîïòôœùûºª►ÄÖÜäöü↑↓←→ᵉ×' for ch in plain)
    if rare > max(1, len(plain) // 10):
        continue
    entry(t, 'code')
for i in cand:
    t = int(words[i]) - ROM_BASE
    e = entries.get(t)
    if e and e['kind'] == 'code':
        e['refs'].append(int(i) * 4)

# 2) marcar textos originales y buscar su versión española oficial
for t, e in entries.items():
    u = decode(us, t)[0]
    if u is not None and norm(u) == norm(e['en']) and t in pairs:
        e['us'] = '%07X' % t
        e['es_off'] = pairs[t][1]
    else:
        hit = by_norm.get(norm(e['en'])) if len(e['en']) >= 14 else None
        if hit:
            e['us'] = '%07X' % hit[0]
            e['es_off'] = hit[1]

inv = sorted(entries.values(), key=lambda e: int(e['id'], 16))
json.dump(inv, open(os.path.join(HERE, '../data/inventory.json'), 'w', encoding='utf8'),
          ensure_ascii=False, indent=1)
nv = sum(1 for e in inv if e['es_off'])
print('textos', len(inv), 'originales con traducción oficial', nv, 'nuevos', len(inv) - nv)
print('palabras nuevas', sum(len(e['en'].split()) for e in inv if not e['es_off']))
print('errores de script', len(w.errors))
