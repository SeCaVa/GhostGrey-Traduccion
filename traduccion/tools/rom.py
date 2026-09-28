"""Utilidades para ROMs de Pokémon Rojo Fuego (GBA): texto, mapas y scripts."""
import struct
from charset import T, CTRL

ROM_BASE = 0x8000000
MAP_GROUPS_PTR = 0x5524C  # literal que apunta a gMapGroups (igual en USA y en el hack)
MAP_GROUPS_PTR_ES = 0x55340  # en el ROM español


def u8(b, a): return b[a]
def u16(b, a): return struct.unpack_from('<H', b, a)[0]
def u32(b, a): return struct.unpack_from('<I', b, a)[0]


def is_ptr(v, size):
    return ROM_BASE <= v < ROM_BASE + size


def off(v): return v - ROM_BASE


# ---------------------------------------------------------------- texto
ENC = {v: k for k, v in T.items()}
ENC.update({'\n': 0xFE, '\\n': 0xFE, '\\l': 0xFA, '\\p': 0xFB})
# argumentos de los códigos 0xFC (según el motor de FR)
FC_ARGS = {0x01: 1, 0x02: 1, 0x03: 1, 0x04: 3, 0x05: 1, 0x06: 1, 0x07: 0, 0x08: 1,
           0x09: 0, 0x0A: 0, 0x0B: 2, 0x0C: 1, 0x0D: 0, 0x0E: 1, 0x0F: 0, 0x10: 2,
           0x11: 1, 0x12: 1, 0x13: 1, 0x14: 1, 0x15: 0, 0x16: 0, 0x17: 0, 0x18: 0}


def decode(b, i, maxlen=4000):
    """Decodifica una cadena terminada en 0xFF. Devuelve (texto, fin) o (None, pos_error)."""
    out = []
    j = i
    while j < len(b) and j - i < maxlen:
        c = b[j]
        if c == 0xFF:
            return ''.join(out), j + 1
        if c in T:
            out.append(T[c]); j += 1
        elif c == 0xFE:
            out.append('\n'); j += 1
        elif c in (0xFA, 0xFB):
            out.append(CTRL[c]); j += 1
        elif c == 0xFD:
            out.append('{B%02X}' % b[j + 1]); j += 2
        elif c == 0xFC:
            n = FC_ARGS.get(b[j + 1])
            if n is None:
                return None, j
            out.append('{C' + b[j + 1:j + 2 + n].hex().upper() + '}'); j += 2 + n
        elif c == 0xF7 or c == 0xF8 or c == 0xF9:
            out.append('{X%02X%02X}' % (c, b[j + 1])); j += 2
        else:
            return None, j
    return None, j


def encode(s):
    out = bytearray()
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == '{':
            k = s.index('}', i)
            tag = s[i + 1:k]
            if tag[0] == 'B':
                out += bytes([0xFD, int(tag[1:], 16)])
            elif tag[0] == 'C':
                out += bytes([0xFC]) + bytes.fromhex(tag[1:])
            elif tag[0] == 'X':
                out += bytes.fromhex(tag[1:])
            elif tag[0] == 'H':  # byte crudo
                out += bytes.fromhex(tag[1:])
            else:
                raise ValueError('etiqueta desconocida ' + tag)
            i = k + 1
            continue
        if ch == '\\':
            out.append(ENC['\\' + s[i + 1]]); i += 2
            continue
        if s.startswith('[Lv]', i): out.append(0x34); i += 4; continue
        if s.startswith('[PK]', i): out.append(0x53); i += 4; continue
        if s.startswith('[MN]', i): out.append(0x54); i += 4; continue
        if ch == "'": ch = '’'
        if ch == '"': raise ValueError('comillas rectas en: ' + s)
        if ch not in ENC:
            raise ValueError('carácter no codificable %r en: %s' % (ch, s))
        out.append(ENC[ch]); i += 1
    out.append(0xFF)
    return bytes(out)


# ---------------------------------------------------------------- scripts
# longitudes de argumentos de cada comando de script de FR (sin contar el opcode)
# Las entradas None son comandos con longitud variable (trainerbattle) o que terminan.
L = {}
def _set(ops, n):
    for o in ops: L[o] = n
_set([0x00, 0x01, 0x02, 0x03, 0x0C, 0x0D, 0x27, 0x2D, 0x2E, 0x30, 0x32, 0x35, 0x43, 0x5A,
      0x5D, 0x5E, 0x5F, 0x66, 0x68, 0x69, 0x6A, 0x6B, 0x6C, 0x6D, 0x72, 0x76, 0x8B, 0x8C,
      0x8D, 0x8E, 0x94, 0xA0, 0xA3, 0xA5, 0xAE, 0xB2, 0xB7, 0xC5, 0xC9, 0xCA, 0xCB, 0xCF], 0)
