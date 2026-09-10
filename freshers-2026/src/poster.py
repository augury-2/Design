"""FRESHERS 2026 - MBA Batch 2026-28 - Graphic Era (Deemed to be University), Dehradun
Theme: India's Cultural Mosaic.

Builds a 2480 x 3508 px (A4 @ 300 DPI) vertical poster:
procedural Indian ornament + AI-generated hero artwork + typographic layer.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import ornament as O

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "fonts")

W, H = 2480, 3508

# ------------------------------------------------------------------ palette ---
MAROON_TOP = (112, 21, 34)
MAROON_MID = (86, 14, 24)
MAROON_BOT = (50, 10, 17)
INDIGO = (26, 30, 74)
DEEP_GREEN = (14, 61, 48)
SAFFRON = (232, 138, 30)
TERRACOTTA = (176, 84, 52)
GOLD = (201, 162, 77)
GOLD_DEEP = (150, 106, 42)
GOLD_LIGHT = (247, 228, 168)
IVORY = (247, 240, 224)
INK = (22, 5, 9)

GOLD_FOIL = [(0.00, GOLD_DEEP), (0.16, (214, 176, 105)), (0.40, GOLD_LIGHT),
             (0.56, (226, 190, 116)), (0.78, (170, 124, 54)), (1.00, (232, 200, 130))]
IVORY_FOIL = [(0.00, (255, 251, 243)), (0.55, IVORY), (1.00, (219, 203, 172))]

ROZHA, CINZEL, CORM, JOST, MARCEL = ("RozhaOne-Regular.ttf", "Cinzel-var.ttf",
                                     "Cormorant-var.ttf", "Jost-var.ttf",
                                     "Marcellus-Regular.ttf")


# -------------------------------------------------------------------- fonts ---
def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(F, name), size)
    if weight is not None:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def tracked_mask(text, fnt, tracking=0.0):
    """Render letterspaced text into a tight L mask."""
    widths = [fnt.getlength(c) for c in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    asc, desc = fnt.getmetrics()
    pad = int(max(24, fnt.size * 0.6))
    img = Image.new("L", (int(total) + 2 * pad, asc + desc + 2 * pad), 0)
    d = ImageDraw.Draw(img)
    x = float(pad)
    for c, w in zip(text, widths):
        d.text((x, pad), c, font=fnt, fill=255)
        x += w + tracking
    bb = img.getbbox()
    return img.crop(bb) if bb else img


def fit_tracked(text, fname, target_w, tracking_em=0.0, start=420, weight=None,
                floor=16):
    """Largest font size whose letterspaced width still fits target_w."""
    size = start
    while size > floor:
        fnt = font(fname, size, weight)
        m = tracked_mask(text, fnt, tracking_em * size)
        if m.width <= target_w:
            return fnt, m
        size -= 2
    fnt = font(fname, floor, weight)
    return fnt, tracked_mask(text, fnt, tracking_em * floor)


def place(mask, xy, anchor="mt"):
    mw, mh = mask.size
    x, y = xy
    if anchor[0] == "m":
        x -= mw / 2
    elif anchor[0] == "r":
        x -= mw
    if anchor[1] == "m":
        y -= mh / 2
    elif anchor[1] == "b":
        y -= mh
    return int(x), int(y)


def stamp(base, mask, xy, fill, anchor="mt", opacity=255, shadow=None, glow=None):
    """Composite a mask with a solid colour or vertical gradient."""
    x, y = place(mask, xy, anchor)
    mw, mh = mask.size
    if glow:
        gcol, grad, gop = glow
        gm = mask.filter(ImageFilter.GaussianBlur(grad)).point(
            lambda v: int(v * gop / 255))
        base.paste(Image.new("RGB", (mw, mh), gcol), (x, y), gm)
    if shadow:
        scol, srad, (ox, oy), sop = shadow
        sm = mask.filter(ImageFilter.GaussianBlur(srad)).point(
            lambda v: int(v * sop / 255))
        base.paste(Image.new("RGB", (mw, mh), scol), (x + ox, y + oy), sm)
    paint = O.linear_gradient(mw, mh, fill) if isinstance(fill, list) \
        else Image.new("RGB", (mw, mh), fill)
    m = mask if opacity >= 255 else mask.point(lambda v: int(v * opacity / 255))
    base.paste(paint, (x, y), m)
    return (x, y, x + mw, y + mh)


def text_line(base, text, fname, y, *, size=None, target_w=None, tracking_em=0.0,
              weight=None, fill=IVORY, anchor="mt", cx=None, opacity=255,
              shadow=None, glow=None):
    if size:
        fnt = font(fname, size, weight)
        mask = tracked_mask(text, fnt, tracking_em * size)
    else:
        fnt, mask = fit_tracked(text, fname, target_w, tracking_em, weight=weight)
    return stamp(base, mask, (cx if cx is not None else W // 2, y), fill,
                 anchor=anchor, opacity=opacity, shadow=shadow, glow=glow)


# --------------------------------------------------------------- background ---
def build_background():
    bg = O.linear_gradient(W, H, [(0.00, MAROON_TOP), (0.30, (98, 17, 28)),
                                  (0.62, MAROON_MID), (1.00, MAROON_BOT)])

    # warm centre glow behind the hero arch
    glow = O.radial_gradient(W, H, inner=255, outer=0, power=1.25, cx=0.5, cy=0.55)
    bg.paste(Image.new("RGB", (W, H), (178, 84, 24)),
             (0, 0), glow.point(lambda v: int(v * 0.38)))

    # indigo weight in the lower corners, green in the upper corners: subtle
    # regional colour spectrum without breaking the maroon field
    for col, (cx, cy), op in (((20, 24, 74), (0.08, 0.94), 0.26),
                              ((20, 24, 74), (0.92, 0.94), 0.26),
                              (DEEP_GREEN, (0.05, 0.06), 0.22),
                              (DEEP_GREEN, (0.95, 0.06), 0.22)):
        g = O.radial_gradient(W, H, 255, 0, power=1.9, cx=cx, cy=cy)
        bg.paste(Image.new("RGB", (W, H), col), (0, 0),
                 g.point(lambda v: int(v * op)))

    # large mandala watermarks
    for size, (cx, cy), op in ((2300, (W // 2, 900), 38), (1500, (W // 2, 3060), 30)):
        m = O.mandala_mask(size)
        x, y = place(m, (cx, cy), "mm")
        bg.paste(Image.new("RGB", (size, size), GOLD), (x, y),
                 m.point(lambda v: int(v * op / 255)))

    # vignette + paper grain
    vig = O.radial_gradient(W, H, inner=0, outer=255, power=1.7, cx=0.5, cy=0.48)
    bg.paste(Image.new("RGB", (W, H), (16, 3, 7)), (0, 0),
             vig.point(lambda v: int(v * 0.38)))
    g = O.grain(W, H, amount=9)
    bg = Image.blend(bg, Image.composite(Image.new("RGB", (W, H), (255, 240, 220)),
                                         bg, g.point(lambda v: 255 if v > 132 else 0)),
                     0.045)
    return bg


# --------------------------------------------------------------------- frame ---
def draw_frame(bg):
    d = ImageDraw.Draw(bg, "RGBA")
    # double rule
    d.rectangle([58, 58, W - 59, H - 59], outline=GOLD + (235,), width=6)
    d.rectangle([84, 84, W - 85, H - 85], outline=GOLD + (120,), width=2)
    # corner quarter-mandalas
    cs = 330
    cm = O.corner_mask(cs)
    corners = [(cm, (96, 96)),
               (cm.transpose(Image.FLIP_LEFT_RIGHT), (W - 96 - cs, 96)),
               (cm.transpose(Image.FLIP_TOP_BOTTOM), (96, H - 96 - cs)),
               (cm.transpose(Image.ROTATE_180), (W - 96 - cs, H - 96 - cs))]
    for m, xy in corners:
        bg.paste(Image.new("RGB", (cs, cs), GOLD), xy,
                 m.point(lambda v: int(v * 205 / 255)))
    return bg


# ---------------------------------------------------------------- hero arch ---
def hero_arch(bg, hero_path, box):
    """Mask the hero artwork into a cusped arch with a gold frame."""
    bx, by, bw, bh = box
    mask = O.arch_mask(bw, bh, cusps=13, arch_frac=0.40)

    if hero_path and os.path.exists(hero_path):
        img = Image.open(hero_path).convert("RGB")
    else:  # placeholder so the layout can be checked without artwork
        img = O.linear_gradient(bw, bh, [(0, (120, 40, 40)), (1, (40, 60, 90))])
    # cover-fit
    s = max(bw / img.width, bh / img.height)
    img = img.resize((max(bw, int(img.width * s)), max(bh, int(img.height * s))),
                     Image.LANCZOS)
    img = img.crop(((img.width - bw) // 2, 0, (img.width - bw) // 2 + bw, bh))

    # gentle warm grade + a soft dark gradient at the very bottom edge
    img = Image.blend(img, Image.new("RGB", (bw, bh), (120, 40, 20)), 0.06)
    fade = O.linear_gradient(bw, bh, [(0.0, (255, 255, 255)), (0.88, (255, 255, 255)),
                                      (1.0, (120, 62, 50))])
    img = ImageChops_multiply(img, fade)

    # drop shadow
    sh = mask.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.55))
    bg.paste(Image.new("RGB", (bw, bh), INK), (bx, by + 16), sh)
    bg.paste(img, (bx, by), mask)

    # gold frame: outer band, then an inner hairline
    ring = O.outline_of(mask, thickness=5, outward=True)
    bg.paste(O.linear_gradient(bw, bh, GOLD_FOIL), (bx, by), ring)
    inner = O.outline_of(mask.filter(ImageFilter.MinFilter(3)), thickness=2,
                         outward=False)
    bg.paste(Image.new("RGB", (bw, bh), GOLD_LIGHT), (bx, by),
             inner.point(lambda v: int(v * 150 / 255)))

    # finial + lotus keystone at the apex
    fs = 132
    lot = O.lotus_mask(fs, petals=8)
    x, y = place(lot, (bx + bw // 2, by - 4), "mm")
    bg.paste(O.linear_gradient(fs, fs, GOLD_FOIL), (x, y), lot)
    d = ImageDraw.Draw(bg, "RGBA")
    d.line([bx + bw // 2, by - 78, bx + bw // 2, by - 40], fill=GOLD + (230,), width=5)
    d.ellipse([bx + bw // 2 - 13, by - 104, bx + bw // 2 + 13, by - 78],
              fill=GOLD_LIGHT + (240,))
    return bg


def ImageChops_multiply(a, b):
    from PIL import ImageChops
    return ImageChops.multiply(a, b)


# ----------------------------------------------------------------- elements ---
def gold_divider(bg, y, width=980, h=64, opacity=235):
    m = O.divider_mask(width, h)
    x, yy = place(m, (W // 2, y), "mm")
    bg.paste(O.linear_gradient(width, h, GOLD_FOIL), (x, yy),
             m.point(lambda v: int(v * opacity / 255)))


def chain(bg, y, width=900, h=26, opacity=210):
    m = O.diamond_chain_mask(width, h)
    x, yy = place(m, (W // 2, y), "mm")
    bg.paste(Image.new("RGB", (width, h), GOLD), (x, yy),
             m.point(lambda v: int(v * opacity / 255)))


def temple_band(bg, y, width, h=34, flip=False, opacity=150):
    m = O.temple_band_mask(width, h, flip=flip)
    x, yy = place(m, (W // 2, y), "mt")
    bg.paste(O.linear_gradient(width, h, GOLD_FOIL), (x, yy),
             m.point(lambda v: int(v * opacity / 255)))


def side_rules(bg, y, gap, length, thickness=4, opacity=225, diamond=True):
    d = ImageDraw.Draw(bg, "RGBA")
    for sign in (-1, 1):
        x0 = W // 2 + sign * gap
        x1 = x0 + sign * length
        d.line([x0, y, x1, y], fill=GOLD + (opacity,), width=thickness)
        if diamond:
            r = 13
            d.polygon([(x1 + sign * r, y), (x1, y - r), (x1 - sign * r, y),
                       (x1, y + r)], fill=GOLD_LIGHT + (opacity,))


def paisley_pair(bg, y, gap, w=76, h=108, opacity=200):
    for sign in (-1, 1):
        p = O.paisley_mask(w, h, line=2.6)
        if sign > 0:
            p = p.transpose(Image.FLIP_LEFT_RIGHT)
        x, yy = place(p, (W // 2 + sign * gap, y), "mm")
        bg.paste(Image.new("RGB", (w, h), GOLD), (x, yy),
                 p.point(lambda v: int(v * opacity / 255)))


# --------------------------------------------------------------------- build ---
def build(hero_path=None, out="poster.png"):
    bg = build_background()
    bg = draw_frame(bg)

    # ---- masthead
    text_line(bg, "GRAPHIC ERA", CINZEL, 214, target_w=1180, tracking_em=0.13,
              weight=600, fill=IVORY_FOIL,
              shadow=(INK, 10, (0, 7), 150))
    text_line(bg, "(DEEMED TO BE UNIVERSITY), DEHRADUN", JOST, 356,
              target_w=1080, tracking_em=0.11, weight=450, fill=GOLD)
    chain(bg, 452, width=760, h=24)

    # ---- theme eyebrow
    text_line(bg, "INDIA'S CULTURAL MOSAIC", JOST, 520, target_w=820,
              tracking_em=0.30, weight=500, fill=GOLD_LIGHT, opacity=245)
    paisley_pair(bg, 546, gap=572, w=94, h=132, opacity=225)

    # ---- headline
    text_line(bg, "FRESHERS", ROZHA, 610, target_w=1830, tracking_em=0.015,
              fill=IVORY_FOIL, shadow=(INK, 22, (0, 16), 165),
              glow=((120, 40, 10), 60, 90))
    y2026 = 982
    text_line(bg, "2026", CINZEL, y2026, target_w=560, tracking_em=0.16,
              weight=700, fill=GOLD_FOIL, shadow=(INK, 14, (0, 9), 150))
    side_rules(bg, y2026 + 92, gap=350, length=430)

    # ---- batch + theme line
    text_line(bg, "MBA BATCH 2026\u201328", JOST, 1235, target_w=1000,
              tracking_em=0.22, weight=500, fill=IVORY)
    text_line(bg, "One India \u2022 Many Cultures \u2022 One Celebration", CORM,
              1322, target_w=1540, tracking_em=0.03, weight=600, fill=GOLD_LIGHT)

    # ---- hero arch
    bw, bh = 1900, 1280
    hero_arch(bg, hero_path, (W // 2 - bw // 2, 1520, bw, bh))

    # ---- event information
    gold_divider(bg, 2870, width=1020, h=62)

    text_line(bg, "DATE", JOST, 2944, size=46, tracking_em=0.42, weight=500,
              fill=GOLD)
    text_line(bg, "20 SEPTEMBER 2026", CINZEL, 3010, target_w=1420,
              tracking_em=0.06, weight=700, fill=IVORY_FOIL,
              shadow=(INK, 12, (0, 8), 140))

    side_rules(bg, 3180, gap=60, length=560, thickness=3, opacity=170,
               diamond=False)
    d = ImageDraw.Draw(bg, "RGBA")
    d.polygon([(W // 2 - 16, 3180), (W // 2, 3165), (W // 2 + 16, 3180),
               (W // 2, 3195)], fill=GOLD_LIGHT + (220,))

    pairs = ((W // 2 - 520, "TIME", "4:00 PM ONWARDS"),
             (W // 2 + 520, "VENUE", "CS/IT OPEN AUDITORIUM"))
    vsize = min(fit_tracked(v, JOST, 880, 0.05, weight=600)[0].size
                for _, _, v in pairs)
    for cx, label, value in pairs:
        text_line(bg, label, JOST, 3232, size=40, tracking_em=0.40, weight=500,
                  fill=GOLD, cx=cx)
        text_line(bg, value, JOST, 3290, size=vsize, tracking_em=0.05,
                  weight=600, fill=IVORY, cx=cx)

    temple_band(bg, 3384, width=W - 260, h=24, flip=True, opacity=125)

    bg = bg.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=3))
    path = os.path.join(HERE, out)
    bg.save(path, "PNG", dpi=(300, 300))
    bg.convert("RGB").save(path.replace(".png", ".jpg"), "JPEG", quality=94,
                           dpi=(300, 300), subsampling=1)
    print("saved", path, bg.size)
    return bg


if __name__ == "__main__":
    hero = sys.argv[1] if len(sys.argv) > 1 else None
    out = sys.argv[2] if len(sys.argv) > 2 else "poster.png"
    build(hero, out)
