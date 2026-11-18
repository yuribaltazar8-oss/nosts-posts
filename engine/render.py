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
RED = (2, 36, 108)  # azul Nostos (cor do logo); nome mantido por compatibilidade
NAVY = RED
LOGO_CREME = (251, 248, 240)
BEIGE = (236, 225, 202)  # creme quente de papel de livro (#ECE1CA), fundo padrão do estilo nota
GREY = (110, 104, 96)
SIZES = {"feed": (1080, 1350), "story": (1080, 1920)}
WA = "WhatsApp 87 943 1217"
NAME = "Nostos Livraria MZ"
HANDLE = "@nostos_livraria_mz"


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
        for w in para.split(" "):
            if not w:
                continue
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
    base = np.array(LOGO_CREME, float)
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
    lg = Image.open(os.path.join(HERE, "logo_marca.png"))
    lg = lg.resize((int(lg.width * 140 / lg.height), 140), Image.LANCZOS)
    img.paste(lg, (M, H - 165), lg)
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
    d.text((M, H - 92), "Nostos Livraria MZ · " + WA, font=sans(24), fill=(220, 212, 198))
    return img



def book_mockup(cover, h):
    """Livro 3D a partir de uma CAPA REAL (foto/scan plano enviado pelo Yuri). Devolve RGBA."""
    cover = cover.convert("RGB")
    cw = int(h * cover.width / cover.height)
    cover = cover.resize((cw, h), Image.LANCZOS)
    spine, pages = max(10, int(cw * 0.05)), max(10, int(cw * 0.045))
    W2, H2 = cw + spine + pages + 60, h + 80
    out = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    # sombra suave no chão
    sh = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(sh).ellipse([20, h + 20, W2 - 10, h + 64], fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    x0, y0 = 20, 20
    # bloco de páginas (lado direito)
    pg = Image.new("RGB", (pages, h - 8), (238, 232, 218))
    pd = ImageDraw.Draw(pg)
    for yy in range(0, h - 8, 3):
        pd.line([(0, yy), (pages, yy)], fill=(222, 214, 198))
    out.paste(pg, (x0 + spine + cw - 4, y0 + 6))
    # lombada (cor tirada da margem esquerda da capa, mais escura)
    edge = np.array(cover.crop((0, 0, max(2, cw // 20), h))).reshape(-1, 3).mean(0) * 0.62
    sp = Image.new("RGB", (spine, h), tuple(int(c) for c in edge))
    g = np.linspace(0.75, 1.0, spine)[None, :, None]
    sp = Image.fromarray((np.array(sp, float) * g).astype(np.uint8))
    out.paste(sp, (x0, y0))
    # capa com leve dobra junto à lombada e brilho suave
    arr = np.array(cover, float)
    hinge = np.ones(cw)
    hinge[: int(cw * 0.04)] = np.linspace(0.78, 1.0, int(cw * 0.04))
    shine = 1 + 0.06 * np.exp(-((np.arange(cw) - cw * 0.12) / (cw * 0.08)) ** 2)
    arr = np.clip(arr * (hinge * shine)[None, :, None], 0, 255)
    out.paste(Image.fromarray(arr.astype(np.uint8)), (x0 + spine, y0))
    # leve rotação 3D: a aresta direita fica mais curta (livro virado para o leitor)
    book = out.crop((0, 0, W2, h + y0 + 2))
    k = 0.045
    src = [(0, 0), (book.width, 0), (book.width, book.height), (0, book.height)]
    dst = [(0, 0), (book.width, book.height * k), (book.width, book.height * (1 - k)), (0, book.height)]
    A = []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); A.append([0, 0, 0, x, y, 1, -v * x, -v * y])
    coef = np.linalg.solve(np.array(A, float), np.array([c for pt in src for c in pt], float))
    book = book.transform(book.size, Image.PERSPECTIVE, coef.tolist(), Image.BICUBIC)
    final = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    final.paste((40, 32, 24, 255), (0, 0), sh)
    final.alpha_composite(book, (0, 0))
    return final

# ---------------- estilo NOTA (fundo branco, a Nostos a escrever) ----------------
LOGO = os.path.join(HERE, "logo.png")


def avatar(size):
    """Logo oficial da Nostos (engine/logo.png), recortado em círculo. Sem logo -> None (nunca inventar um)."""
    if not os.path.exists(LOGO):
        return None
    lg = ImageOps.fit(Image.open(LOGO).convert("RGBA"), (size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size - 1, size - 1], fill=255)
    out = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    out.paste(lg, (0, 0), mask)
    return out


def _old_avatar(size):
    a = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(a)
    d.ellipse([0, 0, size - 1, size - 1], fill=INK)
    f = serif(int(size * 0.62), 600)
    t = "N"
    bb = d.textbbox((0, 0), t, font=f)
    d.text(((size - (bb[2] - bb[0])) / 2 - bb[0], (size - (bb[3] - bb[1])) / 2 - bb[1]), t, font=f, fill=CREAM)
    return a


def nota_draw(W, H, p, n, total):
    """Cartão branco tipo 'nota/tweet' assinado pela Nostos.
    p: {"text": "...", "size": 54, "highlight": ["palavra", ...], "kicker": "...", "book": {"title","author"}}"""
    bg = tuple(p.get("bg", BEIGE))
    canvas = Image.new("RGB", (W, H * 2), bg)
    d = ImageDraw.Draw(canvas)
    M = 90
    story = H > 1500
    y0 = 0
    av = avatar(96)
    tx = M
    if av is not None:
        canvas.paste(av, (M, y0), av)
        tx = M + 120
    d.text((tx, y0 + 10), NAME, font=sans(36, True), fill=(15, 15, 15))
    d.text((tx, y0 + 56), HANDLE, font=sans(30), fill=(110, 110, 110))
    y = y0 + 170
    if p.get("kicker"):
        d.text((M, y), p["kicker"], font=sans(30, True), fill=RED)
        y += 60
    size = p.get("size", 54)
    f, fb = sans(size), sans(size, True)
    hl = set(w.lower().strip(".,!?:;") for w in p.get("highlight", []))
    for para in p["text"].split("\n"):
        if not para.strip():
            y += int(size * 0.7)
            continue
        line_words, x = [], M
        for w in para.split(" "):
            if not w:
                continue
            fw = fb if w.lower().strip(".,!?:;\"“”") in hl or p.get("bold") else f
            tw = d.textlength(w + " ", font=fw)
            if x + tw > W - M and line_words:
                y += int(size * 1.38)
                x = M
            d.text((x, y), w, font=fw, fill=RED if w.lower().strip(".,!?:;\"“”") in hl else (15, 15, 15))
            x += tw
            line_words.append(w)
        y += int(size * 1.38)
    if p.get("book"):
        b = p["book"]
        y += 30
        root = os.path.dirname(HERE)
        cov = b.get("cover")  # capa REAL plana (livros/) -> livro 3D; nunca desenhar capas
        photo = b.get("photo")  # foto REAL do livro já fotografado -> usada tal como está
        cov_path = os.path.join(root, cov) if cov else None
        ph_path = os.path.join(root, photo) if photo else None
        if (cov_path and os.path.exists(cov_path)) or (ph_path and os.path.exists(ph_path)):
            ch = 540
            if cov_path and os.path.exists(cov_path):
                pic = book_mockup(Image.open(cov_path), ch - 80)
                canvas.paste(pic, (M - 20, int(y)), pic)
                pw = pic.width - 20
            else:
                pic = Image.open(ph_path).convert("RGB")
                pw = min(int(pic.width * ch / pic.height), W - 2 * M - 360)
                pic = ImageOps.fit(pic, (pw, ch), Image.LANCZOS)
                mask = Image.new("L", pic.size, 0)
                ImageDraw.Draw(mask).rounded_rectangle([0, 0, pic.width - 1, pic.height - 1], radius=18, fill=255)
                canvas.paste(pic, (M, int(y)), mask)
            tx = M + pw + 44
            ty = y + 40
            d.text((tx, ty - 6), b.get("kicker", "Disponível na Nostos"), font=sans(26), fill=GREY)
            ty += 44
            for ln in wrap(d, b["title"], serif(54, 600), W - M - tx):
                d.text((tx, ty), ln, font=serif(54, 600), fill=INK)
                ty += 62
            if b.get("author"):
                d.text((tx, ty + 8), b["author"], font=sans(30), fill=GREY)
                ty += 52
            if b.get("price"):
                d.text((tx, ty + 18), b["price"], font=sans(40, True), fill=RED)
            y += ch
        else:
            box_h = 170
            d.rounded_rectangle([M, y, W - M, y + box_h], radius=24, outline=(214, 204, 186), width=2,
                                fill=tuple(min(255, c + 8) for c in bg))
            d.rectangle([M + 30, y + 30, M + 36, y + box_h - 30], fill=RED)
            d.text((M + 62, y + 30), b["title"], font=serif(52, 600), fill=INK)
            if b.get("author"):
                d.text((M + 62, y + 98), b["author"] + ("  ·  " + b["price"] if b.get("price") else ""),
                       font=sans(30), fill=GREY)
            y += box_h
    # centrar o bloco (cabeçalho + texto) na vertical
    content_h = int(y)
    rng = np.random.default_rng(7)
    grain = np.array(bg, float)[None, None, :] + rng.normal(0, 2.2, (H, W, 1))
    img = Image.fromarray(np.clip(grain, 0, 255).astype(np.uint8))
    area = H - (260 if story else 150)
    top = max(90, int((area - content_h) / 2))
    crop = canvas.crop((0, 0, W, content_h + 10))
    cm = np.array(crop, float); diff = np.abs(cm - np.array(bg, float)).sum(2)
    img.paste(crop, (0, top), Image.fromarray((np.clip(diff * 40, 0, 255)).astype(np.uint8)))
    d = ImageDraw.Draw(img)
    # rodapé
    fy = H - (260 if story else 110)
    d.text((M, fy), "📚" if False else NAME, font=sans(26), fill=(140, 140, 140))
    if total > 1:
        t = f"{n}/{total}" + ("  →" if n < total else "")
        d.text((W - M - d.textlength(t, font=sans(28, True)), fy), t, font=sans(28, True), fill=RED if n < total else (140, 140, 140))
    else:
        t = WA
        d.text((W - M - d.textlength(t, font=sans(26)), fy), t, font=sans(26), fill=(140, 140, 140))
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
        elif style == "nota":
            img = nota_draw(W, H, p, i + 1, len(pages))
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
