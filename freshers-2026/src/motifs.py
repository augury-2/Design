"""Bright, contemporary Indian cultural motifs.

Everything here returns either an L-mode mask (to be filled with a colour or a
gradient by the caller) or an RGBA layer that is already coloured. Nothing is
stock art - it is all drawn procedurally with Pillow.

Motif vocabulary: rangoli medallions, mandala rosettes, Warli folk figures,
Madhubani borders, phulkari darn bands, Pattachitra scallops, Assamese woven
bands, Uttarakhandi aipan, lehariya waves, floral vines and jali lattices.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import ornament as O

SS = 2  # supersample factor


# ------------------------------------------------------------------ helpers ---
def _new(w, h):
    return Image.new("L", (w * SS, h * SS), 0)


def _down(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def _rgba(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def _rgba_down(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def lw(px):
    return max(1, int(px * SS))


# ------------------------------------------------------------ rangoli / mandala ---
def rangoli(size, palette, rings=6, petals=16, seed=5):
    """Concentric multi-colour rangoli medallion as a finished RGBA layer.

    palette: list of RGB tuples cycled outward through the rings.
    """
    rnd = random.Random(seed)
    S = size * SS
    img = _rgba(size, size)
    d = ImageDraw.Draw(img)
    c = S / 2

    specs = []
    frac = 1.0
    for i in range(rings):
        specs.append((frac, palette[i % len(palette)], i))
        frac *= rnd.uniform(0.70, 0.80)

    for frac, col, i in specs:
        r = c * frac
        kind = i % 4
        if kind == 0:  # petal ring
            n = petals if i == 0 else max(6, petals - i * 2)
            for k in range(n):
                a = 2 * math.pi * k / n
                pl = r * 0.34
                petal = O.bezier([(c, c - r), (c + pl * 0.55, c - r + pl * 0.55),
                                  (c, c - r + pl * 1.15),
                                  (c - pl * 0.55, c - r + pl * 0.55),
                                  (c, c - r)], steps=60)
                d.polygon(O.rotate(petal, c, c, a), fill=col + (255,))
        elif kind == 1:  # dotted ring on a hairline circle
            d.ellipse([c - r, c - r, c + r, c + r], outline=col + (255,),
                      width=lw(3.0))
            n = max(10, petals + 8)
            for k in range(n):
                a = 2 * math.pi * (k + 0.5) / n
                rr = r * 0.055
                px, py = c + r * math.cos(a), c + r * math.sin(a)
                d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col + (255,))
        elif kind == 2:  # scalloped ring
            n = max(8, petals - 4)
            for k in range(n):
                a = 2 * math.pi * k / n
                px, py = c + r * 0.88 * math.cos(a), c + r * 0.88 * math.sin(a)
                rr = r * 0.20
                d.arc([px - rr, py - rr, px + rr, py + rr],
                      math.degrees(a) - 150, math.degrees(a) + 150,
                      fill=col + (255,), width=lw(3.4))
        else:  # solid disc with a ring of teardrops
            d.ellipse([c - r, c - r, c + r, c + r], fill=col + (255,))
            n = max(8, petals - 2)
            for k in range(n):
                a = 2 * math.pi * (k + 0.5) / n
                rr = r * 0.16
                px, py = c + r * 0.62 * math.cos(a), c + r * 0.62 * math.sin(a)
                d.ellipse([px - rr, py - rr, px + rr, py + rr],
                          fill=(255, 255, 255, 210))
    # bright centre
    r = c * 0.09
    d.ellipse([c - r, c - r, c + r, c + r], fill=(255, 255, 255, 240))
    r2 = c * 0.045
    d.ellipse([c - r2, c - r2, c + r2, c + r2], fill=palette[0] + (255,))
    return _rgba_down(img, size, size)


def petal_burst(size, palette, petals=12, seed=2):
    """Flat lotus/marigold rosette - a single ring of bright petals."""
    S = size * SS
    img = _rgba(size, size)
    d = ImageDraw.Draw(img)
    c = S / 2
    for k in range(petals):
        a = 2 * math.pi * k / petals
        col = palette[k % len(palette)]
        petal = O.bezier([(c, c * 0.08), (c + c * 0.32, c * 0.42),
                          (c + c * 0.12, c * 0.92), (c, c * 0.98),
                          (c - c * 0.12, c * 0.92), (c - c * 0.32, c * 0.42),
                          (c, c * 0.08)], steps=80)
        d.polygon(O.rotate(petal, c, c, a), fill=col + (255,))
    r = c * 0.20
    d.ellipse([c - r, c - r, c + r, c + r], fill=(255, 255, 255, 245))
    r2 = c * 0.12
    d.ellipse([c - r2, c - r2, c + r2, c + r2], fill=palette[0] + (255,))
    return _rgba_down(img, size, size)


def quarter_rangoli(size, palette, seed=3):
    """Quarter medallion for poster corners, drawn around the (0,0) origin.

    All rings sit inside the box so nothing is clipped, and stroke weights
    scale with the requested size so the motif reads at print resolution.
    """
    S = size * SS
    img = _rgba(size, size)
    d = ImageDraw.Draw(img)
    t = max(1, int(S * 0.014))
    rings = [(0.95, 14, "petal"), (0.80, 12, "dot"), (0.66, 10, "scallop"),
             (0.52, 9, "petal"), (0.38, 8, "dot"), (0.22, 7, "scallop")]
    for i, (frac, n, kind) in enumerate(rings):
        col = palette[i % len(palette)]
        r = S * frac
        if kind == "dot":
            d.arc([-r, -r, r, r], 0, 90, fill=col + (255,), width=t)
            for k in range(n):
                a = math.pi / 2 * (k + 0.5) / n
                px, py = r * math.cos(a), r * math.sin(a)
                rr = S * 0.026
                d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col + (255,))
        elif kind == "scallop":
            for k in range(n):
                a = math.pi / 2 * (k + 0.5) / n
                px, py = r * 0.88 * math.cos(a), r * 0.88 * math.sin(a)
                rr = S * 0.062
                d.arc([px - rr, py - rr, px + rr, py + rr],
                      math.degrees(a) - 150, math.degrees(a) + 150,
                      fill=col + (255,), width=int(t * 1.3))
        else:
            for k in range(n):
                a = math.pi / 2 * (k + 0.5) / n
                pl = S * 0.115
                px, py = r * 0.90 * math.cos(a), r * 0.90 * math.sin(a)
                petal = O.bezier([(px, py), (px + pl * 0.42, py - pl * 0.34),
                                  (px + pl * 1.0, py),
                                  (px + pl * 0.42, py + pl * 0.34), (px, py)],
                                 steps=50)
                d.polygon(O.rotate(petal, px, py, a), fill=col + (255,))
    return _rgba_down(img, size, size)


# --------------------------------------------------------------------- warli ---
def warli_figure(w, h, pose=0, arms_up=True):
    """Warli folk figure: two triangles, a circle head and stick limbs."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    t = max(lw(3.0), int(W * 0.055))
    cx = W / 2
    head_r = W * 0.15
    head_y = head_r * 1.15
    d.ellipse([cx - head_r, head_y - head_r, cx + head_r, head_y + head_r],
              outline=255, width=t)
    # torso: upper and lower triangle meeting at the waist
    top = head_y + head_r
    waist = H * 0.50
    hip = H * 0.66
    tw = W * 0.30
    d.polygon([(cx, top), (cx - tw, waist), (cx + tw, waist)], outline=255,
              width=t)
    d.polygon([(cx, hip), (cx - tw, waist), (cx + tw, waist)], outline=255,
              width=t)
    d.line([cx, top, cx, hip], fill=255, width=t)
    # arms
    sy = top + (waist - top) * 0.42
    ax = W * 0.46
    if arms_up:
        d.line([cx - tw * 0.55, sy, cx - ax, sy - H * 0.14], fill=255, width=t)
        d.line([cx + tw * 0.55, sy, cx + ax, sy - H * 0.14], fill=255, width=t)
    else:
        d.line([cx - tw * 0.55, sy, cx - ax, sy + H * 0.13], fill=255, width=t)
        d.line([cx + tw * 0.55, sy, cx + ax, sy + H * 0.13], fill=255, width=t)
    # legs
    spread = W * (0.34 if pose % 2 == 0 else 0.24)
    d.line([cx, hip, cx - spread, H * 0.99], fill=255, width=t)
    d.line([cx, hip, cx + spread, H * 0.99], fill=255, width=t)
    return _down(img, w, h)


