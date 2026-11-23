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
- "cover": SÓ a capa de frente, limpa e direita (fotos/livros/capas/<slug>.png, feita com engine/capas.py),
  colada nítida com sombra suave por cima de um fundo real: "bg_clip" (vídeo de fotos/videos/, + "start")
  ou, por defeito, a própria foto do livro desfocada. Ex.: {"kind": "cover", "cover": "a-republica", "dur": 3.6,
  "bg_clip": "fotos/videos/...mp4", "start": 2, "lines": [...], "price": "2 150 MT", "old_price": "2 500 MT"}
  "price" (opcional) = autocolante azul no canto da capa – só em reels-anúncio (~1 em 3); outro com "wa": true.  (Yuri 23/11: "só a parte da frente, bem cortada")
- "sfx": "sons/sfx/whoosh.m4a" (opcional) – som de transição no 1.º segundo para parar o dedo.
- clip/cover: "focus": 0.8 (fundo desfocado → nítido), "plain": true + "color": [255,227,150] (gancho sem etiqueta,
  amarelo-creme), "price_text": "1 650 MT" (preço branco em DM Serif Display Italic, sem fundo; "price_y").
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


def cover_layer(slug, width=640):
    """Capa plana com cantos levemente arredondados e sombra suave (RGBA, já com margem para a sombra)."""
    c = Image.open(P(f'fotos/livros/capas/{slug}.png')).convert('RGB')
    h = int(c.height * width / c.width); c = c.resize((width, h), Image.LANCZOS)
    m = Image.new('L', (width, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, width - 1, h - 1], 8, fill=255)
    pad = 60; lay = Image.new('RGBA', (width + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('L', lay.size, 0); ImageDraw.Draw(sh).rounded_rectangle([pad + 6, pad + 18, pad + width + 6, pad + h + 18], 12, fill=150)
    lay.putalpha(sh.filter(ImageFilter.GaussianBlur(22))); lay = Image.composite(Image.new('RGBA', lay.size, (0, 0, 0, 255)), Image.new('RGBA', lay.size, (0, 0, 0, 0)), lay.getchannel('A'))
    lay.paste(c, (pad, pad), m)
    return lay


def price_text(price, size=92):
    """Preço escrito à mão-elegante (DM Serif Display Italic), branco, sem fundo – só sombra suave."""
    f = font('DMSerifDisplay-Italic.ttf', size)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).text((0, 0), price, font=f, fill=(0, 0, 0, 200))
    d.text((0, 0), price, font=f, fill=(255, 255, 255, 255))
    bb = lay.getbbox(); lay = Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)), lay)
    return lay.crop((0, 0, bb[2] + 30, bb[3] + 30))


def price_badge(price, old=None):
    """Etiqueta de preço tipo autocolante: azul Nostos, preço em creme; "old" = preço antigo riscado (promoção)."""
    fb, fs = font('Inter-ExtraBold.otf', 64), font('Inter-Medium.otf', 32)
    tmp = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    pw = tmp.textlength(price, font=fb); ow = tmp.textlength(old, font=fs) if old else 0
    w = int(max(pw, ow) + 76); h = 112 + (44 if old else 0)
    b = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0))
    sh = Image.new('L', b.size, 0); ImageDraw.Draw(sh).rounded_rectangle([24, 28, w + 24, h + 28], 26, fill=140)
    b.putalpha(sh.filter(ImageFilter.GaussianBlur(10)))
    b = Image.composite(Image.new('RGBA', b.size, (0, 0, 0, 255)), Image.new('RGBA', b.size, (0, 0, 0, 0)), b.getchannel('A'))
    d = ImageDraw.Draw(b); d.rounded_rectangle([20, 20, w + 20, h + 20], 26, fill=NAVY + (255,), outline=CREAM + (255,), width=3)
    y = 34
    if old:
        x = 20 + (w - ow) / 2; d.text((x, y), old, font=fs, fill=(201, 207, 224))
        d.line([(x - 4, y + 21), (x + ow + 4, y + 17)], fill=(235, 90, 90), width=4); y += 44
    d.text((20 + (w - pw) / 2, y), price, font=fb, fill=CREAM)
    return b.rotate(4, resample=Image.BICUBIC, expand=True)


