"""Aplicar y generar parches BPS.
make_bps reutiliza el parche original de Ghost Grey: decodifica sus comandos y sólo sustituye
por TargetRead los tramos cuya salida cambia, así el parche resultante es compacto."""
import os, zlib
import numpy as np

HERE = os.path.dirname(__file__)
ORIG_PATCH = os.path.join(HERE, '../../GhostGrey.bps')


def _reader(p, pos):
    data = 0; shift = 1
    while True:
        x = p[pos]; pos += 1
        data += (x & 0x7f) * shift
        if x & 0x80:
            return data, pos
        shift <<= 7; data += shift


def _num(n):
    out = bytearray()
    while True:
        x = n & 0x7f; n >>= 7
        if n == 0:
            out.append(0x80 | x); return bytes(out)
        out.append(x); n -= 1


def parse(patch):
    """Devuelve (tamaño_origen, tamaño_destino, lista de ops) con ops = (tipo, inicio_salida, longitud, dato)
    tipo 0 SourceRead, 1 TargetRead (dato=offset en el parche), 2 SourceCopy (dato=offset abs), 3 TargetCopy."""
    assert patch[:4] == b'BPS1'
    pos = 4
    ss, pos = _reader(patch, pos); ts, pos = _reader(patch, pos); ms, pos = _reader(patch, pos)
    pos += ms
    ops = []; op = 0; srel = 0; trel = 0; end = len(patch) - 12
    while pos < end:
        d, pos = _reader(patch, pos)
        cmd = d & 3; ln = (d >> 2) + 1
        if cmd == 0:
            ops.append((0, op, ln, op))
        elif cmd == 1:
            ops.append((1, op, ln, pos)); pos += ln
        elif cmd == 2:
            o, pos = _reader(patch, pos); srel += (-1 if o & 1 else 1) * (o >> 1)
            ops.append((2, op, ln, srel)); srel += ln
        else:
            o, pos = _reader(patch, pos); trel += (-1 if o & 1 else 1) * (o >> 1)
            ops.append((3, op, ln, trel)); trel += ln
        op += ln
    return ss, ts, ops


def apply(src, patch):
    ss, ts, ops = parse(patch)
    out = bytearray(ts)
    for t, o, ln, a in ops:
        if t == 0: out[o:o + ln] = src[o:o + ln]
        elif t == 1: out[o:o + ln] = patch[a:a + ln]
        elif t == 2: out[o:o + ln] = src[a:a + ln]
        else:
            for k in range(ln): out[o + k] = out[a + k]
    assert zlib.crc32(out) == int.from_bytes(patch[-8:-4], 'little'), 'CRC de destino incorrecto'
    return bytes(out)


def make_bps(src, tgt, orig=None):
    orig = orig or open(ORIG_PATCH, 'rb').read()
    ss, ts, ops = parse(orig)
    assert ss == len(src) and ts == len(tgt)
    S = np.frombuffer(src, dtype=np.uint8)
    D = np.frombuffer(tgt, dtype=np.uint8)
    # nuevas ops: (tipo, inicio, long, dato_abs)
    new = []

    def push(t, o, ln, a):
        if t == 1 and new and new[-1][0] == 1 and new[-1][1] + new[-1][2] == o:
            p = new.pop(); new.append((1, p[1], p[2] + ln, None))
        else:
            new.append((t, o, ln, a))

    for t, o, ln, a in ops:
        want = D[o:o + ln]
        if t == 1:
            push(1, o, ln, None); continue
        # TargetCopy lee del destino ya escrito, que siempre coincide con el destino final
        got = S[a:a + ln] if t in (0, 2) else D[a:a + ln]
        diff = got != want
        if not diff.any():
            push(t, o, ln, a); continue
        # dividir en tramos iguales / distintos
        idx = np.flatnonzero(np.diff(diff.astype(np.int8))) + 1
        bounds = [0] + idx.tolist() + [ln]
        for i in range(len(bounds) - 1):
            b0, b1 = bounds[i], bounds[i + 1]
            if diff[b0] or b1 - b0 < 8:
                push(1, o + b0, b1 - b0, None)
            else:
                push(t, o + b0, b1 - b0, a + b0)

    out = bytearray(b'BPS1') + _num(len(src)) + _num(len(tgt)) + _num(0)
    srel = trel = 0
    for t, o, ln, a in new:
        out += _num(((ln - 1) << 2) | t)
        if t == 1:
            out += tgt[o:o + ln]
        elif t == 2:
            d = a - srel; out += _num((abs(d) << 1) | (d < 0)); srel = a + ln
        elif t == 3:
            d = a - trel; out += _num((abs(d) << 1) | (d < 0)); trel = a + ln
    out += zlib.crc32(src).to_bytes(4, 'little') + zlib.crc32(tgt).to_bytes(4, 'little')
    out += zlib.crc32(out).to_bytes(4, 'little')
    return bytes(out)
