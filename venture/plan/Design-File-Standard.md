# Design files for production: our standard

Modelled on `Planter Drawing 2.pdf` (REV B, 13 Oct 2026). Applies to every objekt product that goes to Production. First product built to it: OBJ-038. The working skill is `.claude/skills/objekt-drawings/`.

## What goes to Production for each product

One folder per product, named `OBJ-nnn`, holding:

| File | Format | What it is |
|------|--------|------------|
| `OBJ-nnn_revN_drawings.pdf` | PDF, A3 landscape | The drawing set. One file, several sheets. This is what Production reads. |
| `OBJ-nnn_revN_*.svg` | SVG | The same sheets as images, one per sheet. |
| `OBJ-nnn_revN_<part>.dxf` | DXF, mm | One flat pattern per laser-cut part, outline on layer `CUT`. |
| `OBJ-nnn_revN_nest_<sheet>.dxf` | DXF, mm | All parts on one assumed sheet; sheet outline on layer `SHEET`. |
| STEP | only for simple solids | Not produced unless asked. |

Old revisions move into `superseded-revN/`. Nothing is deleted.

## The sheets (A3)

1. **Views:** elevations, plan, balloons matching the bill of materials, reference photo, overall dimensions, colourways (swatch, hex, material and finish).
2. **Part sheet:** each flat pattern at 1:2 with every dimension Production needs, joint details, a DATA table.
3. **Assembly:** exploded view, bought-in part details, numbered assembly sequence (proposed; Production decides jigs and welds).
4. **Cutting layout:** parts nested on one assumed sheet, with total cutting length.
5. **Bill of materials and notes.**

## On every sheet

- **Bilingual:** English and Arabic on title, view names, labels, BOM and notes.
- **Title block:** product number and name, size, scale, units (mm), material, finish, date, sheet n of N, revision.
- **Status stamp:** "DRAFT, not approved, not engineered" until Sabry approves; then "Approved by Sabry <date>. Production review pending. Not engineered".

## What the drawing must say honestly

- Sizes taken from a photo or render are labelled as such.
- Tolerances, sheet size, joints, welding, finish and thickness are Production's. We propose; they decide.
- No structural claims, no stress figures, no sign-off. No costs or prices.

## Open

- Arabic wording needs a native technical reader.
- Standard sheet size (1250 × 2500 mm assumed) and general tolerance (±1 mm assumed) to be confirmed by Production.