_set([0x08, 0x09, 0x0E, 0x37, 0x38, 0x77, 0x7E, 0x97, 0x9A, 0xA6, 0xC3, 0xC7], 1)
_set([0x0A, 0x0B, 0x10, 0x14, 0x1B, 0x1C, 0x6E, 0x98, 0xAB, 0xC0, 0xC1, 0xC2], 2)
_set([0x25, 0x28, 0x29, 0x2A, 0x2B, 0x2F, 0x31, 0x34, 0x36, 0x48, 0x4B, 0x4C, 0x4D, 0x4E,
      0x51, 0x53, 0x55, 0x60, 0x61, 0x62, 0x64, 0x7A, 0x7C, 0x89, 0x8F, 0x96, 0x99, 0x9C,
      0x9E, 0x9F, 0xA4, 0xA7, 0xB3, 0xB4, 0xB5, 0xCD, 0xCE, 0xD0], 2)
_set([0x04, 0x05, 0x23, 0x24, 0x67, 0x78, 0x86, 0x87, 0x88, 0x9B, 0xB8, 0xB9, 0xBA, 0xBD,
      0xBE, 0xC8, 0xD3], 4)
_set([0x06, 0x07, 0x0F, 0x11, 0x12, 0x13, 0x1D, 0x1E, 0x1F, 0x90, 0x91, 0x92, 0xBB, 0xBC,
      0xBF, 0x85, 0xCC], 5)
_set([0x16, 0x17, 0x18, 0x19, 0x1A, 0x21, 0x22, 0x26, 0x2C, 0x42, 0x44, 0x45, 0x46, 0x47,
      0x49, 0x4A, 0x52, 0x54, 0x56, 0x58, 0x59, 0x7B, 0xA1, 0xAC, 0xAD, 0xAF, 0xB0], 4)
_set([0x33, 0x7D, 0x7F, 0x80, 0x81, 0x82, 0x83, 0x84, 0x93, 0x95, 0xC6, 0xD2], 3)
L[0x5B] = 3
L[0x9D] = 3
L[0x20] = 8
L[0x15] = 8
L[0x3C] = 2
for o in (0x39, 0x3A, 0x3B, 0x3D, 0x3E, 0x3F, 0x40, 0x41, 0xC4, 0xD1):
    L[o] = 7
L[0x4F] = 6
L[0x50] = 8
L[0x57] = 6
L[0x63] = 6
L[0x65] = 3
L[0x6F] = 4
L[0x70] = 5
L[0x71] = 5
L[0x73] = 4
L[0x74] = 4
L[0x75] = 4
L[0x79] = 14
L[0x8A] = 3
L[0xA2] = 8
L[0xA8] = 5
L[0xA9] = 4
L[0xAA] = 8
L[0xB1] = 7
L[0xB6] = 5
L[0xD4] = 5
L[0x5C] = None  # trainerbattle

# 16 bit: 0x1B y 0x1C son (u8,u8) → 2 ; 0x14 (u8,u8) → 2 ; ya incluidos
END_OPS = {0x02, 0x03, 0x05, 0x08, 0x0D, 0x24, 0x5E, 0x5F, 0xB9}
# opcodes con puntero a script en la posición indicada
SCRIPT_PTR = {0x04: 0, 0x05: 0, 0x06: 1, 0x07: 1}
# opcodes con puntero a texto (posición del puntero dentro de los argumentos)
TEXT_PTR = {0x67: 0, 0x9B: 0, 0x85: 1, 0xC8: 0}  # 0x78/0xD3 son braille: no se traducen
# trainerbattle: lista de campos tras (tipo, trainer, local) según el tipo
TB = {0: 'tt', 1: 'tts', 2: 'tts', 3: 't', 4: 'ttt', 5: 'tt', 6: 'ttts', 7: 'ttt',
      8: 'ttts', 9: 'tt'}


