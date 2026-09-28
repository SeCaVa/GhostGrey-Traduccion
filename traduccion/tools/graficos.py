"""Busca gráficos comprimidos (LZ77, cabecera 0x10) apuntados desde la ROM USA cuyo equivalente en la
ROM española es distinto (gráficos con texto traducido) y comprueba si el hack los conserva sin cambios.
Salida: data/graficos.json con [dir_puntero_hack, dir_US, dir_ES, tamaño, estado]."""
import json, os, sys, bisect
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from rom import *
import pair_code as pc

ROOT = os.path.join(os.path.dirname(__file__), '..')


def lz77(b, a):
    """Descomprime LZ77 GBA en a; devuelve bytes o None."""
    if a < 0 or a + 4 > len(b) or b[a] != 0x10:
        return None
    size = b[a + 1] | b[a + 2] << 8 | b[a + 3] << 16
    if size == 0 or size > 0x40000 or size % 4:
        return None
    out = bytearray(); p = a + 4
    try:
        while len(out) < size:
            flags = b[p]; p += 1
            for k in range(8):
                if len(out) >= size:
                    break
                if flags & (0x80 >> k):
                    x = b[p] << 8 | b[p + 1]; p += 2
                    n = (x >> 12) + 3; d = (x & 0xFFF) + 1
                    if d > len(out):
                        return None
                    for _ in range(n):
                        out.append(out[-d])
                else:
                    out.append(b[p]); p += 1
    except IndexError:
        return None
    return bytes(out[:size])


def main():
    us, es = pc.us, pc.es
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    A = pc.anchors(); au = [a for a, _ in A]
    w = np.frombuffer(us, dtype='<u4')
    cand = np.nonzero((w >= ROM_BASE) & (w < ROM_BASE + len(us)))[0]
    res = {}
    cache = {}
    for i in cand:
        x = int(i) * 4
        t = int(w[i]) - ROM_BASE
        if us[t] != 0x10:
            continue
        if t not in cache:
            cache[t] = lz77(us, t)
        du = cache[t]
        if du is None or len(du) < 64:
            continue
        k = bisect.bisect_right(au, x) - 1
        if k < 0:
            continue
        best = None
        for j in range(max(0, k - 2), min(len(A), k + 3)):
            y = x + A[j][1] - A[j][0]
            if 0 <= y < len(es) - 4:
                v = u32(es, y) - ROM_BASE
                if 0 <= v < len(es) and es[v] == 0x10:
                    de = lz77(es, v)
                    if de is not None and len(de) == len(du):
                        best = v; break
        if best is None:
            continue
        de = lz77(es, best)
        if de == du:
            continue
        # ¿qué tiene el hack en ese puntero?
        hv = u32(h, x) - ROM_BASE
        dh = lz77(h, hv) if 0 <= hv < len(h) else None
        if dh == du:
            st = 'igual_que_USA'
        elif dh is None:
            st = 'cambiado_sin_LZ'
        else:
            st = 'modificado_por_hack'
        res.setdefault(t, {'us': '%07X' % t, 'es': '%07X' % best, 'size': len(du), 'estado': st, 'punteros': []})
        res[t]['punteros'].append('%07X' % x)
    out = sorted(res.values(), key=lambda r: r['us'])
    json.dump(out, open(os.path.join(ROOT, 'data/graficos.json'), 'w'), indent=1)
    from collections import Counter
    print(len(out), Counter(r['estado'] for r in out))


if __name__ == '__main__':
    main()


def lz77_end(b, a):
    """Devuelve la dirección donde termina el bloque LZ77 comprimido que empieza en a."""
    size = b[a + 1] | b[a + 2] << 8 | b[a + 3] << 16
    n = 0; p = a + 4
    while n < size:
        flags = b[p]; p += 1
        for k in range(8):
            if n >= size:
                break
            if flags & (0x80 >> k):
                x = b[p] << 8 | b[p + 1]; p += 2
                n += (x >> 12) + 3
            else:
                p += 1; n += 1
    return p


def lz77_comp(data):
    """Compresor LZ77 GBA (cabecera 0x10), compatible con descompresión en VRAM (distancia >= 2)."""
    out = bytearray([0x10, len(data) & 0xFF, len(data) >> 8 & 0xFF, len(data) >> 16 & 0xFF])
    i = 0; n = len(data)
    while i < n:
        flagpos = len(out); out.append(0); flags = 0
        for k in range(8):
            if i >= n:
                break
            best_l = 0; best_d = 0
            lo = max(0, i - 4096)
            for j in range(i - 2, lo - 1, -1):
                l = 0
                while l < 18 and i + l < n and data[j + l] == data[i + l]:
                    l += 1
                if l > best_l:
                    best_l, best_d = l, i - j
                    if l == 18:
                        break
            if best_l >= 3:
                flags |= 0x80 >> k
                x = (best_l - 3) << 12 | (best_d - 1)
                out += bytes([x >> 8, x & 0xFF]); i += best_l
            else:
                out.append(data[i]); i += 1
        out[flagpos] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def _px(t):
    return [(t[i // 2] >> (4 * (i & 1))) & 15 for i in range(64)]


def _tile(px):
    return bytes(px[2 * i] | px[2 * i + 1] << 4 for i in range(32))


def recolor(tu, te, th):
    """Si la pieza del hack es la de USA con otros colores (mapa de índices coherente), aplica ese mapa
    a la pieza española. Devuelve la pieza resultante o None."""
    pu, pe, ph = _px(tu), _px(te), _px(th)
    m = {}
    for a, b in zip(pu, ph):
        if m.setdefault(a, b) != b:
            return None
    if any(v not in m for v in pe):
        return None
    return _tile([m[v] for v in pe])


def mezcla(du, de, dh):
    """Pieza a pieza (32 bytes): si el hack no cambió la pieza respecto a USA, se usa la española;
    si solo le cambió los colores, se usa la española con esos colores."""
    out = bytearray(dh)
    cambios = 0; propias = []
    for t in range(len(dh) // 32):
        s = slice(t * 32, t * 32 + 32)
        if t * 32 + 32 > len(du) or de[s] == du[s]:
            if dh[s] != du[s]:
                propias.append(t)
            continue
        if dh[s] == du[s]:
            out[s] = de[s]; cambios += 1
            continue
        r = recolor(du[s], de[s], dh[s])
        if r is not None:
            out[s] = r; cambios += 1
        else:
            propias.append(t)
    return bytes(out), cambios, propias
