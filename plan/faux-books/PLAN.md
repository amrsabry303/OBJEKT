# objekt faux books: plan and design (current, 11 Nov 2026)

Decided by Sabry unless marked as a proposal. Nothing here is costed, quoted, sent to a maker or uploaded. Draft history was removed on 11 Nov; it is in git history.

## What it is
Decorative books that are objects, not books: a solid block wrapped in printed matte paper, sold one at a time and as sets of three. 11 designs, each in three sizes. Day 1 (Sabry, 10 Nov). Website category Table & Living, internal category Desk and book. Not a Polycraft process (outside printer and binder), so it carries no "Made at Polycraft" line.

| Size | Trim (W × H) | Spine | Flat (back + spine + front) |
|---|---|---|---|
| S | 14 × 20 cm | 2.0 cm | 300 × 200 mm |
| M | 18 × 25 cm | 2.8 cm | 388 × 250 mm |
| L | 23 × 30 cm | 3.5 cm | 495 × 300 mm |

Sizes and spines are Sabry's figures (11 Nov). Face ratio 1 : 1.3 to 1 : 1.4, like real books.

## The 11 designs
Working titles, proposals until Sabry confirms. Product numbers OBJ-178 to OBJ-188 (confirmed by Sabry, 11 Nov; FB-nn is the file number); the set of three is OBJ-189. Lettering colour is the second colour. Every colour is one of the eight in `brand/COLOURS-FINISHES.md`.

| FB | OBJ | Title | Cover | Lettering | Front layout |
|---|---|---|---|---|---|
| 01 | 178 | NOT A BOOK | Bone | Objekt Green | small first line, giant last word cropped at the foot |
| 02 | 179 | SHELF LIFE | Putty | Chocolate | title runs up the cover |
| 03 | 180 | HEAVY READING | Carbon | Bone | fills the width |
| 04 | 181 | JUDGE THE COVER | Ink | Putty | fills the width |
| 05 | 182 | OBJEKTS OF CHARACTER | Oxblood | Bone | fills the width |
| 06 | 183 | USELESS ON PURPOSE | Clay | Bone | title runs up the cover |
| 07 | 184 | COFFEE TABLE BOOK | Chocolate | Putty | fills the width |
| 08 | 185 | DESIGN WORTH NOTICING | Objekt Green | Bone | small first lines, giant last word cropped |
| 09 | 186 | EASY TIGER | tiger coat on Clay | Bone | fills the width |
| 10 | 187 | HOLY COW | cow hide on Bone | Bone (on the brown) | fills the width (approved as is) |
| 11 | 188 | BETWEEN THE LINES | 12 Carbon and Bone bands | Bone on dark, Carbon on light | one title line per band, centred on the front |

Sets of three (same size, spines flush, stacked): A = 03 + 01 + 05, B = 07 + 02 + 08, print set = 09 + 10 + 11. 04 and 06 are singles only. Each set has one dark, one light and one colour.

## Design system
- **Type:** Galak Round per the brand rule, caps, tight tracking. Not licensed, so every file uses Inter as a stand-in; the real face is wider and rounder and will change the fits. Titles are aligned by their inked edge to the margin.
- **Back:** the full objekt logo, 40 mm wide, 14 mm from the foot, centred. **Spine:** the symbol (55% of the spine width) at the foot, the title in caps above it, the series number 01 to 11 at the head. On every size these sit at fixed distances from the foot and head.
- **Prints** wrap back, spine and front: tiger (V line down the spine), cow hide (hair strands; Chocolate and Oxblood browns on Bone), stripes (12 bands over the spine). Generated images at 305 dpi, not scans.
- **Colour check:** lettering contrast 4.1 to 12.5 : 1. Bone on Clay is the weakest (4.1 : 1): fine for large type, check the 9 mm spine type on a printed sample.

## Files
- `print/`: print PDFs for all 33 combinations (back, spine, front, 3 mm bleed, crop and fold marks), SVG sources, 305 dpi textures, previews, README with the checklist. Generator: `print/src/make_print.py <repo root> <S|M|L>`, then `node print/src/make_print_pdf.js <repo root>`.
- `renders/`: 3D mockups at size M (the 11 designs and the 3 sets) built from the same files, not AI renders, not photos. Pipeline in `renders/src/`.
- Reference photos: `images/OBJ-178.jpg` to `OBJ-188.jpg` (repo convention). They are other brands' books, kept as reference only, never shown to customers. Which photo stands behind which design: 09 tiger coat, 10 cow hide, 11 striped spines, 01 and 08 cropped title, the rest stacked and vertical titles.

## Not decided or not done
1. **Maker.** No printer or binder. Needs: wrap and turn-in allowance, bleed, real spine thickness for 2.0 / 2.8 / 3.5 cm, block (blank pages or board), price, lead time. Print files include no wrap allowance.
2. **Font and logo licence** (Galak Round, PP Mori, logo lettering). The same open item as the rest of objekt.
3. **Website products: decided (Sabry, 11 Nov): 2.** A "Faux book" with design × size variants, and a "Set of three" (OBJ-189). This keeps Desk and book at its target of 2 and under the 10% cap. OBJ-178 to 188 stay as design and production records.
4. **Names.** The 11 titles are working titles, not names approved under the naming rules.
5. **Logo on product colours** is not one of the guide's six pairings. Needs Sabry's OK.
6. **Drive design folders:** created 11 Nov (OBJ-178 to 189, next to the other design folders) and the books added to the Google product sheet. The 11 Medium print PDFs are uploaded, one per design folder. The S and L files and the OBJ-189 folder are still empty.
7. **Day-1 reality.** With no maker, sample, price or lead time, the books can only be listed as pre-order on 20 Nov.
8. **Printed colour, cow and tiger images, small spine type** are untested; print one proof per size first.
9. Real photos replace the mockups once samples exist.
