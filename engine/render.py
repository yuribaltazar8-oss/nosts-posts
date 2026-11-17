"""Nostos Livraria - gerador de imagens para o Instagram.

Uso:  python3 engine/render.py spec.json
Lê uma especificação JSON e grava as imagens JPEG na pasta "out" indicada.

Formatos ("size"):  feed = 1080x1350 (4:5)   story = 1080x1920 (9:16)
Estilos ("style"):
  page   - página de livro (papel envelhecido, Garamond, número de página)
  design - cartão limpo da marca (creme, tinta, vermelho Nostos, Inter)
  photo  - foto real da pasta fotos/ com texto e assinatura Nostos

Tipos de página ("kind"):
  title    {"lines": [...]}                         título grande
  section  {"title": "...", "body": "..."}          título + texto corrido
  word     {"word","origin","meaning","body":[...]} palavra com significado
  closing  {"lines": [...], "tail": "..."}          fecho centrado
  quote    {"text": "...", "sub": "..."}            frase forte (design/photo)
  book     {"title","author","body","cta"}          menção de livro do catálogo
"""
import json, os, random, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, "fonts")
CREAM = (234, 222, 198)
INK = (34, 29, 24)
RED = (139, 30, 30)
GREY = (110, 104, 96)
SIZES = {"feed": (1080, 1350), "story": (1080, 1920)}
WA = "WhatsApp 87 943 1217"


def serif(size, w=400, it=False):
    f = ImageFont.truetype(os.path.join(FD, "EBGi.ttf" if it else "EBG.ttf"), size)
    f.set_variation_by_axes([w])
    return f


def sans(size, heavy=False):
    return ImageFont.truetype(os.path.join(FD, "Inter-ExtraBold.otf" if heavy else "Inter-Medium.otf"), size)


def wrap(d, text, f, maxw):
    out = []
    for para in text.split("\n"):
        if not para.strip():
            out.append("")
            continue
        line = ""
        for w in para.split():
            t = (line + " " + w).strip()
            if d.textlength(t, font=f) <= maxw:
                line = t
            else:
                out.append(line)
                line = w
        out.append(line)
    return out


# ---------------- papel / textura ----------------
FILLER = ("o tempo passava devagar naquela casa e ninguém se lembrava ao certo de quando as janelas "
          "tinham sido abertas havia cartas guardadas numa gaveta e uma cadeira junto à porta onde a avó "
          "se sentava a ver a chuva cair sobre o quintal e as palavras ficavam no ar").split()


