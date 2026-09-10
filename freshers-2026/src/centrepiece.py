"""Procedural cultural-mosaic centrepiece for the arch panel.

A bright alternative to the photographic hero: a patchwork of ten regional
Indian textile patterns on a white ground, a multi-colour rangoli medallion,
marigold garland swags and a temple-triangle base band.

    python3 centrepiece.py          ->  centrepiece.png
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter

import motifs as M
import ornament as O
import textiles as T

HERE = os.path.dirname(os.path.abspath(__file__))

SAFFRON = (255, 141, 26)
ORANGE = (255, 106, 0)
MARIGOLD = (255, 178, 26)
YELLOW = (255, 203, 20)
CORAL = (255, 94, 87)
PINK = (255, 61, 133)
MAGENTA = (226, 27, 142)
PURPLE = (129, 47, 200)
ORCHID = (168, 46, 190)
ROYAL = (58, 82, 220)
CYAN = (0, 183, 226)
TURQ = (0, 197, 186)
GREEN = (54, 187, 92)
LIME = (146, 205, 44)
LEAF = (46, 160, 84)
WHITE = (255, 255, 255)

PALETTE = [SAFFRON, MAGENTA, TURQ, PURPLE, GREEN, YELLOW, ROYAL, PINK, CYAN,
           CORAL, ORCHID, LIME]


def tint(col, amount):
    return tuple(int(c + (255 - c) * (1 - amount)) for c in col)


def patchwork(w, h, cell=250, seed=11):
    """Mosaic of regional textile tiles, every patch in its own bright hue."""
    rnd = random.Random(seed)
    tiles = [f(cell) for f in T.ALL]
    layer = Image.new("RGB", (w, h), WHITE)
    cols, rows = w // cell + 2, h // cell + 2
    prev = -1
    for r in range(rows):
        for c in range(cols):
            i = rnd.randrange(len(tiles))
            while i == prev:
                i = rnd.randrange(len(tiles))
            prev = i
            col = PALETTE[(i + r * 3 + c) % len(PALETTE)]
            patch = Image.new("RGB", (cell, cell), tint(col, 0.14))
            patch.paste(Image.new("RGB", (cell, cell), tint(col, 0.90)), (0, 0),
                        tiles[i])
            layer.paste(patch, (c * cell, r * cell))
    # white seams between the patches
    d = ImageDraw.Draw(layer)
    for c in range(cols + 1):
        d.line([c * cell, 0, c * cell, h], fill=WHITE, width=6)
    for r in range(rows + 1):
        d.line([0, r * cell, w, r * cell], fill=WHITE, width=6)
    return layer


def marigold(r, seed=0, cols=(ORANGE, MARIGOLD, YELLOW)):
    """Single bright marigold bloom as an RGBA image."""
    rnd = random.Random(seed)
    SS = 2
    S = r * 2 * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = S / 2
    for ring, (frac, n, col) in enumerate(((0.98, 13, cols[0]), (0.74, 11, cols[1]),
                                          (0.48, 8, cols[2]))):
        for i in range(n):
            a = 2 * math.pi * i / n + ring * 0.4
            pr = c * frac * 0.42
            px = c + c * frac * 0.55 * math.cos(a)
            py = c + c * frac * 0.55 * math.sin(a)
            j = rnd.uniform(0.88, 1.12)
            d.ellipse([px - pr * j, py - pr * j, px + pr * j, py + pr * j],
                      fill=col + (255,))
    d.ellipse([c - c * 0.20, c - c * 0.20, c + c * 0.20, c + c * 0.20],
              fill=(255, 255, 255, 255))
    return img.resize((r * 2, r * 2), Image.LANCZOS)


def swag(panel, p0, p1, sag, r=34, seed=1, cols=(ORANGE, MARIGOLD, YELLOW)):
    """Hang a marigold garland along an arc between two points."""
    rnd = random.Random(seed)
    ctrl = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + sag)
    pts = O.bezier([p0, ctrl, p1], steps=200)
    step = max(1, int(len(pts) / (abs(p1[0] - p0[0]) / (r * 1.35))))
    for i, (x, y) in enumerate(pts[::step]):
        if i % 3 == 2:
            lr = int(r * 0.72)
            lf = Image.new("RGBA", (lr * 2, lr), (0, 0, 0, 0))
            ImageDraw.Draw(lf).ellipse([0, 0, lr * 2 - 1, lr - 1],
                                       fill=LEAF + (240,))
            lf = lf.rotate(rnd.uniform(-40, 40), expand=True,
                           resample=Image.BICUBIC)
            panel.alpha_composite(lf, (int(x - lf.width / 2),
                                       int(y - lf.height / 2)))
        rr = int(r * rnd.uniform(0.85, 1.15))
        panel.alpha_composite(marigold(rr, seed=i, cols=cols), (int(x - rr),
                                                               int(y - rr)))


def build(w=1980, h=1160, seed=5):
    panel = O.linear_gradient(w, h, [(0.0, (255, 255, 255)), (0.5, (255, 252, 246)),
                                     (1.0, (255, 246, 238))]).convert("RGBA")

    # the cultural mosaic itself: ten regional weaves, patch by patch
    pw = patchwork(w, h, cell=248, seed=11).convert("RGBA")
    panel = Image.blend(panel, pw, 0.92)

    # soft white wash in the centre so the medallion and any type stay legible
    g = O.radial_gradient(w, h, 255, 0, power=1.5, cx=0.5, cy=0.46)
    panel.paste(Image.new("RGB", (w, h), WHITE), (0, 0),
                g.point(lambda v: int(v * 0.38)))

    # jali lattice whisper for architectural depth
    lat = M.jali(w, h, cell=132, line=2.6)
    panel.paste(Image.new("RGB", (w, h), ORCHID), (0, 0),
                lat.point(lambda v: int(v * 0.10)))

    # rangoli medallion, centred
    ms = 900
    med = M.rangoli(ms, [MAGENTA, SAFFRON, TURQ, PINK, GREEN, PURPLE, CYAN],
                    rings=7)
    a = med.getchannel("A").point(lambda v: int(v * 0.92))
    med.putalpha(a)
    panel.alpha_composite(med, ((w - ms) // 2, int(h * 0.48) - ms // 2))

    # marigold swags draped from the shoulders towards the crown
    swag(panel, (int(w * 0.015), int(h * 0.34)), (w // 2, int(h * 0.10)),
         sag=140, seed=2)
    swag(panel, (w // 2, int(h * 0.10)), (int(w * 0.985), int(h * 0.34)),
         sag=140, seed=3)

    # bright temple-triangle band along the base
    band = M.colour_band(w, 54, lambda ww, hh: O.temple_band_mask(ww, hh),
                         [SAFFRON, PINK, MAGENTA, PURPLE, ROYAL, TURQ, GREEN,
                          YELLOW], segments=16)
    band = band.transpose(Image.FLIP_TOP_BOTTOM)
    panel.alpha_composite(band, (0, h - 54))

    panel = panel.filter(ImageFilter.UnsharpMask(2, 40, 3))
    out = os.path.join(HERE, "centrepiece.png")
    panel.convert("RGB").save(out)
    print("saved", out, panel.size)
    return out


if __name__ == "__main__":
    build()
