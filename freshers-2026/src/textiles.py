"""Procedural regional Indian textile patterns as tileable L masks.

bandhani (Gujarat/Rajasthan), ikat (Telangana/Odisha), phulkari (Punjab),
kanjeevaram temple stripe (Tamil Nadu), paithani diamond (Maharashtra),
assamese woven band (Assam), kalamkari vine (Andhra), chikankari sprig (Awadh),
kashmiri boteh (Kashmir), pahadi/aipan grid (Uttarakhand).
"""
import math
import random
from PIL import Image, ImageDraw

import ornament as O

SS = 2


def _tile(n):
    return Image.new("L", (n * SS, n * SS), 0)


def _fin(img, n):
    return img.resize((n, n), Image.LANCZOS)


def bandhani(n=240, seed=1):
    img = _tile(n)
    d = ImageDraw.Draw(img)
    N = n * SS
    step = N / 6
    for r in range(6):
        for c in range(6):
            cx = step * (c + 0.5) + (step / 2 if r % 2 else 0)
            cy = step * (r + 0.5)
            rr = step * 0.17
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=255)
            rr2 = step * 0.30
            d.ellipse([cx - rr2, cy - rr2, cx + rr2, cy + rr2], outline=170,
                      width=max(1, int(1.4 * SS)))
    return _fin(img, n)


def ikat(n=240):
    img = _tile(n)
    d = ImageDraw.Draw(img)
    N = n * SS
    rows = 6
    step = N / rows
    lw = max(1, int(2.2 * SS))
    for r in range(rows + 1):
        y = r * step
        pts = []
        seg = N / 8
        for i in range(9):
            pts.append((i * seg, y + (step * 0.30 if i % 2 else -step * 0.30)))
        d.line(pts, fill=235, width=lw, joint="curve")
        # feathered edge dashes typical of ikat resist dyeing
        for i in range(9):
            x = i * seg
            d.line([x, y - step * 0.42, x, y - step * 0.30], fill=120, width=lw)
    return _fin(img, n)


def phulkari(n=240):
    img = _tile(n)
    d = ImageDraw.Draw(img)
    N = n * SS
    lw = max(1, int(2.0 * SS))
    step = N / 8
    for i in range(-8, 17):
        d.line([i * step, 0, i * step - N, N], fill=150, width=lw)
        d.line([i * step, 0, i * step + N, N], fill=150, width=lw)
    for r in range(4):
        for c in range(4):
            cx, cy = N / 4 * (c + 0.5), N / 4 * (r + 0.5)
            s = N * 0.055
            d.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)],
                      fill=255)
    return _fin(img, n)


def kanjeevaram(n=240):
    img = _tile(n)
    d = ImageDraw.Draw(img)
    N = n * SS
    for i in range(6):
        x = N / 6 * i
        w = N / 6 * (0.16 if i % 2 else 0.30)
        d.rectangle([x, 0, x + w, N], fill=200 if i % 2 else 120)
    band = O.temple_band_mask(n, int(n * 0.16), count=8)
    bm = band.resize((N, int(N * 0.16)), Image.LANCZOS)
    img.paste(bm, (0, int(N * 0.42)), bm)
    img.paste(bm.transpose(Image.FLIP_TOP_BOTTOM), (0, int(N * 0.80)),
              bm.transpose(Image.FLIP_TOP_BOTTOM))
    return _fin(img, n)


def paithani(n=240):
    img = _tile(n)
    d = ImageDraw.Draw(img)
    N = n * SS
    lw = max(1, int(1.8 * SS))
    step = N / 3
    for r in range(3):
        for c in range(3):
            cx, cy = step * (c + 0.5), step * (r + 0.5)
            s = step * 0.42
            d.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)],
                      outline=230, width=lw)
            s2 = step * 0.20
            d.polygon([(cx, cy - s2), (cx + s2, cy), (cx, cy + s2), (cx - s2, cy)],
                      fill=255)
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                d.line([cx, cy, cx + dx * s * 0.72, cy + dy * s * 0.72],
                       fill=140, width=lw)
    return _fin(img, n)


def assamese(n=240):
    img = _tile(n)
    d = ImageDraw.Draw(img)
    N = n * SS
    lw = max(1, int(2.0 * SS))
    for r in range(5):
        y = N / 5 * (r + 0.5)
        d.line([0, y, N, y], fill=110, width=lw)
        cnt = 6
        for c in range(cnt):
            cx = N / cnt * (c + (0.5 if r % 2 else 0.0))
            s = N * 0.036
            d.polygon([(cx, y - s), (cx + s, y), (cx, y + s), (cx - s, y)],
                      fill=250)
            d.line([cx, y - s * 2.1, cx, y + s * 2.1], fill=90, width=lw)
    return _fin(img, n)


