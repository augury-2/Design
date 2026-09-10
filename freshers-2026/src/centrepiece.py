"""Procedural heritage centrepiece for the arch panel.

Jali lattice + rangoli medallion + marigold swags + a row of brass diyas.
Used when photographic artwork is not available.
"""
import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter

import ornament as O
import textiles as T

SAFFRON = (232, 138, 30)
MARIGOLD = (238, 150, 34)
MARIGOLD_D = (186, 96, 20)
LEAF = (34, 82, 52)
GOLD = (201, 162, 77)
GOLD_LIGHT = (247, 228, 168)
BRASS_STOPS = [(0.0, (214, 168, 84)), (0.45, (150, 102, 40)), (1.0, (96, 60, 24))]


def jali(w, h, cell=118, opacity=34):
    """Interlocking ogee-arch lattice, as in carved sandstone jali screens."""
    layer = Image.new("L", (w, h), 0)
    cw, ch = cell, int(cell * 1.35)
    unit = O.outline_of(O.arch_mask(cw, ch, cusps=5, arch_frac=0.5), thickness=1)
    for row, y in enumerate(range(-ch, h + ch, ch)):
        off = 0 if row % 2 == 0 else cw // 2
        for x in range(-cw + off, w + cw, cw):
            layer.paste(unit, (x, y), unit)
    layer = layer.point(lambda v: int(v * opacity / 255))
    return layer


def rangoli(size):
    """Dense rangoli / mandala medallion."""
    rings = [(0.99, 40, "temple"), (0.93, 32, "dot"), (0.86, 16, "petal"),
             (0.76, 24, "arc"), (0.66, 32, "dot"), (0.58, 12, "petal"),
             (0.46, 16, "arc"), (0.36, 8, "petal"), (0.24, 12, "dot")]
    m = O.mandala_mask(size, rings=rings)
    lot = O.lotus_mask(int(size * 0.30), petals=8)
    x = (size - lot.width) // 2
    m.paste(lot, (x, x), lot)
    return m


def diya(w=190, h=118):
    """Brass oil lamp with flame. Returns (rgba image, glow mask)."""
    SS = 2
    W, H = w * SS, h * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bowl_top = H * 0.50
    # bowl
    d.polygon([(W * 0.10, bowl_top), (W * 0.90, bowl_top),
               (W * 0.74, H * 0.90), (W * 0.26, H * 0.90)],
              fill=(150, 102, 40, 255))
    d.ellipse([W * 0.10, bowl_top - H * 0.10, W * 0.90, bowl_top + H * 0.10],
              fill=(196, 148, 72, 255))
    d.ellipse([W * 0.18, bowl_top - H * 0.055, W * 0.82, bowl_top + H * 0.075],
              fill=(96, 56, 22, 255))
    # base
    d.ellipse([W * 0.24, H * 0.84, W * 0.76, H * 0.99], fill=(120, 78, 32, 255))
    # highlight
    d.arc([W * 0.14, bowl_top + H * 0.02, W * 0.86, H * 0.94],
          20, 160, fill=(226, 186, 108, 220), width=int(3 * SS))
    # wick + flame
    fx, fy = W * 0.5, bowl_top - H * 0.02
    flame = O.bezier([(fx, fy), (fx - W * 0.055, fy - H * 0.20),
                      (fx - W * 0.018, fy - H * 0.46), (fx, fy - H * 0.56)]) + \
        list(reversed(O.bezier([(fx, fy), (fx + W * 0.055, fy - H * 0.20),
                                (fx + W * 0.018, fy - H * 0.46), (fx, fy - H * 0.56)])))
    d.polygon(flame, fill=(255, 176, 46, 255))
    inner = [(x * 0.62 + fx * 0.38, y * 0.66 + fy * 0.34) for x, y in flame]
    d.polygon(inner, fill=(255, 238, 190, 255))

    img = img.resize((w, h), Image.LANCZOS)
    glow = Image.new("L", (w, h), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * 0.30, h * 0.02, w * 0.70, h * 0.62], fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(w * 0.13))
    return img, glow


def marigold(r, seed=0):
    """Single marigold bloom as an RGBA image."""
    rnd = random.Random(seed)
    SS = 2
    S = r * 2 * SS
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = S / 2
    for ring, (frac, n, col) in enumerate((
            (0.98, 13, MARIGOLD_D), (0.74, 11, MARIGOLD), (0.48, 8, SAFFRON))):
        for i in range(n):
            a = 2 * math.pi * i / n + ring * 0.4
            pr = c * frac * 0.42
            px, py = c + c * frac * 0.55 * math.cos(a), c + c * frac * 0.55 * math.sin(a)
            jitter = rnd.uniform(0.88, 1.12)
            d.ellipse([px - pr * jitter, py - pr * jitter,
                       px + pr * jitter, py + pr * jitter],
                      fill=col + (255,))
    d.ellipse([c - c * 0.20, c - c * 0.20, c + c * 0.20, c + c * 0.20],
              fill=(255, 196, 92, 255))
    return img.resize((r * 2, r * 2), Image.LANCZOS)


