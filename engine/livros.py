"""Reel "Livros para quem..." (estilo lista de livros, cortes no ritmo) com a marca Nostos.

Uso:  python3 engine/livros.py spec.json
Spec:
{
  "out": "posts/AAAA-MM-DD/feed_tarde.mp4",
  "bpm": 112,                                   # ritmo dos cortes (1 batida = 60/bpm s)
  "intro": {"text": "Livros para quem\\nrecebe e não vê o dinheiro", "bold": ["dinheiro"],
            "clip": "fotos/videos/pilha.mp4", "start": 0, "beats": 5},     # ou "cover": "livros/x.jpg"
  "books": [
    {"clip": "fotos/videos/livro1.mp4", "start": 1.2, "line": "Para perceber porque o salário foge.", "beats": 4},
    {"cover": "livros/x.jpg", "line": "...", "beats": 4}                    # sem vídeo: livro 3D real
  ],
  "outro": {"text": "Leia. Regresse a si.", "sub": "Peça no WhatsApp 87 943 1217", "beats": 5}
}
- "clip": vídeo REAL filmado pelo Yuri (mão a segurar o livro, estante, entrega) em fotos/videos/.
- "cover": capa REAL de livros/ -> livro 3D sobre creme Nostos.
Nunca imagens geradas por IA, capas desenhadas ou vídeos/fotos da internet.
Movimento: título a escrever-se (máquina de escrever), corte seco a cada livro com punch-in,
frase de cada livro a entrar em 0,2 s, contador discreto, fecho em azul Nostos com o logo.
"""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import render as R  # noqa: E402

W, H, FPS = 1080, 1920, 30
BLUE, CREAM, INK = R.RED, R.LOGO_CREME, R.INK


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def clip_frames(path, start, dur):
    cmd = ["ffmpeg", "-loglevel", "error", "-ss", str(start), "-t", f"{dur:.3f}", "-i", os.path.join(ROOT, path),
           "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    n = len(raw) // (W * H * 3)
    fr = [Image.frombuffer("RGB", (W, H), raw[i * W * H * 3:(i + 1) * W * H * 3]) for i in range(n)]
    need = int(round(dur * FPS))
    while len(fr) < need:          # clip curto: congela o último frame
        fr.append(fr[-1])
    return fr[:need]


def cover_frames(path, dur, seed):
    base = R.paper(W, H, seed, base=R.PAPEL_CLARO, through=0.025, vignette=0.12)
    book = R.book_mockup(Image.open(os.path.join(ROOT, path)), 1050)
    out = []
    for k in range(int(round(dur * FPS))):
        t = k / FPS
        img = base.copy()
        s = 0.97 + 0.04 * (t / dur)
        b = book.resize((int(book.width * s), int(book.height * s)), Image.BILINEAR)
        b = b.rotate(1.2 * math.sin(t * 2.0), resample=Image.BICUBIC, expand=True)
        img.paste(b, ((W - b.width) // 2, int(H * 0.56 - b.height / 2 + 10 * math.sin(t * 2.4))), b)
        out.append(img)
    return out


def photo_frames(path, dur, focus=(0.5, 0.5), z=(1.0, 1.14)):
    """Foto REAL (fotos/ ou livros/) com movimento de câmara (Ken Burns), recortada a 9:16."""
    ph = ImageOps.fit(Image.open(os.path.join(ROOT, path)).convert("RGB"), (W, H), Image.LANCZOS, centering=focus)
    out = []
    n = int(round(dur * FPS))
    for k in range(n):
        s = z[0] + (z[1] - z[0]) * (k / max(1, n - 1))
        w, h = int(W / s), int(H / s)
        cx, cy = focus[0] * W, focus[1] * H
        x0 = int(min(max(0, cx - w / 2), W - w)); y0 = int(min(max(0, cy - h / 2), H - h))
        out.append(ph.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR))
    return out


def source(sc, dur, seed):
    if sc.get("photo"):
        return photo_frames(sc["photo"], dur, tuple(sc.get("focus", (0.5, 0.5))), tuple(sc.get("zoom", (1.0, 1.14))))
    if sc.get("clip"):
        return clip_frames(sc["clip"], sc.get("start", 0), dur)
    if sc.get("cover"):
        return cover_frames(sc["cover"], dur, seed)
    return [R.paper(W, H, seed, base=R.PAPEL_CLARO, through=0.025, vignette=0.12)] * int(round(dur * FPS))


def punch(img, t):
    s = 1.0 + 0.06 * (1 - ease(t / 0.22))
    if s < 1.001:
        return img
    w, h = int(W / s), int(H / s)
    return img.crop(((W - w) // 2, (H - h) // 2, (W - w) // 2 + w, (H - h) // 2 + h)).resize((W, H), Image.BILINEAR)


def top_shade(img, strength=0.55):
    a = np.asarray(img, np.float32)
    g = np.clip(1 - np.linspace(0, 1, H) / 0.42, 0, 1)[:, None, None]
    return Image.fromarray((a * (1 - strength * g)).astype(np.uint8))


def text_layer(lines, bold, size, y, visible_chars=None, dark=True, center=True):
    """Texto Garamond com sombra suave. bold: palavras em negrito (itálico no fundo claro = azul)."""
    lay = Image.new("RGBA", (W, H), 0)
    d = ImageDraw.Draw(lay)
    f, fb = R.serif(size, 500), R.serif(size, 700)
    col = CREAM if dark else INK
    hl = set(w.lower().strip(".,!?:;") for w in bold)
    shown = 0
    for ln in lines:
        words = ln.split(" ")
        widths = [d.textlength(w + " ", font=fb if w.lower().strip(".,!?:;") in hl else f) for w in words]
        x = (W - sum(widths) + d.textlength(" ", font=f)) / 2 if center else 90
        for w, wd in zip(words, widths):
            isb = w.lower().strip(".,!?:;") in hl
            txt = w
            if visible_chars is not None:
                rem = visible_chars - shown
                if rem <= 0:
                    txt = ""
                elif rem < len(w):
                    txt = w[:rem]
            shown += len(w) + 1
            if txt:
                d.text((x, y), txt, font=fb if isb else f, fill=(col if dark or not isb else BLUE))
            x += wd
        y += int(size * 1.22)
    if dark:
        sh = lay.split()[3].filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.75))
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 255))
        shadow.putalpha(sh)
        out = Image.new("RGBA", (W, H), 0)
        out.alpha_composite(shadow)
        out.alpha_composite(lay)
        return out
    return lay


