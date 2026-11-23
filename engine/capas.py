"""Capa de frente limpa a partir da foto real do livro (Yuri, 23/11/2026).

Recorta só a capa (sem mão, sem fundo, sem borrão), endireita a perspectiva e guarda
em fotos/livros/capas/<slug>.png. O reel usa depois a cena "cover" de sextante.py.

Cantos: medir à mão numa grelha (linhas de 50 px sobre a foto, ver com Read) e guardar em
data/capas.json {"slug": {"photo": ..., "quad": [x1,y1, x2,y2, x3,y3, x4,y4]}} – a detecção
automática (rembg) falha com mãos e capas claras. Cantos = só a CAPA DE FRENTE (sem lombada nem mão).

Uso:
  python3 engine/capas.py <slug> [foto] [--quad x1,y1,x2,y2,x3,y3,x4,y4]
  - foto: por defeito fotos/livros/<slug>_anuncio.jpg (ou _calmo.jpg se existir)
  - --quad: cantos manuais (sup-esq, sup-dir, inf-dir, inf-esq) em píxeis da foto ORIGINAL,
    para quando a mão tapa um canto e a detecção automática falha.
Ver SEMPRE o resultado com Read antes de usar (cantos certos, nada de mão, texto direito).
"""
import json, os, sys
import cv2
import numpy as np
from PIL import Image, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda p: p if os.path.isabs(p) else os.path.join(ROOT, p)
OUT_H = 1400


def order(pts):
    pts = np.array(pts, dtype=np.float32)
    s, d = pts.sum(1), np.diff(pts, axis=1).ravel()
    return np.array([pts[s.argmin()], pts[d.argmin()], pts[s.argmax()], pts[d.argmax()]], dtype=np.float32)


def _fit(ys, xs):
    """recta x = a*y + b (robusta: 2 passagens, tira os 20% piores)"""
    a, b = np.polyfit(ys, xs, 1)
    r = np.abs(xs - (a * ys + b)); k = r < np.percentile(r, 80)
    return np.polyfit(ys[k], xs[k], 1)


def detect_quad(img, box):
    """Cantos da capa: esquerda/direita/topo pela silhueta do livro (parte de cima, sem mão);
    base pela linha horizontal mais forte na zona de baixo (entre os dedos)."""
    from rembg import remove, new_session
    x0, y0, x1, y1 = box
    sub = img.crop(box); g = np.array(sub.convert('L'))
    m = np.array(remove(sub, session=new_session('isnet-general-use'), only_mask=True)) > 128
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    m = lab == (1 + st[1:, cv2.CC_STAT_AREA].argmax())
    rows = np.where(m.any(1))[0]; top_y = rows[0]; H = rows[-1] - top_y
    ys = np.arange(top_y + int(H * 0.08), top_y + int(H * 0.55))
    L = np.array([np.where(m[y])[0][0] for y in ys]); R = np.array([np.where(m[y])[0][-1] for y in ys])
    la, lb = _fit(ys.astype(float), L.astype(float)); ra, rb = _fit(ys.astype(float), R.astype(float))
    cols = np.arange(int(L.mean() + 0.1 * (R.mean() - L.mean())), int(R.mean() - 0.1 * (R.mean() - L.mean())))
    T = np.array([np.where(m[:, c])[0][0] for c in cols])
    ta, tb = _fit(cols.astype(float), T.astype(float))            # y = ta*x + tb
    # base: gradiente vertical forte, recta paralela ao topo, procurada na metade de baixo
    gy = np.abs(cv2.Sobel(cv2.GaussianBlur(g, (5, 5), 0).astype(float), cv2.CV_64F, 0, 1, ksize=3))
    best, by = -1, None
    for off in range(int(H * 0.55), int(H * 1.0)):
        yy = (ta * cols + tb + off).astype(int); ok = (yy > 0) & (yy < g.shape[0])
        sc = np.median(gy[yy[ok], cols[ok]]) if ok.sum() > len(cols) * 0.8 else 0
        if sc > best: best, by = sc, off
    def X(a, b, y): return a * y + b
    def cross(a, b, off):   # recta lateral x=a*y+b com y = ta*x + tb + off
        y = (ta * b + tb + off) / (1 - ta * a); return [X(a, b, y), y]
    q = [cross(la, lb, 0), cross(ra, rb, 0), cross(ra, rb, by), cross(la, lb, by)]
    return order(np.array(q) + [x0, y0])


def make(slug, photo=None, quad=None):
    if photo is None:
        c = f'fotos/livros/{slug}_calmo.jpg'
        photo = c if os.path.exists(P(c)) else f'fotos/livros/{slug}_anuncio.jpg'
    img = Image.open(P(photo)).convert('RGB')
    reg = json.load(open(P('data/capas.json')))
    if quad is None and slug in reg:                                # cantos medidos à mão (preferido)
        photo, quad = reg[slug]['photo'], reg[slug]['quad']
        img = Image.open(P(photo)).convert('RGB')
    if quad is None:                                                # automático: só como ponto de partida
        print('AVISO: sem cantos em data/capas.json – detecção automática, verificar com Read', file=sys.stderr)
        box = json.load(open(P('data/recortes.json')))[slug]       # medidas a 1350 px de largura
        s = img.width / 1350
        quad = detect_quad(img, tuple(int(v * s) for v in box))
    else:
        quad = order(np.array(quad, dtype=np.float32).reshape(4, 2))
    w = (np.linalg.norm(quad[1] - quad[0]) + np.linalg.norm(quad[2] - quad[3])) / 2
    h = (np.linalg.norm(quad[3] - quad[0]) + np.linalg.norm(quad[2] - quad[1])) / 2
    W = int(OUT_H * w / h)
    M = cv2.getPerspectiveTransform(quad, np.float32([[0, 0], [W, 0], [W, OUT_H], [0, OUT_H]]))
    flat = cv2.warpPerspective(np.array(img), M, (W, OUT_H), flags=cv2.INTER_CUBIC)
    inset = int(OUT_H * 0.006)                                      # corta a orla (fundo/plástico)
    flat = flat[inset:OUT_H - inset, inset:W - inset]
    out = Image.fromarray(flat).filter(ImageFilter.UnsharpMask(2, 80, 2))
    os.makedirs(P('fotos/livros/capas'), exist_ok=True)
    dst = P(f'fotos/livros/capas/{slug}.png'); out.save(dst)
    print(json.dumps({'slug': slug, 'quad': quad.round().astype(int).tolist(), 'out': dst}))


if __name__ == '__main__':
    a = sys.argv[1:]
    q = None
    if '--quad' in a:
        i = a.index('--quad'); q = [float(v) for v in a[i + 1].split(',')]; del a[i:i + 2]
    make(a[0], a[1] if len(a) > 1 else None, q)
