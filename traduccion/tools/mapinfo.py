"""Muestra warps, NPC, carteles y triggers de un mapa: python tools/mapinfo.py 4.1 [4.0 ...]"""
import os, sys, struct
sys.path.insert(0, os.path.dirname(__file__))
from rom import *
rom = open(os.path.join(os.path.dirname(__file__), '../build/ghostgrey_en.gba'), 'rb').read()
maps = {(g, m): h for g, m, h in iter_maps(rom)}
for arg in sys.argv[1:]:
    g, m = map(int, arg.split('.'))
    h = maps[(g, m)]
    lay = off(u32(rom, h)); w, hh = u32(rom, lay), u32(rom, lay + 4)
    ev = off(u32(rom, h + 4)); no, nw, nc, nb = rom[ev:ev + 4]
    print('== mapa %s  tamaño %dx%d' % (arg, w, hh))
    o = off(u32(rom, ev + 4))
    for i in range(no):
        b = o + 24 * i
        print('  npc%d x=%d y=%d gfx=%d script=%07X flag=%d' % (i + 1, struct.unpack_from('<h', rom, b + 4)[0],
              struct.unpack_from('<h', rom, b + 6)[0], rom[b + 1], u32(rom, b + 16) - ROM_BASE if u32(rom, b + 16) else 0, u16(rom, b + 20)))
    o = off(u32(rom, ev + 8)) if nw else 0
    for i in range(nw):
        b = o + 8 * i
        print('  warp%d x=%d y=%d -> %d.%d warp %d' % (i, u16(rom, b), u16(rom, b + 2), rom[b + 7], rom[b + 6], rom[b + 5]))
    o = off(u32(rom, ev + 12)) if nc else 0
    for i in range(nc):
        b = o + 16 * i
        print('  coord%d x=%d y=%d var=%04X val=%d script=%07X' % (i, u16(rom, b), u16(rom, b + 2), u16(rom, b + 6), u16(rom, b + 8), u32(rom, b + 12) - ROM_BASE))
    o = off(u32(rom, ev + 16)) if nb else 0
    for i in range(nb):
        b = o + 12 * i
        print('  bg%d x=%d y=%d kind=%d' % (i, u16(rom, b), u16(rom, b + 2), rom[b + 5]))