def cover_bg(slug, n, sc):
    if sc.get('bg_clip'):
        fr = clip_frames(sc['bg_clip'], sc.get('start', 0), n / FPS)
        return [Image.eval(f.filter(ImageFilter.GaussianBlur(sc.get('bg_blur', 6))), lambda v: int(v * 0.8)) for f in fr]
    reg = json.load(open(P('data/capas.json')))
    ph = Image.open(P(reg[slug]['photo'])).convert('RGB')
    s = max(W / ph.width, H / ph.height); ph = ph.resize((int(ph.width * s), int(ph.height * s)))
    ph = ph.crop(((ph.width - W) // 2, (ph.height - H) // 2, (ph.width - W) // 2 + W, (ph.height - H) // 2 + H))
    return [ImageEnhance.Brightness(ph.filter(ImageFilter.GaussianBlur(30))).enhance(0.8)] * n


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


def text_layer(lines, size, top, chars=None, color=None, plain=False):
    """plain=True: sem etiqueta azul, tudo em negrito na cor "color" (gancho amarelo-creme, Yuri 23/11)."""
    reg, bold = font('Inter-Medium.otf', size), font('Inter-ExtraBold.otf', size)
    if plain: reg = bold
    col = tuple(color) if color else CREAM
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
            if b and not plain:
                pw = d.textlength(shown, font=f)
                d.rounded_rectangle([x - 12, y - 4, x + pw + 12, y + size * 1.18], 12, fill=NAVY + (235,))
                d.text((x, y), shown, font=f, fill=CREAM)
            else:
                sd.text((x, y + 4), shown, font=f, fill=(0, 0, 0, 230))
                d.text((x, y), shown, font=f, fill=col)
            x += w
        y += lh
    return Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6)), lay)


