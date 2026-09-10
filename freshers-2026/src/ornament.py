"""Procedural Indian ornamental elements drawn with Pillow.

Everything is rendered as an L-mode mask at 2x supersampling and downscaled,
so edges stay crisp at 300 DPI print size.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageChops

SS = 2  # supersample factor


# ---------------------------------------------------------------- geometry ---
def bezier(points, steps=120):
    """Sample an n-th order Bezier curve."""
    n = len(points) - 1
    out = []
    for i in range(steps + 1):
        t = i / steps
        x = y = 0.0
        for k, (px, py) in enumerate(points):
            b = math.comb(n, k) * (t ** k) * ((1 - t) ** (n - k))
            x += px * b
            y += py * b
        out.append((x, y))
    return out


def rotate(pts, cx, cy, ang):
    c, s = math.cos(ang), math.sin(ang)
    return [((x - cx) * c - (y - cy) * s + cx, (x - cx) * s + (y - cy) * c + cy)
            for x, y in pts]


def mirror_x(pts, axis):
    return [(2 * axis - x, y) for x, y in pts]


def _new(w, h):
    return Image.new("L", (w * SS, h * SS), 0)


def _down(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


# ------------------------------------------------------------------- motifs ---
def paisley_mask(w, h, line=0.0):
    """Classic boteh / paisley. line>0 draws it as an outline of that width."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    # teardrop body with the hooked tip
    outer = bezier([(0.50 * W, 0.98 * H), (0.03 * W, 0.72 * H),
                    (0.12 * W, 0.20 * H), (0.46 * W, 0.06 * H),
                    (0.86 * W, 0.10 * H), (0.92 * W, 0.42 * H),
                    (0.62 * W, 0.52 * H), (0.58 * W, 0.30 * H)])
    inner = bezier([(0.58 * W, 0.30 * H), (0.60 * W, 0.62 * H),
                    (0.90 * W, 0.60 * H), (0.88 * W, 0.86 * H),
                    (0.50 * W, 0.98 * H)])
    poly = outer + inner
    if line:
        d.line(poly + [poly[0]], fill=255, width=max(1, int(line * SS)), joint="curve")
    else:
        d.polygon(poly, fill=255)
    return _down(img, w, h)


def lotus_mask(size, petals=8, inner=True):
    """Rotationally symmetric lotus / rangoli rosette."""
    S = size * SS
    img = _new(size, size)
    d = ImageDraw.Draw(img)
    c = S / 2
    for i in range(petals):
        a = 2 * math.pi * i / petals
        petal = bezier([(c, c * 0.06), (c + c * 0.30, c * 0.45),
                        (c + c * 0.10, c * 0.95), (c, c),
                        (c - c * 0.10, c * 0.95), (c - c * 0.30, c * 0.45),
                        (c, c * 0.06)], steps=90)
        d.polygon(rotate(petal, c, c, a), fill=255)
    if inner:
        r = S * 0.14
        d.ellipse([c - r, c - r, c + r, c + r], fill=0)
        r2 = S * 0.07
        d.ellipse([c - r2, c - r2, c + r2, c + r2], fill=255)
    return _down(img, size, size)


