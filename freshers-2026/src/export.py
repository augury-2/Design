"""Export the master poster to print and social delivery sizes.

The master is 1:1.414 (A4). Targets with a different ratio are letterboxed onto
a bright festival field - white with pastel colour blooms and confetti - and the
artwork carries a fine rainbow keyline, so nothing is ever cropped away.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageChops

import motifs as M
import ornament as O
import poster as P

HERE = os.path.dirname(os.path.abspath(__file__))

TARGETS = [
    ("instagram-post-4x5", 1080, 1350),
    ("instagram-story-9x16", 1080, 1920),
    ("whatsapp-square-1x1", 1080, 1080),
    ("digital-display-2x3", 1600, 2400),
    ("web-preview", 1240, 1754),
]


def field(w, h):
    """Bright pastel field for letterboxed formats."""
    bg = O.linear_gradient(w, h, [(0.0, (255, 253, 248)), (0.5, P.IVORY),
                                  (1.0, (255, 244, 236))])
    # warm hues only: mixing cool tints over white turns the field grey
    blooms = [(P.SAFFRON, (0.00, 0.00), 0.46), (P.PINK, (1.00, 0.04), 0.42),
              (P.YELLOW, (0.10, 0.98), 0.34), (P.CORAL, (0.94, 1.00), 0.36)]
    for col, (cx, cy), op in blooms:
        g = O.radial_gradient(w, h, 255, 0, power=2.6, cx=cx, cy=cy)
        bg.paste(Image.new("RGB", (w, h), P.tint(col, 0.26)), (0, 0),
                 g.point(lambda v: int(v * op)))
    c = M.confetti(w, h, P.FESTIVAL, count=int(w * h / 9000),
                   sizes=(int(w * 0.008), int(w * 0.022)), seed=6)
    a = c.getchannel("A").point(lambda v: int(v * 0.45))
    c.putalpha(a)
    bg.paste(c, (0, 0), c)
    return bg


def keyline(canvas, box, thickness=None):
    """Rainbow keyline around the placed artwork."""
    x0, y0, x1, y1 = box
    th = thickness or max(3, (x1 - x0) // 300)
    ring = Image.new("L", canvas.size, 0)
    ImageDraw.Draw(ring).rectangle([x0 - th, y0 - th, x1 + th - 1, y1 + th - 1],
                                  outline=255, width=th)
    grad = O.linear_gradient(canvas.width, canvas.height,
                             [(0.0, P.YELLOW), (0.14, P.SAFFRON), (0.30, P.CORAL),
                              (0.44, P.PINK), (0.58, P.MAGENTA), (0.72, P.PURPLE),
                              (0.86, P.ROYAL), (1.0, P.TURQ)])
    canvas.paste(grad, (0, 0), ring)


def export(master_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    master = Image.open(master_path).convert("RGB")
    made = []
    for name, tw, th in TARGETS:
        s = min(tw / master.width, th / master.height)
        pw, ph = int(master.width * s), int(master.height * s)
        art = master.resize((pw, ph), Image.LANCZOS)
        ox, oy = (tw - pw) // 2, (th - ph) // 2
        if (pw, ph) == (tw, th):
            canvas = art
        else:
            canvas = field(tw, th)
            # soft coloured lift under the artwork instead of a dark shadow
            sh = Image.new("L", (tw, th), 0)
            ImageDraw.Draw(sh).rectangle([ox, oy, ox + pw, oy + ph], fill=255)
            sh = sh.filter(ImageFilter.GaussianBlur(18))
            canvas.paste(Image.new("RGB", (tw, th), P.ORCHID), (0, 0),
                         sh.point(lambda v: int(v * 0.22)))
            canvas.paste(art, (ox, oy))
            keyline(canvas, (ox, oy, ox + pw, oy + ph))
        p = os.path.join(outdir, f"freshers-2026-{name}.jpg")
        canvas.save(p, "JPEG", quality=93, subsampling=1, optimize=True)
        made.append((name, tw, th, os.path.getsize(p)))
        print(f"{name:24s} {tw}x{th}  {os.path.getsize(p)//1024} KB")
    return made


if __name__ == "__main__":
    export(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "social")
