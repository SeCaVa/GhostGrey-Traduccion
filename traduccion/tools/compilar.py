"""Compila la traducción de principio a fin.
Uso: python traduccion/tools/compilar.py [--rehacer]

1. build/ghostgrey_en.gba: aplica el parche original del hack (GhostGrey.bps) a Pokémon FireRed USA 1.0.
2. Si faltan (o con --rehacer): empareja los textos USA/ES oficiales y genera el inventario de textos del hack
   (pair_vanilla, pair_code, pair_tables, inventory).
3. build.py: escribe la traducción y genera build/GhostGrey_ES.bps.
4. Copia el parche a la carpeta raíz y lo aplica (parchear.py) para dejar GhostGrey_ES.gba.

En la carpeta raíz (la que contiene traduccion/) tienen que estar:
  Pokemon - FireRed Version (USA).gba            (CRC32 DD88761C)
  Pokemon - Edicion Rojo Fuego (Spain).gba       (CRC32 9F08064E)
  Pokemon - Edicion Roja (Spain) (SGB Enhanced).gb (solo para regenerar el collage de GB, tools/edit_carteles.py)
  GhostGrey.bps                                  (parche original del hack)"""
import os, shutil, subprocess, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
RAIZ = os.path.join(ROOT, '..')
sys.path.insert(0, HERE)
from bps import apply

USA = os.path.join(RAIZ, 'Pokemon - FireRed Version (USA).gba')
ES = os.path.join(RAIZ, 'Pokemon - Edicion Rojo Fuego (Spain).gba')
HACK = os.path.join(RAIZ, 'GhostGrey.bps')
EN = os.path.join(ROOT, 'build', 'ghostgrey_en.gba')


def paso(script, *args):
    print('==', script, *args)
    subprocess.run([sys.executable, os.path.join(HERE, script), *args], check=True, cwd=ROOT)


def main():
    for f, crc in ((USA, 0xDD88761C), (ES, 0x9F08064E)):
        if not os.path.exists(f):
            sys.exit('falta ' + os.path.basename(f))
        if zlib.crc32(open(f, 'rb').read()) != crc:
            sys.exit('%s no es la ROM esperada (CRC32 %08X)' % (os.path.basename(f), crc))
    if not os.path.exists(EN):
        if not os.path.exists(HACK):
            sys.exit('falta GhostGrey.bps (el parche original del hack)')
        os.makedirs(os.path.dirname(EN), exist_ok=True)
        rom = apply(open(USA, 'rb').read(), open(HACK, 'rb').read())
        open(EN, 'wb').write(rom)
        print('ROM inglesa del hack: CRC32 %08X' % zlib.crc32(rom))
    datos = [os.path.join(ROOT, 'data', f) for f in ('vanilla_pairs.json', 'vanilla_pairs_code.json', 'inventory.json')]
    if '--rehacer' in sys.argv or not all(os.path.exists(f) for f in datos):
        for s in ('pair_vanilla.py', 'pair_code.py', 'pair_tables.py', 'inventory.py'):
            paso(s)
    paso('build.py')
    shutil.copy(os.path.join(ROOT, 'build', 'GhostGrey_ES.bps'), os.path.join(RAIZ, 'GhostGrey_ES.bps'))
    paso('parchear.py')


if __name__ == '__main__':
    main()
