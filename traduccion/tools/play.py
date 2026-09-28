"""Macros para recorrer el juego en el emulador y generar hojas de capturas."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from emu import run, sheet


class Seq:
    def __init__(self, prefix):
        self.s = [('wait', 5)]
        self.shots = []
        self.prefix = prefix

    def shot(self):
        n = '%s%03d' % (self.prefix, len(self.shots))
        self.s.append(('shot', n)); self.shots.append(n)
        return self

    def walk(self, path):
        """path: 'RRUUL' (R,L,U,D)"""
        for c in path:
            k = {'R': 'RIGHT', 'L': 'LEFT', 'U': 'UP', 'D': 'DOWN'}[c]
            self.s += [(k, 16), ('wait', 4)]
        self.s.append(('pos', path[-6:]))
        return self

    def face(self, c):
        k = {'R': 'RIGHT', 'L': 'LEFT', 'U': 'UP', 'D': 'DOWN'}[c]
        self.s += [(k, 3), ('wait', 8)]
        return self

    def talk(self, presses, wait=45, first_wait=40, close=True):
        self.s += [('A', 5), ('wait', first_wait)]
        self.shot()
        for _ in range(presses):
            self.s += [('A', 5), ('wait', wait)]
            self.shot()
        if close:
            self.s += [('B', 5), ('wait', 25), ('B', 5), ('wait', 25)]
        return self

    def wait(self, n):
        self.s.append(('wait', n)); return self

    def press(self, key, n=5, wait=30, shot=True):
        self.s += [(key, n), ('wait', wait)]
        if shot: self.shot()
        return self

    def save(self, path):
        self.s.append(('save', path)); return self

    def go(self, rom, state, sheet_name, cols=6):
        r = run(rom, self.s, state_in=state)
        print(r['ok'], r['secs'], 's', r['pos'])
        if self.shots:
            for i in range(0, len(self.shots), 36):
                out = 'build/shots/%s_%d.png' % (sheet_name, i // 36)
                sheet(self.shots[i:i + 36], out, cols=cols, scale=1)
                print(out)
        return r