def outro(dur, sub, wa=False):
    base = Image.new('RGB', (W, H), NAVY)
    logo = Image.open(os.path.join(ROOT, 'engine', 'logo_azul.jpg')).resize((420, 420))
    base.paste(logo, ((W - 420) // 2, 560))
    d = ImageDraw.Draw(base)
    f = font('EBGi.ttf', 78); t = 'Leia. Regresse a si.'
    d.text(((W - d.textlength(t, font=f)) / 2, 1080), t, font=f, fill=CREAM)
    f2 = font('Inter-Medium.otf', 36)
    d.text(((W - d.textlength(sub, font=f2)) / 2, 1210), sub, font=f2, fill=(201, 207, 224))
    if wa:                                                  # contacto (só nos reels com preço)
        f3 = font('Inter-ExtraBold.otf', 46); t3 = 'WhatsApp 87\u00a0943\u00a01217'; tw = d.textlength(t3, font=f3)
        d.rounded_rectangle([(W - tw) / 2 - 36, 1300, (W + tw) / 2 + 36, 1392], 46, fill=CREAM)
        d.text(((W - tw) / 2, 1318), t3, font=f3, fill=NAVY)
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
           ] + (['-i', P(spec['audio_intro'])] if spec.get('audio_intro') else []) + \
          (['-i', P(spec['sfx'])] if spec.get('sfx') else []) + [
           '-filter_complex', (f'[1:a]atrim=0:{total},afade=t=in:d=0.3,afade=t=out:st={total - 1.6}:d=1.6[a]'
               if not spec.get('audio_intro') else
               # frase falada no início (ex.: som_07, 3 s) e a música entra logo a seguir
               f'[1:a]atrim=0:{total - spec.get("intro_dur", 3)},afade=t=in:d=0.4,adelay={int(spec.get("intro_dur", 3) * 1000)}:all=1[m];'
               f'[2:a]apad[v];[v][m]amix=inputs=2:duration=longest:normalize=0,atrim=0:{total},'
               f'afade=t=out:st={total - 1.6}:d=1.6[a]')
               + (f';[a]volume=1[mm];[{3 if spec.get("audio_intro") else 2}:a]volume={spec.get("sfx_vol", 0.9)},apad[sx];'
                  f'[mm][sx]amix=inputs=2:duration=first:normalize=0[a2]' if spec.get('sfx') else ''),
           '-map', '0:v', '-map', '[a2]' if spec.get('sfx') else '[a]', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE); badges = {}
    for sc in spec['scenes']:
        if sc['kind'] == 'outro':
            for k, fr in enumerate(outro(sc['dur'], sc['sub'], sc.get('wa'))):
                ff.stdin.write(Image.blend(Image.new('RGB', (W, H)), fr, ease(k / (0.4 * FPS))).tobytes())
            continue
        n = int(round(sc['dur'] * FPS))
        if sc['kind'] == 'cover':
            frames = cover_bg(sc['cover'], n, sc); cov = cover_layer(sc['cover'], sc.get('cover_w', 640))
        else:
            frames = [book_still(sc['photo'], sc['crop'])] * n if sc['kind'] == 'photo' \
                else clip_frames(sc['clip'], sc.get('start', 0), sc['dur'])
        size = sc.get('size', 54)
        total_chars = sum(len(t) for l in sc['lines'] for t, _ in l)
        tk = dict(color=sc.get('color'), plain=sc.get('plain', False))
        cache = None if sc.get('type') else text_layer(sc['lines'], size, top, **tk)
        ptxt = price_text(sc['price_text'], sc.get('price_size', 92)) if sc.get('price_text') else None
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
            if sc.get('focus'):                             # fundo desfocado que fica nítido (abertura)
                r = 26 * (1 - ease(t / sc['focus']))
                if r > 0.3: img = img.filter(ImageFilter.GaussianBlur(r))
            img.alpha_composite(grad)
            if ptxt is not None:                            # preço em letra elegante branca, sem fundo
                pa = ease((t - 0.45) / 0.4)
                if pa > 0:
                    pl = ptxt.copy(); pl.putalpha(pl.getchannel('A').point(lambda v: int(v * pa)))
                    img.alpha_composite(pl, ((W - pl.width) // 2, sc.get('price_y', 470) + int(16 * (1 - pa))))
            if sc['kind'] == 'cover':                       # capa entra a crescer e respira devagar
                a = ease(t / 0.45); sc_ = (0.9 + 0.1 * a) * (1 + 0.025 * k / n)
                cw, ch = int(cov.width * sc_), int(cov.height * sc_)
                cl = cov.resize((cw, ch), Image.BILINEAR)
                if a < 1: cl.putalpha(cl.getchannel('A').point(lambda v: int(v * a)))
                cy = sc.get('cover_y', 1130)                # centro vertical da capa
                cx0, cy0 = (W - cw) // 2 - 20, cy - ch // 2
                img.alpha_composite(cl, (cx0, cy0))
                if sc.get('price'):                         # preço: autocolante no canto de baixo da capa
                    pb = badges.setdefault(id(sc), price_badge(sc['price'], sc.get('old_price')))
                    pa = ease((t - 0.35) / 0.3)
                    if pa > 0:
                        ps = 0.7 + 0.3 * pa; pl = pb.rotate(-8, resample=Image.BICUBIC, expand=True).resize((int(pb.width * ps), int(pb.height * ps)), Image.BILINEAR)
                        pl.putalpha(pl.getchannel('A').point(lambda v: int(v * pa)))
                        img.alpha_composite(pl, (max(10, cx0 - int(pl.width * 0.25)),   # canto esquerdo: longe dos botões do Instagram
                                                 cy0 + ch - int(pl.height * 0.7)))
            if sc.get('type'):
                img.alpha_composite(text_layer(sc['lines'], size, top, int(total_chars * min(1, t / sc['type'])), **tk))
            else:
                a = ease(t / 0.35)
                lay = cache.copy(); lay.putalpha(lay.getchannel('A').point(lambda v: int(v * a)))
                img.alpha_composite(lay, (0, int(30 * (1 - a))))
            ff.stdin.write(img.convert('RGB').tobytes())
    ff.stdin.close(); ff.wait()
    print(json.dumps({'video': spec['out'], 'seconds': total}))


if __name__ == '__main__':
    main(sys.argv[1])
