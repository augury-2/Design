"""FRESHERS 2026 - MBA Batch 2026-28 - Graphic Era (Deemed to be University), Dehradun
Theme: India's Cultural Mosaic - One India, Many Cultures, One Celebration.

Builds a 2480 x 3508 px (A4 @ 300 DPI) vertical poster in a bright Indian
festival palette: white/ivory base, flowing colour bands, procedural folk-art
motifs, a hero panel of students in regional attire, and event details on
vivid rounded cards.

    python3 poster.py [hero_image] [out.png]
"""
import math
import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

import motifs as M
import ornament as O

HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "fonts")

W, H = 2480, 3508
MARGIN = 150

# ------------------------------------------------------------------ palette ---
# Bright Indian festival colours only - no black, navy, maroon or antique gold.
SAFFRON = (255, 141, 26)
ORANGE = (255, 106, 0)
MARIGOLD = (255, 178, 26)
YELLOW = (255, 203, 20)
CORAL = (255, 94, 87)
PINK = (255, 61, 133)
MAGENTA = (226, 27, 142)
ORCHID = (168, 46, 190)
PURPLE = (129, 47, 200)
ROYAL = (58, 82, 220)
BLUE = (0, 129, 232)
CYAN = (0, 183, 226)
TURQ = (0, 197, 186)
GREEN = (54, 187, 92)
LIME = (146, 205, 44)

INK = (74, 33, 130)          # deep violet, the darkest tone in the poster
INK_SOFT = (108, 62, 158)
WHITE = (255, 255, 255)
IVORY = (255, 252, 246)
BLUSH = (255, 243, 236)

FESTIVAL = [SAFFRON, PINK, TURQ, PURPLE, GREEN, YELLOW, ROYAL, MAGENTA, CORAL, CYAN]
CORNER_PAL = [SAFFRON, MAGENTA, TURQ, PURPLE, GREEN, YELLOW]

HOLI_GRAD = [(0.00, SAFFRON), (0.18, ORANGE), (0.34, CORAL), (0.50, PINK),
             (0.64, MAGENTA), (0.78, PURPLE), (0.90, ROYAL), (1.00, CYAN)]
SUNRISE_GRAD = [(0.0, YELLOW), (0.35, SAFFRON), (0.72, CORAL), (1.0, PINK)]
LAGOON_GRAD = [(0.0, TURQ), (0.45, CYAN), (1.0, ROYAL)]
ORCHID_GRAD = [(0.0, PINK), (0.45, MAGENTA), (1.0, PURPLE)]
LEAF_GRAD = [(0.0, LIME), (0.5, GREEN), (1.0, TURQ)]

ROZHA, JOST, MONT = "RozhaOne-Regular.ttf", "Jost-var.ttf", "Montserrat-var.ttf"
YATRA, CORM = "YatraOne-Regular.ttf", "Cormorant-var.ttf"

# the regional craft traditions stitched into the mosaic ribbon, left to right:
# Warli (Maharashtra), phulkari (Punjab), aipan (Uttarakhand), Madhubani
# (Mithila), Assamese weave, Pattachitra (Odisha), lehariya (Rajasthan) and an
# Indian floral vine.
FOLK_PATCHES = [
    lambda w, h: M.warli_band(w, h, count=3),
    lambda w, h: M.phulkari_band(w, h),
    lambda w, h: M.aipan_band(w, h),
    lambda w, h: M.assamese_band(w, h),
    lambda w, h: M.lehariya_band(w, h, waves=2, amp=h * 0.24),
    lambda w, h: M.floral_vine(w, h, flowers=3),
]


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