def warli_band(w, h, count=None, seed=1):
    """Row of dancing Warli figures linked hand to hand."""
    count = count or max(4, int(w / (h * 0.62)))
    img = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(img)
    fw = int(w / count)
    fh = int(h * 0.92)
    for i in range(count):
        f = warli_figure(fw, fh, pose=i, arms_up=(i % 2 == 0))
        if i % 3 == 2:
            f = f.transpose(Image.FLIP_LEFT_RIGHT)
        img.paste(f, (i * fw, int(h * 0.04)), f)
    # ground line joining the dancers
    d.line([0, h - 2, w, h - 2], fill=150, width=max(1, h // 40))
    return img


# ----------------------------------------------------------------- madhubani ---
def madhubani_band(w, h):
    """Madhubani-inspired border: lotus buds, leaves and hatched fill."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    t = max(lw(2.4), int(H * 0.055))
    n = max(3, int(w / (h * 1.25)))
    step = W / n
    d.line([0, H * 0.06, W, H * 0.06], fill=200, width=t)
    d.line([0, H * 0.94, W, H * 0.94], fill=200, width=t)
    for i in range(n):
        x0 = i * step
        cx = x0 + step / 2
        # lotus bud
        bud = O.bezier([(cx, H * 0.86), (cx - step * 0.30, H * 0.56),
                        (cx - step * 0.14, H * 0.18), (cx, H * 0.14),
                        (cx + step * 0.14, H * 0.18),
                        (cx + step * 0.30, H * 0.56), (cx, H * 0.86)], steps=90)
        d.line(bud, fill=255, width=t, joint="curve")
        # inner hatching, the signature Madhubani fill
        for k in range(1, 7):
            y = H * (0.24 + k * 0.085)
            spread = step * 0.24 * math.sin(math.pi * k / 8)
            d.line([cx - spread, y, cx + spread, y], fill=185,
                   width=max(lw(1.6), int(H * 0.032)))
        # side leaves
        for sign in (-1, 1):
            leaf = O.bezier([(cx + sign * step * 0.34, H * 0.80),
                             (cx + sign * step * 0.46, H * 0.52),
                             (cx + sign * step * 0.30, H * 0.34),
                             (cx + sign * step * 0.22, H * 0.52),
                             (cx + sign * step * 0.34, H * 0.80)], steps=60)
            d.line(leaf, fill=225, width=t, joint="curve")
        rr = step * 0.035
        d.ellipse([cx - rr, H * 0.06 - rr, cx + rr, H * 0.06 + rr], fill=255)
    return _down(img, w, h)


# ------------------------------------------------------------------ phulkari ---
def phulkari_band(w, h, seed=7):
    """Phulkari darning stitch band: chevrons of short parallel stitches."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    t = lw(2.6)
    n = max(4, int(w / (h * 0.85)))
    step = W / n
    for i in range(n):
        x0 = i * step
        for k in range(7):
            f = k / 6
            y_top = H * (0.10 + 0.34 * f)
            y_bot = H * (0.90 - 0.34 * f)
            x = x0 + step * (0.10 + 0.80 * f)
            d.line([x, y_top, x, y_bot], fill=255, width=t)
        for k in range(7):
            f = k / 6
            y_top = H * (0.10 + 0.34 * f)
            y_bot = H * (0.90 - 0.34 * f)
            x = x0 + step * (0.90 - 0.80 * f)
            d.line([x, y_top, x, y_bot], fill=190, width=t)
    return _down(img, w, h)


# ---------------------------------------------------------------- pattachitra ---
def pattachitra_band(w, h):
    """Pattachitra-inspired scalloped vine with paired petals."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    t = lw(2.6)
    n = max(3, int(w / (h * 1.5)))
    step = W / n
    spine = O.bezier([(0, H * 0.5)] + [
        (step * (i + 0.5), H * (0.22 if i % 2 == 0 else 0.78))
        for i in range(n)] + [(W, H * 0.5)], steps=260)
    d.line(spine, fill=235, width=t, joint="curve")
    for i in range(n):
        cx = step * (i + 0.5)
        cy = H * (0.22 if i % 2 == 0 else 0.78)
        for sign in (-1, 1):
            r = step * 0.16
            d.arc([cx - r + sign * r * 0.8, cy - r, cx + r + sign * r * 0.8, cy + r],
                  0, 360, fill=255, width=t)
        rr = step * 0.05
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=255)
    return _down(img, w, h)


# ------------------------------------------------------------------- assamese ---
def assamese_band(w, h):
    """Assamese mekhela woven band: stepped diamonds between guide rules."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    t = lw(2.2)
    d.line([0, H * 0.10, W, H * 0.10], fill=150, width=t)
    d.line([0, H * 0.90, W, H * 0.90], fill=150, width=t)
    n = max(4, int(w / (h * 0.8)))
    step = W / n
    for i in range(n):
        cx = step * (i + 0.5)
        cy = H * 0.5
        s = min(step * 0.42, H * 0.34)
        d.polygon([(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)],
                  outline=255, width=t)
        d.polygon([(cx, cy - s * 0.45), (cx + s * 0.45, cy),
                   (cx, cy + s * 0.45), (cx - s * 0.45, cy)], fill=255)
        # stepped shoulders
        for sign in (-1, 1):
            d.line([cx + sign * s, cy, cx + sign * s * 1.4, cy], fill=190,
                   width=t)
    return _down(img, w, h)


# ---------------------------------------------------------------------- aipan ---
def aipan_band(w, h):
    """Uttarakhandi aipan: dot grid joined by interlacing loops."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    t = lw(2.4)
    n = max(4, int(w / (h * 0.7)))
    step = W / n
    for i in range(n):
        cx = step * (i + 0.5)
        r = min(step * 0.40, H * 0.36)
        d.arc([cx - r, H * 0.5 - r, cx + r, H * 0.5 + r], 200, 340, fill=255,
              width=t)
        d.arc([cx - r, H * 0.5 - r, cx + r, H * 0.5 + r], 20, 160, fill=255,
              width=t)
        for dy in (-1, 1):
            rr = H * 0.05
            cy = H * 0.5 + dy * r * 0.98
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=255)
        rr = H * 0.07
        d.ellipse([cx - rr, H * 0.5 - rr, cx + rr, H * 0.5 + rr], fill=255)
    return _down(img, w, h)


# -------------------------------------------------------------------- lehariya ---
def lehariya_band(w, h, waves=None, amp=None):
    """Rajasthani lehariya: diagonal wave stripes."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    t = lw(5.0)
    waves = waves or max(3, int(w / 260))
    amp = amp or H * 0.30
    for k in range(5):
        y0 = H * (0.12 + k * 0.19)
        pts = []
        for i in range(waves * 12 + 1):
            x = W * i / (waves * 12)
            pts.append((x, y0 + amp * math.sin(2 * math.pi * waves * i /
                                               (waves * 12))))
        d.line(pts, fill=255 if k % 2 == 0 else 170, width=t, joint="curve")
    return _down(img, w, h)


# ----------------------------------------------------------------- floral vine ---
def floral_vine(w, h, flowers=None):
    """Indian floral vine: undulating stem, blossoms and paired leaves."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    t = lw(2.6)
    flowers = flowers or max(3, int(w / (h * 1.6)))
    step = W / flowers
    pts = []
    for i in range(flowers * 16 + 1):
        x = W * i / (flowers * 16)
        pts.append((x, H * 0.5 + H * 0.26 * math.sin(2 * math.pi * i /
                                                     (flowers * 16) * flowers)))
    d.line(pts, fill=200, width=t, joint="curve")
    for i in range(flowers):
        idx = int((i + 0.25) * 16)
        cx, cy = pts[min(idx, len(pts) - 1)]
        r = min(step * 0.20, H * 0.30)
        for k in range(6):
            a = 2 * math.pi * k / 6
            px, py = cx + r * 0.62 * math.cos(a), cy + r * 0.62 * math.sin(a)
            rr = r * 0.40
            d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=255)
        rr = r * 0.26
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=120)
        # leaf pair on the stem between blossoms
        lx = cx + step * 0.5
        ly = pts[min(int((i + 0.75) * 16), len(pts) - 1)][1]
        for sign in (-1, 1):
            leaf = O.bezier([(lx, ly), (lx + step * 0.10, ly + sign * H * 0.20),
                             (lx + step * 0.24, ly + sign * H * 0.06),
                             (lx, ly)], steps=50)
            d.polygon(leaf, fill=210)
    return _down(img, w, h)


# -------------------------------------------------------------------- garland ---
def garland_band(w, h, count=None):
    """Marigold garland: a hanging string threaded with round pom-pom flowers."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    t = max(lw(2.4), int(H * 0.05))
    count = count or max(5, int(w / (h * 0.62)))
    pts = []
    steps = count * 14
    for i in range(steps + 1):
        x = W * i / steps
        y = H * 0.30 + H * 0.14 * math.sin(2 * math.pi * i / steps * count / 2)
        pts.append((x, y))
    d.line(pts, fill=170, width=t, joint="curve")
    step = W / count
    for i in range(count):
        idx = min(int((i + 0.5) * 14), len(pts) - 1)
        cx, cy = pts[idx][0], pts[idx][1] + H * 0.30
        r = min(step * 0.30, H * 0.30)
        # stem
        d.line([cx, pts[idx][1], cx, cy], fill=150, width=t)
        # pom-pom: ring of petals plus a centre
        for k in range(9):
            a = 2 * math.pi * k / 9
            rr = r * 0.42
            px, py = cx + r * 0.60 * math.cos(a), cy + r * 0.60 * math.sin(a)
            d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=255)
        rr = r * 0.34
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=120)
        # small bud between flowers
        bx = cx + step * 0.5
        by = pts[min(int((i + 1) * 14), len(pts) - 1)][1] + H * 0.12
        br = r * 0.24
        if bx < W:
            d.ellipse([bx - br, by - br, bx + br, by + br], fill=210)
    return _down(img, w, h)


