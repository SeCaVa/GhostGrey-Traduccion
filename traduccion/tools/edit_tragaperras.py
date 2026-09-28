"""Pantalla de información de la tragaperras (dibujo del hack con Aston): "ASTON SEZ!!! 100% of Gamblers
QUIT before a JACKPOT!" -> "ASTON DICE!!! ¡El 100% de los jugadores LO DEJA antes del GORDO!".
Se borra el texto a mano del dibujo y se escribe con la fuente Ink Free de Windows (sin suavizado).
Gráfico 0xF5DB00 y mapa 0xF3B2C0 (punteros 0x1413D0 y 0x1413D4). Salida: data/gfx/slotinfo_gfx.bin y _tm.bin."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from graficos import lz77, _px, _tile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.join(os.path.dirname(__file__), '..')
GFX, TM = 0xF5DB00, 0xF3B2C0


def screen(g,tm,W=32):
    n=len(tm)//2; H=n//W
    img=[[0]*(W*8) for _ in range(H*8)]
    for k in range(n):
        e=tm[2*k]|tm[2*k+1]<<8; t=e&0x3FF; hf=e>>10&1; vf=e>>11&1
        p=_px(g[t*32:t*32+32])
        for y in range(8):
            for x in range(8):
                img[k//W*8+y][k%W*8+x]=p[(7-y if vf else y)*8+(7-x if hf else x)]
    return img


def rebuild(img,tm,W=32):
    """nuevo gráfico (piezas únicas, reutilizando volteos) y mapa conservando paleta"""
    n=len(tm)//2; tiles={}; gfx=bytearray(); out=bytearray(tm)
    for k in range(n):
        c,r=k%W,k//W
        px=[[img[r*8+y][c*8+x] for x in range(8)] for y in range(8)]
        found=None
        for hf in (0,1):
            for vf in (0,1):
                q=[px[7-y if vf else y][7-x if hf else x] for y in range(8) for x in range(8)]
                key=_tile(q)
                if key in tiles: found=(tiles[key],hf,vf); break
            if found: break
        if not found:
            key=_tile([v for row in px for v in row]); tiles[key]=len(gfx)//32; gfx+=key; found=(tiles[key],0,0)
        e=tm[2*k]|tm[2*k+1]<<8
        e=(e&0xF000)|found[0]|found[1]<<10|found[2]<<11
        out[2*k]=e&0xFF; out[2*k+1]=e>>8
    return bytes(gfx),bytes(out)


def main():
    h = open(os.path.join(ROOT, 'build/ghostgrey_en.gba'), 'rb').read()
    global img
    img = screen(lz77(h, GFX), lz77(h, TM))
    H,W=len(img),len(img[0])
    FONT='C:/Windows/Fonts/Inkfree.ttf'
    def mask(text,size,stroke=0):
        f=ImageFont.truetype(FONT,size)
        im=Image.new('1',(400,80),0); d=ImageDraw.Draw(im); d.fontmode='1'
        d.text((2,2),text,font=f,fill=1,stroke_width=stroke,stroke_fill=1)
        bb=im.getbbox(); im=im.crop(bb)
        return [[im.getpixel((x,y)) for x in range(im.width)] for y in range(im.height)]
    def comps(x0,x1,y0,y1,vals):
        seen=set(); out=[]
        for y in range(y0,y1):
            for x in range(x0,x1):
                if (x,y) in seen or img[y][x] not in vals: continue
                st=[(x,y)]; seen.add((x,y)); pts=[]
                while st:
                    a,b=st.pop(); pts.append((a,b))
                    for da,db in ((1,0),(-1,0),(0,1),(0,-1)):
                        c,d=a+da,b+db
                        if y0<=d<y1 and x0<=c<x1 and (c,d) not in seen and img[d][c] in vals:
                            seen.add((c,d)); st.append((c,d))
                out.append(pts)
        return out
    # --- título
    for pts in comps(16,150,36,92,(3,5)):
        if max(p[1] for p in pts)<=86:
            for x,y in pts:
                img[y][x]=5 if (y<=73 and x<=86 and len(pts)>1000) else 2
    def draw_outlined(m,x0,y0,fill,out):
        hh,ww=len(m),len(m[0])
        for y in range(-1,hh+1):
            for x in range(-1,ww+1):
                inside=0<=y<hh and 0<=x<ww and m[y][x]
                if inside: img[y0+y][x0+x]=fill
                else:
                    near=any(0<=y+dy<hh and 0<=x+dx<ww and m[y+dy][x+dx] for dy in (-1,0,1) for dx in (-1,0,1))
                    if near: img[y0+y][x0+x]=out
    m=mask('ASTON',30,1)
    draw_outlined(m,22,41,5,3)
    m=mask('DICE!!!',28,1)
    draw_outlined(m,62,62,5,3)
    # --- bocadillo: rellenar componentes 3 encerradas
    for pts in comps(16,150,88,143,(3,)):
        border=False
        for x,y in pts:
            for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
                v=img[y+dy][x+dx]
                if v not in (3,5): border=True
        if not border:
            for x,y in pts: img[y][x]=5
    # restos de "rs" (Gamblers) pegados al borde derecho del bocadillo
    for y in range(96,108):
        for x in range(126,143):
            if img[y][x]==3 and not any(img[y+dy][x+dx]==2 for dy in (-1,0,1) for dx in (-1,0,1)):
                img[y][x]=5
    def draw(m,x0,y0,col):
        for y,row in enumerate(m):
            for x,v in enumerate(row):
                if v: img[y0+y][x0+x]=col
    lines=[(26,94,'“¡El 100% de',13),(28,105,'los jugadores',13),(28,116,'LO DEJA antes',13),(32,127,'del GORDO!”',13)]
    for x0,y0,t,sz in lines:
        m=mask(t,sz)
        draw(m,x0,y0,3)

    g, t = rebuild(img, lz77(h, TM))
    assert len(g) // 32 <= 297, 'demasiadas piezas: %d' % (len(g) // 32)
    os.makedirs(os.path.join(ROOT, 'data/gfx'), exist_ok=True)
    open(os.path.join(ROOT, 'data/gfx/slotinfo_gfx.bin'), 'wb').write(g)
    open(os.path.join(ROOT, 'data/gfx/slotinfo_tm.bin'), 'wb').write(t)
    print('piezas', len(g) // 32)


if __name__ == '__main__':
    main()
