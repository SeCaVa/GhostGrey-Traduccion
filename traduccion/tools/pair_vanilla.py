"""Empareja textos del ROM USA con los del ROM español recorriendo scripts en paralelo.
Salida: data/vanilla_pairs.json  {offset_us_hex: [texto_us, texto_es]}"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from rom import *

HERE = os.path.dirname(__file__)
us = open(os.path.join(HERE, '../../Pokemon - FireRed Version (USA).gba'), 'rb').read()
es = open(os.path.join(HERE, '../../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()

pairs = {}
conflicts = 0
visited = set()


def add(tu, te):
    global conflicts
    su, _ = decode(us, tu)
    se, _ = decode(es, te)
    if su is None or se is None:
        return
    if tu in pairs and pairs[tu][1] != se:
        conflicts += 1
    pairs[tu] = (su, se)


def lockstep(a, b):
    stack = [(a, b)]
    while stack:
        pa, pb = stack.pop()
        while True:
            if (pa, pb) in visited or pa >= len(us) or pb >= len(es):
                break
            visited.add((pa, pb))
            op = us[pa]
            if op != es[pb] or op not in L:
                break
            x, y = pa + 1, pb + 1
            if op == 0x5C:
                kind = us[x]
                fields = TB.get(kind)
                if fields is None or es[y] != kind:
                    break
                qa, qb = x + 5, y + 5
                for f in fields:
                    va, vb = u32(us, qa), u32(es, qb)
                    if is_ptr(va, len(us)) and is_ptr(vb, len(es)):
                        if f == 't': add(off(va), off(vb))
                        else: stack.append((off(va), off(vb)))
                    qa += 4; qb += 4
                pa, pb = qa, qb
                continue
            n = L[op]
            if op in SCRIPT_PTR:
                k = SCRIPT_PTR[op]
                stack.append((off(u32(us, x + k)), off(u32(es, y + k))))
            elif op in TEXT_PTR or op == 0x0F:
                k = TEXT_PTR.get(op, 1)
                va, vb = u32(us, x + k), u32(es, y + k)
                if is_ptr(va, len(us)) and is_ptr(vb, len(es)):
                    add(off(va), off(vb))
            if op in END_OPS:
                break
            pa, pb = x + n, y + n


mu = list(iter_maps(us))
me = list(iter_maps(es))
assert [(g, m) for g, m, _ in mu] == [(g, m) for g, m, _ in me], 'estructura de mapas distinta'
for (g, m, hu), (_, _, he) in zip(mu, me):
    su, se = map_scripts(us, hu), map_scripts(es, he)
    for (k1, a), (k2, b) in zip(su, se):
        if k1 == k2:
            lockstep(a, b)

# scripts comunes (callstd, etc.) de la tabla gStdScripts: 0x160450 en USA
print('pares', len(pairs), 'conflictos', conflicts)
json.dump({'%07X' % k: v for k, v in sorted(pairs.items())},
          open(os.path.join(HERE, '../data/vanilla_pairs.json'), 'w', encoding='utf8'),
          ensure_ascii=False, indent=0)
