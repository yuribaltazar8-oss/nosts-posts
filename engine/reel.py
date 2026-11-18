"""Reel com movimento real (substitui video.py para o feed).

Uso:  python3 engine/reel.py reel.json
Spec:
{
  "out": "posts/AAAA-MM-DD/feed_tarde.mp4",
  "scenes": [
    {"type": "text", "text": "Hook curto.\nSegunda linha.", "highlight": ["hook"], "size": 80,
     "bold": true, "kicker": "...", "dur": 2.2, "reveal": true},
    {"type": "book", "cover": "livros/x.jpg",            # capa REAL plana -> livro 3D a entrar em cena
     "kicker": "Livro-casa para quem...", "title": "Título", "author": "Autor",
     "line": "1 frase curta", "dur": 3, "bg": "azul"},   # bg: "creme" (padrão) ou "azul"
    {"type": "photo", "photo": "fotos/x.jpg", "text": "Frase curta", "dur": 3}   # foto REAL (Ken Burns)
  ]
}
Movimento: o texto entra parágrafo a parágrafo (já há texto no 1.º frame), cortes secos com "punch-in",
zoom contínuo da câmara, livro 3D a subir e a flutuar. 1080x1920, 30 fps, H.264 + faixa silenciosa.
Nunca usar imagens geradas por IA, capas desenhadas ou fotos da internet: só livros/ e fotos/.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import render as R  # noqa: E402

W, H, FPS = 1080, 1920, 30
BLUE = R.RED


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def camera(img, s, dy=0):
    """zoom centrado (s >= 1) + deslocamento vertical."""
    if s <= 1.0005 and dy == 0:
        return img
    w, h = int(W / s), int(H / s)
    x0, y0 = (W - w) // 2, max(0, min(H - h, (H - h) // 2 - int(dy)))
    return img.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR)


# ---------- cenas ----------
def text_states(sc, idx, total):
    """Imagens cumulativas (1 parágrafo a mais em cada) com o mesmo enquadramento."""
    p = {k: v for k, v in sc.items() if k not in ("type", "dur", "reveal")}
    p["no_footer"] = True
    full = R.nota_draw(W, H, dict(p), idx, total)
    if not sc.get("reveal", True):
        return [full]
    top = R.LAST_TOP
    paras = sc["text"].split("\n")
    cuts = [i for i, x in enumerate(paras) if x.strip()]
    if len(cuts) <= 1:
        return [full]
    states = []
    for c in cuts[:-1]:
        q = dict(p, text="\n".join(paras[:c + 1]), top=top)
        states.append(R.nota_draw(W, H, q, idx, total))
    states.append(full)
    return states


def make_text(sc, idx, total):
    states = text_states(sc, idx, total)
    dur = sc["dur"]
    n = len(states)
    step = min(0.6, (dur - 0.9) / max(1, n - 1)) if n > 1 else dur
    arr = [np.asarray(s, np.float32) for s in states]

    def frame(t):
        k = min(n - 1, int(t / step)) if n > 1 else 0
        a = arr[k]
        if k > 0:
            f = ease((t - k * step) / 0.18)
            a = arr[k - 1] * (1 - f) + arr[k] * f
        img = Image.fromarray(a.astype(np.uint8))
        s = 1.0 + 0.045 * (t / dur) + 0.07 * (1 - ease(t / 0.28))   # punch-in + zoom lento
        return camera(img, s)
    return frame


def bg_img(kind, seed):
    if kind == "azul":
        a = np.zeros((H, W, 3), np.float32) + np.array(BLUE, np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        v = 1 - 0.28 * (((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) * 2
        return Image.fromarray(np.clip(a * v[..., None], 0, 255).astype(np.uint8))
    return R.paper(W, H, seed, base=R.PAPEL_CLARO, through=0.025, vignette=0.08)


def make_book(sc, idx, total):
    dark = sc.get("bg") == "azul"
    fg = R.LOGO_CREME if dark else R.INK
    sub = (200, 205, 225) if dark else R.GREY
    base = bg_img(sc.get("bg"), 40 + idx)
    d = ImageDraw.Draw(base)
    M = 90
    y = 230
    if sc.get("kicker"):
        for ln in R.wrap(d, sc["kicker"], R.serif(52, 600, it=True), W - 2 * M):
            d.text((M, y), ln, font=R.serif(52, 600, it=True), fill=R.LOGO_CREME if dark else BLUE)
            y += 66
    top_y = y + 40
    if sc.get("cover"):
        book = R.book_mockup(Image.open(os.path.join(ROOT, sc["cover"])), 900)
    else:
        ph = Image.open(os.path.join(ROOT, sc["photo"])).convert("RGB")
        ph = ImageOps.fit(ph, (700, 920), Image.LANCZOS)
        book = Image.new("RGBA", ph.size, 0)
        m = Image.new("L", ph.size, 0)
        ImageDraw.Draw(m).rounded_rectangle([0, 0, ph.width - 1, ph.height - 1], radius=24, fill=255)
        book.paste(ph, (0, 0), m)
    # texto de baixo (aparece depois do livro)
    txt = Image.new("RGBA", (W, H), 0)
    td = ImageDraw.Draw(txt)
    ty = top_y + book.height + 30
    for ln in R.wrap(td, sc.get("title", ""), R.serif(66, 650), W - 2 * M):
        td.text(((W - td.textlength(ln, font=R.serif(66, 650))) / 2, ty), ln, font=R.serif(66, 650), fill=fg)
        ty += 76
    if sc.get("author"):
        td.text(((W - td.textlength(sc["author"], font=R.sans(34))) / 2, ty + 6), sc["author"], font=R.sans(34), fill=sub)
        ty += 70
    if sc.get("line"):
        fl = R.serif(58, 650)
        for ln in R.wrap(td, sc["line"], fl, W - 2 * M):
            td.text(((W - td.textlength(ln, font=fl)) / 2, ty + 20), ln, font=fl, fill=R.LOGO_CREME if dark else BLUE)
            ty += 72
    dur = sc["dur"]

    def frame(t):
        img = base.copy()
        e = ease(t / 0.7)
        sc_ = 0.82 + 0.18 * e + 0.03 * (t / dur)
        b = book.resize((int(book.width * sc_), int(book.height * sc_)), Image.BILINEAR)
        if e < 1:
            al = b.split()[3].point(lambda v: int(v * min(1, 0.25 + e)))
            b.putalpha(al)
        float_y = 10 * math.sin(t * 2.2)
        bx = (W - b.width) // 2
        by = int(top_y + (book.height - b.height) / 2 + 380 * (1 - e) + float_y)
        img.paste(b, (bx, by), b)
        f2 = ease((t - 0.55) / 0.35)
        if f2 > 0:
            tl = txt.copy()
            tl.putalpha(tl.split()[3].point(lambda v: int(v * f2)))
            img.paste(tl, (0, int(30 * (1 - f2))), tl)
        return camera(img, 1.0 + 0.04 * (1 - ease(t / 0.25)))
    return frame


def make_photo(sc, idx, total):
    ph = Image.open(os.path.join(ROOT, sc["photo"])).convert("RGB")
    ph = ImageOps.fit(ph, (W, H), Image.LANCZOS)
    a = np.asarray(ph, np.float32)
    g = np.linspace(0, 1, H)[:, None, None]
    a = a * (1 - 0.65 * np.clip((g - 0.45) / 0.55, 0, 1))
    base = Image.fromarray(a.astype(np.uint8))
    d = ImageDraw.Draw(base)
    M = 90
    f = R.serif(int(sc.get("size", 70) * 1.1), 600)
    lines = R.wrap(d, sc.get("text", ""), f, W - 2 * M)
    y = H - 330 - len(lines) * int(f.size * 1.3)
    for ln in lines:
        d.text((M, y), ln, font=f, fill=R.LOGO_CREME)
        y += int(f.size * 1.3)
    dur = sc["dur"]
    return lambda t: camera(base, 1.0 + 0.08 * (t / dur))


MAKERS = {"text": make_text, "book": make_book, "photo": make_photo}


def main(path):
    v = json.load(open(path, encoding="utf-8"))
    scenes = v["scenes"]
    out = os.path.join(ROOT, v["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    total = sum(s["dur"] for s in scenes)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-f", "lavfi", "-t", f"{total:.2f}",
           "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    covers = []
    base = os.path.splitext(out)[0]
    for i, sc in enumerate(scenes):
        fr = MAKERS[sc.get("type", "text")](sc, i + 1, len(scenes))
        nf = int(round(sc["dur"] * FPS))
        for k in range(nf):
            img = fr(k / FPS)
            pr.stdin.write(img.convert("RGB").tobytes())
            if k == nf - 1:   # último frame de cada cena -> .jpg (capa e verificação)
                fn = f"{base}_{i + 1}.jpg"
                img.convert("RGB").save(fn, quality=92)
                covers.append(os.path.relpath(fn, ROOT))
    pr.stdin.close()
    pr.wait()
    print(json.dumps({"video": os.path.relpath(out, ROOT), "seconds": total, "frames": covers}))


if __name__ == "__main__":
    main(sys.argv[1])