def wrap_lines(text, size, maxw=W - 180):
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    out = []
    for para in text.split("\n"):
        out += R.wrap(d, para, R.serif(size, 700), maxw) or [""]
    return out


def pill(img, text, y, n=None, inv=False):
    d = ImageDraw.Draw(img)
    f = R.sans(30, True)
    tw = d.textlength(text, font=f)
    x0 = (W - tw) / 2 - 30
    d.rounded_rectangle([x0, y, x0 + tw + 60, y + 62], radius=31, fill=BLUE if inv else CREAM)
    d.text((x0 + 30, y + 13), text, font=f, fill=CREAM if inv else BLUE)


def card(img, lines, size, label, min_h=0, alpha=1.0, dy=0, visible=None, bold=(), top=110):
    """Cartão creme Nostos no topo: rótulo azul + texto Garamond tinta, palavras-chave a azul."""
    y0 = top + dy
    h = max(min_h, 120 + len(lines) * int(size * 1.22) + 50)
    lay = Image.new("RGBA", (W, H), 0)
    sh = Image.new("L", (W, H), 0)
    ImageDraw.Draw(sh).rounded_rectangle([60, y0 + 14, W - 60, y0 + h + 14], radius=34, fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 255)); shadow.putalpha(sh)
    lay.alpha_composite(shadow)
    ImageDraw.Draw(lay).rounded_rectangle([60, y0, W - 60, y0 + h], radius=34, fill=CREAM + (255,))
    tl = text_layer(lines, bold, size, y0 + 118, visible_chars=visible, dark=False)
    lay.alpha_composite(tl)
    if label:
        pill_l = Image.new("RGBA", (W, H), 0)
        pill(pill_l, label, y0 + 34, inv=True)
        lay.alpha_composite(pill_l)
    if alpha < 1:
        lay.putalpha(lay.split()[3].point(lambda a: int(a * alpha)))
    img = img.convert("RGBA"); img.alpha_composite(lay); return img.convert("RGB")


