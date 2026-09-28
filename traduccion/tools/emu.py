"""Arnés de pruebas con mGBA (Qt) mediante scripts Lua.
Uso típico:
    run(rom, script=[('A',30), ('wait',60), ('shot','intro1'), ...], state_in=..., state_out=...)
Cada paso: (tecla, frames) mantiene la tecla N frames y luego la suelta 8 frames;
('wait', n) espera; ('shot', nombre) guarda captura en build/shots/nombre.png;
('save', ruta) guarda estado."""
import os, subprocess, time, json

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
MGBA = os.path.abspath(os.path.join(ROOT, '../mgba/mGBA.exe'))
WORK = os.path.join(ROOT, 'build/emu')
SHOTS = os.path.join(ROOT, 'build/shots')
KEYS = {'A': 1, 'B': 2, 'SELECT': 4, 'START': 8, 'RIGHT': 16, 'LEFT': 32, 'UP': 64, 'DOWN': 128,
        'R': 256, 'L': 512}


def _lua_path(p):
    return p.replace('\\', '/')


def run(rom, script, state_in=None, timeout=300, release=8):
    os.makedirs(WORK, exist_ok=True); os.makedirs(SHOTS, exist_ok=True)
    events = []  # (frame, kind, arg)
    f = 1
    for step in script:
        k, v = step
        if k == 'wait':
            f += v
        elif k == 'shot':
            events.append((f, 'shot', _lua_path(os.path.join(SHOTS, v + '.png'))))
            f += 1
        elif k == 'save':
            events.append((f, 'save', _lua_path(os.path.abspath(v))))
            f += 1
        elif k == 'pos':
            events.append((f, 'pos', v))
            f += 1
        elif k == 'hold':  # ('hold', (teclas, frames))
            keys, n = v
            mask = sum(KEYS[x] for x in keys.split('+'))
            events.append((f, 'keys', mask)); f += n
            events.append((f, 'keys', 0)); f += release
        else:
            mask = sum(KEYS[x] for x in k.split('+'))
            events.append((f, 'keys', mask)); f += v
            events.append((f, 'keys', 0)); f += release
    total = f + 2
    lines = []
    for fr, kind, arg in events:
        if kind == 'keys':
            lines.append('{f=%d,k="keys",m=%d}' % (fr, arg))
        else:
            lines.append('{f=%d,k="%s",p="%s"}' % (fr, kind, arg))
    done = os.path.join(WORK, 'DONE')
    if os.path.exists(done): os.remove(done)
    log = os.path.join(WORK, 'pos.log')
    if os.path.exists(log): os.remove(log)
    lua = """
local LOG = "%s"
local ev = {%s}
local i = 1
local frame = 0
callbacks:add("frame", function()
  frame = frame + 1
  while i <= #ev and ev[i].f <= frame do
    local e = ev[i]
    if e.k == "keys" then emu:setKeys(e.m)
    elseif e.k == "shot" then emu:screenshot(e.p)
    elseif e.k == "save" then emu:saveStateFile(e.p)
    elseif e.k == "pos" then
      local sb = emu:read32(0x03005008)
      local lf = io.open(LOG, "a")
      lf:write(string.format("%%s %%d %%d %%d.%%d\\n", e.p, emu:read16(sb), emu:read16(sb+2), emu:read8(sb+4), emu:read8(sb+5)))
      lf:close()
    end
    i = i + 1
  end
  if frame == %d then
    local d = io.open("%s", "w"); d:write("OK"); d:close()
  end
end)
""" % (_lua_path(log), ',\n'.join(lines), total, _lua_path(done))
    sf = os.path.join(WORK, 'script.lua')
    open(sf, 'w').write(lua)
    cmd = [MGBA, os.path.abspath(rom)]
    if state_in:
        cmd += ['-t', os.path.abspath(state_in)]
    cmd += ['--script', sf, '-l', '0',
            '-C', 'fpsTarget=2400', '-C', 'audioSync=0', '-C', 'videoSync=0', '-C', 'mute=1']
    env = dict(os.environ, SDL_AUDIODRIVER='dummy')
    p = subprocess.Popen(cmd, cwd=WORK, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    try:
        while time.time() - t0 < timeout:
            if os.path.exists(done):
                time.sleep(0.8)
                break
            if p.poll() is not None:
                break
            time.sleep(0.2)
    finally:
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(p.pid)], stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    pos = open(log).read().split(chr(10)) if os.path.exists(log) else []
    return {'ok': os.path.exists(done), 'frames': total, 'secs': round(time.time() - t0, 1),
            'pos': [x for x in pos if x]}


def sheet(names, out, cols=4, scale=2):
    """Junta varias capturas en una sola imagen para revisarlas de una vez."""
    from PIL import Image
    ims = [Image.open(os.path.join(SHOTS, n + '.png')).convert('RGB').resize((240, 160), Image.NEAREST)
           for n in names]
    w, h = ims[0].size
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * w, rows * h), (40, 40, 40))
    for k, im in enumerate(ims):
        S.paste(im, ((k % cols) * w, (k // cols) * h))
    S = S.resize((S.width * scale, S.height * scale), Image.NEAREST)
    S.save(out)
    return out
