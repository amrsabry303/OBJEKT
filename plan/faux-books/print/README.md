# objekt faux books: print design files (draft 1, 10 Nov 2026)

33 files: 11 volumes in 3 sizes. Each file is one flat: back, spine, front, with 3 mm bleed, crop marks, spine fold marks and an info line. Not final: see "Before this goes to a printer".

| Size | Trim (W × H) | Spine | Flat trim (back + spine + front) | With 3 mm bleed | Page (with marks) |
|---|---|---|---|---|---|
| S | 14 × 20 cm | 2.0 cm | 300 × 200 mm | 306 × 206 mm | 334 × 234 mm |
| M | 18 × 25 cm | 2.8 cm | 388 × 250 mm | 394 × 256 mm | 422 × 284 mm |
| L | 23 × 30 cm | 3.5 cm | 495 × 300 mm | 501 × 306 mm | 529 × 334 mm |

Flat width = 2 × width + spine. The back is on the left, the spine in the middle, the front on the right.

## Files
- `S/`, `M/`, `L/`: `FB-nn_title_SIZE_WxHxD_print.pdf` (one page, exact page size), and `svg/` with the same files as SVG.
- `textures/`: the cow and tiger images, one per size, with bleed, 12 px/mm (305 dpi), JPEG quality 88. The SVGs link to these, so keep the folders together. The PDFs have them embedded.
- `preview_S.png`, `preview_M.png`, `preview_L.png`: contact sheets.
- Source: `../artwork/make_print.py` (run `python3 make_print.py <repo root> <S|M|L>`), `../artwork/make_print_pdf.js` (PDFs).

## Volumes
01 NOT A BOOK · 02 SHELF LIFE · 03 HEAVY READING · 04 JUDGE THE COVER · 05 OBJEKTS OF CHARACTER · 06 USELESS ON PURPOSE · 07 COFFEE TABLE BOOK · 08 DESIGN WORTH NOTICING · 09 EASY TIGER (tiger print) · 10 HOLY COW (cow hide) · 11 BETWEEN THE LINES (stripes). Spine numbers 01 to 11 on every spine.

## What scales with the size
- Title type fills the cover width (margin 11 mm on the Medium, scaled with the width on S and L), with the same four layouts as the approved design.
- Spine type is one size per book size, set by the spine width and the longest title: S 9.0 mm, M 12.6 mm, L 15.8 mm font size (cap height 6.6, 9.2 and 11.5 mm). It keeps at least 12 mm clear of the number at the head.
- Spine symbol is 55% of the spine width (11, 15.4, 19.3 mm wide), centred.
- Fixed on every size, measured from the foot: back logo 40 mm wide and symbol both sit 14 mm from the foot edge; spine title starts 8 mm above the symbol; the number sits 14 mm from the head.
- Stripes (11): 12 bands, eleven equal ones to 25 mm from the foot, so the band edge falls between the logo's symbol and wordmark on every size.
- Cow and tiger: regenerated for each size from the same seeds, so the look is the same and the patches sit in the same relative places (title, spine and logo zones kept clear).

## Before this goes to a printer
1. **Fonts.** Lettering is Inter, a stand-in. Galak Round and PP Mori are not licensed for commercial use, and no font files are committed. Every title, spine and fit will change with the real face (wider and rounder). The PDFs embed Inter as Type 3 outlines. Final files need the licensed font, then are regenerated.
2. **Logo.** The supplied logo files only. Licence for the logo lettering is still unconfirmed. The logo in a product colour on a cover is not one of the pairings in the brand guide and needs Sabry's OK.
3. **Wrap allowance.** None. A paper wrap over a solid block needs a turn-in on all sides, and the maker's template decides how much. The flat is trim size plus 3 mm bleed only. Ask the maker for the template and the turn-in.
4. **Bleed.** 3 mm is a standard assumption, not the maker's figure.
5. **Colour.** RGB hex values from `brand/COLOURS-FINISHES.md`, which are screen approximations. The printer converts to CMYK or Pantone from a physical sample. Cow and tiger are full-colour images, so they print as CMYK.
6. **Spine width.** 2.0, 2.8 and 3.5 cm are Sabry's figures. They must match the real thickness of the block plus the board, so confirm with the maker before print.
7. **Dielines.** Crop marks and fold marks only. No die line, because there is no template.
8. **Raster art.** The cow and tiger are generated images (305 dpi), not scanned hides. A designer should check them. Printed colour is untested.
9. **Proof.** Print one of each size at actual size before any run. Check spine type, the number, and Clay lettering on the Clay covers (Bone on Clay is 4.1 : 1).