def mandala_mask(size, rings=None, seed=7):
    """Concentric mandala used as a large low-opacity watermark."""
    rnd = random.Random(seed)
    S = size * SS
    img = _new(size, size)
    d = ImageDraw.Draw(img)
    c = S / 2
    lw = max(1, int(1.6 * SS))
    if rings is None:
        rings = [(0.97, 32, "temple"), (0.90, 24, "petal"), (0.80, 16, "arc"),
                 (0.66, 24, "dot"), (0.56, 12, "petal"), (0.42, 16, "arc"),
                 (0.30, 8, "petal"), (0.16, 12, "dot")]
    for frac, count, kind in rings:
        r = c * frac
        d.ellipse([c - r, c - r, c + r, c + r], outline=255, width=lw)
        for i in range(count):
            a = 2 * math.pi * i / count
            px, py = c + r * math.cos(a), c + r * math.sin(a)
            if kind == "dot":
                rr = c * 0.012
                d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=255)
            elif kind == "petal":
                pl = c * 0.075
                petal = bezier([(px, py), (px + pl * 0.7, py - pl * 0.5),
                                (px + pl * 1.5, py), (px + pl * 0.7, py + pl * 0.5),
                                (px, py)], steps=50)
                d.line(rotate(petal, px, py, a), fill=255, width=lw, joint="curve")
            elif kind == "arc":
                rr = c * 0.055
                d.arc([px - rr, py - rr, px + rr, py + rr],
                      math.degrees(a) + 200, math.degrees(a) + 340,
                      fill=255, width=lw)
            elif kind == "temple":  # kanjeevaram-style triangle border
                t = c * 0.045
                tri = [(px, py - t), (px + t * 0.8, py + t * 0.6), (px - t * 0.8, py + t * 0.6)]
                d.line(rotate(tri, px, py, a) + [rotate(tri, px, py, a)[0]],
                       fill=255, width=lw, joint="curve")
        # radial hairlines between some rings
        if kind == "arc":
            for i in range(count):
                a = 2 * math.pi * (i + .5) / count
                d.line([c + r * .82 * math.cos(a), c + r * .82 * math.sin(a),
                        c + r * 1.0 * math.cos(a), c + r * 1.0 * math.sin(a)],
                       fill=255, width=lw)
    return _down(img, size, size)


def temple_band_mask(w, h, count=None, flip=False):
    """Row of triangles - the 'temple' border of South Indian weaves."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    count = count or max(2, int(w / (h * 0.9)))
    step = W / count
    for i in range(count):
        x = i * step
        tri = ([(x, H), (x + step / 2, 0), (x + step, H)] if not flip
               else [(x, 0), (x + step / 2, H), (x + step, 0)])
        d.polygon(tri, fill=255)
    return _down(img, w, h)


def diamond_chain_mask(w, h, count=None, rule=True):
    """Thin rule with a chain of diamonds and dots - textile selvedge feel."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    cy = H / 2
    if rule:
        lw = max(1, int(H * 0.06))
        d.line([0, cy, W, cy], fill=90, width=lw)
    count = count or max(3, int(w / (h * 1.6)))
    step = W / count
    r = H * 0.32
    for i in range(count):
        cx = step * (i + 0.5)
        d.polygon([(cx, cy - r), (cx + r * 0.62, cy), (cx, cy + r), (cx - r * 0.62, cy)],
                  fill=255)
        dr = H * 0.07
        for off in (-step * 0.30, step * 0.30):
            d.ellipse([cx + off - dr, cy - dr, cx + off + dr, cy + dr], fill=200)
    return _down(img, w, h)


