# Freshers 2026 — MBA Batch 2026–28

Event poster for **Graphic Era (Deemed to be University), Dehradun**.
Theme: **India's Cultural Mosaic** — *One India • Many Cultures • One Celebration*.

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

Social crops are letterboxed onto a matching maroon field with a gold keyline, so
no part of the composition is ever cut off.

## Design system

**Layout.** Vertical editorial hierarchy: university masthead, theme eyebrow,
`FRESHERS` display headline, `2026` on flanking rules, batch line, theme line, a
cusped-arch hero panel, then the event information block.

**Structure.** The hero sits inside a cusped multifoil Mughal arch built from an
ogee Bézier profile, scalloped along the curve and finished with a gold band, an
inner hairline, a lotus keystone and a finial.

**Ornament.** Everything is drawn procedurally — no stock clip art. Quarter
mandalas in the corners, concentric mandala watermarks, paisley/boteh motifs,
lotus rosettes, kanjeevaram temple-triangle borders and diamond-chain textile
selvedge rules.

**Cultural mosaic panel.** The arch is filled with a patchwork of ten
procedurally generated regional textile patterns — bandhani, ikat, phulkari,
kanjeevaram temple stripe, paithani, Assamese woven band, kalamkari vine,
chikankari, Kashmiri boteh and Uttarakhandi aipan — overlaid with a jali lattice,
a rangoli medallion, marigold swags and a row of brass diyas.

**Palette.** Deep maroon field, royal saffron centre glow, indigo lower corners,
deep green upper corners, muted gold and ivory typography, terracotta accents. No
neon.

**Typography.** Cinzel for the masthead and date, Rozha One for the `FRESHERS`
display line, Jost for event details, Cormorant Garamond for the theme line. Gold
foil fills are vertical gradients masked through the glyphs.

## Rebuilding

```bash
pip install pillow
cd src
python3 centrepiece.py                                    # arch panel
python3 poster.py centrepiece.png ../print/poster.png     # master poster
python3 export.py ../print/poster.png ../social           # delivery sizes
```

`poster.py` accepts any image as its first argument and will cover-fit it into the
arch, so the panel can be swapped for photography without touching the layout.

`gen.py` with `hero_a.json` / `hero_b.json` generates a photographic group
portrait of students in regional attire via the Bria FIBO API, for the
photography variant of the hero panel:

```bash
python3 gen.py hero_a.json && python3 poster.py hero_a.png ../print/poster.png
```

## Fonts

Bundled under the SIL Open Font License 1.1 from
[Google Fonts](https://github.com/google/fonts): Cinzel, Cinzel Decorative,
Cormorant Garamond, Jost, Marcellus, Marcellus SC, Montserrat, Rozha One,
Yatra One.
