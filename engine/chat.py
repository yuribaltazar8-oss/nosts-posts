"""Imagem de "conversa" (balões de chat) com as cores Nostos – para posts divertidos.

Uso:  python3 engine/chat.py spec.json
{
  "out": "posts/AAAA-MM-DD/feed_tarde_1.jpg",
  "title": "Eu a tentar comprar só UM livro",          # opcional, no topo
  "who": ["Eu", "Nostos"],                             # [quem envia = DIREITA, quem responde = ESQUERDA]
  "msgs": [[0, "Só vou ver, não vou comprar nada."], [1, "Claro 🙂"], [0, "…manda também esse."]],
  "footer": "Leia. Regresse a si.",                     # opcional
  "style": "nostos" | "ia",                            # "ia" = conversa com uma IA (tema escuro, genérico)
  "react": "😭"                                         # opcional: emoji grande de reacção (estilo meme)
}
"ia": formato "Perguntei à IA…" com aspecto genérico de app de IA (sem logótipos nem nomes de marcas reais,
ex.: nunca o logo/visual do ChatGPT); os lados chamam-se "Eu" e "IA".
Regras: é humor/encenação da marca – nunca apresentar como conversa REAL de um cliente, nunca usar nomes
ou números de pessoas reais, nunca inventar elogios/testemunhos de clientes.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
F = os.path.join(ROOT, 'engine', 'fonts') + '/'
W, H = 1080, 1350
NAVY = (2, 36, 108); CREAM = (246, 239, 224); WHITE = (255, 255, 255); INK = (34, 29, 24); GREY = (110, 104, 96)


def font(n, s):
    return ImageFont.truetype(F + n, s)


def wrap(d, text, f, maxw):
    out = []
    for para in text.split('\n'):
        cur = ''
        for w in para.split():
            t = (cur + ' ' + w).strip()
            if d.textlength(t, font=f) <= maxw: cur = t
            else: out.append(cur); cur = w
        out.append(cur)
    return out


def emoji(ch, px):
    try:
        f = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
    except OSError:
        return None
    im = Image.new('RGBA', (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True)
    return im.crop(im.getbbox()).resize((px, px), Image.LANCZOS)


def render(s, size):
    ia = s.get('style') == 'ia'
    bg, b0, b1, t0, t1, lab = ((12, 12, 14), (40, 40, 44), (2, 36, 108), (236, 236, 236), (251, 248, 240), (160, 160, 165)) if ia \
        else (CREAM, WHITE, NAVY, INK, (251, 248, 240), GREY)
    im = Image.new('RGB', (W, H), bg); d = ImageDraw.Draw(im)
    y = 90
    if s.get('title'):
        ft = font('Inter-ExtraBold.otf', 64)
        for line in wrap(d, s['title'], ft, W - 160):
            d.text(((W - d.textlength(line, font=ft)) / 2, y), line, font=ft, fill=t0 if ia else INK); y += 78
        y += 40
    fm = font('Inter-Medium.otf', size); fn = font('Inter-Medium.otf', 28); lh = int(size * 1.28)
    who = s.get('who', ['', ''])
    # Como nas apps: "Eu" (lado 0) à DIREITA em balão; o outro lado à ESQUERDA.
    # Estilo "ia": a resposta da IA é texto corrido sem balão (como nas apps de IA), sem nomes.
    for side, text in s['msgs']:
        me = side == 0
        if ia and not me:
            lines = wrap(d, text, fm, W - 160)
            for i, l in enumerate(lines):
                d.text((80, y + i * lh), l, font=fm, fill=t0)
            y += len(lines) * lh + 46
            continue
        lines = wrap(d, text, fm, 640)
        bw = max(d.textlength(l, font=fm) for l in lines) + 70; bh = len(lines) * lh + 40
        x = W - 80 - bw if me else 80
        if who[side] and not ia:
            nx = x + bw - 10 - d.textlength(who[side], font=fn) if me else x + 10
            d.text((nx, y), who[side], font=fn, fill=lab); y += 34
        d.rounded_rectangle([x, y, x + bw, y + bh], 40 if ia else 34, fill=b1 if me else b0)
        for i, l in enumerate(lines):
            d.text((x + 35, y + 20 + i * lh), l, font=fm, fill=t1 if me else t0)
        y += bh + (46 if ia else 26)
    if s.get('react'):
        e = emoji(s['react'], 150)
        if e: im.paste(e, (80, y - 10), e); y += 150
    if s.get('footer'):
        ff = font('EBGi.ttf', 46); t = s['footer']
        d.text(((W - d.textlength(t, font=ff)) / 2, H - 110), t, font=ff, fill=(201, 207, 224) if ia else NAVY)
    return im, y


def main(path):
    s = json.load(open(path))
    strip = lambda t: ''.join(ch for ch in t if ord(ch) < 0x2190)   # a letra não tem emojis: tirá-los
    s['msgs'] = [[a, strip(t)] for a, t in s['msgs']]
    for size in (52, 48, 44, 40):                                   # reduzir até caber (mín. 40)
        im, y = render(s, size)
        if y <= H - 125: break
    else:
        print('AVISO: texto demasiado longo mesmo a 40 px – encurtar a conversa')
    out = os.path.join(ROOT, s['out']) if not os.path.isabs(s['out']) else s['out']
    os.makedirs(os.path.dirname(out), exist_ok=True); im.save(out, quality=93)
    print(out)


if __name__ == '__main__':
    main(sys.argv[1])
