"""Código C de la traducción (carpeta codigo/), compilado a un bloque en una dirección fija de la ROM:
  intro.c    pantallas de crédito de la traducción ('SeCaVa' y 'Traducido por SeCaVa') con el jingle de campanas,
             las mismas que en la traducción de Emerald Rogue. Salen al acabar la escena del logo del creador del
             hack (la del logo de GAME FREAK en FireRed), antes de la escena del combate. B se las salta;
             A/START/SELECT se saltan toda la intro, como en el juego original.
  clases.c   clase de entrenador en femenino según el sprite ("Jardinera"), tabla en data/tablas/clases_femeninas.tsv.

  python tools/codigo_c.py extraer    copia gráficos y jingle del proyecto de Emerald Rogue a codigo/
  python tools/codigo_c.py            compila codigo/ (arm-none-eabi-gcc de WSL) -> data/codigo.bin y data/codigo.json

build.py mete data/codigo.bin en su dirección fija y aplica los ganchos de data/codigo.json, así que para compilar la
traducción no hace falta nada de esto: solo para cambiar el código.

extraer necesita, junto a la carpeta ghostgrey, el proyecto emeraldrogue con:
  src/graphics/intro/traduccion{,2}.png/.bin   pantallas de 240x160 a 16 colores (tools/gfx_traduccion.py de allí)
  emeraldrogue_ex_es.gba                       compilada con el jingle (sound/songs/midi/mus_traduccion.mid); la
                                               dirección de la canción (CANCION) sale de pokeemerald.map."""
import json, os, shutil, struct, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..'))
INTRO = os.path.join(ROOT, 'codigo')
ROGUE = os.path.normpath(os.path.join(ROOT, '..', '..', 'emeraldrogue'))

DIR = 0x1F00000                  # dirección fija del bloque en la ROM (build.py deja libre desde aquí)
TAM_MAX = 0x20000                # desde DIR + TAM_MAX, datos que escribe build.py (clases femeninas)
FUENTES = 'intro.c clases.c graficos.s cancion.s'
# punteros de la ROM que pasan a apuntar a funciones del bloque: (dirección, valor original, función)
GANCHOS = [(0x0ECEA0, 0x080ECEA5, 'IntroCB_Traduccion'),      # IntroCB_GF_RevealLogo -> IntroCB_Scene1
           (0x0D809C, 0x0823EAC8, 'NombreClaseEntrenador')]   # literal de gTrainers en B_TXT_TRAINER1_CLASS
# código de la ROM que se cambia: BufferStringBattle, B_TXT_TRAINER1_CLASS (0x080D8084), en vez de
# gTrainerClassNames[gTrainers[id].trainerClass] llama a NombreClaseEntrenador(id):
#   ldrh r0,[r3] / ldr r1,=NombreClaseEntrenador (literal 0x0D809C) / bl _call_via_r1 / adds r4,r0,#0 / b 0x080D8382
PARCHES = [(0x0D8084, '054a198888004018c0008018', '188805490bf190fd041c78e1',
            'B_TXT_TRAINER1_CLASS: nombre de clase por NombreClaseEntrenador')]

# jingle en la ROM de Emerald Rogue (pokeemerald.map: mus_traduccion y su .rodata)
ROGUE_ROM = 'emeraldrogue_ex_es.gba'
CANCION = 0x1DF346C
PROGRAMAS = (9, 11, 14, 28, 48)  # VOICE que usan las pistas


def u32(b, a):
    return struct.unpack_from('<I', b, a)[0]


def gbapal(im):
    p = im.getpalette()[:48]
    p += [0] * (48 - len(p))
    return b''.join(struct.pack('<H', (p[i] >> 3) | (p[i + 1] >> 3) << 5 | (p[i + 2] >> 3) << 10)
                    for i in range(0, 48, 3))


def tiles4bpp(im, n):
    px = im.load()
    w = im.size[0] // 8
    out = bytearray()
    for t in range(n):
        x0, y0 = t % w * 8, t // w * 8
        for y in range(8):
            for x in range(0, 8, 2):
                out.append((px[x0 + x, y0 + y] & 15) | (px[x0 + x + 1, y0 + y] & 15) << 4)
    return bytes(out)


def extraer_graficos():
    for src, dst in (('traduccion', 'pantalla1'), ('traduccion2', 'pantalla2')):
        base = os.path.join(ROGUE, 'src', 'graphics', 'intro', src)
        im = Image.open(base + '.png')
        assert im.mode == 'P'
        mapa = open(base + '.bin', 'rb').read()
        n = max(e & 0x3FF for e in struct.unpack('<1024H', mapa)) + 1
        open(os.path.join(INTRO, dst + '.4bpp'), 'wb').write(tiles4bpp(im, n))
        open(os.path.join(INTRO, dst + '.gbapal'), 'wb').write(gbapal(im))
        open(os.path.join(INTRO, dst + '.bin'), 'wb').write(mapa)
        print(dst, n, 'teselas')


