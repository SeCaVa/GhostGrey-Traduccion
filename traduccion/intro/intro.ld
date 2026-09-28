/* Bloque de las pantallas de la traducción: dirección fija 0x1F00000 de la ROM (tools/intro_traduccion.py). */
/* Funciones y variables de Pokémon FireRed USA 1.0 (pokefirered / CFRU bpre.ld). */
SetIntroCB = 0x080ECAA8 | 1;
IntroCB_Scene1 = 0x080ECEA4 | 1;
SetGpuReg = 0x08000A38 | 1;
GetGpuReg = 0x08000AC4 | 1;
LoadPalette = 0x080703EC | 1;
BlendPalettes = 0x080714D4 | 1;
BeginNormalPaletteFade = 0x08070588 | 1;
CpuSet = 0x081E3B64 | 1;
MPlayStart = 0x081DD858 | 1;
FadeOutBGM = 0x08071DBC | 1;
gMPlayInfo_BGM = 0x03007300;
gPaletteFade = 0x02037AB8;
gMain_newKeys = 0x030030F0 + 0x2E;

SECTIONS
{
    . = 0x09F00000;
    .text : { *(.text.entry) *(.text*) *(.rodata*) }
    .data : { *(.data*) *(.bss*) *(COMMON) }
    /DISCARD/ : { *(.comment) *(.ARM.attributes) *(.note*) }
}
