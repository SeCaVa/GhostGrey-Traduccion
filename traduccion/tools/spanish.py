"""Ajustes de texto en español: estilo de mayúsculas y cortes de línea según la fuente del hack."""
import re
from rom import encode, FC_ARGS

FONT_TABLE = 0x1FB100      # tabla de anchos de la fuente normal del hack
MAX_W = 208                # ancho útil del cuadro de diálogo (px)
BS = '\\'

# ancho estimado de los códigos de sustitución {Bxx}
VAR_W = {0x01: 42, 0x06: 42, 0x02: 60, 0x03: 60, 0x04: 60,
         0x05: 6, 0x08: 6, 0x09: 11, 0x0A: 18, 0x0B: 6, 0x0C: 22, 0x0D: 19}  # 5, 8-13: terminaciones de género

# palabras en mayúsculas del texto oficial que se mantienen así
KEEP_UPPER = {'PC', 'MT', 'MO', 'PP', 'PS', 'OK', 'TV', 'ID', 'KO', 'S.S.', 'EV', 'EXP', 'VS',
              'HM', 'TM', 'EE', 'UU', 'DJ', 'RPG', 'UFO', 'CD', 'PK', 'MN', 'I', 'II', 'III', 'IV',
              'V', 'VI', 'VII', 'VIII', 'IX', 'X', 'XI', 'XII', 'ADN', 'NPC', 'S.S', 'S.A'}

_UP = 'A-ZÁÉÍÓÚÑÜÀÈÌÒÙÇ'
_WORD = re.compile(r"[%s][%sé\.]*[%sé]|[%s]" % (_UP, _UP, _UP, _UP))


MINOR = {'de', 'del', 'la', 'el', 'los', 'las', 'y', 'e', 'a', 'al', 'en', 'con', 'para', 'por', 'o', 'u'}
SPECIAL = {'MT. MOON': 'Mt. Moon', 'S.S. ANNE': 'S.S. Anne', 'S.A.': 'S.A.', 'LT. SURGE': 'Lt. Surge',
           'POKéMON': 'Pokémon', 'POKé BALL': 'Poké Ball', 'POKéDEX': 'Pokédex', 'POKé': 'Poké'}


# primeras palabras de nombres propios (lugares, edificios): se escriben con mayúscula inicial
TITLE_START = {'CIUDAD', 'PUEBLO', 'RUTA', 'ISLA', 'CUEVA', 'BOSQUE', 'TORRE', 'CALLE', 'ZONA', 'TÚNEL',
               'GIMNASIO', 'GIM.', 'MT.', 'MUSEO', 'CABO', 'BALNEARIO', 'CAMINO', 'RUINAS', 'CÁMARA',
               'LLAVE', 'ROCA', 'CENTRAL', 'CASA', 'DOJO', 'TIENDA', 'CENTRO', 'LABORATORIO', 'MANSIÓN',
               'SILPH', 'TEAM', 'ALTO', 'MEDALLA', 'MED.', 'BAYA', 'CC', 'CASINO', 'VALLE', 'PLAYA',
               'MONTE', 'PUERTO', 'FARO', 'PASO', 'ALDEA', 'GRUTA', 'ACANTILADO', 'LAGO', 'POKéMON',
               'HALL', 'SALA', 'CLUB', 'MINA', 'PUENTE', 'CARRIL', 'CABAÑA', 'ANTIGUA'}


def sentence_case(s):
    low = s.lower()
    for i, ch in enumerate(low):
        if ch.isalpha():
            return low[:i] + ch.upper() + low[i + 1:]
    return low


def decap(s):
    """Convierte palabras en MAYÚSCULAS del texto oficial al estilo del hack (Ciudad Celeste, Pokémon)."""
    plain = re.sub(r'\{[^}]*\}', '', s)
    words = plain.split()
    # frase entera en mayúsculas que no es un nombre propio: tipo oración (¿Cómo te llamas?)
    if words and not any(c.islower() for c in plain.replace('é', '')) and len(words) > 1             and words[0].lstrip('¿¡') not in TITLE_START:
        out = sentence_case(s)
        for k, v in SPECIAL.items():
            out = out.replace(k.lower(), v)
        return re.sub(r'\{[^}]*\}', lambda m: m.group(0).upper(), out)
    for k, v in SPECIAL.items():
        s = s.replace(k, v)

    def fix(m):
        w = m.group(0)
        core = w.rstrip('.')
        if core in KEEP_UPPER or w in KEEP_UPPER or len(core) < 2:
            return w
        low = w.lower()
        # preposiciones y artículos dentro de nombres propios en mayúsculas: en minúscula
        start = m.start()
        prev = m.string[:start].rstrip()
        if low in MINOR and prev and prev[-1].isalpha():
            return low
        return low[0].upper() + low[1:]
    # no tocar los códigos {..}
    parts = re.split(r'(\{[^}]*\})', s)
    return ''.join(p if p.startswith('{') else _WORD.sub(fix, p) for p in parts)


class Wrapper:
    def __init__(self, rom):
        self.W = rom[FONT_TABLE:FONT_TABLE + 256]

    def width(self, text):
        b = encode(text)[:-1]
        w = i = 0
        while i < len(b):
            c = b[i]
            if c == 0xFD:
                w += VAR_W.get(b[i + 1], 60); i += 2
            elif c == 0xFC:
                i += 2 + FC_ARGS[b[i + 1]]
            else:
                w += self.W[c]; i += 1
        return w

    def wrap(self, text, maxw=MAX_W):
        """Recorta cada párrafo (separado por \\p) en líneas: la 1ª ruptura es \\n, las siguientes \\l.
        Un salto '\\n' escrito a mano se respeta como ruptura forzada."""
        out = []
        for para in text.split(BS + 'p'):
            lines = []
            for chunk in re.split(r'\n|' + re.escape(BS + 'n') + '|' + re.escape(BS + 'l'), para):
                words = chunk.split(' ')
                cur = ''
                for wd in words:
                    cand = wd if not cur else cur + ' ' + wd
                    if cur and self.width(cand) > maxw:
                        lines.append(cur)
                        cur = wd
                    else:
                        cur = cand
                lines.append(cur)
            s = ''
            for k, ln in enumerate(lines):
                if k == 0:
                    s = ln
                elif k == 1:
                    s += '\n' + ln
                else:
                    s += BS + 'l' + ln
            out.append(s)
        return (BS + 'p').join(out)

    def too_wide(self, text, maxw=MAX_W):
        bad = []
        for ln in re.split(r'\n|' + re.escape(BS + 'l') + '|' + re.escape(BS + 'p'), text):
            if self.width(ln) > maxw:
                bad.append(ln)
        return bad


def r_effect(t):
    """Efecto de la secta de los bichos: un espacio antes de cada 'r' que no empiece palabra."""
    out = []
    for i, ch in enumerate(t):
        if ch in 'rR' and i > 0 and t[i - 1] not in (' ', '{', chr(92), chr(10)):
            out.append(' ')
        out.append(ch)
    return ''.join(out)
