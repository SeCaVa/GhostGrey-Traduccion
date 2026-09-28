"""Aplica ../GhostGrey_ES.bps a la ROM USA (igual que RomPatcher.js) y deja la ROM parcheada en
../GhostGrey_ES.gba, comprobando los CRC de origen, destino y del propio parche."""
import os, sys, zlib
sys.path.insert(0, os.path.dirname(__file__))
from bps import apply

ROOT = os.path.join(os.path.dirname(__file__), '..', '..')
usa = open(os.path.join(ROOT, 'Pokemon - FireRed Version (USA).gba'), 'rb').read()
patch = open(os.path.join(ROOT, 'GhostGrey_ES.bps'), 'rb').read()
assert zlib.crc32(usa) == int.from_bytes(patch[-12:-8], 'little'), 'la ROM de origen no es la USA 1.0'
assert zlib.crc32(patch[:-4]) == int.from_bytes(patch[-4:], 'little'), 'parche dañado'
out = apply(usa, patch)
dst = os.path.join(ROOT, 'GhostGrey_ES.gba')
open(dst, 'wb').write(out)
print('ROM parcheada:', os.path.abspath(dst), len(out) // 1024, 'KB  CRC32 %08X' % zlib.crc32(out))