def swag(panel, p0, p1, sag, r=32, seed=1):
    """Hang a marigold garland along a catenary-ish arc between two points."""
    rnd = random.Random(seed)
    ctrl = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2 + sag)
    pts = O.bezier([p0, ctrl, p1], steps=200)
    step = max(1, int(len(pts) / (abs(p1[0] - p0[0]) / (r * 1.35))))
    for i, (x, y) in enumerate(pts[::step]):
        # leaf pairs between blooms
        if i % 3 == 2:
            lr = int(r * 0.72)
            lf = Image.new("RGBA", (lr * 2, lr), (0, 0, 0, 0))
            ImageDraw.Draw(lf).ellipse([0, 0, lr * 2 - 1, lr - 1],
                                       fill=LEAF + (235,))
            lf = lf.rotate(rnd.uniform(-40, 40), expand=True,
                           resample=Image.BICUBIC)
            panel.alpha_composite(lf, (int(x - lf.width / 2), int(y - lf.height / 2)))
        rr = int(r * rnd.uniform(0.85, 1.15))
        b = marigold(rr, seed=i)
        panel.alpha_composite(b, (int(x - rr), int(y - rr)))


def build(w=1900, h=1280, seed=5):
    panel = O.linear_gradient(w, h, [(0.00, (86, 15, 26)), (0.42, (64, 12, 24)),
                                     (0.74, (38, 18, 52)), (1.00, (26, 24, 62))]
                              ).convert("RGBA")

    # warm hearth glow low-centre
    g = O.radial_gradient(w, h, 255, 0, power=1.45, cx=0.5, cy=0.78)
    panel.paste(Image.new("RGB", (w, h), (190, 96, 26)), (0, 0),
                g.point(lambda v: int(v * 0.42)))

    # patchwork of regional textile patterns - the cultural mosaic itself
    pw = T.patchwork(w, h, cell=254, opacity=32, gap_opacity=46, seed=11)
    panel.paste(Image.new("RGB", (w, h), GOLD), (0, 0), pw)
    # a breath of jali lattice over it for architectural depth
    lat = jali(w, h, cell=124, opacity=18)
    panel.paste(Image.new("RGB", (w, h), (255, 226, 178)), (0, 0), lat)

    # rangoli medallion with a soft aura
    ms = 1000
    med = rangoli(ms)
    mx, my = (w - ms) // 2, int(h * 0.30) - ms // 2 + 160
    aura = Image.new("L", (w, h), 0)
    ImageDraw.Draw(aura).ellipse([mx - 40, my - 40, mx + ms + 40, my + ms + 40],
                                 fill=255)
    aura = aura.filter(ImageFilter.GaussianBlur(120))
    panel.paste(Image.new("RGB", (w, h), (210, 120, 40)), (0, 0),
                aura.point(lambda v: int(v * 0.30)))
    panel.paste(O.linear_gradient(ms, ms, [(0, GOLD_LIGHT), (0.5, GOLD),
                                           (1, (168, 122, 52))]).convert("RGBA"),
                (mx, my), med.point(lambda v: int(v * 218 / 255)))

    # marigold swags across the top
    # drape from the arch shoulders so the swags sit inside the arch opening
    swag(panel, (int(w * 0.015), int(h * 0.40)), (w // 2, int(h * 0.135)),
         sag=150, seed=2)
    swag(panel, (w // 2, int(h * 0.135)), (int(w * 0.985), int(h * 0.40)),
         sag=150, seed=3)

    # row of diyas along the base
    dw, dh = 210, 130
    ys = int(h * 0.845)
    xs = [int(w * f) for f in (0.13, 0.305, 0.5, 0.695, 0.87)]
    for i, cx in enumerate(xs):
        scale = 1.0 if i == 2 else (0.86 if abs(i - 2) == 1 else 0.74)
        img, glow = diya(int(dw * scale), int(dh * scale))
        gx, gy = cx - img.width // 2, ys - img.height // 2
        panel.paste(Image.new("RGB", (img.width, img.height), (255, 168, 70)),
                    (gx, gy - int(20 * scale)),
                    glow.point(lambda v: int(v * 0.85)))
        panel.alpha_composite(img, (gx, gy))
        # pooled light on the floor
        pw, ph = img.width * 3, 150
        fl = Image.new("L", (pw, ph), 0)
        ImageDraw.Draw(fl).ellipse([pw * 0.22, ph * 0.34, pw * 0.78, ph * 0.66],
                                   fill=255)
        fl = fl.filter(ImageFilter.GaussianBlur(38))
        panel.paste(Image.new("RGB", fl.size, (206, 112, 36)),
                    (cx - pw // 2, ys + img.height // 2 - ph // 2 + 14),
                    fl.point(lambda v: int(v * 0.34)))

    # temple border along the base
    tb = O.temple_band_mask(w, 46)
    panel.paste(O.linear_gradient(w, 46, [(0, (196, 150, 70)), (1, (140, 96, 40))]
                                  ).convert("RGBA"), (0, h - 46),
                tb.transpose(Image.FLIP_TOP_BOTTOM).point(
                    lambda v: int(v * 150 / 255)))

    panel = panel.filter(ImageFilter.UnsharpMask(2, 40, 3))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "centrepiece.png")
    panel.convert("RGB").save(out)
    print("saved", out, panel.size)
    return out


if __name__ == "__main__":
    build()