def fit_tracked(text, fname, target_w, tracking_em=0.0, start=460, weight=None,
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


def paint(size, fill):
    """Solid colour, vertical gradient (list of stops) or ('h', stops)."""
    w, h = size
    if isinstance(fill, tuple) and len(fill) == 2 and fill[0] == "h":
        return O.linear_gradient(w, h, fill[1], horizontal=True)
    if isinstance(fill, list):
        return O.linear_gradient(w, h, fill)
    return Image.new("RGB", (w, h), fill)


def stamp(base, mask, xy, fill, anchor="mt", opacity=255, shadow=None,
          outline=None):
    """Composite a mask with a solid colour or a gradient.

    outline: (colour, thickness) halo drawn behind the glyphs, which keeps big
    type crisp where it crosses colour bands.
    """
    x, y = place(mask, xy, anchor)
    mw, mh = mask.size
    if outline:
        ocol, oth = outline
        grown = mask.filter(ImageFilter.MaxFilter(oth * 2 + 1))
        base.paste(Image.new("RGB", (mw, mh), ocol), (x, y), grown)
    if shadow:
        scol, srad, (ox, oy), sop = shadow
        sm = mask.filter(ImageFilter.GaussianBlur(srad)).point(
            lambda v: int(v * sop / 255))
        base.paste(Image.new("RGB", (mw, mh), scol), (x + ox, y + oy), sm)
    m = mask if opacity >= 255 else mask.point(lambda v: int(v * opacity / 255))
    base.paste(paint((mw, mh), fill), (x, y), m)
    return (x, y, x + mw, y + mh)


def text_line(base, text, fname, y, *, size=None, target_w=None, tracking_em=0.0,
              weight=None, fill=INK, anchor="mt", cx=None, opacity=255,
              shadow=None, outline=None):
    if size:
        fnt = font(fname, size, weight)
        mask = tracked_mask(text, fnt, tracking_em * size)
    else:
        fnt, mask = fit_tracked(text, fname, target_w, tracking_em, weight=weight)
    return stamp(base, mask, (cx if cx is not None else W // 2, y), fill,
                 anchor=anchor, opacity=opacity, shadow=shadow, outline=outline)


# --------------------------------------------------------------- background ---
def flow_band(w, h, y0, amp, thick, phase=0.0, waves=1.4):
    """Mask of a flowing horizontal ribbon - the textile colour bands."""
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    steps = 260
    top, bot = [], []
    for i in range(steps + 1):
        t = i / steps
        x = t * w
        y = y0 + amp * math.sin(2 * math.pi * (t * waves + phase))
        th = thick * (0.72 + 0.42 * math.sin(math.pi * t))
        top.append((x, y - th / 2))
        bot.append((x, y + th / 2))
    d.polygon(top + list(reversed(bot)), fill=255)
    return m.filter(ImageFilter.GaussianBlur(2))


def tint(col, amount):
    """Pastel version of a colour, mixed towards white."""
    return tuple(int(c + (255 - c) * (1 - amount)) for c in col)


def bloom_mask(cx, cy, radius, power=1.7, scale=8):
    """Local radial bloom: 255 at the centre, 0 at radius (fraction of H)."""
    w, h = W // scale, H // scale
    m = Image.new("L", (w, h), 0)
    px = m.load()
    ccx, ccy = cx * w, cy * h
    r = radius * h
    for y in range(h):
        for x in range(w):
            t = math.hypot(x - ccx, y - ccy) / r
            px[x, y] = 0 if t >= 1 else int(255 * (1 - t) ** power)
    return m.resize((W, H), Image.BICUBIC)


def build_background():
    bg = O.linear_gradient(W, H, [(0.00, WHITE), (0.38, IVORY), (0.74, BLUSH),
                                  (1.00, (255, 248, 242))])

    # local corner blooms in pastel tints: colour at the edges, white at the core
    blooms = [(SAFFRON, (0.00, 0.00), 0.40, 0.62), (YELLOW, (0.22, 0.00), 0.24, 0.42),
              (PINK, (1.00, 0.02), 0.38, 0.58), (MAGENTA, (0.86, 0.20), 0.20, 0.34),
              (TURQ, (-0.02, 0.42), 0.26, 0.44), (PURPLE, (1.02, 0.60), 0.26, 0.40),
              (GREEN, (0.02, 1.00), 0.34, 0.46), (CYAN, (0.98, 1.00), 0.34, 0.48),
              (SAFFRON, (0.50, 1.02), 0.22, 0.34)]
    for col, (cx, cy), rad, op in blooms:
        g = bloom_mask(cx, cy, rad)
        bg.paste(Image.new("RGB", (W, H), tint(col, 0.42)), (0, 0),
                 g.point(lambda v: int(v * op)))

    # flowing textile colour bands, top and bottom only: movement without noise
    bands = [(360, 150, 175, SAFFRON, 0.00, 0.48),
             (505, 120, 120, PINK, 0.35, 0.44),
             (250, 100, 95, TURQ, 0.62, 0.38),
             (2050, 210, 260, TURQ, 0.15, 0.30),
             (2450, 190, 230, PINK, 0.48, 0.26),
             (2760, 170, 200, YELLOW, 0.72, 0.26),
             (3110, 160, 200, PURPLE, 0.20, 0.38),
             (3270, 130, 150, TURQ, 0.55, 0.40),
             (3390, 110, 130, MAGENTA, 0.80, 0.36)]
    for y0, amp, thick, col, phase, op in bands:
        m = flow_band(W, H, y0, amp, thick, phase)
        bg.paste(Image.new("RGB", (W, H), tint(col, 0.34)), (0, 0),
                 m.point(lambda v: int(v * op)))

    # large mandala watermarks behind the headline and the event block
    for size, (cx, cy), col, op in ((2300, (W // 2, 960), MAGENTA, 0.09),
                                    (1400, (W // 2, 3180), TURQ, 0.08)):
        m = O.mandala_mask(size)
        x, y = place(m, (cx, cy), "mm")
        bg.paste(Image.new("RGB", (size, size), col), (x, y),
                 m.point(lambda v: int(v * op)))

    # festive confetti of petals, diamonds and dots
    for box, count, sizes, op in (((0, 150, W, 1560), 120, (12, 32), 0.50),
                                  ((0, 2880, W, H - 60), 80, (12, 30), 0.45)):
        x0, y0, x1, y1 = box
        c = M.confetti(x1 - x0, y1 - y0, FESTIVAL, count=count, sizes=sizes,
                       seed=int(y0))
        a = c.getchannel("A").point(lambda v: int(v * op))
        c.putalpha(a)
        bg.paste(c, (x0, y0), c)

    return bg


# --------------------------------------------------------------------- frame ---
def draw_frame(bg):
    # rainbow keyline, rounded, drawn as a ring so the colours run continuously
    inset, th, rad = 54, 13, 92
    ring = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(ring)
    d.rounded_rectangle([inset, inset, W - inset - 1, H - inset - 1], radius=rad,
                        outline=255, width=th)
    grad = O.linear_gradient(W, H, [(0.00, YELLOW), (0.10, SAFFRON),
                                    (0.22, CORAL), (0.34, PINK), (0.46, MAGENTA),
                                    (0.58, PURPLE), (0.70, ROYAL), (0.82, CYAN),
                                    (0.92, TURQ), (1.00, GREEN)])
    bg.paste(grad, (0, 0), ring)

    # inner hairline
    d2 = ImageDraw.Draw(bg, "RGBA")
    d2.rounded_rectangle([inset + 26, inset + 26, W - inset - 27, H - inset - 27],
                         radius=rad - 18, outline=ORCHID + (70,), width=3)

    # quarter rangoli in the corners: larger at the top, smaller at the foot so
    # they never crowd the event cards
    for cs, op, spots in ((360, 0.90, ("tl", "tr")), (250, 0.75, ("bl", "br"))):
        q = M.quarter_rangoli(cs, CORNER_PAL)
        a = q.getchannel("A").point(lambda v: int(v * op))
        q.putalpha(a)
        off = inset + 30
        for spot in spots:
            if spot == "tl":
                layer, xy = q, (off, off)
            elif spot == "tr":
                layer, xy = q.transpose(Image.FLIP_LEFT_RIGHT), (W - off - cs, off)
            elif spot == "bl":
                layer, xy = q.transpose(Image.FLIP_TOP_BOTTOM), (off, H - off - cs)
            else:
                layer, xy = q.transpose(Image.ROTATE_180), (W - off - cs,
                                                            H - off - cs)
            bg.paste(layer, xy, layer)
    return bg


# ---------------------------------------------------------------- components ---
def rounded_card(bg, box, fill, radius=None, shadow_col=None, border=None,
                 shadow_op=0.30):
    """Bright rounded card with a soft coloured shadow."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    radius = radius if radius is not None else h // 2
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=radius,
                                        fill=255)
    if shadow_col:
        pad = 60
        sm = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
        sm.paste(m, (pad, pad))
        sm = sm.filter(ImageFilter.GaussianBlur(26)).point(
            lambda v: int(v * shadow_op))
        bg.paste(Image.new("RGB", sm.size, shadow_col), (x0 - pad, y0 - pad + 14),
                 sm)
    bg.paste(paint((w, h), fill), (x0, y0), m)
    if border:
        bcol, bth = border
        ring = O.outline_of(m, thickness=bth, outward=False)
        bg.paste(Image.new("RGB", (w, h), bcol), (x0, y0), ring)
    return m


def pill_text(bg, text, cy, *, fname=JOST, weight=600, tracking_em=0.18,
              text_w=900, pad_x=90, pad_y=42, fill=ORCHID_GRAD, ink=WHITE,
              shadow_col=None, cx=None, radius=None, border=None):
    """A line of type inside a bright rounded pill."""
    fnt, mask = fit_tracked(text, fname, text_w, tracking_em, weight=weight)
    cx = cx if cx is not None else W // 2
    w = mask.width + 2 * pad_x
    h = mask.height + 2 * pad_y
    box = (int(cx - w / 2), int(cy - h / 2), int(cx + w / 2), int(cy + h / 2))
    rounded_card(bg, box, fill, radius=radius, shadow_col=shadow_col,
                 border=border)
    stamp(bg, mask, (cx, cy), ink, anchor="mm")
    return box


def motif_strip(bg, y, width, height, fn, palette=None, opacity=255, cx=None,
                segments=None):
    """Paste a folk-art band, cut into rotating colour segments."""
    palette = palette or FESTIVAL
    layer = M.colour_band(width, height, fn, palette, segments=segments)
    if opacity < 255:
        a = layer.getchannel("A").point(lambda v: int(v * opacity / 255))
        layer.putalpha(a)
    x = int((cx if cx is not None else W // 2) - width / 2)
    bg.paste(layer, (x, y), layer)


def rainbow_rule(bg, y, width, height=14, palette=None, cx=None):
    palette = palette or [SAFFRON, PINK, MAGENTA, PURPLE, ROYAL, TURQ, GREEN,
                          YELLOW]
    bar = M.rainbow_rule(width, height, palette)
    x = int((cx if cx is not None else W // 2) - width / 2)
    bg.paste(bar, (x, y), bar)


def bullet_line(bg, parts, y, *, target_w, fname=MONT, weight=600,
                tracking_em=0.06, ink=INK, dot_cols=None):
    """A line such as ONE INDIA - MANY CULTURES - ONE CELEBRATION with
    coloured lozenge separators between the phrases."""
    dot_cols = dot_cols or [SAFFRON, TURQ, MAGENTA, GREEN]
    gap = 0.0
    # size the whole line, separators included, then draw the pieces
    joined = "   ".join(parts)
    fnt, _ = fit_tracked(joined, fname, target_w, tracking_em, weight=weight)
    masks = [tracked_mask(p, fnt, tracking_em * fnt.size) for p in parts]
    sep = int(fnt.size * 1.5)
    total = sum(m.width for m in masks) + sep * (len(masks) - 1)
    x = W // 2 - total / 2
    top = y
    for i, m in enumerate(masks):
        stamp(bg, m, (x + m.width / 2, top + max(mm.height for mm in masks) / 2),
              ink, anchor="mm")
        x += m.width
        if i < len(masks) - 1:
            cy = top + max(mm.height for mm in masks) / 2
            r = fnt.size * 0.22
            d = ImageDraw.Draw(bg, "RGBA")
            col = dot_cols[i % len(dot_cols)]
            d.polygon([(x + sep / 2, cy - r), (x + sep / 2 + r * 0.72, cy),
                       (x + sep / 2, cy + r), (x + sep / 2 - r * 0.72, cy)],
                      fill=col + (255,))
            x += sep
    return top, top + max(m.height for m in masks)


# ---------------------------------------------------------------- hero panel ---
def hero_panel(bg, hero_path, box):
    """Cusped arch panel holding the student artwork, framed in rainbow."""
    bx, by, bw, bh = box
    # the arch sits inset inside the panel box so the outward rainbow ring has
    # room to wrap the sides and the foot of the panel as well as the crown
    pad = 22
    iw, ih = bw - 2 * pad, bh - 2 * pad
    inner = O.arch_mask(iw, ih, cusps=13, arch_frac=0.34)
    mask = Image.new("L", (bw, bh), 0)
    mask.paste(inner, (pad, pad))

    if hero_path and os.path.exists(hero_path):
        img = Image.open(hero_path).convert("RGB")
    else:
        img = Image.open(os.path.join(HERE, "centrepiece.png")).convert("RGB") \
            if os.path.exists(os.path.join(HERE, "centrepiece.png")) \
            else O.linear_gradient(bw, bh, SUNRISE_GRAD)
    # cover-fit with a small zoom so the group fills the arch rather than
    # floating inside it
    s = max(bw / img.width, bh / img.height) * 1.10
    img = img.resize((max(bw, int(img.width * s)), max(bh, int(img.height * s))),
                     Image.LANCZOS)
    # bias the crop towards the top so faces are never trimmed
    oy = int((img.height - bh) * 0.30)
    ox = (img.width - bw) // 2
    img = img.crop((ox, oy, ox + bw, oy + bh))

    # keep the hero bright and punchy
    from PIL import ImageEnhance
    img = ImageEnhance.Color(img).enhance(1.12)
    img = ImageEnhance.Brightness(img).enhance(1.03)

    # soft magenta shadow instead of a black one, so nothing goes dark
    spad = 70
    sm = Image.new("L", (bw + 2 * spad, bh + 2 * spad), 0)
    sm.paste(mask, (spad, spad))
    sm = sm.filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * 0.30))
    bg.paste(Image.new("RGB", sm.size, MAGENTA), (bx - spad, by - spad + 22), sm)

    bg.paste(img, (bx, by), mask)

    # rainbow band frame + white inner hairline
    ring = O.outline_of(mask, thickness=17, outward=True)
    band = O.linear_gradient(bw, bh, [(0.0, YELLOW), (0.13, SAFFRON),
                                      (0.27, CORAL), (0.40, PINK),
                                      (0.54, MAGENTA), (0.68, PURPLE),
                                      (0.82, ROYAL), (0.93, CYAN), (1.0, TURQ)])
    bg.paste(band, (bx, by), ring)
    hair = O.outline_of(mask.filter(ImageFilter.MinFilter(3)), thickness=5,
                        outward=False)
    bg.paste(Image.new("RGB", (bw, bh), WHITE), (bx, by),
             hair.point(lambda v: int(v * 0.80)))

    # marigold rosette keystone at the apex
    fs = 190
    rose = M.petal_burst(fs, [SAFFRON, YELLOW, MARIGOLD, ORANGE], petals=14)
    x, y = place(rose, (bx + bw // 2, by + pad + 2), "mm")
    bg.paste(rose, (x, y), rose)
    return bg


# --------------------------------------------------------------------- build ---
def build(hero_path=None, out="poster.png"):
    bg = build_background()
    bg = draw_frame(bg)

    # ---- masthead
    text_line(bg, "GRAPHIC ERA", MONT, 196, target_w=1230, tracking_em=0.10,
              weight=800, fill=[(0.0, INK), (1.0, (96, 40, 165))])
    text_line(bg, "(DEEMED TO BE UNIVERSITY), DEHRADUN", JOST, 348,
              target_w=1120, tracking_em=0.13, weight=500, fill=MAGENTA)
    rainbow_rule(bg, 424, width=620, height=15)

    # ---- theme eyebrow
    pill_text(bg, "INDIA'S CULTURAL MOSAIC", 540, fname=JOST, weight=600,
              tracking_em=0.26, text_w=880, pad_x=86, pad_y=40,
              fill=("h", [(0.0, TURQ), (0.5, ROYAL), (1.0, PURPLE)]),
              shadow_col=ROYAL)

    # small paisley pair flanking the eyebrow
    for sign in (-1, 1):
        pw, ph = 104, 146
        p = O.paisley_mask(pw, ph, line=3.4)
        if sign > 0:
            p = p.transpose(Image.FLIP_LEFT_RIGHT)
        x, y = place(p, (W // 2 + sign * 700, 540), "mm")
        bg.paste(Image.new("RGB", (pw, ph), MAGENTA), (x, y),
                 p.point(lambda v: int(v * 0.85)))

    # ---- headline
    text_line(bg, "FRESHERS", ROZHA, 640, target_w=1960, tracking_em=0.012,
              fill=("h", HOLI_GRAD), outline=(WHITE, 10),
              shadow=(ORCHID, 22, (0, 16), 62))

    y2026 = 1035
    text_line(bg, "2026", MONT, y2026, target_w=690, tracking_em=0.05,
              weight=800, fill=("h", [(0.0, TURQ), (0.5, ROYAL), (1.0, PURPLE)]),
              outline=(WHITE, 8), shadow=(ROYAL, 20, (0, 14), 80))
    for sign in (-1, 1):
        rainbow_rule(bg, y2026 + 108, width=470, height=14,
                     palette=[SAFFRON, PINK, MAGENTA, PURPLE] if sign < 0
                     else [PURPLE, ROYAL, TURQ, GREEN],
                     cx=W // 2 + sign * 640)

    # ---- batch + theme line
    pill_text(bg, "MBA BATCH 2026\u201328", 1330, fname=JOST, weight=600,
              tracking_em=0.20, text_w=1010, pad_x=96, pad_y=46,
              fill=("h", [(0.0, SAFFRON), (0.5, PINK), (1.0, MAGENTA)]),
              shadow_col=PINK)

    bullet_line(bg, ["ONE INDIA", "MANY CULTURES", "ONE CELEBRATION"], 1452,
                target_w=1560, weight=700, tracking_em=0.05, ink=INK,
                dot_cols=[SAFFRON, TURQ])

    # ---- marigold garland above the hero
    motif_strip(bg, 1536, 1900, 118, lambda w, h: M.garland_band(w, h, count=13),
                palette=FESTIVAL, opacity=245, segments=13)

    # ---- hero panel
    bw, bh = 1980, 1160
    hero_panel(bg, hero_path, (W // 2 - bw // 2, 1690, bw, bh))

    # ---- cultural mosaic ribbon: eight regional folk traditions, patch by patch
    ribbon = M.mosaic_ribbon(1980, 136, FOLK_PATCHES,
                             [SAFFRON, MAGENTA, TURQ, PURPLE, GREEN, ROYAL],
                             radius=30)
    bg.paste(ribbon, (W // 2 - 990, 2882), ribbon)

    # ---- event details
    rounded_card(bg, (MARGIN + 110, 3054, W - MARGIN - 110, 3240),
                 ("h", [(0.0, SAFFRON), (0.42, ORANGE), (0.72, CORAL),
                        (1.0, PINK)]), radius=93, shadow_col=CORAL,
                 shadow_op=0.34)
    text_line(bg, "20 SEPTEMBER 2026", MONT, 3147, target_w=1420,
              tracking_em=0.05, weight=800, fill=WHITE, anchor="mm")

    cw, gap = 1010, 60
    left = (W - (cw * 2 + gap)) // 2
    cards = [(left, "4:00 PM ONWARDS", ("h", [(0.0, TURQ), (1.0, ROYAL)]), CYAN),
             (left + cw + gap, "CS/IT OPEN AUDITORIUM",
              ("h", [(0.0, ORCHID), (1.0, PURPLE)]), ORCHID)]
    vsize = min(fit_tracked(t, JOST, cw - 150, 0.05, weight=600)[0].size
                for _, t, _, _ in cards)
    for x0, label, fill, sh in cards:
        rounded_card(bg, (x0, 3276, x0 + cw, 3394), fill, radius=59,
                     shadow_col=sh, shadow_op=0.30)
        text_line(bg, label, JOST, 3335, size=vsize, tracking_em=0.05,
                  weight=600, fill=WHITE, cx=x0 + cw // 2, anchor="mm")

    bg = bg.filter(ImageFilter.UnsharpMask(radius=2, percent=52, threshold=3))
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