# ----------------------------------------------------------------------- jali ---
def jali(w, h, cell=120, line=3.0):
    """Interlocking star jali lattice, used as a light overlay."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    t = lw(line)
    c = cell * SS
    rows = int(H / c) + 2
    cols = int(W / c) + 2
    for r in range(rows):
        for q in range(cols):
            cx, cy = q * c + (c / 2 if r % 2 else 0), r * c
            rr = c * 0.46
            pts = []
            for k in range(16):
                a = 2 * math.pi * k / 16
                rad = rr if k % 2 == 0 else rr * 0.52
                pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
            d.line(pts + [pts[0]], fill=255, width=t, joint="curve")
    return _down(img, w, h)


# ------------------------------------------------------------- coloured bands ---
def colour_band(w, h, mask_fn, palette, bg=None, seed=0, segments=None):
    """Fill a band mask with bands of rotating colour, on an optional bg.

    Produces an RGBA layer: the mask is cut into vertical segments and each
    segment is painted a different palette colour, which makes a single motif
    read as a bright multi-colour strip.
    """
    m = mask_fn(w, h)
    layer = Image.new("RGBA", (w, h), bg + (255,) if bg else (0, 0, 0, 0))
    segments = segments or max(4, int(w / max(1, h)))
    seg_w = w / segments
    paint = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    pd = ImageDraw.Draw(paint)
    for i in range(segments):
        col = palette[i % len(palette)]
        pd.rectangle([i * seg_w, 0, (i + 1) * seg_w, h], fill=col + (255,))
    layer.paste(paint, (0, 0), m)
    return layer


def rainbow_rule(w, h, palette, radius=None):
    """Solid multi-colour bar with rounded ends."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    n = len(palette)
    seg = w / n
    for i, col in enumerate(palette):
        d.rectangle([i * seg, 0, (i + 1) * seg, h], fill=col + (255,))
    if radius is None:
        radius = h / 2
    if radius > 0:
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1],
                                              radius=int(radius), fill=255)
        img.putalpha(ImageChops.multiply(img.getchannel("A"), mask))
    return img


