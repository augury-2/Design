"""Export the master poster to print and social delivery sizes.

The master is 1:1.414 (A4). Targets with a different ratio are letterboxed onto a
matching maroon field with a fine gold keyline, so nothing is ever cropped away.
"""
import os
import sys
from PIL import Image, ImageDraw, ImageFilter

import ornament as O

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD = (201, 162, 77)

TARGETS = [
    ("instagram-post-4x5", 1080, 1350),
    ("instagram-story-9x16", 1080, 1920),
    ("whatsapp-square-1x1", 1080, 1080),
    ("digital-display-2x3", 1600, 2400),
    ("web-preview", 1240, 1754),
]


def field(w, h):
    bg = O.linear_gradient(w, h, [(0.0, (78, 14, 24)), (0.55, (58, 11, 20)),
                                  (1.0, (40, 9, 16))])
    g = O.radial_gradient(w, h, 255, 0, power=1.5, cx=0.5, cy=0.45)
    bg.paste(Image.new("RGB", (w, h), (150, 66, 20)), (0, 0),
             g.point(lambda v: int(v * 0.22)))
    grain = O.grain(w, h, amount=8)
    bg = Image.blend(bg, Image.composite(Image.new("RGB", (w, h), (255, 240, 220)),
                                         bg, grain.point(lambda v: 255 if v > 133 else 0)),
                     0.04)
    return bg


def export(master_path, outdir):
    os.makedirs(outdir, exist_ok=True)
    master = Image.open(master_path).convert("RGB")
    made = []
    for name, tw, th in TARGETS:
        s = min(tw / master.width, th / master.height)
        pw, ph = int(master.width * s), int(master.height * s)
        canvas = field(tw, th)
        art = master.resize((pw, ph), Image.LANCZOS)
        ox, oy = (tw - pw) // 2, (th - ph) // 2
        if (pw, ph) != (tw, th):
            sh = Image.new("L", (tw, th), 0)
            ImageDraw.Draw(sh).rectangle([ox, oy, ox + pw, oy + ph], fill=255)
            sh = sh.filter(ImageFilter.GaussianBlur(14))
            canvas.paste(Image.new("RGB", (tw, th), (18, 4, 8)), (0, 0),
                         sh.point(lambda v: int(v * 0.5)))
        canvas.paste(art, (ox, oy))
        if (pw, ph) != (tw, th):
            ImageDraw.Draw(canvas, "RGBA").rectangle(
                [ox, oy, ox + pw - 1, oy + ph - 1], outline=GOLD + (150,), width=2)
        p = os.path.join(outdir, f"freshers-2026-{name}.jpg")
        canvas.save(p, "JPEG", quality=93, subsampling=1, optimize=True)
        made.append((name, tw, th, os.path.getsize(p)))
        print(f"{name:24s} {tw}x{th}  {os.path.getsize(p)//1024} KB")
    return made


if __name__ == "__main__":
    export(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "social")