def extraer_jingle():
    rom = open(os.path.join(ROGUE, ROGUE_ROM), 'rb').read()
    ntr = rom[CANCION]
    vg = u32(rom, CANCION + 4) - 0x8000000
    pistas = [u32(rom, CANCION + 8 + 4 * i) - 0x8000000 for i in range(ntr)]
    lim = pistas[1:] + [CANCION]
    os.makedirs(os.path.join(INTRO, 'muestras'), exist_ok=True)
    s = ['@ Generado por tools/codigo_c.py extraer: jingle de la traducción (mus_traduccion de Emerald Rogue,',
         '@ voicegroup191 de DPPt). Las pistas solo usan FINE, TEMPO, KEYSH, VOICE, VOL, EOT, notas y esperas.',
         '\t.section .rodata', '\t.align 2', '\t.global mus_traduccion', 'mus_traduccion:',
         '\t.byte %d, %d, %d, %d' % tuple(rom[CANCION:CANCION + 4]), '\t.word voces']
    s += ['\t.word pista%d' % i for i in range(ntr)]
    for i, (a, b) in enumerate(zip(pistas, lim)):
        datos = rom[a:b]
        assert not any(0xB2 <= c <= 0xB5 for c in datos), 'la pista %d tiene saltos (habría que reubicarlos)' % i
        s.append('pista%d:' % i)
        s += ['\t.byte ' + ', '.join('0x%02X' % c for c in datos[k:k + 16]) for k in range(0, len(datos), 16)]
    muestras = {}

    def muestra(p):
        a = p - 0x8000000
        if a not in muestras:
            tam = u32(rom, a + 12) + 16
            nombre = 'm%07X' % a
            open(os.path.join(INTRO, 'muestras', nombre + '.bin'), 'wb').write(rom[a:a + tam])
            muestras[a] = nombre
        return muestras[a]

    def voz(e, etiqueta):
        assert e[0] in (0x00, 0x08), 'tipo de voz %02X' % e[0]
        return ['\t.byte 0x%02X, 0x%02X, 0x%02X, 0x%02X' % tuple(e[:4]),
                '\t.word %s' % muestra(u32(e, 4)),
                '\t.byte 0x%02X, 0x%02X, 0x%02X, 0x%02X   @ %s' % (tuple(e[8:12]) + (etiqueta,))]

    s += ['\t.align 2', 'voces:']
    extra = []
    for p in range(max(PROGRAMAS) + 1):
        q = p if p in PROGRAMAS else PROGRAMAS[0]     # los programas que no se usan repiten el primero
        e = rom[vg + 12 * q: vg + 12 * q + 12]
        if e[0] == 0x40:
            sub, tabla = u32(e, 4) - 0x8000000, u32(e, 8) - 0x8000000
            if p == q:
                t = rom[tabla:tabla + 128]
                extra += ['\t.align 2', 'sub%d:' % p]
                for k in range(max(t) + 1):
                    extra += voz(rom[sub + 12 * k: sub + 12 * k + 12], 'programa %d, zona %d' % (p, k))
                extra += ['tabla%d:' % p] + ['\t.byte ' + ', '.join(str(c) for c in t[k:k + 16])
                                             for k in range(0, 128, 16)]
            s += ['\t.byte 0x40, 0, 0, 0', '\t.word sub%d, tabla%d   @ programa %d' % (q, q, p)]
        else:
            s += voz(e, 'programa %d' % p)
    s += extra
    for a, nombre in sorted(muestras.items()):
        s += ['\t.align 2', '%s:' % nombre, '\t.incbin "muestras/%s.bin"' % nombre]
    open(os.path.join(INTRO, 'cancion.s'), 'w', newline='\n').write('\n'.join(s) + '\n')
    print('jingle:', ntr, 'pistas,', len(muestras), 'muestras,',
          sum(os.path.getsize(os.path.join(INTRO, 'muestras', n + '.bin')) for n in muestras.values()), 'bytes')


def wsl(ruta):
    ruta = os.path.abspath(ruta).replace('\\', '/')
    return '/mnt/%s%s' % (ruta[0].lower(), ruta[2:])


def compilar():
    cmd = ('cd "%s" && arm-none-eabi-gcc -mthumb -mcpu=arm7tdmi -Os -mlong-calls -ffreestanding -fno-builtin '
           '-nostartfiles -Wall -Wextra -T codigo.ld -Wl,--no-warn-rwx-segments -o codigo.elf %s -lgcc '
           '&& arm-none-eabi-objcopy -O binary codigo.elf codigo.bin && arm-none-eabi-nm codigo.elf'
           % (wsl(INTRO), FUENTES))
    r = subprocess.run(['wsl', '-e', 'bash', '-lc', cmd], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)
    simbolos = {l.split()[2]: int(l.split()[0], 16) for l in r.stdout.splitlines() if len(l.split()) == 3}
    blob = open(os.path.join(INTRO, 'codigo.bin'), 'rb').read()
    assert len(blob) <= TAM_MAX, 'el bloque no cabe antes de la tabla de clases femeninas'
    ganchos = []
    for a, orig, f in GANCHOS:
        v = simbolos[f]
        assert v & 1 == 0 and 0x8000000 + DIR <= v < 0x8000000 + DIR + len(blob), f
        ganchos.append({'addr': '%07X' % a, 'orig': '%08X' % orig, 'new': '%08X' % (v | 1), 'nota': f})
    shutil.move(os.path.join(INTRO, 'codigo.bin'), os.path.join(ROOT, 'data', 'codigo.bin'))
    os.remove(os.path.join(INTRO, 'codigo.elf'))
    info = {'dir': '%07X' % DIR, 'clases_femeninas': '%07X' % (DIR + TAM_MAX), 'ganchos': ganchos,
            'parches': [{'addr': '%07X' % a, 'orig': o, 'new': n, 'nota': t} for a, o, n, t in PARCHES]}
    json.dump(info, open(os.path.join(ROOT, 'data', 'codigo.json'), 'w'), indent=1)
    print('data/codigo.bin: %d bytes en %07X' % (len(blob), DIR))
    for g in ganchos:
        print('  %s -> %s (%s)' % (g['addr'], g['new'], g['nota']))


if __name__ == '__main__':
    if sys.argv[1:] == ['extraer']:
        extraer_graficos()
        extraer_jingle()
    else:
        compilar()