def main(path):
    v = json.load(open(path, encoding="utf-8"))
    beat = 60.0 / v.get("bpm", 112)
    out = os.path.join(ROOT, v["out"])
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if v.get("scenes"):
        scenes = [(sc["kind"], sc) for sc in v["scenes"]]
    else:
        scenes = [("intro", v["intro"])] + [("book", b) for b in v.get("books", [])] + [("outro", v["outro"])]
    v.setdefault("books", [sc for k, sc in scenes if k == "book"])
    total = sum(s["beats"] * beat for _, s in scenes)
    audio = ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]
    if v.get("music", "afro"):   # batida original Nostos (engine/musica.py), no mesmo bpm dos cortes
        import musica
        wav = os.path.splitext(out)[0] + "_musica.wav"
        musica.save(musica.make(total + 0.1, v.get("bpm", 112), v.get("music", "afro"), v.get("seed", 7)), wav)
        audio = ["-i", wav]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"] + audio + [
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    thumbs, nb = [], len(v["books"])
    bi = 0
    for kind, sc in scenes:
        dur = sc["beats"] * beat
        nf = int(round(dur * FPS))
        if kind == "text":   # cartão nota com texto a entrar parágrafo a parágrafo (engine/reel.py)
            import reel
            q = dict(sc, dur=dur)
            fr = reel.make_text(q, 1, 1)
            for k in range(nf):
                img = fr(k / FPS).convert("RGB")
                pr.stdin.write(img.tobytes())
                if k == int(nf * 0.9):
                    fn = f"{os.path.splitext(out)[0]}_{len(thumbs) + 1}.jpg"
                    img.save(fn, quality=92); thumbs.append(os.path.relpath(fn, ROOT))
            continue
        if kind == "outro":
            base = Image.new("RGB", (W, H), BLUE)
            logo = Image.open(os.path.join(HERE, "logo_azul.jpg")).convert("RGB").resize((420, 420), Image.LANCZOS)
            frames = [base] * nf
        else:
            frames = source(sc, dur, 77 + bi)
        if kind == "book":
            bi += 1
        dark = bool(sc.get("clip") or sc.get("photo")) or kind == "outro"
        lines = wrap_lines(sc.get("text") or sc.get("line", ""), 74 if kind == "intro" else 62, W - 260)
        nchar = sum(len(l) + 1 for l in lines)
        for k in range(nf):
            t = k / FPS
            img = frames[k].copy()
            if kind == "outro":
                e = ease(t / 0.5)
                lg = logo.resize((int(420 * (0.9 + 0.1 * e)),) * 2, Image.LANCZOS)
                img.paste(lg, ((W - lg.width) // 2, 430 + (420 - lg.height) // 2))
                tl = text_layer(lines, sc.get("bold", ["Leia.", "Regresse", "a", "si."]), 84, 980, dark=True)
                tl.putalpha(tl.split()[3].point(lambda a: int(a * ease((t - 0.15) / 0.3))))
                img = img.convert("RGBA"); img.alpha_composite(tl, (0, int(40 * (1 - ease((t - 0.15) / 0.3)))))
                img = img.convert("RGB")
                if sc.get("sub") and t > 0.5:
                    d = ImageDraw.Draw(img)
                    s = sc["sub"].replace(" ", " ") if False else sc["sub"]
                    f = R.sans(40, True)
                    d.text(((W - d.textlength(s, font=f)) / 2, 1200), s, font=f, fill=CREAM)
            else:
                if sc.get("clip") or sc.get("photo"):
                    if kind == "intro":
                        vis = int(nchar * min(1, t / max(0.6, dur * 0.45)))
                        img = card(img, lines, 74, sc.get("kicker"), sc.get("card_min", 0), visible=vis, bold=sc.get("bold", []), top=sc.get("card_y", 110))
                    else:
                        img = punch(img, t)
                        e = ease((t - 0.03) / 0.2)
                        img = card(img, lines, 62, sc.get("label", f"{bi}/{nb}"), sc.get("card_min", 0), alpha=e, dy=int(-40 * (1 - e)), bold=sc.get("bold", []), top=sc.get("card_y", 110))
                    pr.stdin.write(img.tobytes())
                    if k == min(nf - 1, int(nf * 0.7)):
                        fn = f"{os.path.splitext(out)[0]}_{len(thumbs) + 1}.jpg"
                        img.save(fn, quality=92); thumbs.append(os.path.relpath(fn, ROOT))
                    continue
                if kind == "intro":
                    vis = int(nchar * min(1, t / max(0.6, dur * 0.45)))       # máquina de escrever
                    tl = text_layer(lines, sc.get("bold", []), 74, 300, visible_chars=vis, dark=dark)
                    img = img.convert("RGBA"); img.alpha_composite(tl); img = img.convert("RGB")
                    if sc.get("kicker"):
                        pill(img, sc["kicker"], 190)
                else:
                    img = punch(img, t)
                    e = ease((t - 0.05) / 0.2)
                    tl = text_layer(lines, sc.get("bold", []), 60, 250, dark=dark)
                    tl.putalpha(tl.split()[3].point(lambda a: int(a * e)))
                    img = img.convert("RGBA"); img.alpha_composite(tl, (0, int(30 * (1 - e)))); img = img.convert("RGB")
                    pill(img, f"{bi}/{nb}", 150)
            pr.stdin.write(img.tobytes())
            if k == min(nf - 1, int(nf * 0.7)):
                fn = f"{os.path.splitext(out)[0]}_{len(thumbs) + 1}.jpg"
                img.save(fn, quality=92)
                thumbs.append(os.path.relpath(fn, ROOT))
    pr.stdin.close()
    pr.wait()
    print(json.dumps({"video": os.path.relpath(out, ROOT), "seconds": round(total, 2), "frames": thumbs}))


if __name__ == "__main__":
    main(sys.argv[1])
