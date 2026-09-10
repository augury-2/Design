# Freshers 2026 — MBA Batch 2026–28

Event poster for **Graphic Era (Deemed to be University), Dehradun**.
Theme: **India's Cultural Mosaic** — *One India • Many Cultures • One Celebration*.

Bright, vibrant, festival-coloured artwork aimed at a young MBA audience. No
dark, antique or luxury-event treatment anywhere in the set.

## Event details as set in the artwork

| Field | Value |
|---|---|
| Date | 20 SEPTEMBER 2026 |
| Time | 4:00 PM ONWARDS |
| Venue | CS/IT OPEN AUDITORIUM |

## Deliverables

| File | Size | Use |
|---|---|---|
| `print/Freshers-2026-MBA-GraphicEra.png` | 2480 × 3508 px, 300 DPI | A4 print master, lossless |
| `print/Freshers-2026-MBA-GraphicEra.jpg` | 2480 × 3508 px, 300 DPI | print/press hand-off |
| `social/freshers-2026-instagram-post-4x5.jpg` | 1080 × 1350 | Instagram feed |
| `social/freshers-2026-instagram-story-9x16.jpg` | 1080 × 1920 | Stories, Reels, WhatsApp status |
| `social/freshers-2026-whatsapp-square-1x1.jpg` | 1080 × 1080 | WhatsApp broadcast |
| `social/freshers-2026-digital-display-2x3.jpg` | 1600 × 2400 | campus screens |
| `social/freshers-2026-web-preview.jpg` | 1240 × 1754 | web / email |

Social crops are letterboxed onto a warm ivory field with confetti and a fine
rainbow keyline, so no part of the composition is ever cut off.

## Design system

**Palette.** Bright Indian festival colours only — saffron, orange, marigold,
yellow, coral, pink, magenta, orchid, purple, royal blue, cyan, turquoise, green
and lime, on a white/ivory base. The darkest ink in the poster is a deep violet
used for type. No black, navy, maroon, brown, charcoal, antique gold or bronze.

**Layout.** Vertical hierarchy: university masthead → theme eyebrow →
`FRESHERS` display headline → `2026` between rainbow rules → batch pill → theme
line → marigold garland → hero arch of students in regional attire → cultural
mosaic ribbon → event cards.

**Background.** White-to-ivory base lifted by local pastel colour blooms in the
corners, flowing textile colour bands across the top, middle and foot, faint
mandala watermarks, and scattered confetti of petals, diamonds, rings and dots.

**Hero.** A cusped multifoil arch built from an ogee Bézier profile, scalloped
along the curve, wrapped in a saturated rainbow band with a white inner
hairline, a marigold rosette keystone and a soft magenta lift instead of a dark
drop shadow.

**Cultural mosaic ribbon.** One strip under the hero stitched from six regional
craft traditions, each patch in its own hue over a pale wash of the same colour:
Warli dancers (Maharashtra), phulkari darning (Punjab), aipan (Uttarakhand),
Assamese woven diamonds, lehariya waves (Rajasthan) and an Indian floral vine.

**Ornament.** Everything is drawn procedurally — no stock clip art. Quarter
rangoli medallions in the corners, a rainbow keyline frame, paisley/boteh pairs,
a marigold garland swag, a jali lattice whisper, mandala watermarks and
temple-triangle bands. `motifs.py` also carries Madhubani and Pattachitra bands,
petal bursts and full rangoli medallions for future variants.

**Event details.** Placed on vivid gradient cards — saffron→pink for the date,
turquoise→royal blue for the time, orchid→purple for the venue — each with a
soft coloured shadow.

**Typography.** Montserrat for the masthead, `2026` and the date; Rozha One for
the `FRESHERS` display line with a horizontal Holi-gradient fill and a white
outline; Jost for the pills and event text. Regional textile patterns for the
procedural panel come from `textiles.py`.

## Rebuilding

```bash
pip install pillow
cd src
python3 poster.py hero.jpg ../print/Freshers-2026-MBA-GraphicEra.png
python3 export.py ../print/Freshers-2026-MBA-GraphicEra.png ../social
```

`poster.py` accepts any image as its first argument and cover-fits it into the
arch, so the hero can be swapped without touching the layout.

`centrepiece.py` renders a fully procedural alternative hero — a patchwork of
ten regional textile patterns with a rangoli medallion and marigold swags — for
use when photography is not available:

```bash
python3 centrepiece.py
python3 poster.py centrepiece.png ../print/Freshers-2026-MBA-GraphicEra.png
```

`gen.py` with `hero_a.json` / `hero_b.json` regenerates the photographic group
portrait of students in regional attire via the Bria FIBO API. `hero.jpg` is the
selected `hero_b` frame and `hero-alt.jpg` the `hero_a` alternative:

```bash
python3 gen.py hero_b.json && python3 poster.py hero_b.png ../print/Freshers-2026-MBA-GraphicEra.png
```

## Fonts

Bundled under the SIL Open Font License 1.1 from
[Google Fonts](https://github.com/google/fonts): Cinzel, Cinzel Decorative,
Cormorant Garamond, Jost, Marcellus, Marcellus SC, Montserrat, Rozha One,
Yatra One.