def paper(W, H, seed):
    r = np.random.default_rng(seed)
    small = r.normal(0, 1, (14, 11))
    m = np.array(Image.fromarray(((small - small.min()) / np.ptp(small) * 255).astype(np.uint8))
                 .resize((W, H), Image.BICUBIC), float) / 255 - 0.5
    fine = r.normal(0, 1, (H, W))
    img = np.zeros((H, W, 3))
    for c in range(3):
        img[..., c] = CREAM[c] + m * 10 + fine * 4.2
    yy, xx = np.mgrid[0:H, 0:W]
    dd = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    img *= (1 - 0.16 * np.clip(dd, 0, 1.4) ** 2)[..., None]
    img[:, :60] *= np.linspace(0.9, 1, 60)[None, :, None]
    # texto do verso a transparecer
    rr = random.Random(seed)
    layer = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(layer)
    f = serif(34)
    y = 70
    while y < H - 60:
        x, line = 70, []
        while True:
            w = rr.choice(FILLER)
            tw = d.textlength(w + " ", font=f)
            if x + tw > W - 80:
                break
            line.append(w)
            x += tw
        d.text((70, y), " ".join(line), font=f, fill=255)
        y += 50
    layer = layer.transpose(Image.FLIP_LEFT_RIGHT).filter(ImageFilter.GaussianBlur(1.6))
    a = np.array(layer, float) / 255 * 0.055
    img = img * (1 - a[..., None]) + np.array([90, 80, 66]) * a[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def flat(W, H, seed):
    r = np.random.default_rng(seed)
    base = np.array([245, 241, 234], float)
    img = base[None, None, :] + r.normal(0, 1.6, (H, W, 1))
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def ink_on(img, draw_fn, color=INK, blur=0.45, alpha=0.93):
    W, H = img.size
    layer = Image.new("L", (W, H), 0)
    draw_fn(ImageDraw.Draw(layer))
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    a = np.array(layer, float) / 255 * alpha
    arr = np.array(img, float)
    arr = arr * (1 - a[..., None]) + np.array(color) * a[..., None]
    return Image.fromarray(arr.astype(np.uint8))


# ---------------- estilo PAGE ----------------
def page_layers(p, W, H, n):
    """devolve lista de (cor, função de desenho) para a página"""
    M = 120
    story = H > 1500
    top = 300 if story else 0

    def center(d, y, t, f):
        d.text(((W - d.textlength(t, font=f)) / 2, y), t, font=f, fill=255)

    def body(d, y, text, size=42, lh=1.5, italic=False):
        f = serif(size, it=italic)
        for ln in wrap(d, text, f, W - 2 * M):
            if ln:
                d.text((M, y), ln, font=f, fill=255)
            y += int(size * lh)
        return y

    def chrome(d):
        center(d, 150 if story else 74, "N O S T O S   ·   L I V R A R I A", serif(24, 500))
        if p.get("page_number", True):
            center(d, H - (200 if story else 104), str(n), serif(32))

    k = p["kind"]

    def draw(d):
        chrome(d)
        if k == "title":
            f = serif(p.get("size", 108), 500)
            lines = p["lines"]
            y = (H - len(lines) * int(f.size * 1.18)) / 2 - 40
            for ln in lines:
                d.text((M, y), ln, font=f, fill=255)
                y += int(f.size * 1.18)
        elif k == "section":
            d.text((M, 250 + top), p["title"], font=serif(p.get("title_size", 62), 600), fill=255)
            body(d, 400 + top, p["body"], p.get("size", 44), 1.55)
        elif k == "word":
            center(d, 250 + top, p["word"], serif(118, 600))
            y = 410 + top
            for t in [p.get("origin"), p.get("meaning")]:
                if t:
                    center(d, y, t, serif(36, it=True))
                    y += 52
            d.line([(W / 2 - 40, y + 50), (W / 2 + 40, y + 50)], fill=255, width=2)
            y += 120
            for i, para in enumerate(p.get("body", [])):
                last = i == len(p["body"]) - 1 and p.get("italic_last", True)
                y = body(d, y, para, 42, 1.5, italic=last) + 30
        elif k == "closing":
            f = serif(64, 500)
            lines = p["lines"]
            y = H / 2 - len(lines) * 45 - 60
            for ln in lines:
                center(d, y, ln, f)
                y += 90
            if p.get("tail"):
                center(d, y + 60, p["tail"], serif(42, it=True))
        elif k == "book":
            d.text((M, 250 + top), p.get("kicker", "Leitura recomendada"), font=serif(32, it=True), fill=255)
            y = 310 + top
            for ln in wrap(d, p["title"], serif(78, 600), W - 2 * M):
                d.text((M, y), ln, font=serif(78, 600), fill=255)
                y += 92
            if p.get("author"):
                d.text((M, y + 6), p["author"], font=serif(38, it=True), fill=255)
                y += 70
            d.line([(M, y + 30), (M + 80, y + 30)], fill=255, width=2)
            y = body(d, y + 80, p.get("body", ""), 42, 1.5)
            if p.get("cta"):
                d.text((M, y + 40), p["cta"], font=serif(36, it=True), fill=255)
        elif k == "quote":
            y = H / 2 - 200
            for ln in wrap(d, p["text"], serif(70, 500), W - 2 * M):
                center(d, y, ln, serif(70, 500))
                y += 92
            if p.get("sub"):
                center(d, y + 50, p["sub"], serif(40, it=True))
    return draw


# ---------------- estilo DESIGN ----------------
def design_draw(img, p, n, total):
    W, H = img.size
    d = ImageDraw.Draw(img)
    M = 96
    story = H > 1500
    d.text((M, 90 if not story else 150), f"{n:02d} / {total:02d}" if total > 1 else "", font=sans(26), fill=GREY)
    y = (230 if not story else 420)
    k = p["kind"]
    if k in ("quote", "title"):
        lines = p.get("lines") or wrap(d, p["text"], sans(p.get("size", 100), True), W - 2 * M)
        red_from = p.get("red_from", len(lines))
        sz = p.get("size", 100)
        for i, ln in enumerate(lines):
            d.text((M, y), ln, font=sans(sz, True), fill=RED if i >= red_from else INK)
            y += int(sz * 1.12)
        y += 40
        d.rectangle([M, y, M + 90, y + 8], fill=RED)
        y += 58
        for s in p.get("sub", []) if isinstance(p.get("sub"), list) else ([p["sub"]] if p.get("sub") else []):
            for ln in wrap(d, s, sans(40), W - 2 * M):
                d.text((M, y), ln, font=sans(40), fill=GREY)
                y += 56
    elif k == "book":
        d.text((M, y), p.get("kicker", "Leitura recomendada"), font=sans(30), fill=GREY)
        y += 60
        for ln in wrap(d, p["title"], serif(84, 600), W - 2 * M):
            d.text((M, y), ln, font=serif(84, 600), fill=INK)
            y += 96
        if p.get("author"):
            y += 24
            d.text((M, y), p["author"], font=sans(34), fill=GREY)
            y += 70
        d.rectangle([M, y + 10, M + 90, y + 18], fill=RED)
        y += 70
        for ln in wrap(d, p.get("body", ""), sans(40), W - 2 * M):
            d.text((M, y), ln, font=sans(40), fill=INK)
            y += 58
    if p.get("cta") or (n == total and p.get("show_contact", True)):
        d.text((M, H - (330 if not story else 440)), "Encomende pelo WhatsApp", font=sans(30), fill=GREY)
        d.text((M, H - (286 if not story else 396)), "87 943 1217", font=sans(64, True), fill=RED)
    d.line([M, H - 190, W - M, H - 190], fill=(200, 192, 180), width=2)
    x = M
    for ch in "NOSTOS":
        d.text((x, H - 160), ch, font=serif(64, 700), fill=INK)
        x += d.textlength(ch, font=serif(64, 700)) + 14
    d.text((M, H - 72), "LÁ LIVRARIA MZ  ·  MAPUTO", font=sans(24), fill=GREY)
    if n < total:
        a = "desliza  →"
        d.text((W - M - d.textlength(a, font=sans(28)), H - 140), a, font=sans(28), fill=RED)
    return img


# ---------------- estilo PHOTO ----------------
def photo_draw(W, H, p, root):
    src = Image.open(os.path.join(root, p["photo"])).convert("RGB")
    img = ImageOps.fit(src, (W, H), Image.LANCZOS)
    # escurecer a metade de baixo para o texto respirar
    grad = np.linspace(0, 1, H) ** 1.6
    arr = np.array(img, float) * (1 - 0.62 * grad)[:, None, None]
    img = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(img)
    M = 96
    text = p.get("text", "")
    f = serif(p.get("size", 72), 500)
    lines = wrap(d, text, f, W - 2 * M)
    y = H - 300 - len(lines) * int(f.size * 1.2)
    for ln in lines:
        d.text((M, y), ln, font=f, fill=(250, 245, 236))
        y += int(f.size * 1.2)
    if p.get("sub"):
        d.text((M, y + 20), p["sub"], font=serif(38, it=True), fill=(230, 222, 206))
    x = M
    for ch in "NOSTOS":
        d.text((x, H - 150), ch, font=serif(44, 700), fill=(250, 245, 236))
        x += d.textlength(ch, font=serif(44, 700)) + 10
    d.text((M, H - 92), "Lá Livraria MZ · " + WA, font=sans(24), fill=(220, 212, 198))
    return img


def render(spec, root):
    W, H = SIZES[spec.get("size", "feed")]
    style = spec.get("style", "page")
    out = os.path.join(root, spec["out"])
    os.makedirs(out, exist_ok=True)
    pages = spec["pages"]
    start = spec.get("start_page", 1)
    seed0 = spec.get("seed", random.randint(1, 10 ** 6))
    files = []
    for i, p in enumerate(pages):
        n = start + i
        if style == "page":
            img = paper(W, H, seed0 + i)
            img = ink_on(img, page_layers(p, W, H, n))
            img = img.rotate(0.25, resample=Image.BICUBIC, fillcolor=(200, 190, 170))
        elif style == "design":
            img = design_draw(flat(W, H, seed0 + i), p, i + 1, len(pages))
        elif style == "photo":
            img = photo_draw(W, H, p, root)
        else:
            raise SystemExit("estilo desconhecido: " + style)
        fn = os.path.join(out, f"{spec.get('name', 'post')}_{i + 1}.jpg")
        img.save(fn, quality=92)
        files.append(os.path.relpath(fn, root))
    print(json.dumps(files))
    return files


if __name__ == "__main__":
    root = os.path.dirname(HERE)
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    render(spec, root)
