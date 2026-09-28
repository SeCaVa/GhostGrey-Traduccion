import sys, zlib
def rd(p):
    return open(p,'rb').read()
def apply(src, patch):
    assert patch[:4]==b'BPS1'
    pos=4
    def num():
        nonlocal pos
        data=0; shift=1
        while True:
            x=patch[pos]; pos+=1
            data+=(x&0x7f)*shift
            if x&0x80: break
            shift<<=7; data+=shift
        return data
    ssize=num(); tsize=num(); msize=num()
    meta=patch[pos:pos+msize]; pos+=msize
    out=bytearray(tsize); op=0; srel=0; trel=0
    end=len(patch)-12
    while pos<end:
        d=num(); cmd=d&3; ln=(d>>2)+1
        if cmd==0:
            out[op:op+ln]=src[op:op+ln]; op+=ln
        elif cmd==1:
            out[op:op+ln]=patch[pos:pos+ln]; pos+=ln; op+=ln
        elif cmd==2:
            o=num(); srel+=(-1 if o&1 else 1)*(o>>1)
            out[op:op+ln]=src[srel:srel+ln]; srel+=ln; op+=ln
        else:
            o=num(); trel+=(-1 if o&1 else 1)*(o>>1)
            for _ in range(ln):
                out[op]=out[trel]; op+=1; trel+=1
    sc,tc,pc=[int.from_bytes(patch[end+i*4:end+i*4+4],'little') for i in range(3)]
    print('src size',ssize,'tgt size',tsize,'meta',meta[:200])
    print('src crc ok', zlib.crc32(src)==sc, 'tgt crc ok', zlib.crc32(out)==tc)
    return bytes(out)
src=rd(sys.argv[1]); p=rd(sys.argv[2])
out=apply(src,p)
open(sys.argv[3],'wb').write(out)
