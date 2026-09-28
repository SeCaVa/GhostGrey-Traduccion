"""Compara las propuestas de género (### ID + texto) con la traducción actual y muestra solo los cambios."""
import sys, json, os, re, difflib
TMP = os.environ['TMP']
todo = {o['id']: o for o in json.load(open(os.path.join(TMP, 'gen/todo.json'), encoding='utf8'))}


def parse(path):
    out = {}; cur = None
    for line in open(path, encoding='utf8').read().split('\n'):
        if line.startswith('### '):
            cur = line[4:].strip()
        elif cur and line.strip():
            out[cur] = line.strip(); cur = None
    return out


def show(path):
    for k, v in parse(path).items():
        if k not in todo:
            print('!! ID desconocido', k); continue
        old = todo[k]['es'].replace('\n', '\n')
        a, b = re.findall(r'\S+|\s', old), re.findall(r'\S+|\s', v)
        sm = difflib.SequenceMatcher(None, a, b)
        ch = [('%s -> %s' % (''.join(a[i1:i2]).strip(), ''.join(b[j1:j2]).strip())) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal']
        print(k, ' | '.join(ch))


if __name__ == '__main__':
    show(sys.argv[1])