class ScriptWalker:
    """Recorre scripts siguiendo saltos y registra dónde hay punteros a texto."""

    def __init__(self, rom):
        self.rom = rom
        self.visited = set()
        self.text_refs = {}      # offset del campo puntero -> offset del texto
        self.ref_ctx = {}        # offset del campo -> (script raíz, opcode)
        self.errors = []
        self.movement_ptrs = set()
        self.mart_ptrs = set()

    def walk(self, start, root=None):
        rom = self.rom
        stack = [start]
        root = start if root is None else root
        while stack:
            pc = stack.pop()
            while True:
                if pc in self.visited or not (0 <= pc < len(rom)):
                    break
                self.visited.add(pc)
                op = rom[pc]
                if op not in L:
                    self.errors.append((root, pc, op))
                    break
                a = pc + 1
                if op == 0x5C:
                    kind = rom[a]
                    fields = TB.get(kind)
                    if fields is None:
                        self.errors.append((root, pc, 'tb%d' % kind))
                        break
                    q = a + 5
                    for f in fields:
                        v = u32(rom, q)
                        if f == 't' and is_ptr(v, len(rom)):
                            self._text(q, off(v), root, op)
                        elif f == 's' and is_ptr(v, len(rom)):
                            stack.append(off(v))
                        q += 4
                    pc = q
                    continue
                n = L[op]
                if op in SCRIPT_PTR:
                    v = u32(rom, a + SCRIPT_PTR[op])
                    if is_ptr(v, len(rom)):
                        stack.append(off(v))
                elif op in TEXT_PTR:
                    q = a + TEXT_PTR[op]
                    v = u32(rom, q)
                    if is_ptr(v, len(rom)):
                        self._text(q, off(v), root, op)
                elif op == 0x0F:  # loadword idx, valor
                    v = u32(rom, a + 1)
                    if is_ptr(v, len(rom)):
                        # si le sigue callstd o message suele ser texto; se comprueba al decodificar
                        self._text(a + 1, off(v), root, op, weak=True)
                elif op in (0x4F, 0x50):
                    self.movement_ptrs.add(off(u32(rom, a + 2)))
                elif op == 0x86:
                    self.mart_ptrs.add(off(u32(rom, a)))
                elif op in (0xBB, 0xBC):
                    pass
                if op in END_OPS:
                    break
                pc = a + n

    def _text(self, field, target, root, op, weak=False):
        s, _ = decode(self.rom, target)
        if s is None:
            if not weak:
                self.errors.append((root, field, 'text?'))
            return
        self.text_refs[field] = target
        self.ref_ctx[field] = (root, op)


# ---------------------------------------------------------------- mapas
def iter_maps(rom):
    lit = MAP_GROUPS_PTR_ES if rom[0xAF] == ord('S') else MAP_GROUPS_PTR
    groups = off(u32(rom, lit))
    gps = []
    while is_ptr(u32(rom, groups + 4 * len(gps)), len(rom)) and len(gps) < 60:
        gps.append(off(u32(rom, groups + 4 * len(gps))))
    for g, gp in enumerate(gps):
        # el grupo termina donde empieza la siguiente tabla de grupo o el propio índice
        bound = min([x for x in gps + [groups] if x > gp], default=len(rom))
        m = 0
        while gp + 4 * m < bound:
            hp = u32(rom, gp + 4 * m)
            if not is_ptr(hp, len(rom)):
                break
            h = off(hp)
            ev = u32(rom, h + 4)
            if not is_ptr(ev, len(rom)):
                break
            yield g, m, h
            m += 1
            if m > 200:
                break


def map_scripts(rom, h):
    """Devuelve lista de (tipo, offset de script) de un mapa."""
    out = []
    ev = off(u32(rom, h + 4))
    no, nw, nc, nb = rom[ev:ev + 4]
    objs = u32(rom, ev + 4); coords = u32(rom, ev + 12); bgs = u32(rom, ev + 16)
    size = len(rom)
    if no and is_ptr(objs, size):
        for i in range(no):
            v = u32(rom, off(objs) + 24 * i + 16)
            if is_ptr(v, size): out.append(('npc%d' % (i + 1), off(v)))
    if nc and is_ptr(coords, size):
        for i in range(nc):
            v = u32(rom, off(coords) + 16 * i + 12)
            if is_ptr(v, size): out.append(('coord%d' % i, off(v)))
    if nb and is_ptr(bgs, size):
        for i in range(nb):
            base = off(bgs) + 12 * i
            kind = rom[base + 5]
            v = u32(rom, base + 8)
            if kind < 5 and is_ptr(v, size): out.append(('bg%d' % i, off(v)))
    ms = u32(rom, h + 8)
    if is_ptr(ms, size):
        p = off(ms)
        while rom[p] != 0 and p < size:
            t = rom[p]; v = u32(rom, p + 1)
            if is_ptr(v, size):
                if t in (2, 4):
                    q = off(v)
                    while u16(rom, q) != 0:
                        w = u32(rom, q + 4)
                        if is_ptr(w, size): out.append(('ms%d' % t, off(w)))
                        q += 8
                else:
                    out.append(('ms%d' % t, off(v)))
            p += 5
    return out