def kalamkari(n=240):
    img = _tile(n)
    d = ImageDraw.Draw(img)
    N = n * SS
    lw = max(1, int(2.0 * SS))
    for k in range(3):
        y0 = N / 3 * (k + 0.5)
        vine = O.bezier([(0, y0), (N * 0.25, y0 - N * 0.16),
                         (N * 0.5, y0 + N * 0.16), (N * 0.75, y0 - N * 0.16),
                         (N, y0)], steps=140)
        d.line(vine, fill=210, width=lw, joint="curve")
        for i in range(6, len(vine), 22):
            x, y = vine[i]
            lr = N * 0.030
            d.ellipse([x - lr, y - lr * 1.9, x + lr, y + lr * 0.4], fill=245)
            d.ellipse([x - lr * 0.7, y + lr * 0.2, x + lr * 0.7, y + lr * 1.7],
                      outline=150, width=lw)
    return _fin(img, n)


def chikankari(n=240, seed=4):
    rnd = random.Random(seed)
    img = _tile(n)
    d = ImageDraw.Draw(img)
    N = n * SS
    lw = max(1, int(1.5 * SS))
    for r in range(5):
        for c in range(5):
            cx = N / 5 * (c + 0.5) + (N / 10 if r % 2 else 0)
            cy = N / 5 * (r + 0.5)
            pr = N * 0.030
            for i in range(5):
                a = 2 * math.pi * i / 5
                px, py = cx + pr * 1.5 * math.cos(a), cy + pr * 1.5 * math.sin(a)
                d.ellipse([px - pr, py - pr, px + pr, py + pr], outline=235,
                          width=lw)
            d.ellipse([cx - pr * .4, cy - pr * .4, cx + pr * .4, cy + pr * .4],
                      fill=255)
    return _fin(img, n)


def kashmiri(n=240):
    img = _tile(n)
    N = n * SS
    for r in range(2):
        for c in range(2):
            pw, ph = int(n * 0.40), int(n * 0.56)
            p = O.paisley_mask(pw, ph, line=1.8)
            pm = p.resize((pw * SS, ph * SS), Image.LANCZOS)
            if (r + c) % 2:
                pm = pm.transpose(Image.FLIP_LEFT_RIGHT)
            img.paste(pm, (int(N / 2 * c + N * 0.05), int(N / 2 * r + N * 0.02)), pm)
    return _fin(img, n)


def aipan(n=240):
    """Uttarakhandi aipan: dotted grid joined by looping lines."""
    img = _tile(n)
    d = ImageDraw.Draw(img)
    N = n * SS
    lw = max(1, int(2.0 * SS))
    g = 5
    step = N / g
    for r in range(g):
        for c in range(g):
            cx, cy = step * (c + 0.5), step * (r + 0.5)
            rr = N * 0.014
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=255)
    for r in range(g):
        for c in range(g):
            cx, cy = step * (c + 0.5), step * (r + 0.5)
            rr = step * 0.34
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 0, 180, fill=180, width=lw)
            d.arc([cx - rr, cy - rr, cx + rr, cy + rr], 180, 360, fill=180,
                  width=lw)
    return _fin(img, n)


ALL = [bandhani, ikat, phulkari, kanjeevaram, paithani, assamese, kalamkari,
       chikankari, kashmiri, aipan]


def patchwork(w, h, cell=250, opacity=34, seed=9, gap_opacity=60):
    """Mosaic field of regional textile tiles with fine gold seams."""
    rnd = random.Random(seed)
    tiles = [f(cell) for f in ALL]
    layer = Image.new("L", (w, h), 0)
    cols = w // cell + 2
    rows = h // cell + 2
    order = []
    for r in range(rows):
        for c in range(cols):
            # avoid the same pattern touching itself horizontally
            choices = [t for i, t in enumerate(tiles)
                       if not order or i != order[-1]]
            i = rnd.randrange(len(tiles))
            order.append(i)
            layer.paste(tiles[i], (c * cell, r * cell))
    layer = layer.point(lambda v: int(v * opacity / 255))
    seams = ImageDraw.Draw(layer)
    for c in range(cols + 1):
        seams.line([c * cell, 0, c * cell, h], fill=gap_opacity, width=2)
    for r in range(rows + 1):
        seams.line([0, r * cell, w, r * cell], fill=gap_opacity, width=2)
    return layer


if __name__ == "__main__":
    sheet = Image.new("L", (250 * 5, 250 * 2), 0)
    for i, f in enumerate(ALL):
        sheet.paste(f(250), (250 * (i % 5), 250 * (i // 5)))
    sheet.save("_textiles.png")
    patchwork(1900, 700).save("_patchwork.png")
    print("ok")
