"""Batida original da Nostos (composta por código -> sem direitos de autor de terceiros).

Uso:  python3 engine/musica.py <segundos> <bpm> <saida.wav> [estilo] [seed]
Estilos: "afro" (afro-house suave, padrão), "lofi" (calmo, para textos emocionais).
Os cortes do vídeo (engine/livros.py, mesmo bpm) caem em cima das batidas.
"""
import sys, wave
import numpy as np

SR = 44100


def env(n, a=0.005, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def kick(n):
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.18)


def noise_hit(n, d, hp=True, rng=None):
    x = rng.standard_normal(n)
    if hp:
        x = np.diff(np.concatenate([[0], x]))
    return x * env(n, 0.001, d)


def tone(freq, n, d=0.6, harm=(1, 0.5, 0.25, 0.12)):
    t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * freq * (k + 1) * t) * np.exp(-t * (k + 1) / d) for k, a in enumerate(harm))
    return x * np.minimum(1, t / 0.01)


def lowpass(x, a=0.15):
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):          # simples, suficiente para pads curtos
        acc += a * (x[i] - acc)
        y[i] = acc
    return y


def midi(m):
    return 440 * 2 ** ((m - 69) / 12)


def make(seconds, bpm=112, style="afro", seed=7):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    beat = 60 / bpm
    out = np.zeros(n + int(SR * (beat * 4 + 1)))   # folga para o último acorde (4 batidas) não sair do buffer
    s16 = beat / 4
    # progressão quente (Am - F - C - G) / lofi: Dm9 - G13 - Cmaj9 - Am7
    prog = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 60, 64], [55, 59, 62, 67]] if style == "afro" else \
           [[50, 53, 57, 60, 64], [43, 53, 57, 59, 64], [48, 52, 55, 59, 62], [45, 48, 52, 55, 59]]
    bass_notes = [45, 41, 48, 43] if style == "afro" else [38, 43, 36, 45]
    steps = int(seconds / s16) + 1
    for i in range(steps):
        p = int(i * s16 * SR)
        if p >= n:
            break
        bar = i // 16
        st = i % 16
        swing = int(0.018 * SR) if st % 2 == 1 else 0
        p += swing
        ch = prog[bar % 4]
        if style == "afro":
            if st % 4 == 0:
                out[p:p + int(0.35 * SR)] += 0.95 * kick(int(0.35 * SR))
            if st in (4, 12):
                out[p:p + int(0.2 * SR)] += 0.35 * noise_hit(int(0.2 * SR), 0.06, rng=rng)
            if st % 2 == 1:
                out[p:p + int(0.08 * SR)] += 0.10 * noise_hit(int(0.08 * SR), 0.02, rng=rng)
            if st in (3, 7, 10, 14):   # shaker/conga sincopada
                out[p:p + int(0.12 * SR)] += 0.22 * tone(midi(62 + (st % 3) * 2), int(0.12 * SR), 0.05, (1, 0.3))
            if st in (0, 6, 10):
                out[p:p + int(0.4 * SR)] += 0.45 * tone(midi(bass_notes[bar % 4] - 12), int(0.4 * SR), 0.25, (1, 0.35, 0.1))
            if st in (2, 8, 13):       # stabs de piano
                for m in ch:
                    out[p:p + int(0.5 * SR)] += 0.07 * tone(midi(m), int(0.5 * SR), 0.18)
        else:
            if st in (0, 10):
                out[p:p + int(0.35 * SR)] += 0.8 * kick(int(0.35 * SR))
            if st in (4, 12):
                out[p:p + int(0.25 * SR)] += 0.25 * noise_hit(int(0.25 * SR), 0.09, rng=rng)
            if st % 2 == 0:
                out[p:p + int(0.06 * SR)] += 0.06 * noise_hit(int(0.06 * SR), 0.015, rng=rng)
            if st == 0:
                L = int(beat * 4 * SR)
                for m in ch:
                    out[p:p + L] += 0.06 * tone(midi(m), L, 1.6)
                out[p:p + L] += 0.35 * tone(midi(bass_notes[bar % 4] - 12), L, 0.9, (1, 0.2))
    out = out[:n]
    out += 0.004 * rng.standard_normal(n)          # leve "ar" de vinil
    fade = int(0.25 * SR)
    out[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
    out[-fade:] *= np.linspace(1, 0, fade)
    out = np.tanh(out * 1.4) / np.tanh(1.4)
    out /= max(1e-6, np.abs(out).max()) / 0.85
    return out


def save(x, path):
    st = np.stack([x, np.roll(x, 90)], 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


if __name__ == "__main__":
    sec, bpm, out = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    style = sys.argv[4] if len(sys.argv) > 4 else "afro"
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else 7
    save(make(sec, bpm, style, seed), out)
    print(out)
