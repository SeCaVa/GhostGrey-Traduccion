"""Empareja textos USA↔ES apuntados desde tablas de punteros (rachas de punteros a texto).
Complementa pair_code.py: en las tablas no hay anclas de bytes idénticos, así que se prueba
cada desplazamiento de las anclas cercanas y se elige el que empareja la racha entera.
Añade los pares nuevos a data/vanilla_pairs_code.json"""
import json, os, sys, bisect
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from rom import *
import pair_code as pc

HERE = os.path.dirname(__file__)
us, es = pc.us, pc.es


def loose(a, b):
    if sorted(pc.CODES.findall(a)) != sorted(pc.CODES.findall(b)):
        return False
    la, lb = len(a), len(b)
    return la < 12 or 0.3 <= lb / la <= 3.0


def text_runs(b):
    w = np.frombuffer(b[:len(b) // 4 * 4], dtype='<u4')
    cand = np.nonzero((w >= ROM_BASE) & (w < ROM_BASE + len(b)))[0]
    txt = {}
    for i in cand:
        t = int(w[i]) - ROM_BASE
        s = pc.text_ok(b, t)
        if s is not None:
            txt[int(i) * 4] = (t, s)
    locs = sorted(txt)
    runs = []
    cur = [locs[0]]
    for x in locs[1:]:
        if x - cur[-1] <= 8:
            cur.append(x)
        else:
            runs.append(cur); cur = [x]
    runs.append(cur)
    return txt, runs


def main():
    A = pc.anchors()
    etxt, eruns = text_runs(es)
    eruns6 = [r for r in eruns if len(r) >= 6]
    au = [a for a, _ in A]
    w = np.frombuffer(us, dtype='<u4')
    cand = np.nonzero((w >= ROM_BASE) & (w < ROM_BASE + len(us)))[0]
    txt = {}
    for i in cand:
        t = int(w[i]) - ROM_BASE
        s = pc.text_ok(us, t)
        if s is not None:
            txt[int(i) * 4] = (t, s)
    # rachas de punteros consecutivos (se permiten huecos de 1 palabra no-texto)
    locs = sorted(txt)
    runs = []
    cur = [locs[0]]
    for x in locs[1:]:
        if x - cur[-1] <= 8:
            cur.append(x)
        else:
            runs.append(cur); cur = [x]
    runs.append(cur)
    out = json.load(open(os.path.join(HERE, '../data/vanilla_pairs_code.json'), encoding='utf8'))
    new = 0
    for run in runs:
        if len(run) < 3:
            continue
        k = bisect.bisect_right(au, run[0]) - 1
        deltas = set()
        for j in range(max(0, k - 3), min(len(A), k + 5)):
            deltas.add(A[j][1] - A[j][0])
        best = None
        for d in deltas:
            ok = []
            for x in run:
                y = x + d
                if y < 0 or y + 4 > len(es):
                    continue
                v = u32(es, y)
                se = pc.text_ok(es, v - ROM_BASE) if is_ptr(v, len(es)) else None
                if se is not None and pc.compatible(txt[x][1], se):
                    ok.append((x, se))
            if best is None or len(ok) > len(best):
                best = ok
        if (not best or len(best) < 0.8 * len(run)) and len(run) >= 6:
            # búsqueda global: rachas españolas alineadas por su primer puntero
            for r in eruns6:
                d = r[0] - run[0]
                pre = [x for x in run[:6] if x + d in etxt]
                if sum(loose(txt[x][1], etxt[x + d][1]) for x in pre) < 5:
                    continue
                ok = [(x, etxt[x + d][1]) for x in run
                      if x + d in etxt and loose(txt[x][1], etxt[x + d][1])]
                if len(ok) >= 0.8 * len(run) and (best is None or len(ok) > len(best)):
                    best = ok
        if not best or len(best) < 0.8 * len(run):
            continue
        for x, se in best:
            t, su = txt[x]
            key = '%07X' % t
            if key not in out:
                out[key] = [su, se]
                new += 1
    print('pares nuevos', new)
    # correcciones manuales (pares mal emparejados): data/pares_ajustes.json
    aj = json.load(open(os.path.join(HERE, '../data/pares_ajustes.json'), encoding='utf8'))
    for k in aj['descartar']:
        out.pop(k, None)
    out.update(aj['fijar'])
    json.dump(dict(sorted(out.items())), open(os.path.join(HERE, '../data/vanilla_pairs_code.json'), 'w',
                                             encoding='utf8'), ensure_ascii=False, indent=0)


if __name__ == '__main__':
    main()
