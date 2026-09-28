"""Parches de código en ensamblador THUMB (necesita keystone-engine solo para regenerarlos).
Genera data/parches_codigo.json: {dirección: {"orig": hex original, "new": hex nuevo}} que aplica build.py.

- Pokédex: altura en metros y peso en kilos (el código USA convierte a pies/pulgadas y libras).
"""
import json, os, sys
import keystone

HERE = os.path.dirname(__file__)
ROOT = os.path.join(HERE, '..')
ROM_BASE = 0x8000000
UDIV = 0x81E460D  # __udivsi3 (| 1: THUMB)
UMOD = 0x81E4685  # __umodsi3
CODE_AREA = 0x1FF0000  # tras FREE_END de build.py: código nuevo en posiciones fijas

# Altura (DexScreen_PrintMonHeight). Al llegar a 0x10591C: r0 = ¿capturado?, r4 = altura en dm,
# buffer en sp+8 con la cabecera FC 14 05 00. Deja " dd,d m" en sp+12 (hueco extra: coma alineada con el peso) y vuelve a la impresión (0x1059FE).
ALTURA = (0x10591C, 0x1059FE, f'''
    lsls r0, r0, #24
    cmp r0, #0
    beq nc
    add r5, sp, #12
    movs r0, #0
    strb r0, [r5]
    adds r5, #1
    adds r0, r4, #0
    movs r1, #100
    ldr r3, ={UDIV:#x}
    bl vr3
    cmp r0, #0
    beq a1
    adds r0, #0xA1
a1: strb r0, [r5]
    adds r0, r4, #0
    movs r1, #10
    ldr r3, ={UDIV:#x}
    bl vr3
    movs r1, #10
    ldr r3, ={UMOD:#x}
    bl vr3
    adds r0, #0xA1
    strb r0, [r5, #1]
    movs r0, #0xB8
    strb r0, [r5, #2]
    adds r0, r4, #0
    movs r1, #10
    ldr r3, ={UMOD:#x}
    bl vr3
    adds r0, #0xA1
    strb r0, [r5, #3]
    b fin
nc: add r5, sp, #12
    movs r0, #0
    strb r0, [r5]
    adds r5, #1
    movs r0, #0xAC
    strb r0, [r5]
    strb r0, [r5, #1]
    movs r1, #0xB8
    strb r1, [r5, #2]
    strb r0, [r5, #3]
fin:
    movs r0, #0
    strb r0, [r5, #4]
    movs r0, #0xE1
    strb r0, [r5, #5]
    movs r0, #0xFF
    strb r0, [r5, #6]
    ldr r1, =0x81059FF
    bx r1
vr3: bx r3
''')

# Peso (DexScreen_PrintMonWeight). En 0x105A8A: r0 = ¿capturado?, r4 = peso en hg, r8 = x,
# buffer en sp+8 con FC 14 05. Deja " ddd,d kg" y vuelve a la impresión (0x105C6C) con r5 = x + 30.
PESO = (0x105A8A, 0x105C6C, f'''
    lsls r0, r0, #24
    add r6, sp, #8
    movs r1, #0
    strb r1, [r6, #3]
    adds r6, #4
    cmp r0, #0
    beq nc
    movs r7, #0
    adds r0, r4, #0
    movs r1, #0xFA
    lsls r1, r1, #2
    ldr r3, ={UDIV:#x}
    bl vr3
    cmp r0, #0
    beq s1
    adds r0, #0xA1
    movs r7, #1
s1: strb r0, [r6]
    adds r0, r4, #0
    movs r1, #100
    ldr r3, ={UDIV:#x}
    bl vr3
    movs r1, #10
    ldr r3, ={UMOD:#x}
    bl vr3
    cmp r0, #0
    bne d2
    cmp r7, #0
    beq s2
d2: adds r0, #0xA1
s2: strb r0, [r6, #1]
    adds r0, r4, #0
    movs r1, #10
    ldr r3, ={UDIV:#x}
    bl vr3
    movs r1, #10
    ldr r3, ={UMOD:#x}
    bl vr3
    adds r0, #0xA1
    strb r0, [r6, #2]
    movs r0, #0xB8
    strb r0, [r6, #3]
    adds r0, r4, #0
    movs r1, #10
    ldr r3, ={UMOD:#x}
    bl vr3
    adds r0, #0xA1
    strb r0, [r6, #4]
    b fin
nc: movs r0, #0xAC
    strb r0, [r6]
    strb r0, [r6, #1]
    strb r0, [r6, #2]
    movs r1, #0xB8
    strb r1, [r6, #3]
    strb r0, [r6, #4]
fin:
    movs r0, #0
    strb r0, [r6, #5]
    movs r0, #0xDF
    strb r0, [r6, #6]
    movs r0, #0xDB
    strb r0, [r6, #7]
    movs r0, #0xFF
    strb r0, [r6, #8]
    mov r5, r8
    adds r5, #30
    ldr r1, =0x8105C6D
    bx r1
vr3: bx r3
''')


def gancho(ks, addr, dest):
    """ldr r1, =dest; bx r1 en addr (r1 está libre en los dos puntos). Usa 8 o 10 bytes."""
    src = 'ldr r1, [pc, #0]; bx r1' if addr % 4 == 0 else 'ldr r1, [pc, #4]; bx r1; nop'
    code, _ = ks.asm(src, ROM_BASE + addr)
    return bytes(code) + (dest | 1).to_bytes(4, 'little')


def main():
    rom = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    ks = keystone.Ks(keystone.KS_ARCH_ARM, keystone.KS_MODE_THUMB)
    out = []
    pos = CODE_AREA
    for start, _end, src in (ALTURA, PESO):
        code, _ = ks.asm(src, ROM_BASE + pos)
        code = bytes(code)
        hook = gancho(ks, start, ROM_BASE + pos)
        out.append({'addr': '%X' % start, 'orig': rom[start:start + len(hook)].hex(), 'new': hook.hex()})
        assert rom[pos:pos + len(code)] == bytes([0xFF]) * len(code)
        out.append({'addr': '%X' % pos, 'orig': 'ff' * len(code), 'new': code.hex()})
        print('%X -> %X: %d bytes' % (start, pos, len(code)))
        pos = (pos + len(code) + 3) & ~3
    json.dump(out, open(os.path.join(ROOT, 'data/parches_codigo.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
