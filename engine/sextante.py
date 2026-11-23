"""Reel no estilo APROVADO pelo Yuri (21/11/2026): "Sextante" com as cores Nostos + som viral escolhido por ele.

Uso:  python3 engine/sextante.py spec.json

Spec (caminhos relativos à raiz do repositório):
{
  "out": "posts/AAAA-MM-DD/reel_meio.mp4",
  "audio": "sons/som_01_felipe_reis.m4a",    # um dos sons em sons/ (rodar; nunca música gerada)
  "audio_start": 0.3, "audio_loop": true,      # loop quando o som é mais curto do que o vídeo
  "audio_intro": "sons/som_07_fala_valorizam_inteligente.m4a", "intro_dur": 3,  # opcional: frase falada antes da música
  "scenes": [
    {"kind": "clip", "clip": "fotos/videos/embrulho-presente-separadores.mp4", "start": 0, "dur": 4.5,
     "type": 1.5, "size": 62,                  # "type" = gancho a escrever-se (segundos)
     "lines": [[["Livros para quem não", false]], [["consegue ", false], ["desligar a cabeça", true]]]},
    {"kind": "photo", "photo": "fotos/livros/o-poder-do-agora_anuncio.jpg", "crop": [405,150,1075,1160], "dur": 4.2,
     "lines": [[["Para quem vive preso", false]], [["ao passado ou ao ", false], ["futuro.", true]]]},
    {"kind": "outro", "dur": 3.2, "sub": "Qual destes é o seu?"}
  ]
}
- lines: até 2 linhas curtas; [texto, true] = palavra-chave (creme sobre etiqueta azul Nostos).
- "photo" + "crop" (x0,y0,x1,y1 na foto de 1350 px de largura): recorte SÓ ao livro e à mão, sem preço/texto do
  anúncio (ver data/recortes.json). O livro fica a ~80 % da largura, um pouco à esquerda, com bordas em degradê
  subtil sobre o fundo desfocado da própria foto (longe dos botões e da legenda do Instagram).
- "clip": vídeo real em ecrã inteiro (opcional "inset": 0.6 para recuar – só se pedido).
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, 'engine', 'fonts') + '/'
W, H, FPS = 1080, 1920, 30
NAVY = (2, 36, 108); CREAM = (251, 248, 240)


def P(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def font(name, s):
    return ImageFont.truetype(F + name, s)


def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3


def clip_frames(path, start, dur):
    cmd = ['ffmpeg', '-loglevel', 'error', '-ss', str(start), '-t', f'{dur:.3f}', '-i', P(path),
           '-vf', f'scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (W * H * 3)
    fr = [Image.frombuffer('RGB', (W, H), raw[i * W * H * 3:(i + 1) * W * H * 3]) for i in range(n)]
    need = int(round(dur * FPS))
    while len(fr) < need: fr.append(fr[-1])
    return fr[:need]


def book_still(photo, crop):
    """Livro recortado (sem preço) a ~80 % da largura, bordas em degradê subtil, fundo desfocado claro."""
    im = Image.open(P(photo)).convert('RGB')
    if im.width != 1350:
        im = im.resize((1350, round(im.height * 1350 / im.width)), Image.LANCZOS)
    c = im.crop(tuple(crop))
    s = max(W / c.width, H / c.height)
    bg = c.resize((int(c.width * s) + 2, int(c.height * s) + 2), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(40))).enhance(0.85)
    fh = 1230; fw = int(c.width * fh / c.height)
    if fw > 860: fw = 860; fh = int(c.height * fw / c.width)
    fg = c.resize((fw, fh), Image.LANCZOS)
    m = Image.new('L', (fw, fh), 0)
    ImageDraw.Draw(m).rounded_rectangle([22, 22, fw - 22, fh - 22], 30, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(14))
    bg.paste(fg, ((W - fw) // 2 - 20, 440 + (1230 - fh) // 2), m)
    return bg


def text_layer(lines, size, top, chars=None):
    reg, bold = font('Inter-Medium.otf', size), font('Inter-ExtraBold.otf', size)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shadow)
    lh = int(size * 1.32); y = top; left = chars if chars is not None else 10 ** 6
    for line in lines:
        widths = [d.textlength(t, font=bold if b else reg) for t, b in line]
        x = (W - sum(widths)) / 2
        for (t, b), w in zip(line, widths):
            f = bold if b else reg
            shown = t[:max(0, left)]; left -= len(t)
            if not shown: break
            if b:
                pw = d.textlength(shown, font=f)
                d.rounded_rectangle([x - 12, y - 4, x + pw + 12, y + size * 1.18], 12, fill=NAVY + (235,))
                d.text((x, y), shown, font=f, fill=CREAM)
            else:
                sd.text((x, y + 3), shown, font=f, fill=(0, 0, 0, 220))
                d.text((x, y), shown, font=f, fill=CREAM)
            x += w
        y += lh
    return Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)), lay)


def outro(dur, sub):
    base = Image.new('RGB', (W, H), NAVY)
    logo = Image.open(os.path.join(ROOT, 'engine', 'logo_azul.jpg')).resize((420, 420))
    base.paste(logo, ((W - 420) // 2, 560))
    d = ImageDraw.Draw(base)
    f = font('EBGi.ttf', 78); t = 'Leia. Regresse a si.'
    d.text(((W - d.textlength(t, font=f)) / 2, 1080), t, font=f, fill=CREAM)
    f2 = font('Inter-Medium.otf', 36)
    d.text(((W - d.textlength(sub, font=f2)) / 2, 1210), sub, font=f2, fill=(201, 207, 224))
    return [base] * int(round(dur * FPS))


def main(spec_path):
    spec = json.load(open(spec_path))
    out = P(spec['out']); os.makedirs(os.path.dirname(out), exist_ok=True)
    total = sum(s['dur'] for s in spec['scenes']); top = spec.get('text_y', 250)
    grad = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(grad)
    for yy in range(760):
        gd.line([(0, yy), (W, yy)], fill=(2, 14, 40, int(175 * (1 - yy / 760) ** 1.6)))
    cmd = ['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
           '-r', str(FPS), '-i', '-'] + (['-stream_loop', '-1'] if spec.get('audio_loop') else []) + \
          ['-ss', str(spec.get('audio_start', 0)), '-i', P(spec['audio']),
           ] + (['-i', P(spec['audio_intro'])] if spec.get('audio_intro') else []) + [
           '-filter_complex', (f'[1:a]atrim=0:{total},afade=t=in:d=0.3,afade=t=out:st={total - 1.6}:d=1.6[a]'
               if not spec.get('audio_intro') else
               # frase falada no início (ex.: som_07, 3 s) e a música entra logo a seguir
               f'[1:a]atrim=0:{total - spec.get("intro_dur", 3)},afade=t=in:d=0.4,adelay={int(spec.get("intro_dur", 3) * 1000)}:all=1[m];'
               f'[2:a]apad[v];[v][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:{total},'
               f'afade=t=out:st={total - 1.6}:d=1.6[a]'),
           '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for sc in spec['scenes']:
        if sc['kind'] == 'outro':
            for k, fr in enumerate(outro(sc['dur'], sc['sub'])):
                ff.stdin.write(Image.blend(Image.new('RGB', (W, H)), fr, ease(k / (0.4 * FPS))).tobytes())
            continue
        n = int(round(sc['dur'] * FPS))
        frames = [book_still(sc['photo'], sc['crop'])] * n if sc['kind'] == 'photo' \
            else clip_frames(sc['clip'], sc.get('start', 0), sc['dur'])
        size = sc.get('size', 54)
        total_chars = sum(len(t) for l in sc['lines'] for t, _ in l)
        cache = None if sc.get('type') else text_layer(sc['lines'], size, top)
        for k, fr in enumerate(frames):
            t = k / FPS; z = 1 + 0.05 * (k / n); zw, zh = int(W * z), int(H * z)
            img = fr.resize((zw, zh), Image.BILINEAR).crop(((zw - W) // 2, (zh - H) // 2,
                                                            (zw - W) // 2 + W, (zh - H) // 2 + H)).convert('RGBA')
            if sc.get('inset'):
                small = img.convert('RGB').resize((W // 8, H // 8)).filter(ImageFilter.GaussianBlur(5)).resize((W, H))
                small = Image.eval(small, lambda v: int(v * 0.72)).convert('RGBA')
                iw, ih = int(W * sc['inset']), int(H * sc['inset'])
                small.alpha_composite(img.resize((iw, ih), Image.BILINEAR), ((W - iw) // 2 - 30, 440))
                img = small
            img.alpha_composite(grad)
            if sc.get('type'):
                img.alpha_composite(text_layer(sc['lines'], size, top, int(total_chars * min(1, t / sc['type']))))
            else:
                a = ease(t / 0.35)
                lay = cache.copy(); lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
                img.alpha_composite(lay, (0, int(30 * (1 - a))))
            ff.stdin.write(img.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()
    print(json.dumps({'video': spec['out'], 'seconds': total}))


if __name__ == '__main__':
    main(sys.argv[1])
