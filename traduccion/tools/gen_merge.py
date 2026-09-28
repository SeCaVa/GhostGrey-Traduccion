"""Aplica propuestas de género (### ID + texto en una línea) sobre data/trad/*.txt.
Las entradas con el efecto de las "r" (cabecera '### ID r') no se tocan: se listan para hacerlas a mano."""
import sys, glob, os
BS = chr(92)


def parse(path):
    out = {}; cur = None
    for line in open(path, encoding='utf8').read().split('\n'):
        if line.startswith('### '):
            cur = line[4:].strip()
        elif cur and line.strip():
            out[cur] = line.strip(); cur = None
    return out


def main(paths):
    props = {}
    for p in paths:
        props.update(parse(p))
    hechos = set(); manual = []
    for f in sorted(glob.glob('data/trad/*.txt')):
        L = open(f, encoding='utf8').read().split('\n')
        out = []; i = 0; changed = False
        while i < len(L):
            line = L[i]
            parts = line[4:].split() if line.startswith('### ') else []
            if parts and parts[0] in props and parts[0] not in hechos:
                if 'r' in parts[1:]:
                    manual.append(parts[0]); out.append(line); i += 1; continue
                out.append(line)
                j = i + 1
                while j < len(L) and not L[j].startswith('### ') and L[j].strip():
                    j += 1
                out.append(props[parts[0]])
                hechos.add(parts[0]); changed = True
                i = j
                continue
            out.append(line); i += 1
        if changed:
            open(f, 'w', encoding='utf8').write('\n'.join(out))
    print('aplicadas', len(hechos), 'de', len(props))
    print('a mano (efecto r):', manual)
    print('no encontradas:', sorted(set(props) - hechos - set(manual)))


if __name__ == '__main__':
    main(sys.argv[1:])
