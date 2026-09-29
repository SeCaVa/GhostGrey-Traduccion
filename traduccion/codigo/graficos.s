@ Pantallas de la traducción (tools/codigo_c.py extraer): teselas 4bpp, paleta y mapa 32x32 sin comprimir.
	.section .rodata
	.global sPantalla1_Gfx, sPantalla1_Gfx_End, sPantalla1_Pal, sPantalla1_Map
	.global sPantalla2_Gfx, sPantalla2_Gfx_End, sPantalla2_Pal, sPantalla2_Map

	.align 2
sPantalla1_Gfx:
	.incbin "pantalla1.4bpp"
sPantalla1_Gfx_End:
	.align 2
sPantalla1_Pal:
	.incbin "pantalla1.gbapal"
	.align 2
sPantalla1_Map:
	.incbin "pantalla1.bin"

	.align 2
sPantalla2_Gfx:
	.incbin "pantalla2.4bpp"
sPantalla2_Gfx_End:
	.align 2
sPantalla2_Pal:
	.incbin "pantalla2.gbapal"
	.align 2
sPantalla2_Map:
	.incbin "pantalla2.bin"
