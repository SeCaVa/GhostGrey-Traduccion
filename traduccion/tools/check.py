"""Comprueba el ancho de las líneas de un texto: python tools/check.py ID "texto español" """
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from spanish import Wrapper, MAX_W, BS
ROOT = os.path.join(os.path.dirname(__file__), '..')
rom = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
wr = Wrapper(rom)
inv = {e['id']: e for e in json.load(open(os.path.join(ROOT, 'data/inventory.json'), encoding='utf8'))}
e = inv[sys.argv[1].upper().zfill(7)]
lines = e['en'].split(chr(10))
lim = max(wr.width(x) for x in lines) + 4 if len(lines) >= 3 else MAX_W
print('límite', lim)
txt = sys.argv[2].replace('|', chr(10)) if len(sys.argv) > 2 else e['en']
for ln in txt.split(chr(10)):
    print('%4d %s %s' % (wr.width(ln), '!!' if wr.width(ln) > lim else '  ', ln))