def divider_mask(w, h):
    """Centred lotus flanked by tapering rules - section divider."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    cy = H / 2
    lw = max(1, int(2.0 * SS))
    gap = W * 0.055
    for x0, x1 in ((0, W / 2 - gap), (W / 2 + gap, W)):
        d.line([x0, cy, x1, cy], fill=255, width=lw)
        # small terminal dots
        tx = x0 if x0 else x1
        d.ellipse([tx - 3 * SS, cy - 3 * SS, tx + 3 * SS, cy + 3 * SS], fill=255)
    for side in (-1, 1):
        cx = W / 2 + side * gap * 0.62
        r = H * 0.16
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    ls = int(h * 0.92)
    lot = lotus_mask(ls, petals=8)
    img.paste(lot.resize((ls * SS, ls * SS), Image.LANCZOS),
              (int(W / 2 - ls * SS / 2), int(cy - ls * SS / 2)),
              lot.resize((ls * SS, ls * SS), Image.LANCZOS))
    return _down(img, w, h)


def corner_mask(size, seed=3):
    """Quarter mandala + paisley for the poster corners."""
    S = size * SS
    img = _new(size, size)
    d = ImageDraw.Draw(img)
    lw = max(1, int(1.8 * SS))
    # alternating plain rules and beaded rings
    for frac, beads in ((1.00, 0), (0.90, 14), (0.74, 0), (0.58, 10), (0.40, 0)):
        r = S * frac
        d.arc([-r, -r, r, r], 0, 90, fill=255, width=lw)
        for i in range(beads):
            a = math.pi / 2 * (i + 0.5) / beads
            px, py = r * math.cos(a), r * math.sin(a)
            rr = S * 0.011
            d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=255)
    # petal scallops riding the outer ring
    r = S * 0.74
    for i in range(9):
        a = math.pi / 2 * (i + 0.5) / 9
        px, py = r * math.cos(a), r * math.sin(a)
        rr = S * 0.055
        d.arc([px - rr, py - rr, px + rr, py + rr],
              math.degrees(a) - 80, math.degrees(a) + 80, fill=210, width=lw)
    # small lotus in the inner corner
    ls = int(size * 0.26)
    lot = lotus_mask(ls, petals=6).resize((ls * SS, ls * SS), Image.LANCZOS)
    img.paste(lot, (int(S * 0.06), int(S * 0.06)), lot)
    return _down(img, size, size)


# -------------------------------------------------------------------- arch ---
def arch_mask(w, h, cusps=11, arch_frac=0.42):
    """Cusped (multifoil) Mughal arch: rectangle below, scalloped ogee above."""
    W, H = w * SS, h * SS
    img = _new(w, h)
    d = ImageDraw.Draw(img)
    ys = H * arch_frac          # springing line
    apex = H * 0.004
    A = ys - apex
    # ogee rise from the springing, meeting the apex on a near-vertical tangent
    left = bezier([(0, ys), (0, ys - A * 0.60),
                   (W * 0.33, apex + A * 0.60), (W * 0.487, apex + A * 0.26),
                   (W / 2, apex)], steps=300)
    right = list(reversed(mirror_x(left, W / 2)))
    poly = [(0, H)] + left + right + [(W, H)]
    d.polygon(poly, fill=255)
    # scallop the arch curve into cusps (skip the springing and the apex)
    path = left + right
    lo, hi = int(len(path) * 0.06), int(len(path) * 0.94)
    r = W * 0.0135
    span = hi - lo
    idxs = [lo + int((i + 0.5) * span / cusps) for i in range(cusps)]
    for i in idxs:
        px, py = path[i]
        d.ellipse([px - r, py - r, px + r, py + r], fill=0)
    return _down(img, w, h)


def outline_of(mask, thickness=6, outward=True):
    """Ring/outline mask derived from a filled shape mask."""
    k = thickness * 2 + 1
    if outward:
        big = mask.filter(ImageFilter.MaxFilter(k))
        return ImageChops.subtract(big, mask)
    small = mask.filter(ImageFilter.MinFilter(k))
    return ImageChops.subtract(mask, small)


# ---------------------------------------------------------------- textures ---
def grain(w, h, amount=10, seed=11):
    rnd = random.Random(seed)
    n = Image.new("L", (w // 2, h // 2))
    n.putdata([rnd.randint(128 - amount, 128 + amount) for _ in range(
        (w // 2) * (h // 2))])
    return n.resize((w, h), Image.BILINEAR)


def radial_gradient(w, h, inner=255, outer=0, power=1.5, cx=0.5, cy=0.42):
    g = Image.new("L", (w, h))
    px = g.load()
    ccx, ccy = w * cx, h * cy
    maxd = math.hypot(max(ccx, w - ccx), max(ccy, h - ccy))
    step = 2
    for y in range(0, h, step):
        for x in range(0, w, step):
            t = (math.hypot(x - ccx, y - ccy) / maxd) ** power
            v = int(inner + (outer - inner) * min(1.0, t))
            for dy in range(step):
                for dx in range(step):
                    if x + dx < w and y + dy < h:
                        px[x + dx, y + dy] = v
    return g.filter(ImageFilter.GaussianBlur(6))


def linear_gradient(w, h, stops, horizontal=False):
    """stops: list of (pos 0-1, (r,g,b))."""
    n = w if horizontal else h
    img = Image.new("RGB", (1, n) if not horizontal else (n, 1))
    px = img.load()
    for i in range(n):
        t = i / max(1, n - 1)
        prev = stops[0]
        nxt = stops[-1]
        for j in range(len(stops) - 1):
            if stops[j][0] <= t <= stops[j + 1][0]:
                prev, nxt = stops[j], stops[j + 1]
                break
        span = max(1e-6, nxt[0] - prev[0])
        f = (t - prev[0]) / span
        col = tuple(int(prev[1][c] + (nxt[1][c] - prev[1][c]) * f) for c in range(3))
        px[(i, 0) if horizontal else (0, i)] = col
    return img.resize((w, h), Image.BILINEAR)
