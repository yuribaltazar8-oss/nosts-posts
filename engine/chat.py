"""Imagem de "conversa" (balões de chat) com as cores Nostos – para posts divertidos.

Uso:  python3 engine/chat.py spec.json
{
  "out": "posts/AAAA-MM-DD/feed_tarde_1.jpg",
  "title": "Eu a tentar comprar só UM livro",          # opcional, no topo
  "who": ["Eu", "Nostos"],                             # [quem envia = DIREITA, quem responde = ESQUERDA]
  "msgs": [[0, "Só vou ver, não vou comprar nada."], [1, "Claro 🙂"], [0, "…manda também esse."]],
  "footer": "Leia. Regresse a si.",                     # opcional
  "style": "nostos" | "ia" | "app",                    # "app" = parecido com a app de IA do telemóvel (genérico)                            # "ia" = conversa com uma IA (tema escuro, genérico)
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


def icon_row(d, x, y, col):
    """Ícones genéricos de acção (copiar, gosto, som, partilhar, mais) – desenhados, sem marca."""
    w = 4
    d.rounded_rectangle([x, y + 8, x + 26, y + 34], 6, outline=col, width=w)
    d.rounded_rectangle([x + 10, y, x + 36, y + 26], 6, outline=col, width=w, fill=(0, 0, 0))
    x += 80
    d.polygon([(x, y + 14), (x + 10, y + 14), (x + 18, y), (x + 24, y + 4), (x + 22, y + 14), (x + 36, y + 14),
               (x + 32, y + 34), (x, y + 34)], outline=col, width=w)
    x += 80
    d.polygon([(x, y + 12), (x + 10, y + 12), (x + 22, y + 2), (x + 22, y + 34), (x + 10, y + 24), (x, y + 24)], outline=col, width=w)
    d.arc([x + 22, y + 6, x + 36, y + 30], -60, 60, fill=col, width=w)
    x += 80
    d.line([x + 18, y, x + 18, y + 24], fill=col, width=w); d.line([x + 8, y + 10, x + 18, y, x + 28, y + 10], fill=col, width=w)
    d.line([x + 2, y + 18, x + 2, y + 34, x + 34, y + 34, x + 34, y + 18], fill=col, width=w)
    x += 80
    for k in range(3): d.ellipse([x + k * 14, y + 14, x + k * 14 + 8, y + 22], fill=col)


def render_app(s, size):
    """Estilo "app": parecido com uma app de IA no telemóvel (fundo preto, pergunta à direita num balão,
    resposta em texto corrido, ícones, barra de escrever) – genérico, SEM nome/logo de nenhuma marca."""
    im = Image.new('RGB', (W, H), (0, 0, 0)); d = ImageDraw.Draw(im)
    G = (38, 38, 40); TX = (236, 236, 236); LB = (150, 150, 155)
    d.ellipse([50, 50, 150, 150], fill=G)
    for k in range(3): d.line([78, 84 + k * 16, 122 - (k == 2) * 14, 84 + k * 16], fill=TX, width=6)
    d.rounded_rectangle([W - 290, 50, W - 50, 150], 50, fill=G)
    d.rounded_rectangle([W - 252, 78, W - 206, 124], 10, outline=TX, width=5)
    d.line([W - 232, 112, W - 200, 76], fill=TX, width=6)
    for k in range(3): d.ellipse([W - 150 + k * 22, 94, W - 138 + k * 22, 106], fill=TX)
    y = 200
    if s.get('title'):
        ft = font('Inter-ExtraBold.otf', 52)
        for line in wrap(d, s['title'], ft, W - 160):
            d.text(((W - d.textlength(line, font=ft)) / 2, y), line, font=ft, fill=TX); y += 64
        y += 30
    fm = font('Inter-Medium.otf', size); lh = int(size * 1.3)
    for side, text in s['msgs']:
        if side == 0:
            lines = wrap(d, text, fm, 620)
            bw = max(d.textlength(l, font=fm) for l in lines) + 76; bh = len(lines) * lh + 44
            d.rounded_rectangle([W - 50 - bw, y, W - 50, y + bh], min(56, bh // 2), fill=(10, 14, 110))
            for i, l in enumerate(lines): d.text((W - 50 - bw + 38, y + 22 + i * lh), l, font=fm, fill=(220, 224, 255))
            y += bh + 60
        else:
            for para in text.split('\n\n'):
                lines = wrap(d, para, fm, W - 120)
                for i, l in enumerate(lines): d.text((50, y + i * lh), l, font=fm, fill=TX)
                y += len(lines) * lh + 30
            icon_row(d, 52, y + 6, (200, 200, 205)); y += 90
    if s.get('react'):
        e = emoji(s['react'], 130)
        if e: im.paste(e, (50, y - 10), e); y += 130
    by = H - 190
    d.rounded_rectangle([50, by, W - 50, by + 130], 65, fill=(28, 28, 30), outline=(60, 60, 64), width=2)
    d.line([115, by + 65, 155, by + 65], fill=TX, width=5); d.line([135, by + 45, 135, by + 85], fill=TX, width=5)
    d.text((190, by + 42), s.get('placeholder', 'Pergunte qualquer coisa'), font=font('Inter-Medium.otf', 40), fill=LB)
    d.rounded_rectangle([W - 300, by + 38, W - 276, by + 80], 12, outline=TX, width=5)
    d.arc([W - 310, by + 58, W - 266, by + 96], 0, 180, fill=TX, width=5)
    d.ellipse([W - 185, by + 15, W - 85, by + 115], fill=(60, 90, 230))
    for k, hh in enumerate((16, 30, 22, 30, 16)): d.line([W - 160 + k * 12, by + 65 - hh, W - 160 + k * 12, by + 65 + hh], fill=WHITE, width=6)
    return im, y + 140


def main(path):
    s = json.load(open(path))
    strip = lambda t: ''.join(ch for ch in t if ord(ch) < 0x2190)   # a letra não tem emojis: tirá-los
    s['msgs'] = [[a, strip(t)] for a, t in s['msgs']]
    for size in (52, 48, 44, 40):                                   # reduzir até caber (mín. 40)
        im, y = (render_app if s.get('style') == 'app' else render)(s, size)
        if y <= H - 125: break
    else:
        print('AVISO: texto demasiado longo mesmo a 40 px – encurtar a conversa')
    out = os.path.join(ROOT, s['out']) if not os.path.isabs(s['out']) else s['out']
    os.makedirs(os.path.dirname(out), exist_ok=True); im.save(out, quality=93)
    print(out)


if __name__ == '__main__':
    main(sys.argv[1])
