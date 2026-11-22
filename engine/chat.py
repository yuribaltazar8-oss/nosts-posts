"""Imagem de "conversa" (balões de chat) com as cores Nostos – para posts divertidos.

Uso:  python3 engine/chat.py spec.json
{
  "out": "posts/AAAA-MM-DD/feed_tarde_1.jpg",
  "title": "Eu a tentar comprar só UM livro",          # opcional, no topo
  "who": ["Eu", "Nostos"],                             # nomes dos dois lados (esquerda, direita)
  "msgs": [[0, "Só vou ver, não vou comprar nada."], [1, "Claro 🙂"], [0, "…manda também esse."]],
  "footer": "Leia. Regresse a si."                      # opcional
}
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


def main(path):
    s = json.load(open(path))
    im = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(im)
    y = 90
    if s.get('title'):
        ft = font('Inter-ExtraBold.otf', 64)
        for line in wrap(d, s['title'], ft, W - 160):
            d.text(((W - d.textlength(line, font=ft)) / 2, y), line, font=ft, fill=INK); y += 78
        y += 40
    fm = font('Inter-Medium.otf', 50); fn = font('Inter-Medium.otf', 28)
    who = s.get('who', ['', ''])
    for side, text in s['msgs']:
        lines = wrap(d, text, fm, 640)
        bw = max(d.textlength(l, font=fm) for l in lines) + 70; bh = len(lines) * 64 + 40
        x = 80 if side == 0 else W - 80 - bw
        if who[side]:
            nx = x + 10 if side == 0 else x + bw - 10 - d.textlength(who[side], font=fn)
            d.text((nx, y), who[side], font=fn, fill=GREY); y += 40
        d.rounded_rectangle([x, y, x + bw, y + bh], 34, fill=WHITE if side == 0 else NAVY)
        for i, l in enumerate(lines):
            d.text((x + 35, y + 20 + i * 64), l, font=fm, fill=INK if side == 0 else (251, 248, 240))
        y += bh + 34
    if s.get('footer'):
        ff = font('EBGi.ttf', 46); t = s['footer']
        d.text(((W - d.textlength(t, font=ff)) / 2, H - 120), t, font=ff, fill=NAVY)
    out = os.path.join(ROOT, s['out']) if not os.path.isabs(s['out']) else s['out']
    os.makedirs(os.path.dirname(out), exist_ok=True); im.save(out, quality=93)
    if y > H - 140: print('AVISO: texto demasiado longo, encurtar')
    print(out)


if __name__ == '__main__':
    main(sys.argv[1])
