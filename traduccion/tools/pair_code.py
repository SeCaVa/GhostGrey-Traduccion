"""Empareja textos USA↔ES referenciados desde código y tablas (punteros alineados).
Se calcula un mapa de direcciones USA→ES con anclas (bloques de bytes idénticos y únicos) y,
para cada puntero USA a un texto, se lee el puntero en la posición equivalente del ROM español.
Salida: data/vanilla_pairs_code.json"""
import json, os, re, sys, bisect
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from rom import *

HERE = os.path.dirname(__file__)
us = open(os.path.join(HERE, '../../Pokemon - FireRed Version (USA).gba'), 'rb').read()
es = open(os.path.join(HERE, '../../Pokemon - Edicion Rojo Fuego (Spain).gba'), 'rb').read()


def keys8(b):
    a = np.frombuffer(b, dtype=np.uint8).astype(np.uint64)
    n = len(b) - 16
    k = np.zeros(n, dtype=np.uint64)
    for j in range(8):
        k |= a[j:j + n] << np.uint64(8 * j)
    k2 = np.zeros(n, dtype=np.uint64)
    for j in range(8):
        k2 |= a[8 + j:8 + j + n] << np.uint64(8 * j)
    return k ^ (k2 * np.uint64(0x9E3779B97F4A7C15))


def anchors():
    ke = keys8(es)
    order = np.argsort(ke, kind='stable')
    ks = ke[order]
    ku = keys8(us)
    pos = np.arange(0, len(us) - 16, 8)
    q = ku[pos]
    lo = np.searchsorted(ks, q, 'left'); hi = np.searchsorted(ks, q, 'right')
    uniq = (hi - lo) == 1
    # descartar bloques de baja entropía
    ua = np.frombuffer(us, dtype=np.uint8)
    good = []
    for p, l, u in zip(pos[uniq], lo[uniq], [True] * int(uniq.sum())):
        blk = ua[p:p + 16]
        if len(np.unique(blk)) < 5:
            continue
        good.append((int(p), int(order[l])))
    return good


def text_ok(b, t):
    if t <= 0 or b[t - 1] not in (0xFF, 0x00):
        return None
    s, _ = decode(b, t)
    if not s or not re.search('[A-Za-zÁÉÍÓÚáéíóúñÑ]{2}', s):
        return None
    return s


CODES = re.compile(r'\{[^}]*\}')


def compatible(a, b):
    """Mismos códigos de sustitución y longitudes razonables."""
    if sorted(CODES.findall(a)) != sorted(CODES.findall(b)):
        return False
    la, lb = len(a), len(b)
    if la >= 12 and not (0.55 <= lb / la <= 2.2):
        return False
    return True


def main():
    A = anchors()
    print('anclas', len(A))
    au = [a for a, _ in A]
    # punteros alineados USA a textos
    w = np.frombuffer(us, dtype='<u4')
    cand = np.nonzero((w >= ROM_BASE) & (w < ROM_BASE + len(us)))[0]
    pairs = {}
    bad = 0
    for i in cand:
        x = int(i) * 4
        t = int(w[i]) - ROM_BASE
        su = text_ok(us, t)
        if su is None:
            continue
        k = bisect.bisect_right(au, x) - 1
        if k < 0 or k + 1 >= len(A):
            continue
        d0 = A[k][1] - A[k][0]; d1 = A[k + 1][1] - A[k + 1][0]
        # sólo zonas con desplazamiento coherente y anclas cercanas
        if d0 != d1 or A[k + 1][0] - A[k][0] > 1024:
            bad += 1
            continue
        y = x + d0
        v = u32(es, y) if y + 4 <= len(es) else 0
        se = text_ok(es, v - ROM_BASE) if is_ptr(v, len(es)) else None
        if se is None or not compatible(su, se):
            bad += 1
            continue
        pairs.setdefault(t, set()).add(se)
    out = {}
    amb = 0
    for t, ss in pairs.items():
        if len(ss) == 1:
            out['%07X' % t] = [decode(us, t)[0], ss.pop()]
        else:
            amb += 1
    print('pares', len(out), 'ambiguos', amb, 'sin pareja', bad)
    json.dump(dict(sorted(out.items())), open(os.path.join(HERE, '../data/vanilla_pairs_code.json'), 'w',
                                             encoding='utf8'), ensure_ascii=False, indent=0)


if __name__ == '__main__':
    main()