def _tint(col, amount):
    return tuple(int(c + (255 - c) * (1 - amount)) for c in col)


def mosaic_ribbon(w, h, fns, palette, radius=None, wash=0.13, gap=4):
    """One ribbon stitched from several folk traditions, patch by patch.

    Each patch gets its own bright colour and a pale wash of the same hue, so
    the strip reads as a mosaic of regional craft rather than a single border.
    """
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    n = len(fns)
    edges = [int(round(i * w / n)) for i in range(n + 1)]
    for i, fn in enumerate(fns):
        x0, x1 = edges[i], edges[i + 1]
        sw = max(2, x1 - x0 - (gap if i < n - 1 else 0))
        col = palette[i % len(palette)]
        patch = Image.new("RGBA", (sw, h), _tint(col, wash) + (255,))
        m = fn(sw, h)
        patch.paste(Image.new("RGBA", (sw, h), col + (255,)), (0, 0), m)
        layer.paste(patch, (x0, 0))
    radius = h // 2 if radius is None else radius
    if radius > 0:
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, w - 1, h - 1],
                                              radius=int(radius), fill=255)
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    return layer


def confetti(w, h, palette, count=180, seed=4, sizes=(10, 30)):
    """Scattered festive shapes - petals, diamonds, dots and short arcs."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(count):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        s = rnd.uniform(*sizes)
        col = palette[rnd.randrange(len(palette))]
        a = rnd.randint(120, 235)
        kind = rnd.randrange(4)
        if kind == 0:
            d.ellipse([x - s / 2, y - s / 2, x + s / 2, y + s / 2], fill=col + (a,))
        elif kind == 1:
            d.polygon([(x, y - s / 1.6), (x + s / 2.4, y), (x, y + s / 1.6),
                       (x - s / 2.4, y)], fill=col + (a,))
        elif kind == 2:
            d.arc([x - s, y - s, x + s, y + s], rnd.randint(0, 300),
                  rnd.randint(320, 620), fill=col + (a,), width=max(2, int(s / 6)))
        else:
            pts = O.bezier([(x, y), (x + s * 0.8, y - s * 0.5),
                            (x + s * 1.5, y), (x + s * 0.8, y + s * 0.5),
                            (x, y)], steps=30)
            d.polygon(pts, fill=col + (a,))
    return img


if __name__ == "__main__":
    P = [(255, 122, 0), (233, 30, 99), (156, 39, 176), (0, 172, 193),
         (67, 160, 71), (255, 193, 7)]
    sheet = Image.new("RGB", (1600, 1500), (255, 255, 255))
    sheet.paste(rangoli(420, P), (30, 30), rangoli(420, P))
    sheet.paste(petal_burst(300, P), (520, 90), petal_burst(300, P))
    q = quarter_rangoli(300, P)
    sheet.paste(q, (900, 60), q)
    y = 500
    for fn in (warli_band, madhubani_band, phulkari_band, pattachitra_band,
               assamese_band, aipan_band, lehariya_band, floral_vine):
        band = colour_band(1500, 90, fn, P)
        sheet.paste(band, (50, y), band)
        y += 120
    sheet.save("_motifs.png")
    print("ok")
